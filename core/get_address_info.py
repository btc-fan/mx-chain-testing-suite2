import requests

from config.config import DEFAULT_PROXY
from utils.logger import logger


def get_nonce(address: str) -> int:
    """
    Retrieves the nonce for a given address.

    Args:
        address (str): The address for which to get the nonce.

    Returns:
        int: The nonce of the address.
    """
    logger.info(f"Checking Nonce for Address: {address}")
    response = requests.get(f"{DEFAULT_PROXY}/address/{address}/nonce")
    response.raise_for_status()
    nonce = response.json()["data"]["nonce"]
    logger.info(f"Address Nonce: {nonce}")
    return nonce


def get_balance(address: str) -> str:
    """
    Retrieves the balance for a given address.

    Args:
        address (str): The address for which to get the balance.

    Returns:
        str: The balance of the address.
    """
    logger.info(f"Checking Balance for Address: {address}")
    response = requests.get(f"{DEFAULT_PROXY}/address/{address}/balance")
    response.raise_for_status()
    balance = response.json()["data"]["balance"]
    logger.info(f"Address Balance: {balance}")
    return balance


def get_address_details(address: str) -> dict:
    """
    Retrieves detailed information for a given address.

    Args:
        address (str): The address for which to get the details.

    Returns:
        dict: A dictionary containing the address details.
    """
    logger.info(f"Checking Details for Address: {address}")
    response = requests.get(f"{DEFAULT_PROXY}/address/{address}")
    response.raise_for_status()
    response_json = response.json()
    logger.info(f"Address Details: {response_json}")
    return response_json
