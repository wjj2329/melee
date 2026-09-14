#!/usr/bin/env python3
"""Inspect or unlock the roster in a North American Melee GCI save.

Melee stores its logical files in checksummed, obfuscated 0x2000-byte blocks.
This tool edits both redundant copies of logical file 1 (the 0x1790-byte
global save-data file) and leaves every other byte of decoded payload intact.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SECTOR_SIZE = 0x2000
GCI_HEADER_SIZE = 0x40
CHECKSUM_SEED = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
ENCODE_LUT = (0x26, 0xFF, 0xE8, 0xEF, 0x42, 0xD6, 0x01,
              0x54, 0x14, 0xA3, 0x80, 0xFD, 0x6E)


def _permute(value: int, shifts: tuple[int, ...]) -> int:
    result = 0
    for bit, shift in enumerate(shifts):
        masked = value & (1 << bit)
        result |= masked << shift if shift >= 0 else masked >> -shift
    return result & 0xFF


DECODE_SHIFTS = (
    (0, 1, 2, 3, -3, -2, -1, 0),
    (1, 6, 0, -3, 1, -1, -3, -1),
    (2, 2, 4, 1, 3, -4, -6, -2),
    (4, -1, 3, -2, -1, 1, 1, -5),
    (3, 4, -1, 4, 2, -3, -2, -7),
    (5, 5, 5, 0, -2, -5, -5, -3),
    (6, 0, -2, 2, 0, 2, -4, -4),
)


def deobfuscate_byte(previous_cipher: int, cipher: int) -> int:
    value = _permute(cipher, DECODE_SHIFTS[previous_cipher % 7])
    return value ^ ENCODE_LUT[previous_cipher % 13] ^ previous_cipher


def checksum(data: bytes | bytearray) -> bytes:
    result = bytearray(CHECKSUM_SEED)
    for index, value in enumerate(data):
        result[index % 16] = (result[index % 16] + value) & 0xFF
    for index in range(1, 16):
        if result[index - 1] == result[index]:
            result[index] ^= 0xFF
    return bytes(result)


def decode_block(ciphertext: bytes) -> bytearray:
    if len(ciphertext) != SECTOR_SIZE:
        raise ValueError("encoded block is not 0x2000 bytes")
    decoded = bytearray(ciphertext)
    previous = ciphertext[15]
    for index in range(16, len(decoded)):
        current = ciphertext[index]
        decoded[index] = deobfuscate_byte(previous, current)
        previous = current
    if decoded[:16] != checksum(decoded[16:]):
        raise ValueError("block checksum mismatch")
    return decoded


def encode_block(decoded: bytes | bytearray) -> bytes:
    if len(decoded) != SECTOR_SIZE:
        raise ValueError("decoded block is not 0x2000 bytes")
    encoded = bytearray(decoded)
    encoded[:16] = checksum(encoded[16:])
    inverse = [[-1] * 256 for _ in range(256)]
    for previous in range(256):
        for cipher in range(256):
            inverse[previous][deobfuscate_byte(previous, cipher)] = cipher
    previous = encoded[15]
    for index in range(16, len(encoded)):
        encoded[index] = inverse[previous][encoded[index]]
        previous = encoded[index]
    return bytes(encoded)


def find_global_save_blocks(gci: bytes) -> list[tuple[int, bytearray]]:
    if gci[:6] != b"GALE01":
        raise ValueError("not a North American Melee (GALE01) GCI save")
    if (len(gci) - GCI_HEADER_SIZE) % SECTOR_SIZE:
        raise ValueError("GCI payload is not sector-aligned")

    matches = []
    sector_count = (len(gci) - GCI_HEADER_SIZE) // SECTOR_SIZE
    for sector in range(1, sector_count):
        offset = GCI_HEADER_SIZE + sector * SECTOR_SIZE
        try:
            decoded = decode_block(gci[offset:offset + SECTOR_SIZE])
        except ValueError:
            continue
        file_id = int.from_bytes(decoded[0x10:0x12], "big")
        # Logical file 1 is the 0x1790-byte gmMainLib_GetSaveData payload.
        if file_id == 1:
            matches.append((offset, decoded))
    return matches


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()

    original = args.input.read_bytes()
    blocks = find_global_save_blocks(original)
    print(f"global save blocks: {len(blocks)}")
    for offset, decoded in blocks:
        mask = int.from_bytes(decoded[0x20:0x22], "big")
        print(f"  file offset 0x{offset:X}, sequence {decoded[0x12]}, "
              f"roster mask 0x{mask:04X}")

    if args.inspect:
        return
    if args.output is None:
        parser.error("--output is required unless --inspect is used")
    if len(blocks) != 2:
        raise ValueError(f"expected two redundant global-save blocks, found {len(blocks)}")

    modified = bytearray(original)
    for offset, decoded in blocks:
        # All eleven unlockable-character bits. Higher bits remain untouched.
        old_mask = int.from_bytes(decoded[0x20:0x22], "big")
        decoded[0x20:0x22] = (old_mask | 0x07FF).to_bytes(2, "big")
        encoded = encode_block(decoded)
        # The stored checksum at [0:16] must change with the payload, so compare
        # the decoded header and payload rather than the stale incoming checksum.
        if decode_block(encoded)[16:] != decoded[16:]:
            raise AssertionError("encode/decode round-trip verification failed")
        modified[offset:offset + SECTOR_SIZE] = encoded

    if args.backup:
        args.backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.input, args.backup)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(modified)

    verify = args.output.read_bytes()
    verified_blocks = find_global_save_blocks(verify)
    if len(verified_blocks) != 2:
        raise AssertionError("written save failed block verification")
    for _, decoded in verified_blocks:
        if int.from_bytes(decoded[0x20:0x22], "big") & 0x07FF != 0x07FF:
            raise AssertionError("written save does not contain the full roster mask")
    print(f"wrote verified unlocked save: {args.output}")


if __name__ == "__main__":
    main()
