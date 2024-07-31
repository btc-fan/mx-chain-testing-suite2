import json

import requests
from multiversx_sdk.core.address import Address

from config.config import DEFAULT_PROXY
from config.constants import VALIDATOR_CONTRACT
from models.wallet import Wallet
from utils.helpers import base64_to_decimal, base64_to_string
from utils.logger import logger


def get_total_staked(owner: str):
    logger.info(f"Fetching total staked for owner: {owner}")

    address_in_hex = Address.from_bech32(owner).to_hex()
    post_body = {
        "scAddress": VALIDATOR_CONTRACT,
        "funcName": "getTotalStaked",
        "args": [address_in_hex],
    }

    json_structure = json.dumps(post_body)
    logger.debug(f"Query payload prepared: {json_structure}")

    response = requests.post(f"{DEFAULT_PROXY}/vm-values/query", data=json_structure)
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    total_staked_list = tx_response_data.get("returnData")
    total_staked = total_staked_list[0]

    total_staked = base64_to_string(total_staked)
    logger.info(f"Total staked for owner {owner}: {total_staked}")
    return total_staked


def get_user_active_stake(wallet: Wallet, delegation_sc_address: str):
    logger.info(f"Fetching user active stake for wallet: {wallet.public_address()}")

    address_in_hex = Address.from_bech32(wallet.public_address()).to_hex()
    post_body = {
        "scAddress": delegation_sc_address,
        "funcName": "getUserActiveStake",
        "args": [address_in_hex],
    }

    json_structure = json.dumps(post_body)
    logger.debug(f"Query payload prepared: {json_structure}")

    response = requests.post(f"{DEFAULT_PROXY}/vm-values/query", data=json_structure)
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    active_staked_list = tx_response_data.get("returnData")
    active_staked = active_staked_list[0]
    active_staked = base64_to_decimal(active_staked)
    logger.info(f"Active stake wallet {wallet.public_address()}: {active_staked}")
    return active_staked


def get_user_un_delegated_list(wallet: Wallet, delegation_sc_address: str):
    logger.info(
        f"Fetching undelegated stake list for wallet: {wallet.public_address()}"
    )

    address_in_hex = Address.from_bech32(wallet.public_address()).to_hex()
    post_body = {
        "scAddress": delegation_sc_address,
        "funcName": "getUserUnDelegatedList",
        "args": [address_in_hex],
    }

    json_structure = json.dumps(post_body)
    logger.debug(f"Query payload prepared: {json_structure}")

    response = requests.post(f"{DEFAULT_PROXY}/vm-values/query", data=json_structure)
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    undelegated_stake_list = tx_response_data.get("returnData")
    undelegated_stake = undelegated_stake_list[0]
    undelegated_stake = base64_to_decimal(undelegated_stake)
    logger.info(
        f"Undelegated stake values for wallet {wallet.public_address()}: {undelegated_stake}"
    )
    return undelegated_stake


def get_delegators_un_staked_funds_data(wallet: Wallet, delegation_sc_address: str):
    logger.info(
        f"Fetching  un-staked stake for delegator wallet: {wallet.public_address()}"
    )

    address_in_hex = Address.from_bech32(wallet.public_address()).to_hex()
    post_body = {
        "scAddress": delegation_sc_address,
        "funcName": "getDelegatorFundsData",
        "args": [address_in_hex],
    }

    json_structure = json.dumps(post_body)
    logger.debug(f"Query payload prepared: {json_structure}")

    response = requests.post(f"{DEFAULT_PROXY}/vm-values/query", data=json_structure)
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    un_staked_amount_list = tx_response_data.get("returnData")
    un_staked_amount = un_staked_amount_list[2]
    un_staked_amount = base64_to_decimal(un_staked_amount)
    logger.info(
        f"Un-staked for delegator wallet {wallet.public_address()}: {un_staked_amount}"
    )
    return un_staked_amount
