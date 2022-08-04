import ape
from typing import Dict, List, Tuple

from scripts.dao_utils import stakeholders


def simulate(vote_id: int, quorum: int, voting_contract: str):
    """Create AragonDAO vote and simulate passing vote on mainnet-fork.

    Args:
        target (dict): one of either CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAMS or EMERGENCY_DAO
        actions (list(tuple)): ("target addr", "fn_name", *args)
        description (str): Description of the on-chain governance proposal
    """
    top_stakeholders = stakeholders.get_vecrv_holders_data()

    # check if stakeholders meet quorum:
    assert sum([stakeholder.share * 100 for stakeholder in top_stakeholders]) > quorum

    # vote
    aragon = ape.Contract(voting_contract)
    for stakeholder in top_stakeholders:
        print(
            f"simulate vote for: {stakeholder.address} with "
            f"vote weight share: {stakeholder.share * 100}"
        )
        aragon.vote(vote_id, True, False, sender=ape.accounts[stakeholder.address])

    # sleep for a week so it has time to pass
    ape.chain.pending_timestamp += 86400 * 7

    # moment of truth - execute the vote!
    aragon.executeVote(vote_id, sender=ape.accounts[top_stakeholders[0].address])
