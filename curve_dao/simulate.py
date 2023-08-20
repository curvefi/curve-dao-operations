import pprint

import ape
from ape.logging import logger

from curve_dao import CONVEX_VOTERPROXY


def simulate(vote_id: int, voting_contract: str):
    """Simulate passing vote on mainnet-fork"""
    logger.info("--------- SIMULATE VOTE ---------")

    aragon = ape.project.Voting.at(voting_contract)

    # print vote details to console first:
    logger.info("Vote stats before Convex Vote:")
    vote_stats = aragon.getVote(vote_id)
    logger.info(pprint.pformat(vote_stats, indent=4))

    # vote
    logger.info("Simulate Convex 'yes' vote")
    aragon.vote(vote_id, True, False, sender=ape.accounts[CONVEX_VOTERPROXY])

    # sleep for a week so it has time to pass
    num_seconds = aragon.voteTime()
    ape.chain.mine(deltatime=num_seconds)

    # get vote stats:
    logger.info("Vote stats after 1 week:")
    vote_stats = aragon.getVote(vote_id)
    logger.info(pprint.pformat(vote_stats, indent=4))

    # moment of truth - execute the vote!
    logger.info("Simulate proposal execution")
    enacter = ape.accounts[CONVEX_VOTERPROXY]
    aragon.executeVote(vote_id, sender=enacter)
    logger.info("Vote Executed!")
