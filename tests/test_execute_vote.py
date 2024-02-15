from ape import Contract, accounts

from curve_dao.addresses import get_dao_voting_contract
from curve_dao.vote_utils import execute


def test_execute(vote_id, vote_type):

    voting_contract = get_dao_voting_contract(vote_type)
    voting_contract = Contract(voting_contract)

    assert voting_contract.getVote(vote_id)["executed"] is False

    with accounts.use_sender("0x0000000000000000000000000000000000000000"):
        execute(vote_id, vote_type)

    assert voting_contract.getVote(vote_id)["executed"] is True


# need to input vote type and voteID of a passed but not executed vote
test_execute(vote_id=515, vote_type="ownership")
