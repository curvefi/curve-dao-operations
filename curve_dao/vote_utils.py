import warnings
from typing import Dict, List, Tuple
from datetime import datetime

import ape
from ape.logging import logger

from .addresses import get_dao_voting_contract
from .decoder_utils import decode_input
from .ipfs import get_ipfs_hash_from_description

warnings.filterwarnings("ignore")


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
    except:
        return False 


def get_vote_data(vote_id: str, vote_type: str) -> str:
    voting_contract_address = get_dao_voting_contract(vote_type)
    voting_contract = ape.project.Voting.at(voting_contract_address)
    func = voting_contract.getVote(vote_id)                         
    data = [] 
    data.append(func["yea"] / 1e18)
    data.append(func["nay"] / 1e18)
    data.append(func["votingPower"] / 1e18)
    data.append(func["open"])
    data.append(func["executed"])
    data.append(func["startDate"])

    return data

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


def format_data(data, vote_type):

    yes = round(data[0], 2)
    no = round(data[1], 2)
    quorum = round((data[0] + data[1]) / data[2] * 100, 2)
    support = round((data[0] - data[1]) / (data[0] + data[1]) * 100 , 2)
    if data[3] == True:
        state = "vote ongoing"
    else:
        if data[4] == True:
            state = "vote closed & executed!"
        else:
            state = "vote closed & executable if passed"


    start = datetime.utcfromtimestamp(data[5])
    start = start.strftime("%Y-%m-%d %H:%M:%S")
    end = data[5] + 604800
    end = datetime.utcfromtimestamp(end)
    end = end.strftime("%Y-%m-%d %H:%M:%S")

    if vote_type == "ownership":
        results_output = (
            f"[bold]Data: ({state})[/]:\n"
            f" ├─ [black]START[/]: {start}\n"
            f" ├─ [black]END[/]: {end}\n"
            f" ├─ [green]YES[/]: {yes}\n"
            f" ├─ [red]NO[/]: {no}\n"
            f" ├─ [black]Support[/]: {support}% (51% required)\n"
            f" └─ [black]Quorum[/]: {quorum}% (30% required)\n"
        )
        return results_output
    
    elif vote_type == "parameter":
        results_output = (
            f"[bold]Data: ({state})[/]:\n"
            f" ├─ [black]START[/]: {start}\n"
            f" ├─ [black]END[/]: {end}\n"
            f" ├─ [green]YES[/]: {yes}\n"
            f" ├─ [red]NO[/]: {no}\n"
            f" ├─ [black]Support[/]: {support}% (60% required)\n"
            f" └─ [black]Quorum[/]: {quorum}% (15% required)\n"
        )
        return results_output


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
