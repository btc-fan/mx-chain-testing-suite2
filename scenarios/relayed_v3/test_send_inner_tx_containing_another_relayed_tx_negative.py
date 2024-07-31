from pathlib import Path

from multiversx_sdk.network_providers.errors import GenericError

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from core.delegation import create_and_sign_new_inner_delegation_contract_tx
from models.wallet import Wallet


def test_create_relayed_v3_tx_invalid_data_value_for_sc_delegation(blockchain):
    """
    Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender and relayer wallets.
    3. Retrieve initial account data (nonces and balances) for sender and relayer wallets.
    4. Create and sign a delegation contract creation transaction (inner transaction) from sender with relayer included.
    5. Create and sign a relayed v3 transaction that includes the inner delegation contract transaction.
    6. Create and sign another relayed v3 transaction that includes the first relayed v3 transaction to simulate recursion.
    7. Attempt to send the relayed v3 transaction and verify that it fails due to recursion.
    8. Retrieve and verify the final nonces and balances for sender and relayer wallets.
       - Ensure the sender's nonce remains unchanged.
       - Ensure the relayer's nonce remains unchanged.
       - Ensure the sender's balance remains unchanged.
       - Ensure the relayer's balance remains unchanged.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_7.pem"))

    # Set balances for wallets
    SENDER_AMOUNT = "2501" + "000000000000000000"  # 2501 EGLD in wei
    RELAYER_AMOUNT = "100" + "000000000000000000"  # 100 EGLD in wei
    assert "success" in sender_wallet.set_balance(SENDER_AMOUNT)
    assert "success" in relayer_wallet.set_balance(RELAYER_AMOUNT)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()
    sender_balance_before = int(sender_wallet.get_balance())
    relayer_balance_before = int(relayer_wallet.get_balance())

    # Create and sign delegation contract creation transaction
    delegation_contract_tx = create_and_sign_new_inner_delegation_contract_tx(
        sender_wallet=sender_wallet,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce(),
        amount=SENDER_AMOUNT,
        gas_limit=85000000,
    )

    # Create and sign relayed v3 transaction
    relayed_v3_delegation_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[delegation_contract_tx],
        relayer_wallet=relayer_wallet,
        gas_limit=99000000,
        nonce=relayer_wallet.get_nonce(),
    )

    # Create and sign another relayed v3 transaction to simulate recursion
    relayed_v3_delegation_tx_2 = create_and_sign_relayed_v3_transaction(
        inner_transactions=[relayed_v3_delegation_tx],
        relayer_wallet=relayer_wallet,
        gas_limit=99500000,
        nonce=relayer_wallet.get_nonce(),
    )

    # Attempt to send the transaction and check for recursion error
    try:
        delegation_tx_hash = send_transaction_and_check_for_success(
            relayed_v3_delegation_tx_2
        )
    except GenericError as e:
        assert "recursive relayed tx is not allowed" in str(
            e
        ), f"Expected recursive relayed tx error, got: {e}"

    # Verify final nonces and balance
    sender_nonce_after = sender_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()
    sender_balance_after = int(sender_wallet.get_balance())
    relayer_balance_after = int(relayer_wallet.get_balance())

    # Check nonces
    assert sender_nonce_after == sender_nonce_before
    assert relayer_nonce_after == relayer_nonce_before

    # Verify balances
    assert sender_balance_after == sender_balance_before
    assert relayer_balance_after == relayer_balance_before
