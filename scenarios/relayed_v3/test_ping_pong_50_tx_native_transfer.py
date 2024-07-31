from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_inner_transfer_tx,
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from models.wallet import Wallet


def test_ping_pong_transactions(blockchain):
    """
        Scenario:
        Send 50 inner transactions with 2 different senders ping-ponging 1 EGLD back and forth.
        All transactions should be executed successfully.

        Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender1, sender2, and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender1, sender2, and relayer wallets.
    4. Create and sign 50 native EGLD transfer transactions (inner transactions) ping-ponging between sender1 and sender2, each transaction signed by the relayer.
       - For each iteration:
         - Sender1 sends 1 EGLD to Sender2 and signs the transaction with the relayer.
         - Sender2 sends 1 EGLD back to Sender1 and signs the transaction with the relayer.
    5. Send each relayed v3 transaction and verify its successful execution.
    6. Retrieve and verify the final nonces and balances for sender1, sender2, and relayer wallets.
       - Ensure the sender1's nonce is incremented by 25.
       - Ensure the sender2's nonce is incremented by 25.
       - Ensure the relayer's nonce is incremented by 50.
       - Ensure sender1's balance remains unchanged.
       - Ensure sender2's balance remains unchanged.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender1_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))
    sender2_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))

    # Set balances for wallets
    INITIAL_BALANCE = "10000000000000000000"  # 10 EGLD
    assert "success" in sender1_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in sender2_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in relayer_wallet.set_balance(INITIAL_BALANCE)

    # Get initial account data
    sender1_nonce_before = sender1_wallet.get_nonce()
    sender2_nonce_before = sender2_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()

    # Get initial account balances
    sender1_balance_before = sender1_wallet.get_balance()
    sender2_balance_before = sender2_wallet.get_balance()
    relayer_wallet.get_balance()

    TRANSFER_AMOUNT = 1000000000000000000  # 1 EGLD

    # Create and sign 50 transfer transactions ping-ponging between sender1 and sender2

    for i in range(25):
        # Sender1 to Sender2
        nonce1 = sender1_wallet.get_nonce_and_increment()
        transfer_tx1 = create_and_sign_inner_transfer_tx(
            sender_wallet=sender1_wallet,
            receiver_wallet=sender2_wallet,
            native_amount=TRANSFER_AMOUNT,
            relayer_wallet=relayer_wallet,
            nonce=nonce1,
        )

        # Create and sign relayed v3 transaction with the transfer transaction
        relayed_v3_tx1 = create_and_sign_relayed_v3_transaction(
            inner_transactions=[transfer_tx1],
            relayer_wallet=relayer_wallet,
            nonce=relayer_wallet.get_nonce_and_increment(),
        )

        # Send transaction and check for success
        send_transaction_and_check_for_success(relayed_v3_tx1)

        # Sender2 to Sender1
        nonce2 = sender2_wallet.get_nonce_and_increment()
        transfer_tx2 = create_and_sign_inner_transfer_tx(
            sender_wallet=sender2_wallet,
            receiver_wallet=sender1_wallet,
            native_amount=TRANSFER_AMOUNT,
            relayer_wallet=relayer_wallet,
            nonce=nonce2,
        )

        # Create and sign relayed v3 transaction with the transfer transaction
        relayed_v3_tx2 = create_and_sign_relayed_v3_transaction(
            inner_transactions=[transfer_tx2],
            relayer_wallet=relayer_wallet,
            nonce=relayer_wallet.get_nonce_and_increment(),
        )

        # Send transaction and check for success
        send_transaction_and_check_for_success(relayed_v3_tx2)

    # Verify final nonces and balances
    sender1_nonce_after = sender1_wallet.get_nonce()
    sender2_nonce_after = sender2_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()

    sender1_balance_after = sender1_wallet.get_balance()
    sender2_balance_after = sender2_wallet.get_balance()
    relayer_wallet.get_balance()

    # Check that the nonce for sender1 has incremented by 25
    assert sender1_nonce_after == sender1_nonce_before + 25

    # Check that the nonce for sender2 has incremented by 25
    assert sender2_nonce_after == sender2_nonce_before + 25

    # Check that the nonce for the relayer has incremented by 50
    assert relayer_nonce_after == relayer_nonce_before + 50

    # Verify that sender1's balance has not decreased as the same amount is received back
    assert int(sender1_balance_after) == int(sender1_balance_before)

    # Verify that sender2's balance has not decreased as the same amount is received back
    assert int(sender2_balance_after) == int(sender2_balance_before)

    # Verify that relayer's balance has decreased by the gas used for the relayed transactions
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert int(relayer_balance_after) == int(relayer_balance_before) - relayed_v3_tx_gas_used
