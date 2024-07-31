from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import add_blocks, is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_inner_transfer_tx,
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_fail,
)
from models.wallet import Wallet


def test_inner_tx_with_decreasing_nonces(blockchain):
    """
        Scenario:
        Send 5 inner transactions from the same sender with nonces starting from current_nonce + 5 and decreasing by 1.
        Only the last one should be executed.

    Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender, receiver, and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender, receiver, and relayer wallets.
    4. Create and sign 5 native EGLD transfer transactions (inner transactions) from the sender to the receiver
    with nonces starting from current_nonce + 5 and decreasing by 1. Include relayer for all transactions.
    5. Create and sign a relayed v3 transaction that includes all 5 inner transactions.
    6. Send the relayed v3 transaction and verify its execution.
    7. Retrieve and verify the final nonces and balances for sender, receiver, and relayer wallets.
       - Ensure only the last inner transaction is executed.
       - Ensure the sender's nonce is incremented by 1.
       - Ensure the receiver's nonce remains unchanged.
       - Ensure the relayer's nonce is incremented by 1.
       - Ensure the sender's balance is decremented by the amount transferred in the last transaction.
       - Ensure the receiver's balance is incremented by the amount received in the last transaction.
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

    TRANSFER_AMOUNT = 1000000000000000000  # 1 EGLD

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    receiver_nonce_before = receiver_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()
    sender_balance_before = sender_wallet.get_balance()
    receiver_balance_before = receiver_wallet.get_balance()

    transfer_txs = []
    # Create and sign transfer transactions with nonces starting from current_nonce+5 and decreasing by 1
    transfer_tx1 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce() + 5,
    )
    transfer_txs.append(transfer_tx1)

    transfer_tx2 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce() + 4,
    )
    transfer_txs.append(transfer_tx2)

    transfer_tx3 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce() + 3,
    )
    transfer_txs.append(transfer_tx3)

    transfer_tx4 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce() + 2,
    )
    transfer_txs.append(transfer_tx4)

    transfer_tx5 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce() + 1,
    )
    transfer_txs.append(transfer_tx5)

    transfer_tx6 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce(),
    )
    transfer_txs.append(transfer_tx6)

    # Create and sign relayed v3 transaction with all transfer transactions
    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=transfer_txs,
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce_and_increment(),
    )

    # Send transaction and check for fail
    send_transaction_and_check_for_fail(relayed_v3_tx)

    # Add blocks
    assert "success" in add_blocks(20)

    # Verify final nonces and balances
    sender_nonce_after = sender_wallet.get_nonce()
    receiver_nonce_after = receiver_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()
    sender_balance_after = sender_wallet.get_balance()
    receiver_balance_after = receiver_wallet.get_balance()
    relayer_wallet.get_balance()

    # Check nonces and balances
    assert sender_nonce_after == sender_nonce_before + 1
    assert receiver_nonce_before == receiver_nonce_after
    assert relayer_nonce_after == relayer_nonce_before + 1
    assert int(sender_balance_after) == int(sender_balance_before) - TRANSFER_AMOUNT
    assert int(receiver_balance_after) == int(receiver_balance_before) + TRANSFER_AMOUNT

    # Verify that relayer's balance has decreased by the gas used for the relayed transaction
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert int(relayer_balance_after) == int(relayer_balance_before) - relayed_v3_tx_gas_used
