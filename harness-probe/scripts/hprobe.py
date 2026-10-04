#!/usr/bin/env python3
"""hprobe - run the LegalQuants capability probes on any harness and report.

    hprobe.py init     --run DIR --harness NAME [--profile upstream|cowork]
    hprobe.py status   --run DIR                  what is done, what is next
    hprobe.py steps    PROBE --run DIR            the agent's steps for one probe
    hprobe.py env      --run DIR                  P1: the runtime fingerprint
    hprobe.py check    PROBE --run DIR [...]      verify one probe and record it
    hprobe.py record   PROBE OUTCOME --run DIR    record an observed outcome
    hprobe.py posture  --run DIR key=value ...    note the harness's settings
    hprobe.py report   --run DIR [--profile P]    write report.md/.html/.json
    hprobe.py verdict  --results FILE [...]       report from results files alone

Standard library only, Python 3.8 or later. See ../SKILL.md.
"""

from __future__ import annotations

import argparse
import json
import random
import secrets
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import hprobe_checks as checks  # noqa: E402
import hprobe_engine as engine  # noqa: E402
import hprobe_fixtures as fixtures  # noqa: E402

SKILL = HERE.parent
DEFAULT_RUN = Path("hprobe-run")
EXIT_OK, EXIT_FAIL, EXIT_USAGE = 0, 1, 2


def _catalog(args: argparse.Namespace) -> Dict[str, Any]:
    return engine.load_catalog(
        Path(args.catalog)
        if getattr(args, "catalog", None)
        else engine.default_catalog_path()
    )


def _run_dir(args: argparse.Namespace) -> Path:
    return Path(args.run or DEFAULT_RUN).resolve()


def _load_run(root: Path) -> checks.Run:
    info_path = root / "run.json"
    if not info_path.is_file():
        raise SystemExit(f"{root} is not a probe run; start one with `hprobe.py init`")
    info = json.loads(info_path.read_text(encoding="utf-8"))
    key = json.loads((root / "key.json").read_text(encoding="utf-8"))
    return checks.Run(root=root, skill=SKILL, key=key, info=info)


def _static_run(args: argparse.Namespace) -> checks.Run:
    """Verify answers given against the packaged static fixtures."""
    static = SKILL / "assets" / "fixtures"
    key = json.loads((static / "static-key.json").read_text(encoding="utf-8"))
    root = _run_dir(args)
    root.mkdir(parents=True, exist_ok=True)
    return checks.Run(
        root=root,
        skill=SKILL,
        key=key,
        info={"static": True},
        fixtures_dir=fixtures.unpack_static(SKILL / "assets", root / "static-fixtures"),
    )


def _results_path(root: Path) -> Path:
    return root / "results.json"


def _load_results(root: Path) -> Dict[str, Any]:
    return engine.load_results(_results_path(root))


def _save_results(root: Path, results: Dict[str, Any]) -> None:
    _results_path(root).write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _subst(text: str, root: Path) -> str:
    return text.replace("<run>", str(root)).replace("<skill>", str(SKILL))


# --------------------------------------------------------------------------


def cmd_init(args: argparse.Namespace) -> int:
    root = _run_dir(args)
    if (root / "run.json").exists() and not args.force:
        print(
            f"{root} already holds a run; use --force to start again", file=sys.stderr
        )
        return EXIT_USAGE
    if root.exists() and args.force:
        for name in ("fixtures", "outputs", "state", "report"):
            shutil.rmtree(root / name, ignore_errors=True)
    for name in ("outputs", "inputs", "state"):
        (root / name).mkdir(parents=True, exist_ok=True)
    seed = secrets.randbits(64)
    salt = secrets.token_hex(16)
    key = fixtures.generate(root / "fixtures", random.Random(seed), salt)
    (root / "key.json").write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
    (root / "outputs" / "roundtrip.html").write_text(
        fixtures.roundtrip_html(key["P20"]["nonce"]), encoding="utf-8"
    )
    info = {
        "created": engine._dt.datetime.now(engine._dt.timezone.utc).isoformat(
            timespec="seconds"
        ),
        "skill": str(SKILL),
        "harness": args.harness,
        "profile": args.profile,
    }
    (root / "run.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    results_file = _results_path(root)
    if not results_file.exists() or args.force:
        results = engine.new_results(
            args.harness,
            args.profile,
            client=args.client or "",
            version=args.version or "",
            model=args.model or "",
            recorded_by=args.recorded_by or "",
        )
        _save_results(root, results)
    print(f"probe run ready at {root}")
    print(f"  fixtures: {root / 'fixtures'}")
    print(f"  results:  {results_file}")
    print("next: `hprobe.py status --run " + str(root) + "`")
    return EXIT_OK


def cmd_status(args: argparse.Namespace) -> int:
    root = _run_dir(args)
    catalog = _catalog(args)
    results = _load_results(root)
    latest = engine.latest_by_probe(results)
    print(
        f"Run {root} - harness {results['harness']['name']} ({results['harness']['profile']})"
    )
    done = 0
    for probe in sorted(
        catalog["probes"], key=lambda p: engine.probe_sort_key(p["id"])
    ):
        entry = latest.get(probe["id"])
        outcome = entry["outcome"] if entry else "not-run"
        if outcome not in ("not-run", "pending"):
            done += 1
        method = (probe.get("harness") or {}).get("method", "")
        print(f"  {probe['id']:<4} {outcome:<12} {method:<12} {probe['title']}")
    print(f"{done} of {len(catalog['probes'])} probes have an outcome.")
    return EXIT_OK


def cmd_steps(args: argparse.Namespace) -> int:
    catalog = _catalog(args)
    probe = engine.probes_by_id(catalog).get(args.probe.upper())
    if not probe:
        print(f"no probe {args.probe}", file=sys.stderr)
        return EXIT_USAGE
    root = _run_dir(args)
    harness = probe.get("harness") or {}
    print(f"{probe['id']}: {probe['title']}")
    print(
        f"tests {', '.join(probe.get('tests', []))}; method {harness.get('method')}; "
        f"cost {probe.get('cost')}"
    )
    print()
    print(_subst(" ".join(str(harness.get("steps", "")).split()), root))
    return EXIT_OK


def _record_check(root: Path, probe_id: str, result: checks.Check, args) -> None:
    if not result.record:
        return
    results = _load_results(root)
    engine.record(
        results,
        probe_id,
        result.outcome,
        observer=getattr(args, "observer", None) or "script",
        evidence=result.evidence,
        notes=" ".join(
            x for x in (result.notes, getattr(args, "notes", "") or "") if x
        ),
        codes=result.codes or None,
        facts=result.facts or None,
    )
    _save_results(root, results)


def cmd_check(args: argparse.Namespace) -> int:
    catalog = _catalog(args)
    probe_id = args.probe.upper()
    probe = engine.probes_by_id(catalog).get(probe_id)
    if not probe:
        print(f"no probe {args.probe}", file=sys.stderr)
        return EXIT_USAGE
    check_id = (probe.get("harness") or {}).get("check")
    if not check_id or check_id not in checks.CHECKS:
        print(
            f"{probe_id} has no scripted check; record what was observed with "
            f"`hprobe.py record {probe_id} <outcome> --observer user`",
            file=sys.stderr,
        )
        return EXIT_USAGE
    run = _static_run(args) if args.static else _load_run(_run_dir(args))
    if args.outputs:
        run.outputs_dir = Path(args.outputs).resolve()
    result = checks.CHECKS[check_id](run, args)
    if _results_path(run.root).exists():
        _record_check(run.root, probe_id, result, args)
    elif args.static and result.record:
        print("(not recorded: no results.json here; run `init` first to keep a record)")
    print(f"{probe_id} {result.outcome}: {result.evidence}")
    return EXIT_OK if result.outcome in ("pass", "pending") else EXIT_FAIL


def cmd_env(args: argparse.Namespace) -> int:
    args.probe = "P1"
    return cmd_check(args)


def cmd_record(args: argparse.Namespace) -> int:
    root = _run_dir(args)
    results = _load_results(root)
    codes = {}
    for item in args.code or []:
        if "=" not in item:
            print(f"--code expects CODE=outcome, got {item}", file=sys.stderr)
            return EXIT_USAGE
        code, outcome = item.split("=", 1)
        codes[code.strip().upper()] = outcome.strip()
    try:
        engine.record(
            results,
            args.probe.upper(),
            args.outcome,
            observer=args.observer,
            evidence=args.evidence or "",
            notes=args.notes or "",
            codes=codes or None,
            issue=args.issue or "",
        )
    except engine.EngineError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_USAGE
    problems = engine.validate_results(results)
    if problems:
        print("; ".join(problems), file=sys.stderr)
        return EXIT_USAGE
    _save_results(root, results)
    print(f"{args.probe.upper()} recorded as {args.outcome} ({args.observer})")
    return EXIT_OK


def cmd_posture(args: argparse.Namespace) -> int:
    root = _run_dir(args)
    results = _load_results(root)
    posture = results["harness"].setdefault("posture", {})
    for item in args.items:
        if "=" not in item:
            print(f"expected key=value, got {item}", file=sys.stderr)
            return EXIT_USAGE
        k, v = item.split("=", 1)
        posture[k.strip()] = v.strip()
    for field in ("client", "version", "model", "recorded_by"):
        value = getattr(args, field, None)
        if value:
            results["harness"][field] = value
    _save_results(root, results)
    print("posture: " + json.dumps(posture, sort_keys=True))
    return EXIT_OK


def cmd_report(args: argparse.Namespace) -> int:
    root = _run_dir(args)
    catalog = _catalog(args)
    documents = [_load_results(root)] + [
        engine.load_results(Path(p)) for p in args.results or []
    ]
    results = engine.merge_results(documents)
    profiles = (
        [args.profile]
        if args.profile
        else [results["harness"].get("profile", "upstream")]
    )
    if args.both:
        profiles = list(engine.PROFILES)
    out = Path(args.out).resolve() if args.out else root / "report"
    for profile in profiles:
        report = engine.build_report(catalog, results, profile)
        stem = "report" if len(profiles) == 1 else f"report-{profile}"
        _write_named(report, out, stem)
    return EXIT_OK


def _write_named(report: Dict[str, Any], out: Path, stem: str) -> None:
    paths = engine.write_report(report, out, stem)
    summary = ", ".join(
        f"{engine.VERDICT_TITLE[v].lower()} {report['summary'][v]}"
        for v in engine.VERDICTS
    )
    print(f"{report['profile']} profile: {summary}")
    for path in paths:
        print(f"  {path}")


def cmd_verdict(args: argparse.Namespace) -> int:
    catalog = _catalog(args)
    documents = [engine.load_results(Path(p)) for p in args.results]
    results = engine.merge_results(documents)
    profile = args.profile or results["harness"].get("profile", "upstream")
    report = engine.build_report(catalog, results, profile)
    if args.out:
        _write_named(report, Path(args.out), args.stem)
    else:
        sys.stdout.write(engine.render_markdown(report))
    return EXIT_OK


def cmd_fixtures(args: argparse.Namespace) -> int:
    fixtures.write_static(SKILL / "assets")
    print(f"static fixtures written under {SKILL / 'assets' / 'fixtures'}")
    return EXIT_OK


# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hprobe.py",
        description="Run the LegalQuants capability probes on this harness and report.",
    )
    parser.add_argument(
        "--catalog", help="catalogue JSON (default: ../data/catalog.json)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def run_arg(p: argparse.ArgumentParser) -> None:
        p.add_argument("--run", help=f"the run folder (default: ./{DEFAULT_RUN})")

    init = sub.add_parser("init", help="create a run folder with fresh fixtures")
    run_arg(init)
    init.add_argument(
        "--harness", required=True, help="a name for the harness under test"
    )
    init.add_argument("--profile", choices=engine.PROFILES, default="upstream")
    init.add_argument("--client")
    init.add_argument("--version")
    init.add_argument("--model")
    init.add_argument("--recorded-by", dest="recorded_by")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    status = sub.add_parser("status", help="list every probe and its outcome so far")
    run_arg(status)
    status.set_defaults(func=cmd_status)

    steps = sub.add_parser("steps", help="print one probe's steps with paths filled in")
    steps.add_argument("probe")
    run_arg(steps)
    steps.set_defaults(func=cmd_steps)

    def check_args(p: argparse.ArgumentParser) -> None:
        run_arg(p)
        p.add_argument("--answer")
        p.add_argument("--phase")
        p.add_argument("--url")
        p.add_argument("--bytes", type=int, default=0)
        p.add_argument("--count", type=int, default=0)
        p.add_argument("--model")
        p.add_argument("--implicit", choices=("quiet", "fired"))
        p.add_argument("--notes")
        p.add_argument("--observer", choices=engine.OBSERVERS, default="script")
        p.add_argument(
            "--static",
            action="store_true",
            help="check against the packaged static fixtures (no init needed)",
        )
        p.add_argument("--outputs", help="read the agent's output files from here")

    check = sub.add_parser("check", help="verify one probe and record the outcome")
    check.add_argument("probe")
    check_args(check)
    check.set_defaults(func=cmd_check)

    env = sub.add_parser("env", help="P1: record the runtime fingerprint")
    check_args(env)
    env.set_defaults(func=cmd_env)

    rec = sub.add_parser("record", help="record an outcome you observed")
    rec.add_argument("probe")
    rec.add_argument("outcome", choices=engine.OUTCOMES)
    run_arg(rec)
    rec.add_argument("--observer", choices=engine.OBSERVERS, default="agent")
    rec.add_argument("--evidence")
    rec.add_argument("--notes")
    rec.add_argument("--issue", help="link to the issue the result was reported in")
    rec.add_argument("--code", action="append", help="per-code outcome, CODE=outcome")
    rec.set_defaults(func=cmd_record)

    posture = sub.add_parser("posture", help="note settings: key=value ...")
    run_arg(posture)
    posture.add_argument("items", nargs="*")
    posture.add_argument("--client")
    posture.add_argument("--version")
    posture.add_argument("--model")
    posture.add_argument("--recorded-by", dest="recorded_by")
    posture.set_defaults(func=cmd_posture)

    report = sub.add_parser("report", help="write the report for this run")
    run_arg(report)
    report.add_argument("--profile", choices=engine.PROFILES)
    report.add_argument("--both", action="store_true", help="one report per profile")
    report.add_argument(
        "--results", action="append", help="extra results files to merge"
    )
    report.add_argument("--out", help="output folder (default: <run>/report)")
    report.set_defaults(func=cmd_report)

    verdict = sub.add_parser("verdict", help="report from results files, no run needed")
    verdict.add_argument("--results", action="append", required=True)
    verdict.add_argument("--profile", choices=engine.PROFILES)
    verdict.add_argument("--out")
    verdict.add_argument("--stem", default="report")
    verdict.set_defaults(func=cmd_verdict)

    fx = sub.add_parser(
        "fixtures", help="(maintainers) regenerate the packaged fixtures"
    )
    fx.set_defaults(func=cmd_fixtures)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except engine.EngineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
