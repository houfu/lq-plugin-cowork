"""Minimal PNG header reader (no Pillow anywhere in this repository)."""

from __future__ import annotations

import struct
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PngError(Exception):
    """The file is not a readable PNG."""


def png_size(path: Path) -> tuple[int, int]:
    """Return ``(width, height)`` by reading the PNG signature and IHDR."""
    try:
        header = path.read_bytes()[:33]
    except OSError as exc:
        raise PngError(f"{path}: cannot be read ({exc})") from exc
    if len(header) < 24 or not header.startswith(PNG_SIGNATURE):
        raise PngError(f"{path}: not a PNG (bad signature)")
    length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or length != 13:
        raise PngError(f"{path}: first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", header[16:24])
    if width == 0 or height == 0:
        raise PngError(f"{path}: zero-sized image")
    return width, height
