import ape
import pytest

from curve_dao import (CRYPTOSWAP_OWNER_PROXY, CURVE_DAO_OWNERSHIP,
                       CURVE_DAO_PARAM)
from curve_dao.modules.smartwallet_checker import (SMARTWALLET_CHECKER,
                                                   whitelist_vecrv_lock)
from curve_dao.simulate import simulate
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def crypto_factory_gauge():
    # JPEGpETH gauge
    yield ape.Contract("0x762648808ef8b25c6d92270b1c84ec97df3bed6b")


@pytest.fixture(scope="module")
def tricrypto_ng_gauge():
    # TriCryptoINV gauge
    yield ape.Contract("0x4fc86cd0f9b650280fa783e3116258e0e0496a2c")


def test_kill_factory_gauge(vote_deployer, crypto_factory_gauge):
    assert crypto_factory_gauge.is_killed() == False

    parameter_action = (
        CRYPTOSWAP_OWNER_PROXY,
        "set_killed",
        crypto_factory_gauge.address,
        True,
    )

    tx = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[parameter_action],
        description="test",
        vote_creator=vote_deployer,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    # this advances the chain one week from vote creation
    simulate(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    assert crypto_factory_gauge.is_killed() == True


def test_kill_ng_gauge(vote_deployer, tricrypto_ng_gauge):
    assert tricrypto_ng_gauge.is_killed() == False

    parameter_action = (
        tricrypto_ng_gauge.address,  # owner is factory admin
        "set_killed",
        True,
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

    # this advances the chain one week from vote creation
    simulate(
        vote_id=vote_id,
        voting_contract=CURVE_DAO_OWNERSHIP["voting"],
    )

    assert tricrypto_ng_gauge.is_killed() == True
