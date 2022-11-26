import ape
import pytest

from curve_dao import CURVE_DAO_OWNERSHIP
from curve_dao.modules.smartwallet_checker import (
    SMARTWALLET_CHECKER,
    whitelist_vecrv_lock,
)
from curve_dao.simulate import simulate
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def smartwallet_checker():
    yield ape.Contract(SMARTWALLET_CHECKER)


@pytest.fixture(scope="module")
def addr_to_whitelist():
    # cryptoriskteam msig:
    yield "0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86"


def test_whitelist(smartwallet_checker, addr_to_whitelist, vote_deployer):
    assert not smartwallet_checker.check(addr_to_whitelist)

    tx = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[whitelist_vecrv_lock(addr_to_whitelist)],
        description="test",
        vote_creator=vote_deployer,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    simulate(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    assert smartwallet_checker.check(addr_to_whitelist)
    assert 1 == 1
