import requests
from multiversx_sdk.core.address import Address

from config.config import DEFAULT_PROXY
from utils.helpers import base64_to_hex
from utils.logger import logger


def get_delegation_contract_address_from_tx(tx_hash):
    logger.info(f"Fetching transaction details for hash: {tx_hash}")
    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=True")
    response.raise_for_status()
    parsed = response.json()

    logger.debug("Parsing transaction data")
    general_data = parsed.get("data")
    transaction_data = general_data.get("transaction")
    logs_data = transaction_data.get("logs")
    events_data = logs_data.get("events")
    first_set_of_events = events_data[0]
    topics = first_set_of_events.get("topics")
    delegation_contract_address = topics[1]

    delegation_contract_address = base64_to_hex(delegation_contract_address)
    delegation_contract_address = Address.from_hex(
        delegation_contract_address, "erd"
    ).to_bech32()
    logger.info(f"Delegation contract address obtained: {delegation_contract_address}")
    return delegation_contract_address


def get_delegation_sc_address_from_sc_results_using_inner_tx(tx_hash):
    logger.info(f"Fetching transaction details for hash: {tx_hash}")
    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=True")
    response.raise_for_status()
    parsed = response.json()

    logger.debug("Parsing transaction data")
    transaction_data = parsed.get("data", {}).get("transaction", {})
    sc_results = transaction_data.get("smartContractResults", [])

    for sc_result in sc_results:
        logs_data = sc_result.get("logs")
        if logs_data:
            events_data = logs_data.get("events")
            if events_data:
                for event in events_data:
                    topics = event.get("topics")
                    for topic in topics:
                        try:
                            possible_address = base64_to_hex(topic)
                            delegation_contract_address = Address.from_hex(
                                possible_address, "erd"
                            ).to_bech32()
                            logger.info(
                                f"Delegation contract address obtained for inner tx: {delegation_contract_address}"
                            )
                            return delegation_contract_address
                        except Exception as e:
                            logger.debug(
                                f"Failed to convert topic to address: {str(e)}"
                            )
                            continue
    error_message = "Delegation contract address not found in transaction results."
    logger.error(error_message)
    raise ValueError(error_message)
    return None
