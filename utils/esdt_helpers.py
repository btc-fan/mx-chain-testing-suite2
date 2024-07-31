from utils.helpers import (
    base64_to_hex,
    decimal_to_hex,
    flag_to_hex,
    string_to_base64,
    string_to_hex,
)
from utils.logger import logger


def convert_esdt_props_to_hex(
    token_name: str,
    token_ticker: str,
    initial_supply: str,
    nr_of_decimals: str,
    can_freeze: str = "true",
    can_wipe: str = "true",
    can_pause: str = "true",
    can_change_owner: str = "true",
    can_upgrade: str = "true",
    can_add_special_roles: str = "true",
) -> str:
    """
    Converts ESDT properties to hexadecimal format.

    Args:
        token_name (str): The name of the token.
        token_ticker (str): The ticker of the token.
        initial_supply (str): The initial supply of the token.
        nr_of_decimals (str): The number of decimals for the token.
        can_freeze (str, optional): Whether the token can be frozen. Defaults to "true".
        can_wipe (str, optional): Whether the token can be wiped. Defaults to "true".
        can_pause (str, optional): Whether the token can be paused. Defaults to "true".
        can_change_owner (str, optional): Whether the token owner can be changed. Defaults to "true".
        can_upgrade (str, optional): Whether the token can be upgraded. Defaults to "true".
        can_add_special_roles (str, optional): Whether special roles can be added to the token. Defaults to "true".

    Returns:
        str: The hexadecimal string representing the ESDT properties.
    """

    # Encode strings to base64 and then to hexadecimal
    token_name_hex = base64_to_hex(string_to_base64(token_name))
    token_ticker_hex = base64_to_hex(string_to_base64(token_ticker))
    initial_supply_hex = decimal_to_hex(int(initial_supply))
    nr_of_decimals_hex = decimal_to_hex(int(nr_of_decimals))

    # Construct hex parts for each flag
    can_freeze_hex = flag_to_hex("canFreeze", can_freeze)
    can_wipe_hex = flag_to_hex("canWipe", can_wipe)
    can_pause_hex = flag_to_hex("canPause", can_pause)
    can_change_owner_hex = flag_to_hex("canChangeOwner", can_change_owner)
    can_upgrade_hex = flag_to_hex("canUpgrade", can_upgrade)
    can_add_special_roles_hex = flag_to_hex("canAddSpecialRoles", can_add_special_roles)

    # Construct the hexadecimal string
    hex_string = (
        "issue@"
        + token_name_hex
        + "@"
        + token_ticker_hex
        + "@"
        + initial_supply_hex
        + "@"
        + nr_of_decimals_hex
        + "@"
        + can_freeze_hex
        + "@"
        + can_wipe_hex
        + "@"
        + can_pause_hex
        + "@"
        + can_change_owner_hex
        + "@"
        + can_upgrade_hex
        + "@"
        + can_add_special_roles_hex
    )

    logger.info(f"Converted ESDT hex string: {hex_string}")

    return hex_string


def convert_roles_assigning_to_hex(
    token_identifier: str, assigned_address: str, roles: list
) -> str:
    """
    Converts roles assigning data to hexadecimal format.

    Args:
        token_identifier (str): The token identifier.
        assigned_address (str): The address to assign roles to.
        roles (list): The list of roles to assign.

    Returns:
        str: The hexadecimal string for roles assigning.
    """
    token_identifier_hex = string_to_hex(token_identifier)
    # assigned_address_hex = string_to_hex(assigned_address)

    roles_hex = [role.encode("utf-8").hex() for role in roles]

    hex_string = (
        "setSpecialRole@"
        + token_identifier_hex
        + "@"
        + assigned_address
        + "".join(["@" + role_hex for role_hex in roles_hex])
    )

    return hex_string


def convert_esdt_nft_props_to_hex(
    token_name: str,
    token_ticker: str,
    can_freeze: str = "true",
    can_wipe: str = "true",
    can_pause: str = "true",
    can_transfer_nft_create_role: str = "true",
    can_change_owner: str = "true",
    can_upgrade: str = "true",
    can_add_special_roles: str = "true",
) -> str:
    """
    Converts ESDT NFT properties to hexadecimal format.

    Args:
        token_name (str): The name of the NFT token.
        token_ticker (str): The ticker of the NFT token.
        can_freeze (str, optional): Whether the NFT can be frozen. Defaults to "true".
        can_wipe (str, optional): Whether the NFT can be wiped. Defaults to "true".
        can_pause (str, optional): Whether the NFT can be paused. Defaults to "true".
        can_transfer_nft_create_role (str, optional): Whether the NFT create role can be transferred. Defaults to "true".
        can_change_owner (str, optional): Whether the NFT owner can be changed. Defaults to "true".
        can_upgrade (str, optional): Whether the NFT can be upgraded. Defaults to "true".
        can_add_special_roles (str, optional): Whether special roles can be added to the NFT. Defaults to "true".

    Returns:
        str: The hexadecimal string representing the ESDT NFT properties.
    """
    token_name_hex = base64_to_hex(string_to_base64(token_name))
    token_ticker_hex = base64_to_hex(string_to_base64(token_ticker))

    can_freeze_hex = flag_to_hex("canFreeze", can_freeze)
    can_wipe_hex = flag_to_hex("canWipe", can_wipe)
    can_pause_hex = flag_to_hex("canPause", can_pause)
    can_transfer_nft_create_role_hex = flag_to_hex(
        "canTransferNFTCreateRole", can_transfer_nft_create_role
    )
    can_change_owner_hex = flag_to_hex("canChangeOwner", can_change_owner)
    can_upgrade_hex = flag_to_hex("canUpgrade", can_upgrade)
    can_add_special_roles_hex = flag_to_hex("canAddSpecialRoles", can_add_special_roles)

    hex_string = (
        "issueNonFungible@"
        + token_name_hex
        + "@"
        + token_ticker_hex
        + "@"
        + can_freeze_hex
        + "@"
        + can_wipe_hex
        + "@"
        + can_pause_hex
        + "@"
        + can_transfer_nft_create_role_hex
        + "@"
        + can_change_owner_hex
        + "@"
        + can_upgrade_hex
        + "@"
        + can_add_special_roles_hex
    )

    logger.info(f"Converted ESDT hex string: {hex_string}")

    return hex_string


def convert_create_esdt_nft_tx_to_hex(
    token_identifier: str,
    quantity: int,
    nft_name: str,
    royalties: int,
    hash_value: str,
    attributes: str,
    uri: str = "",
    additional_uri: str = "",
) -> str:
    """
    Converts ESDT NFT creation data to hexadecimal format.

    Args:
        token_identifier (str): The token identifier.
        quantity (int): The quantity of NFTs to create.
        nft_name (str): The name of the NFT.
        royalties (int): The royalties for the NFT.
        hash_value (str): The hash value for the NFT.
        attributes (str): The attributes of the NFT.
        uri (str, optional): The URI for the NFT. Defaults to an empty string.
        additional_uri (str, optional): An additional URI for the NFT. Defaults to an empty string.

    Returns:
        str: The hexadecimal string for creating an ESDT NFT.
    """
    token_identifier_hex = string_to_hex(token_identifier)
    quantity_hex = decimal_to_hex(quantity)
    nft_name_hex = string_to_hex(nft_name)
    royalties_hex = decimal_to_hex(royalties)
    attributes_hex = string_to_hex(attributes)
    uri_hex = string_to_hex(uri) if uri else ""  # Encode only if non-empty
    additional_uri_hex = string_to_hex(additional_uri) if additional_uri else ""

    hex_parts = [
        "ESDTNFTCreate",
        token_identifier_hex,
        quantity_hex,
        nft_name_hex,
        royalties_hex,
        "@" + hash_value,
        attributes_hex,
    ]

    # Add URI if it's non-empty
    if uri_hex:
        hex_parts.append(uri_hex)

    # Add additional URI if it's non-empty
    if additional_uri_hex:
        hex_parts.append(additional_uri_hex)

    # Join all parts with '@' and ensure no empty parts are added
    hex_string = "@".join(part for part in hex_parts if part)

    return hex_string


def convert_esdt_nft_transfer_to_hex(
    token_identifier: str, nonce: int, quantity: int, destination_address: str
) -> str:
    """
    Converts ESDT NFT transfer data to hexadecimal format.

    Args:
        token_identifier (str): The token identifier.
        nonce (int): The nonce.
        quantity (int): The quantity to transfer.
        destination_address (str): The destination address.

    Returns:
        str: The hexadecimal string for ESDTNFTTransfer.
    """
    token_identifier_hex = string_to_hex(token_identifier)
    nonce_hex = decimal_to_hex(nonce)
    quantity_hex = decimal_to_hex(quantity)
    # destination_address_hex = string_to_hex(destination_address)

    hex_string = (
        "ESDTNFTTransfer@"
        + token_identifier_hex
        + "@"
        + nonce_hex
        + "@"
        + quantity_hex
        + "@"
        + destination_address
    )

    logger.info(f"Converted ESDTNFTTransfer hex string: {hex_string}")

    return hex_string


def convert_multi_tokens_transfer_to_hex(
    receiver_address: str, token_identifier: str, tokens: list
) -> str:
    """
    Constructs the 'Data' part of a MultiTokensTransferTransaction in hexadecimal format.

    Args:
        receiver_address (str): The hexadecimal address of the receiver.
        token_identifier (str): The token identifier.
        tokens (list of dict): A list of tokens to transfer, each token is a dictionary
                               with keys 'tokenIdentifier', 'nonce', and 'balance'.

    Returns:
        str: The complete 'Data' string for a MultiESDTNFTTransfer.
    """
    # receiver_hex = string_to_hex(receiver_address)
    num_tokens_hex = decimal_to_hex(len(tokens))

    tokens_data = []
    for token in tokens:
        identifier_hex = string_to_hex(token_identifier)
        nonce_hex = decimal_to_hex(token["nonce"])
        quantity_hex = decimal_to_hex(int(token["balance"]))
        tokens_data.append(identifier_hex + "@" + nonce_hex + "@" + quantity_hex)

    # Construct the full data string
    data = (
        "MultiESDTNFTTransfer@"
        + receiver_address
        + "@"
        + num_tokens_hex
        + "@"
        + "@".join(tokens_data)
    )

    return data


def convert_modify_royalties_to_hex(
    token_identifier: str, nonce: int, new_royalty: int
) -> str:
    """
    Converts data for modifying royalties to hexadecimal format.

    Args:
        token_identifier (str): The token identifier.
        nonce (int): The nonce of the token.
        new_royalty (int): The new royalty value.

    Returns:
        str: The hexadecimal string for modifying royalties.
    """
    token_identifier_hex = string_to_hex(token_identifier)
    nonce_hex = decimal_to_hex(nonce)
    new_royalty_hex = decimal_to_hex(new_royalty)

    hex_string = (
        f"ESDTModifyRoyalties@{token_identifier_hex}@{nonce_hex}@{new_royalty_hex}"
    )
    return hex_string


def convert_set_new_uris_to_hex(token_identifier: str, nonce: int, uris: list) -> str:
    """
    Converts data for setting new URIs to hexadecimal format.

    Args:
        token_identifier (str): The token identifier.
        nonce (int): The nonce of the token.
        uris (list): List of new URIs.

    Returns:
        str: The hexadecimal string for setting new URIs.
    """
    token_identifier_hex = string_to_hex(token_identifier)
    nonce_hex = decimal_to_hex(nonce)
    uris_hex = "@".join([string_to_hex(uri) for uri in uris])

    hex_string = f"ESDTNFTSetNewURIs@{token_identifier_hex}@{nonce_hex}@{uris_hex}"
    return hex_string


def convert_modify_creator_to_hex(token_identifier: str, nonce: int) -> str:
    """
    Converts data for modifying creator to hexadecimal format.

    Args:
        token_identifier (str): The token identifier.
        nonce (int): The nonce of the token.

    Returns:
        str: The hexadecimal string for modifying creator.
    """
    token_identifier_hex = string_to_hex(token_identifier)
    nonce_hex = decimal_to_hex(nonce)

    hex_string = f"ESDTNFTModifyCreator@{token_identifier_hex}@{nonce_hex}"
    return hex_string


def convert_recreate_metadata_to_hex(
    token_identifier: str,
    nonce: int,
    token_name: str,
    royalties: int,
    hash_value: str,
    attributes: str,
    uris: list,
) -> str:
    """
    Converts data for recreating metadata to hexadecimal format.

    Args:
        token_identifier (str): The token identifier.
        nonce (int): The nonce of the token.
        token_name (str): The name of the token.
        royalties (int): The royalties for the token.
        hash_value (str): The hash value for the token.
        attributes (str): The attributes of the token.
        uris (list): List of URIs.

    Returns:
        str: The hexadecimal string for recreating metadata.
    """
    token_identifier_hex = string_to_hex(token_identifier)
    nonce_hex = decimal_to_hex(nonce)
    token_name_hex = string_to_hex(token_name)
    royalties_hex = decimal_to_hex(royalties)
    hash_hex = string_to_hex(hash_value)
    attributes_hex = string_to_hex(attributes)
    uris_hex = "@".join([string_to_hex(uri) for uri in uris])

    hex_string = f"ESDTMetaDataRecreate@{token_identifier_hex}@{nonce_hex}@{token_name_hex}@{royalties_hex}@{hash_hex}@{attributes_hex}@{uris_hex}"
    return hex_string
