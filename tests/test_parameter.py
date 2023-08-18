import ape
import pytest

from curve_dao import CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAM
from curve_dao.modules.smartwallet_checker import (SMARTWALLET_CHECKER,
                                                   whitelist_vecrv_lock)
from curve_dao.simulate import simulate
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def tricrypto_pool():
    yield ape.Contract("0x5426178799ee0a0181a89b4f57efddfab49941ec")


def test_parameter_update(vote_deployer, tricrypto_pool):
    # TriCryptoINV
    future_A = 1707650
    future_gamma = 11809167829000
    future_time = 1693011177
    parameter_action = (
        tricrypto_pool.address,
        "ramp_A_gamma",
        future_A,
        future_gamma,
        future_time,
    )

    tx = make_vote(
        target=CURVE_DAO_OWNERSHIP,  # tricrypto-ng factory admin is OWNERSHIP agent
        actions=[parameter_action],
        description="test",
        vote_creator=vote_deployer,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    return
    simulate(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    # assert the parameter has updated
