# these utility scripts are used to prepare, simulate and broadcast votes within Curve's DAO
# modify the constants below according the the comments, and then use `simulate` in
# a forked mainnet to verify the result of the vote prior to broadcasting on mainnet
#
# NOMENCLATURE:
#
# target: the intended target of the vote, should be one of the above constant dicts
# sender: address to create the vote from - you will need to modify this prior to mainnet use
# action: a list of calls to perform in the vote, formatted as a lsit of tuples
#         in the format (target, function name, *input args).
#         for example, to call:
#         GaugeController("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB").add_gauge("0xFA712...", 0, 0)
#
#         use the following:
#         [("0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB", "add_gauge", "0xFA712...", 0, 0),]
#
#         commonly used addresses:
#         GaugeController - 0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB
#         GaugeProxy - 0x519AFB566c05E00cfB9af73496D00217A630e4D5
#         PoolProxy - 0xeCb456EA5365865EbAb8a2661B0c503410e9B347
# description: description of the vote, will be pinned to IPFS

# ------- CONSTANTS --------- #
# addresses related to the DAO - these should not need modification

from .vote_utils import make_vote

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
SMARTWALLET_WHITELIST = "0xca719728Ef172d0961768581fdF35CB116e0B7a4"
CONVEX_VOTERPROXY = "0x989AEB4D175E16225E39E87D0D97A3360524AD80"
CURVE_DEPLOYER_2 = "0xbabe61887f1de2713c6f97e567623453d3C79f67"
