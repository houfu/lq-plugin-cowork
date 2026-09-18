#!/usr/bin/env python3
"""Generate branding/color.png (192x192) and branding/outline.png (32x32).

Both icons are derived from the upstream LegalQuants logo
(``upstream/plugins/legalquants-litigation/assets/lq-logo.png``), a black
rounded square carrying a white "LQ".

* ``color.png`` — the logo tile scaled down and centred on a white field.
* ``outline.png`` — the "LQ" letterforms alone, white on transparency.

Pure standard library: PNG decoding, box filtering and PNG encoding are all
done here because Pillow is deliberately not a dependency of this repository.
``sips`` (macOS) is used only when the source PNG is in a form the decoder
here does not read, to normalise it to 8-bit RGBA first.

    uv run --project tools python tools/scripts/make_icons.py
"""

from __future__ import annotations

import argparse
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class IconError(Exception):
    pass


# --------------------------------------------------------------------------
# PNG decoding
# --------------------------------------------------------------------------


def _chunks(data: bytes):
    if not data.startswith(PNG_SIGNATURE):
        raise IconError("not a PNG")
    offset = len(PNG_SIGNATURE)
    while offset < len(data):
        (length,) = struct.unpack(">I", data[offset : offset + 4])
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        yield kind, payload
        offset += 12 + length


def _unfilter(raw: bytes, width: int, height: int, stride: int) -> bytearray:
    out = bytearray(width * height * stride)
    line = width * stride
    pos = 0
    for row in range(height):
        filter_type = raw[pos]
        pos += 1
        scan = bytearray(raw[pos : pos + line])
        pos += line
        base = row * line
        prior = out[base - line : base] if row else bytearray(line)
        if filter_type == 1:
            for i in range(stride, line):
                scan[i] = (scan[i] + scan[i - stride]) & 0xFF
        elif filter_type == 2:
            for i in range(line):
                scan[i] = (scan[i] + prior[i]) & 0xFF
        elif filter_type == 3:
            for i in range(line):
                left = scan[i - stride] if i >= stride else 0
                scan[i] = (scan[i] + ((left + prior[i]) >> 1)) & 0xFF
        elif filter_type == 4:
            for i in range(line):
                left = scan[i - stride] if i >= stride else 0
                up = prior[i]
                up_left = prior[i - stride] if i >= stride else 0
                p = left + up - up_left
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - up_left)
                if pa <= pb and pa <= pc:
                    pred = left
                elif pb <= pc:
                    pred = up
                else:
                    pred = up_left
                scan[i] = (scan[i] + pred) & 0xFF
        elif filter_type != 0:
            raise IconError(f"unsupported PNG filter {filter_type}")
        out[base : base + line] = scan
    return out


def read_rgba(path: Path) -> tuple[int, int, bytearray]:
    """Decode an 8-bit, non-interlaced PNG into a flat RGBA buffer."""
    data = path.read_bytes()
    width = height = depth = color_type = interlace = 0
    idat = bytearray()
    palette: bytes = b""
    trns: bytes = b""
    for kind, payload in _chunks(data):
        if kind == b"IHDR":
            width, height, depth, color_type, _, _, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
        elif kind == b"PLTE":
            palette = payload
        elif kind == b"tRNS":
            trns = payload
        elif kind == b"IDAT":
            idat += payload
        elif kind == b"IEND":
            break
    if depth != 8 or interlace != 0:
        raise IconError("only 8-bit, non-interlaced PNGs are supported")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        raise IconError(f"unsupported PNG colour type {color_type}")
    raw = _unfilter(zlib.decompress(bytes(idat)), width, height, channels)

    rgba = bytearray(width * height * 4)
    for index in range(width * height):
        src = index * channels
        dst = index * 4
        if color_type == 6:
            rgba[dst : dst + 4] = raw[src : src + 4]
        elif color_type == 2:
            rgba[dst : dst + 3] = raw[src : src + 3]
            rgba[dst + 3] = 255
        elif color_type == 0:
            value = raw[src]
            rgba[dst : dst + 4] = bytes((value, value, value, 255))
        elif color_type == 4:
            value = raw[src]
            rgba[dst : dst + 4] = bytes((value, value, value, raw[src + 1]))
        else:  # palette
            entry = raw[src]
            rgba[dst : dst + 3] = palette[entry * 3 : entry * 3 + 3]
            rgba[dst + 3] = trns[entry] if entry < len(trns) else 255
    return width, height, rgba


def normalise(path: Path, work: Path) -> Path:
    """Return a PNG this module can decode, using sips when it cannot."""
    try:
        read_rgba(path)
        return path
    except IconError:
        pass
    sips = shutil.which("sips")
    if not sips:
        raise IconError(f"{path}: cannot decode and sips is unavailable")
    target = work / "normalised.png"
    subprocess.run(
        [sips, "-s", "format", "png", str(path), "--out", str(target)],
        check=True,
        capture_output=True,
    )
    return target


# --------------------------------------------------------------------------
# PNG encoding
# --------------------------------------------------------------------------


def write_png(path: Path, width: int, height: int, pixels: bytes, alpha: bool) -> None:
    channels = 4 if alpha else 3
    stride = width * channels
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        raw += pixels[row * stride : (row + 1) * stride]

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6 if alpha else 2, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        PNG_SIGNATURE
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


# --------------------------------------------------------------------------
# resampling
# --------------------------------------------------------------------------


def box_resize_rgba(
    width: int, height: int, rgba: bytearray, new_w: int, new_h: int
) -> bytearray:
    """Area-average downscale with premultiplied alpha (no dark halos)."""
    out = bytearray(new_w * new_h * 4)
    for y in range(new_h):
        y0, y1 = y * height // new_h, max(
            (y + 1) * height // new_h, y * height // new_h + 1
        )
        for x in range(new_w):
            x0, x1 = (
                x * width // new_w,
                max((x + 1) * width // new_w, x * width // new_w + 1),
            )
            r = g = b = a = 0
            count = 0
            for sy in range(y0, y1):
                base = (sy * width) * 4
                for sx in range(x0, x1):
                    off = base + sx * 4
                    alpha = rgba[off + 3]
                    r += rgba[off] * alpha
                    g += rgba[off + 1] * alpha
                    b += rgba[off + 2] * alpha
                    a += alpha
                    count += 1
            dst = (y * new_w + x) * 4
            mean_a = a // count
            if a:
                out[dst] = min(255, r // a)
                out[dst + 1] = min(255, g // a)
                out[dst + 2] = min(255, b // a)
            out[dst + 3] = mean_a
    return out


def box_resize_mask(
    width: int, height: int, mask: bytearray, new_w: int, new_h: int
) -> bytearray:
    out = bytearray(new_w * new_h)
    for y in range(new_h):
        y0, y1 = (
            y * height // new_h,
            max((y + 1) * height // new_h, y * height // new_h + 1),
        )
        for x in range(new_w):
            x0, x1 = (
                x * width // new_w,
                max((x + 1) * width // new_w, x * width // new_w + 1),
            )
            total = count = 0
            for sy in range(y0, y1):
                base = sy * width
                for sx in range(x0, x1):
                    total += mask[base + sx]
                    count += 1
            out[y * new_w + x] = total // count
    return out


# --------------------------------------------------------------------------
# the two icons
# --------------------------------------------------------------------------


def make_color(
    width: int,
    height: int,
    rgba: bytearray,
    size: int,
    inset: int,
    bg: tuple[int, int, int],
) -> bytes:
    """The logo tile scaled to ``size - 2 * inset`` and centred on ``bg``."""
    inner = size - 2 * inset
    scaled = box_resize_rgba(width, height, rgba, inner, inner)
    canvas = bytearray(bg * (size * size))
    for y in range(inner):
        for x in range(inner):
            src = (y * inner + x) * 4
            alpha = scaled[src + 3]
            dst = ((y + inset) * size + (x + inset)) * 3
            if alpha == 255:
                canvas[dst : dst + 3] = scaled[src : src + 3]
            elif alpha:
                for channel in range(3):
                    fore = scaled[src + channel]
                    back = canvas[dst + channel]
                    canvas[dst + channel] = (fore * alpha + back * (255 - alpha)) // 255
    return bytes(canvas)


def glyph_mask(width: int, height: int, rgba: bytearray) -> bytearray:
    """Coverage of the light letterforms inside the opaque tile."""
    mask = bytearray(width * height)
    for index in range(width * height):
        off = index * 4
        alpha = rgba[off + 3]
        if not alpha:
            continue
        luma = (rgba[off] * 299 + rgba[off + 1] * 587 + rgba[off + 2] * 114) // 1000
        mask[index] = luma * alpha // 255
    return mask


def crop_mask(
    width: int, height: int, mask: bytearray, threshold: int = 96
) -> tuple[int, int, bytearray]:
    min_x, min_y, max_x, max_y = width, height, -1, -1
    for y in range(height):
        row = y * width
        for x in range(width):
            if mask[row + x] >= threshold:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
    if max_x < 0:
        raise IconError("no letterforms found in the source logo")
    new_w = max_x - min_x + 1
    new_h = max_y - min_y + 1
    out = bytearray(new_w * new_h)
    for y in range(new_h):
        src = (y + min_y) * width + min_x
        out[y * new_w : (y + 1) * new_w] = mask[src : src + new_w]
    return new_w, new_h, out


def make_outline(
    width: int, height: int, rgba: bytearray, size: int, margin: int
) -> bytes:
    """White letterforms on transparency, fitted inside ``size``."""
    mask = glyph_mask(width, height, rgba)
    crop_w, crop_h, cropped = crop_mask(width, height, mask)
    box = size - 2 * margin
    if crop_w >= crop_h:
        new_w, new_h = box, max(1, round(box * crop_h / crop_w))
    else:
        new_h, new_w = box, max(1, round(box * crop_w / crop_h))
    small = box_resize_mask(crop_w, crop_h, cropped, new_w, new_h)
    canvas = bytearray(size * size * 4)
    off_x = (size - new_w) // 2
    off_y = (size - new_h) // 2
    for y in range(new_h):
        for x in range(new_w):
            alpha = small[y * new_w + x]
            if not alpha:
                continue
            dst = ((y + off_y) * size + (x + off_x)) * 4
            canvas[dst : dst + 4] = bytes((255, 255, 255, alpha))
    return bytes(canvas)


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        default=str(
            root / "upstream/plugins/legalquants-litigation/assets/lq-logo.png"
        ),
    )
    parser.add_argument("--color-out", default=str(root / "branding/color.png"))
    parser.add_argument("--outline-out", default=str(root / "branding/outline.png"))
    parser.add_argument(
        "--background",
        default="#FFFFFF",
        help="padding colour behind the colour icon",
    )
    parser.add_argument("--inset", type=int, default=18)
    parser.add_argument("--margin", type=int, default=3)
    args = parser.parse_args(argv)

    bg_hex = args.background.lstrip("#")
    bg = tuple(int(bg_hex[i : i + 2], 16) for i in (0, 2, 4))

    with tempfile.TemporaryDirectory(prefix="lq-icons-") as tmp:
        source = normalise(Path(args.source), Path(tmp))
        width, height, rgba = read_rgba(source)

    color = make_color(width, height, rgba, 192, args.inset, bg)
    write_png(Path(args.color_out), 192, 192, color, alpha=False)

    outline = make_outline(width, height, rgba, 32, args.margin)
    write_png(Path(args.outline_out), 32, 32, outline, alpha=True)

    for path in (Path(args.color_out), Path(args.outline_out)):
        size = struct.unpack(">II", path.read_bytes()[16:24])
        print(f"{path}: {size[0]}x{size[1]}, {path.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except IconError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
