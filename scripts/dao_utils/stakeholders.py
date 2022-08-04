import ape
from scripts.dao_utils import veCRV
from dataclasses import dataclass
from typing import List


# TOP veCRV HOLDERS, derived from: https://dao.curve.fi/vote/ownership/196
TOP_HOLDERS = [
    "0x989AEb4d175e16225E39E87d0D97A3360524AD80",
    "0x7a16fF8270133F063aAb6C9977183D9e72835428",
    "0xF89501B77b2FA6329F94F5A05FE84cEbb5c8b1a0",
    "0x9B44473E223f8a3c047AD86f387B80402536B029",
    "0x425d16B0e08a28A3Ff9e4404AE99D78C0a076C5A",
    "0x32D03DB62e464c9168e41028FFa6E9a05D8C6451",
    "0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6",
]


@dataclass
class VotingEscrowStakeholder:
    address: str
    balance: int
    share: float


def get_vecrv_holders_data(vecrv_holders: List = TOP_HOLDERS) -> List:

    curve_vecrv_contract = ape.project.VotingEscrow.at(veCRV)
    total_vecrv_supply = curve_vecrv_contract.totalSupply()
    vecrv_holders_data = []
    for vecrv_holder in vecrv_holders:

        vecrv_balance = curve_vecrv_contract.balanceOf(vecrv_holder)

        vecrv_holders_data.append(
            VotingEscrowStakeholder(
                address=vecrv_holder,
                balance=vecrv_balance,
                share=vecrv_balance / total_vecrv_supply,
            )
        )

    return vecrv_holders_data
