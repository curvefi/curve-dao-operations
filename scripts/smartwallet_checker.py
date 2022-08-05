import ape
import click
import pprint

from scripts.dao_utils import (
    CURVE_DAO_OWNERSHIP,
    CURVE_DEPLOYER_2,
    SMARTWALLET_WHITELIST,
)
from scripts.dao_utils import make_vote
from scripts.dao_utils.simulate import simulate


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
@click.option("--simulate_outcome", "-s", type=bool, default=False)
def _whitelist(network, account, address_to_whitelist, description, simulate_outcome):

    click.echo(f"Connected to {network}")
    click.echo(f"Creating vote to whitelist: {address_to_whitelist}")

    account = ape.accounts[account]
    click.echo(f"Proposer: {account}")

    tx = make_vote(
        target=CURVE_DAO_OWNERSHIP,
        actions=[(SMARTWALLET_WHITELIST, "approveWallet", address_to_whitelist)],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.__dict__["event_arguments"]["voteId"]
        break

    click.echo(f"Proposal submitted successfully! VoteId: {vote_id}")

    if simulate_outcome and "mainnet-fork" in network:
        click.echo("Simulating vote outcome...")
        simulate(
            vote_id=vote_id,
            quorum=CURVE_DAO_OWNERSHIP["quorum"],
            voting_contract=CURVE_DAO_OWNERSHIP["voting"],
        )

        # todo: add assertions here:

        click.echo("vote passed!")

    pprint.pprint(tx.__dict__)
