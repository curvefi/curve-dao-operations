import sys
import warnings
from rich.console import Console as RichConsole
import os
from dotenv import load_dotenv
from typing import Dict, List, Tuple
from boa.network import NetworkEnv

import boa

from curve_dao.vote_utils import prepare_vote_script
from curve_dao.ipfs import get_ipfs_hash_from_description

load_dotenv()

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)

def create_vote(
        target: Dict, 
        actions: List[Tuple], 
        description: str, 
        vote_creator: str
):
    """
    Prepares EVM script and creates an on-chain AragonDAO vote.

    Args:
        target (dict): ownership / parameter / emergency
        actions (list(tuple)): ("target addr", "fn_name", *args)
        vote_creator (str): msg.sender address
        description (str): Description of the on-chain governance proposal

    Returns:
        str: vote ID of the created vote.
    """

    boa.env.fork(f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}")

    RICH_CONSOLE.log("Creating a DAO vote:")


    # get contract instance of the voting ownership of the target address.
    aragon = boa.load_abi("contracts/aragon_interfaces/Voting.json", name="Aragon")
    aragon = aragon.at(target["voting"])

    assert aragon.canCreateNewVote(vote_creator), "user cannot create a new vote"

    # evm script
    evm_script = prepare_vote_script(target, actions)
    RICH_CONSOLE.log(f"EVM script: {evm_script}")

    # ipfs hash
    ipfs_hash = get_ipfs_hash_from_description(description)

    # actual transcation
    with boa.env.prank(vote_creator):
        tx = aragon.newVote(
            evm_script,
            f"ipfs: {ipfs_hash}",
            False,
            False
        )

    return tx
