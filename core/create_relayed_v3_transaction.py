from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.transactions_factory_config import (
    TransactionsFactoryConfig,
)

from config.config import CHAIN_ID, provider
from config.constants import GAS_PRICE
from core.chain_commander import (
    add_blocks_until_epoch_reached,
    add_blocks_until_tx_fully_executed,
)
from models.wallet import Wallet
from utils.helpers import log_transaction
from utils.logger import logger

config = TransactionsFactoryConfig(CHAIN_ID)
transaction_computer = TransactionComputer()


def create_and_sign_inner_transfer_tx(
    sender_wallet: Wallet,
    receiver_wallet: Wallet,
    relayer_wallet: Wallet,
    native_amount: int,
    nonce: int,
    gas_limit: int = 50000,
    gas_price: int = GAS_PRICE,
):
    """
    Creates and signs a native token transfer transaction, including a relayer address.
    Args:
        sender_wallet (Wallet): The wallet of the sender.
        receiver_wallet (Wallet): The wallet of the receiver.
        relayer_wallet (Wallet): The wallet of the relayer.
        native_amount (int): The amount of native token to transfer.
        gas_limit (str): Expected gas cos, default is 50k
    Returns:
        Transaction: The signed transfer transaction.
    """
    tx = Transaction(
        sender=sender_wallet.public_address(),
        receiver=receiver_wallet.public_address(),
        gas_limit=gas_limit,
        gas_price=gas_price,
        chain_id=CHAIN_ID,
        value=native_amount,
        nonce=nonce,
    )
    tx.relayer = relayer_wallet.public_address()
    tx.nonce = nonce
    logger.info(
        f"Relayer {relayer_wallet.public_address()} added to transfer transaction"
    )
    log_transaction(tx, "Created and signed Native Transfer transaction")
    signer_sender = sender_wallet.get_signer()
    tx.signature = signer_sender.sign(
        transaction_computer.compute_bytes_for_signing(tx)
    )
    logger.info(
        f"Created and signed transfer transaction from {sender_wallet.public_address()} to {receiver_wallet.public_address()} for amount {native_amount}."
    )
    return tx


def create_and_sign_relayed_v3_transaction(
    inner_transactions: list,
    relayer_wallet: Wallet,
    nonce: int,
    gas_limit=1440000,
    data: str = "",
):
    """
    Creates and signs a relayed v3 transaction, including inner transactions.
    Args:
        inner_transactions (list): The list of inner transactions.
        relayer_wallet (Wallet): The Wallet of the relayer.
        nonce (int): The nonce for the relayed transaction.
        gas_limit (int): Expected gas cost, default is 1440000.
    Returns:
        Transaction: The signed relayed v3 transaction.
    """

    relayed_v3_tx = Transaction(
        sender=relayer_wallet.public_address(),
        receiver=relayer_wallet.public_address(),
        gas_limit=gas_limit,
        chain_id=CHAIN_ID,
        value=0,
        inner_transactions=inner_transactions,
        nonce=nonce,
    )
    relayed_v3_tx.data = data.encode()
    log_transaction(relayed_v3_tx, "Created and signed relayed v3 transaction")
    signer_relayer = relayer_wallet.get_signer()
    assert "success" in add_blocks_until_epoch_reached(7)
    relayed_v3_tx.signature = signer_relayer.sign(
        transaction_computer.compute_bytes_for_signing(relayed_v3_tx)
    )
    logger.info(
        f"Created and signed relayed v3 transaction with relayer {relayer_wallet.public_address()}."
    )
    return relayed_v3_tx


def send_transaction_and_check_for_success(transaction):
    """
    Sends a transaction and checks for its success.

    Args:
        transaction (Transaction): The transaction to send.

    Returns:
        str: The transaction hash.
    """
    tx_hash = provider.send_transaction(transaction)
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"
    logger.info(f"Transaction sent successfully with hash: {tx_hash}")
    return tx_hash


def send_transaction_and_check_for_fail(transaction):
    """
    Sends a transaction and checks for its fail.

    Args:
        transaction (Transaction): The transaction to send.

    Returns:
        str: The transaction hash.
    """
    tx_hash = provider.send_transaction(transaction)
    assert add_blocks_until_tx_fully_executed(tx_hash) == "fail"
    logger.info(f"Transaction failed with hash: {tx_hash}")
    return tx_hash
