from curve_dao.modules import smartwallet_checker  # noqa

from .vote_utils import make_vote  # noqa

CURVE_DAO_OWNERSHIP = {
    "agent": "0x40907540d8a6c65c637785e8f8b742ae6b0b9968",
    "voting": "0xe478de485ad2fe566d49342cbd03e49ed7db3356",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 30,
}

CURVE_DAO_PARAM = {
    "agent": "0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f",
    "voting": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "token": "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2",
    "quorum": 15,
}

EMERGENCY_DAO = {
    "forwarder": "0xf409Ce40B5bb1e4Ef8e97b1979629859c6d5481f",
    "agent": "0x00669DF67E4827FCc0E48A1838a8d5AB79281909",
    "voting": "0x1115c9b3168563354137cdc60efb66552dd50678",
    "token": "0x4c0947B16FB1f755A2D32EC21A0c4181f711C500",
    "quorum": 51,
}

veCRV = "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2"
CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"
CURVE_DEPLOYER_2 = "0xbabe61887f1de2713c6f97e567623453d3C79f67"


def select_target(vote_type: str):

    match vote_type:
        case "ownership":
            return CURVE_DAO_OWNERSHIP
        case "parameter":
            return CURVE_DAO_PARAM
        case "emergency":
            return EMERGENCY_DAO
