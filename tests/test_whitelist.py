import ape
import pytest
import yaml
from ape.logging import logger

from curve_dao.compile_vote import _compile_actions
from curve_dao.modules.smartwallet_checker import SMARTWALLET_CHECKER
from curve_dao.simulate import simulate
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def addr_to_whitelist():
    # cryptoriskteam msig:
    yield "0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86"


@pytest.fixture(scope="module")
def vote_config():
    vote_yaml = """
    description: Allow cryptoriskteam msig to lock vecrv

    whitelist:
        - "0xE6DA683076b7eD6ce7eC972f21Eb8F91e9137a17"
    """
    return _compile_actions(yaml.safe_load(vote_yaml))


def test_whitelist(addr_to_whitelist, vote_config, vote_deployer):
    smartwallet_check = ape.Contract(SMARTWALLET_CHECKER)
    assert not smartwallet_check.check(addr_to_whitelist)

    tx = make_vote(
        target=vote_config["target"],
        actions=vote_config["actions"],
        description=vote_config["description"],
        vote_creator=vote_deployer,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    simulate(
        vote_id=vote_id,
        voting_contract=vote_config["target"]["voting"],
    )

    if not smartwallet_check.check(addr_to_whitelist):
        logger.info("Whitelist failed!")
        assert False

    logger.info("Successful Whitelist!")
