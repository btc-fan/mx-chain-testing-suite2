from multiversx_sdk.core import Transaction, TransactionComputer
from multiversx_sdk.wallet.validator_pem import ValidatorPEM
from multiversx_sdk.wallet.validator_signer import ValidatorSigner

from config.config import CHAIN_ID
from config.constants import *
from models.validatorKey import *
from models.wallet import *
from utils.helpers import decimal_to_hex


def create_new_delegation_contract(
    owner: Wallet,
    AMOUNT="1250000000000000000000",
    SERVICE_FEE="00",
    DELEGATION_CAP="00",
) -> str:
    # compute tx
    tx = Transaction(
        sender=owner.get_address().to_bech32(),
        receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
        nonce=owner.get_account().nonce,
        gas_price=1000000000,
        gas_limit=590000000,
        chain_id=CHAIN_ID,
        value=int(AMOUNT),
    )

    tx.data = (f"createNewDelegationContract@{DELEGATION_CAP}@{SERVICE_FEE}").encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(f"New delegation contract created, transaction hash: {tx_hash}")
    return tx_hash


def make_new_contract_from_validator_data(
    owner: Wallet, SERVICE_FEE="00", DELEGATION_CAP="00"
) -> str:
    # compute tx
    tx = Transaction(
        sender=owner.get_address().to_bech32(),
        receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
        nonce=owner.get_account().nonce,
        gas_price=1000000000,
        gas_limit=590000000,
        chain_id=CHAIN_ID,
        value=0,
    )

    tx.data = (
        f"makeNewContractFromValidatorData@{DELEGATION_CAP}@{SERVICE_FEE}".encode()
    )

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(
        f"New contract from validator data created, transaction hash: {tx_hash}"
    )
    return tx_hash


def whitelist_for_merge(
    old_owner: Wallet, new_owner: Wallet, delegation_sc_address: str
) -> str:
    delegation_sc_address = Address.from_bech32(delegation_sc_address)

    # compute tx
    tx = Transaction(
        sender=old_owner.get_address().to_bech32(),
        receiver=delegation_sc_address.to_bech32(),
        nonce=old_owner.get_account().nonce,
        gas_price=1000000000,
        gas_limit=590000000,
        chain_id=CHAIN_ID,
        value=0,
    )

    tx.data = f"whitelistForMerge@{new_owner.get_address().to_hex()}".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = old_owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(f"Whitelist for merge processed, transaction hash: {tx_hash}")
    return tx_hash


def merge_validator_to_delegation_with_whitelist(
    new_owner: Wallet, delegation_sc_address: str
):
    delegation_sc_address_as_hex = Address.from_bech32(delegation_sc_address).to_hex()

    # compute tx
    tx = Transaction(
        sender=new_owner.get_address().to_bech32(),
        receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
        nonce=new_owner.get_account().nonce,
        gas_price=1000000000,
        gas_limit=590000000,
        chain_id=CHAIN_ID,
        value=0,
    )

    tx.data = f"mergeValidatorToDelegationWithWhitelist@{delegation_sc_address_as_hex}".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = new_owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(
        f"Validator merged to delegation with whitelist, transaction hash: {tx_hash}"
    )
    return tx_hash


def merge_validator_to_delegation_same_owner(owner: Wallet, delegation_sc_address: str):
    delegation_sc_address_as_hex = Address.from_bech32(delegation_sc_address).to_hex()

    # compute tx
    tx = Transaction(
        sender=owner.get_address().to_bech32(),
        receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
        nonce=owner.get_account().nonce,
        gas_price=1000000000,
        gas_limit=590000000,
        chain_id=CHAIN_ID,
        value=0,
    )

    tx.data = (
        f"mergeValidatorToDelegationSameOwner@{delegation_sc_address_as_hex}".encode()
    )

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(
        f"Validator merged to delegation with the same owner, transaction hash: {tx_hash}"
    )
    return tx_hash


def add_nodes(
    owner: Wallet, delegation_sc_address: str, validatorKeys: list[ValidatorKey]
) -> str:
    # load needed data for stake transactions signatures
    stake_signature_and_public_key = ""
    for key in validatorKeys:
        pem_file = ValidatorPEM.from_file(key.path)
        public_key = key.public_address()

        validator_signer = ValidatorSigner(pem_file.secret_key)
        signed_message = validator_signer.sign(owner.get_address().pubkey).hex()

        stake_signature_and_public_key += f"@{public_key}@{signed_message}"

    tx = Transaction(
        sender=owner.get_address().to_bech32(),
        receiver=delegation_sc_address,
        nonce=owner.get_account().nonce,
        gas_price=1000000000,
        gas_limit=200000000,
        chain_id=CHAIN_ID,
        value=0,
    )

    tx.data = f"addNodes{stake_signature_and_public_key}".encode()

    # prepare signature
    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(f"Nodes added to delegation, transaction hash: {tx_hash}")
    return tx_hash


def stake_nodes(
    owner: Wallet, delegation_sc_address: str, validatorKeys: list[ValidatorKey]
):
    pub_key_string = ""
    for key in validatorKeys:
        pub_key_string += f"@{key.public_address()}"

    # create transaction
    tx = Transaction(
        sender=owner.get_address().to_bech32(),
        receiver=delegation_sc_address,
        nonce=owner.get_account().nonce,
        gas_price=1000000000,
        gas_limit=200000000,
        chain_id=CHAIN_ID,
        value=0,
    )

    tx.data = f"stakeNodes{pub_key_string}".encode()

    # prepare signature
    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(f"Nodes staked in delegation, transaction hash: {tx_hash}")
    return tx_hash


def delegate(sender: Wallet, delegation_sc_address: str, amount: int):
    # compute tx
    tx = Transaction(
        sender=sender.get_address().to_bech32(),
        receiver=delegation_sc_address,
        nonce=sender.get_account().nonce,
        gas_price=1000000000,
        gas_limit=12000000,
        chain_id=CHAIN_ID,
        value=amount,
    )

    tx.data = f"delegate".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = sender.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)
    logger.info(f"Funds are delegated, transaction hash: {tx_hash}")
    return tx_hash


def create_and_sign_inner_delegation_tx(
    sender_wallet: Wallet,
    relayer_wallet: Wallet,
    delegation_sc_address: str,
    amount: int,
    gas_limit: int = 12000000,
):
    # compute tx
    tx = Transaction(
        sender=sender_wallet.get_address().to_bech32(),
        receiver=delegation_sc_address,
        nonce=sender_wallet.get_account().nonce,
        gas_price=GAS_PRICE,
        gas_limit=gas_limit,
        chain_id=CHAIN_ID,
        value=amount,
    )
    tx.relayer = relayer_wallet.public_address()

    tx.data = f"delegate".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = sender_wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    logger.info(
        f"Created and signed delegate transaction from {sender_wallet.public_address()} with amount {amount}."
    )
    return tx


def create_and_sign_new_inner_delegation_contract_tx(
    sender_wallet: Wallet,
    relayer_wallet: Wallet,
    nonce: int,
    amount: int = 1250000000000000000000,
    gas_limit: int = 55000000,
    service_fee="00",
    delegation_cap="00",
) -> str:
    # compute tx
    tx = Transaction(
        sender=sender_wallet.get_address().to_bech32(),
        receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
        nonce=nonce,
        value=amount,
        gas_limit=gas_limit,
        gas_price=GAS_PRICE,
        chain_id=CHAIN_ID,
    )
    tx.relayer = relayer_wallet.public_address()
    tx.data = tx.data = (
        f"createNewDelegationContract@{delegation_cap}@{service_fee}"
    ).encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = sender_wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    logger.info(
        f"Created and signed createNewDelegationContract transaction from {sender_wallet.public_address()} to {SYSTEM_DELEGATION_MANAGER_CONTRACT} with amount {amount}."
    )
    return tx


def create_and_sign_inner_un_delegation_tx(
    sender_wallet: Wallet,
    relayer_wallet: Wallet,
    delegation_sc_address: str,
    amount: int,
    nonce: int,
    gas_limit: int = 12000000,
):
    # Compute tx
    tx = Transaction(
        sender=sender_wallet.get_address().to_bech32(),
        receiver=delegation_sc_address,
        nonce=nonce,
        gas_price=GAS_PRICE,
        gas_limit=gas_limit,
        chain_id=CHAIN_ID,
        value=0,
    )
    tx.relayer = relayer_wallet.public_address()

    tx.data = f"unDelegate@{decimal_to_hex(amount)}".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = sender_wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    logger.info(
        f"Created and signed unDelegate transaction from {sender_wallet.public_address()} with amount {amount}."
    )
    return tx
