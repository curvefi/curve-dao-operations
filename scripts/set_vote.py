import sys

import ape
import click
from rich.console import Console as RichConsole

from curve_dao import CURVE_DEPLOYER_2, make_vote, select_target
from curve_dao.modules.smartwallet_checker import whitelist_vecrv_lock

RICH_CONSOLE = RichConsole(file=sys.stdout)


@click.group(short_help="Smartwallet Checker Admin Control Operations")
def cli():
    """
    Command-line helper for managing Smartwallet Checker
    """


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="whitelist",
    short_help="Whitelist proposed contract to lock veCRV",
)
@ape.cli.network_option()
@ape.cli.account_option()
@click.option(
    "--address",
    "-w",
    type=str,
    default="0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86",  # some default address
)
@click.option("--description", "-d", type=str, default="test")
def whitelist(network, account, address, description):

    if network == "ethereum:mainnet-fork":
        account = ape.accounts[CURVE_DEPLOYER_2]

    RICH_CONSOLE.log(f"Connected to {network}")
    RICH_CONSOLE.log(f"Creating vote. Proposer: {account}")

    target = select_target("ownership")
    tx = make_vote(
        target=target,
        actions=[whitelist_vecrv_lock(address)],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    RICH_CONSOLE.log(f"Proposal submitted successfully! VoteId: {vote_id}")
