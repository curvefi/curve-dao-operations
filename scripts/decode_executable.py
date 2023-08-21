import sys
import warnings

import ape
import click
from curve_dao.decoder_utils import decode_input
from curve_dao.vote_utils import (decode_vote_script,
                                  get_vote_description_from_ifps_hash)
from rich.console import Console as RichConsole

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)
DAO_VOTING_CONTRACTS = {
    "ownership": "0xE478de485ad2fe566d49342Cbd03E49ed7DB3356",
    "parameter": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "emergency": "0x1115c9b3168563354137cdc60efb66552dd50678",
}


def get_evm_script(vote_id: str, voting_contract: str) -> str:
    return ape.project.Voting.at(voting_contract).getVote(vote_id)["script"]


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
    script = get_evm_script(vote_id, DAO_VOTING_CONTRACTS[target])
    if not script:
        RICH_CONSOLE.log("[red] VoteID not found in any DAO voting contract [/red]")
        return
    snapshot_block = ape.project.Voting.at(DAO_VOTING_CONTRACTS[target]).getVote(
        vote_id
    )["snapshotBlock"]

    votes = decode_vote_script(script)
    new_vote_event = ape.project.Voting.at(DAO_VOTING_CONTRACTS[target]).StartVote
    all_new_vote_events = new_vote_event.query(
        "voteId",
        "metadata",
        start_block=snapshot_block - 1,
        stop_block=snapshot_block + 1,
    )
    vote_row = all_new_vote_events.loc[all_new_vote_events["voteId"] == vote_id]
    ipfs_hash = vote_row["metadata"].iloc[0]
    ipfs_hash = ipfs_hash[5:]
    description = get_vote_description_from_ifps_hash(ipfs_hash)
    RICH_CONSOLE.log(description)
    for vote in votes:
        formatted_output = vote["formatted_output"]
        RICH_CONSOLE.log(formatted_output)
