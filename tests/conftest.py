import ape
import pytest

from curve_dao.addresses import CRV, CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAM, VOTING_ESCROW


@pytest.fixture(scope="module")
def ownership_agent():
    return ape.Contract(CURVE_DAO_OWNERSHIP["agent"])


@pytest.fixture(scope="module")
def ownership_voting():
    return ape.Contract(CURVE_DAO_OWNERSHIP["voting"])


@pytest.fixture(scope="module")
def parameter_agent():
    return ape.Contract(CURVE_DAO_PARAM["agent"])


@pytest.fixture(scope="module")
def parameter_voting():
    return ape.Contract(CURVE_DAO_PARAM["voting"])


@pytest.fixture(scope="module")
def vote_deployer():
    """
    Fund test user account with CRV and then lock for >= 2500 veCRV.

    Since we fork mainnet for tests, we need a "random" account to avoid
    cooldown issues with the real user creating a vote in the same period.
    """
    user = ape.accounts.test_accounts[0]
    crv_whale = ape.accounts["0x7a16ff8270133f063aab6c9977183d9e72835428"]
    crv_token = ape.Contract(CRV)
    voting_escrow = ape.Contract(VOTING_ESCROW)
    # greater than 2500 so we can avoid fiddly issues
    amount = 3000 * 10**18
    crv_token.transfer(user.address, amount, sender=crv_whale)
    # max lock for 4 years
    locktime = ape.chain.pending_timestamp + 86400 * 365 * 4
    crv_token.approve(voting_escrow.address, amount, sender=user)
    voting_escrow.create_lock(amount, locktime, sender=user)
    return user
