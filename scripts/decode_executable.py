import sys
import warnings
import click
from rich.console import Console as RichConsole

# need to find a way how to query events for ipfs hash
from curve_dao.ipfs import get_description_from_vote_id

from curve_dao.vote_utils import (
    MissingVote,
    decode_vote_data,
    decode_vote_script,
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
    name="decode",
    short_help="Decode Curve DAO proposal by Vote ID",
)

@click.option(
    "--vote-type",
    "-t",
    type=click.Choice(["ownership", "parameter"]),
    required=True,
)

@click.option(
    "--vote-id", 
    "-v", 
    type=int, 
    required=True)


def decode(vote_type: str, vote_id: int):
    """
    Function to decode Curve DAO votes.

    Decoding with: $ python3 scripts/decode_executable.py --vote-type ownership --vote-id 100
    """

    RICH_CONSOLE.log(f"Decoding {vote_type} VoteID: {vote_id}")

    try:
        script = get_vote_script(vote_id, vote_type)
    except MissingVote:
        RICH_CONSOLE.log(
            f"[red] VoteID not found in the {vote_type} DAO voting contract [/red]"
        )
        return

    # need to find a way to query events with boa to fetch the ipfs link and description of the vote.
    try:
        description = get_description_from_vote_id(vote_id, vote_type)
        RICH_CONSOLE.log(description)
    except:
        pass

    # decoding the vote script
    votes = decode_vote_script(script)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        RICH_CONSOLE.log(formatted_output)

    # fetching vote data
    data = get_vote_data(vote_id, vote_type)

    # decoding vote data
    results = decode_vote_data(data, vote_type)
    RICH_CONSOLE.log(results["formatted_output"])


if __name__ == '__main__':
    decode()
