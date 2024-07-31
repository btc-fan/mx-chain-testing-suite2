import base64
import random
import string

from multiversx_sdk.converters.transactions_converter import TransactionsConverter

from utils.logger import logger


def base64_to_decimal(b):
    return int(base64.b64decode(b).hex(), 16)


def decimal_to_hex(value: int):
    hex_value = f"{value:x}"
    if len(hex_value) % 2 > 0:
        hex_value = "0" + hex_value
    return hex_value


def base64_to_hex(b):
    return base64.b64decode(b).hex()


def string_to_base64(s):
    return base64.b64encode(s.encode("utf-8"))


def base64_to_string(b):
    return base64.b64decode(b).decode("utf-8")


def string_to_hex(s: str) -> str:
    return s.encode("utf-8").hex()


def replace_random_data_with_another_random_data(input_string: str) -> str:
    def generate_random_letter() -> str:
        return random.choice(string.ascii_letters)

    letter_to_be_replaced = random.choice(input_string)
    letter_to_replace_with = generate_random_letter()

    new_string = input_string.replace(letter_to_be_replaced, letter_to_replace_with)
    return new_string


def log_transaction(transaction, message):
    transaction_converter = TransactionsConverter()
    transaction_dict = transaction_converter.transaction_to_dictionary(transaction)
    logger.info(f"{message}: {transaction_dict}")


def flag_to_hex(flag_name: str, flag_value: str) -> str:
    flag_name_hex = string_to_hex(flag_name)
    flag_value_hex = string_to_hex(flag_value)
    return f"{flag_name_hex}@{flag_value_hex}"
