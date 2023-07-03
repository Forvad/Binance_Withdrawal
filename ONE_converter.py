import re
from typing import Tuple, Any

from eth_utils import *
from Crypto.Hash import keccak

HRP = "one"

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"



def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk


def bech32_hrp_expand(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def bech32_verify_checksum(hrp, data):
    """Verify a checksum given HRP and converted data characters."""
    return bech32_polymod(bech32_hrp_expand(hrp) + data) == 1


def bech32_create_checksum(hrp, data):
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def bech32_encode(hrp, data):
    """Compute a Bech32 string given HRP and data values."""
    combined = data + bech32_create_checksum(hrp, data)
    return hrp + "1" + "".join([CHARSET[d] for d in combined])


def bech32_decode(bech):
    """Validate a Bech32 string, and determine HRP and data."""
    if (any(ord(x) < 33 or ord(x) > 126 for x in bech)) or (
        bech.lower() != bech and bech.upper() != bech
    ):
        return (None, None)
    bech = bech.lower()
    pos = bech.rfind("1")
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return (None, None)
    if not all(x in CHARSET for x in bech[pos + 1 :]):
        return (None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos + 1 :]]
    if not bech32_verify_checksum(hrp, data):
        return (None, None)
    return (hrp, data[:-6])


def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def decode(hrp, addr):
    """Decode a segwit address."""
    hrpgot, data = bech32_decode(addr)
    if hrpgot != hrp:
        return (None, None)
    decoded = convertbits(data[1:], 5, 8, False)
    if decoded is None or len(decoded) < 2 or len(decoded) > 40:
        return (None, None)
    if data[0] > 16:
        return (None, None)
    if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
        return (None, None)
    return (data[0], decoded)


def encode(hrp, witver, witprog):
    """Encode a segwit address."""
    ret = bech32_encode(hrp, [witver] + convertbits(witprog, 8, 5))
    if decode(hrp, ret) == (None, None):
        return None
    return ret


def is_eth_checksum_address(address: str) -> bool:
    """Takes an Ethereum based address and checks that the checksum is valid

    Args:
        address (str): Eth Address

    Returns:
        bool: Result if valid or not.
    """
    address = address.replace("0x", "")
    address_hash = keccak.new(digest_bits=256)
    address_hash = address_hash.update(address.lower().encode("utf-8")).hexdigest()

    for i in range(0, 40):
        # The nth letter should be uppercase if the nth digit of casemap is 1
        if (int(address_hash[i], 16) > 7 and address[i].upper() != address[i]) or (
            int(address_hash[i], 16) <= 7 and address[i].lower() != address[i]
        ):
            return False
    return True


def is_eth_address(address: str) -> bool:
    """Takes an Ethereum based address and checks that it is valid

    Args:
        address (str): Eth Address

    Returns:
        bool: Result if valid or not.
    """
    if not re.match(r"^(0x)?[0-9a-f]{40}$", address, flags=re.IGNORECASE):
        # Check if it has the basic requirements of an address
        return False
    elif re.match(r"^(0x)?[0-9a-f]{40}$", address) or re.match(
        r"^(0x)?[0-9A-F]{40}$", address
    ):
        # If it's all small caps or all all caps, return true
        return True
    else:
        # Otherwise check each case
        return is_eth_checksum_address(address)


def convert_eth_to_one(address: str, useHRP: str = HRP) -> str:
    """
            Encodes a canonical 20-byte Ethereum-style address as a bech32 Harmony
            address.

            The expected format is one1<address><checksum> where address and checksum
            are the result of bech32 encoding a Buffer containing the address bytes.

    Args:
            address (str): 20 byte canonical address
            useHRP (str, optional):  38 char bech32 bech32Encoded Harmony address. Defaults to HRP.

    Returns:
            str: Converted ONE address or Error String.
    """

    if not is_eth_address(address):
        return "ERROR: Invalid address format."

    address_remove_0x = bytearray.fromhex(address.replace("0x", ""))
    addrBz = convertbits(address_remove_0x, 8, 5)

    if not addrBz:
        return "ERROR: Could not convert byte Buffer to 5-bit Buffer"

    return bech32_encode(useHRP, addrBz)


async def is_valid_address(address: str) -> bool:
    """
    Check if given string is valid one address
    NOTE: This function is NOT thread safe due to the C function used by the bech32 library.
    Parameters
    ----------
    address: str
        String to check if valid one address
    Returns
    -------
    bool
        Is valid address
    """
    if not address.startswith("one1"):
        return False
    hrp, _ = bech32_decode(address)
    if not hrp:
        return False
    return True


def convert_one_to_eth(addr: str) -> tuple[str, to_checksum_address] | tuple[str, str]:
    """
    Given a one address, convert it to hex checksum address
    """
    try:
        if not is_valid_address(addr):
            return "error", to_checksum_address(addr)
        hrp, data = bech32_decode(addr)
        buf = convertbits(data, 5, 8, False)
        address = "0x" + "".join("{:02x}".format(x) for x in buf)
        return "success", to_checksum_address(address)
    except ValueError as e:
        return "error", str(e)

if __name__ == '__main__':
    print(convert_eth_to_one('0xDbde3A019589F121eBFd68cFCBa6f70becD76CC5'))