"""Structural checks for the generated DOL and modded GameCube ISO."""

from __future__ import annotations

import os
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOL_PATH = ROOT / "build" / "GALE01" / "main.dol"
DEFAULT_ISO_PATH = ROOT / "build" / "GALE01" / "melee-mystery-roster.iso"


def read_u32be(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def dol_sections(data: bytes) -> list[tuple[str, int, int, int]]:
    if len(data) < 0x100:
        raise ValueError("DOL is smaller than its 0x100-byte header")

    sections = []
    groups = (
        ("text", 7, 0x00, 0x48, 0x90),
        ("data", 11, 0x1C, 0x64, 0xAC),
    )
    for kind, count, offsets_base, addresses_base, sizes_base in groups:
        for index in range(count):
            file_offset = read_u32be(data, offsets_base + index * 4)
            address = read_u32be(data, addresses_base + index * 4)
            size = read_u32be(data, sizes_base + index * 4)
            if size:
                sections.append((f"{kind}{index}", file_offset, address, size))
    return sections


def fst_files(iso, fst_offset: int, fst_size: int) -> list[tuple[int, int]]:
    iso.seek(fst_offset)
    fst = iso.read(fst_size)
    if len(fst) != fst_size or fst_size < 12:
        raise ValueError("ISO contains a truncated FST")

    entry_count = read_u32be(fst, 8)
    if entry_count == 0 or entry_count * 12 > len(fst):
        raise ValueError("ISO contains an invalid FST entry count")

    files = []
    for index in range(1, entry_count):
        offset = index * 12
        type_and_name = read_u32be(fst, offset)
        if type_and_name >> 24 == 0:
            files.append(
                (read_u32be(fst, offset + 4), read_u32be(fst, offset + 8))
            )
    return files


class DolLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not DOL_PATH.is_file():
            raise FileNotFoundError(f"build artifact not found: {DOL_PATH}")
        cls.data = DOL_PATH.read_bytes()
        cls.sections = dol_sections(cls.data)

    def test_entry_point_is_in_gamecube_memory(self) -> None:
        entry_point = read_u32be(self.data, 0xE0)
        self.assertGreaterEqual(entry_point, 0x80000000)
        self.assertLess(entry_point, 0x81800000)

    def test_file_sections_are_valid_and_non_overlapping(self) -> None:
        ranges = []
        for name, file_offset, address, size in self.sections:
            with self.subTest(section=name):
                self.assertGreaterEqual(file_offset, 0x100)
                self.assertLessEqual(file_offset + size, len(self.data))
                self.assertGreaterEqual(address, 0x80000000)
                self.assertLessEqual(address + size, 0x81800000)
            ranges.append((file_offset, file_offset + size, name))

        ranges.sort()
        for previous, current in zip(ranges, ranges[1:]):
            self.assertLessEqual(
                previous[1],
                current[0],
                f"DOL sections overlap: {previous[2]} and {current[2]}",
            )


class IsoPackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.iso_path = Path(os.environ.get("MELEE_TEST_ISO", DEFAULT_ISO_PATH))
        if not DOL_PATH.is_file() or not cls.iso_path.is_file():
            raise FileNotFoundError(
                f"DOL or ISO artifact missing: {DOL_PATH}, {cls.iso_path}"
            )
        cls.dol = DOL_PATH.read_bytes()

    def test_iso_identity_and_magic(self) -> None:
        with self.iso_path.open("rb") as iso:
            header = iso.read(0x430)
        self.assertEqual(header[:6], b"GALE01")
        self.assertEqual(read_u32be(header, 0x1C), 0xC2339F3D)

    def test_iso_contains_the_current_dol_exactly(self) -> None:
        with self.iso_path.open("rb") as iso:
            iso.seek(0x420)
            dol_offset = int.from_bytes(iso.read(4), "big")
            iso.seek(dol_offset)
            embedded = iso.read(len(self.dol))
        self.assertEqual(embedded, self.dol)

    def test_dol_does_not_overlap_disc_files(self) -> None:
        with self.iso_path.open("rb") as iso:
            iso.seek(0x420)
            dol_offset = int.from_bytes(iso.read(4), "big")
            fst_offset = int.from_bytes(iso.read(4), "big")
            fst_size = int.from_bytes(iso.read(4), "big")
            files = fst_files(iso, fst_offset, fst_size)

        dol_end = dol_offset + len(self.dol)
        collisions = [
            (offset, size)
            for offset, size in files
            if dol_offset < offset + size and offset < dol_end
        ]
        self.assertEqual(collisions, [])


if __name__ == "__main__":
    unittest.main()
