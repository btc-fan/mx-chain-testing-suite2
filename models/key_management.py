import json

import requests

from config.config import DEFAULT_PROXY, proxy_default
from core.chain_commander import add_blocks, add_blocks_until_epoch_reached
from models.validatorKey import ValidatorKey
from utils.logger import logger


def add_key(keys: list[ValidatorKey]) -> str:
    logger.info("Adding keys to simulator")
    private_keys = []
    for key in keys:
        private_keys.append(key.get_private_key())

    post_body = {"privateKeysBase64": private_keys}

    json_structure = json.dumps(post_body)
    req = requests.post(f"{DEFAULT_PROXY}/simulator/add-keys", data=json_structure)

    logger.info("Keys added successfully")
    return req.text


def add_blocks_until_key_eligible(keys: list[ValidatorKey]) -> ValidatorKey:
    logger.info("Attempting to reach eligibility for given keys")
    flag = False
    while not flag:
        for key in keys:
            if key.get_state() == "eligible":
                eligible_key = key
                print("eligible key found")
                flag = True

            else:
                print("no eligible key found , moving to next epoch...")
                current_epoch = proxy_default.get_network_status().epoch_number
                add_blocks_until_epoch_reached(current_epoch + 1)
                add_blocks(3)

    logger.info(f"Key {eligible_key.get_public_key()} is now eligible")
    return eligible_key
