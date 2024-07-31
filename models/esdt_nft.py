from config.constants import ESDT_CONTRACT
from core.create_esdt_transaction import create_and_sign_esdt_tx
from core.create_relayed_v3_transaction import send_transaction_and_check_for_success
from utils.esdt_helpers import (
    convert_create_esdt_nft_tx_to_hex,
    convert_esdt_nft_props_to_hex,
    convert_esdt_nft_transfer_to_hex,
    convert_modify_creator_to_hex,
    convert_modify_royalties_to_hex,
    convert_multi_tokens_transfer_to_hex,
    convert_recreate_metadata_to_hex,
    convert_roles_assigning_to_hex,
    convert_set_new_uris_to_hex,
)


class NFT:
    def __init__(self, wallet):
        self.wallet = wallet
        self.toke_identifier = None

    def issue_nft(self, token_name, token_ticker, initial_value):
        nonce = self.wallet.get_nonce_and_increment()
        data = convert_esdt_nft_props_to_hex(
            token_name=token_name, token_ticker=token_ticker
        ).encode()
        esdt_issue_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=ESDT_CONTRACT,
            data=data,
            nonce=nonce,
            value=initial_value,
        )
        tx_hash = send_transaction_and_check_for_success(esdt_issue_tx)
        return tx_hash

    def assign_roles(self, assigned_address, token_identifier, roles):
        nonce = self.wallet.get_nonce_and_increment()
        data = convert_roles_assigning_to_hex(
            token_identifier=token_identifier,
            assigned_address=assigned_address.get_address().hex(),
            roles=roles,
        ).encode()
        esdt_set_nft_role_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=ESDT_CONTRACT,
            data=data,
            nonce=nonce,
            value=0,
        )
        tx_hash = send_transaction_and_check_for_success(esdt_set_nft_role_tx)
        return tx_hash

    def create_nft(
        self, token_identifier, nft_name, quantity, royalties, hash_value, attributes
    ):
        nonce = self.wallet.get_nonce_and_increment()
        data = convert_create_esdt_nft_tx_to_hex(
            token_identifier=token_identifier,
            quantity=quantity,
            nft_name=nft_name,
            royalties=royalties,
            hash_value=hash_value,
            attributes=attributes,
        ).encode()
        esdt_create_nft_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=self.wallet.public_address(),
            data=data,
            nonce=nonce,
            value=0,
        )
        tx_hash = send_transaction_and_check_for_success(esdt_create_nft_tx)
        return tx_hash

    def transfer_nfts(self, nft_holder_wallet, token_identifier, nft_details):
        sender_nonce = self.wallet.get_nonce_and_increment()
        data = convert_multi_tokens_transfer_to_hex(
            receiver_address=nft_holder_wallet.get_address().hex(),
            token_identifier=token_identifier,
            tokens=nft_details,
        ).encode()
        esdt_nft_multi_transfer_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=self.wallet.public_address(),
            data=data,
            nonce=sender_nonce,
            value=0,
            gas_limit=550000000,
        )
        send_transaction_and_check_for_success(esdt_nft_multi_transfer_tx)

    def transfer_single_nft(self, nft_holder_wallet, token_identifier, nonce, quantity):
        sender_nonce = self.wallet.get_nonce_and_increment()
        data = convert_esdt_nft_transfer_to_hex(
            token_identifier=token_identifier,
            nonce=nonce,
            quantity=quantity,
            destination_address=nft_holder_wallet.get_address().hex(),
        ).encode()
        esdt_nft_transfer_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=self.wallet.public_address(),
            data=data,
            nonce=sender_nonce,
            value=0,
        )
        tx_hash = send_transaction_and_check_for_success(esdt_nft_transfer_tx)
        return tx_hash

    def modify_royalties(self, token_identifier, nonce, new_royalty):
        sender_nonce = self.wallet.get_nonce_and_increment()
        data = convert_modify_royalties_to_hex(
            token_identifier, nonce, new_royalty
        ).encode()
        modify_royalties_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=self.wallet.public_address(),
            data=data,
            nonce=sender_nonce,
            value=0,
        )
        tx_hash = send_transaction_and_check_for_success(modify_royalties_tx)
        return tx_hash

    def set_new_uris(self, token_identifier, nonce, uris):
        sender_nonce = self.wallet.get_nonce_and_increment()
        data = convert_set_new_uris_to_hex(token_identifier, nonce, uris).encode()
        set_new_uris_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=self.wallet.public_address(),
            data=data,
            nonce=sender_nonce,
            value=0,
        )
        tx_hash = send_transaction_and_check_for_success(set_new_uris_tx)
        return tx_hash

    def modify_creator(self, token_identifier, nonce):
        sender_nonce = self.wallet.get_nonce_and_increment()
        data = convert_modify_creator_to_hex(token_identifier, nonce).encode()
        modify_creator_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=self.wallet.public_address(),
            data=data,
            nonce=sender_nonce,
            value=0,
        )
        tx_hash = send_transaction_and_check_for_success(modify_creator_tx)
        return tx_hash

    def recreate_metadata(
        self,
        token_identifier,
        nonce,
        token_name,
        royalties,
        hash_value,
        attributes,
        uris,
    ):
        sender_nonce = self.wallet.get_nonce_and_increment()
        data = convert_recreate_metadata_to_hex(
            token_identifier=token_identifier,
            nonce=nonce,
            token_name=token_name,
            royalties=royalties,
            hash_value=hash_value,
            attributes=attributes,
            uris=uris,
        ).encode()
        recreate_metadata_tx = create_and_sign_esdt_tx(
            sender_wallet=self.wallet,
            receiver_wallet=self.wallet.public_address(),
            data=data,
            nonce=sender_nonce,
            value=0,
        )
        tx_hash = send_transaction_and_check_for_success(recreate_metadata_tx)
        return tx_hash
