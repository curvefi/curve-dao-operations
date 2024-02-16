import sys
import warnings

import ape
import click
from ape.cli import get_user_selected_account
from rich.console import Console as RichConsole

from curve_dao.vote_utils import (
    EVMCallsReverted,
    NoFunds,
    NoSigner,
    execute,
    get_execution_status,
)

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)


@click.group(short_help="Curve DAO vote executor")
def cli():
    """
    Command-line helper for executing passed DAO votes.
    """


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="execute",
    short_help="Execute successfully passed Curve DAO votes.",
)
@ape.cli.network_option()
@click.option(
    "--vote-type",
    "-t",
    type=click.Choice(["ownership", "parameter"]),
    required=True,
)
@click.option("--vote-id", "-v", type=int, required=True)
@click.option(
    "--simulate",
    "-s",
    type=bool,
    default=True,
)
def execute_vote(network, vote_type: str, vote_id: int, simulate: bool):
    """
    Executes a vote based on the vote type and ID.

    Parameters:
    - vote_type: Vote type: "ownership" or "parameter"
    - vote_id: VoteID to execute.
    - simulate: Whether to simulate the transaction or not. Default is to simulate.
    """

    executable_status = get_execution_status(vote_id, vote_type)

    if executable_status:

        try:

            if not simulate:
                RICH_CONSOLE.log(
                    f"Executing {vote_type} VoteID: {vote_id}", style="bold"
                )

                account = get_user_selected_account("Select account to use")
                RICH_CONSOLE.log(f"You selected {account.address}.")

                with ape.accounts.use_sender(account):
                    execute(vote_id, vote_type)

                RICH_CONSOLE.log("Vote successfully executed.", style="green")

            else:
                RICH_CONSOLE.log(
                    f"Simulating the execution of {vote_type} VoteID: {vote_id}",
                    style="bold",
                )

                with ape.accounts.use_sender(
                    "0x0000000000000000000000000000000000000000"
                ):
                    execute(vote_id, vote_type)

                RICH_CONSOLE.log("Vote successfully simulated.", style="green")

        except NoSigner:
            RICH_CONSOLE.log("Error: The transaction was not signed", style="red")

        except EVMCallsReverted:
            RICH_CONSOLE.log("Error: The function call was reverted.", style="red")

        except NoFunds:
            RICH_CONSOLE.log(
                "Error: The signer does not have enough funds to execute the transaction.",
                style="red",
            )

    else:
        RICH_CONSOLE.log("Vote can not be executed.", style="red")
