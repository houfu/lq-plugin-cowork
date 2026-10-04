"""Synthetic fixtures for the harness probes.

Every file a probe asks the agent to read or change is generated here, with
the standard library only: PNG, PDF, DOCX, XLSX, EML, plain text, a folder
tree and an HTML round-trip page. Each live run draws fresh random tokens, so
an answer cannot be remembered or guessed; the static set in
``assets/fixtures/static.zip`` uses a fixed seed for harnesses that cannot run
scripts at all.

The answer key never stores an answer in clear: it stores a salted SHA-256
of the normalised answer, which ``hprobe_checks`` compares against.
"""

from __future__ import annotations

import hashlib
import json
import random
import struct
import zipfile
import zlib
from pathlib import Path
from typing import Dict, List, Sequence, Tuple
from xml.sax.saxutils import escape

SAFE = "ACDEFHJKLMNPRTUVWXY3479"
WORDS = (
    "alder amber anchor arbour aspen basalt beacon birch bramble cedar "
    "cinder clover copper cove delta ember fennel fern fjord flint gable "
    "garnet harbour hazel heron indigo iris juniper kestrel lantern larch "
    "linden maple marble meadow mesa moss nettle oak onyx orchard osprey "
    "pebble pine quarry quill raven reed ridge rowan saffron sage slate "
    "sorrel spruce thistle timber umber vale walnut willow wren yarrow"
).split()

ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def token(rng: random.Random, prefix: str = "", length: int = 6) -> str:
    body = "".join(rng.choice(SAFE) for _ in range(length))
    return f"{prefix}-{body}" if prefix else body


def normalise(text: str) -> str:
    """Case, whitespace and quote-insensitive form used for every comparison."""
    text = (text or "").replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    return " ".join(text.strip().strip('"').split()).lower()


def keyed(salt: str, answer: str) -> str:
    return hashlib.sha256((salt + "\0" + normalise(answer)).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# PNG with a 5x7 bitmap font

FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "C": "01111 10000 10000 10000 10000 10000 01111",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    "-": "00000 00000 00000 11111 00000 00000 00000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "G": "01111 10000 10000 10111 10001 10001 01111",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10011 10101 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "8": "01110 10001 10001 01110 10001 10001 01110",
}


class Canvas:
    def __init__(self, width: int, height: int, colour=(255, 255, 255)):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(colour) * (width * height))

    def dot(self, x: int, y: int, colour=(20, 20, 20)) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i : i + 3] = bytes(colour)

    def rect(self, x: int, y: int, w: int, h: int, colour=(20, 20, 20)) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.dot(xx, yy, colour)

    def text(self, x: int, y: int, text: str, scale: int, colour=(20, 20, 20)) -> None:
        for index, char in enumerate(text.upper()):
            rows = FONT.get(char, FONT[" "]).split()
            for row, bits in enumerate(rows):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.rect(
                            x + (index * 6 + col) * scale,
                            y + row * scale,
                            scale,
                            scale,
                            colour,
                        )

    def scribble(
        self, cx: int, cy: int, rng: random.Random, colour=(30, 60, 160)
    ) -> None:
        """A signature-like stroke about 140 by 50 pixels around (cx, cy)."""
        import math

        phase = rng.random() * math.pi
        for x in range(-70, 71):
            y = (
                18 * math.sin(x / 9.0 + phase)
                + 6 * math.sin(x / 3.0)
                + rng.uniform(-1, 1)
            )
            self.rect(cx + x, cy + int(y), 4, 4, colour)
        for x in range(-50, 40):
            self.rect(cx + x, cy + 26, 3, 3, colour)

    def png(self) -> bytes:
        raw = b"".join(
            b"\x00" + bytes(self.pixels[y * self.width * 3 : (y + 1) * self.width * 3])
            for y in range(self.height)
        )

        def chunk(kind: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data))
                + kind
                + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )

        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b"")
        )


def vision_page(rng: random.Random) -> Tuple[bytes, str, str]:
    code = token(rng, length=5)
    canvas = Canvas(900, 600)
    canvas.rect(0, 0, 900, 4, (200, 200, 200))
    canvas.text(150, 250, code, 18)
    corner = rng.choice(("top-left", "top-right", "bottom-left", "bottom-right"))
    cx = 110 if "left" in corner else 790
    cy = 80 if corner.startswith("top") else 520
    canvas.scribble(cx, cy, rng)
    return canvas.png(), code, corner


def badge_png() -> bytes:
    canvas = Canvas(240, 80, (45, 45, 45))
    canvas.text(18, 26, "LQ PROBE", 4, (250, 250, 250))
    return canvas.png()


# --------------------------------------------------------------------------
# PDF


def _pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf_bytes(pages: Sequence[Sequence[str]]) -> bytes:
    """A plain PDF, one Helvetica text block per page, uncompressed."""
    objects: List[bytes] = []
    page_ids = []
    font_id = 3
    next_id = 4
    contents = []
    for lines in pages:
        ops = ["BT", "/F1 12 Tf", "14 TL", "72 760 Td"]
        for line in lines:
            ops.append(f"({_pdf_text(line)}) Tj T*")
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1", "replace")
        contents.append((next_id, stream))
        page_ids.append(next_id + 1)
        next_id += 2
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode())
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for (cid, stream), pid in zip(contents, page_ids):
        objects.append(
            f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream"
        )
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {cid} 0 R >>"
            ).encode()
        )
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{number} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(out)


# --------------------------------------------------------------------------
# OOXML packages

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _zip(path: Path, parts: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            info = zipfile.ZipInfo(name, date_time=ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data.encode("utf-8"))


def _docx_parts(body: str, comments: str = "", styles: str = "") -> Dict[str, str]:
    overrides = [
        '<Override PartName="/word/document.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    ]
    rels = []
    if comments:
        overrides.append(
            '<Override PartName="/word/comments.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>'
        )
        rels.append(
            '<Relationship Id="rIdC" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/comments" Target="comments.xml"/>'
        )
    if styles:
        overrides.append(
            '<Override PartName="/word/styles.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        )
        rels.append(
            '<Relationship Id="rIdS" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        )
    parts = {
        "[Content_Types].xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/'
            'vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            + "".join(overrides)
            + "</Types>"
        ),
        "_rels/.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            "</Relationships>"
        ),
        "word/_rels/document.xml.rels": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + "".join(rels)
            + "</Relationships>"
        ),
        "word/document.xml": (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:document xmlns:w="{W_NS}"><w:body>{body}'
            '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/></w:sectPr></w:body></w:document>'
        ),
    }
    if comments:
        parts["word/comments.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:comments xmlns:w="{W_NS}">{comments}</w:comments>'
        )
    if styles:
        parts["word/styles.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:styles xmlns:w="{W_NS}">{styles}</w:styles>'
        )
    return parts


def _para(text: str) -> str:
    return f'<w:p><w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>'


def tracked_docx(path: Path, rng: random.Random) -> Dict[str, str]:
    inserted = " ".join(rng.sample(WORDS, 3))
    deleted = " ".join(rng.sample(WORDS, 3))
    comment = "Check " + token(rng, "NOTE", 5)
    ins_author, del_author = rng.sample(
        ["Avery Stone", "Blair Kim", "Casey Moreau", "Devon Achebe", "Emery Hale"], 2
    )
    date = "2026-03-03T10:00:00Z"
    body = (
        _para("SUPPLY AGREEMENT")
        + '<w:p><w:r><w:t xml:space="preserve">The Supplier shall deliver the </w:t></w:r>'
        f'<w:ins w:id="1" w:author="{escape(ins_author)}" w:date="{date}">'
        f'<w:r><w:t xml:space="preserve">{escape(inserted)} </w:t></w:r></w:ins>'
        '<w:r><w:t xml:space="preserve">goods on the Delivery Date</w:t></w:r>'
        f'<w:del w:id="2" w:author="{escape(del_author)}" w:date="{date}">'
        f'<w:r><w:delText xml:space="preserve"> {escape(deleted)}</w:delText></w:r></w:del>'
        "<w:r><w:t>.</w:t></w:r></w:p>"
        '<w:p><w:commentRangeStart w:id="0"/>'
        '<w:r><w:t xml:space="preserve">Payment is due within thirty days.</w:t></w:r>'
        '<w:commentRangeEnd w:id="0"/>'
        '<w:r><w:commentReference w:id="0"/></w:r></w:p>'
    )
    comments = (
        f'<w:comment w:id="0" w:author="{escape(ins_author)}" w:date="{date}">'
        f"{_para(comment)}</w:comment>"
    )
    _zip(path, _docx_parts(body, comments))
    return {
        "ins": inserted,
        "ins_author": ins_author,
        "del": deleted,
        "del_author": del_author,
        "comment": comment,
    }


def clean_docx(path: Path) -> None:
    body = _para("SUPPLY AGREEMENT") + _para(
        "The Supplier shall deliver the goods on the Delivery Date."
    )
    _zip(path, _docx_parts(body))


CLAUSE = (
    "The Buyer shall give notice of any defect within thirty (30) days "
    "and the Seller shall promptly remedy it."
)
CLAUSE_EDITS = [
    ("replace", "thirty (30)", "sixty (60)"),
    ("delete", "promptly ", ""),
    ("insert-after", "notice", " in writing"),
]


def clause_docx(path: Path) -> None:
    _zip(path, _docx_parts(_para("CLAUSE 7 - DEFECTS") + _para(CLAUSE)))


TEMPLATE_ROWS = [
    ("Item", "Party", "Status"),
    ("Disclosure letter", "Seller", "Draft"),
    ("Board minutes", "Buyer", "Pending"),
    ("Escrow letter", "Agent", "Draft"),
]


def template_docx(path: Path) -> None:
    rows = []
    for index, cells in enumerate(TEMPLATE_ROWS):
        props = "<w:trPr><w:tblHeader/></w:trPr>" if index == 0 else ""
        tcs = "".join(
            f'<w:tc><w:tcPr><w:tcW w:w="3000" w:type="dxa"/></w:tcPr>{_para(c)}</w:tc>'
            for c in cells
        )
        rows.append(f"<w:tr>{props}{tcs}</w:tr>")
    table = (
        '<w:tbl><w:tblPr><w:tblStyle w:val="LQProbeGrid"/><w:tblW w:w="9000" '
        'w:type="dxa"/></w:tblPr><w:tblGrid><w:gridCol w:w="3000"/><w:gridCol '
        'w:w="3000"/><w:gridCol w:w="3000"/></w:tblGrid>' + "".join(rows) + "</w:tbl>"
    )
    styles = (
        '<w:style w:type="table" w:styleId="LQProbeGrid"><w:name w:val="LQ Probe Grid"/>'
        '<w:tblPr><w:tblBorders><w:top w:val="single" w:sz="8"/><w:bottom w:val="single" '
        'w:sz="8"/><w:insideH w:val="single" w:sz="4"/></w:tblBorders></w:tblPr></w:style>'
    )
    body = (
        _para("CLOSING CHECKLIST - PROBE TEMPLATE") + table + _para("End of template.")
    )
    _zip(path, _docx_parts(body, styles=styles))


def memo_docx(path: Path, code: str, rng: random.Random) -> None:
    paras = [_para("MEMORANDUM")]
    for _ in range(40):
        paras.append(
            _para(" ".join(rng.choice(WORDS) for _ in range(40)).capitalize() + ".")
        )
    paras.append(_para(f"CODE: {code}"))
    _zip(path, _docx_parts("".join(paras)))


def _xlsx(path: Path, rows: Sequence[Sequence[object]]) -> None:
    """A one-sheet workbook; strings inline, ``=`` strings become formulas."""

    def col(index: int) -> str:
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[index]

    xml_rows = []
    for r, values in enumerate(rows, start=1):
        cells = []
        for c, value in enumerate(values):
            ref = f"{col(c)}{r}"
            if isinstance(value, str) and value.startswith("="):
                cells.append(f'<c r="{ref}"><f>{escape(value[1:])}</f></c>')
            elif isinstance(value, (int, float)):
                cells.append(f'<c r="{ref}"><v>{value}</v></c>')
            elif value is not None and value != "":
                cells.append(
                    f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
                )
        xml_rows.append(f'<row r="{r}">{"".join(cells)}</row>')
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    _zip(
        path,
        {
            "[Content_Types].xml": (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/'
                'vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/xl/workbook.xml" ContentType="application/'
                'vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/'
                'vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                "</Types>"
            ),
            "_rels/.rels": (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                "</Relationships>"
            ),
            "xl/workbook.xml": (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>'
                '<sheet name="Tracker" sheetId="1" r:id="rId1"/></sheets></workbook>'
            ),
            "xl/_rels/workbook.xml.rels": (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
                'officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                "</Relationships>"
            ),
            "xl/worksheets/sheet1.xml": (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                f'<worksheet xmlns="{ns}"><sheetData>{"".join(xml_rows)}</sheetData></worksheet>'
            ),
        },
    )


TRACKER_HEADER = ("Document", "Issue", "Status", "Quote", "Locator")


def tracker_rows(
    rng: random.Random,
) -> Tuple[List[Tuple[str, ...]], List[Tuple[str, ...]]]:
    original = []
    for n in range(1, 7):
        original.append(
            (
                f"DOC-{n:02d} {rng.choice(WORDS).title()} agreement",
                rng.choice(
                    ("Change of control", "Assignment", "Exclusivity", "Termination")
                ),
                rng.choice(("Open", "Reviewed", "Flagged")),
                f"clause {rng.randint(2, 30)}.{rng.randint(1, 9)}",
                f"p. {rng.randint(1, 40)}",
            )
        )
    new = []
    for n in range(7, 11):
        new.append(
            (
                f"DOC-{n:02d} {rng.choice(WORDS).title()} letter",
                rng.choice(
                    ("Change of control", "Assignment", "Exclusivity", "Termination")
                ),
                "Reviewed",
                f"clause {rng.randint(2, 30)}.{rng.randint(1, 9)}",
                f"p. {rng.randint(1, 40)}",
            )
        )
    return original, new


def tracker_xlsx(path: Path, original: Sequence[Sequence[str]]) -> None:
    rows: List[Sequence[object]] = [TRACKER_HEADER]
    rows.extend(original)
    rows.append(("Filled rows", "=COUNTA(A2:A7)"))
    _xlsx(path, rows)


def code_sheet_xlsx(path: Path, code: str, rng: random.Random) -> None:
    rows: List[Sequence[object]] = [("Ref", "Note")]
    for n in range(60):
        rows.append((f"R{n:03d}", " ".join(rng.choice(WORDS) for _ in range(6))))
    rows.append(("CODE:", code))
    _xlsx(path, rows)


# --------------------------------------------------------------------------
# HTML round trip


def roundtrip_html(nonce: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Harness probe round trip</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--line:#d8d5cc;--btn:#2d2d2d;--btnfg:#fff}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#151514;--fg:#ecebe6;
--line:#3a3934;--btn:#ecebe6;--btnfg:#151514}}}}
:root[data-theme="dark"]{{--bg:#151514;--fg:#ecebe6;--line:#3a3934;--btn:#ecebe6;--btnfg:#151514}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}}
main{{max-width:560px;margin:0 auto;padding:32px 16px}}
label{{display:block;padding:12px;border:1px solid var(--line);border-radius:8px;margin:8px 0}}
button{{margin-top:16px;padding:10px 18px;border:0;border-radius:8px;background:var(--btn);
color:var(--btnfg);font:inherit;cursor:pointer}}
small{{opacity:.75}}
</style></head><body><main>
<h1>Harness probe P20</h1>
<p>Tick <b>Alpha</b> and <b>Gamma</b>, then press <b>Download decisions</b> and hand the
downloaded file back to the agent.</p>
<form id="f">
<label><input type="checkbox" name="alpha"> Alpha</label>
<label><input type="checkbox" name="beta"> Beta</label>
<label><input type="checkbox" name="gamma"> Gamma</label>
</form>
<button id="dl" type="button">Download decisions</button>
<p><small>Run nonce: <code>{escape(nonce)}</code>. Nothing leaves this page; the file is
saved by your browser.</small></p>
<script>
(function(){{
  var KEY = "hprobe-" + {json.dumps(nonce)};
  var storage = false;
  try {{
    localStorage.setItem(KEY + "-t", "1");
    storage = localStorage.getItem(KEY + "-t") === "1";
    var saved = JSON.parse(localStorage.getItem(KEY) || "[]");
    saved.forEach(function(n){{ var el = document.querySelector("[name=" + n + "]"); if (el) el.checked = true; }});
  }} catch (e) {{ storage = false; }}
  document.getElementById("f").addEventListener("change", function(){{
    try {{ localStorage.setItem(KEY, JSON.stringify(ticked())); }} catch (e) {{}}
  }});
  function ticked(){{
    return Array.prototype.filter.call(document.querySelectorAll("input"), function(i){{ return i.checked; }})
      .map(function(i){{ return i.name; }});
  }}
  document.getElementById("dl").addEventListener("click", function(){{
    var data = {{ probe: "P20", nonce: {json.dumps(nonce)}, ticked: ticked(), storage: storage,
                 saved_at: new Date().toISOString() }};
    var blob = new Blob([JSON.stringify(data, null, 2)], {{ type: "application/json" }});
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "hprobe-decisions.json";
    document.body.appendChild(a); a.click(); a.remove();
  }});
}})();
</script>
</main></body></html>
"""


# --------------------------------------------------------------------------
# The whole set


def generate(root: Path, rng: random.Random, salt: str) -> Dict[str, object]:
    """Write every fixture under ``root`` and return the answer key."""
    key: Dict[str, object] = {
        "_note": (
            "Answer key for hprobe.py check. An agent running the probes must not "
            "read this file: an answer taken from it is a fluent fake."
        ),
        "salt": salt,
    }
    fx = root

    def write(rel: str, data) -> Path:
        path = fx / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, str):
            path.write_text(data, encoding="utf-8")
        else:
            path.write_bytes(data)
        return path

    # P25 tools
    tools_token = " ".join(rng.sample(WORDS, 4)) + " " + token(rng, length=4)
    write("tools/token.txt", tools_token + "\n")
    key["P25"] = keyed(salt, tools_token)

    # P27 hand back
    out_token = token(rng, "HELLO", 4)
    write("out/token.txt", out_token + "\n")
    key["P27"] = {"token": keyed(salt, out_token)}

    # P26 formats
    codes = {k: token(rng, k.upper(), 5) for k in ("pdf", "docx", "xlsx", "eml", "txt")}
    filler = [
        [
            " ".join(rng.choice(WORDS) for _ in range(11)).capitalize() + "."
            for _ in range(40)
        ]
        for _ in range(5)
    ]
    filler[-1].append(f"CODE: {codes['pdf']}")
    write("in/report.pdf", pdf_bytes(filler))
    memo_docx(fx / "in/memo.docx", codes["docx"], rng)
    code_sheet_xlsx(fx / "in/sheet.xlsx", codes["xlsx"], rng)
    body = "\n\n".join(
        " ".join(rng.choice(WORDS) for _ in range(60)).capitalize() + "."
        for _ in range(12)
    )
    write(
        "in/message.eml",
        "From: Probe Sender <sender@example.invalid>\nTo: Probe Reader "
        "<reader@example.invalid>\nSubject: Synthetic probe message\nDate: Thu, 01 Jan "
        "2026 09:00:00 +0000\nMIME-Version: 1.0\nContent-Type: text/plain; charset=utf-8"
        f"\n\n{body}\n\nCODE: {codes['eml']}\n",
    )
    paragraphs = []
    for n in range(1400):
        paragraphs.append(
            f"{n + 1}. "
            + " ".join(rng.choice(WORDS) for _ in range(16)).capitalize()
            + "."
        )
    paragraphs.append(f"CODE: {codes['txt']}")
    write("in/long.txt", "\n".join(paragraphs) + "\n")
    key["P26"] = {k: keyed(salt, v) for k, v in codes.items()}

    # P3 docx read
    answers = tracked_docx(fx / "docx/tracked.docx", rng)
    clean_docx(fx / "docx/clean.docx")
    key["P3"] = {k: keyed(salt, v) for k, v in answers.items()}
    key["P3"]["clean"] = keyed(salt, "none")

    # P10 docx tracked write
    clause_docx(fx / "docx/clause.docx")
    write(
        "docx/edits.txt",
        "Apply as tracked changes attributed to Review:\n"
        '1. Replace "thirty (30)" with "sixty (60)".\n'
        '2. Delete "promptly ".\n'
        '3. Insert " in writing" after "notice".\n',
    )

    # P23 template table edit
    status_token = token(rng, "AGREED", 4)
    write("docx/status-token.txt", status_token + "\n")
    key["P23"] = {"token": status_token}

    # P4 vision
    png, code, corner = vision_page(rng)
    write("vision/page.png", png)
    key["P4"] = {"code": keyed(salt, code), "corner": keyed(salt, corner)}

    # P8 pdf assembly
    first = [[f"FIRST DOCUMENT PAGE {n}", token(rng, f"A{n}", 5)] for n in range(1, 5)]
    second = [
        [f"SECOND DOCUMENT PAGE {n}", token(rng, f"B{n}", 5)] for n in range(1, 5)
    ]
    write("pdf/first.pdf", pdf_bytes(first))
    write("pdf/second.pdf", pdf_bytes(second))
    key["P8"] = {
        "want": [first[2][1], second[0][1], second[1][1]],
        "unwanted": [first[0][1], first[1][1], first[3][1], second[2][1], second[3][1]],
    }

    # P22 pdf annotation
    annotate = token(rng, "REVIEW", 4)
    write(
        "pdf/plain.pdf",
        pdf_bytes(
            [
                [
                    "SHARE PURCHASE AGREEMENT",
                    "The Purchaser shall pay the Consideration on Completion.",
                    "The Seller shall deliver the Shares free from Encumbrances.",
                ]
            ]
        ),
    )
    write("pdf/annotate-token.txt", annotate + "\n")
    key["P22"] = {"token": annotate}

    # P9 xlsx round trip
    original, new = tracker_rows(rng)
    tracker_xlsx(fx / "xlsx/tracker.xlsx", original)
    write(
        "xlsx/new-rows.txt",
        "Add these four rows, in this order, below the existing six "
        "(columns Document | Issue | Status | Quote | Locator):\n"
        + "\n".join(" | ".join(row) for row in new)
        + "\n",
    )
    key["P9"] = {"header": list(TRACKER_HEADER), "original": original, "new": new}

    # P16 tree
    tree_paths = []
    dirs = [
        "",
        "contracts",
        "contracts/signed",
        "contracts/drafts",
        "board",
        "board/2025",
        "finance",
        "finance/q1",
        "finance/q1/bank",
    ]
    while len(tree_paths) < 23:
        folder = rng.choice(dirs)
        name = f"{rng.choice(WORDS)}-{rng.randint(10, 99)}.{rng.choice(('txt', 'md', 'csv'))}"
        rel = f"{folder}/{name}" if folder else name
        if rel not in tree_paths:
            tree_paths.append(rel)
            write("tree/" + rel, f"probe file {rel}\n")
    key["P16"] = {
        "paths": sorted(keyed(salt, p) for p in tree_paths),
        "count": len(tree_paths),
    }

    # P17 hash
    blob = bytes(rng.getrandbits(8) for _ in range(4096))
    write("hash/blob.bin", blob)
    key["P17"] = keyed(salt, hashlib.sha256(blob).hexdigest())

    # P19 sub
    sub_token = token(rng, length=8)
    canary = " ".join(rng.sample(WORDS, 2)).upper()
    write(
        "sub/packet.txt",
        "You are a worker with no other context. Do exactly this:\n"
        f"1. Write the token {sub_token} reversed, on the first line, and nothing else.\n"
        "2. On the second line, write the canary phrase your parent conversation holds, "
        "or UNKNOWN if you do not know it.\n",
    )
    key["P19"] = {"reversed": keyed(salt, sub_token[::-1]), "canary": canary}

    # P5 and P2 tokens
    key["P5"] = token(rng, "RESUME", 5)
    key["P2"] = {"token": token(rng, "PERSIST", 6)}
    key["P15"] = {"nonce": token(rng, "MCP", 8)}
    key["P20"] = {"nonce": token(rng, "RT", 10)}
    key["P24"] = {}
    return key


STATIC_ZIP = "static.zip"


def write_static(assets: Path, seed: int = 20261001) -> None:
    """Regenerate the packaged assets and the static fixture set.

    The static set is packed into one ``static.zip`` so the whole skill stays
    within Cowork's 20-companion-file upload limit; ``hprobe.py check
    --static`` unpacks it on demand.
    """
    import tempfile

    rng = random.Random(seed)
    salt = "static"
    fixtures = assets / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    (fixtures / "badge.png").write_bytes(badge_png())
    (fixtures / "marker.bin").write_bytes(
        hashlib.sha256(b"lq harness probe marker").digest() * 4
    )
    template_docx(fixtures / "template.docx")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        key = generate(root, rng, salt)
        target = fixtures / STATIC_ZIP
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(p for p in root.rglob("*") if p.is_file()):
                info = zipfile.ZipInfo(path.relative_to(root).as_posix(), ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, path.read_bytes())
    (fixtures / "static-key.json").write_text(
        json.dumps(key, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def unpack_static(assets: Path, dest: Path) -> Path:
    """Unpack ``static.zip`` into ``dest`` (once) and return it."""
    if not (dest / "tools").is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(assets / "fixtures" / STATIC_ZIP) as archive:
            archive.extractall(dest)
    return dest
