from pathlib import Path

from config.constants import ESDT_CONTRACT, WALLETS_FOLDER
from core.chain_commander import is_chain_online
from core.create_esdt_transaction import create_and_sign_esdt_inner_tx
from core.create_relayed_v3_transaction import (
    create_and_sign_relayed_v3_transaction,
    send_transaction_and_check_for_success,
)
from core.get_esdt import get_esdt_roles, get_single_esdt_details
from core.get_esdt_nft import has_nft_token
from core.get_transaction_info import get_token_identifier_from_esdt_tx
from models.wallet import Wallet
from utils.esdt_helpers import (
    convert_create_esdt_nft_tx_to_hex,
    convert_esdt_nft_props_to_hex,
    convert_esdt_nft_transfer_to_hex,
    convert_roles_assigning_to_hex,
)
from utils.helpers import base64_to_string


def test_transfer_inner_single_nft_tx_cross_sd(blockchain):
    """
    Test Steps:
    1. Ensure the blockchain is online.
    2. Initialize wallets for sender, receiver, NFT holder, and relayer, from shard 0,1,2
    3. Set initial balances for sender, receiver, and relayer wallets.
    4. Retrieve initial nonces and balances for sender, receiver, NFT holder, and relayer wallets.
    5. Issue a new ESDT NFT token from the sender wallet using the relayer.
    6. Assign NFT creation and burn roles to the receiver wallet using the relayer.
    7. Create an NFT using the receiver wallet with specific attributes, through the relayer.
    8. Verify the NFT creation details in the receiver wallet.
    9. Transfer the created NFT to the NFT holder wallet through the relayer.
    10. Verify the NFT details in the NFT holder wallet after transfer.
    11. Verify final nonces and balances for all wallets.
    """

    # Ensure the blockchain is online
    assert is_chain_online()

    # Initialize wallets
    sender_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_0_wallet_key_5.pem"))
    receiver_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_0_bob.pem"))
    nft_holder_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_1_wallet_key_7.pem"))
    relayer_wallet = Wallet(Path(WALLETS_FOLDER + "/sd_0_wallet_key_9.pem"))

    # Set balances for wallets
    INITIAL_BALANCE = "15000000000000000000"  # 15 EGLD
    assert "success" in sender_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in receiver_wallet.set_balance(INITIAL_BALANCE)
    assert "success" in relayer_wallet.set_balance(INITIAL_BALANCE)

    # Get initial account data
    receiver_nonce_before = receiver_wallet.get_nonce()
    nft_holder_nonce_before = nft_holder_wallet.get_nonce()
    sender_nonce_before = sender_wallet.get_nonce()
    relayer_nonce_before = relayer_wallet.get_nonce()

    receiver_balance_before = int(receiver_wallet.get_balance())
    nft_holder_balance_before = int(nft_holder_wallet.get_balance())
    sender_balance_before = int(sender_wallet.get_balance())
    # relayer_balance_before = int(relayer_wallet.get_balance())

    # Issue a new ESDT NFT token from the sender wallet using the relayer
    token_name = "TEST"
    token_ticker = "TST"
    data = convert_esdt_nft_props_to_hex(
        token_name=token_name, token_ticker=token_ticker
    ).encode()
    # TODO fix the test with following value 50000000000000000
    mint_price = 5000000000000000000
    esdt_issue_tx = create_and_sign_esdt_inner_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=ESDT_CONTRACT,
        relayer_wallet=relayer_wallet,
        data=data,
        nonce=sender_wallet.get_nonce(),
        value=mint_price,
    )

    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[esdt_issue_tx],
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce(),
        gas_limit=600000000,
    )
    esdt_issue_tx_hash = send_transaction_and_check_for_success(relayed_v3_tx)
    assert has_nft_token(address=sender_wallet.public_address()) == True

    token_identifier = get_token_identifier_from_esdt_tx(esdt_issue_tx_hash)

    # Assign NFT creation and burn roles to the receiver wallet using the relayer
    roles = ["ESDTRoleNFTCreate", "ESDTRoleNFTBurn"]
    data = convert_roles_assigning_to_hex(
        token_identifier=token_identifier,
        assigned_address=receiver_wallet.get_address().hex(),
        roles=roles,
    ).encode()
    esdt_set_nft_role_tx = create_and_sign_esdt_inner_tx(
        sender_wallet=sender_wallet,
        receiver_wallet=ESDT_CONTRACT,
        relayer_wallet=relayer_wallet,
        data=data,
        nonce=sender_wallet.get_nonce(),
        value=0,
    )
    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[esdt_set_nft_role_tx],
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce(),
        gas_limit=600000000,
    )
    send_transaction_and_check_for_success(relayed_v3_tx)
    assert has_nft_token(address=sender_wallet.public_address()) == True

    retrieved_roles = get_esdt_roles(receiver_wallet.public_address())
    assert all(
        role in retrieved_roles for role in roles
    ), f"Expected roles {roles}, but got {retrieved_roles}"

    # Create an NFT using the receiver wallet with specific attributes, through the relayer
    quantity = 1
    nft_name = "test song"
    royalties = 7500  # 75%
    hash_value = "00"
    attributes = (
        "tags:test,free,fun;metadata:This is a test description for an awesome NFT"
    )

    data = convert_create_esdt_nft_tx_to_hex(
        token_identifier=token_identifier,
        quantity=quantity,
        nft_name=nft_name,
        royalties=royalties,
        hash_value=hash_value,
        attributes=attributes,
    ).encode()

    esdt_create_nft_tx = create_and_sign_esdt_inner_tx(
        sender_wallet=receiver_wallet,
        receiver_wallet=receiver_wallet.public_address(),
        relayer_wallet=relayer_wallet,
        data=data,
        nonce=receiver_wallet.get_nonce(),
        value=0,
    )
    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[esdt_create_nft_tx],
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce(),
        gas_limit=600000000,
    )
    send_transaction_and_check_for_success(relayed_v3_tx)

    nft_holder_details = get_single_esdt_details(
        address=receiver_wallet.public_address(), token_identifier=token_identifier
    )
    assert str(quantity) == nft_holder_details.get("balance")
    assert receiver_wallet.public_address() == nft_holder_details.get("creator")
    assert nft_name == nft_holder_details.get("name")
    assert str(royalties) == nft_holder_details.get("royalties")
    assert token_identifier in nft_holder_details.get("tokenIdentifier")
    assert nft_holder_details.get("uris") is not None
    decoded_metadata = base64_to_string(nft_holder_details.get("uris")[0])
    assert attributes == decoded_metadata

    # Transfer the created NFT to the NFT holder wallet through the relayer
    data = convert_esdt_nft_transfer_to_hex(
        token_identifier=token_identifier,
        nonce=1,
        quantity=quantity,
        destination_address=nft_holder_wallet.get_address().hex(),
    ).encode()
    esdt_nft_transfer_tx = create_and_sign_esdt_inner_tx(
        sender_wallet=receiver_wallet,
        receiver_wallet=receiver_wallet.public_address(),
        relayer_wallet=relayer_wallet,
        data=data,
        nonce=receiver_wallet.get_nonce(),
        value=0,
    )
    relayed_v3_tx = create_and_sign_relayed_v3_transaction(
        inner_transactions=[esdt_nft_transfer_tx],
        relayer_wallet=relayer_wallet,
        nonce=relayer_wallet.get_nonce(),
        gas_limit=600000000,
    )
    send_transaction_and_check_for_success(relayed_v3_tx)

    nft_holder_details = get_single_esdt_details(
        address=nft_holder_wallet.public_address(), token_identifier=token_identifier
    )
    assert str(quantity) == nft_holder_details.get("balance")
    assert receiver_wallet.public_address() == nft_holder_details.get("creator")
    assert nft_name == nft_holder_details.get("name")
    assert str(royalties) == nft_holder_details.get("royalties")
    assert token_identifier in nft_holder_details.get("tokenIdentifier")
    assert nft_holder_details.get("uris") is not None
    decoded_metadata = base64_to_string(nft_holder_details.get("uris")[0])
    assert attributes == decoded_metadata

    # Verify final nonces and balances
    sender_nonce_after = sender_wallet.get_nonce()
    receiver_nonce_after = receiver_wallet.get_nonce()
    nft_holder_nonce_after = nft_holder_wallet.get_nonce()
    relayer_nonce_after = relayer_wallet.get_nonce()

    sender_balance_after = int(sender_wallet.get_balance())
    receiver_balance_after = int(receiver_wallet.get_balance())
    nft_holder_balance_after = int(nft_holder_wallet.get_balance())
    # relayer_balance_after = int(relayer_wallet.get_balance())

    # Check nonces
    assert sender_nonce_after == sender_nonce_before + 2
    assert relayer_nonce_after == relayer_nonce_before + 4
    assert receiver_nonce_after == receiver_nonce_before + 2
    assert nft_holder_nonce_after == nft_holder_nonce_before

    # Verify balances
    assert sender_balance_after == sender_balance_before - int(mint_price)
    assert receiver_balance_after == receiver_balance_before
    assert nft_holder_balance_after == nft_holder_balance_before
    # TODO: Uncomment the below line once we have a solution to deduct inner gas used properly
    # assert relayer_balance_after == relayer_balance_before
