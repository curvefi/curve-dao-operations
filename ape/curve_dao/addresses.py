CURVE_DAO_OWNERSHIP = {
    "agent": "0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
    "voting": "0xE478de485ad2fe566d49342Cbd03E49ed7DB3356",
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

VOTING_ESCROW = "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2"
veCRV = VOTING_ESCROW
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"
# 2-coin factory cryptopools only;
# tricrypto-ng factory admin is already the OWNERSHIP agent
CRYPTOSWAP_OWNER_PROXY = "0x5a8fdC979ba9b6179916404414F7BA4D8B77C8A1"


def get_dao_voting_contract(vote_type: str):
    target = select_target(vote_type)
    return target["voting"]


def select_target(vote_type: str):

    match vote_type:
        case "ownership":
            return CURVE_DAO_OWNERSHIP
        case "parameter":
            return CURVE_DAO_PARAM
        case "emergency":
            return EMERGENCY_DAO
