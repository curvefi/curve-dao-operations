import ape
import json
import requests
from eth_abi import encode_abi
from eth_utils import encode_hex
from typing import List, Dict, Tuple


def encode_fn_inputs(contract: ape.Contract, fn_name: str, args: List):

    fn = getattr(contract, fn_name)
    input_types = [abi_input.canonical_type for abi_input in fn.abis[0].inputs]
    encoded_inputs = encode_abi(input_types, args)
    return encode_hex(encoded_inputs)


def prepare_evm_script(target: Dict, actions: List[Tuple]) -> str:
    """Generates EVM script to be executed by AragonDAO contracts.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)

    Returns:
        str: Generated EVM script.
    """
    agent = ape.Contract(target["agent"])
    evm_script = "0x00000001"

    for address, fn_name, *args in actions:

        # build target contract calldata:
        target_contract = ape.Contract(address)
        target_contract_calldata = encode_fn_inputs(target_contract, fn_name, args)

        # build governance agent calldata:
        agent_calldata = encode_fn_inputs(
            agent, "execute", [address, 0, target_contract_calldata.encode()]
        )[2:]

        # concat into evm script:
        length = hex(len(agent_calldata) // 2)[2:].zfill(8)
        evm_script = f"{evm_script}{agent.address[2:]}{length}{agent_calldata}"

    return evm_script


def get_vote_description_ipfs_hash(description: str):
    text = json.dumps({"text": description})
    response = requests.post(
        "https://ipfs.infura.io:5001/api/v0/add", files={"file": text}
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

        print("Generated calldata: ", evm_script, "\n")
        tx = aragon.newVote(
            evm_script,
            f"ipfs:{get_vote_description_ipfs_hash(description)}",
            False,
            False,
            sender=vote_creator,
        )

    return tx
