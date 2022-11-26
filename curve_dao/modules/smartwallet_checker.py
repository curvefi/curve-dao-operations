SMARTWALLET_CHECKER = "0xca719728Ef172d0961768581fdF35CB116e0B7a4"


def whitelist_vecrv_lock(addr):
    return (SMARTWALLET_CHECKER, "approveWallet", addr)
