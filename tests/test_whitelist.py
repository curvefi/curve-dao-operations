import ape
import pytest

from curve_dao.modules.smartwallet_checker import (
    SMARTWALLET_CHECKER,
    whitelist_vecrv_lock,
)
from curve_dao.simulate import simulate
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def smartwallet_checker():
    return ape.Contract(SMARTWALLET_CHECKER)


@pytest.fixture
def addr_to_whitelist():
    # cryptoriskteam msig:
    return "0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86"


def test_simulate_whitelist(
    smartwallet_checker, dao_ownership, addr_to_whitelist, deployer
):
    assert not smartwallet_checker.check(addr_to_whitelist)

    tx = make_vote(
        target=dao_ownership,
        actions=[whitelist_vecrv_lock(addr_to_whitelist)],
        description="test",
        vote_creator=deployer,
    )
    vote_id = tx.decode_logs().event_arguments["voteId"]

    simulate(
        vote_id=vote_id,
        voting_contract=dao_ownership["voting"],
    )

    assert smartwallet_checker.check(addr_to_whitelist)
