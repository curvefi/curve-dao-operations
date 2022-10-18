import os
import sys
import ape
import json
import requests
from eth_abi import decode_abi
from typing import List, Dict, Tuple
import warnings
from hexbytes import HexBytes
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
    # RICH_CONSOLE.log(decode_vote(evm_script))

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


def attempt_decode_call_signature(contract: ape.Contract, selector: str):

    # decode method id (or at least try):
    method = selector.hex()
    if selector in contract.contract_type.mutable_methods:
        method = contract.contract_type.mutable_methods[selector]
        return method.name or f"<{selector}>"
    elif selector in contract.contract_type.view_methods:
        method = contract.contract_type.view_methods[selector]
        return method.name or f"<{selector}>"
    else:
        raise
    
    
def decode_input(calldata: str, target: ape.Contract):
    
    _ecosystem = ape.networks.ecosystems["ethereum"]
    selector = calldata[:4]
    method = attempt_decode_call_signature(target, selector)
    
    print(target, method)
    
    raw_calldata = calldata[4:]
    print(target, selector)
    method_abi = target.contract_type.mutable_methods[selector]
    
    input_types = [i.canonical_type for i in method_abi.inputs]  # type: ignore
    raw_input_values = decode_abi(input_types, raw_calldata)
    arguments = [
        _ecosystem.decode_primitive_value(v, ape.utils.abi.parse_type(t))
        for v, t in zip(raw_input_values, input_types)
    ]
    
    return method, arguments


def decode_vote(script: str):
    
    RICH_CONSOLE.log("---- DECODING SCRIPT ----")
    
    script = HexBytes(script)
    
    RICH_CONSOLE.log(f"First four bytes: {script[:4].hex()}")
    idx = 4   
    
    while idx < len(script):
        
        # get target contract address:
        target = ape.Contract(script[idx : idx + 20])
        RICH_CONSOLE.log(
            f"Decoding snippet: {script[idx : idx + 20]} "
            f"-> (target addr) {target.address}"
        )
        idx += 20
        
        length = int(script[idx : idx + 4].hex(), 16)
        RICH_CONSOLE.log(
            f"Decoding Snippet: {script[idx : idx + 4]} "
            f"-> (length) {length}"
        )
        idx += 4
        
        # calldata to execute for the dao:
        calldata = script[idx : idx + length]
        RICH_CONSOLE.log(
            f"Decoding Snippet: {script[idx : idx + length]} "
            f"-> (calldata) {calldata.hex()}"
        )
        idx += length
        
        # given calldata, get fn name and args:
        fn, inputs = decode_input(calldata, target)
        
        # print decoded vote:
        if calldata[:4].hex() == "0xb61d27f6":
            agent_target = ape.Contract(inputs[0])
            fn, inputs = decode_input(inputs[2], agent_target)
            RICH_CONSOLE.log(
                f"Call via agent ({target}):\n ├─ To: {agent_target}\n"
                f" ├─ Function: {fn}\n └─ Inputs: {inputs}\n"
            )
        else:
            RICH_CONSOLE.log(
                f"Direct call:\n ├─ To: {target}\n ├─ Function: {fn}\n └─ Inputs: {inputs}"
            )
