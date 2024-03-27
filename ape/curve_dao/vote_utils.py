import warnings
from datetime import datetime
from typing import Dict, List, Tuple

import ape
from ape.exceptions import ContractLogicError
from ape.logging import logger

from .addresses import get_dao_voting_contract
from .decoder_utils import decode_input
from .ipfs import get_ipfs_hash_from_description

warnings.filterwarnings("ignore")


class MissingVote(Exception):
    """Exception raised when a vote ID is invalid."""


def prepare_vote_script(target: Dict, actions: List[Tuple]) -> str:
    """Generates EVM script to be executed by AragonDAO contracts.

    Args:
        target (dict): CURVE_DAO_OWNERSHIP / CURVE_DAO_PARAMS / EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)

    Returns:
        str: Generated EVM script.
    """
    agent = ape.Contract(target["agent"])
    voting = target["voting"]

    logger.info(f"Agent Contract: {agent.address}")
    logger.info(f"Voting Contract: {voting}")

    evm_script = bytes.fromhex("00000001")

    for address, fn_name, *args in actions:
        contract = ape.Contract(address)
        fn = getattr(contract, fn_name)
        calldata = bytes(fn.encode_input(*args))
        agent_calldata = bytes(agent.execute.encode_input(address, 0, calldata))
        length = bytes.fromhex(hex(len(agent_calldata.hex()) // 2)[2:].zfill(8))
        evm_script = (
            evm_script + bytes.fromhex(agent.address[2:]) + length + agent_calldata
        )

    return evm_script


def make_vote(target: Dict, actions: List[Tuple], description: str, vote_creator: str):
    """Prepares EVM script and creates an on-chain AragonDAO vote.

    Args:
        target (dict): ownership / parameter / emergency
        actions (list(tuple)): ("target addr", "fn_name", *args)
        vote_creator (str): msg.sender address
        description (str): Description of the on-chain governance proposal

    Returns:
        str: vote ID of the created vote.
    """
    aragon = ape.project.Voting.at(target["voting"])
    assert aragon.canCreateNewVote(vote_creator), "dev: user cannot create new vote"

    evm_script = prepare_vote_script(target, actions)
    logger.info(f"EVM script: {evm_script}")

    ipfs_hash = get_ipfs_hash_from_description(description)
    tx = aragon.newVote(
        evm_script,
        f"ipfs:{ipfs_hash}",
        False,
        False,
        sender=vote_creator,
    )

    return tx


def get_vote_script(vote_id: str, vote_type: str) -> str:
    try:
        voting_contract_address = get_dao_voting_contract(vote_type)
        voting_contract = ape.project.Voting.at(voting_contract_address)
        vote = voting_contract.getVote(vote_id)
        script = vote["script"]
        return script
    except ContractLogicError as e:
        if "VOTING_NO_VOTE" in str(e):
            raise MissingVote(f"Vote ID {vote_id} not found")
        else:
            raise


def get_vote_data(vote_id: str, vote_type: str) -> str:
    voting_contract_address = get_dao_voting_contract(vote_type)
    voting_contract = ape.project.Voting.at(voting_contract_address)
    vote_data = voting_contract.getVote(vote_id)

    return {
        "yea": vote_data["yea"],
        "nay": vote_data["nay"],
        "votingPower": vote_data["votingPower"],
        "open": vote_data["open"],
        "executed": vote_data["executed"],
        "startDate": vote_data["startDate"],
    }


def decode_vote_script(script):
    idx = 4

    votes = []
    while idx < len(script):

        # get target contract address:
        target = ape.Contract(script[idx : idx + 20])
        idx += 20

        length = int(script[idx : idx + 4].hex(), 16)
        idx += 4

        # calldata to execute for the dao:
        calldata = script[idx : idx + length]
        idx += length

        fn, inputs = decode_input(target, calldata)
        agent = None

        # print decoded vote:
        if calldata[:4].hex() == "0xb61d27f6":
            agent = target
            target = ape.Contract(inputs[0])
            fn, inputs = decode_input(target, inputs[2])
            inputs_with_names = get_inputs_with_names(fn, inputs)
            formatted_inputs = format_fn_inputs(inputs_with_names)
            formatted_output = (
                f"Call via agent: [yellow]{agent}[/]\n"
                f" ├─ [bold]To[/]: [green]{target}[/]\n"
                f" ├─ [bold]Function[/]: [yellow]{fn.name}[/]\n"
                f" └─ [bold]Inputs[/]: \n{formatted_inputs}\n"
            )
        else:
            inputs_with_names = get_inputs_with_names(fn, inputs)
            formatted_inputs = format_fn_inputs(inputs_with_names)
            formatted_output = (
                f"Direct call\n "
                f" ├─ [bold]To[/]: [green]{target}[/]\n"
                f" ├─ [bold]Function[/]: [yellow]{fn.name}[/]\n"
                f" └─ [bold]Inputs[/]: {formatted_inputs}\n"
            )

        vote = {
            "agent": agent.address if agent else None,
            "target": target.address,
            "function": fn.name,
            "inputs": inputs_with_names,
            "formatted_output": formatted_output,
        }
        votes.append(vote)

    return votes


def decode_vote_data(data: dict, vote_type: str):
    yes = round(data["yea"] / 1e18, 2)
    no = round(data["nay"] / 1e18, 2)
    total_votes = data["yea"] + data["nay"]
    total_voting_power = data["votingPower"]

    VOTE_TIME = 604800

    # Handle edge case where there are no votes at all
    if total_votes == 0 or total_voting_power == 0:
        quorum = 0
        support = 0
    else:
        quorum = total_votes / total_voting_power
        support = data["yea"] / total_votes

    required_support = 0.51 if vote_type == "ownership" else 0.30
    required_quorum = 0.30 if vote_type == "ownership" else 0.15

    if data["open"]:  # Voting is ongoing
        pass_status = "[yellow]Voting Ongoing[/]"
    else:  # Voting is closed
        if total_votes == 0 or total_voting_power == 0:
            pass_status = "[red]Vote Invalid: No Votes[/]"
        elif support >= required_support and quorum >= required_quorum:
            # Check if the vote has been executed
            execution_status = (
                "[green]Executed[/]" if data["executed"] else "[red]Not Executed[/]"
            )
            pass_status = (
                f"[green]Vote Passed[/] ([grey]Execution Status[/]: {execution_status})"
            )
        else:
            if support < required_support and quorum < required_quorum:
                failure_reason = "Both Support and Quorum Not Met"
            elif support < required_support:
                failure_reason = "Support Not Met"
            else:
                failure_reason = "Quorum Not Met"
            pass_status = f"[red]Vote Failed: {failure_reason}[/]"

    start = datetime.utcfromtimestamp(data["startDate"]).strftime("%Y-%m-%d %H:%M:%S")
    end = datetime.utcfromtimestamp(data["startDate"] + VOTE_TIME).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    formatted_output = (
        f"[bold]Results[/]: {pass_status}\n"
        f" ├─ [grey]Voting Start Time[/]: {start}\n"
        f" ├─ [grey]Voting End Time[/]: {end}\n"
        f" ├─ [green]Votes For[/]: {yes}\n"
        f" ├─ [red]Votes Against[/]: {no}\n"
        f" ├─ [blue]Support[/]: {round(support * 100, 2)}% (Required: {int(required_support * 100)}%)\n"
        f" └─ [purple]Quorum[/]: {round(quorum * 100, 2)}% (Minimum: {int(required_quorum * 100)}%)\n"
    )

    results = {
        "start": data["startDate"],
        "end": data["startDate"] + VOTE_TIME,
        "votingPower": data["votingPower"],
        "open": data["open"],
        "executed": data["executed"],
        "yes": data["yea"],
        "no": data["nay"],
        "support": support,
        "quorum": quorum,
        "formatted_output": formatted_output,
    }

    return results


def get_inputs_with_names(abi, inputs):
    arg_names = []
    for i in range(len(inputs)):
        argname = abi.inputs[i].name
        arg_names.append(argname)

    inputs_with_names = list(zip(arg_names, inputs))
    return inputs_with_names


def format_fn_inputs(inputs_with_names):
    if len(inputs_with_names) == 0:
        return ""

    if len(inputs_with_names) == 1:
        name, arg = inputs_with_names[0]
        return f"    └─ [bold]{name}[/]: [yellow]{arg}[/]"

    formatted_args = ""
    for name, arg in inputs_with_names[:-1]:
        formatted_args += f"    ├─ [bold]{name}[/]: [yellow]{arg}[/]\n"
    name, arg = inputs_with_names[-1]
    formatted_args += f"    └─ [bold]{name}[/]: [yellow]{arg}[/]"
    return formatted_args
