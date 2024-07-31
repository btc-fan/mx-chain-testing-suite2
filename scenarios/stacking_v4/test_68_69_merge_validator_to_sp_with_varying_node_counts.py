# Config:
# -num-validators-per-shard 10
# -num-waiting-validators-per-shard 6
# -num-validators-meta 10
# -num-waiting-validators-meta 6
# max nr of nodes that a SP should have = 10% * total num validators (=40)  = 4

# Steps :
# - We have Addresses A B C and D
# - 1) Stake 4 nodes with B in epoch 4
# - 2) Stake 2 nodes with C in epoch 4
# - 3) Stake 2 nodes with D in epoch 4
# - 4) Create a delegation contract with A
# - 5) Merge C nodes in A's contract - should succeed
# - 6) Merge D nodes in A's contract - should succeed
# - 7) Merge B nodes in A's contract - should fail

import pytest

from core.chain_commander import *
from core.delegation import *
from core.get_delegation_info import get_delegation_contract_address_from_tx
from core.get_transaction_info import check_if_error_is_present_in_tx
from core.staking import *

# TODO Re-check later on why Epoch 3 is not working properly
EPOCHS_ID = [4, 5, 6]


def epoch_id(val):
    return f"EPOCH-{val}"


def main():
    print("Happy testing")


# TODO Uncoment test after we check the flow manually and ensure that there is NOT a bug


@pytest.mark.parametrize("epoch", EPOCHS_ID, indirect=True, ids=epoch_id)
def XXXtest_68_69_merge_validator_to_sp_with_varying_node_counts(blockchain, epoch):
    # === PRE-CONDITIONS ==============================================================
    assert True == is_chain_online()
    # mint addresses
    AMOUNT_TO_MINT = "50000" + "000000000000000000"

    _A = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))
    _B = Wallet(Path(WALLETS_FOLDER + "/sd_2_wallet_key_2.pem"))
    _C = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))
    _D = Wallet(Path(WALLETS_FOLDER + "/sd_2_wallet_key_4.pem"))

    # check minting request will succeed
    assert "success" in _A.set_balance(AMOUNT_TO_MINT)
    assert "success" in _B.set_balance(AMOUNT_TO_MINT)
    assert "success" in _C.set_balance(AMOUNT_TO_MINT)
    assert "success" in _D.set_balance(AMOUNT_TO_MINT)

    # add some blocks
    response = add_blocks(5)
    assert "success" in response
    time.sleep(0.5)

    # check balances
    assert _A.get_balance() == AMOUNT_TO_MINT
    assert _B.get_balance() == AMOUNT_TO_MINT
    assert _C.get_balance() == AMOUNT_TO_MINT
    assert _D.get_balance() == AMOUNT_TO_MINT

    # go to needed epoch
    time.sleep(1)
    response = add_blocks_until_epoch_reached(epoch)
    assert "success" in response

    # === STEP 1 ===============================================================
    # 1) Stake 4 nodes with B
    VALIDATOR_KEY_1 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_1.pem"))
    VALIDATOR_KEY_2 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_2.pem"))
    VALIDATOR_KEY_3 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_3.pem"))
    VALIDATOR_KEY_4 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_4.pem"))
    B_valid_keys_list = [
        VALIDATOR_KEY_1,
        VALIDATOR_KEY_2,
        VALIDATOR_KEY_3,
        VALIDATOR_KEY_4,
    ]

    # stake
    tx_hash = stake(_B, B_valid_keys_list)

    # move on until tx is success
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check bls keys statuses
    for key in B_valid_keys_list:
        if epoch == 3:
            assert key.get_status(_B.public_address()) == "queued"
        else:
            assert key.get_status(_B.public_address()) == "staked"

    # check if owner is B
    for key in B_valid_keys_list:
        assert key.belongs_to(_B.public_address())

    # === STEP 2 ================================================================
    # 2) Stake 2 nodes with C
    VALIDATOR_KEY_5 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_5.pem"))
    VALIDATOR_KEY_6 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_6.pem"))
    C_valid_keys_list = [VALIDATOR_KEY_5, VALIDATOR_KEY_6]

    # stake
    tx_hash = stake(_C, C_valid_keys_list)

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check bls keys statuses
    for key in C_valid_keys_list:
        if epoch == 3:
            assert key.get_status(_C.public_address()) == "queued"
        else:
            assert key.get_status(_C.public_address()) == "staked"

    # check if owner is C
    for key in C_valid_keys_list:
        assert key.belongs_to(_C.public_address())

    # === STEP 3 ============================================================
    # 3) Stake 2 nodes with D
    VALIDATOR_KEY_7 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_7.pem"))
    VALIDATOR_KEY_8 = ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_8.pem"))
    D_valid_keys_list = [VALIDATOR_KEY_7, VALIDATOR_KEY_8]

    # stake
    tx_hash = stake(_D, D_valid_keys_list)

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check bls keys statuses
    for key in D_valid_keys_list:
        if epoch == 3:
            assert key.get_status(_D.public_address()) == "queued"
        else:
            assert key.get_status(_D.public_address()) == "staked"

    # check if owner is B
    for key in D_valid_keys_list:
        assert key.belongs_to(_D.public_address())

    # === STEP 4 ============================================================
    # 4) Create a delegation contract with A

    # create contract
    tx_hash = create_new_delegation_contract(_A)

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # get delegation contract address
    DELEGATION_CONTRACT_ADDRESS = get_delegation_contract_address_from_tx(tx_hash)

    # === STEP 5 ============================================================
    # 5) Merge C nodes in A's contract - should succeed
    # 5.1 - send a whitelist for merge from A to C
    tx_hash = whitelist_for_merge(_A, _C, DELEGATION_CONTRACT_ADDRESS)

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # 5.2 - send merging tx from C
    tx_hash = merge_validator_to_delegation_with_whitelist(
        _C, DELEGATION_CONTRACT_ADDRESS
    )

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check if keys from C were transfered to A's contract
    for key in C_valid_keys_list:
        assert key.belongs_to(DELEGATION_CONTRACT_ADDRESS)

    # check if keys are still staked
    for key in C_valid_keys_list:
        if epoch == 3:
            assert key.get_status(DELEGATION_CONTRACT_ADDRESS) == "queued"
        else:
            assert key.get_status(DELEGATION_CONTRACT_ADDRESS) == "staked"

    # === STEP 6 ==================================================
    # 6) Merge D nodes in A's contract - should succeed
    # 6.1 - send a whitelist for merge from A to D
    tx_hash = whitelist_for_merge(_A, _D, DELEGATION_CONTRACT_ADDRESS)

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # 6.2 - send merging tx from A
    tx_hash = merge_validator_to_delegation_with_whitelist(
        _D, DELEGATION_CONTRACT_ADDRESS
    )

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check if keys from C were transfered to A's contract
    for key in C_valid_keys_list:
        assert key.belongs_to(DELEGATION_CONTRACT_ADDRESS)

    # check if keys are still staked / queued
    for key in C_valid_keys_list:
        if epoch == 3:
            assert key.get_status(DELEGATION_CONTRACT_ADDRESS) == "queued"
        else:
            assert key.get_status(DELEGATION_CONTRACT_ADDRESS) == "staked"

    # === STEP 7 ===============================================================
    # 7) Merge B nodes in A's contract - should fail
    # 7.1 - send a whitelist for merge from A to B
    tx_hash = whitelist_for_merge(_A, _B, DELEGATION_CONTRACT_ADDRESS)

    # move few blocks and check tx
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # 7.2 - send merging tx from B
    tx_hash = merge_validator_to_delegation_with_whitelist(
        _B, DELEGATION_CONTRACT_ADDRESS
    )

    assert add_blocks_until_tx_fully_executed(tx_hash) == "fail"
    # check reason of failure
    assert check_if_error_is_present_in_tx("number of nodes is too high", tx_hash)

    # make sure all checks were done in needed epoch
    assert proxy_default.get_network_status().epoch_number == epoch
    # === FINISH ===============================================================


if __name__ == "__main__":
    main()