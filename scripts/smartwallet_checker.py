import sys
import ape
import click
import pprint

from scripts.utils import (
    CURVE_DAO_OWNERSHIP,
    CURVE_DEPLOYER_2,
    SMARTWALLET_WHITELIST,
)
from scripts.utils import make_vote
from scripts.utils.simulate import simulate
from rich.console import Console as RichConsole

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
@click.option("--account", "-a", type=str, default=CURVE_DEPLOYER_2)
@click.option(
    "--address_to_whitelist",
    "-w",
    type=str,
    default="0xa2482aA1376BEcCBA98B17578B17EcE82E6D9E86",  # some default address
)
@click.option("--description", "-d", type=str, default="test")
def _whitelist(network, account, address_to_whitelist, description):

    RICH_CONSOLE.log(f"Connected to {network}")
    RICH_CONSOLE.log(f"Creating vote to whitelist: {address_to_whitelist}")

    account = ape.accounts[account]
    RICH_CONSOLE.log(f"Proposer: {account}")

    tx = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[(SMARTWALLET_WHITELIST, "approveWallet", address_to_whitelist)],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    RICH_CONSOLE.log(f"Proposal submitted successfully! VoteId: {vote_id}")

    if network == "ethereum:mainnet-fork":
        simulate(
            vote_id=vote_id,
            voting_contract=CURVE_DAO_OWNERSHIP["voting"],
        )

        # todo: add assertions here:

        RICH_CONSOLE.log("vote passed!")

    RICH_CONSOLE.log(pprint.pformat(tx, indent=4))
    