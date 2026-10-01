"""capabilities.yaml, the catalogue, the chart and the verdicts (contract 4b).

The fixture repository gains a small ``capabilities.yaml`` for its three
skills and a copy of the real harness-probe skill; each test then breaks one
thing to provoke one rule.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import pytest
import yaml

from lqcowork.build import check_cards
from lqcowork.config import load_card, load_cards, load_config, upstream_skill_names
from lqcowork.harness import (
    CATALOG_REL,
    PROBES_MD_REL,
    build_report_lines,
    check_capabilities,
    derive_unlocks,
    derived_tools,
    harness_reports,
    load_capabilities,
    matrix_markdown,
    render_chart,
    write_catalog,
    write_chart,
)

PROBES = """probes:
  - id: P3
    title: Does Cowork report tracked changes in a Word document?
    settles: Whether tracked changes are visible at all.
    setup: A synthetic DOCX with tracked insertions and deletions.
    prompt: List every tracked change in this agreement.
    pass: Insertions and deletions listed separately with authors.
    fail: It reports no changes.
    bad_outcome: silent
    tests: [IN, DOCX]
    cost: low
    harness:
      method: agent
      check: docx-read
      steps: Read the file.
  - id: P25
    title: Does a tool call actually execute?
    settles: Whether tools run.
    prompt: Read the file with a tool.
    pass: The exact contents.
    fail: Anything else.
    bad_outcome: fluent-fake
    tests: [TOOLS, OUT]
    cost: free
    harness:
      method: agent
      check: tools
      steps: Read the token.
"""

CAPABILITIES = """codes:
  - {id: TOOLS, name: Tool execution, summary: Tools run., evidence: [P25]}
  - {id: IN, name: Read supplied files, summary: Files are read., evidence: [P3]}
  - {id: OUT, name: Hand back files, summary: Files go back., evidence: [P25]}
  - {id: DOCX, name: Word structure, summary: Tracked changes., evidence: [P3]}
unprobed: []
skills:
  alpha:
    group: core
    upstream:
      levels: {TOOLS: R, IN: R, OUT: R}
      fallbacks: {}
    cowork:
      levels: {TOOLS: D, IN: R, DOCX: D}
      fallbacks:
        DOCX: {text: "Tracked changes are named as unseen.", ref: "skills/alpha/skill.yaml"}
  beta:
    group: core
    upstream:
      levels: {}
      fallbacks: {}
    cowork:
      levels: {}
      fallbacks: {}
  gamma:
    group: extra
    upstream:
      levels: {TOOLS: O, OUT: O}
      fallbacks: {}
    cowork:
      levels: {}
      fallbacks: {}
"""

ROOT = Path(__file__).resolve().parents[2]


def install(repo: Path) -> Path:
    (repo / "probes.yaml").write_text(PROBES, encoding="utf-8")
    (repo / "capabilities.yaml").write_text(CAPABILITIES, encoding="utf-8")
    for name in ("harness-probe", "harness-probe-invoke"):
        shutil.copytree(
            ROOT / name, repo / name, ignore=shutil.ignore_patterns("__pycache__")
        )
    config = load_config(repo)
    write_catalog(config, load_capabilities(repo))
    return repo


@pytest.fixture
def repo(fixture_repo: Path) -> Path:
    return install(fixture_repo)


def codes(repo: Path) -> list[str]:
    config = load_config(repo)
    cards = load_cards(config, ["alpha", "beta", "gamma"])
    errors, _ = check_capabilities(config, load_capabilities(repo), cards)
    return [e.code for e in errors]


def edit_caps(repo: Path, change) -> None:
    path = repo / "capabilities.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    config = load_config(repo)
    write_catalog(config, load_capabilities(repo))


class TestRules:
    def test_clean_fixture_passes(self, repo):
        assert codes(repo) == []

    def test_check_cards_runs_the_capability_rules(self, repo):
        config = load_config(repo)
        cards = load_cards(config, ["alpha", "beta", "gamma"])
        edit_caps(
            repo, lambda d: d["skills"]["alpha"]["upstream"]["levels"].update(TOOLS="O")
        )
        errors, _ = check_cards(load_config(repo), cards)
        assert "LQC-K006" in [e.code for e in errors]

    def test_tools_must_match_the_strongest_action_code(self, repo):
        edit_caps(
            repo, lambda d: d["skills"]["alpha"]["upstream"]["levels"].update(TOOLS="D")
        )
        assert "LQC-K006" in codes(repo)

    def test_degradable_needs_fallback_wording(self, repo):
        edit_caps(repo, lambda d: d["skills"]["alpha"]["cowork"].update(fallbacks={}))
        assert "LQC-K006" in codes(repo)

    def test_unknown_code_and_level(self, repo):
        edit_caps(
            repo, lambda d: d["skills"]["beta"]["upstream"]["levels"].update(WIFI="Q")
        )
        assert codes(repo).count("LQC-K004") >= 2

    def test_facet_needs_evidence(self, repo):
        def change(d):
            d["skills"]["gamma"]["upstream"]["levels"]["OUT:pdf-assemble"] = "O"

        edit_caps(repo, change)
        assert "LQC-K004" in codes(repo)

    def test_untested_code_without_reason(self, repo):
        def change(d):
            d["codes"].append(
                {"id": "SUB", "name": "Workers", "summary": "s", "evidence": []}
            )

        edit_caps(repo, change)
        assert "LQC-K005" in codes(repo)

        def explain(d):
            d["unprobed"] = [{"code": "SUB", "reason": "no harness offers it yet"}]

        edit_caps(repo, explain)
        assert "LQC-K005" not in codes(repo)

    def test_card_citing_a_probe_it_does_not_rate(self, repo):
        edit_caps(
            repo,
            lambda d: d["skills"]["alpha"]["cowork"].update(levels={}, fallbacks={}),
        )
        assert "LQC-K006" in codes(repo)

    def test_declared_unlocks_is_refused(self, repo):
        path = repo / "probes.yaml"
        path.write_text(
            path.read_text().replace(
                "    cost: low\n", "    cost: low\n    unlocks: [alpha]\n"
            ),
            encoding="utf-8",
        )
        assert "LQC-K004" in codes(repo)

    def test_stale_catalogue(self, repo):
        (repo / CATALOG_REL).write_text("{}\n", encoding="utf-8")
        assert "LQC-K008" in codes(repo)

    def test_bad_results_file(self, repo):
        folder = repo / "probe-results"
        folder.mkdir()
        (folder / "bad.json").write_text(
            json.dumps(
                {
                    "schema": "lq-harness-probe-results/1",
                    "harness": {"name": "h", "profile": "upstream"},
                    "results": [
                        {"probe": "P99", "outcome": "pass", "date": "2026-01-01"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        assert "LQC-K007" in codes(repo)


class TestDerived:
    def test_unlocks_come_from_the_cowork_profile(self, repo):
        config = load_config(repo)
        assert config.probe("P3").unlocks == ("alpha",)  # IN is required
        assert config.probe("P25").unlocks == ("alpha",)  # TOOLS is degradable
        edit_caps(
            repo, lambda d: d["skills"]["alpha"]["cowork"]["levels"].update(TOOLS="O")
        )
        assert load_config(repo).probe("P25").unlocks == ()

    def test_derived_tools(self):
        assert derived_tools({"IN": "R"}) is None
        assert derived_tools({"IN": "R", "OUT": "D", "OUT:pdf-assemble": "R"}) == "R"

    def test_catalogue_and_probes_md(self, repo):
        catalog = json.loads((repo / CATALOG_REL).read_text())
        assert catalog["schema"] == "lq-harness-probe-catalog/1"
        alpha = next(s for s in catalog["skills"] if s["name"] == "alpha")
        assert alpha["profiles"]["cowork"]["card"]["status"] == "probe-gated"
        assert (
            "## P25: Does a tool call actually execute?"
            in (repo / PROBES_MD_REL).read_text()
        )

    def test_chart_markers(self, repo):
        caps = load_capabilities(repo)
        text = (
            "intro\n<!-- gen:matrix-upstream -->\n<!-- /gen:matrix-upstream -->\nend\n"
        )
        out = render_chart(text, caps)
        assert "| alpha | ● |" in out and out.endswith("end\n")
        assert render_chart(out, caps) == out

    def test_reports_and_build_lines(self, repo):
        folder = repo / "probe-results"
        folder.mkdir()
        (folder / "lab.json").write_text(
            json.dumps(
                {
                    "schema": "lq-harness-probe-results/1",
                    "harness": {"name": "Lab harness", "profile": "upstream"},
                    "results": [
                        {
                            "probe": "P25",
                            "outcome": "pass",
                            "date": "2026-01-01",
                            "observer": "script",
                        },
                        {
                            "probe": "P3",
                            "outcome": "fail",
                            "date": "2026-01-01",
                            "observer": "script",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        config = load_config(repo)
        reports = harness_reports(config, load_capabilities(repo))
        assert [r.slug for r in reports] == [
            "baseline-upstream",
            "baseline-cowork",
            "lab",
        ]
        lab = reports[-1].report
        alpha = next(s for s in lab["skills"] if s["skill"] == "alpha")
        assert alpha["verdict"] == "cannot-run"
        lines = "\n".join(build_report_lines(reports))
        assert "## Harness verdicts" in lines and "Lab harness" in lines


class TestPipeline:
    def test_package_writes_the_harness_archives_and_report(self, repo, monkeypatch):
        from lqcowork.cli import main

        monkeypatch.chdir(repo)
        assert main(["package"]) == 0
        archive = repo / "dist" / "harness" / "harness-probe.skill"
        with zipfile.ZipFile(archive) as z:
            names = z.namelist()
        assert "SKILL.md" in names and "scripts/hprobe.py" in names
        assert "data/catalog.json" in names and "LICENSE" in names
        assert not any("__pycache__" in n for n in names)
        companions = [n for n in names if n not in ("SKILL.md", "LICENSE")]
        assert len(companions) <= 20, "Cowork's Upload skill takes 20 companion files"
        assert (repo / "dist" / "harness" / "harness-probe-invoke.skill").is_file()
        assert "## Harness verdicts" in (repo / "dist" / "build-report.md").read_text()

    def test_site_renders_verdicts(self, repo, monkeypatch):
        from lqcowork.cli import main

        monkeypatch.chdir(repo)
        assert main(["package"]) == 0
        assert main(["site"]) == 0
        page = (repo / "dist" / "site" / "verdicts.html").read_text()
        assert "no results (upstream)" in page and "Probe coverage" in page
        probes = (repo / "dist" / "site" / "probes.html").read_text()
        assert "IN DOCX" in probes and "harness-probe" in probes


class TestRealRepository:
    def test_every_upstream_skill_is_rated(self, real_root):
        config = load_config(real_root)
        caps = load_capabilities(real_root)
        assert set(caps.skills) == set(upstream_skill_names(config))

    def test_rules_pass(self, real_root):
        config = load_config(real_root)
        caps = load_capabilities(real_root)
        cards = {n: load_card(config, n) for n in caps.skills}
        errors, _ = check_capabilities(config, caps, cards)
        assert [e.render() for e in errors] == []

    def test_generated_files_are_current(self, real_root):
        config = load_config(real_root)
        caps = load_capabilities(real_root)
        assert write_catalog(config, caps, check=True), "run `make catalog`"
        assert write_chart(config, caps, check=True), "run `make chart`"

    def test_unlocks_are_derived(self, real_root):
        config = load_config(real_root)
        derived = derive_unlocks(load_capabilities(real_root), config.probes)
        for probe in config.probes:
            assert probe.unlocks == derived[probe.id]
        assert "read-redline" in config.probe("P3").unlocks

    def test_matrix_has_every_skill(self, real_root):
        text = matrix_markdown(load_capabilities(real_root), "upstream")
        assert text.count("\n| ") == 31 + 4

    def test_issue_form_lists_every_probe(self, real_root):
        form = yaml.safe_load(
            (real_root / ".github/ISSUE_TEMPLATE/probe-report.yml").read_text()
        )
        probe_field = next(b for b in form["body"] if b.get("id") == "probe")
        ids = [opt.split(":", 1)[0] for opt in probe_field["attributes"]["options"]]
        assert ids == [p.id for p in load_config(real_root).probes]

    def test_committed_results_validate(self, real_root):
        reports = harness_reports(load_config(real_root), load_capabilities(real_root))
        assert len(reports) >= 2
        for item in reports:
            assert sum(item.report["summary"].values()) == 31
