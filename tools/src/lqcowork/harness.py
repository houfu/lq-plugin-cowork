"""capabilities.yaml, the harness-probe catalogue, the chart matrix and verdicts.

The verdict logic itself lives in the harness-probe skill
(``harness-probe/scripts/hprobe_engine.py``), so the skill a tester runs and
the site this repository publishes can never disagree. This module loads it,
feeds it the repository's data, and owns everything that needs PyYAML:

- loading and validating ``capabilities.yaml`` (LQC-K004 to LQC-K006);
- writing ``harness-probe/data/catalog.json`` from ``probes.yaml``,
  ``capabilities.yaml`` and the cards (``lqcowork catalog``);
- regenerating the matrices in docs/research/harness-capability-chart.md
  (``lqcowork chart``);
- loading ``probe-results/*.json`` and building one report per results file
  for the build report and the site.

See docs/CONTRACT.md section 4b.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from .build import Issue
from .config import PROBES_NAME, Card, Config, ConfigError, Probe, load_card

CAPABILITIES_NAME = "capabilities.yaml"
HARNESS_DIR = "harness-probe"
CATALOG_REL = f"{HARNESS_DIR}/data/catalog.json"
PROBES_MD_REL = f"{HARNESS_DIR}/references/probes.md"
ENGINE_REL = f"{HARNESS_DIR}/scripts/hprobe_engine.py"
RESULTS_DIR = "probe-results"
CHART_REL = "docs/research/harness-capability-chart.md"

LEVELS = ("R", "D", "O")
LEVEL_SYMBOL = {"R": "●", "D": "◐", "O": "○"}
RANK = {"R": 3, "D": 2, "O": 1}
PROFILES = ("upstream", "cowork")
# Codes whose use goes through a tool call; TOOLS is the strongest of them.
ACTION_CODES = (
    "OUT",
    "FS",
    "PERSIST",
    "EXEC",
    "BIN",
    "NET",
    "SEARCH",
    "VISION",
    "DOCX",
    "SUB",
    "SESSION",
    "SCHED",
    "MCP",
    "HASH",
    "SKILLDIR",
)
CODE_RE = re.compile(r"^[A-Z]+(:[a-z0-9-]+)?$")


@dataclass(frozen=True)
class Capabilities:
    path: Path
    codes: tuple[dict[str, Any], ...]
    unprobed: tuple[dict[str, Any], ...]
    skills: dict[str, dict[str, Any]]

    @property
    def code_ids(self) -> list[str]:
        return [c["id"] for c in self.codes]

    def column_codes(self) -> list[str]:
        return [c["id"] for c in self.codes if c.get("column", True)]


def capabilities_path(root: Path) -> Path:
    return root / CAPABILITIES_NAME


def load_capabilities(root: Path) -> Capabilities | None:
    """Parse ``capabilities.yaml``; ``None`` when the file does not exist."""
    path = capabilities_path(root)
    if not path.is_file():
        return None
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{CAPABILITIES_NAME}: invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{CAPABILITIES_NAME}: expected a top-level mapping")
    codes = raw.get("codes")
    skills = raw.get("skills")
    if not isinstance(codes, list) or not all(isinstance(c, dict) for c in codes):
        raise ConfigError(f"{CAPABILITIES_NAME}.codes: expected a list of mappings")
    if not isinstance(skills, dict):
        raise ConfigError(f"{CAPABILITIES_NAME}.skills: expected a mapping")
    for index, code in enumerate(codes):
        for key in ("id", "name", "summary"):
            if not isinstance(code.get(key), str):
                raise ConfigError(f"{CAPABILITIES_NAME}.codes[{index}].{key}: required")
    return Capabilities(
        path=path,
        codes=tuple(codes),
        unprobed=tuple(raw.get("unprobed") or ()),
        skills=skills,
    )


def base_code(key: str) -> str:
    return key.split(":", 1)[0]


def derived_tools(levels: dict[str, str]) -> str | None:
    best = 0
    for key, level in levels.items():
        if base_code(key) in ACTION_CODES and level in RANK:
            best = max(best, RANK[level])
    return {3: "R", 2: "D", 1: "O"}.get(best)


def column_levels(levels: dict[str, str]) -> dict[str, str]:
    """Collapse facets onto their base code, keeping the strongest level."""
    out: dict[str, str] = {}
    for key, level in levels.items():
        code = base_code(key)
        if code not in out or RANK[level] > RANK[out[code]]:
            out[code] = level
    return out


def derive_unlocks(
    caps: Capabilities, probes: tuple[Probe, ...], profile: str = "cowork"
) -> dict[str, tuple[str, ...]]:
    """probe id -> skills whose required or degradable levels it decides."""
    primary = {c["id"]: list(c.get("evidence") or []) for c in caps.codes}
    out: dict[str, set[str]] = {p.id: set() for p in probes}
    for name, skill in caps.skills.items():
        block = (skill or {}).get(profile) or {}
        extra = block.get("evidence") or {}
        for key, level in (block.get("levels") or {}).items():
            if level not in ("R", "D"):
                continue
            for probe_id in primary.get(key, []) + list(extra.get(key) or []):
                out.setdefault(probe_id, set()).add(name)
    return {k: tuple(sorted(v)) for k, v in out.items()}


# --------------------------------------------------------------------------
# Validation


def check_capabilities(
    config: Config, caps: Capabilities | None, cards: dict[str, Card]
) -> tuple[list[Issue], list[Issue]]:
    """LQC-K004 (shape), LQC-K005 (coverage) and LQC-K006 (consistency)."""
    errors: list[Issue] = []
    warnings: list[Issue] = []
    if caps is None:
        return errors, warnings
    probe_ids = config.probe_ids
    codes = set(caps.code_ids)
    where = CAPABILITIES_NAME

    def err(code: str, message: str, skill: str | None = None) -> None:
        errors.append(Issue(code, message, skill=skill))

    for code in caps.codes:
        for probe_id in code.get("evidence") or []:
            if probe_id not in probe_ids:
                err(
                    "LQC-K004",
                    f"{where}: code {code['id']} names evidence probe '{probe_id}', "
                    f"which {PROBES_NAME} does not define",
                )
    for probe in config.probes:
        unknown = [t for t in probe.tests if t not in codes]
        if unknown:
            err(
                "LQC-K004",
                f"{PROBES_NAME}: {probe.id} tests unknown code(s) {', '.join(unknown)}",
            )
        if not probe.tests:
            err("LQC-K004", f"{PROBES_NAME}: {probe.id} has no `tests` codes")
        if probe.declares_unlocks:
            err(
                "LQC-K004",
                f"{PROBES_NAME}: {probe.id} still declares `unlocks`; with "
                f"{CAPABILITIES_NAME} present it is derived, so remove it",
            )
        check = (probe.harness or {}).get("check")
        if not probe.harness:
            err("LQC-K004", f"{PROBES_NAME}: {probe.id} has no `harness` block")
        elif check is not None and not isinstance(check, str):
            err("LQC-K004", f"{PROBES_NAME}: {probe.id}.harness.check must be a string")

    # LQC-K005: every code is tested by a probe, or deliberately unprobed.
    tested = {t for p in config.probes for t in p.tests}
    unprobed = {u.get("code") for u in caps.unprobed}
    for code in caps.code_ids:
        if code not in tested and code not in unprobed:
            err(
                "LQC-K005",
                f"capability {code} is tested by no probe and is not listed under "
                "`unprobed` with a reason",
            )
        if code in tested and code in unprobed:
            warnings.append(
                Issue(
                    "LQC-K005",
                    f"capability {code} is listed as unprobed, but a probe tests it",
                )
            )

    for name in sorted(cards):
        if name not in caps.skills:
            err("LQC-K004", f"{where}: no capability levels for this skill", name)
    for name, skill in caps.skills.items():
        if not isinstance(skill, dict):
            err("LQC-K004", f"{where}: skill {name} must be a mapping", name)
            continue
        for profile in PROFILES:
            block = skill.get(profile)
            if not isinstance(block, dict):
                err("LQC-K004", f"{where}: {name}.{profile} is missing", name)
                continue
            levels = block.get("levels") or {}
            evidence = block.get("evidence") or {}
            fallbacks = block.get("fallbacks") or {}
            for key, level in levels.items():
                if not CODE_RE.match(str(key)) or base_code(key) not in codes:
                    err("LQC-K004", f"{name}.{profile}: unknown code '{key}'", name)
                if level not in LEVELS:
                    err(
                        "LQC-K004",
                        f"{name}.{profile}.{key}: level must be R, D or O, got {level!r}",
                        name,
                    )
                if ":" in str(key) and not evidence.get(key):
                    err(
                        "LQC-K004",
                        f"{name}.{profile}: facet {key} has no evidence probes",
                        name,
                    )
                if level == "D" and key != "TOOLS" and key not in fallbacks:
                    err(
                        "LQC-K006",
                        f"{name}.{profile}: {key} is degradable but has no fallback wording",
                        name,
                    )
            for key, probes in evidence.items():
                for probe_id in probes or []:
                    if probe_id not in probe_ids:
                        err(
                            "LQC-K004",
                            f"{name}.{profile}.evidence.{key}: unknown probe {probe_id}",
                            name,
                        )
            want = derived_tools(levels)
            if levels.get("TOOLS") != want:
                err(
                    "LQC-K006",
                    f"{name}.{profile}: TOOLS is {levels.get('TOOLS')!r} but the "
                    f"strongest action code makes it {want!r}",
                    name,
                )

    # A card that cites a probe must rate something that probe tests.
    for name, card in sorted(cards.items()):
        skill = caps.skills.get(name) or {}
        cowork = (skill.get("cowork") or {}).get("levels") or {}
        rated = {base_code(k) for k in cowork}
        for known in card.known_issues:
            if not known.probe:
                continue
            probe = config.probe(known.probe)
            if probe is None or not probe.tests:
                continue
            if not set(probe.tests) & rated:
                err(
                    "LQC-K006",
                    f"known issue {known.id} cites {known.probe}, which tests "
                    f"{', '.join(probe.tests)}; the card's cowork profile rates none of "
                    "them",
                    name,
                )
    # LQC-K008: generated files must match their sources.
    if not write_catalog(config, caps, check=True):
        err(
            "LQC-K008",
            f"{CATALOG_REL} is out of date with {PROBES_NAME} and {CAPABILITIES_NAME}; "
            "run `lqcowork catalog`",
        )
    if not write_chart(config, caps, check=True):
        err(
            "LQC-K008",
            f"{CHART_REL} matrices are out of date with {CAPABILITIES_NAME}; "
            "run `lqcowork chart`",
        )
    errors += check_results(config)
    return errors, warnings


# --------------------------------------------------------------------------
# Catalogue


def _card_summary(card: Card | None) -> dict[str, Any] | None:
    if card is None or card.cowork is None:
        return None
    return {
        "tier": card.cowork.tier,
        "status": card.cowork.status,
        "probes": list(card.cowork.probes),
    }


def build_catalog(config: Config, caps: Capabilities) -> dict[str, Any]:
    cards: dict[str, Card] = {}
    for name in caps.skills:
        try:
            cards[name] = load_card(config, name)
        except ConfigError:
            continue
    probes = []
    for probe in config.probes:
        harness = dict(probe.harness or {})
        if "steps" in harness:
            harness["steps"] = " ".join(str(harness["steps"]).split())
        probes.append(
            {
                "id": probe.id,
                "title": probe.title,
                "settles": " ".join(probe.settles.split()),
                "tests": list(probe.tests),
                "cost": probe.cost or "low",
                "harness": harness,
                "cowork": {
                    "setup": " ".join((probe.setup or "").split()),
                    "prompt": probe.prompt,
                    "pass": " ".join(probe.passes.split()),
                    "fail": " ".join(probe.fails.split()),
                    "bad_outcome": probe.bad_outcome,
                },
            }
        )
    skills = []
    for name, skill in caps.skills.items():
        profiles: dict[str, Any] = {}
        for profile in PROFILES:
            block = dict(skill.get(profile) or {})
            out: dict[str, Any] = {
                "levels": dict(block.get("levels") or {}),
                "evidence": {
                    k: list(v) for k, v in (block.get("evidence") or {}).items()
                },
                "fallbacks": dict(block.get("fallbacks") or {}),
            }
            if block.get("needs"):
                out["needs"] = block["needs"]
            if block.get("notes"):
                out["notes"] = block["notes"]
            if profile == "cowork":
                summary = _card_summary(cards.get(name))
                if summary:
                    out["card"] = summary
            profiles[profile] = out
        skills.append(
            {"name": name, "group": skill.get("group", ""), "profiles": profiles}
        )
    codes = []
    for code in caps.codes:
        codes.append(
            {
                "id": code["id"],
                "name": code["name"],
                "label": code.get("label") or code["name"],
                "summary": code["summary"],
                "evidence": list(code.get("evidence") or []),
                "column": bool(code.get("column", True)),
            }
        )
    return {
        "schema": "lq-harness-probe-catalog/1",
        "source": {
            "upstream": f"LegalQuants/lq-plugin-oss@{config.sha7}",
            "package": config.version,
        },
        "codes": codes,
        "unprobed": [dict(u) for u in caps.unprobed],
        "probes": probes,
        "skills": skills,
    }


def probes_markdown(catalog: dict[str, Any]) -> str:
    """harness-probe/references/probes.md: every probe, as the agent runs it."""
    lines = [
        "# The probes",
        "",
        "Generated from `probes.yaml` by `lqcowork catalog`; do not edit by hand.",
        "`<run>` is the run folder and `<skill>` this skill's folder;",
        "`hprobe.py steps <probe> --run <run>` prints the steps with both filled in.",
        "",
        "| Probe | Tests | Method | Cost | Question |",
        "|---|---|---|---|---|",
    ]
    for probe in catalog["probes"]:
        harness = probe.get("harness") or {}
        lines.append(
            f"| {probe['id']} | {' '.join(probe['tests'])} | {harness.get('method', '')} | "
            f"{probe['cost']} | {probe['title']} |"
        )
    lines.append("")
    for probe in catalog["probes"]:
        harness = probe.get("harness") or {}
        lines += [
            f"## {probe['id']}: {probe['title']}",
            "",
            f"Tests {', '.join(probe['tests'])}. Method {harness.get('method')}; cost "
            f"{probe['cost']}; checked by "
            + (
                f"`hprobe.py check {probe['id']}`."
                if harness.get("check")
                else "observation."
            )
            + "",
            "",
            probe["settles"],
            "",
            "**Steps.** " + str(harness.get("steps", "")),
            "",
            f"**Worst outcome to watch for:** {probe['cowork']['bad_outcome']}.",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def write_catalog(config: Config, caps: Capabilities, *, check: bool = False) -> bool:
    """Write the catalogue and probes.md; with ``check``, only report staleness."""
    catalog = build_catalog(config, caps)
    outputs = {
        config.root / CATALOG_REL: json.dumps(catalog, indent=2, ensure_ascii=False)
        + "\n",
        config.root / PROBES_MD_REL: probes_markdown(catalog),
    }
    if check:
        return all(
            path.is_file() and path.read_text(encoding="utf-8") == text
            for path, text in outputs.items()
        )
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return True


# --------------------------------------------------------------------------
# Chart matrices


GROUP_ORDER = ("core", "companion", "litigation", "transactional")


def matrix_markdown(caps: Capabilities, profile: str) -> str:
    columns = caps.column_codes()
    lines = [
        "| Skill | " + " | ".join(columns) + " |",
        "|---|" + "---|" * len(columns),
    ]
    groups: dict[str, list[str]] = {}
    for name, skill in caps.skills.items():
        groups.setdefault(skill.get("group", ""), []).append(name)
    order = [g for g in GROUP_ORDER if g in groups] + sorted(
        g for g in groups if g not in GROUP_ORDER
    )
    for group in order:
        lines.append(f"| **{group}** |" + " |" * len(columns))
        for name in sorted(groups[group]):
            levels = column_levels(
                (caps.skills[name].get(profile) or {}).get("levels") or {}
            )
            cells = [LEVEL_SYMBOL.get(levels.get(c, ""), "") for c in columns]
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def aux_markdown(caps: Capabilities, profile: str) -> str:
    aux = [c["id"] for c in caps.codes if not c.get("column", True)]
    rows = []
    for name in sorted(caps.skills):
        levels = (caps.skills[name].get(profile) or {}).get("levels") or {}
        cells = []
        for code in aux:
            keys = [k for k in levels if base_code(k) == code]
            cells.append(
                ", ".join(
                    f"{LEVEL_SYMBOL[levels[k]]}{'' if k == code else ' ' + k.split(':', 1)[1]}"
                    for k in keys
                )
            )
        if any(cells):
            rows.append(f"| {name} | " + " | ".join(cells) + " |")
    head = ["| Skill | " + " | ".join(aux) + " |", "|---|" + "---|" * len(aux)]
    return "\n".join(head + rows)


def facet_markdown(caps: Capabilities, profile: str) -> str:
    rows = []
    for name in sorted(caps.skills):
        block = caps.skills[name].get(profile) or {}
        for key, level in (block.get("levels") or {}).items():
            if ":" not in key or base_code(key) not in caps.column_codes():
                continue
            probes = ", ".join((block.get("evidence") or {}).get(key) or [])
            rows.append(f"| {name} | `{key}` | {LEVEL_SYMBOL[level]} | {probes} |")
    if not rows:
        return "No facets."
    return "\n".join(["| Skill | Facet | Level | Probes |", "|---|---|---|---|"] + rows)


def counts_markdown(caps: Capabilities, profile: str) -> str:
    tools = {"R": 0, "D": 0, "O": 0}
    none_required = []
    for name, skill in caps.skills.items():
        levels = (skill.get(profile) or {}).get("levels") or {}
        if levels.get("TOOLS") in tools:
            tools[levels["TOOLS"]] += 1
        if "R" not in levels.values():
            none_required.append(name)
    return (
        f"{len(none_required)} skills have no ● at all and run on the baseline alone, in "
        f"their documented degraded form where they have ◐ items: "
        f"{', '.join(sorted(none_required)) or 'none'}. TOOLS is ● for {tools['R']} "
        f"skills, ◐ for {tools['D']} and ○ for {tools['O']}."
    )


# The build-out ladder: each rung adds these codes to everything below it.
LADDER: tuple[tuple[str, frozenset[str]], ...] = (
    ("Baseline only: chat plus Agent Skills", frozenset()),
    (
        "IN (attachments in context) and calling a skill by name (INVOKE)",
        frozenset({"IN", "INVOKE"}),
    ),
    (
        "TOOLS with OUT, FS and PERSIST: a durable workspace, skills materialised on disk",
        frozenset({"TOOLS", "OUT", "FS", "PERSIST"}),
    ),
    (
        "EXEC, SKILLDIR, HASH and DOCX: a Python 3.12 stdlib sandbox over the workspace "
        "and the skill folders",
        frozenset({"EXEC", "SKILLDIR", "HASH", "DOCX"}),
    ),
    (
        "BIN and VISION: pypdf, pdfplumber, python-docx, Pillow, Poppler, LibreOffice, "
        "and a model that reads rendered pages",
        frozenset({"BIN", "VISION"}),
    ),
    ("HTML: the user opens a generated page and returns its file", frozenset({"HTML"})),
    ("SUB: isolated workers, model chosen per worker", frozenset({"SUB"})),
    ("NET (raw bytes) and SEARCH", frozenset({"NET", "SEARCH"})),
    ("SESSION: the session's own events and past transcripts", frozenset({"SESSION"})),
    ("MCP connection", frozenset({"MCP"})),
    ("SCHED: scheduled runs and hooks", frozenset({"SCHED"})),
)
# Facets that need more than their base code's rung.
FACET_CODES = {
    "OUT:pdf-assemble": "BIN",
    "OUT:pdf-annotate": "BIN",
    "OUT:xlsx-roundtrip": "BIN",
    "OUT:docx-template": "SKILLDIR",
    "SKILLDIR:asset": "SKILLDIR",
    "DOCX:table-edit": "DOCX",
    "DOCX:tracked-write": "DOCX",
    "SEARCH:org": "SEARCH",
    "SESSION:resume": "SESSION",
}


def _rung_of(key: str) -> int:
    code = FACET_CODES.get(key, base_code(key))
    for index, (_, codes) in enumerate(LADDER):
        if code in codes:
            return index
    return len(LADDER) - 1


def ladder_markdown(caps: Capabilities, profile: str) -> str:
    runs: dict[int, list[str]] = {}
    full: dict[int, list[str]] = {}
    for name, skill in caps.skills.items():
        levels = (skill.get(profile) or {}).get("levels") or {}
        required = [k for k, v in levels.items() if v == "R"]
        needed = [k for k, v in levels.items() if v in ("R", "D")]
        runs.setdefault(max([_rung_of(k) for k in required], default=0), []).append(
            name
        )
        full.setdefault(max([_rung_of(k) for k in needed], default=0), []).append(name)
    lines = [
        "| Rung | Add | Runs from here (every ● met) | Runs as intended from here (every ● and ◐ met) |",
        "|---|---|---|---|",
    ]
    for index, (label, _) in enumerate(LADDER):
        r = sorted(runs.get(index, []))
        f = sorted(full.get(index, []))
        lines.append(
            f"| {index} | {label} | **{len(r)}**"
            + (f": {', '.join(r)}" if r else "")
            + f" | **{len(f)}**"
            + (f": {', '.join(f)}" if f else "")
            + " |"
        )
    return "\n".join(lines)


MARKERS = {
    "matrix-upstream": lambda c: matrix_markdown(c, "upstream"),
    "matrix-cowork": lambda c: matrix_markdown(c, "cowork"),
    "aux-upstream": lambda c: aux_markdown(c, "upstream"),
    "aux-cowork": lambda c: aux_markdown(c, "cowork"),
    "facets-upstream": lambda c: facet_markdown(c, "upstream"),
    "facets-cowork": lambda c: facet_markdown(c, "cowork"),
    "counts-upstream": lambda c: counts_markdown(c, "upstream"),
    "counts-cowork": lambda c: counts_markdown(c, "cowork"),
    "ladder-upstream": lambda c: ladder_markdown(c, "upstream"),
    "ladder-cowork": lambda c: ladder_markdown(c, "cowork"),
}


def render_chart(text: str, caps: Capabilities) -> str:
    """Replace every generated block between ``<!-- gen:NAME -->`` markers."""

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in MARKERS:
            return match.group(0)
        return f"<!-- gen:{name} -->\n{MARKERS[name](caps)}\n<!-- /gen:{name} -->"

    return re.sub(
        r"<!-- gen:([a-z-]+) -->\n(?:.*?\n)?<!-- /gen:\1 -->", replace, text, flags=re.S
    )


def write_chart(config: Config, caps: Capabilities, *, check: bool = False) -> bool:
    path = config.root / CHART_REL
    if not path.is_file():
        return True
    text = path.read_text(encoding="utf-8")
    new = render_chart(text, caps)
    if check:
        return new == text
    path.write_text(new, encoding="utf-8")
    return True


# --------------------------------------------------------------------------
# Engine and results


def load_engine(root: Path) -> ModuleType:
    path = root / ENGINE_REL
    if not path.is_file():
        raise ConfigError(f"{ENGINE_REL}: the harness-probe engine is missing")
    name = "hprobe_engine"
    if name in sys.modules and getattr(sys.modules[name], "__file__", "") == str(path):
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class HarnessReport:
    source: Path
    slug: str
    report: dict[str, Any]


def results_files(root: Path) -> list[Path]:
    folder = root / RESULTS_DIR
    return sorted(folder.glob("*.json")) if folder.is_dir() else []


def harness_reports(config: Config, caps: Capabilities | None) -> list[HarnessReport]:
    """One report per results file, plus an empty baseline per profile."""
    if caps is None:
        return []
    engine = load_engine(config.root)
    catalog = build_catalog(config, caps)
    reports: list[HarnessReport] = []
    for profile in PROFILES:
        empty = engine.new_results(f"no results ({profile})", profile)
        reports.append(
            HarnessReport(
                source=Path(""),
                slug=f"baseline-{profile}",
                report=engine.build_report(
                    catalog, empty, profile, generated="(no probe results recorded)"
                ),
            )
        )
    for path in results_files(config.root):
        try:
            results = engine.load_results(path)
        except engine.EngineError as exc:
            raise ConfigError(str(exc)) from exc
        profile = results["harness"].get("profile", "upstream")
        report = engine.build_report(
            catalog, results, profile, generated=_latest_date(results)
        )
        reports.append(HarnessReport(source=path, slug=path.stem, report=report))
    return reports


def _latest_date(results: dict[str, Any]) -> str:
    dates = [r.get("date", "") for r in results.get("results", [])]
    return max(dates) if dates else "(no results)"


def check_results(config: Config) -> list[Issue]:
    """LQC-K007: every committed results file is well formed and names real probes."""
    issues: list[Issue] = []
    if not results_files(config.root):
        return issues
    engine = load_engine(config.root)
    for path in results_files(config.root):
        rel = path.relative_to(config.root)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(Issue("LQC-K007", f"{rel}: invalid JSON: {exc}"))
            continue
        for problem in engine.validate_results(data, str(rel)):
            issues.append(Issue("LQC-K007", problem))
        for item in data.get("results") or []:
            if isinstance(item, dict) and item.get("probe") not in config.probe_ids:
                issues.append(
                    Issue(
                        "LQC-K007",
                        f"{rel}: result for unknown probe {item.get('probe')}",
                    )
                )
    return issues


def build_report_lines(reports: list[HarnessReport]) -> list[str]:
    """The `## Harness verdicts` section of dist/build-report.md."""
    if not reports:
        return []
    lines = [
        "## Harness verdicts",
        "",
        "Computed from `probe-results/` against `capabilities.yaml` by the "
        "harness-probe engine. The baselines show what is settled before any probe "
        "has run.",
        "",
        "| Harness | Profile | As intended | Fallback | Cannot run | Untested |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for item in reports:
        summary = item.report["summary"]
        name = item.report["harness"].get("name", item.slug)
        lines.append(
            f"| {name} | {item.report['profile']} | {summary['as-intended']} | "
            f"{summary['fallback']} | {summary['cannot-run']} | {summary['untested']} |"
        )
    lines.append("")
    flagged = [
        (item, flag)
        for item in reports
        for flag in item.report.get("disagreements") or []
    ]
    if flagged:
        lines += [
            "### Cards that disagree with a computed verdict",
            "",
            "| Harness | Skill | Card | Computed | Why |",
            "| --- | --- | --- | --- | --- |",
        ]
        for item, flag in flagged:
            lines.append(
                f"| {item.report['harness'].get('name')} | {flag['skill']} | {flag['card']} | "
                f"{flag['computed']} | {flag['note']} |"
            )
        lines.append("")
    return lines
