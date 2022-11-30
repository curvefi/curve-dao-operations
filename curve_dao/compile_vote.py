import typing

import yaml

from curve_dao import select_target
from curve_dao.modules import gauge_utils, smartwallet_checker


def _load_vote_yaml(yaml_file: str) -> typing.Dict:
    with open("vote.yaml", "r") as stream:
        return yaml.safe_load(stream)


def _compile_actions(vote_configs: typing.Dict) -> typing.Dict:

    actions = []
    for key in vote_configs.keys():

        match key:
            case "whitelist":
                addrs = vote_configs[key]["addresses"]
                for addr in set(addrs):
                    action = smartwallet_checker.whitelist_vecrv_lock(addr)
                    if action:
                        actions.append(action)
            case "kill_gauge":
                addr = vote_configs[key]["addresses"]
                for addr in addrs:
                    action = gauge_utils.kill_gauge(addr)
                    if action:
                        actions.append(action)

    return {
        "target": select_target(vote_configs["target"]),
        "description": vote_configs["description"],
        "actions": actions,
    }


def compile_actions(yaml_file: str) -> typing.Dict:
    return _compile_actions(_load_vote_yaml(yaml_file))
