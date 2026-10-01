"""The harness-probe skill: fixtures, verifiers, verdict engine and CLI.

The verifiers are exercised by an "oracle agent": helpers that solve each
probe honestly from the fixtures with the standard library, exactly as an
agent with tools would. Each probe is then also fed a wrong or faked answer,
which must not pass.
"""

from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "harness-probe"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

import hprobe  # noqa: E402
import hprobe_checks as checks  # noqa: E402
import hprobe_engine as engine  # noqa: E402
import hprobe_fixtures as fixtures  # noqa: E402

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def args(**kw):
    base = dict(
        answer=None,
        phase=None,
        url=None,
        bytes=0,
        count=0,
        model=None,
        implicit=None,
        notes=None,
        observer="script",
    )
    base.update(kw)
    return SimpleNamespace(**base)


@pytest.fixture
def run(tmp_path: Path) -> checks.Run:
    root = tmp_path / "run"
    assert hprobe.main(["init", "--run", str(root), "--harness", "test harness"]) == 0
    return hprobe._load_run(root)


def results_of(run: checks.Run) -> dict:
    return json.loads((run.root / "results.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# The oracle agent


def code_line(text: str) -> str:
    return re.findall(r"CODE:\s*([A-Z0-9-]+)", text)[-1]


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        root = checks.ET.fromstring(archive.read("word/document.xml"))
    return " ".join(el.text or "" for el in root.iter(f"{W}t"))


def solve_formats(fx: Path) -> str:
    pdf = checks.Pdf((fx / "in/report.pdf").read_bytes())
    pdf_text = b"".join(pdf.page_text(n) for n in pdf.pages()).decode("latin-1")
    rows = checks.read_xlsx(fx / "in/sheet.xlsx")
    last = rows[max(rows)]
    return ";".join(
        [
            f"pdf={code_line(pdf_text)}",
            f"docx={code_line(docx_text(fx / 'in/memo.docx'))}",
            f"xlsx={last['B'][0]}",
            f"eml={code_line((fx / 'in/message.eml').read_text())}",
            f"txt={code_line((fx / 'in/long.txt').read_text())}",
        ]
    )


def solve_tracked(fx: Path) -> str:
    with zipfile.ZipFile(fx / "docx/tracked.docx") as archive:
        doc = checks.ET.fromstring(archive.read("word/document.xml"))
        comments = checks.ET.fromstring(archive.read("word/comments.xml"))
    ins = next(doc.iter(f"{W}ins"))
    dele = next(doc.iter(f"{W}del"))
    return ";".join(
        [
            f"ins={''.join(t.text for t in ins.iter(f'{W}t')).strip()}",
            f"ins_author={ins.get(f'{W}author')}",
            f"del={''.join(t.text for t in dele.iter(f'{W}delText')).strip()}",
            f"del_author={dele.get(f'{W}author')}",
            f"comment={''.join(t.text for t in comments.iter(f'{W}t'))}",
            "clean=none",
        ]
    )


def pdf_pages(path: Path) -> list[list[str]]:
    pdf = checks.Pdf(path.read_bytes())
    out = []
    for number in pdf.pages():
        text = pdf.page_text(number).decode("latin-1")
        out.append(re.findall(r"\((.*?)\) Tj", text))
    return out


def compressed_pdf(pages: list[list[str]]) -> bytes:
    """A PDF whose content streams are FlateDecode, like most tools write."""
    plain = fixtures.pdf_bytes(pages)

    def deflate(match: re.Match) -> bytes:
        data = match.group(2)
        packed = zlib_compress(data)
        return (
            b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(packed)
            + packed
            + b"\nendstream"
        )

    return re.sub(
        rb"<< /Length (\d+) >>\nstream\n(.*?)\nendstream", deflate, plain, flags=re.S
    )


def zlib_compress(data: bytes) -> bytes:
    import zlib

    return zlib.compress(data)


def annotated_pdf(token: str, highlight: bool = True, comment: bool = True) -> bytes:
    annots = []
    if highlight:
        annots.append(
            b"<< /Type /Annot /Subtype /Highlight /Rect [70 740 400 760] "
            b"/QuadPoints [70 760 400 760 70 740 400 740] >>"
        )
    if comment:
        annots.append(
            b"<< /Type /Annot /Subtype /Text /Rect [400 740 420 760] /Contents ("
            + token.encode()
            + b") >>"
        )
    base = fixtures.pdf_bytes([["The Purchaser shall pay the Consideration."]])
    extra = b"".join(
        b"%d 0 obj\n%s\nendobj\n" % (90 + i, a) for i, a in enumerate(annots)
    )
    return base.replace(b"xref", extra + b"xref", 1)


def tracked_clause(author: str = "Review", tracked: bool = True) -> dict:
    if not tracked:
        text = fixtures.CLAUSE.replace("thirty (30)", "sixty (60)").replace(
            "promptly ", ""
        )
        return fixtures._docx_parts(fixtures._para(text))
    body = (
        '<w:p><w:r><w:t xml:space="preserve">The Buyer shall give notice</w:t></w:r>'
        f'<w:ins w:id="1" w:author="{author}"><w:r><w:t xml:space="preserve"> in writing'
        "</w:t></w:r></w:ins>"
        '<w:r><w:t xml:space="preserve"> of any defect within </w:t></w:r>'
        f'<w:del w:id="2" w:author="{author}"><w:r><w:delText>thirty (30)</w:delText>'
        "</w:r></w:del>"
        f'<w:ins w:id="3" w:author="{author}"><w:r><w:t>sixty (60)</w:t></w:r></w:ins>'
        '<w:r><w:t xml:space="preserve"> days and the Seller shall </w:t></w:r>'
        f'<w:del w:id="4" w:author="{author}"><w:r><w:delText xml:space="preserve">promptly '
        "</w:delText></w:r></w:del>"
        "<w:r><w:t>remedy it.</w:t></w:r></w:p>"
    )
    return fixtures._docx_parts(body)


def write_docx(path: Path, parts: dict) -> None:
    fixtures._zip(path, parts)


# --------------------------------------------------------------------------
# Fixtures


class TestFixtures:
    def test_static_fixtures_are_reproducible_and_committed(self, tmp_path):
        fixtures.write_static(tmp_path / "a")
        fixtures.write_static(tmp_path / "b")
        files_a = sorted(
            p.relative_to(tmp_path / "a")
            for p in (tmp_path / "a").rglob("*")
            if p.is_file()
        )
        assert files_a
        for rel in files_a:
            assert (tmp_path / "a" / rel).read_bytes() == (
                tmp_path / "b" / rel
            ).read_bytes(), rel
            committed = SKILL / "assets" / rel
            assert committed.is_file(), f"run `hprobe.py fixtures`: {rel} is missing"
            assert (
                committed.read_bytes() == (tmp_path / "a" / rel).read_bytes()
            ), f"run `hprobe.py fixtures`: {rel} is stale"

    def test_live_runs_draw_fresh_tokens(self, tmp_path):
        key_a = fixtures.generate(tmp_path / "a", random.Random(1), "s1")
        key_b = fixtures.generate(tmp_path / "b", random.Random(2), "s2")
        assert key_a["P25"] != key_b["P25"]
        assert (tmp_path / "a/tools/token.txt").read_text() != (
            tmp_path / "b/tools/token.txt"
        ).read_text()

    def test_the_key_never_holds_a_read_answer_in_clear(self, run):
        key_text = (run.root / "key.json").read_text()
        for rel in ("tools/token.txt", "hash/blob.bin"):
            data = (run.fixtures / rel).read_bytes()
            assert data.strip().decode("latin-1") not in key_text
        assert (
            hashlib.sha256((run.fixtures / "hash/blob.bin").read_bytes()).hexdigest()
            not in key_text
        )

    def test_png_is_a_valid_image(self, run):
        data = (run.fixtures / "vision/page.png").read_bytes()
        assert data.startswith(b"\x89PNG\r\n\x1a\n")
        assert b"IHDR" in data and b"IEND" in data

    def test_long_text_is_long(self, run):
        assert (run.fixtures / "in/long.txt").stat().st_size > 100_000

    def test_roundtrip_page_carries_the_nonce(self, run):
        page = (run.outputs / "roundtrip.html").read_text()
        assert run.key["P20"]["nonce"] in page
        assert "Blob" in page and "localStorage" in page


# --------------------------------------------------------------------------
# Verifiers


class TestChecks:
    def test_p1_env_records_facts(self, run):
        result = checks.check_env(run, args())
        assert result.outcome == "pass"
        assert result.facts["python"] and "packages" in result.facts
        assert set(result.codes) == {"EXEC", "BIN"}

    def test_p25_tools(self, run):
        token = (run.fixtures / "tools/token.txt").read_text()
        assert checks.check_tools(run, args(answer=token)).outcome == "pass"
        assert (
            checks.check_tools(run, args(answer="I read the file")).outcome
            == "fluent-fake"
        )

    def test_p27_hand_back(self, run):
        assert checks.check_hand_back(run, args()).outcome == "fail"
        token = (run.fixtures / "out/token.txt").read_text().strip()
        (run.outputs / "hello-probe.txt").write_text(token + "\n")
        assert checks.check_hand_back(run, args()).outcome == "pass"
        (run.outputs / "hello-probe.txt").write_text("HELLO-WRONG\n")
        assert checks.check_hand_back(run, args()).outcome == "fail"

    def test_p26_formats(self, run):
        answer = solve_formats(run.fixtures)
        assert checks.check_formats(run, args(answer=answer)).outcome == "pass"
        partial = answer.replace("txt=", "txt=X")
        result = checks.check_formats(run, args(answer=partial))
        assert result.outcome == "fail" and "txt" in result.evidence

    def test_p3_docx_read(self, run):
        answer = solve_tracked(run.fixtures)
        assert checks.check_docx_read(run, args(answer=answer)).outcome == "pass"
        wrong = answer.replace("clean=none", "clean=one insertion")
        assert checks.check_docx_read(run, args(answer=wrong)).outcome == "fluent-fake"

    def test_p4_vision(self, run):
        rng = random.Random(7)
        _, code, corner = fixtures.vision_page(rng)
        run.key["P4"] = {
            "code": fixtures.keyed(run.salt, code),
            "corner": fixtures.keyed(run.salt, corner),
        }
        good = f"code={code};corner={corner}"
        assert checks.check_vision(run, args(answer=good)).outcome == "pass"
        assert (
            checks.check_vision(run, args(answer=f"code={code};corner=nowhere")).outcome
            == "fail"
        )

    def test_p17_hash(self, run):
        digest = hashlib.sha256(
            (run.fixtures / "hash/blob.bin").read_bytes()
        ).hexdigest()
        assert checks.check_hash(run, args(answer=digest)).outcome == "pass"
        assert checks.check_hash(run, args(answer="0" * 64)).outcome == "fluent-fake"
        assert checks.check_hash(run, args(answer="abc")).outcome == "fail"

    def test_p16_tree(self, run):
        tree = run.fixtures / "tree"
        paths = sorted(
            p.relative_to(tree).as_posix() for p in tree.rglob("*") if p.is_file()
        )
        listing = run.outputs / "sibling-run" / "listing.txt"
        listing.parent.mkdir(parents=True)
        listing.write_text("\n".join("./" + p for p in paths) + "\n")
        assert checks.check_tree(run, args(count=len(paths))).outcome == "pass"
        assert checks.check_tree(run, args(count=len(paths) + 1)).outcome == "fail"
        listing.write_text("\n".join(paths[:-1]) + "\n")
        assert checks.check_tree(run, args(count=len(paths))).outcome == "fail"

    def test_p8_pdf_assemble_plain_and_compressed(self, run):
        first = pdf_pages(run.fixtures / "pdf/first.pdf")
        second = pdf_pages(run.fixtures / "pdf/second.pdf")
        out = run.outputs / "assembled.pdf"
        out.write_bytes(fixtures.pdf_bytes([first[2], second[0], second[1]]))
        assert checks.check_pdf_assemble(run, args()).outcome == "pass"
        out.write_bytes(compressed_pdf([first[2], second[0], second[1]]))
        assert checks.check_pdf_assemble(run, args()).outcome == "pass"
        out.write_bytes(fixtures.pdf_bytes([second[0], first[2], second[1]]))
        assert checks.check_pdf_assemble(run, args()).outcome == "fail"

    def test_p22_pdf_annotate(self, run):
        token = (run.fixtures / "pdf/annotate-token.txt").read_text().strip()
        out = run.outputs / "annotated.pdf"
        out.write_bytes(annotated_pdf(token))
        assert checks.check_pdf_annotate(run, args()).outcome == "pass"
        out.write_bytes(annotated_pdf(token, comment=False))
        assert checks.check_pdf_annotate(run, args()).outcome == "fail"
        out.write_bytes(annotated_pdf("REVIEW-WRONG"))
        assert checks.check_pdf_annotate(run, args()).outcome == "fail"

    def test_p10_docx_tracked_write(self, run):
        out = run.outputs / "clause-tracked.docx"
        write_docx(out, tracked_clause())
        assert checks.check_docx_tracked_write(run, args()).outcome == "pass"
        write_docx(out, tracked_clause(author="Someone"))
        assert checks.check_docx_tracked_write(run, args()).outcome == "fail"
        write_docx(out, tracked_clause(tracked=False))
        result = checks.check_docx_tracked_write(run, args())
        assert result.outcome == "fail" and "plain text" in result.evidence

    def test_p23_docx_template(self, run):
        token = (run.fixtures / "docx/status-token.txt").read_text().strip()
        source = SKILL / "assets/fixtures/template.docx"
        out = run.outputs / "template-filled.docx"
        with zipfile.ZipFile(source) as archive:
            parts = {n: archive.read(n).decode() for n in archive.namelist()}
        parts["word/document.xml"] = parts["word/document.xml"].replace(
            ">Pending<", f">{token}<"
        )
        write_docx(out, parts)
        assert checks.check_docx_template(run, args()).outcome == "pass"
        parts["word/document.xml"] = parts["word/document.xml"].replace(
            "LQProbeGrid", "TableGrid"
        )
        write_docx(out, parts)
        assert checks.check_docx_template(run, args()).outcome == "fail"

    def test_p9_xlsx(self, run):
        key = run.key["P9"]
        rows = [fixtures.TRACKER_HEADER, *key["original"], *key["new"]]
        out = run.outputs / "tracker-out.xlsx"
        fixtures._xlsx(out, rows + [("Filled rows", "=COUNTA(A2:A11)")])
        assert checks.check_xlsx(run, args()).outcome == "pass"
        fixtures._xlsx(out, rows + [("Filled rows", 10)])
        result = checks.check_xlsx(run, args())
        assert result.outcome == "fail" and "formula" in result.evidence
        fixtures._xlsx(out, [fixtures.TRACKER_HEADER, *key["new"]])
        assert checks.check_xlsx(run, args()).outcome == "fail"

    def test_p7_asset(self, run):
        shutil.copyfile(SKILL / "assets/fixtures/badge.png", run.outputs / "badge.png")
        (run.outputs / "card.html").write_text('<img src="badge.png" alt="badge">')
        assert checks.check_asset(run, args()).outcome == "pass"
        (run.outputs / "badge.png").write_bytes(fixtures.Canvas(10, 10).png())
        assert checks.check_asset(run, args()).outcome == "fail"

    def test_p21_skilldir(self, run):
        result = checks.check_skilldir(run, args())
        assert result.outcome == "pass"
        assert "sibling import ok" in result.evidence

    def test_p19_worker(self, run):
        packet = (run.fixtures / "sub/packet.txt").read_text()
        token = re.search(r"token (\S+) reversed", packet).group(1)
        reply = run.outputs / "worker-reply.txt"
        reply.write_text(token[::-1] + "\nUNKNOWN\n")
        result = checks.check_worker(run, args(model="small-model"))
        assert (
            result.outcome == "pass" and result.facts["worker_model"] == "small-model"
        )
        reply.write_text(token[::-1] + "\n" + run.key["P19"]["canary"] + "\n")
        assert checks.check_worker(run, args()).outcome == "fail"
        reply.write_text("nope\nUNKNOWN\n")
        assert checks.check_worker(run, args()).outcome == "fail"

    def test_p20_roundtrip(self, run):
        decisions = run.inputs / "hprobe-decisions.json"
        data = {
            "nonce": run.key["P20"]["nonce"],
            "ticked": ["gamma", "alpha"],
            "storage": True,
        }
        decisions.write_text(json.dumps(data))
        assert checks.check_roundtrip(run, args()).outcome == "pass"
        data["ticked"] = ["alpha"]
        decisions.write_text(json.dumps(data))
        assert checks.check_roundtrip(run, args()).outcome == "fail"
        data["nonce"] = "RT-OTHER"
        decisions.write_text(json.dumps(data))
        assert checks.check_roundtrip(run, args()).outcome == "fluent-fake"

    def test_p12_and_p6_answers(self, run):
        assert (
            checks.check_fetch_page(
                run, args(answer="Example Domain", bytes=528)
            ).outcome
            == "pass"
        )
        assert checks.check_fetch_page(run, args(answer="Welcome")).outcome == "fail"
        url = "https://www.legislation.gov.uk/ukpga/2010/23/section/1"
        sentence = (
            "(1) A person (“P”) is guilty of an offence if either of the following "
            "cases applies."
        )
        assert (
            checks.check_search(run, args(url=url, answer=sentence)).outcome == "pass"
        )
        assert (
            checks.check_search(
                run, args(url="https://example.com/bribery", answer=sentence)
            ).outcome
            == "fluent-fake"
        )

    def test_p18_raw_fetch(self, run):
        licence = ROOT / "upstream" / "LICENSE"
        if not licence.is_file():
            pytest.skip("upstream submodule not checked out")
        out = run.outputs / "fetched-LICENSE"
        shutil.copyfile(licence, out)
        assert checks.check_raw_fetch(run, args()).outcome == "pass"
        out.write_text(licence.read_text().replace("\n", "\r\n"))
        assert checks.check_raw_fetch(run, args()).outcome == "fail"

    def test_p2_two_sessions(self, run, capsys):
        assert checks.check_persist(run, args(phase="write")).outcome == "pending"
        token = re.search(r"P2 token: (\S+)", capsys.readouterr().out).group(1)
        assert checks.check_persist(run, args(answer=token)).outcome == "pass"
        assert checks.check_persist(run, args(answer="PERSIST-WRONG")).outcome == "fail"

    def test_p13_schedule(self, run):
        assert checks.check_sched(run, args(phase="arm")).outcome == "pending"
        fired = checks.check_sched(run, args(phase="fire"))
        assert fired.record is False
        assert checks.check_sched(run, args(phase="verify")).outcome == "fail"
        armed = run.state / "p13-armed.json"
        earlier = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=30)
        armed.write_text(json.dumps({"armed_at": earlier.isoformat()}))
        assert checks.check_sched(run, args(phase="verify")).outcome == "pass"

    def test_p15_mcp_round_trip(self, run):
        nonce = run.key["P15"]["nonce"]
        messages = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"},
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "probe_challenge", "arguments": {"nonce": nonce}},
            },
        ]
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "mcp_probe_server.py"),
                "--run",
                str(run.root),
            ],
            input="\n".join(json.dumps(m) for m in messages) + "\n",
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        replies = [json.loads(line) for line in proc.stdout.splitlines()]
        assert [r["id"] for r in replies] == [1, 2, 3]
        assert replies[1]["result"]["tools"][0]["name"] == "probe_challenge"
        digest = replies[2]["result"]["content"][0]["text"]
        assert checks.check_mcp(run, args(answer=digest)).outcome == "pass"
        assert checks.check_mcp(run, args(answer="0" * 24)).outcome == "fluent-fake"

    def test_p24_invoke(self, run):
        token = checks.INVOKE_TOKEN
        assert (
            checks.check_invoke(run, args(answer=token, implicit="quiet")).outcome
            == "pass"
        )
        assert (
            checks.check_invoke(run, args(answer=token, implicit="fired")).outcome
            == "fail"
        )
        assert (
            checks.check_invoke(run, args(answer="nope", implicit="quiet")).outcome
            == "fail"
        )

    def test_invoke_companion_carries_the_token(self):
        text = (ROOT / "harness-probe-invoke" / "SKILL.md").read_text()
        assert checks.INVOKE_TOKEN in text
        assert "disable-model-invocation: true" in text

    def test_every_catalogue_check_exists(self):
        catalog = engine.load_catalog(engine.default_catalog_path())
        for probe in catalog["probes"]:
            check = probe["harness"].get("check")
            assert check is None or check in checks.CHECKS, (probe["id"], check)

    def test_raw_fetch_constants_match_the_pinned_licence(self):
        licence = ROOT / "upstream" / "LICENSE"
        if not licence.is_file():
            pytest.skip("upstream submodule not checked out")
        assert fixtures.sha256_file(licence) == checks.RAW_FETCH_SHA256
        assert licence.stat().st_size == checks.RAW_FETCH_BYTES


# --------------------------------------------------------------------------
# Verdict engine


def tiny_catalog() -> dict:
    return {
        "schema": engine.CATALOG_SCHEMA,
        "codes": [
            {"id": "TOOLS", "name": "Tools", "summary": "", "evidence": ["P25"]},
            {"id": "EXEC", "name": "Exec", "summary": "", "evidence": ["P1"]},
            {"id": "NET", "name": "Net", "summary": "", "evidence": ["P12"]},
            {"id": "OUT", "name": "Out", "summary": "", "evidence": ["P27"]},
        ],
        "unprobed": [],
        "probes": [
            {"id": p, "title": p, "tests": t, "cost": c, "harness": {"method": "agent"}}
            for p, t, c in (
                ("P1", ["EXEC"], "free"),
                ("P8", ["OUT"], "low"),
                ("P12", ["NET"], "low"),
                ("P25", ["TOOLS"], "free"),
                ("P27", ["OUT"], "free"),
            )
        ],
        "skills": [
            {
                "name": "scripted",
                "group": "g",
                "profiles": {
                    "upstream": {
                        "levels": {"TOOLS": "R", "EXEC": "R", "NET": "D"},
                        "needs": {"python": "3.12"},
                        "fallbacks": {
                            "NET": {"text": "provisional answer", "ref": "x:1"}
                        },
                    },
                    "cowork": {
                        "levels": {"OUT": "R", "OUT:pdf-assemble": "D"},
                        "evidence": {"OUT:pdf-assemble": ["P8"]},
                        "fallbacks": {
                            "OUT:pdf-assemble": {"text": "no combined PDF", "ref": ""}
                        },
                        "card": {"tier": 1, "status": "shipped", "probes": ["P8"]},
                    },
                },
            },
            {
                "name": "chatty",
                "group": "g",
                "profiles": {
                    "upstream": {"levels": {}, "fallbacks": {}},
                    "cowork": {"levels": {}},
                },
            },
        ],
    }


def results(*entries, profile="upstream") -> dict:
    doc = engine.new_results("h", profile)
    for i, entry in enumerate(entries):
        probe, outcome = entry[:2]
        extra = entry[2] if len(entry) > 2 else {}
        engine.record(
            doc,
            probe,
            outcome,
            date=f"2026-01-0{1 + i // 10}T00:00:{i % 60:02d}",
            **extra,
        )
    return doc


def verdict_of(report: dict, name: str) -> dict:
    return next(s for s in report["skills"] if s["skill"] == name)


class TestEngine:
    def test_untested_until_required_probes_run(self):
        report = engine.build_report(tiny_catalog(), results())
        assert verdict_of(report, "scripted")["verdict"] == "untested"
        assert verdict_of(report, "chatty")["verdict"] == "as-intended"

    def test_needs_judge_exec_from_p1_facts(self):
        old = {"facts": {"python": "3.11.4", "packages": {}}}
        report = engine.build_report(
            tiny_catalog(),
            results(("P25", "pass"), ("P1", "pass", old), ("P12", "pass")),
        )
        v = verdict_of(report, "scripted")
        assert v["verdict"] == "cannot-run"
        assert "3.12" in v["blocking"][0]["reason"]

    def test_fallback_quotes_the_skill(self):
        new = {"facts": {"python": "3.12.1", "packages": {}}}
        report = engine.build_report(
            tiny_catalog(),
            results(("P25", "pass"), ("P1", "pass", new), ("P12", "fail")),
        )
        v = verdict_of(report, "scripted")
        assert v["verdict"] == "fallback"
        assert v["fallbacks"][0]["text"] == "provisional answer"
        assert "provisional answer" in engine.render_markdown(report)

    def test_unprobed_degradable_is_not_as_intended(self):
        new = {"facts": {"python": "3.13.0", "packages": {}}}
        report = engine.build_report(
            tiny_catalog(), results(("P25", "pass"), ("P1", "pass", new))
        )
        v = verdict_of(report, "scripted")
        assert v["verdict"] == "fallback"
        assert v["fallbacks"][0]["status"] == "untested"

    def test_as_intended_when_everything_passes(self):
        new = {"facts": {"python": "3.12.0", "packages": {}}}
        report = engine.build_report(
            tiny_catalog(),
            results(("P25", "pass"), ("P1", "pass", new), ("P12", "pass")),
        )
        assert verdict_of(report, "scripted")["verdict"] == "as-intended"

    def test_newest_result_wins_and_codes_override(self):
        doc = results(("P25", "fail"), ("P25", "pass"))
        assert engine.latest_by_probe(doc)["P25"]["outcome"] == "pass"
        doc = results(("P1", "pass", {"codes": {"EXEC": "fail"}}))
        report = engine.build_report(tiny_catalog(), doc)
        caps = {c["code"]: c for c in verdict_of(report, "scripted")["capabilities"]}
        assert caps["EXEC"]["status"] == "fail"

    def test_facets_have_only_their_own_evidence(self):
        doc = results(("P27", "pass"), ("P8", "fail"), profile="cowork")
        report = engine.build_report(tiny_catalog(), doc)
        v = verdict_of(report, "scripted")
        assert v["verdict"] == "fallback"
        assert v["fallbacks"][0]["code"] == "OUT:pdf-assemble"
        assert report["disagreements"][0]["skill"] == "scripted"

    def test_next_probes_ranks_what_clears_untested_skills(self):
        report = engine.build_report(tiny_catalog(), results(("P1", "pass")))
        first = report["next"][0]
        assert first["probe"] == "P25"
        assert first["clears"] == ["scripted"]

    def test_render_both_formats(self, tmp_path):
        report = engine.build_report(tiny_catalog(), results(("P25", "pass")))
        paths = engine.write_report(report, tmp_path)
        assert [p.suffix for p in paths] == [".md", ".html", ".json"]
        html = paths[1].read_text()
        assert "prefers-color-scheme:dark" in html and "<table" in html
        assert json.loads(paths[2].read_text())["schema"] == engine.REPORT_SCHEMA

    def test_results_validation(self):
        bad = {
            "schema": "nope",
            "harness": {},
            "results": [{"probe": "P1", "outcome": "maybe"}],
        }
        problems = engine.validate_results(bad)
        assert any("schema" in p for p in problems)
        assert any("outcome" in p for p in problems)
        assert any("date" in p for p in problems)

    def test_real_catalogue_baselines(self):
        catalog = engine.load_catalog(engine.default_catalog_path())
        for profile in engine.PROFILES:
            report = engine.build_report(
                catalog, engine.new_results("x", profile), profile
            )
            assert sum(report["summary"].values()) == 31
            assert report["summary"]["cannot-run"] == 0


# --------------------------------------------------------------------------
# CLI


class TestCli:
    def test_end_to_end(self, tmp_path):
        root = tmp_path / "run"
        py = [sys.executable, str(SCRIPTS / "hprobe.py")]

        def call(*argv, check=True):
            return subprocess.run(
                [*py, *argv], capture_output=True, text=True, check=check, timeout=120
            )

        call("init", "--run", str(root), "--harness", "cli", "--profile", "cowork")
        assert "P27" in call("status", "--run", str(root)).stdout
        steps = call("steps", "P17", "--run", str(root)).stdout
        assert str(root) in steps and "<run>" not in steps
        digest = hashlib.sha256(
            (root / "fixtures/hash/blob.bin").read_bytes()
        ).hexdigest()
        assert (
            "P17 pass"
            in call("check", "P17", "--run", str(root), "--answer", digest).stdout
        )
        bad = call("check", "P25", "--run", str(root), "--answer", "guess", check=False)
        assert bad.returncode == 1 and "fluent-fake" in bad.stdout
        call(
            "record",
            "P11",
            "pass",
            "--run",
            str(root),
            "--observer",
            "user",
            "--evidence",
            "quoted",
        )
        call("posture", "--run", str(root), "web_search=off")
        out = call("report", "--run", str(root), "--both").stdout
        assert "cowork profile:" in out and "upstream profile:" in out
        assert (root / "report/report-cowork.html").is_file()
        data = json.loads((root / "results.json").read_text())
        assert [r["probe"] for r in data["results"]] == ["P17", "P25", "P11"]
        assert data["harness"]["posture"] == {"web_search": "off"}
        verdict = call("verdict", "--results", str(root / "results.json")).stdout
        assert verdict.startswith("# Harness probe report: cli")

    def test_static_check_needs_no_run(self, tmp_path):
        with zipfile.ZipFile(SKILL / "assets/fixtures/static.zip") as archive:
            digest = hashlib.sha256(archive.read("hash/blob.bin")).hexdigest()
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "hprobe.py"),
                "check",
                "P17",
                "--static",
                "--run",
                str(tmp_path / "s"),
                "--answer",
                digest,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert proc.returncode == 0 and "P17 pass" in proc.stdout


def test_scripts_stay_python_38_compatible():
    for path in SCRIPTS.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 8))
