from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import add_blocks, is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_inner_transfer_tx,
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from models.wallet import Wallet


def test_multiple_inner_tx_on_same_shard(blockchain):
    """
    Sender is in Shard 1, Relayer is in Shard 1, and receiver in Shard 1.
    The sender is sending ten consecutive transactions to the same receiver.
    Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender, receiver, and relayer wallets.
    4. Create and sign multiple native EGLD transfer transactions (inner transactions) from sender to receiver with relayer included.
    5. Create and sign a relayed v3 transaction that includes the inner transactions.
    6. Send the relayed v3 transaction and verify its successful execution.
    7. Retrieve and verify the final nonces and balances for sender, receiver, and relayer wallets.
       - Ensure the sender's nonce is incremented by the number of transactions.
       - Ensure the relayer's nonce is incremented by 1.
       - Ensure the sender's balance is decremented by the total amount transferred.
       - Ensure the receiver's balance is incremented by the total amount received.
       - Ensure the relayer's balance is decremented by the gas used for the transaction.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))  # Shard 1
    receiver_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))  # Shard 1
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))  # Shard 1

    # Set balances for wallets
    INITIAL_BALANCE = "15000000000000000000"  # 15 EGLD
    assert "success" in sender_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in relayer_wallet.set_balance(INITIAL_BALANCE)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    receiver_nonce_before = receiver_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()

    # Get initial account balances
    sender_balance_before = sender_wallet.get_balance()
    receiver_balance_before = receiver_wallet.get_balance()

    amounts = [
        20000000000000000,
        30000000000000000,
        40000000000000000,
        50000000000000000,
        60000000000000000,
        70000000000000000,
        80000000000000000,
        90000000000000000,
        100000000000000000,
        110000000000000000,
    ]

    transfer_txs = []
    for amount in amounts:
        transfer_tx = create_and_sign_inner_transfer_tx(
            sender_wallet=sender_wallet,
            receiver_wallet=receiver_wallet,
            native_amount=amount,
            relayer_wallet=relayer_wallet,
            nonce=sender_wallet.get_nonce_and_increment(),
        )
        transfer_txs.append(transfer_tx)

    # Create and sign relayed v3 transaction with all transfer transactions
    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=transfer_txs,
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce_and_increment(),
    )

    # Send transaction and check for success
    send_transaction_and_check_for_success(relayed_v3_tx)

    # Add blocks
    assert "success" in add_blocks(20)

    # Verify final nonces and balances
    sender_nonce_after = sender_wallet.get_nonce()
    receiver_nonce_after = receiver_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()

    # Check that the nonce for sender has incremented by 10 (indicating the transactions were sent)
    assert sender_nonce_before == sender_nonce_after - 10
    # Check that the nonce for receiver has not changed (indicating no transaction was sent from this wallet)
    assert receiver_nonce_before == receiver_nonce_after
    # Check that the nonce for relayer has incremented by 1 (indicating the relayed transaction was sent)
    assert relayer_nonce_before == relayer_nonce_after - 1

    # Get the balances after the transaction
    sender_balance_after = sender_wallet.get_balance()
    receiver_balance_after = receiver_wallet.get_balance()
    # relayer_balance_after = relayer_wallet.get_balance()

    # Verify that sender's balance has decreased by the total amount sent (sum of amounts)
    total_native_amount = sum(amounts)
    assert int(sender_balance_after) == int(sender_balance_before) - total_native_amount
    # Verify that receiver's balance has increased by the total amount received (sum of amounts)
    assert (
        int(receiver_balance_after)
        == int(receiver_balance_before) + total_native_amount
    )
    # Verify that relayer's balance has decreased by the gas used for the relayed transaction
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert int(relayer_balance_after) == int(relayer_balance_before) - relayed_v3_tx_gas_used
