import ape
import pprint

from scripts.dao_utils import CONVEX_VOTERPROXY, CURVE_DEPLOYER_2


def simulate(vote_id: int, quorum: int, voting_contract: str):
    """Create AragonDAO vote and simulate passing vote on mainnet-fork.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)
        description (str): Description of the on-chain governance proposal
    """
    print("\n# --------- SIMULATE VOTE --------- #")
    # vote
    aragon = ape.project.Voting.at(voting_contract)
    aragon.vote(vote_id, True, False, sender=ape.accounts[CONVEX_VOTERPROXY])

    # sleep for a week so it has time to pass
    num_blocks = int(aragon.voteTime() + 200 / 10)
    ape.chain.mine(num_blocks)

    # get vote stats:
    vote_stats = aragon.getVote(vote_id)
    pprint.pprint(vote_stats)

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, sender=ape.accounts[CURVE_DEPLOYER_2])
    print("# --------- VOTE EXECUTED --------- #\n")
