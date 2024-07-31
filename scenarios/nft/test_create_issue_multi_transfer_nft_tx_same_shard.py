from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.get_esdt import get_esdt_roles, get_multiple_esdt_details
from core.get_esdt_nft import has_nft_token
from core.get_transaction_info import get_token_identifier_from_esdt_tx
from models.esdt_nft import NFT
from models.wallet import Wallet
from utils.helpers import base64_to_string


# TODO Failed test due to bug in progress
def test_multi_transfer_nft_same_shard(blockchain):
    """
    Test Steps:
    1. Ensure the blockchain is online.
    2. Initialize wallets for sender, receiver, and NFT holder.
    3. Set initial balances for sender and receiver wallets.
    4. Retrieve initial nonces and balances for sender and receiver wallets.
    5. Issue a new ESDT NFT token from the sender wallet.
    6. Assign NFT creation and burn roles to the sender wallet.
    7. Create multiple NFTs using the sender wallet with specific attributes.
    8. Verify the NFT creation details in the sender wallet.
    9. Transfer the created NFTs to the NFT holder wallet.
    10. Verify the NFT details in the NFT holder wallet after transfer.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))  # Shard 1
    nft_holder_wallet = Wallet(
        Path(WALLETS_FOLDER + "/sd_1_wallet_key_7.pem")
    )  # Shard 1

    # Initialize ESDTNFT instance
    sender_nft = NFT(sender_wallet)

    # Set balances for wallets
    INITIAL_BALANCE = "150000000000000000000"  # 15 EGLD
    assert "success" in sender_wallet.set_balance(INITIAL_BALANCE)

    # Issue a new ESDT NFT token from the sender wallet
    token_name = "TEST"
    token_ticker = "TST"
    initial_value = 50000000000000000
    esdt_issue_tx_hash = sender_nft.issue_nft(token_name, token_ticker, initial_value)
    assert has_nft_token(address=sender_wallet.public_address()) == True

    token_identifier = get_token_identifier_from_esdt_tx(esdt_issue_tx_hash)

    # Assign NFT creation and burn roles to the sender wallet
    roles = ["ESDTRoleNFTCreate", "ESDTRoleNFTBurn"]
    sender_nft.assign_roles(
        assigned_address=sender_wallet, token_identifier=token_identifier, roles=roles
    )
    retrieved_roles = get_esdt_roles(sender_wallet.public_address())
    assert all(
        role in retrieved_roles for role in roles
    ), f"Expected roles {roles}, but got {retrieved_roles}"

    # Create multiple NFTs using the sender wallet with specific attributes
    nft_details_list = []
    for i in range(1, 4):  # Creates 3 NFTs
        nft_name = f"test song {i}"
        attributes = f"tags:test,free,fun;metadata:This is a test description for an awesome NFT {nft_name}"
        quantity = 1
        royalties = 7500  # 75%
        hash_value = "00"

        sender_nft.create_nft(
            token_identifier, nft_name, quantity, royalties, hash_value, attributes
        )
        nft_details_list.append(
            {
                "nft_name": nft_name,
                "attributes": attributes,
                "quantity": quantity,
                "royalties": royalties,
                "hash_value": hash_value,
                "token_identifier": token_identifier,
                "nonce": i,
            }
        )

    nft_holder_details = get_multiple_esdt_details(
        address=sender_wallet.public_address(), token_identifier=token_identifier
    )

    # Assert details for each NFT
    for expected, actual in zip(nft_details_list, nft_holder_details):
        assert str(expected["quantity"]) == actual.get("balance"), "Quantity mismatch."
        assert sender_wallet.public_address() == actual.get(
            "creator"
        ), "Creator address mismatch."
        assert expected["nft_name"] == actual.get("name"), "NFT name mismatch."
        assert expected["nonce"] == actual.get("nonce"), "Nonce mismatch."
        assert str(expected["royalties"]) == actual.get(
            "royalties"
        ), "Royalties mismatch."
        assert expected["token_identifier"] + f"-{expected['nonce']:02}" in actual.get(
            "tokenIdentifier"
        ), "Token identifier mismatch."
        assert actual.get("uris") is not None, "URIs should not be None."
        decoded_metadata = base64_to_string(actual.get("uris")[0])
        assert expected["attributes"] == decoded_metadata, "Metadata mismatch."

    # Transfer the created NFTs to the NFT holder wallet
    sender_nft.transfer_nfts(nft_holder_wallet, token_identifier, nft_holder_details)

    nft_holder_details = get_multiple_esdt_details(
        address=nft_holder_wallet.public_address(), token_identifier=token_identifier
    )

    # Assert details for each NFT after transfer
    for expected, actual in zip(nft_details_list, nft_holder_details):
        assert str(expected["quantity"]) == actual.get("balance"), "Quantity mismatch."
        assert sender_wallet.public_address() == actual.get(
            "creator"
        ), "Creator address mismatch."
        assert expected["nft_name"] == actual.get("name"), "NFT name mismatch."
        assert expected["nonce"] == actual.get("nonce"), "Nonce mismatch."
        assert str(expected["royalties"]) == actual.get(
            "royalties"
        ), "Royalties mismatch."
        assert expected["token_identifier"] + f"-{expected['nonce']:02}" in actual.get(
            "tokenIdentifier"
        ), "Token identifier mismatch."
        assert actual.get("uris") is not None, "URIs should not be None."
        decoded_metadata = base64_to_string(actual.get("uris")[0])
        assert expected["attributes"] == decoded_metadata, "Metadata mismatch."
