import sys
import ape
import warnings
import click

from rich.console import Console as RichConsole

from scripts.utils.decoder_utils import decode_input

warnings.filterwarnings("ignore")

RICH_CONSOLE = RichConsole(file=sys.stdout)
DAO_VOTING_CONTRACTS = {
    "ownership": "0xe478de485ad2fe566d49342cbd03e49ed7db3356",
    "parameter": "0xbcff8b0b9419b9a88c44546519b1e909cf330399",
    "emergency": "0x1115c9b3168563354137cdc60efb66552dd50678"
}


def get_evm_script(vote_id: str) -> str:
    
    evm_script = ""
    for name, voting_contract in DAO_VOTING_CONTRACTS.items():
        
        try:
            
            aragon = ape.project.Voting.at(voting_contract)
            proposal_data = aragon.getVote(vote_id)
            RICH_CONSOLE.log(f"Voting contract: {voting_contract} ({name})")
            evm_script = proposal_data["script"]

        except:
            
            continue
        
    return evm_script
    

@click.group(
    short_help="Curve DAO proposal decoder",
)
def cli():
    """
    Command-line helper for managing Smartwallet Checker
    """


@cli.command(
    cls=ape.cli.NetworkBoundCommand,
    name = "decode",
    short_help="Decode Curve DAO proposal by Vote ID",
)
@ape.cli.network_option()
@click.option("--vote_id", "-v", type=int, default=0)
def decode_vote(network, vote_id: int):
    
    RICH_CONSOLE.log(f"Decoding VoteID: {vote_id}")
    
    # get script from voting data:
    script = get_evm_script(vote_id)
    if not script:
        RICH_CONSOLE.log("[red] VoteID not found in any DAO voting contract [/red]")
        return
    idx = 4   
    
    while idx < len(script):
        
        # get target contract address:
        target = ape.Contract(script[idx : idx + 20])
        idx += 20
        
        length = int(script[idx : idx + 4].hex(), 16)
        idx += 4
        
        # calldata to execute for the dao:
        calldata = script[idx : idx + length]
        idx += length
        
        _, inputs = decode_input(target, calldata)
        
        # print decoded vote:
        if calldata[:4].hex() == "0xb61d27f6":
            
            agent_target = ape.Contract(inputs[0])
            fn, inputs = decode_input(agent_target, inputs[2])
            RICH_CONSOLE.log(
                f"Call via agent ({target}):\n ├─ To: {agent_target}\n"
                f" ├─ Function: {fn}\n └─ Inputs: {inputs}\n"
            )
        else:

            fn, inputs = decode_input(target, calldata)
            RICH_CONSOLE.log(
                f"Direct call:\n ├─ To: {target}\n ├─ Function: {fn}\n └─ Inputs: {inputs}"
            )
