import pytest
import yaml

from curve_dao.compile_vote import _compile_actions
from curve_dao.modules.smartwallet_checker import smartwallet_check
from curve_dao.simulate import simulate
from curve_dao.vote_utils import make_vote


@pytest.fixture(scope="module")
def addr_to_whitelist():
    # cryptoriskteam msig:
    yield "0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86"


@pytest.fixture(scope="module")
def whitelist_vote_config():
    vote_yaml = """
    target: ownership
    description: Allow cryptoriskteam msig to lock vecrv

    whitelist:
    addresses:
        - "0xE6DA683076b7eD6ce7eC972f21Eb8F91e9137a17"
    """
    return _compile_actions(yaml.safe_load(vote_yaml))


def test_whitelist(addr_to_whitelist, whitelist_vote_config, vote_deployer):
    assert not smartwallet_check.check(addr_to_whitelist)

    tx = make_vote(
        target=whitelist_vote_config["target"],
        actions=whitelist_vote_config["actions"],
        description=whitelist_vote_config["description"],
        vote_creator=vote_deployer,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    simulate(
        vote_id=vote_id,
        voting_contract=whitelist_vote_config["target"]["voting"],
    )

    assert smartwallet_check.check(addr_to_whitelist)
