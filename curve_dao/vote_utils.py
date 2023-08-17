import json
import os
import warnings
from typing import Dict, List, Tuple

import ape
import requests
from ape.logging import logger

warnings.filterwarnings("ignore")

CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"

# def prepare_evm_script():
#     agent = Contract.from_explorer(TARGET["agent"])
#     evm_script = "0x00000001"
#
#     for address, fn_name, *args in ACTIONS:
#         contract = Contract.from_explorer(address)
#         fn = getattr(contract, fn_name)
#         calldata = fn.encode_input(*args)
#         agent_calldata = agent.execute.encode_input(address, 0, calldata)[2:]
#         length = hex(len(agent_calldata) // 2)[2:].zfill(8)
#         evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata}"
#
#     return evm_script


def prepare_evm_script(target: Dict, actions: List[Tuple]) -> str:
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

    # evm_script = "0x00000001"
    evm_script = bytes.fromhex("00000001")

    for address, fn_name, *args in actions:
        print(address, fn_name, *args)
        contract = ape.Contract(address)
        fn = getattr(contract, fn_name)
        calldata = fn.as_transaction(*args, sender=agent).data
        print(calldata)
        agent_calldata = agent.execute.as_transaction(
            address, 0, calldata, sender=voting
        ).data
        print(agent_calldata)
        length = bytes.fromhex(hex(len(agent_calldata.hex()) // 2)[2:].zfill(8))
        evm_script = (
            evm_script + bytes.fromhex(agent.address[2:]) + length + agent_calldata
        )
        # evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata.hex()}"
        # evm_script = bytes(evm_script, "utf-8")

    return evm_script


def get_vote_description_ipfs_hash(description: str):
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

    evm_script = prepare_evm_script(target, actions)
    logger.info(f"EVM script: {evm_script}")

    tx = aragon.newVote(
        evm_script,
        f"ipfs:{get_vote_description_ipfs_hash(description)}",
        False,
        False,
        sender=vote_creator,
    )

    return tx
