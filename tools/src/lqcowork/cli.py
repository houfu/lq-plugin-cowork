"""``lqcowork`` command line: build, validate, package, bump-upstream, anchor."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import package as pkg
from .build import AnchorFailure, Builder, BuildError, Issue, Suppression
from .bump import BumpError, anchor, bump_upstream
from .config import (
    Config,
    ConfigError,
    find_repo_root,
    load_cards,
    load_config,
    upstream_skill_names,
)
from .validate import validate_bundle

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_INVALID = 2


def _echo(text: str = "") -> None:
    print(text, flush=True)


def _report_issues(label: str, issues: list[Issue]) -> None:
    if not issues:
        return
    _echo(f"{label} ({len(issues)}):")
    for issue in issues:
        _echo(f"  {issue.render()}")


def _load(args: argparse.Namespace) -> Config:
    root = find_repo_root(Path(args.root) if getattr(args, "root", None) else None)
    return load_config(root)


def _rel(config: Config, path: Path) -> str:
    """Repo-relative when we can, absolute when the output is elsewhere."""
    try:
        return str(path.relative_to(config.root))
    except ValueError:
        return str(path)


def _out_dir(args: argparse.Namespace) -> Path | None:
    return Path(args.out).resolve() if getattr(args, "out", None) else None


def cmd_build(args: argparse.Namespace) -> int:
    config = _load(args)
    upstream = Path(args.upstream_path).resolve() if args.upstream_path else None
    out = _out_dir(args)
    builder = Builder(
        config,
        upstream_path=upstream,
        report_anchors=args.report_anchors,
        out_dir=out,
    )
    result = builder.build(args.bundle)
    cards = {
        skill.name: skill.card for built in result.bundles for skill in built.skills
    }
    errors: list[Issue] = list(result.errors)
    warnings: list[Issue] = []
    suppressed: list[Suppression] = []
    for built in result.bundles:
        bundle_errors, bundle_warnings = validate_bundle(
            config,
            built.bundle,
            cards=cards,
            skill_names=builder.skill_names,
            upstream_path=upstream,
            out_dir=out,
            suppressed=suppressed,
        )
        errors += bundle_errors
        warnings += bundle_warnings
        _echo(
            f"{pkg.summarise(built)}, {len(bundle_errors)} errors, "
            f"{len(bundle_warnings)} warnings"
        )
    _report_issues("anchor failures", result.anchors)
    _report_issues("errors", errors)
    _report_issues("warnings", warnings)
    if suppressed:
        _echo(f"{len(suppressed)} warning(s) suppressed by card decisions")
    return EXIT_INVALID if (result.anchors or errors) else EXIT_OK


def cmd_validate(args: argparse.Namespace) -> int:
    config = _load(args)
    out = _out_dir(args)
    bundles = config.select(args.bundle)
    names = sorted({name for b in bundles for name in b.skills})
    cards = load_cards(config, names)
    skill_names = upstream_skill_names(config)
    suppressed: list[Suppression] = []
    status = EXIT_OK
    for bundle in bundles:
        errors, warnings = validate_bundle(
            config,
            bundle,
            cards=cards,
            skill_names=skill_names,
            out_dir=out,
            suppressed=suppressed,
        )
        _echo(
            f"{bundle.id}: {len(bundle.skills)} skills, {len(errors)} errors, "
            f"{len(warnings)} warnings"
        )
        _report_issues("errors", errors)
        _report_issues("warnings", warnings)
        if errors:
            status = EXIT_INVALID
    if suppressed:
        _echo(f"{len(suppressed)} warning(s) suppressed by card decisions")
    return status


def cmd_package(args: argparse.Namespace) -> int:
    config = _load(args)
    out = _out_dir(args)
    builder = Builder(config, out_dir=out)
    result = builder.build(args.bundle)
    cards = {
        skill.name: skill.card for built in result.bundles for skill in built.skills
    }
    skill_names = builder.skill_names

    all_errors: list[Issue] = list(result.errors)
    all_warnings: list[Issue] = []
    all_suppressed: list[Suppression] = []
    for built in result.bundles:
        bundle = built.bundle
        errors, warnings = validate_bundle(
            config,
            bundle,
            cards=cards,
            skill_names=skill_names,
            out_dir=out,
            suppressed=all_suppressed,
        )
        archive = pkg.write_zip(config, bundle, out)
        errors += pkg.validate_zip_entries(config, bundle, archive)
        triggers = pkg.write_trigger_tests(config, bundle, cards, out)
        all_errors += errors
        all_warnings += warnings
        _echo(
            f"{pkg.summarise(built)}, {archive.stat().st_size:,} bytes zipped, "
            f"{len(errors)} errors, {len(warnings)} warnings"
        )
        _echo(f"  {_rel(config, archive)}")
        _echo(f"  {_rel(config, triggers)}")

    report = pkg.write_build_report(
        config,
        result,
        errors=all_errors,
        warnings=all_warnings,
        suppressed=all_suppressed,
        out_dir=out,
    )
    _echo(f"  {_rel(config, report)}")
    _report_issues("errors", all_errors)
    _report_issues("warnings", all_warnings)
    if all_suppressed:
        _echo(f"{len(all_suppressed)} warning(s) suppressed by card decisions")
    return EXIT_INVALID if (all_errors or result.anchors) else EXIT_OK


def cmd_triggers(args: argparse.Namespace) -> int:
    config = _load(args)
    out = _out_dir(args)
    bundles = config.select(args.bundle)
    names = sorted({name for b in bundles for name in b.skills})
    cards = load_cards(config, names)
    for bundle in bundles:
        target = pkg.write_trigger_tests(config, bundle, cards, out)
        count = sum(
            len(cards[n].triggers.positive) + len(cards[n].triggers.negative)
            for n in bundle.skills
        )
        _echo(f"{bundle.id}: {count} prompts -> {_rel(config, target)}")
    return EXIT_OK


def cmd_bump(args: argparse.Namespace) -> int:
    config = _load(args)
    report_path = Path(args.report).resolve() if args.report else None
    status, target, report = bump_upstream(
        config, to=args.to, dry_run=args.dry_run, report_path=report_path
    )
    _echo(f"upstream {report.from_sha[:7]} -> {report.to_sha[:7]}")
    moved = [s.name for s in report.skills if s.interesting]
    _echo(
        f"{len(moved)} adapted skills moved upstream, "
        f"{len(report.anchors)} anchor failures, {len(report.errors)} errors, "
        f"{len(report.warnings)} warnings"
    )
    _echo(f"report: {target}")
    if args.dry_run:
        _echo("dry run: the submodule and cowork.yaml were not touched")
    elif report.from_sha != report.to_sha:
        _echo("submodule checked out and cowork.yaml pinned; next: review the")
        _echo("report, fix the cards, re-run `make package`, then `make anchor`")
    return status


def cmd_anchor(args: argparse.Namespace) -> int:
    config = _load(args)
    updated = anchor(config, args.skill)
    if updated:
        _echo(
            f"anchored {len(updated)} card(s) to {config.sha7}: " + ", ".join(updated)
        )
    else:
        _echo(f"every card is already anchored to {config.sha7}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lqcowork",
        description=(
            "Turn the vendored LegalQuants skills into Microsoft 365 Copilot "
            "Cowork plugin packages. See docs/CONTRACT.md."
        ),
    )
    parser.add_argument(
        "--root",
        help="start the search for cowork.yaml here instead of the cwd",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build dist/<bundle>/ trees")
    build.add_argument("--bundle", help="build only this bundle id")
    build.add_argument(
        "--report-anchors",
        action="store_true",
        help="report anchor failures instead of failing the build",
    )
    build.add_argument(
        "--upstream-path", help="build against this checkout of upstream"
    )
    build.add_argument("--out", help="output directory (default: dist)")
    build.set_defaults(func=cmd_build)

    validate = subparsers.add_parser(
        "validate", help="validate dist/<bundle>/ without rebuilding"
    )
    validate.add_argument("--bundle", help="validate only this bundle id")
    validate.add_argument("--out", help="output directory (default: dist)")
    validate.set_defaults(func=cmd_validate)

    package = subparsers.add_parser(
        "package", help="build + validate + zip + trigger tests + report"
    )
    package.add_argument("--bundle", help="package only this bundle id")
    package.add_argument("--out", help="output directory (default: dist)")
    package.set_defaults(func=cmd_package)

    bump = subparsers.add_parser(
        "bump-upstream", help="fetch upstream, report the drift, move the pin"
    )
    bump.add_argument("--to", default="origin/main", help="upstream ref (or SHA)")
    bump.add_argument(
        "--dry-run",
        action="store_true",
        help="report only; never move the submodule or the pin",
    )
    bump.add_argument("--report", help="write the report here")
    bump.set_defaults(func=cmd_bump)

    anchor_cmd = subparsers.add_parser(
        "anchor", help="set anchored_to to the current pin after review"
    )
    anchor_cmd.add_argument("--skill", help="anchor only this skill's card")
    anchor_cmd.set_defaults(func=cmd_anchor)

    triggers = subparsers.add_parser(
        "triggers", help="write dist/<bundle>-trigger-tests.md only"
    )
    triggers.add_argument("--bundle", help="only this bundle id")
    triggers.add_argument("--out", help="output directory (default: dist)")
    triggers.set_defaults(func=cmd_triggers)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except AnchorFailure as exc:
        print(f"anchor failure: {exc}", file=sys.stderr)
        return EXIT_INVALID
    except (ConfigError, BuildError, BumpError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
