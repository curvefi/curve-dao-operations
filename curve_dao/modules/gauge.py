import ape

gauge_controller = "0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB"


class UnkillableGauge(Exception):
    pass


def _get_gauge_admin(addr):
    contract = ape.Contract(addr)
    if hasattr(contract, "factory"):
        factory = ape.Contract(contract.factory())
        admin = ape.Contract(factory.admin())
    elif hasattr(contract, "admin"):
        admin = ape.Contract(contract.admin())
    elif hasattr(contract, "owner"):
        admin = contract.owner()

    if hasattr(admin, "set_killed"):
        return admin.address

    raise UnkillableGauge


def kill_gauge(addr):

    gauge = ape.Contract(addr)
    if not gauge.is_killed():
        admin = _get_gauge_admin(addr)
        return (admin, "set_killed", addr, True)
    return ()
