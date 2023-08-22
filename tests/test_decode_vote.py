import ape
import pytest
from curve_dao.addresses import CURVE_DAO_OWNERSHIP
from curve_dao.modules.smartwallet_checker import (
    SMARTWALLET_CHECKER,
    whitelist_vecrv_lock,
)
from curve_dao.simulate import simulate
from curve_dao.vote_utils import decode_vote_script, get_vote_script, make_vote


def test_decode_vote_script_ownership(vote_deployer):
    vote_id = 404
    script = get_vote_script(vote_id, "ownership")
    votes = decode_vote_script(script)

    expected_votes = [
        {
            "agent": "0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
            "target": "0xbeF434E2aCF0FBaD1f0579d2376fED0d1CfC4217",
            "function": "price_w",
            "inputs": [],
        },
        {
            "agent": "0x40907540d8a6C65c637785e8f8B742ae6b0b9968",
            "target": "0xC9332fdCB1C491Dcc683bAe86Fe3cb70360738BC",
            "function": "add_market",
            "inputs": [
                ("token", "0x18084fbA666a33d37592fA2633fD49a74DD93a88"),
                ("A", 100),
                ("fee", 6000000000000000),
                ("admin_fee", 0),
                (
                    "_price_oracle_contract",
                    "0xbeF434E2aCF0FBaD1f0579d2376fED0d1CfC4217",
                ),
                ("monetary_policy", "0xb8687d7dc9d8fa32fabde63E19b2dBC9bB8B2138"),
                ("loan_discount", 90000000000000000),
                ("liquidation_discount", 60000000000000000),
                ("debt_ceiling", 50000000000000000000000000),
            ],
        },
    ]
    for vote, expected_vote in zip(votes, expected_votes):
        assert vote["agent"] == expected_vote["agent"]
        assert vote["target"] == expected_vote["target"]
        assert vote["function"] == expected_vote["function"]
        assert vote["inputs"] == expected_vote["inputs"]


def test_decode_vote_script_parameter(vote_deployer):
    vote_id = 69
    script = get_vote_script(vote_id, "parameter")
    votes = decode_vote_script(script)

    expected_votes = [
        {
            "agent": "0x4EEb3bA4f221cA16ed4A0cC7254E2E32DF948c5f",
            "target": "0xeCb456EA5365865EbAb8a2661B0c503410e9B347",
            "function": "commit_new_fee",
            "inputs": [
                ("_pool", "0xDC24316b9AE028F1497c275EB9192a3Ea0f67022"),
                ("new_fee", 1000000),
                ("new_admin_fee", 5000000000),
            ],
        }
    ]
    for vote, expected_vote in zip(votes, expected_votes):
        assert vote["agent"] == expected_vote["agent"]
        assert vote["target"] == expected_vote["target"]
        assert vote["function"] == expected_vote["function"]
        assert vote["inputs"] == expected_vote["inputs"]
