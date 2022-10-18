from .constants import *  # noqa
from .vote_utils import make_vote  # noqa


def select_target(vote_type: str):

    match vote_type:
        case "ownership":
            return CURVE_DAO_OWNERSHIP
        case "parameter":
            return CURVE_DAO_PARAM
        case "emergency":
            return EMERGENCY_DAO
