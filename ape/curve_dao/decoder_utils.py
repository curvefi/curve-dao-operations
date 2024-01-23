from typing import Any, Dict, List, Optional, Tuple, Union

import ape
from ape.exceptions import DecodingError
from ape.utils.abi import Struct
from eth_abi.exceptions import InsufficientDataBytes
from eth_hash.auto import keccak
from eth_utils import humanize_hash, is_hex_address, to_checksum_address
from ethpm_types import HexBytes
from ethpm_types.abi import MethodABI

try:
    from eth_abi import decode_abi
except ImportError:
    from eth_abi import decode as decode_abi


def get_type_strings(abi_params: List, substitutions: Optional[Dict] = None) -> List:
    types_list = []
    if substitutions is None:
        substitutions = {}

    for i in abi_params:
        if i.type.startswith("tuple"):
            params = get_type_strings(i.components, substitutions)
            array_size = i.type[5:]
            types_list.append(f"({','.join(params)}){array_size}")
        else:
            type_str = i.type
            for orig, sub in substitutions.items():
                if type_str.startswith(orig):
                    type_str = type_str.replace(orig, sub)
            types_list.append(type_str)

    return types_list


def build_function_signature(abi: Dict) -> str:
    types_list = get_type_strings(abi.inputs)
    return f"{abi.name}({','.join(types_list)})"


def build_function_selector(abi: Dict) -> str:
    sig = build_function_signature(abi)
    return "0x" + keccak(sig.encode()).hex()[:8]


def decode_address(raw_address):
    if isinstance(raw_address, int):
        raw_address = HexBytes(raw_address)

    return to_checksum_address(raw_address)


def decode_value(value):
    if isinstance(value, HexBytes):
        try:
            string_value = value.strip(b"\x00").decode("utf8")
            return f"'{string_value}'"
        except UnicodeDecodeError:
            # Truncate bytes if very long.
            if len(value) > 24:
                return humanize_hash(value)

            hex_str = HexBytes(value).hex()
            if is_hex_address(hex_str):
                return decode_value(hex_str)

            return hex_str

    elif isinstance(value, str) and is_hex_address(value):
        return decode_address(value)

    elif value and isinstance(value, str):
        # Surround non-address strings with quotes.
        return f'"{value}"'

    elif isinstance(value, (list, tuple)):
        decoded_values = [decode_value(v) for v in value]
        return decoded_values

    elif isinstance(value, Struct):
        decoded_values = {k: decode_value(v) for k, v in value.items()}
        return decoded_values

    return value


def decode_calldata(
    method: MethodABI,
    raw_data: bytes,
) -> List:
    input_types = [i.canonical_type for i in method.inputs]  # type: ignore

    try:

        raw_input_values = decode_abi(input_types, raw_data)
        input_values = [decode_value(v) for v in raw_input_values]

    except (DecodingError, InsufficientDataBytes):

        input_values = ["<?>" for _ in input_types]

    return input_values


def decode_input(
    contract: ape.Contract, calldata: Union[str, bytes]
) -> Tuple[str, Any]:

    if not isinstance(calldata, HexBytes):
        calldata = HexBytes(calldata)

    fn_selector = calldata[:4].hex()  # type: ignore
    abi = next(
        (
            i
            for i in contract.contract_type.abi
            if i.type == "function" and build_function_selector(i) == fn_selector
        ),
        None,
    )

    if abi is None:
        raise ValueError("Four byte selector does not match the ABI for this contract")

    return abi, decode_calldata(abi, calldata[4:])
