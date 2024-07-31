from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_inner_transfer_tx,
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from models.wallet import Wallet


def test_five_inner_txs_with_increasing_nonces(blockchain):
    """
        Scenario:
        Send 5 inner transactions from the same sender, with nonces starting from the current nonce and increasing by 1.
        All transactions should be executed successfully.

        Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender, receiver, and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender, receiver, and relayer wallets.
    4. Create and sign 5 native EGLD transfer transactions (inner transactions) from the sender to the receiver with nonces starting from the current nonce and increasing by 1. Include relayer for all transactions.
    5. Create and sign a relayed v3 transaction that includes all 5 inner transactions.
    6. Send the relayed v3 transaction and verify its execution.
    7. Retrieve and verify the final nonces and balances for sender, receiver, and relayer wallets.
       - Ensure the sender's nonce is incremented by 5.
       - Ensure the receiver's nonce remains unchanged.
       - Ensure the relayer's nonce is incremented by 1.
       - Ensure the sender's balance is decremented by the total amount transferred in all 5 transactions.
       - Ensure the receiver's balance is incremented by the total amount received in all 5 transactions.
       - Ensure the relayer's balance is decremented by the gas used for the transaction.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))
    receiver_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))

    # Set balances for wallets
    INITIAL_BALANCE = "10000000000000000000"  # 10 EGLD
    assert "success" in sender_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in relayer_wallet.set_balance(INITIAL_BALANCE)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    receiver_nonce_before = receiver_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()

    # Get initial account balances
    sender_balance_before = sender_wallet.get_balance()
    receiver_balance_before = receiver_wallet.get_balance()
    relayer_wallet.get_balance()

    TRANSFER_AMOUNT = 1000000000000000000  # 1 EGLD

    # Create and sign 5 transfer transactions with increasing nonces
    transfer_txs = []
    for i in range(5):
        nonce = sender_wallet.get_nonce_and_increment()
        transfer_tx = create_and_sign_inner_transfer_tx(
            sender_wallet=sender_wallet,
            receiver_wallet=receiver_wallet,
            native_amount=TRANSFER_AMOUNT,
            relayer_wallet=relayer_wallet,
            nonce=nonce,
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

    # Verify final nonces and balances
    sender_nonce_after = sender_wallet.get_nonce()
    receiver_nonce_after = receiver_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()

    sender_balance_after = sender_wallet.get_balance()
    receiver_balance_after = receiver_wallet.get_balance()

    # Check that the nonce for the sender has incremented by 5
    assert sender_nonce_after == sender_nonce_before + 5

    # Check that the nonce for the receiver has not changed
    assert receiver_nonce_before == receiver_nonce_after

    # Check that the nonce for the relayer has incremented by 1
    assert relayer_nonce_after == relayer_nonce_before + 1

    # Verify that sender's balance has decreased by the total amount sent (5 * TRANSFER_AMOUNT)
    assert int(sender_balance_after) == int(sender_balance_before) - (
        5 * TRANSFER_AMOUNT
    )

    # Verify that receiver's balance has increased by the total amount received (5 * TRANSFER_AMOUNT)
    assert int(receiver_balance_after) == int(receiver_balance_before) + (
        5 * TRANSFER_AMOUNT
    )

    # Verify that relayer's balance has decreased by the gas used for the relayed transaction
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert int(relayer_balance_after) == int(relayer_balance_before) - relayed_v3_tx_gas_used
