import pprint
import sys
import os
from dotenv import load_dotenv
from rich.console import Console as RichConsole

import boa

from addresses import CONVEX_VOTERPROXY

load_dotenv()

RICH_CONSOLE = RichConsole(file=sys.stdout)


def simulate(vote_id: int, voting_contract: str):

    boa.env.fork(f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}")

    """Simulate passing vote on mainnet-fork"""
    RICH_CONSOLE.log("--------- SIMULATE VOTE ---------")

    aragon = boa.load_abi("contracts/aragon_interfaces/Voting.json", name="Aragon")

    aragon = aragon.at(voting_contract)

    # print vote details to console first:
    RICH_CONSOLE.log("Vote stats before Convex Vote:")

    vote_stats = aragon.getVote(vote_id)
    RICH_CONSOLE.log(pprint.pformat(vote_stats, indent=4))

    # vote
    RICH_CONSOLE.log("Simulate Convex 'yes' vote")

    with boa.env.prank(CONVEX_VOTERPROXY):
        aragon.vote(vote_id, True, False)

    # sleep for a week so it has time to pass
    num_seconds = aragon.voteTime()

    boa.env.time_travel(num_seconds)

    # get vote stats:
    RICH_CONSOLE.log("Vote stats after 1 week:")
    vote_stats = aragon.getVote(vote_id)
    RICH_CONSOLE.log(pprint.pformat(vote_stats, indent=4))

    # moment of truth - execute the vote!
    RICH_CONSOLE.log("Simulate proposal execution")

    with boa.env.prank(CONVEX_VOTERPROXY):
        aragon.executeVote(vote_id)

    RICH_CONSOLE.log("Vote Executed!")
