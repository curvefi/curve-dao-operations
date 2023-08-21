import sys
import warnings

import ape
import click
from curve_dao.decoder_utils import decode_input
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


def get_inputs_with_names(abi, inputs):
    arg_names = []
    for i in range(len(inputs)):
        argname = abi.inputs[i].name
        arg_names.append(argname)

    inputs_with_names = list(zip(arg_names, inputs))
    return inputs_with_names


def format_fn_inputs(inputs_with_names):
    if len(inputs_with_names) == 0:
        return ""

    if len(inputs_with_names) == 1:
        name, arg = inputs_with_names[0]
        return f"    └─ [bold]{name}[/]: [yellow]{arg}[/]"

    formatted_args = ""
    for name, arg in inputs_with_names[:-1]:
        formatted_args += f"    ├─ [bold]{name}[/]: [yellow]{arg}[/]\n"
    name, arg = inputs_with_names[-1]
    formatted_args += f"    └─ [bold]{name}[/]: [yellow]{arg}[/]"
    return formatted_args


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
def decode_vote(network, target: str, vote_id: int):

    RICH_CONSOLE.log(f"Decoding {target} VoteID: {vote_id}")

    # get script from voting data:
    script = get_evm_script(vote_id, DAO_VOTING_CONTRACTS[target])
    if not script:
        RICH_CONSOLE.log("[red] VoteID not found in any DAO voting contract [/red]")
        return
    idx = 4

    votes = []
    while idx < len(script):

        # get target contract address:
        target = ape.Contract(script[idx : idx + 20])
        idx += 20

        length = int(script[idx : idx + 4].hex(), 16)
        idx += 4

        # calldata to execute for the dao:
        calldata = script[idx : idx + length]
        idx += length

        fn, inputs = decode_input(target, calldata)
        agent = None

        # print decoded vote:
        if calldata[:4].hex() == "0xb61d27f6":
            agent = target
            target = ape.Contract(inputs[0])
            fn, inputs = decode_input(target, inputs[2])
            inputs_with_names = get_inputs_with_names(fn, inputs)
            formatted_inputs = format_fn_inputs(inputs_with_names)
            RICH_CONSOLE.log(
                f"Call via agent: [yellow]{agent}[/]\n"
                f" ├─ [bold]To[/]: [green]{target}[/]\n"
                f" ├─ [bold]Function[/]: [yellow]{fn.name}[/]\n"
                f" └─ [bold]Inputs[/]: \n{formatted_inputs}\n"
            )
        else:
            inputs_with_names = get_inputs_with_names(fn, inputs)
            formatted_inputs = format_fn_inputs(inputs_with_names)
            RICH_CONSOLE.log(
                f"Direct call\n "
                f" ├─ [bold]To[/]: [green]{target}[/]\n"
                f" ├─ [bold]Function[/]: [yellow]{fn.name}[/]\n"
                f" └─ [bold]Inputs[/]: {formatted_inputs}\n"
            )

        vote = {
            "agent": agent.address if agent else None,
            "target": target.address,
            "function": fn.name,
            "inputs": inputs_with_names,
        }
        votes.append(vote)

    return votes
