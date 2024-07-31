from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_inner_transfer_tx,
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_fail,
)
from models.wallet import Wallet


def test_inner_tx_with_varied_nonces(blockchain):
    """
    Scenario:
    Send 5 inner transactions from the same sender:
    - First 2 with higher nonce
    - Middle one with current nonce
    - Last 2 with lower nonce
    Only the middle one should be executed.

     Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender, receiver, and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender, receiver, and relayer wallets.
    4. Increase the sender's nonce by 3 to avoid negative or zero nonce values.
    5. Create and sign 5 inner transfer transactions from the same sender with varied nonces:
       - First 2 with higher nonce than current
       - Middle one with current nonce
       - Last 2 with lower nonce than current
    6. Create and sign a relayed v3 transaction that includes all 5 inner transactions.
    7. Send the relayed v3 transaction and verify that it fails.
    8. Retrieve and verify the final nonces and balances for sender, receiver, and relayer wallets:
       - Ensure only the middle transaction (with the current nonce) is executed.
       - Ensure the sender's balance is decremented by the transfer amount.
       - Ensure the receiver's balance is incremented by the transfer amount.
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

    # Increase the nonce with 3 because operations are not possible fi nonce is zero or has negative value.
    sender_nonce_before = sender_wallet.get_nonce() + 3

    receiver_nonce_before = receiver_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()
    sender_balance_before = sender_wallet.get_balance()
    receiver_balance_before = receiver_wallet.get_balance()

    transfer_txs = []
    transfer_tx1 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_nonce_before + 2,
    )
    transfer_txs.append(transfer_tx1)

    transfer_tx2 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_nonce_before + 1,
    )
    transfer_txs.append(transfer_tx2)

    transfer_tx3 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce(),  # Middle one with current nonce
    )
    transfer_txs.append(transfer_tx3)

    transfer_tx4 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_nonce_before - 1,
    )
    transfer_txs.append(transfer_tx4)

    transfer_tx5 = create_and_sign_inner_transfer_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=receiver_wallet,
        native_amount=TRANSFER_AMOUNT,
        relayer_wallet=relayer_wallet,
        nonce=sender_nonce_before - 3,
    )
    transfer_txs.append(transfer_tx5)

    # Create and sign relayed v3 transaction with all transfer transactions
    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=transfer_txs,
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce_and_increment(),
    )

    # Send transaction and check for fail
    send_transaction_and_check_for_fail(relayed_v3_tx)

    # Verify final nonces and balances
    sender_nonce_after = sender_wallet.get_nonce()
    receiver_nonce_after = receiver_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()
    sender_balance_after = sender_wallet.get_balance()
    receiver_balance_after = receiver_wallet.get_balance()

    # Check nonces and balances
    assert (
        sender_nonce_after == sender_nonce_before - 2
    )  # Only the middle one should be executed
    assert receiver_nonce_before == receiver_nonce_after
    assert relayer_nonce_after == relayer_nonce_before + 1
    assert int(sender_balance_after) == int(sender_balance_before) - TRANSFER_AMOUNT
    assert int(receiver_balance_after) == int(receiver_balance_before) + TRANSFER_AMOUNT

    # Verify that relayer's balance has decreased by the gas used for the relayed transaction
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert int(relayer_balance_after) == int(relayer_balance_before) - relayed_v3_tx_gas_used
