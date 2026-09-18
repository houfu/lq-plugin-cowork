"""The PNG IHDR reader, and the two committed branding icons."""

from __future__ import annotations

from pathlib import Path

import pytest

from lqcowork.icons import PngError, png_size


def test_reads_the_committed_icons(real_root: Path):
    assert png_size(real_root / "branding/color.png") == (192, 192)
    assert png_size(real_root / "branding/outline.png") == (32, 32)


def test_reads_a_generated_png(tmp_path: Path):
    from conftest import write_png

    target = tmp_path / "x.png"
    write_png(target, 7, 11, (1, 2, 3))
    assert png_size(target) == (7, 11)


def test_rejects_a_non_png(tmp_path: Path):
    target = tmp_path / "x.png"
    target.write_bytes(b"not a png at all, really quite long though")
    with pytest.raises(PngError, match="bad signature"):
        png_size(target)


def test_rejects_a_truncated_png(tmp_path: Path):
    target = tmp_path / "x.png"
    target.write_bytes(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(PngError):
        png_size(target)


def test_rejects_a_missing_file(tmp_path: Path):
    with pytest.raises(PngError):
        png_size(tmp_path / "absent.png")
