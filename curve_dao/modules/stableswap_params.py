import ape
from ape.logging import logger


def pool_params(pool, admin, amplification, fee, admin_fee, min_asymmetry):

    contract = ape.Contract(pool)
    if contract.A() > amplification and min_asymmetry == 0:
        logger.error("Cannot lower amplification without min_asymmetry!")
        raise

    return (pool, admin, amplification, fee, admin_fee, min_asymmetry)
