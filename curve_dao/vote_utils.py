import json
import os
import sys
import warnings
from typing import Dict, List, Tuple

import ape
import requests
from ape.logging import logger

from curve_dao.decoder_utils import decode_input

warnings.filterwarnings("ignore")


warnings.filterwarnings("ignore")

CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"
DAO_VOTING_CONTRACTS = {
    "ownership": "0xE478de485ad2fe566d49342Cbd03E49ed7DB3356",
    "parameter": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "emergency": "0x1115c9b3168563354137cdc60efb66552dd50678",
}


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
        calldata = fn.as_transaction(*args, sender=agent).data
        agent_calldata = agent.execute.as_transaction(
            address, 0, calldata, sender=voting
        ).data
        length = bytes.fromhex(hex(len(agent_calldata.hex()) // 2)[2:].zfill(8))
        evm_script = (
            evm_script + bytes.fromhex(agent.address[2:]) + length + agent_calldata
        )

    return evm_script


def get_ipfs_hash_from_description(description: str):
    """Uploads vote description to IPFS and returns the IPFS hash.

    NOTE: needs environment variables for infura IPFS access. Please
    set up an IPFS project to generate project id and project secret!
    """
    text = json.dumps({"text": description})
    response = requests.post(
        "https://ipfs.infura.io:5001/api/v0/add",
        files={"file": text},
        auth=(os.getenv("IPFS_PROJECT_ID"), os.getenv("IPFS_PROJECT_SECRET")),
    )
    assert (
        200 <= response.status_code < 400
    ), f"POST to IPFS failed: {response.status_code}"
    return response.json()["Hash"]


def get_description_from_ipfs_hash(ipfs_hash: str):
    response = requests.post(
        f"https://ipfs.infura.io:5001/api/v0/get?arg={ipfs_hash}",
        auth=(os.getenv("IPFS_PROJECT_ID"), os.getenv("IPFS_PROJECT_SECRET")),
    )
    response.raise_for_status()
    response_string = response.content.decode("utf-8")
    json_string = []
    in_json = False
    for c in response_string:
        if c == "{":
            in_json = True
        if in_json:
            json_string.append(c)
        if c == "}":
            break
    json_string = "".join(json_string)
    return json.loads(json_string)


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

    tx = aragon.newVote(
        evm_script,
        f"ipfs:{get_ipfs_hash_from_description(description)}",
        False,
        False,
        sender=vote_creator,
    )

    return tx


def get_vote_script(vote_id: str, target: str) -> str:
    voting_contract_address = DAO_VOTING_CONTRACTS[target]
    voting_contract = ape.project.Voting.at(voting_contract_address)
    vote = voting_contract.getVote(vote_id)
    script = vote["script"]
    return script


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


def get_ipfs_hash_from_vote_id(target, vote_id):
    voting_contract_address = DAO_VOTING_CONTRACTS[target]
    voting_contract = ape.project.Voting.at(voting_contract_address)
    snapshot_block = voting_contract.getVote(vote_id)["snapshotBlock"]
    vote_events = voting_contract.StartVote.query(
        "voteId",
        "metadata",
        start_block=snapshot_block - 1,
        stop_block=snapshot_block + 1,
    )
    vote_row = vote_events.loc[vote_events["voteId"] == vote_id]
    ipfs_hash = vote_row["metadata"].iloc[0]
    ipfs_hash = ipfs_hash[5:]
    return ipfs_hash


def get_description_from_vote_id(vote_id, target):
    ipfs_hash = get_ipfs_hash_from_vote_id(target, vote_id)
    description = get_description_from_ipfs_hash(ipfs_hash)
    return description
