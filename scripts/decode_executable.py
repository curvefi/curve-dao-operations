import sys
import warnings

import ape
import click
from curve_dao.decoder_utils import decode_input
from curve_dao.vote_utils import (decode_vote_script,
                                  get_description_from_ipfs_hash,
                                  get_description_from_vote_id,
                                  get_vote_script)
from rich.console import Console as RichConsole

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
    "--target",
    "-t",
    type=click.Choice(["ownership", "parameter"]),
    required=True,
)
@click.option("--vote_id", "-v", type=int, default=0)
def decode(network, target: str, vote_id: int):

    RICH_CONSOLE.log(f"Decoding {target} VoteID: {vote_id}")

    # get script from voting data:
    script = get_vote_script(vote_id, target)
    if not script:
        RICH_CONSOLE.log("[red] VoteID not found in any DAO voting contract [/red]")
        return

    description = get_description_from_vote_id(vote_id, target)
    RICH_CONSOLE.log(description)

    votes = decode_vote_script(script)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        RICH_CONSOLE.log(formatted_output)
