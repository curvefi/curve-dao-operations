import ape
import click
from ape.logging import logger

from curve_dao import compile_actions, make_vote


@click.group()
def cli():
    pass


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="propose",
    short_help="Propose an on-chain Curve DAO vote",
)
@ape.cli.network_option()
@ape.cli.account_option()
@click.option("--votefile", "-vf", type=str, default="vote.yaml")
def whitelist(network, account, votefile):

    proposal = compile_actions(votefile)

    tx = make_vote(
        target=proposal["target"],
        actions=proposal["actions"],
        description=proposal["description"],
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")
