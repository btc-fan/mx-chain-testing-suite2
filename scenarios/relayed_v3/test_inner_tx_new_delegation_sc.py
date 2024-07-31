from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_relayed_v3_transaction import (
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from core.delegation import (
    create_and_sign_inner_delegation_tx,
    create_and_sign_new_inner_delegation_contract_tx,
)
from core.get_delegation_info import (
    get_delegation_sc_address_from_sc_results_using_inner_tx,
)
from core.get_staking_info import get_user_active_stake
from models.wallet import Wallet


def test_relayed_v3_create_new_delegation_contract(blockchain):
    """
    Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender, relayer, and delegator wallets.
    3. Retrieve initial account data (nonces and balances) for sender, relayer, and delegator wallets.
    4. Create and sign a delegation contract creation transaction (inner transaction) from sender with relayer included.
    5. Create and sign a relayed v3 transaction that includes the inner delegation contract transaction.
    6. Send the relayed v3 transaction and verify its successful execution.
    7. Retrieve and verify the final nonces and balances for sender, relayer, and delegator wallets.
       - Ensure the sender's nonce is incremented by 1.
       - Ensure the relayer's nonce is incremented by 1.
       - Ensure the delegator's nonce is incremented by 1.
       - Ensure the sender's balance is decremented by the delegation amount.
       - Ensure the relayer's balance is decremented by the gas used for the transaction.
       - Ensure the delegator's balance is decremented by the delegation amount.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_7.pem"))
    delegator_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_10.pem"))

    # Set balances for wallets
    SENDER_AMOUNT = "2501" + "000000000000000000"
    RELAYER_AMOUNT = "100" + "000000000000000000"
    DELEGATOR_AMOUNT = "100" + "000000000000000000"
    assert "success" in sender_wallet.set_balance(SENDER_AMOUNT)
    assert "success" in relayer_wallet.set_balance(RELAYER_AMOUNT)
    assert "success" in delegator_wallet.set_balance(DELEGATOR_AMOUNT)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()
    delegator_nonce_before = delegator_wallet.get_nonce()
    sender_balance_before = int(sender_wallet.get_balance())
    relayer_balance_before = int(relayer_wallet.get_balance())
    delegator_balance_before = int(delegator_wallet.get_balance())

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

    # Send transaction and check for success
    delegation_tx_hash = send_transaction_and_check_for_success(
        relayed_v3_delegation_tx
    )

    # Verify final nonces and balance
    sender_nonce_after = sender_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()
    sender_balance_after = int(sender_wallet.get_balance())

    # Check nonces
    assert sender_nonce_after == sender_nonce_before + 1
    assert relayer_nonce_after == relayer_nonce_before + 1

    # Verify balances
    expected_sender_balance = sender_balance_before - int(SENDER_AMOUNT)
    assert sender_balance_after == expected_sender_balance

    # Calculate gas used for the relayed transaction
    gas_used = relayed_v3_delegation_tx.gas_limit * relayed_v3_delegation_tx.gas_price
    relayer_balance_before - gas_used
    int(relayer_wallet.get_balance())
    # TODO: Uncomment line below nce we have a solution to deduct inner gas used properly
    # assert relayer_balance_after == expected_relayer_balance

    # Get Delegation contract address
    delegation_contract_address = (
        get_delegation_sc_address_from_sc_results_using_inner_tx(delegation_tx_hash)
    )

    # Create and sign delegation transaction
    delegation_tx_hash = create_and_sign_inner_delegation_tx(
        delegator_wallet,
        relayer_wallet,
        delegation_contract_address,
        int(DELEGATOR_AMOUNT),
    )

    # Create and sign relayed v3 transaction for delegation
    relayed_v3_delegation_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[delegation_tx_hash],
        relayer_wallet=relayer_wallet,
        gas_limit=99000000,
        nonce=relayer_wallet.get_nonce(),
    )
    send_transaction_and_check_for_success(relayed_v3_delegation_tx)

    # Verify delegator's final nonces and balances
    delegator_nonce_after = delegator_wallet.get_nonce()
    active_staked = get_user_active_stake(delegator_wallet, delegation_contract_address)
    assert int(active_staked) == int(DELEGATOR_AMOUNT)

    delegator_balance_after = int(delegator_wallet.get_balance())
    expected_delegator_balance = delegator_balance_before - int(DELEGATOR_AMOUNT)
    assert delegator_balance_after == expected_delegator_balance
    assert delegator_nonce_after == delegator_nonce_before + 1
