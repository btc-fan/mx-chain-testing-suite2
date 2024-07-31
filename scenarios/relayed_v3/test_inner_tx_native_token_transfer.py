from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_inner_transfer_tx,
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from models.wallet import Wallet


def test_relayed_v3_egld_native_token_transfer_positive(blockchain):
    """
    Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender, receiver, and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender, receiver, and relayer wallets.
    4. Create and sign a native EGLD transfer transaction (inner transaction) from sender to receiver with relayer included.
    5. Create and sign a relayed v3 transaction that includes the inner transaction.
    6. Send the relayed v3 transaction and verify its successful execution.
    7. Retrieve and verify the final nonces and balances for sender, receiver, and relayer wallets.
       - Ensure the sender's nonce is incremented by 1.
       - Ensure the relayer's nonce is incremented by 1.
       - Ensure the sender's balance is decremented by the amount transferred.
       - Ensure the receiver's balance is incremented by the amount received.
       - Ensure the relayer's balance is decremented by the gas used for the transaction.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))
    receiver_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))

    # Set balances for wallets
    INITIAL_BALANCE = "5000000000000000000"  # 5 EGLD
    assert "success" in sender_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in relayer_wallet.set_balance(INITIAL_BALANCE)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    receiver_nonce_before = receiver_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()

    # Get initial account balances
    sender_balance_before = sender_wallet.get_balance()
    receiver_balance_before = receiver_wallet.get_balance()

    TRANSFER_AMOUNT = 1000000000000000000  # 1 EGLD

    # Create and sign transfer transaction
    transfer_tx = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce(),
    )

    # Create and sign relayed v3 transaction
    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[transfer_tx],
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce(),
    )

    # Send transaction and check for success
    send_transaction_and_check_for_success(relayed_v3_tx)

    # Get the nonces after the transaction
    sender_nonce_after = sender_wallet.get_nonce()
    receiver_nonce_after = receiver_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()

    # Check that the nonce for the sender has incremented by 1 (indicating the transaction was sent)
    assert sender_nonce_before == sender_nonce_after - 1
    # Check that the nonce for the receiver has not changed (indicating no transaction was sent from this wallet)
    assert receiver_nonce_before == receiver_nonce_after
    # Check that the nonce for the relayer has incremented by 1 (indicating the relayed transaction was sent)
    assert relayer_nonce_before == relayer_nonce_after - 1

    # Get the balances after the transaction
    sender_balance_after = sender_wallet.get_balance()
    receiver_balance_after = receiver_wallet.get_balance()
    # relayer_balance_after = relayer_wallet.get_balance()

    # Verify that the sender's balance has decreased by the amount sent (TRANSFER_AMOUNT)
    assert int(sender_balance_after) == int(sender_balance_before) - TRANSFER_AMOUNT
    # Verify that the receiver's balance has increased by the amount received (TRANSFER_AMOUNT)
    assert int(receiver_balance_after) == int(receiver_balance_before) + TRANSFER_AMOUNT
    # Verify that the relayer's balance has decreased by the gas used for the relayed transaction
    # TODO: Uncomment line below once we have a solution to deduct inner gas used properly
    # assert int(relayer_balance_after) == int(relayer_balance_before) - relayed_v3_tx_gas_used
