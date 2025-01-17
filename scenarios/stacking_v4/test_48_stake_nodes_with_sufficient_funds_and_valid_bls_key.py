import pytest

from core.chain_commander import *
from core.get_staking_info import get_total_staked
from core.staking import *
from utils.logger import logger

# Steps:
# 1) Stake with A 2 nodes
# 2) check if balance is - (5000 + gas fees)
# 3) check with getTotalStaked that has 5000 egld staked
# 4) check with getOwner if staked keys belongs to A
# 5) check with getBlsKeysStatus if keys are staked
# do this in epoch 3, 4, 5 and 6


# TODO Re-check later on why Epoch 3 is not working properly
EPOCHS_ID = [4, 5]


def epoch_id(val):
    return f"EPOCH-{val}"


def main():
    logger.info("Happy testing")


@pytest.mark.parametrize("epoch", EPOCHS_ID, indirect=True, ids=epoch_id)
def test_48_stake_nodes_with_sufficient_funds_and_valid_bls_key(blockchain, epoch):
    # === PRE-CONDITIONS ==============================================================
    assert True == is_chain_online()
    AMOUNT_TO_MINT = "6000" + "000000000000000000"

    _A = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))

    # check if minting is successful
    assert "success" in _A.set_balance(AMOUNT_TO_MINT)

    # add some blocks
    response = add_blocks(5)
    assert "success" in response
    time.sleep(0.5)

    # check balance
    assert _A.get_balance() == AMOUNT_TO_MINT

    # move to epoch
    assert "success" in add_blocks_until_epoch_reached(epoch)

    # === STEP 1 ==============================================================
    # 1) Stake with A 2 nodes
    VALIDATOR_KEY_1 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_1.pem"))
    VALIDATOR_KEY_2 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_2.pem"))
    A_Keys = [VALIDATOR_KEY_1, VALIDATOR_KEY_2]

    tx_hash = stake(_A, A_Keys)

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # === STEP 2 ==============================================================
    # 2) check balance of A to be - (5000+gas fees)
    assert int(_A.get_balance()) < int(AMOUNT_TO_MINT) - 5000

    # === STEP 3 ==============================================================
    # 3) check total stake of A
    total_staked = get_total_staked(_A.public_address())
    assert total_staked == "5000" + "000000000000000000"

    # === STEP 4 ==============================================================
    # 4) check owner of keys
    for key in A_Keys:
        assert key.belongs_to(_A.public_address())

    # === STEP 5 ==============================================================
    # 5) check with getBlsKeysStatus if keys are staked or queued if epoch 3
    for key in A_Keys:
        if epoch == 3:
            assert key.get_status(_A.public_address()) == "queued"
        else:
            assert key.get_status(_A.public_address()) == "staked"

    # make sure all checks were done in needed epoch
    assert proxy_default.get_network_status().epoch_number == epoch
    # === FINISH ===============================================================


if __name__ == "__main__":
    main()
