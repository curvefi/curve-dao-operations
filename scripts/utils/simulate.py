import sys
import ape
import pprint

from scripts.utils import CONVEX_VOTERPROXY, CURVE_DEPLOYER_2
from rich.console import Console as RichConsole


RICH_CONSOLE = RichConsole(file=sys.stdout)

def simulate(vote_id: int, voting_contract: str):
    """Create AragonDAO vote and simulate passing vote on mainnet-fork.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)
        description (str): Description of the on-chain governance proposal
    """
    RICH_CONSOLE.log("[yellow]--------- SIMULATE VOTE ---------")
    
    aragon = ape.project.Voting.at(voting_contract)

    # print vote details to console first:
    RICH_CONSOLE.log("Vote stats before Convex Vote:")
    vote_stats = aragon.getVote(vote_id)
    RICH_CONSOLE.log(pprint.pformat(vote_stats, indent=4))
    
    # vote
    RICH_CONSOLE.log("Simulate Convex 'yes' vote")
    aragon.vote(vote_id, True, False, sender=ape.accounts[CONVEX_VOTERPROXY])

    # sleep for a week so it has time to pass
    num_blocks = int(aragon.voteTime() + 200 / 10)
    ape.chain.mine(num_blocks)

    # get vote stats:
    RICH_CONSOLE.log("Vote stats after 1 week:")
    vote_stats = aragon.getVote(vote_id)
    RICH_CONSOLE.log(pprint.pformat(vote_stats, indent=4))

    # moment of truth - execute the vote!
    RICH_CONSOLE.log("Simulate proposal execution")
    aragon.executeVote(vote_id, sender=ape.accounts[CURVE_DEPLOYER_2])
    print("[green]--------- VOTE EXECUTED ---------")
