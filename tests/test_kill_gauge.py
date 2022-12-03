import ape
import pytest
import yaml
from ape.logging import logger

from curve_dao.compile_vote import _compile_actions
from curve_dao.simulate import simulate
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def vote_config():
    vote_yaml = """
    description: Kill Gauge

    kill_gauge:
        - 0xCFc25170633581Bf896CB6CDeE170e3E3Aa59503
    """
    return _compile_actions(yaml.safe_load(vote_yaml))


def test_kill_gauge(vote_config, vote_deployer):
    gauge_to_kill = "0xCFc25170633581Bf896CB6CDeE170e3E3Aa59503"
    gauge = ape.Contract(gauge_to_kill)
    assert not gauge.is_killed()

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

    if not gauge.is_killed():
        logger.info("Kill gauge failed!")
        assert False
