import json
import os
import requests

import boa

from .addresses import get_dao_voting_contract



def get_ipfs_hash_from_description(description: str):
    """Uploads vote description to IPFS and returns the IPFS hash.

    NOTE: needs environment variables for pinata IPFS access. Please
    set up an IPFS project to generate api key and api secret!
    https://www.pinata.cloud/
    """

    headers = {
            "pinata_api_key": os.getenv("PINATA_API_KEY"),
            "pinata_secret_api_key": os.getenv("PINATA_API_SECRET")
        }

    response = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        json={"pinataContent": {"text": description}},
        headers=headers
    )

    assert (
        200 <= response.status_code < 400
    ), f"POST to IPFS failed: {response.status_code}"
    return response.json()["IpfsHash"]


def get_description_from_ipfs_hash(ipfs_hash: str):
    try:
        response = requests.post(
            f"https://ipfs.infura.io:5001/api/v0/get?arg={ipfs_hash}",
            auth=(os.getenv("IPFS_PROJECT_ID"), os.getenv("IPFS_PROJECT_SECRET")),
            timeout=5,
        )
        response.raise_for_status()
    except requests.Timeout:
        return "IPFS timed out.  Possibly the description is no longer pinned."
    except requests.ConnectionError as e:
        return f"IPFS connection error: {e}"
    except requests.HTTPError as e:
        return f"IPFS request error: {e}"

    response_string = response.content.decode("utf-8")
    json_string = []
    in_json = False
    for c in response_string:
        if c == "{":
            in_json = True
        if in_json:
            json_string.append(c)
        if c == "}":
            break
    json_string = "".join(json_string)
    return json.loads(json_string)


def get_ipfs_hash_from_vote_id(vote_type, vote_id):
    voting_contract_address = get_dao_voting_contract(vote_type)

    # voting_contract = ape.project.Voting.at(voting_contract_address)
    #voting = "contracts/Voting.json"

    boa.env.fork(f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}")

    voting_contract_address = get_dao_voting_contract(vote_type)
    voting_contract = boa.from_etherscan(voting_contract_address, name="VotingContract", api_key=os.getenv('ETHERSCAN_API_KEY'))

    # can't do ["snapshotBlock"], need to do [3] instead
    snapshot_block = voting_contract.getVote(vote_id)[3]

    # how to query events in boa? need this for voteID and metadata
    vote_events = voting_contract.StartVote.query(
        "voteId",
        "metadata",
        start_block=snapshot_block - 1,
        stop_block=snapshot_block + 1,
    )
    vote_row = vote_events.loc[vote_events["voteId"] == vote_id]
    ipfs_hash = vote_row["metadata"].iloc[0]
    ipfs_hash = ipfs_hash[5:]
    return ipfs_hash


def get_description_from_vote_id(vote_id, target):
    ipfs_hash = get_ipfs_hash_from_vote_id(target, vote_id)
    description = get_description_from_ipfs_hash(ipfs_hash)
    return description



# need to find out how to query events with boa: https://etherscan.io/tx/0x543634439bf556698c487acaf54c8ed4643f7bb68a7c4865380de66656d466bd#eventlog