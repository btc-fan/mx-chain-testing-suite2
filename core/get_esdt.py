import requests

from config.config import DEFAULT_PROXY
from utils.logger import logger


def get_esdt_roles(address: str) -> list:
    """
    Retrieves the roles for a given address.

    Args:
        address (str): The address for which to get the roles.

    Returns:
        list: A list of roles found, or an empty list if none are found.
    """
    logger.info(f"Retrieving roles for Address: {address}")
    response = requests.get(f"{DEFAULT_PROXY}/address/{address}/esdts/roles")
    response.raise_for_status()
    roles_dict = response.json().get("data", {}).get("roles", {})
    roles = []
    for role_list in roles_dict.values():
        roles.extend(role_list)
    if not roles:
        logger.error(f"No roles found for Address: {address}")
    else:
        logger.info(f"Roles found for Address {address}: {roles}")
    return roles


def get_single_esdt_details(address: str, token_identifier: str) -> dict:
    """
    Retrieves the ESDT details for a given address and token identifier.

    Args:
        address (str): The address to query.
        token_identifier (str): The token identifier to look for.

    Returns:
        dict: A dictionary containing the ESDT details.
    """
    logger.info(
        f"Retrieving ESDT details for Address: {address} and Token Identifier: {token_identifier}"
    )
    response = requests.get(f"{DEFAULT_PROXY}/address/{address}/esdt")
    response.raise_for_status()

    esdts = response.json().get("data", {}).get("esdts", {})
    esdt_details = {}

    for key, value in esdts.items():
        if token_identifier in key:
            esdt_details = value
            break

    if not esdt_details:
        logger.error(
            f"No ESDT details found for Token Identifier: {token_identifier} and Address: {address}"
        )
    else:
        logger.info(
            f"ESDT details for Address {address} and Token Identifier {token_identifier}: {esdt_details}"
        )

    return esdt_details


def get_multiple_esdt_details(address: str, token_identifier: str) -> list:
    """
    Retrieves the ESDT details for a given address and a list of token identifiers.

    Args:
        address (str): The address to query.
        token_identifier (str): The token identifier to look for.

    Returns:
        list: A list of dictionaries, each containing the ESDT details for a matching token.
    """
    logger.info(
        f"Retrieving ESDT details for Address: {address} and Token Identifiers: {token_identifier}"
    )

    response = requests.get(f"{DEFAULT_PROXY}/address/{address}/esdt")
    response.raise_for_status()

    esdts = response.json().get("data", {}).get("esdts", {})
    matching_esdts = []

    for key, value in esdts.items():
        if key.startswith(token_identifier):
            matching_esdts.append(value)
            logger.info(
                f"Found ESDT details for Token Identifier: {key} at Address: {address}"
            )

    if not matching_esdts:
        logger.error(
            f"No ESDT details found for Token Identifier Prefix: {token_identifier} at Address: {address}"
        )
    else:
        logger.info(
            f"Retrieved ESDT details for Address {address} with Token Identifier Prefix: {token_identifier}"
        )

    return matching_esdts
