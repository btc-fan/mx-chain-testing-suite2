from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import (
    add_blocks_until_last_block_of_current_epoch,
    is_chain_online,
)
from core.create_relayed_v3_transaction import (
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from core.delegation import (
    create_and_sign_inner_delegation_tx,
    create_and_sign_inner_un_delegation_tx,
    create_and_sign_new_inner_delegation_contract_tx,
)
from core.get_delegation_info import (
    get_delegation_sc_address_from_sc_results_using_inner_tx,
)
from core.get_staking_info import get_delegators_un_staked_funds_data
from models.wallet import Wallet


def test_delegation_and_undelegation_ping_pong(blockchain):
    """
        Scenario:
        Send 50 inner transactions from the same sender to delegate and undelegate 10 EGLD to/from a delegation
        contract that already has a top-up of 3000 EGLD. At the end, the sender should have 10 EGLD,
        and the contract should have 3000 EGLD.

        Test Steps:
    1. Ensure the blockchain is online.
    2. Set initial balances for sender, relayer, delegator, and top-up wallets.
    3. Retrieve initial account data (nonces and balances) for sender, relayer, and delegator wallets.
    4. Create and sign a new delegation contract creation transaction (inner transaction) from sender with relayer included.
    5. Create and sign a relayed v3 transaction that includes the inner delegation contract transaction.
    6. Send the relayed v3 transaction and verify its successful execution.
    7. Retrieve and verify the final nonces and balances for sender and relayer wallets.
       - Ensure the sender's nonce is incremented by 1.
       - Ensure the relayer's nonce is incremented by 1.
       - Ensure the sender's balance is decremented by the delegation amount.
    8. Add a top-up of 3000 EGLD to the delegation contract.
    9. Perform 50 inner transactions (25 delegations and 25 undelegations) from the delegator to the delegation contract and back.
       - For each iteration:
         - Create and sign a delegation transaction (inner transaction) with relayer included.
         - Create and sign a relayed v3 transaction that includes the inner delegation transaction.
         - Send the relayed v3 transaction and verify its successful execution.
         - Create and sign an undelegation transaction (inner transaction) with relayer included.
         - Create and sign a relayed v3 transaction that includes the inner undelegation transaction.
         - Send the relayed v3 transaction and verify its successful execution.
    10. Add blocks until the last block of the current epoch.
    11. Retrieve and verify the final nonces and balances for delegator wallet.
        - Ensure the delegator's nonce is incremented by 50.
        - Ensure the delegator's funds data matches the expected amount.

    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_7.pem"))
    delegator_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_10.pem"))
    topup_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_3.pem"))

    # Set balances for wallets
    SENDER_AMOUNT = "4500" + "000000000000000000"
    RELAYER_AMOUNT = "100" + "000000000000000000"
    DELEGATOR_AMOUNT = "3000" + "000000000000000000"
    TOP_UP_AMOUNT = "3000" + "000000000000000000"
    DELEGATION_AMOUNT = "10" + "000000000000000000"

    assert "success" in sender_wallet.set_balance(SENDER_AMOUNT)
    assert "success" in relayer_wallet.set_balance(RELAYER_AMOUNT)
    assert "success" in delegator_wallet.set_balance(DELEGATOR_AMOUNT)
    assert "success" in topup_wallet.set_balance(TOP_UP_AMOUNT)

    # Get initial account data
    sender_nonce_before = sender_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()
    delegator_nonce_before = delegator_wallet.get_nonce()
    sender_balance_before = int(sender_wallet.get_balance())
    relayer_balance_before = int(relayer_wallet.get_balance())

    # Create and sign delegation contract
    delegation_contract_tx = create_and_sign_new_inner_delegation_contract_tx(
        sender_wallet=sender_wallet,
        relayer_wallet=relayer_wallet,
        nonce=sender_wallet.get_nonce(),
        amount=int(SENDER_AMOUNT) - 1000000000000000000000,
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
    expected_sender_balance = (
        sender_balance_before - int(SENDER_AMOUNT) + 1000000000000000000000
    )
    assert sender_balance_after == expected_sender_balance

    # Calculate gas used for the relayed transaction
    gas_used = relayed_v3_delegation_tx.gas_limit * relayed_v3_delegation_tx.gas_price
    relayer_balance_before - gas_used
    int(relayer_wallet.get_balance())

    # Get Delegation contract address
    delegation_contract_address = (
        get_delegation_sc_address_from_sc_results_using_inner_tx(delegation_tx_hash)
    )

    # ---------------TOP-UP------------------------------------

    # Add top-up to the delegation contract
    # Create and sign top-up transaction
    topup_tx = create_and_sign_inner_delegation_tx(
        topup_wallet, relayer_wallet, delegation_contract_address, int(TOP_UP_AMOUNT)
    )
    # Create and sign relayed v3 transaction for top-up
    relayed_v3_topup_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[topup_tx],
        relayer_wallet=relayer_wallet,
        gas_limit=99000000,
        nonce=relayer_wallet.get_nonce(),
    )
    send_transaction_and_check_for_success(relayed_v3_topup_tx)

    # Perform 50 inner transactions (25 delegations and 25 undelegations)
    for i in range(25):
        # ---------------DELEGATION------------------------------------
        # Create and sign delegation transaction
        delegation_tx = create_and_sign_inner_delegation_tx(
            delegator_wallet,
            relayer_wallet,
            delegation_contract_address,
            int(DELEGATION_AMOUNT),
        )

        # Create and sign relayed v3 transaction for delegation
        relayed_v3_delegation_tx = create_and_sign_relayed_v3_transaction(
            inner_transactions=[delegation_tx],
            relayer_wallet=relayer_wallet,
            gas_limit=99000000,
            nonce=relayer_wallet.get_nonce(),
        )
        send_transaction_and_check_for_success(relayed_v3_delegation_tx)

        # ---------------UnDELEGATION------------------------------------
        undelegation_tx = create_and_sign_inner_un_delegation_tx(
            sender_wallet=delegator_wallet,
            relayer_wallet=relayer_wallet,
            delegation_sc_address=delegation_contract_address,
            amount=int(DELEGATION_AMOUNT),
            nonce=delegator_wallet.get_nonce(),
        )

        # Create and sign relayed v3 transaction for undelegation
        relayed_v3_undelegation_tx = create_and_sign_relayed_v3_transaction(
            inner_transactions=[undelegation_tx],
            relayer_wallet=relayer_wallet,
            gas_limit=99000000,
            nonce=relayer_wallet.get_nonce(),
        )
        send_transaction_and_check_for_success(relayed_v3_undelegation_tx)

    # add blocks
    assert "success" in add_blocks_until_last_block_of_current_epoch()

    # Verify final nonces
    delegator_nonce_after = delegator_wallet.get_nonce()
    assert delegator_nonce_after == delegator_nonce_before + 50

    # Verify final balances
    final_delegator_funds_data = get_delegators_un_staked_funds_data(
        delegator_wallet, delegation_contract_address
    )
    assert final_delegator_funds_data == int(DELEGATION_AMOUNT) * 25
