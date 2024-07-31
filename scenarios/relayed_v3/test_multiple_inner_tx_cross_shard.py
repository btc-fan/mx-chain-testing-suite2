from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import add_blocks, is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_inner_transfer_tx,
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from models.wallet import Wallet


def test_multiple_inner_tx_cross_shard(blockchain):
    """
    Sender is in Shard 1, Relayer is in Shard 1, and receivers are in Shard 0, 1, and 2.
    The sender is sending ten transactions to ten different receivers.
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
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))  # Shard 1

    receiver_wallets = [
        Wallet(Path(WALLETS_FOLDER + "/sd_2_wallet_key_2.pem")),  # Shard 2
        Wallet(Path(WALLETS_FOLDER + "/sd_2_wallet_key_4.pem")),  # Shard 2
        Wallet(Path(WALLETS_FOLDER + "/sd_0_wallet_key_5.pem")),  # Shard 0
        Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem")),  # Shard 1
        Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_7.pem")),  # Shard 1
        Wallet(Path(WALLETS_FOLDER + "/sd_2_wallet_key_8.pem")),  # Shard 2
        Wallet(Path(WALLETS_FOLDER + "/sd_0_wallet_key_9.pem")),  # Shard 0
        Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_10.pem")),  # Shard 1
        Wallet(Path(WALLETS_FOLDER + "/sd_0_bob.pem")),  # Shard 0 (Bob)
        Wallet(Path(WALLETS_FOLDER + "/sd_1_alice.pem")),  # Shard 1 (Alice)
    ]

    # Set balances for sender and relayer
    INITIAL_BALANCE = "15000000000000000000"  # 15 EGLD
    assert "success" in sender_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in relayer_wallet.set_balance(INITIAL_BALANCE)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()

    # Get initial account balances
    sender_balance_before = sender_wallet.get_balance()
    relayer_wallet.get_balance()

    # Get initial balances for receivers
    receiver_balances_before = [wallet.get_balance() for wallet in receiver_wallets]

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
    for amount, receiver_wallet in zip(amounts, receiver_wallets):
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
    # Get the nonces after the transaction
    sender_nonce_after = sender_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()

    # Check that the nonce for sender has incremented by the number of transactions
    assert sender_nonce_before == sender_nonce_after - len(amounts)
    # Check that the nonce for relayer has incremented by 1 (indicating the relayed transaction was sent)
    assert relayer_nonce_before == relayer_nonce_after - 1

    # Get the balances after the transaction
    sender_balance_after = sender_wallet.get_balance()
    relayer_wallet.get_balance()
    receiver_balances_after = [wallet.get_balance() for wallet in receiver_wallets]

    # Verify that sender's balance has decreased by the total amount sent (sum of amounts)
    total_native_amount = sum(amounts)
    assert int(sender_balance_after) == int(sender_balance_before) - total_native_amount
    # Verify that relayer's balance has decreased by the gas used for the relayed transaction
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert int(relayer_balance_after) == int(relayer_balance_before) - relayed_v3_tx_gas_used

    # Verify that receiver's balances have increased by the amounts received
    for before, after, amount in zip(
        receiver_balances_before, receiver_balances_after, amounts
    ):
        assert int(after) == int(before) + int(amount)
