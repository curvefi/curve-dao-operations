import sys
import warnings

import ape
import click
from rich.console import Console as RichConsole

from curve_dao.ipfs import get_description_from_vote_id
from curve_dao.vote_utils import (
    decode_vote_script,
    format_data,
    get_vote_data,
    get_vote_script,
)

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)


@click.group(
    short_help="Curve DAO proposal decoder",
)
def cli():
    """
    Command-line helper for managing Smartwallet Checker
    """


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="decode",
    short_help="Decode Curve DAO proposal by Vote ID",
)
@ape.cli.network_option()
@click.option(
    "--vote-type",
    "-t",
    type=click.Choice(["ownership", "parameter"]),
    required=True,
)
@click.option("--vote-id", "-v", type=int, required=True)
def decode(network, vote_type: str, vote_id: int):

    RICH_CONSOLE.log(f"Decoding {vote_type} VoteID: {vote_id}")

    # get script from voting data:
    script = get_vote_script(vote_id, vote_type)
    if not script:
        RICH_CONSOLE.log("[red] VoteID not found in any DAO voting contract [/red]")
        return

    description = get_description_from_vote_id(vote_id, vote_type)
    RICH_CONSOLE.log(description)

    votes = decode_vote_script(script)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        RICH_CONSOLE.log(formatted_output)

    data = get_vote_data(vote_id, vote_type)
    results = format_data(data, vote_type)
    RICH_CONSOLE.log(results)
