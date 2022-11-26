import ape
import click
from ape.logging import logger

from curve_dao import make_vote, select_target
from curve_dao.modules.smartwallet_checker import whitelist_vecrv_lock


@click.group()
def cli():
    pass


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name="whitelist",
    short_help="Whitelist proposed contract to lock veCRV",
)
@ape.cli.network_option()
@ape.cli.account_option()
@click.option("--addr", "-a", type=str, required=True)
@click.option("--description", "-d", type=str, required=True)
def whitelist(network, account, addr, description):

    target = select_target("ownership")
    tx = make_vote(
        target=target,
        actions=[whitelist_vecrv_lock(addr)],
        description=description,
        vote_creator=account,
    )

    for log in tx.decode_logs():
        vote_id = log.event_arguments["voteId"]
        break

    logger.info(f"Proposal submitted successfully! VoteId: {vote_id}")
