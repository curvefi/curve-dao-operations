import os
import sys
import ape
import json
import requests
from eth_abi import decode_abi
from typing import List, Dict, Tuple
import warnings
from rich.console import Console as RichConsole

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)
CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"


def prepare_evm_script(target: Dict, actions: List[Tuple]) -> str:
    """Generates EVM script to be executed by AragonDAO contracts.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)

    Returns:
        str: Generated EVM script.
    """
    agent = ape.Contract(target["agent"])
    voting = target["voting"]
    
    RICH_CONSOLE.log(f"Agent Contract: [yellow]{agent.address}")
    RICH_CONSOLE.log(f"Voting Contract: [yellow]{voting}")

    evm_script = "0x00000001"

    for address, fn_name, *args in actions:

        # build target contract calldata:
        target_contract = ape.Contract(address)
        RICH_CONSOLE.log(f"Target Contract [green]: {target_contract.address}")
        target_fn = getattr(target_contract, fn_name)
        target_contract_calldata = target_fn.as_transaction(
            *args, sender=agent
        ).data
        
        RICH_CONSOLE.log(f"Target contract calldata: [blue]{target_contract_calldata.hex()}")

        # build governance agent calldata:
        agent_fn = getattr(agent, "execute")
        agent_calldata = agent_fn.as_transaction(
            address, 0, target_contract_calldata, sender=target["voting"]
        ).data.hex()[2:]
        RICH_CONSOLE.log(f"Agent calldata: [blue]{agent_calldata}")

        # concat into evm script:
        length = hex(len(agent_calldata) // 2)[2:].zfill(8)
        RICH_CONSOLE.log(f"Script length: [blue]{int(length, 16)}")
        
        evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata}"

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
    return response.json()["Hash"]


def make_vote(target: Dict, actions: List[Tuple], description: str, vote_creator: str):
    """Prepares EVM script and creates an on-chain AragonDAO vote.

    Note: this script can be used to deploy on-chain governance proposals as well.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)
        vote_creator (str): msg.sender address
        description (str): Description of the on-chain governance proposal

    Returns:
        str: vote ID of the created vote.
    """
    aragon = ape.project.Voting.at(target["voting"])
    assert aragon.canCreateNewVote(vote_creator), "dev: user cannot create new vote"

    evm_script = prepare_evm_script(target, actions)
    
    RICH_CONSOLE.log(f"EVM script: {evm_script}")    

    if target.get("forwarder"):

        # the emergency DAO only allows new votes via a forwarder contract
        # so we have to wrap the call in another layer of evm script

        vote_calldata = aragon.newVote.encode_input(
            evm_script, description, False, False
        )[2:]
        length = hex(len(vote_calldata) // 2)[2:].zfill(8)
        evm_script = f"0x00000001{aragon.address[2:]}{length}{vote_calldata}"

        # send tx via forwarder
        forwarder = ape.project.TokenManager.at(target["forwarder"])
        tx = forwarder.forward(evm_script, sender=vote_creator)

    else:

        RICH_CONSOLE.log("Generated calldata: ", evm_script, "\n")
        tx = aragon.newVote(
            evm_script,
            f"ipfs:{get_vote_description_ipfs_hash(description)}",
            False,
            False,
            sender=vote_creator,
        )

    return tx
