import requests

from config.config import DEFAULT_PROXY
from utils.logger import logger


def has_nft_token(address: str) -> bool:
    """
    Validates if the response for a given address contains tokens.

    Args:
        address (str): The address for which to check the tokens.

    Returns:
        bool: True if tokens are present, otherwise False.
    """
    logger.info(f"Validating nft tokens for Address: {address}")
    response = requests.get(f"{DEFAULT_PROXY}/address/{address}/registered-nfts")
    response.raise_for_status()
    tokens = response.json().get("data", {}).get("tokens", [])
    has_tokens = bool(tokens)
    logger.info(f"NFT Tokens: {tokens} present for Address: {address}: {has_tokens}")
    return has_tokens
