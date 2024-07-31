from pathlib import Path

from config.constants import WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.get_esdt import get_esdt_roles, get_single_esdt_details
from core.get_esdt_nft import has_nft_token
from core.get_transaction_info import get_token_identifier_from_esdt_tx
from models.esdt_nft import NFT
from models.wallet import Wallet
from utils.helpers import base64_to_string


def test_transfer_nft_tx_same_shard(blockchain):
    """
    Test Steps:
    1. Ensure the blockchain is online.
    2. Initialize wallets for sender, receiver, and NFT holder.
    3. Set initial balances for sender and receiver wallets.
    4. Retrieve initial nonces and balances for sender and receiver wallets.
    5. Issue a new ESDT NFT token from the sender wallet.
    6. Assign NFT creation and burn roles to the receiver wallet.
    7. Create an NFT using the receiver wallet with specific attributes.
    8. Verify the NFT creation details in the receiver wallet.
    9. Transfer the created NFT to the NFT holder wallet.
    10. Verify the NFT details in the NFT holder wallet after transfer.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_1.pem"))  # Shard 1
    receiver_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_6.pem"))  # Shard 1
    nft_holder_wallet = Wallet(
        Path(WALLETS_FOLDER + "/sd_1_wallet_key_7.pem")
    )  # Shard 1

    # Initialize ESDTNFT instances
    sender_nft = NFT(sender_wallet)
    receiver_nft = NFT(receiver_wallet)

    # Set balances for wallets
    INITIAL_BALANCE = "15000000000000000000"  # 15 EGLD
    assert "success" in sender_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in receiver_wallet.set_balance(INITIAL_BALANCE)

    # Issue a new ESDT NFT token from the sender wallet
    token_name = "TEST"
    token_ticker = "TST"
    initial_value = 50000000000000000
    esdt_issue_tx_hash = sender_nft.issue_nft(token_name, token_ticker, initial_value)
    assert has_nft_token(address=sender_wallet.public_address()) == True

    token_identifier = get_token_identifier_from_esdt_tx(esdt_issue_tx_hash)

    # Assign NFT creation and burn roles to the receiver wallet
    roles = ["ESDTRoleNFTCreate", "ESDTRoleNFTBurn"]
    sender_nft.assign_roles(
        assigned_address=receiver_wallet, token_identifier=token_identifier, roles=roles
    )
    retrieved_roles = get_esdt_roles(receiver_wallet.public_address())
    assert all(
        role in retrieved_roles for role in roles
    ), f"Expected roles {roles}, but got {retrieved_roles}"

    # Create an NFT using the receiver wallet with specific attributes
    quantity = 1
    nft_name = "test song"
    royalties = 7500  # 75%
    hash_value = "00"
    attributes = (
        "tags:test,free,fun;metadata:This is a test description for an awesome nft"
    )
    receiver_nft.create_nft(
        token_identifier, nft_name, quantity, royalties, hash_value, attributes
    )

    # Verify the NFT creation details in the receiver wallet
    nft_holder_details = get_single_esdt_details(
        address=receiver_wallet.public_address(), token_identifier=token_identifier
    )
    assert str(quantity) == nft_holder_details.get("balance")
    assert receiver_wallet.public_address() == nft_holder_details.get("creator")
    assert nft_name == nft_holder_details.get("name")
    assert 1 == nft_holder_details.get("nonce")
    assert str(royalties) == nft_holder_details.get("royalties")
    assert token_identifier in nft_holder_details.get("tokenIdentifier")
    assert nft_holder_details.get("uris") is not None
    decoded_metadata = base64_to_string(nft_holder_details.get("uris")[0])
    assert attributes == decoded_metadata

    # Transfer the created NFT to the NFT holder wallet
    receiver_nft.transfer_single_nft(nft_holder_wallet, token_identifier, 1, quantity)

    # Verify the NFT details in the NFT holder wallet after transfer
    nft_holder_details = get_single_esdt_details(
        address=nft_holder_wallet.public_address(), token_identifier=token_identifier
    )
    assert str(quantity) == nft_holder_details.get("balance")
    assert receiver_wallet.public_address() == nft_holder_details.get("creator")
    assert nft_name == nft_holder_details.get("name")
    assert 1 == nft_holder_details.get("nonce")
    assert str(royalties) == nft_holder_details.get("royalties")
    assert token_identifier in nft_holder_details.get("tokenIdentifier")
    assert nft_holder_details.get("uris") is not None
    decoded_metadata = base64_to_string(nft_holder_details.get("uris")[0])
    assert attributes == decoded_metadata
