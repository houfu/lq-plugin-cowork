"""Verdict engine for the harness probe skill.

Reads the probe catalogue (``data/catalog.json``) and one or more results
files, and works out, for every skill under a chosen profile, whether it runs
as intended, runs on a fallback, cannot run, or is untested. It also renders
the report as Markdown, HTML and JSON.

Standard library only, Python 3.8 or later, so that it runs on whatever
harness the skill lands on. The repository's build tooling imports this same
file, so the site and the skill can never disagree about a verdict.
"""

from __future__ import annotations

import datetime as _dt
import html
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

CATALOG_SCHEMA = "lq-harness-probe-catalog/1"
RESULTS_SCHEMA = "lq-harness-probe-results/1"
REPORT_SCHEMA = "lq-harness-probe-report/1"

LEVEL_SYMBOL = {"R": "●", "D": "◐", "O": "○"}
LEVEL_NAME = {"R": "required", "D": "degradable", "O": "optional"}
LEVEL_RANK = {"R": 3, "D": 2, "O": 1}

OUTCOMES = ("pass", "fail", "refused", "fluent-fake", "not-run", "pending")
FAILED = frozenset({"fail", "refused", "fluent-fake"})
OBSERVERS = ("script", "agent", "user", "maintainer")
COST_ORDER = {"free": 0, "low": 1, "setup": 2, "two-session": 3, "admin": 4}

VERDICTS = ("as-intended", "fallback", "cannot-run", "untested")
VERDICT_TITLE = {
    "as-intended": "Runs as intended",
    "fallback": "Runs on a fallback",
    "cannot-run": "Cannot run",
    "untested": "Untested",
}
VERDICT_BLURB = {
    "as-intended": "Every required and every degradable capability has a passing probe.",
    "fallback": (
        "Every required capability passes, but at least one degradable capability "
        "failed or has not been probed, so the skill runs on its documented fallback."
    ),
    "cannot-run": "At least one required capability failed its probe.",
    "untested": (
        "No required capability failed, but at least one has no result yet, so "
        "the skill cannot be confirmed either way."
    ),
}

PROFILES = ("upstream", "cowork")


class EngineError(Exception):
    """A catalogue or results file that cannot be used."""


# --------------------------------------------------------------------------
# Loading


def load_json(path: Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EngineError(f"{path}: not found") from exc
    except json.JSONDecodeError as exc:
        raise EngineError(f"{path}: invalid JSON: {exc}") from exc


def load_catalog(path: Path) -> Dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict) or data.get("schema") != CATALOG_SCHEMA:
        raise EngineError(f"{path}: not a {CATALOG_SCHEMA} file")
    return data


def default_catalog_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "catalog.json"


def new_results(
    name: str,
    profile: str = "upstream",
    *,
    client: str = "",
    version: str = "",
    model: str = "",
    recorded_by: str = "",
) -> Dict[str, Any]:
    if profile not in PROFILES:
        raise EngineError(f"profile must be one of {', '.join(PROFILES)}")
    return {
        "schema": RESULTS_SCHEMA,
        "harness": {
            "name": name,
            "profile": profile,
            "client": client,
            "version": version,
            "model": model,
            "recorded_by": recorded_by,
            "posture": {},
        },
        "results": [],
    }


def validate_results(data: Any, where: str = "results") -> List[str]:
    """Shape problems in a results document; an empty list means usable."""
    problems: List[str] = []
    if not isinstance(data, dict):
        return [f"{where}: expected a JSON object"]
    if data.get("schema") != RESULTS_SCHEMA:
        problems.append(f"{where}.schema: expected '{RESULTS_SCHEMA}'")
    harness = data.get("harness")
    if not isinstance(harness, dict) or not harness.get("name"):
        problems.append(f"{where}.harness.name: required")
    elif harness.get("profile", "upstream") not in PROFILES:
        problems.append(
            f"{where}.harness.profile: expected one of {', '.join(PROFILES)}"
        )
    results = data.get("results")
    if not isinstance(results, list):
        problems.append(f"{where}.results: expected a list")
        return problems
    for index, item in enumerate(results):
        spot = f"{where}.results[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{spot}: expected an object")
            continue
        if not isinstance(item.get("probe"), str):
            problems.append(f"{spot}.probe: required")
        if item.get("outcome") not in OUTCOMES:
            problems.append(f"{spot}.outcome: expected one of {', '.join(OUTCOMES)}")
        if not isinstance(item.get("date"), str) or not re.match(
            r"^\d{4}-\d{2}-\d{2}", item.get("date") or ""
        ):
            problems.append(f"{spot}.date: expected an ISO date")
        if item.get("observer", "agent") not in OBSERVERS:
            problems.append(f"{spot}.observer: expected one of {', '.join(OBSERVERS)}")
        codes = item.get("codes", {})
        if not isinstance(codes, dict) or any(
            v not in OUTCOMES for v in codes.values()
        ):
            problems.append(f"{spot}.codes: expected {{CODE: outcome}}")
    return problems


def load_results(path: Path) -> Dict[str, Any]:
    data = load_json(path)
    problems = validate_results(data, str(path))
    if problems:
        raise EngineError("; ".join(problems))
    return data


def record(
    results: Dict[str, Any],
    probe: str,
    outcome: str,
    *,
    observer: str = "agent",
    evidence: str = "",
    notes: str = "",
    codes: Optional[Dict[str, str]] = None,
    facts: Optional[Dict[str, Any]] = None,
    issue: str = "",
    date: Optional[str] = None,
) -> Dict[str, Any]:
    if outcome not in OUTCOMES:
        raise EngineError(f"outcome must be one of {', '.join(OUTCOMES)}")
    if observer not in OBSERVERS:
        raise EngineError(f"observer must be one of {', '.join(OBSERVERS)}")
    entry: Dict[str, Any] = {
        "probe": probe,
        "outcome": outcome,
        "date": date
        or _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "observer": observer,
    }
    if codes:
        entry["codes"] = dict(codes)
    if facts:
        entry["facts"] = facts
    if evidence:
        entry["evidence"] = evidence
    if notes:
        entry["notes"] = notes
    if issue:
        entry["issue"] = issue
    results.setdefault("results", []).append(entry)
    return entry


# --------------------------------------------------------------------------
# Catalogue helpers


def codes_by_id(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {code["id"]: code for code in catalog["codes"]}


def probes_by_id(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {probe["id"]: probe for probe in catalog["probes"]}


def probe_sort_key(probe_id: str) -> Tuple[int, str]:
    match = re.match(r"^P(\d+)", probe_id)
    return (int(match.group(1)) if match else 9999, probe_id)


def profile_of(skill: Dict[str, Any], profile: str) -> Dict[str, Any]:
    block = skill.get("profiles", {}).get(profile)
    if block is None:
        raise EngineError(f"skill {skill['name']} has no '{profile}' profile")
    return block


def evidence_for(
    catalog: Dict[str, Any], skill: Dict[str, Any], profile: str, code: str
) -> List[str]:
    """The probes whose results decide ``code`` for this skill and profile."""
    # A facet (CODE:facet) has no primary probes; only its own evidence counts.
    primary = list(codes_by_id(catalog).get(code, {}).get("evidence", []))
    extra = profile_of(skill, profile).get("evidence", {}).get(code, [])
    seen: List[str] = []
    for probe_id in primary + list(extra):
        if probe_id not in seen:
            seen.append(probe_id)
    return seen


def derived_unlocks(
    catalog: Dict[str, Any], profile: str, levels: Iterable[str] = ("R", "D")
) -> Dict[str, List[str]]:
    """probe id -> skills whose rated capabilities that probe decides."""
    wanted = set(levels)
    out: Dict[str, List[str]] = {p["id"]: [] for p in catalog["probes"]}
    for skill in catalog["skills"]:
        block = skill.get("profiles", {}).get(profile)
        if not block:
            continue
        for code, level in block.get("levels", {}).items():
            if level not in wanted:
                continue
            for probe_id in evidence_for(catalog, skill, profile, code):
                names = out.setdefault(probe_id, [])
                if skill["name"] not in names:
                    names.append(skill["name"])
    return {k: sorted(v) for k, v in out.items()}


# --------------------------------------------------------------------------
# Results


def _date_key(entry: Dict[str, Any], index: int) -> Tuple[str, int]:
    return (str(entry.get("date", "")), index)


def latest_by_probe(results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """The newest result for each probe (by date, then by file order)."""
    latest: Dict[str, Tuple[Tuple[str, int], Dict[str, Any]]] = {}
    for index, entry in enumerate(results.get("results", [])):
        key = _date_key(entry, index)
        current = latest.get(entry["probe"])
        if current is None or key >= current[0]:
            latest[entry["probe"]] = (key, entry)
    return {probe: pair[1] for probe, pair in latest.items()}


def merge_results(documents: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Several results files for one harness, as one document."""
    if not documents:
        raise EngineError("no results to merge")
    merged = json.loads(json.dumps(documents[0]))
    for extra in documents[1:]:
        merged["results"].extend(json.loads(json.dumps(extra["results"])))
    return merged


def outcome_for(
    latest: Dict[str, Dict[str, Any]], probe_id: str, code: str
) -> Tuple[str, Optional[Dict[str, Any]]]:
    entry = latest.get(probe_id)
    if entry is None:
        return "not-run", None
    per_code = entry.get("codes") or {}
    return per_code.get(code, entry["outcome"]), entry


def _version_tuple(text: str) -> Tuple[int, ...]:
    parts = re.findall(r"\d+", text or "")
    return tuple(int(p) for p in parts[:3]) if parts else ()


def needs_status(
    needs: Dict[str, Any], code: str, facts: Dict[str, Any]
) -> Tuple[Optional[str], str]:
    """Judge EXEC or BIN against a skill's exact runtime needs, from P1 facts.

    Returns (status, reason); status None means the needs say nothing about
    this code, so the probe's own outcome stands.
    """
    if code == "EXEC":
        want_py = needs.get("python")
        packages = needs.get("packages") or []
        if not want_py and not packages:
            return None, ""
        have_py = facts.get("python")
        if want_py:
            if not have_py:
                return "untested", "no Python version was recorded"
            if _version_tuple(have_py) < _version_tuple(want_py):
                return "fail", f"needs Python ≥{want_py}, harness has {have_py}"
        have = facts.get("packages") or {}
        missing = [p for p in packages if not have.get(p)]
        if missing:
            if not have:
                return "untested", "no package list was recorded"
            return "fail", "missing Python packages: " + ", ".join(missing)
        return "pass", ""
    if code == "BIN":
        binaries = needs.get("binaries") or []
        any_of = needs.get("binaries_any") or []
        if not binaries and not any_of:
            return None, ""
        have = facts.get("binaries") or {}
        if not have:
            return "untested", "no binary list was recorded"
        missing = [b for b in binaries if not have.get(b)]
        if any_of and not any(have.get(b) for b in any_of):
            missing.append("one of " + "/".join(any_of))
        if missing:
            return "fail", "missing executables: " + ", ".join(missing)
        return "pass", ""
    return None, ""


def capability_status(
    catalog: Dict[str, Any],
    skill: Dict[str, Any],
    profile: str,
    code: str,
    latest: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    probes: List[Dict[str, Any]] = []
    statuses: List[str] = []
    reason = ""
    needs = profile_of(skill, profile).get("needs") or {}
    for probe_id in evidence_for(catalog, skill, profile, code):
        outcome, entry = outcome_for(latest, probe_id, code)
        status = (
            "pass" if outcome == "pass" else "fail" if outcome in FAILED else "untested"
        )
        if entry is not None and code in ("EXEC", "BIN") and status == "pass":
            # P1's outcome says scripts run at all; the skill's exact runtime
            # needs decide whether they run for this skill.
            judged, why = needs_status(needs, code, entry.get("facts") or {})
            if judged is not None:
                status = judged
                reason = why or reason
        probes.append(
            {
                "id": probe_id,
                "outcome": outcome,
                "date": (entry or {}).get("date", ""),
                "observer": (entry or {}).get("observer", ""),
            }
        )
        statuses.append(status)
    if not statuses:
        overall = "untested"
        reason = reason or "no probe tests this capability"
    elif "fail" in statuses:
        overall = "fail"
    elif all(s == "pass" for s in statuses):
        overall = "pass"
    else:
        overall = "untested"
    return {"code": code, "status": overall, "probes": probes, "reason": reason}


def skill_verdict(
    catalog: Dict[str, Any],
    skill: Dict[str, Any],
    profile: str,
    latest: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    block = profile_of(skill, profile)
    levels: Dict[str, str] = block.get("levels", {})
    fallbacks: Dict[str, Any] = block.get("fallbacks", {})
    caps: List[Dict[str, Any]] = []
    for code in _ordered_codes(catalog, levels):
        status = capability_status(catalog, skill, profile, code, latest)
        status["level"] = levels[code]
        caps.append(status)

    required = [c for c in caps if c["level"] == "R"]
    degradable = [c for c in caps if c["level"] == "D"]
    optional = [c for c in caps if c["level"] == "O"]

    blocking = [c for c in required if c["status"] == "fail"]
    unknown = [c for c in required if c["status"] == "untested"]
    lost = [c for c in degradable if c["status"] != "pass"]
    if blocking:
        verdict = "cannot-run"
    elif unknown:
        verdict = "untested"
    elif lost:
        verdict = "fallback"
    else:
        verdict = "as-intended"

    fallback_items = []
    for cap in lost:
        wording = fallbacks.get(cap["code"]) or {}
        fallback_items.append(
            {
                "code": cap["code"],
                "status": cap["status"],
                "text": wording.get("text", ""),
                "ref": wording.get("ref", ""),
                "probes": [p["id"] for p in cap["probes"]],
            }
        )
    out: Dict[str, Any] = {
        "skill": skill["name"],
        "group": skill.get("group", ""),
        "verdict": verdict,
        "capabilities": caps,
        "blocking": [
            {
                "code": c["code"],
                "probes": [p["id"] for p in c["probes"]],
                "reason": c["reason"],
            }
            for c in blocking
        ],
        "unknown": [
            {"code": c["code"], "probes": [p["id"] for p in c["probes"]]}
            for c in unknown
        ],
        "fallbacks": fallback_items,
        "optional_missing": [c["code"] for c in optional if c["status"] == "fail"],
        "optional_available": [c["code"] for c in optional if c["status"] == "pass"],
    }
    card = block.get("card")
    if card:
        out["card"] = card
    return out


def _ordered_codes(catalog: Dict[str, Any], levels: Dict[str, str]) -> List[str]:
    order = [code["id"] for code in catalog["codes"]]

    def key(name: str) -> Tuple[int, str]:
        base = name.split(":", 1)[0]
        return (order.index(base) if base in order else len(order), name)

    return sorted(levels, key=key)


def _probe_status(latest: Dict[str, Dict[str, Any]], probe_id: str) -> str:
    entry = latest.get(probe_id)
    if entry is None:
        return "not-run"
    return entry["outcome"]


def next_probes(
    catalog: Dict[str, Any],
    verdicts: List[Dict[str, Any]],
    latest: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Unrun probes, ranked by how many skills each would move."""
    probes = probes_by_id(catalog)
    ranking = []
    for probe_id, probe in probes.items():
        if (
            _probe_status(latest, probe_id) in ("pass",)
            or _probe_status(latest, probe_id) in FAILED
        ):
            continue
        clears: List[str] = []
        touches: List[str] = []
        confirms: List[str] = []
        for verdict in verdicts:
            unknown = verdict["unknown"]
            involved = [u for u in unknown if probe_id in u["probes"]]
            if involved:
                touches.append(verdict["skill"])
                remaining = [
                    pid
                    for u in unknown
                    for pid in u["probes"]
                    if _probe_status(latest, pid) not in ("pass",)
                    and _probe_status(latest, pid) not in FAILED
                ]
                if set(remaining) == {probe_id}:
                    clears.append(verdict["skill"])
            if verdict["verdict"] in ("fallback", "as-intended") and any(
                probe_id in f["probes"] and f["status"] == "untested"
                for f in verdict["fallbacks"]
            ):
                confirms.append(verdict["skill"])
        if not (clears or touches or confirms):
            continue
        ranking.append(
            {
                "probe": probe_id,
                "title": probe["title"],
                "cost": probe.get("cost", "low"),
                "method": (probe.get("harness") or {}).get("method", ""),
                "tests": probe.get("tests", []),
                "clears": sorted(clears),
                "touches": sorted(touches),
                "confirms": sorted(confirms),
            }
        )
    ranking.sort(
        key=lambda r: (
            -len(r["clears"]),
            -len(r["touches"]),
            -len(r["confirms"]),
            COST_ORDER.get(r["cost"], 9),
            probe_sort_key(r["probe"]),
        )
    )
    return ranking


def capability_table(
    catalog: Dict[str, Any], latest: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Each code's status on its primary evidence alone."""
    rows = []
    for code in catalog["codes"]:
        statuses = []
        probes = []
        for probe_id in code.get("evidence", []):
            outcome, entry = outcome_for(latest, probe_id, code["id"])
            probes.append(
                {
                    "id": probe_id,
                    "outcome": outcome,
                    "date": (entry or {}).get("date", ""),
                }
            )
            statuses.append(
                "pass"
                if outcome == "pass"
                else "fail" if outcome in FAILED else "untested"
            )
        if not statuses:
            status = "unprobed"
        elif "fail" in statuses:
            status = "fail"
        elif all(s == "pass" for s in statuses):
            status = "pass"
        else:
            status = "untested"
        rows.append(
            {
                "code": code["id"],
                "name": code["name"],
                "column": code.get("column", True),
                "status": status,
                "probes": probes,
            }
        )
    return rows


def coverage(catalog: Dict[str, Any]) -> Dict[str, Any]:
    """Which probes test which codes, and which codes no probe tests."""
    tested: Dict[str, List[str]] = {c["id"]: [] for c in catalog["codes"]}
    for probe in sorted(catalog["probes"], key=lambda p: probe_sort_key(p["id"])):
        for code in probe.get("tests", []):
            tested.setdefault(code, []).append(probe["id"])
    unprobed = {u["code"]: u["reason"] for u in catalog.get("unprobed", [])}
    rows = [
        {
            "code": code,
            "probes": probes,
            "unprobed_reason": unprobed.get(code, ""),
        }
        for code, probes in tested.items()
    ]
    return {"rows": rows, "gaps": [r["code"] for r in rows if not r["probes"]]}


def disagreements(verdicts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Where a card's hand-set status or tier disagrees with the computed verdict."""
    flags: List[Dict[str, str]] = []
    for verdict in verdicts:
        card = verdict.get("card")
        if not card:
            continue
        status = card.get("status", "")
        tier = card.get("tier")
        name = verdict["skill"]
        if verdict["verdict"] == "cannot-run" and status == "shipped":
            codes = ", ".join(b["code"] for b in verdict["blocking"])
            flags.append(
                {
                    "skill": name,
                    "card": f"status {status}, tier {tier}",
                    "computed": verdict["verdict"],
                    "note": f"shipped, but required {codes} failed on this harness",
                }
            )
        elif status == "probe-gated" and verdict["verdict"] == "as-intended":
            flags.append(
                {
                    "skill": name,
                    "card": f"status {status}, tier {tier}",
                    "computed": verdict["verdict"],
                    "note": "every probe the gate waits on passed; the gate could lift",
                }
            )
        elif isinstance(tier, int) and tier <= 1 and verdict["verdict"] == "fallback":
            lost = ", ".join(
                f["code"] for f in verdict["fallbacks"] if f["status"] == "fail"
            )
            if lost:
                flags.append(
                    {
                        "skill": name,
                        "card": f"status {status}, tier {tier}",
                        "computed": verdict["verdict"],
                        "note": f"low tier, but {lost} failed and the fallback is in use",
                    }
                )
    return flags


def build_report(
    catalog: Dict[str, Any],
    results: Dict[str, Any],
    profile: Optional[str] = None,
    *,
    generated: Optional[str] = None,
) -> Dict[str, Any]:
    harness = results.get("harness", {})
    profile = profile or harness.get("profile") or "upstream"
    if profile not in PROFILES:
        raise EngineError(f"profile must be one of {', '.join(PROFILES)}")
    latest = latest_by_probe(results)
    verdicts = [
        skill_verdict(catalog, skill, profile, latest)
        for skill in sorted(
            catalog["skills"], key=lambda s: (s.get("group", ""), s["name"])
        )
        if profile in skill.get("profiles", {})
    ]
    groups = {v: [x["skill"] for x in verdicts if x["verdict"] == v] for v in VERDICTS}
    probes = probes_by_id(catalog)
    probe_rows = []
    for probe_id in sorted(probes, key=probe_sort_key):
        entry = latest.get(probe_id)
        probe_rows.append(
            {
                "id": probe_id,
                "title": probes[probe_id]["title"],
                "tests": probes[probe_id].get("tests", []),
                "outcome": entry["outcome"] if entry else "not-run",
                "date": entry.get("date", "") if entry else "",
                "observer": entry.get("observer", "") if entry else "",
                "evidence": entry.get("evidence", "") if entry else "",
                "notes": entry.get("notes", "") if entry else "",
                "codes": entry.get("codes", {}) if entry else {},
            }
        )
    facts = {}
    p1 = latest.get("P1")
    if p1 and p1.get("facts"):
        facts = p1["facts"]
    return {
        "schema": REPORT_SCHEMA,
        "generated": generated
        or _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "catalog": catalog.get("source", {}),
        "harness": harness,
        "profile": profile,
        "summary": {v: len(groups[v]) for v in VERDICTS},
        "groups": groups,
        "skills": verdicts,
        "probes": probe_rows,
        "capabilities": capability_table(catalog, latest),
        "coverage": coverage(catalog),
        "next": next_probes(catalog, verdicts, latest),
        "disagreements": disagreements(verdicts) if profile == "cowork" else [],
        "facts": facts,
    }


# --------------------------------------------------------------------------
# Rendering: Markdown


def _md_escape(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _status_word(status: str) -> str:
    return {
        "pass": "pass",
        "fail": "**fail**",
        "untested": "untested",
        "unprobed": "no probe",
    }.get(status, status)


def render_markdown(report: Dict[str, Any]) -> str:
    h = report["harness"]
    lines = [
        f"# Harness probe report: {h.get('name', 'unnamed harness')}",
        "",
        f"- Profile: **{report['profile']}**"
        + (
            " (vendored upstream skills)"
            if report["profile"] == "upstream"
            else " (adapted Cowork cards)"
        ),
    ]
    for key, label in (
        ("client", "Client"),
        ("version", "Version"),
        ("model", "Model"),
        ("recorded_by", "Recorded by"),
    ):
        if h.get(key):
            lines.append(f"- {label}: {h[key]}")
    posture = h.get("posture") or {}
    if posture:
        lines.append(
            "- Posture: " + "; ".join(f"{k}: {v}" for k, v in sorted(posture.items()))
        )
    lines.append(f"- Generated: {report['generated']}")
    source = report.get("catalog") or {}
    if source:
        lines.append(
            "- Catalogue: "
            + ", ".join(f"{k} {v}" for k, v in sorted(source.items()) if v)
        )
    lines += ["", "## Summary", "", "| Verdict | Skills |", "| --- | ---: |"]
    for v in VERDICTS:
        lines.append(f"| {VERDICT_TITLE[v]} | {report['summary'][v]} |")
    lines.append("")
    for v in VERDICTS:
        names = report["groups"][v]
        lines += [f"## {VERDICT_TITLE[v]} ({len(names)})", "", VERDICT_BLURB[v], ""]
        if not names:
            lines += ["None.", ""]
            continue
        for verdict in [s for s in report["skills"] if s["verdict"] == v]:
            lines.append(f"- **{verdict['skill']}**{_md_detail(verdict)}")
        lines.append("")

    lines += [
        "## Per skill",
        "",
        "Levels: ● required, ◐ degradable (documented fallback), ○ optional.",
        "",
        "| Skill | Verdict | ● required | ◐ degradable | ○ optional |",
        "| --- | --- | --- | --- | --- |",
    ]
    for verdict in report["skills"]:
        cells = {"R": [], "D": [], "O": []}
        for cap in verdict["capabilities"]:
            mark = {"pass": "", "fail": " ✗", "untested": " ?"}.get(cap["status"], "")
            cells[cap["level"]].append(cap["code"] + mark)
        lines.append(
            f"| {verdict['skill']} | {VERDICT_TITLE[verdict['verdict']]} | "
            f"{', '.join(cells['R']) or '—'} | {', '.join(cells['D']) or '—'} | "
            f"{', '.join(cells['O']) or '—'} |"
        )
    lines += ["", "✗ failed, ? not yet probed, no mark = passed.", ""]

    lines += [
        "## Capabilities",
        "",
        "Each capability on its primary probes alone; a skill can need extra probes.",
        "",
        "| Code | Capability | Status | Probes |",
        "| --- | --- | --- | --- |",
    ]
    for cap in report["capabilities"]:
        probes = ", ".join(f"{p['id']} {p['outcome']}" for p in cap["probes"]) or "—"
        lines.append(
            f"| {cap['code']} | {_md_escape(cap['name'])} | "
            f"{_status_word(cap['status'])} | {probes} |"
        )
    lines.append("")

    lines += [
        "## Probe results",
        "",
        "| Probe | Title | Tests | Outcome | Date | Observer | Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for probe in report["probes"]:
        outcome = probe["outcome"]
        if probe["codes"]:
            outcome += (
                " ("
                + ", ".join(f"{k} {v}" for k, v in sorted(probe["codes"].items()))
                + ")"
            )
        lines.append(
            f"| {probe['id']} | {_md_escape(probe['title'])} | "
            f"{', '.join(probe['tests'])} | {outcome} | {probe['date'][:10]} | "
            f"{probe['observer']} | {_md_escape(probe['evidence'])[:160]} |"
        )
    lines.append("")

    if report["next"]:
        lines += [
            "## What to probe next",
            "",
            "Ranked by how many skills each unrun probe would move out of Untested "
            "(clears), then how many it bears on, then cost.",
            "",
            "| Probe | Title | Cost | Clears | Touches | Confirms a fallback for |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for row in report["next"]:
            lines.append(
                f"| {row['probe']} | {_md_escape(row['title'])} | {row['cost']} | "
                f"{len(row['clears'])}: {', '.join(row['clears']) or '—'} | "
                f"{len(row['touches'])} | {', '.join(row['confirms']) or '—'} |"
            )
        lines.append("")

    if report["disagreements"]:
        lines += [
            "## Where a card disagrees with the verdict",
            "",
            "Flagged for the maintainer, not changed.",
            "",
            "| Skill | Card says | Computed | Why |",
            "| --- | --- | --- | --- |",
        ]
        for flag in report["disagreements"]:
            lines.append(
                f"| {flag['skill']} | {flag['card']} | {VERDICT_TITLE[flag['computed']]} "
                f"| {_md_escape(flag['note'])} |"
            )
        lines.append("")

    cov = report["coverage"]
    lines += [
        "## Probe coverage",
        "",
        "| Code | Probes that test it |",
        "| --- | --- |",
    ]
    for row in cov["rows"]:
        lines.append(
            f"| {row['code']} | {', '.join(row['probes']) or 'none — ' + (row['unprobed_reason'] or 'gap')} |"
        )
    lines.append("")
    if report["facts"]:
        lines += ["## Runtime facts (from P1)", "", "```json"]
        lines.append(json.dumps(report["facts"], indent=2, sort_keys=True))
        lines += ["```", ""]
    return "\n".join(lines).rstrip() + "\n"


def _md_detail(verdict: Dict[str, Any]) -> str:
    parts = []
    if verdict["blocking"]:
        parts.append(
            "blocked by "
            + "; ".join(
                f"{b['code']} ({', '.join(b['probes'])}{': ' + b['reason'] if b['reason'] else ''})"
                for b in verdict["blocking"]
            )
        )
    if verdict["verdict"] == "untested" and verdict["unknown"]:
        parts.append(
            "waiting on "
            + "; ".join(
                f"{u['code']} ({', '.join(u['probes'])})" for u in verdict["unknown"]
            )
        )
    if verdict["fallbacks"] and verdict["verdict"] in ("fallback",):
        items = []
        for f in verdict["fallbacks"]:
            label = f["code"] + (" failed" if f["status"] == "fail" else " unprobed")
            if f["text"]:
                text = (
                    f["text"]
                    if len(f["text"]) <= 160
                    else f["text"][:157].rstrip() + "..."
                )
                label += f": “{text}”"
            items.append(label)
        parts.append("; ".join(items))
    return (" — " + " · ".join(parts)) if parts else ""


# --------------------------------------------------------------------------
# Rendering: HTML

_CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#5f5d57;--line:#dedbd2;--card:#ffffff;
--ok:#1f7a4d;--ok-bg:#e3f2ea;--warn:#8a5a00;--warn-bg:#fbf0d9;--bad:#b3261e;
--bad-bg:#fbe4e2;--unk:#4a5568;--unk-bg:#e9ecf1;--accent:#2d2d2d}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#151514;
--fg:#ecebe6;--muted:#a9a69d;--line:#34332f;--card:#1d1d1b;--ok:#7fd1a5;--ok-bg:#16301f;
--warn:#f0c46b;--warn-bg:#3a2d10;--bad:#ff8f86;--bad-bg:#3d1714;--unk:#c3cad6;
--unk-bg:#262a31;--accent:#ecebe6}}
:root[data-theme="dark"]{--bg:#151514;--fg:#ecebe6;--muted:#a9a69d;--line:#34332f;
--card:#1d1d1b;--ok:#7fd1a5;--ok-bg:#16301f;--warn:#f0c46b;--warn-bg:#3a2d10;
--bad:#ff8f86;--bad-bg:#3d1714;--unk:#c3cad6;--unk-bg:#262a31;--accent:#ecebe6}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.6rem;margin:.2em 0}h2{font-size:1.2rem;margin:2em 0 .6em}
.meta{color:var(--muted);margin:0 0 1em;padding:0;list-style:none}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.tile b{display:block;font-size:2rem;line-height:1.1}
.as-intended{color:var(--ok)}.fallback{color:var(--warn)}.cannot-run{color:var(--bad)}
.untested{color:var(--unk)}
.pill{display:inline-block;border-radius:999px;padding:1px 9px;font-size:.82rem;
font-weight:600;white-space:nowrap}
.p-as-intended,.p-pass{background:var(--ok-bg);color:var(--ok)}
.p-fallback{background:var(--warn-bg);color:var(--warn)}
.p-cannot-run,.p-fail,.p-refused,.p-fluent-fake{background:var(--bad-bg);color:var(--bad)}
.p-untested,.p-not-run,.p-pending,.p-unprobed{background:var(--unk-bg);color:var(--unk)}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{position:sticky;top:0;background:var(--card)}
tr:last-child td{border-bottom:0}
.list{list-style:none;padding:0;margin:0;display:grid;gap:8px}
.list li{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.list .why{color:var(--muted);font-size:.88rem;margin-top:3px}
.cap{display:inline-block;margin:1px 3px 1px 0;font-family:ui-monospace,monospace;font-size:.8rem;
padding:0 6px;border-radius:5px}
.c-pass{background:var(--ok-bg);color:var(--ok)}.c-fail{background:var(--bad-bg);color:var(--bad)}
.c-untested{background:var(--unk-bg);color:var(--unk)}
small,.muted{color:var(--muted)}code{font-family:ui-monospace,monospace;font-size:.85em}
"""


def _e(text: Any) -> str:
    return html.escape(str(text), quote=True)


def render_html(report: Dict[str, Any]) -> str:
    h = report["harness"]
    title = f"Harness probe report: {h.get('name', 'harness')}"
    out = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        f"<title>{_e(title)}</title><style>{_CSS}</style></head><body><main>",
        f"<h1>{_e(title)}</h1><ul class='meta'>",
        f"<li>Profile <b>{_e(report['profile'])}</b> · generated {_e(report['generated'])}</li>",
    ]
    detail = " · ".join(
        f"{label} {_e(h[key])}"
        for key, label in (
            ("client", "client"),
            ("version", "version"),
            ("model", "model"),
            ("recorded_by", "recorded by"),
        )
        if h.get(key)
    )
    if detail:
        out.append(f"<li>{detail}</li>")
    posture = h.get("posture") or {}
    if posture:
        out.append(
            "<li>Posture: "
            + _e("; ".join(f"{k}: {v}" for k, v in sorted(posture.items())))
            + "</li>"
        )
    out.append("</ul><div class='tiles'>")
    for v in VERDICTS:
        out.append(
            f"<div class='tile'><b class='{v}'>{report['summary'][v]}</b>"
            f"{_e(VERDICT_TITLE[v])}</div>"
        )
    out.append("</div>")

    for v in VERDICTS:
        items = [s for s in report["skills"] if s["verdict"] == v]
        out.append(f"<h2>{_e(VERDICT_TITLE[v])} ({len(items)})</h2>")
        out.append(f"<p class='muted'>{_e(VERDICT_BLURB[v])}</p>")
        if not items:
            out.append("<p>None.</p>")
            continue
        out.append("<ul class='list'>")
        for s in items:
            why = _md_detail(s).lstrip(" —")
            out.append(
                f"<li><b>{_e(s['skill'])}</b> <small>{_e(s['group'])}</small>"
                + (f"<div class='why'>{_e(why)}</div>" if why else "")
                + "</li>"
            )
        out.append("</ul>")

    out.append("<h2>Per skill</h2><div class='scroll'><table><thead><tr>")
    out.append(
        "<th>Skill</th><th>Verdict</th><th>● required</th><th>◐ degradable</th>"
        "<th>○ optional</th></tr></thead><tbody>"
    )
    for s in report["skills"]:
        cells = {"R": [], "D": [], "O": []}
        for cap in s["capabilities"]:
            cells[cap["level"]].append(
                f"<span class='cap c-{cap['status']}' title='{_e(cap['status'])}'>"
                f"{_e(cap['code'])}</span>"
            )
        out.append(
            f"<tr><td>{_e(s['skill'])}</td><td><span class='pill p-{s['verdict']}'>"
            f"{_e(VERDICT_TITLE[s['verdict']])}</span></td>"
            f"<td>{''.join(cells['R']) or '—'}</td><td>{''.join(cells['D']) or '—'}</td>"
            f"<td>{''.join(cells['O']) or '—'}</td></tr>"
        )
    out.append(
        "</tbody></table></div><p><small>Green passed, red failed, grey not yet probed."
        "</small></p>"
    )

    out.append("<h2>Capabilities</h2><div class='scroll'><table><thead><tr>")
    out.append(
        "<th>Code</th><th>Capability</th><th>Status</th><th>Probes</th></tr></thead><tbody>"
    )
    for cap in report["capabilities"]:
        probes = ", ".join(f"{p['id']} {p['outcome']}" for p in cap["probes"]) or "—"
        out.append(
            f"<tr><td><code>{_e(cap['code'])}</code></td><td>{_e(cap['name'])}</td>"
            f"<td><span class='pill p-{cap['status']}'>{_e(cap['status'])}</span></td>"
            f"<td>{_e(probes)}</td></tr>"
        )
    out.append("</tbody></table></div>")

    out.append("<h2>Probe results</h2><div class='scroll'><table><thead><tr>")
    out.append(
        "<th>Probe</th><th>Title</th><th>Tests</th><th>Outcome</th><th>Date</th>"
        "<th>Observer</th><th>Evidence</th></tr></thead><tbody>"
    )
    for p in report["probes"]:
        codes = (
            "<br><small>"
            + _e(", ".join(f"{k} {v}" for k, v in sorted(p["codes"].items())))
            + "</small>"
            if p["codes"]
            else ""
        )
        out.append(
            f"<tr><td>{_e(p['id'])}</td><td>{_e(p['title'])}</td>"
            f"<td><code>{_e(' '.join(p['tests']))}</code></td>"
            f"<td><span class='pill p-{p['outcome']}'>{_e(p['outcome'])}</span>{codes}</td>"
            f"<td>{_e(p['date'][:10])}</td><td>{_e(p['observer'])}</td>"
            f"<td><small>{_e(p['evidence'][:300])}</small></td></tr>"
        )
    out.append("</tbody></table></div>")

    if report["next"]:
        out.append("<h2>What to probe next</h2><div class='scroll'><table><thead><tr>")
        out.append(
            "<th>Probe</th><th>Title</th><th>Cost</th><th>Clears</th><th>Touches</th>"
            "<th>Confirms a fallback for</th></tr></thead><tbody>"
        )
        for row in report["next"]:
            out.append(
                f"<tr><td>{_e(row['probe'])}</td><td>{_e(row['title'])}</td>"
                f"<td>{_e(row['cost'])}</td><td><b>{len(row['clears'])}</b> "
                f"<small>{_e(', '.join(row['clears']))}</small></td>"
                f"<td>{len(row['touches'])}</td>"
                f"<td><small>{_e(', '.join(row['confirms']) or '—')}</small></td></tr>"
            )
        out.append("</tbody></table></div>")

    if report["disagreements"]:
        out.append("<h2>Where a card disagrees with the verdict</h2>")
        out.append(
            "<div class='scroll'><table><thead><tr><th>Skill</th><th>Card says</th>"
        )
        out.append("<th>Computed</th><th>Why</th></tr></thead><tbody>")
        for flag in report["disagreements"]:
            out.append(
                f"<tr><td>{_e(flag['skill'])}</td><td>{_e(flag['card'])}</td>"
                f"<td>{_e(VERDICT_TITLE[flag['computed']])}</td><td>{_e(flag['note'])}</td></tr>"
            )
        out.append("</tbody></table></div>")

    out.append("<h2>Probe coverage</h2><div class='scroll'><table><thead><tr>")
    out.append("<th>Code</th><th>Probes that test it</th></tr></thead><tbody>")
    for row in report["coverage"]["rows"]:
        text = ", ".join(row["probes"]) or (
            "none — " + (row["unprobed_reason"] or "gap")
        )
        out.append(
            f"<tr><td><code>{_e(row['code'])}</code></td><td>{_e(text)}</td></tr>"
        )
    out.append("</tbody></table></div>")
    if report["facts"]:
        out.append(
            "<h2>Runtime facts (from P1)</h2><div class='scroll'><pre style='margin:0;padding:12px'>"
        )
        out.append(_e(json.dumps(report["facts"], indent=2, sort_keys=True)))
        out.append("</pre></div>")
    out.append("</main></body></html>")
    return "\n".join(out) + "\n"


def write_report(
    report: Dict[str, Any], out_dir: Path, stem: str = "report"
) -> List[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        out_dir / f"{stem}.md",
        out_dir / f"{stem}.html",
        out_dir / f"{stem}.json",
    ]
    paths[0].write_text(render_markdown(report), encoding="utf-8")
    paths[1].write_text(render_html(report), encoding="utf-8")
    paths[2].write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return paths
