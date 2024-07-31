from multiversx_sdk.core.transaction import Transaction
from multiversx_sdk.core.transaction_computer import TransactionComputer
from multiversx_sdk.core.transactions_factories.transactions_factory_config import (
    TransactionsFactoryConfig,
)

from config.config import CHAIN_ID
from config.constants import GAS_PRICE
from core.chain_commander import add_blocks_until_epoch_reached
from models.wallet import Wallet
from utils.helpers import log_transaction
from utils.logger import logger

config = TransactionsFactoryConfig(CHAIN_ID)
transaction_computer = TransactionComputer()


def create_and_sign_esdt_tx(
    sender_wallet: Wallet,
    receiver_wallet: str,
    data: bytes,
    nonce: int,
    value: int = 500000000000000000,
    gas_limit: int = 60000000,
    gas_price: int = GAS_PRICE,
):
    """
    Creates and signs an ESDT transaction.

    Args:
        sender_wallet (Wallet): The wallet initiating the transaction.
        receiver_wallet (str): The recipient's address.
        data (bytes): The data to be included in the transaction.
        nonce (int): The nonce of the sender's wallet.
        value (int, optional): The amount of EGLD to transfer. Defaults to 500000000000000000 (0.5 EGLD).
        gas_limit (int, optional): The gas limit for the transaction. Defaults to 60000000.
        gas_price (int, optional): The gas price for the transaction. Defaults to GAS_PRICE.

    Returns:
        Transaction: The created and signed transaction.
    """

    issue_estd_tx = Transaction(
        sender=sender_wallet.public_address(),
        receiver=receiver_wallet,
        value=value,
        gas_limit=gas_limit,
        gas_price=gas_price,
        chain_id=CHAIN_ID,
        nonce=nonce,
        data=data,
    )
    log_transaction(issue_estd_tx, f"Created and signed ESDT tx with data: {data}")
    signer_sender = sender_wallet.get_signer()
    assert "success" in add_blocks_until_epoch_reached(7)
    issue_estd_tx.signature = signer_sender.sign(
        transaction_computer.compute_bytes_for_signing(issue_estd_tx)
    )
    logger.info(
        f"Created and signed ESDT tx with sender {sender_wallet.public_address()}."
    )
    return issue_estd_tx


def create_and_sign_esdt_inner_tx(
    sender_wallet: Wallet,
    receiver_wallet: str,
    relayer_wallet: Wallet,
    data: bytes,
    nonce: int,
    value: int = 500000000000000000,
    gas_limit: int = 60000000,
    gas_price: int = GAS_PRICE,
):
    """ """

    issue_estd_tx = Transaction(
        sender=sender_wallet.public_address(),
        receiver=receiver_wallet,
        value=value,
        gas_limit=gas_limit,
        gas_price=gas_price,
        chain_id=CHAIN_ID,
        nonce=nonce,
        data=data,
    )
    issue_estd_tx.relayer = relayer_wallet.public_address()
    # issue_estd_tx.nonce = nonce
    logger.info(
        f"Relayer {relayer_wallet.public_address()} added to Inner ESDT transaction"
    )
    log_transaction(
        issue_estd_tx, f"Created and signed Inner ESDT tx with data: {data}"
    )
    signer_sender = sender_wallet.get_signer()
    # assert "success" in add_blocks_until_epoch_reached(7)
    issue_estd_tx.signature = signer_sender.sign(
        transaction_computer.compute_bytes_for_signing(issue_estd_tx)
    )
    logger.info(
        f"Created and signed Inner ESDT tx with sender {sender_wallet.public_address()}."
    )
    return issue_estd_tx
