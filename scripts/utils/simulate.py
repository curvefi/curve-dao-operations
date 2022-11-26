import pprint
import sys

import ape
from rich.console import Console as RichConsole

from scripts.utils import CONVEX_VOTERPROXY, CURVE_DEPLOYER_2

RICH_CONSOLE = RichConsole(file=sys.stdout)


def simulate(vote_id: int, voting_contract: str):
    """Simulate passing vote on mainnet-fork"""
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
    enacter = ape.accounts[CURVE_DEPLOYER_2]
    aragon.executeVote(vote_id, sender=enacter)
    RICH_CONSOLE.log("[green] Vote Executed!")
