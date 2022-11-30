import ape

smartwallet_check = ape.Contract("0xca719728Ef172d0961768581fdF35CB116e0B7a4")


def whitelist_vecrv_lock(addr):
    if not smartwallet_check.check(addr):
        return (smartwallet_check.address, "approveWallet", addr)
    return ()
