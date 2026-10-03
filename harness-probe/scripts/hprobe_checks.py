"""Verifiers for the harness probes.

Each ``check_*`` function looks at what the agent produced - an answer, a
file in ``<run>/outputs/``, a file the user handed back - and returns a
:class:`Check` with an outcome, the evidence it saw, and any per-code
outcomes or runtime facts. Nothing here reads an answer the agent supplied
without comparing it to the run's key or to the fixture it came from.

Standard library only. The PDF, DOCX and XLSX readers are deliberately
small: they read what common tools write, and they say "could not read"
rather than guess.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import hmac
import importlib.util
import json
import platform
import re
import shutil
import sys
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

from hprobe_fixtures import CLAUSE, TEMPLATE_ROWS, keyed, normalise, sha256_file

RAW_FETCH_URL = (
    "https://raw.githubusercontent.com/LegalQuants/lq-plugin-oss/"
    "fa5a6681dc3cc9a08fa9ed48a5fd213057edafa0/LICENSE"
)
RAW_FETCH_SHA256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
RAW_FETCH_BYTES = 11358
EXAMPLE_HEADING = "example domain"
# P12 accepts any one of these stable public pages, so a harness behind an
# egress allow-list is judged on whether it can fetch at all, not on one host.
FETCH_PAGES = (
    ("example.com/", EXAMPLE_HEADING),
    ("www.iana.org/help/example-domains", "example domains"),
    (RAW_FETCH_URL.split("://", 1)[1], "apache license"),
)
BRIBERY_PATH = "/ukpga/2010/23/section/1"
BRIBERY_SENTENCE = "is guilty of an offence if either of the following cases applies"
INVOKE_TOKEN = "INVOKE-OK-4K7R"

PACKAGES = ("pypdf", "pdfplumber", "docx", "openpyxl", "PIL", "fitz", "playwright")
BINARIES = (
    "pdftoppm",
    "pdfinfo",
    "pdftotext",
    "soffice",
    "libreoffice",
    "tesseract",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "rsvg-convert",
    "magick",
    "convert",
    "inkscape",
    "codex",
)

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


@dataclass
class Check:
    outcome: str
    evidence: str
    codes: Dict[str, str] = field(default_factory=dict)
    facts: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    record: bool = True


@dataclass
class Run:
    root: Path
    skill: Path
    key: Dict[str, Any]
    info: Dict[str, Any]
    fixtures_dir: Optional[Path] = None
    outputs_dir: Optional[Path] = None

    @property
    def fixtures(self) -> Path:
        return self.fixtures_dir or self.root / "fixtures"

    @property
    def outputs(self) -> Path:
        return self.outputs_dir or self.root / "outputs"

    @property
    def inputs(self) -> Path:
        return self.root / "inputs"

    @property
    def state(self) -> Path:
        path = self.root / "state"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def salt(self) -> str:
        return str(self.key["salt"])


def _missing(path: Path, what: str) -> Check:
    return Check("fail", f"{what} not found at {path}")


def parse_pairs(answer: str) -> Dict[str, str]:
    pairs: Dict[str, str] = {}
    for part in re.split(r";\s*(?=[a-z_]+=)", answer or ""):
        if "=" in part:
            k, v = part.split("=", 1)
            pairs[k.strip().lower()] = v.strip()
    return pairs


def _now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


# --------------------------------------------------------------------------
# P1 environment


def check_env(run: Run, args: Any) -> Check:
    packages = {name: importlib.util.find_spec(name) is not None for name in PACKAGES}
    binaries = {name: shutil.which(name) is not None for name in BINARIES}
    read_ok = False
    write_ok = False
    try:
        read_ok = bool(
            (run.fixtures / "tools" / "token.txt").read_text(encoding="utf-8")
        )
    except OSError:
        pass
    try:
        run.outputs.mkdir(parents=True, exist_ok=True)
        probe = run.outputs / "env-probe.txt"
        probe.write_text("written by hprobe.py env\n", encoding="utf-8")
        write_ok = probe.read_text(encoding="utf-8").startswith("written")
    except OSError:
        pass
    facts = {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "packages": packages,
        "binaries": binaries,
        "read_fixture": read_ok,
        "write_output": write_ok,
    }
    exec_ok = read_ok and write_ok
    codes = {
        "EXEC": "pass" if exec_ok else "fail",
        "BIN": "pass" if any(binaries.values()) else "fail",
    }
    line = (
        f"python {facts['python']} on {facts['platform']}; packages "
        + ",".join(k for k, v in packages.items() if v)
        + "; binaries "
        + ",".join(k for k, v in binaries.items() if v)
        + f"; read={read_ok} write={write_ok}"
    )
    return Check("pass" if exec_ok else "fail", line, codes=codes, facts=facts)


# --------------------------------------------------------------------------
# Simple answer checks


def _keyed_match(run: Run, expected: str, answer: str) -> bool:
    return hmac.compare_digest(keyed(run.salt, answer or ""), expected)


def check_tools(run: Run, args: Any) -> Check:
    if not args.answer:
        return Check("fail", "no answer given")
    ok = _keyed_match(run, run.key["P25"], args.answer)
    return Check(
        "pass" if ok else "fluent-fake",
        (
            "contents match the generated token"
            if ok
            else "contents do not match the file"
        ),
    )


def check_hash(run: Run, args: Any) -> Check:
    answer = (args.answer or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", answer):
        return Check("fail", "answer is not a 64-character hex digest")
    ok = _keyed_match(run, run.key["P17"], answer)
    return Check(
        "pass" if ok else "fluent-fake",
        "digest matches" if ok else "digest does not match blob.bin",
    )


def check_vision(run: Run, args: Any) -> Check:
    pairs = parse_pairs(args.answer or "")
    key = run.key["P4"]
    code_ok = _keyed_match(run, key["code"], pairs.get("code", ""))
    corner_ok = _keyed_match(run, key["corner"], pairs.get("corner", ""))
    if code_ok and corner_ok:
        return Check("pass", "code and scribble corner both right")
    wrong = [n for n, ok in (("code", code_ok), ("corner", corner_ok)) if not ok]
    return Check("fail", "wrong: " + ", ".join(wrong))


def check_formats(run: Run, args: Any) -> Check:
    pairs = parse_pairs(args.answer or "")
    key = run.key["P26"]
    right = [k for k in key if _keyed_match(run, key[k], pairs.get(k, ""))]
    wrong = [k for k in key if k not in right]
    if not wrong:
        return Check("pass", "all five codes right: " + ", ".join(sorted(right)))
    return Check(
        "fail",
        f"{len(right)} of {len(key)} right; wrong or missing: "
        + ", ".join(sorted(wrong)),
        facts={"formats_read": sorted(right), "formats_missed": sorted(wrong)},
    )


def check_docx_read(run: Run, args: Any) -> Check:
    pairs = parse_pairs(args.answer or "")
    key = run.key["P3"]
    wrong = [k for k in key if not _keyed_match(run, key[k], pairs.get(k, ""))]
    if not wrong:
        return Check(
            "pass",
            "insertion, deletion, both authors, comment and the clean nil all right",
        )
    outcome = "fail"
    if "clean" in wrong and len(wrong) == 1:
        outcome = "fluent-fake"
    return Check(outcome, "wrong or missing: " + ", ".join(sorted(wrong)))


def _page_key(url: str) -> str:
    """A URL without scheme, query, fragment or trailing slash, for comparison."""
    url = (url or "https://example.com/").strip().split("://", 1)[-1]
    return url.split("#", 1)[0].split("?", 1)[0].rstrip("/")


def check_fetch_page(run: Run, args: Any) -> Check:
    key = _page_key(args.url)
    heading = next((h for page, h in FETCH_PAGES if key == page.rstrip("/")), None)
    facts = {"url": key, "bytes_reported": int(args.bytes or 0)}
    if heading is None:
        return Check(
            "fail",
            f"{key} is not one of the probe's pages: "
            + ", ".join(p for p, _ in FETCH_PAGES),
            facts=facts,
        )
    ok = normalise(args.answer or "") == heading
    return Check(
        "pass" if ok else "fail",
        f"heading of {key} quoted verbatim" if ok else f"heading was '{args.answer}'",
        facts=facts,
    )


def check_search(run: Run, args: Any) -> Check:
    url = (args.url or "").strip()
    url_ok = "legislation.gov.uk" in url and BRIBERY_PATH in url
    quote_ok = BRIBERY_SENTENCE in normalise(args.answer or "")
    facts = {"url": url, "bytes_reported": int(args.bytes or 0)}
    if url_ok and quote_ok:
        return Check("pass", f"quoted from {url}", facts=facts)
    if quote_ok and not url_ok:
        return Check(
            "fluent-fake",
            "the sentence is right but the address is not the official page",
            facts=facts,
        )
    return Check("fail", "address or quotation wrong", facts=facts)


def check_hand_back(run: Run, args: Any) -> Check:
    path = run.outputs / "hello-probe.txt"
    if not path.is_file():
        return _missing(path, "hello-probe.txt")
    ok = _keyed_match(run, run.key["P27"]["token"], path.read_text(encoding="utf-8"))
    return Check(
        "pass" if ok else "fail",
        (
            "file written with exactly the token"
            if ok
            else "file contents differ from the token"
        ),
    )


def check_persist(run: Run, args: Any) -> Check:
    token = run.key["P2"]["token"]
    if args.phase == "write":
        (run.state / "p2-armed.json").write_text(
            json.dumps({"armed_at": _now().isoformat()}), encoding="utf-8"
        )
        print(f"P2 token: {token}")
        return Check(
            "pending",
            "session one armed; write the token to lq-probe-persist.txt in the workspace root",
        )
    if not args.answer:
        return Check("fail", "no token found in the second session")
    ok = normalise(args.answer) == normalise(token)
    armed = run.state / "p2-armed.json"
    later = ""
    if armed.is_file():
        when = json.loads(armed.read_text(encoding="utf-8"))["armed_at"]
        later = f"; armed {when}"
    return Check(
        "pass" if ok else "fail",
        ("token found in a later session" if ok else "token did not match") + later,
    )


def check_resume_token(run: Run, args: Any) -> Check:
    print(f"P5 token: {run.key['P5']}")
    return Check(
        "pending",
        "token issued; resume this task later and ask for it, then try a new task",
    )


# --------------------------------------------------------------------------
# P7 and P21: the skill folder


def check_asset(run: Run, args: Any) -> Check:
    badge = run.outputs / "badge.png"
    card = run.outputs / "card.html"
    source = run.skill / "assets" / "fixtures" / "badge.png"
    if not badge.is_file():
        return _missing(badge, "badge.png")
    if not card.is_file():
        return _missing(card, "card.html")
    same = source.is_file() and sha256_file(source) == sha256_file(badge)
    refs = "badge.png" in card.read_text(encoding="utf-8", errors="replace")
    if same and refs:
        return Check(
            "pass", "packaged badge copied byte for byte and referenced by card.html"
        )
    problems = []
    if not same:
        problems.append("badge.png is not the packaged file")
    if not refs:
        problems.append("card.html does not reference badge.png")
    codes = {"OUT": "pass", "SKILLDIR": "fail"} if not same and refs else {}
    return Check("fail", "; ".join(problems), codes=codes)


def check_skilldir(run: Run, args: Any) -> Check:
    here = Path(__file__).resolve().parent
    try:
        import hprobe_engine  # noqa: F401  (the sibling import is the point)

        imported = True
    except ImportError:
        imported = False
    marker = here.parent / "assets" / "fixtures" / "marker.bin"
    digest = sha256_file(marker) if marker.is_file() else ""
    siblings = sorted(
        p.name
        for p in here.parent.parent.iterdir()
        if p.is_dir() and p != here.parent and (p / "SKILL.md").is_file()
    )
    ok = imported and bool(digest)
    evidence = (
        f"script at {here}; sibling import {'ok' if imported else 'failed'}; "
        f"marker sha256 {digest[:16] or 'unreadable'}; sibling skills: "
        + (", ".join(siblings) or "none visible")
    )
    return Check(
        "pass" if ok else "fail",
        evidence,
        facts={"skill_dir": str(here.parent), "sibling_skills": siblings},
    )


# --------------------------------------------------------------------------
# PDF reading (P8, P22)


class Pdf:
    """Just enough of a PDF reader to find pages, text tokens and annotations."""

    OBJ_RE = re.compile(rb"(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj", re.S)

    def __init__(self, data: bytes):
        self.data = data
        self.objects: Dict[int, bytes] = {}
        for match in self.OBJ_RE.finditer(data):
            self.objects[int(match.group(1))] = match.group(3)
        for number, body in list(self.objects.items()):
            if b"/ObjStm" in body:
                self._unpack_objstm(body)

    @staticmethod
    def stream(body: bytes) -> bytes:
        match = re.search(rb"stream\r?\n(.*?)\r?\n?endstream", body, re.S)
        if not match:
            return b""
        raw = match.group(1)
        if b"/FlateDecode" in body.split(b"stream", 1)[0]:
            try:
                return zlib.decompress(raw)
            except zlib.error:
                try:
                    return zlib.decompressobj().decompress(raw)
                except zlib.error:
                    return b""
        return raw

    def _unpack_objstm(self, body: bytes) -> None:
        data = self.stream(body)
        first = re.search(rb"/First\s+(\d+)", body)
        count = re.search(rb"/N\s+(\d+)", body)
        if not data or not first or not count:
            return
        head = data[: int(first.group(1))].split()
        pairs = [(int(head[i]), int(head[i + 1])) for i in range(0, len(head) - 1, 2)]
        base = int(first.group(1))
        for index, (number, offset) in enumerate(pairs[: int(count.group(1))]):
            end = base + pairs[index + 1][1] if index + 1 < len(pairs) else len(data)
            self.objects.setdefault(number, data[base + offset : end])

    @staticmethod
    def refs(text: bytes) -> List[int]:
        return [int(n) for n in re.findall(rb"(\d+)\s+0\s+R", text)]

    def root(self) -> Optional[int]:
        for match in re.finditer(rb"/Root\s+(\d+)\s+0\s+R", self.data):
            return int(match.group(1))
        return None

    def pages(self) -> List[int]:
        root = self.root()
        out: List[int] = []
        if root and root in self.objects:
            pages = re.search(rb"/Pages\s+(\d+)\s+0\s+R", self.objects[root])
            if pages:
                self._walk(int(pages.group(1)), out, set())
        if not out:
            out = [
                n
                for n, body in sorted(self.objects.items())
                if re.search(rb"/Type\s*/Page(?!s)", body)
            ]
        return out

    def _walk(self, number: int, out: List[int], seen: set) -> None:
        if number in seen or number not in self.objects:
            return
        seen.add(number)
        body = self.objects[number]
        if re.search(rb"/Type\s*/Pages", body):
            kids = re.search(rb"/Kids\s*\[(.*?)\]", body, re.S)
            for kid in self.refs(kids.group(1)) if kids else []:
                self._walk(kid, out, seen)
        elif re.search(rb"/Type\s*/Page", body):
            out.append(number)

    def page_text(self, number: int) -> bytes:
        body = self.objects.get(number, b"")
        contents = re.search(rb"/Contents\s*(\[.*?\]|\d+\s+0\s+R)", body, re.S)
        if not contents:
            return b""
        chunks = []
        for ref in self.refs(contents.group(1)):
            chunks.append(self.stream(self.objects.get(ref, b"")))
        return b"\n".join(chunks)

    def annotations(self) -> List[Tuple[str, str]]:
        found = []
        for body in self.objects.values():
            sub = re.search(rb"/Subtype\s*/(\w+)", body)
            if (
                not sub
                or b"/Annot" not in body
                and sub.group(1)
                not in (
                    b"Highlight",
                    b"Text",
                    b"FreeText",
                    b"Underline",
                    b"Squiggly",
                )
            ):
                continue
            contents = ""
            match = re.search(
                rb"/Contents\s*(\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f\s]*>)", body
            )
            if match:
                contents = _pdf_string(match.group(1))
            found.append((sub.group(1).decode("latin-1"), contents))
        return found


def _pdf_string(raw: bytes) -> str:
    if raw.startswith(b"<"):
        data = bytes.fromhex(re.sub(rb"\s", b"", raw[1:-1]).decode("ascii") or "")
    else:
        body = raw[1:-1]
        out = bytearray()
        i = 0
        while i < len(body):
            c = body[i]
            if c == 0x5C and i + 1 < len(body):
                nxt = body[i + 1]
                mapping = {0x6E: 10, 0x72: 13, 0x74: 9, 0x62: 8, 0x66: 12}
                if nxt in mapping:
                    out.append(mapping[nxt])
                    i += 2
                    continue
                if 0x30 <= nxt <= 0x37:
                    octal = re.match(rb"[0-7]{1,3}", body[i + 1 : i + 4]).group(0)
                    out.append(int(octal, 8) & 0xFF)
                    i += 1 + len(octal)
                    continue
                out.append(nxt)
                i += 2
                continue
            out.append(c)
            i += 1
        data = bytes(out)
    if data.startswith(b"\xfe\xff"):
        return data[2:].decode("utf-16-be", "replace")
    if data.startswith(b"\xff\xfe"):
        return data[2:].decode("utf-16-le", "replace")
    return data.decode("latin-1")


def check_pdf_assemble(run: Run, args: Any) -> Check:
    path = run.outputs / "assembled.pdf"
    if not path.is_file():
        return _missing(path, "assembled.pdf")
    pdf = Pdf(path.read_bytes())
    pages = pdf.pages()
    key = run.key["P8"]
    seen = []
    for number in pages:
        text = pdf.page_text(number).decode("latin-1", "replace")
        hit = [t for t in key["want"] + key["unwanted"] if t in text]
        seen.append(hit[0] if hit else "?")
    if seen == key["want"]:
        return Check("pass", f"{len(pages)} pages in the right order")
    if "?" in seen:
        return Check(
            "fail",
            f"{len(pages)} pages; could not read the page markers on "
            f"{seen.count('?')} of them (the tool may have rasterised them)",
        )
    return Check("fail", f"pages are {seen}, wanted {key['want']}")


def check_pdf_annotate(run: Run, args: Any) -> Check:
    path = run.outputs / "annotated.pdf"
    if not path.is_file():
        return _missing(path, "annotated.pdf")
    pdf = Pdf(path.read_bytes())
    annots = pdf.annotations()
    token = run.key["P22"]["token"]
    kinds = {kind for kind, _ in annots}
    highlight = bool(kinds & {"Highlight", "Underline", "Squiggly"})
    comment = any(token in contents for _, contents in annots)
    if highlight and comment:
        return Check("pass", "a highlight and a comment carrying the token")
    problems = []
    if not highlight:
        problems.append("no highlight annotation")
    if not comment:
        problems.append("no annotation whose contents carry the token")
    return Check(
        "fail", "; ".join(problems) + f" (annotations seen: {sorted(kinds) or 'none'})"
    )


# --------------------------------------------------------------------------
# DOCX reading (P10, P23)


def _docx_xml(path: Path, part: str = "word/document.xml") -> ET.Element:
    with zipfile.ZipFile(path) as archive:
        return ET.fromstring(archive.read(part))


def _texts(node: ET.Element, tag: str = "t") -> str:
    return "".join(el.text or "" for el in node.iter(f"{W}{tag}"))


def check_docx_tracked_write(run: Run, args: Any) -> Check:
    path = run.outputs / "clause-tracked.docx"
    if not path.is_file():
        return _missing(path, "clause-tracked.docx")
    try:
        root = _docx_xml(path)
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        return Check("fail", f"not a readable Word file: {exc}")
    inserted = [(el.get(f"{W}author"), _texts(el)) for el in root.iter(f"{W}ins")]
    deleted = [
        (el.get(f"{W}author"), _texts(el, "delText")) for el in root.iter(f"{W}del")
    ]
    ins_text = normalise(" ".join(t for _, t in inserted))
    del_text = normalise(" ".join(t for _, t in deleted))
    authors = {a for a, _ in inserted + deleted}
    edits = {
        "replace": "sixty (60)" in ins_text and "thirty (30)" in del_text,
        "delete": "promptly" in del_text,
        "insert": "in writing" in ins_text,
    }
    if not inserted and not deleted:
        return Check(
            "fail", "no tracked changes at all; the edits were applied as plain text"
        )
    if all(edits.values()) and authors == {"Review"}:
        return Check("pass", "all three edits are tracked changes attributed to Review")
    missing = [k for k, ok in edits.items() if not ok]
    note = []
    if missing:
        note.append("missing tracked edits: " + ", ".join(missing))
    if authors != {"Review"}:
        note.append("authors " + ", ".join(sorted(a or "?" for a in authors)))
    return Check("fail", "; ".join(note))


def check_docx_template(run: Run, args: Any) -> Check:
    path = run.outputs / "template-filled.docx"
    if not path.is_file():
        return _missing(path, "template-filled.docx")
    try:
        root = _docx_xml(path)
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        return Check("fail", f"not a readable Word file: {exc}")
    tables = list(root.iter(f"{W}tbl"))
    if not tables:
        return Check("fail", "no table in the document")
    table = tables[0]
    style = table.find(f"{W}tblPr/{W}tblStyle")
    rows = [
        [normalise(_texts(tc)) for tc in tr.findall(f"{W}tc")]
        for tr in table.findall(f"{W}tr")
    ]
    token = run.key["P23"]["token"]
    expected = [[normalise(c) for c in row] for row in TEMPLATE_ROWS]
    expected[2][2] = normalise(token)
    problems = []
    if style is None or style.get(f"{W}val") != "LQProbeGrid":
        problems.append("table style LQProbeGrid lost")
    if len(rows) != len(expected):
        problems.append(f"{len(rows)} rows, expected {len(expected)}")
    elif rows != expected:
        diffs = [
            f"row {r} col {c}"
            for r, (got, want) in enumerate(zip(rows, expected))
            for c, (g, w) in enumerate(zip(got, want))
            if g != w
        ]
        problems.append("cells differ: " + ", ".join(diffs[:6]))
    if problems:
        return Check("fail", "; ".join(problems))
    return Check(
        "pass", "packaged template copied, one cell changed, style and rows intact"
    )


# --------------------------------------------------------------------------
# XLSX reading (P9)


def read_xlsx(path: Path) -> Dict[int, Dict[str, Tuple[str, Optional[str]]]]:
    """row number -> column letter -> (value, formula) for the first sheet."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        shared: List[str] = []
        if "xl/sharedStrings.xml" in names:
            sst = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in sst.iter(f"{S}si"):
                shared.append("".join(t.text or "" for t in si.iter(f"{S}t")))
        sheet_part = "xl/worksheets/sheet1.xml"
        try:
            workbook = ET.fromstring(archive.read("xl/workbook.xml"))
            first = workbook.find(f"{S}sheets/{S}sheet")
            rid = first.get(f"{R_NS}id") if first is not None else None
            rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
            for rel in rels:
                if rel.get("Id") == rid:
                    target = rel.get("Target", "")
                    sheet_part = (
                        target.lstrip("/") if target.startswith("/") else "xl/" + target
                    )
        except (KeyError, ET.ParseError):
            pass
        sheet = ET.fromstring(archive.read(sheet_part))
    rows: Dict[int, Dict[str, Tuple[str, Optional[str]]]] = {}
    for c in sheet.iter(f"{S}c"):
        ref = c.get("r", "")
        match = re.match(r"([A-Z]+)(\d+)", ref)
        if not match:
            continue
        col, row = match.group(1), int(match.group(2))
        kind = c.get("t", "n")
        formula_el = c.find(f"{S}f")
        formula = formula_el.text if formula_el is not None else None
        value_el = c.find(f"{S}v")
        value = value_el.text if value_el is not None else ""
        if kind == "s" and value:
            value = shared[int(value)]
        elif kind == "inlineStr":
            value = "".join(t.text or "" for t in c.iter(f"{S}t"))
        if (
            formula is not None
            and formula_el is not None
            and formula == ""
            and formula_el.get("t") == "shared"
        ):
            formula = "(shared)"
        rows.setdefault(row, {})[col] = (value or "", formula)
    return rows


def check_xlsx(run: Run, args: Any) -> Check:
    path = run.outputs / "tracker-out.xlsx"
    if not path.is_file():
        return _missing(path, "tracker-out.xlsx")
    try:
        rows = read_xlsx(path)
    except (zipfile.BadZipFile, KeyError, ET.ParseError) as exc:
        return Check("fail", f"not a readable workbook: {exc}")
    key = run.key["P9"]
    cols = "ABCDE"

    def row_values(n: int) -> List[str]:
        return [normalise(rows.get(n, {}).get(c, ("", None))[0]) for c in cols]

    problems = []
    if row_values(1) != [normalise(h) for h in key["header"]]:
        problems.append("header row changed")
    for i, original in enumerate(key["original"], start=2):
        if row_values(i) != [normalise(v) for v in original]:
            problems.append(f"original row {i} changed")
    data_rows = [n for n in sorted(rows) if n > 7]
    new_found = 0
    for new in key["new"]:
        if any(row_values(n)[0] == normalise(new[0]) for n in data_rows):
            new_found += 1
    if new_found != len(key["new"]):
        problems.append(f"{new_found} of {len(key['new'])} new rows found")
    formulas = [
        (n, c, f) for n, cells in rows.items() for c, (_, f) in cells.items() if f
    ]
    if not formulas:
        problems.append("the count is no longer a live formula")
    if problems:
        return Check("fail", "; ".join(problems))
    return Check(
        "pass",
        "header and six original rows intact, four new rows added, count still a formula ("
        + ", ".join(f"{c}{n}={f}" for n, c, f in formulas[:2])
        + ")",
    )


# --------------------------------------------------------------------------
# P13 schedule, P15 MCP, P16 tree, P18 raw fetch, P19 worker, P20, P24


def check_sched(run: Run, args: Any) -> Check:
    armed = run.state / "p13-armed.json"
    fired = run.state / "p13-fired.json"
    if args.phase == "arm":
        armed.write_text(json.dumps({"armed_at": _now().isoformat()}), encoding="utf-8")
        command = (
            f'python3 "{run.skill / "scripts" / "hprobe.py"}" check P13 '
            f'--run "{run.root}" --phase fire'
        )
        print(f"Schedule this to run at least ten minutes from now:\n  {command}")
        return Check("pending", "armed; waiting for the scheduled run")
    if args.phase == "fire":
        fired.write_text(json.dumps({"fired_at": _now().isoformat()}), encoding="utf-8")
        return Check("pending", "scheduled run fired", record=False)
    if not armed.is_file():
        return Check("fail", "P13 was never armed")
    if not fired.is_file():
        return Check("fail", "no scheduled run has fired")
    a = _dt.datetime.fromisoformat(json.loads(armed.read_text())["armed_at"])
    f = _dt.datetime.fromisoformat(json.loads(fired.read_text())["fired_at"])
    gap = (f - a).total_seconds() / 60
    if gap >= 5:
        return Check("pass", f"scheduled run fired {gap:.0f} minutes after arming")
    return Check(
        "fail", f"run fired only {gap:.1f} minutes after arming (not a later run)"
    )


def mcp_digest(secret: bytes, nonce: str) -> str:
    return hmac.new(secret, nonce.encode("utf-8"), hashlib.sha256).hexdigest()[:24]


def check_mcp(run: Run, args: Any) -> Check:
    nonce = run.key["P15"]["nonce"]
    if args.phase == "nonce":
        print(f"P15 nonce: {nonce}")
        return Check("pending", "nonce issued", record=False)
    secret_path = run.state / "mcp-secret"
    log_path = run.state / "mcp-calls.jsonl"
    if not secret_path.is_file():
        return Check("fail", "the probe server has never started for this run")
    expected = mcp_digest(secret_path.read_bytes(), nonce)
    answered = (args.answer or "").strip().lower()
    called = log_path.is_file() and nonce in log_path.read_text(encoding="utf-8")
    if answered == expected and called:
        return Check("pass", "digest returned by the server's probe_challenge tool")
    if answered == expected:
        return Check("fail", "digest right but the server never logged the call")
    return Check(
        "fluent-fake" if answered else "fail",
        "digest does not match what the server would return"
        + ("" if called else "; the server logged no call with this nonce"),
    )


def check_tree(run: Run, args: Any) -> Check:
    listing = run.outputs / "sibling-run" / "listing.txt"
    if not listing.is_file():
        return _missing(listing, "sibling-run/listing.txt")
    lines = []
    for raw in listing.read_text(encoding="utf-8").splitlines():
        line = raw.strip().replace("\\", "/")
        if not line:
            continue
        for prefix in ("./", "tree/", "fixtures/tree/"):
            if line.startswith(prefix):
                line = line[len(prefix) :]
        lines.append(line)
    key = run.key["P16"]
    got = {keyed(run.salt, line) for line in lines}
    want = set(key["paths"])
    count = int(args.count or 0)
    problems = []
    if got != want:
        problems.append(
            f"{len(got & want)} of {len(want)} paths right, {len(got - want)} not in the folder"
        )
    if count != key["count"]:
        problems.append(f"count given {count}, folder has {key['count']}")
    if problems:
        return Check("fail", "; ".join(problems))
    return Check(
        "pass",
        f"all {key['count']} relative paths and the count right, in a sibling folder",
    )


def check_raw_fetch(run: Run, args: Any) -> Check:
    path = run.outputs / "fetched-LICENSE"
    if not path.is_file():
        return _missing(path, "fetched-LICENSE")
    size = path.stat().st_size
    digest = sha256_file(path)
    facts = {"bytes": size, "sha256": digest}
    if digest == RAW_FETCH_SHA256:
        return Check(
            "pass", f"{size} bytes, digest matches the published file", facts=facts
        )
    return Check(
        "fail",
        f"{size} bytes (want {RAW_FETCH_BYTES}); digest differs - the bytes were changed "
        "on the way (re-encoded, reformatted or summarised)",
        facts=facts,
    )


def check_worker(run: Run, args: Any) -> Check:
    key = run.key["P19"]
    if args.phase == "canary":
        print(f"P19 canary (keep it in this conversation only): {key['canary']}")
        return Check("pending", "canary issued", record=False)
    reply_path = run.outputs / "worker-reply.txt"
    if not reply_path.is_file():
        return _missing(reply_path, "worker-reply.txt")
    reply = reply_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in reply.splitlines() if line.strip()]
    reversed_ok = bool(lines) and _keyed_match(run, key["reversed"], lines[0])
    leaked = normalise(key["canary"]) in normalise(reply)
    facts = {"worker_model": args.model or ""}
    if leaked:
        return Check(
            "fail",
            "the worker knew the parent's canary, so it shared the parent's context",
            facts=facts,
        )
    if not reversed_ok:
        return Check(
            "fail", "the worker did not carry out the packet's instruction", facts=facts
        )
    return Check(
        "pass",
        "the worker followed the packet and did not know the canary"
        + (f"; model {args.model}" if args.model else "; model not named"),
        facts=facts,
    )


def check_roundtrip(run: Run, args: Any) -> Check:
    path = run.inputs / "hprobe-decisions.json"
    if not path.is_file():
        return _missing(path, "inputs/hprobe-decisions.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return Check("fail", "the returned file is not the page's JSON")
    facts = {"browser_storage": bool(data.get("storage"))}
    if data.get("nonce") != run.key["P20"]["nonce"]:
        return Check(
            "fluent-fake", "the file does not carry this run's nonce", facts=facts
        )
    if sorted(data.get("ticked", [])) != ["alpha", "gamma"]:
        return Check(
            "fail",
            f"ticked {data.get('ticked')}, asked for alpha and gamma",
            facts=facts,
        )
    return Check(
        "pass",
        "page opened, choices saved by the browser and handed back"
        + ("" if facts["browser_storage"] else "; browser storage was unavailable"),
        facts=facts,
    )


def check_invoke(run: Run, args: Any) -> Check:
    token_ok = normalise(args.answer or "") == normalise(INVOKE_TOKEN)
    implicit = (args.implicit or "").strip().lower()
    if implicit == "fired":
        return Check("fail", "the explicit-only skill fired on a matching prompt")
    if not token_ok:
        return Check("fail", "calling the skill by name did not return its token")
    if implicit != "quiet":
        return Check("pending", "token right; record --implicit quiet|fired to finish")
    return Check(
        "pass", "stayed quiet on a matching prompt and answered when called by name"
    )


CHECKS = {
    "env": check_env,
    "persist": check_persist,
    "resume": check_resume_token,
    "docx-read": check_docx_read,
    "vision": check_vision,
    "search": check_search,
    "asset": check_asset,
    "pdf-assemble": check_pdf_assemble,
    "xlsx": check_xlsx,
    "docx-tracked-write": check_docx_tracked_write,
    "fetch-page": check_fetch_page,
    "sched": check_sched,
    "mcp": check_mcp,
    "tree": check_tree,
    "hash": check_hash,
    "raw-fetch": check_raw_fetch,
    "worker": check_worker,
    "roundtrip": check_roundtrip,
    "skilldir": check_skilldir,
    "pdf-annotate": check_pdf_annotate,
    "docx-template": check_docx_template,
    "invoke": check_invoke,
    "tools": check_tools,
    "formats": check_formats,
    "hand-back": check_hand_back,
}
