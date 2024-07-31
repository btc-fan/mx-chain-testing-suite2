import json
from pathlib import Path

import requests
from multiversx_sdk.core.address import Address
from multiversx_sdk.wallet.user_signer import UserSigner

from config.config import DEFAULT_PROXY, proxy_default
from utils.logger import logger


class Wallet:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.nonce = None
        logger.info(f"Wallet initialized with path: {self.path}")

    def public_address(self) -> str:
        with open(self.path) as f:
            lines = f.readlines()

        for line in lines:
            if "BEGIN" in line:
                line = line.split(" ")
                address = line[-1].replace("-----", "").strip()
                return address

    def get_balance(self) -> int:
        address = self.public_address()
        logger.info(f"Fetching balance for address: {address}")
        response = requests.get(f"{DEFAULT_PROXY}/address/{address}/balance")
        response.raise_for_status()
        parsed = response.json()

        general_data = parsed.get("data")
        balance = general_data.get("balance")
        logger.info(f"Retrieved balance: {balance} for address: {address}")

        return balance

    def set_balance(self, egld_amount):
        address = self.public_address()
        logger.info(f"Setting balance for address: {address} to {egld_amount}")
        details = {"address": address, "balance": egld_amount}

        details_list = [details]
        json_structure = json.dumps(details_list)
        req = requests.post(f"{DEFAULT_PROXY}/simulator/set-state", data=json_structure)
        logger.info(f"Set balance request status: {req.status_code}")

        return req.text

    def get_signer(self) -> UserSigner:
        logger.info("Creating UserSigner from PEM file.")
        return UserSigner.from_pem_file(self.path)

    def get_address(self) -> Address:
        address = self.public_address()
        return Address.from_bech32(address)

    def get_account(self):
        account = proxy_default.get_account(self.get_address())
        logger.info(f"Retrieved account details for: {account.address.to_bech32()}")
        return account

    def get_pem_path(self) -> str:
        """
        Retrieves the pem PATH for a given wallet.

        Returns:
            str: Full PEM Path
        """
        logger.info(f"Returned wallet path: {self.path}")
        return self.path

    def fetch_nonce_from_server(self) -> int:
        """
        Fetches the nonce for the wallet's address from the server.

        Returns:
            int: The nonce of the wallet's address.
        """
        address = self.public_address()
        logger.info(f"Checking Nonce for Address: {address}")
        response = requests.get(f"{DEFAULT_PROXY}/address/{address}/nonce")
        response.raise_for_status()
        nonce = response.json()["data"]["nonce"]
        logger.info(f"Address Nonce: {nonce}")
        return nonce

    def get_nonce(self) -> int:
        """
         Fetches the nonce for the wallet's address from the server.

        Returns:
            int: The nonce of the address.
        """
        address = self.public_address()
        logger.info(f"Checking Nonce for Address: {address}")
        response = requests.get(f"{DEFAULT_PROXY}/address/{address}/nonce")
        response.raise_for_status()
        self.nonce = response.json()["data"]["nonce"]
        logger.info(f"Address Nonce: {self.nonce}")
        return self.nonce

    def get_nonce_and_increment(self) -> int:
        """
        Retrieves the nonce for a given address and then increments.
        Returns:
            int: The incremented nonce of the address.
        """
        if self.nonce is None:
            self.nonce = self.fetch_nonce_from_server()
        current_nonce = self.nonce
        self.nonce += 1
        logger.info(
            f"Current nonce for address {self.public_address()}: {current_nonce}"
        )
        logger.info(
            f"Incremented nonce for address {self.public_address()}: {self.nonce}"
        )
        return current_nonce
