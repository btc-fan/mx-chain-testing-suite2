from pathlib import Path

from config.constants import VALIDATOR_KEYS_FOLDER, WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from core.staking import create_and_sign_relayed_staking_tx
from models.validatorKey import ValidatorKey
from models.wallet import Wallet


# TODO Failed test due to bug in progress
def test_relayed_v3_inner_tx_normal_stake(blockchain):
    """
    Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender and relayer wallets.
    4. Create and sign a normal stake transaction (inner transaction) from sender to staking contract with relayer included.
    5. Create and sign a relayed v3 transaction that includes the inner stake transaction.
    6. Send the relayed v3 transaction and verify its successful execution.
    7. Retrieve and verify the final nonces and balances for sender and relayer wallets.
       - Ensure the sender's nonce is incremented by 1.
       - Ensure the relayer's nonce is incremented by 1.
       - Ensure the sender's balance is decremented by the stake amount.
       - Ensure the relayer's balance is decremented by the gas used for the transaction.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))

    # Set balances for wallets
    SENDER_AMOUNT = "5001" + "000000000000000000"  # 5001 EGLD in wei
    RELAYER_AMOUNT = "1" + "000000000000000000"  # 1 EGLD in wei
    assert "success" in sender_wallet.set_balance(SENDER_AMOUNT)
    assert "success" in relayer_wallet.set_balance(RELAYER_AMOUNT)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()
    sender_balance_before = int(sender_wallet.get_balance())
    int(relayer_wallet.get_balance())

    # Initialize validator keys
    validator_keys = [
        ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_1.pem")),
        ValidatorKey(Path(VALIDATOR_KEYS_FOLDER + "/validatorKey_2.pem")),
    ]

    # Calculate stake amount
    stake_amount = len(validator_keys) * 2500000000000000000000  # Amount for staking

    # Create and sign stake transaction
    stake_tx = create_and_sign_relayed_staking_tx(
        sender_wallet=sender_wallet,
        relayer_wallet=relayer_wallet,
        validator_keys=validator_keys,
        amount=stake_amount,
        nonce=sender_wallet.get_nonce(),
        gas_limit=55000000,
    )

    # Create and sign relayed v3 transaction
    relayed_v3_stake_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[stake_tx],
        relayer_wallet=relayer_wallet,
        gas_limit=55050000,
        nonce=relayer_wallet.get_nonce(),
    )

    # Send transaction and check for success
    send_transaction_and_check_for_success(relayed_v3_stake_tx)

    # Check if validator keys are staked properly
    for key in validator_keys:
        assert key.get_status(sender_wallet.public_address()) == "staked"

    # Verify final nonces and balances
    sender_nonce_after = sender_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()
    sender_balance_after = int(sender_wallet.get_balance())
    # relayer_balance_after = int(relayer_wallet.get_balance())

    # Check nonces
    assert sender_nonce_after == sender_nonce_before + 1
    assert relayer_nonce_after == relayer_nonce_before + 1

    # Verify balances
    assert sender_balance_after == sender_balance_before - stake_amount
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert relayer_balance_after == relayer_balance_before
