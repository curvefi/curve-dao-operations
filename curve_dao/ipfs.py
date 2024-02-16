import json
import os

import ape
import requests

from .addresses import get_dao_voting_contract


def get_ipfs_hash_from_description(description: str):
    """Uploads vote description to IPFS and returns the IPFS hash.

    NOTE: needs environment variables for infura IPFS access. Please
    set up an IPFS project to generate project id and project secret!
    """
    text = json.dumps({"text": description})
    response = requests.post(
        "https://ipfs.infura.io:5001/api/v0/add",
        files={"file": text},
        auth=(os.getenv("IPFS_PROJECT_ID"), os.getenv("IPFS_PROJECT_SECRET")),
    )
    assert (
        200 <= response.status_code < 400
    ), f"POST to IPFS failed: {response.status_code}"
    return response.json()["Hash"]


def get_description_from_ipfs_hash(ipfs_hash: str) -> str:
    try:
        url = f"https://ipfs.io/ipfs/{ipfs_hash}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("text", "Text field not found")
    except requests.Timeout:
        return "IPFS timed out. Possibly the description is no longer pinned."
    except requests.ConnectionError as e:
        return f"IPFS connection error: {e}"
    except requests.HTTPError as e:
        return f"IPFS request error: {e}"


def get_ipfs_hash_from_vote_id(vote_type, vote_id):
    voting_contract_address = get_dao_voting_contract(vote_type)
    voting_contract = ape.project.Voting.at(voting_contract_address)
    snapshot_block = voting_contract.getVote(vote_id)["snapshotBlock"]
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
