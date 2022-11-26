import ape
import pytest

from curve_dao import CURVE_DAO_OWNERSHIP, CURVE_DAO_PARAM


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
