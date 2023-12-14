from curve_dao.vote_utils import decode_vote_data, get_vote_data


def test_vote_data_ended(vote_deployer):
    vote_type = "ownership"
    vote_id = 404
    data = get_vote_data(vote_id, vote_type)
    decode = decode_vote_data(data, vote_type)

    expected_data = {
        "start": 1692475643,
        "end": 1693080443,
        "votingPower": 625546146444045385843289050,
        "open": False,
        "executed": True,
        "yes": 459475144503577289039481284,
        "no": 0,
        "support": 1.0,
        "quorum": 0.7345183838402511,
    }

    assert decode["start"] == expected_data["start"]
    assert decode["end"] == expected_data["end"]
    assert decode["end"] == expected_data["start"] + 604800
    assert decode["votingPower"] == expected_data["votingPower"]
    assert decode["open"] == expected_data["open"]
    assert decode["executed"] == expected_data["executed"]
    assert decode["yes"] == expected_data["yes"]
    assert decode["no"] == expected_data["no"]
    assert decode["support"] == expected_data["support"]
    assert decode["quorum"] == expected_data["quorum"]
