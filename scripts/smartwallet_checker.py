import sys

import ape
import click
from rich.console import Console as RichConsole

from scripts.utils import CURVE_DEPLOYER_2, make_vote, select_target
from scripts.utils.simulate import simulate

RICH_CONSOLE = RichConsole(file=sys.stdout)
SMARTWALLET_WHITELIST = "0xca719728Ef172d0961768581fdF35CB116e0B7a4"


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
    RICH_CONSOLE.log(f"Creating vote to whitelist: {address}")
    RICH_CONSOLE.log(f"Proposer: {account}")

    target = select_target("ownership")
    tx = make_vote(
        target=target,
        actions=[(SMARTWALLET_WHITELIST, "approveWallet", address)],
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
            voting_contract=target["voting"],
        )

        checker = ape.Contract(SMARTWALLET_WHITELIST)
        assert checker.check(address)
        RICH_CONSOLE.log("Correct execution.")
