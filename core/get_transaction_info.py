import base64

import requests

from config.config import DEFAULT_PROXY
from utils.helpers import string_to_base64
from utils.logger import logger


def get_status_of_tx(tx_hash: str) -> str:
    logger.info(f"Checking transaction status for hash: {tx_hash}")
    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}/process-status")
    response.raise_for_status()
    parsed = response.json()

    if "transaction not found" in response.text:
        return "expired"

    general_data = parsed.get("data")
    status = general_data.get("status")
    logger.info(f"Transaction status: {status} for tx_hash: {tx_hash}")
    return status


def check_if_error_is_present_in_tx(error, tx_hash) -> bool:
    logger.info(f"Checking for error in transaction {tx_hash}")
    error_bytes = string_to_base64(error)

    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=True")
    response.raise_for_status()
    error_present = error_bytes.decode() in response.text or error in response.text
    logger.info(f"Error presence: {error_present} | in tx_hash: {tx_hash}")

    return error_present


def get_gas_used_from_tx(tx_hash: str) -> str:
    logger.info(f"Fetching gas used for transaction {tx_hash}")
    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=true")
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    transaction = general_data.get("transaction")
    gas_used = transaction.get("fee")

    logger.info(f"Gas used: {gas_used} for tx_hash: {tx_hash}")
    return gas_used


def get_token_identifier_from_esdt_tx(tx_hash: str) -> str:
    logger.info(f"Fetching token identifier from tx: {tx_hash}")
    try:
        response = requests.get(
            f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=true"
        )
        response.raise_for_status()
        parsed = response.json()

        transaction = parsed.get("data", {}).get("transaction", {})
        logs = transaction.get("logs", {}).get("events", [])
        scrs = transaction.get("smartContractResults", [])

        def extract_token_identifier(events):
            for event in events:
                if event.get("identifier") in ["issueNonFungible", "issue"]:
                    topics = event.get("topics", [])
                    if topics:
                        encoded_identifier = topics[0]
                        return base64.b64decode(encoded_identifier).decode("utf-8")
            return None

        token_identifier = extract_token_identifier(logs)

        if not token_identifier:
            for scr in scrs:
                events = scr.get("logs", {}).get("events", [])
                token_identifier = extract_token_identifier(events)
                if token_identifier:
                    break

        if token_identifier:
            logger.info(
                f"Token identifier found: {token_identifier} for tx_hash: {tx_hash}"
            )
        else:
            logger.error(f"No token identifier found for tx_hash: {tx_hash}")

        return token_identifier

    except requests.RequestException as e:
        logger.error(
            f"Failed to fetch transaction details for tx_hash: {tx_hash} due to {e}"
        )
        return None
