import typing

import yaml

from curve_dao import select_target
from curve_dao.modules import gauge, smartwallet_checker, stableswap_params


def _load_vote_yaml(yaml_file: str) -> typing.Dict:
    with open("vote.yaml", "r") as stream:
        return yaml.safe_load(stream)


def _compile_actions(vote_configs: typing.Dict) -> typing.Dict:

    actions = []
    for key in vote_configs.keys():

        match key:
            case "whitelist":
                target = "ownership"
                addrs = vote_configs["whitelist"]
                addrs = [hex(addr) for addr in addrs]
                for addr in set(addrs):
                    action = smartwallet_checker.whitelist_vecrv_lock(addr)
                    if action:
                        actions.append(action)
            case "kill_gauge":
                target = "ownership"
                addrs = vote_configs["kill_gauge"]
                addrs = [hex(addr) for addr in addrs]
                for addr in addrs:
                    action = gauge.kill_gauge(addr)
                    if action:
                        actions.append(action)
            case "stableswap_params":
                target = "parameter"
                pools = vote_configs[key]["pools"]
                for pool in pools:
                    actions.append(
                        stableswap_params.pool_params(
                            pool["pool"],
                            pool["admin"],
                            pool["amplification"],
                            pool["fee"],
                            pool["admin_fee"],
                            pool["min_asymmetry"],
                        )
                    )

    return {
        "target": select_target(target),
        "description": vote_configs["description"],
        "actions": actions,
    }


def compile_actions(yaml_file: str) -> typing.Dict:
    return _compile_actions(_load_vote_yaml(yaml_file))
