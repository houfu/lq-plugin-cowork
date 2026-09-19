"""Zip assembly, trigger-test checklists and the build report."""

from __future__ import annotations

import os
import time
import zipfile
from pathlib import Path

from .build import (
    BuildError,
    BuildResult,
    BundleBuild,
    Issue,
    Suppression,
    build_manifest,
    dist_root,
)
from .config import Bundle, Card, Config, builtin_name, split_negative
from .validate import validate_skill_archive, validate_zip


def zip_path(config: Config, bundle: Bundle, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / f"{bundle.id}.zip"


def trigger_path(config: Config, bundle: Bundle, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / f"{bundle.id}-trigger-tests.md"


def report_path(config: Config, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / "build-report.md"


def skill_archive_dir(config: Config, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / "skills"


def skill_archive_path(config: Config, name: str, out_dir: Path | None = None) -> Path:
    return skill_archive_dir(config, out_dir) / f"{name}.skill"


def allowed_roots(config: Config) -> set[str]:
    roots = {"manifest.json", "color.png", "outline.png", "skills"}
    roots |= {Path(rel).name for rel in config.root_files}
    return roots


def write_zip(config: Config, bundle: Bundle, out_dir: Path | None = None) -> Path:
    """Zip ``<out>/<bundle>/`` with everything at the archive root."""
    source = dist_root(config, out_dir) / bundle.id
    return _write_archive(
        zip_path(config, bundle, out_dir),
        [
            (p.relative_to(source).as_posix(), p)
            for p in source.rglob("*")
            if p.is_file()
        ],
    )


def _write_archive(target: Path, entries: list[tuple[str, Path]]) -> Path:
    """The one zip writer: sorted entries, fixed stamps, deflate, no dotfiles.

    Bundle packages and single-skill archives share it so both are
    byte-reproducible in the same way.
    """
    if target.exists():
        target.unlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    stamp = _zip_timestamp()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for rel, path in sorted(entries):
            if any(part.startswith(".") for part in rel.split("/")):
                continue
            if rel.split("/", 1)[0] == "__MACOSX":
                continue
            info = zipfile.ZipInfo(rel, date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return target


def _zip_timestamp() -> tuple[int, int, int, int, int, int]:
    """A fixed entry timestamp, so two identical builds zip to equal bytes.

    1980-01-01 is the earliest a zip entry can record. ``SOURCE_DATE_EPOCH``
    overrides it for anyone who wants the package dated.
    """
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        try:
            return time.gmtime(int(epoch))[:6]
        except (ValueError, OSError):
            pass
    return (1980, 1, 1, 0, 0, 0)


def validate_zip_entries(config: Config, bundle: Bundle, archive: Path) -> list[Issue]:
    """LQC-Z001 against the archive we just wrote."""
    return validate_zip(archive, bundle.id, allowed_roots(config))


def skill_bundles(bundles: list[Bundle]) -> dict[str, list[str]]:
    """Every distinct skill in ``bundles``, mapped to the ids that ship it.

    A skill in two bundles is built once and archived once, so this is what
    decides both the archive list and the report's "Bundles" column.
    """
    shipped: dict[str, list[str]] = {}
    for bundle in bundles:
        for name in bundle.skills:
            shipped.setdefault(name, []).append(bundle.id)
    return dict(sorted(shipped.items()))


def _built_skill_dir(
    config: Config, bundle_id: str, name: str, out_dir: Path | None
) -> Path:
    """The built folder an archive is made from; the bundle must exist."""
    bundle_dir = dist_root(config, out_dir) / bundle_id
    if not bundle_dir.is_dir():
        raise BuildError(f"{bundle_dir} does not exist; run build first")
    skill_dir = bundle_dir / "skills" / name
    if not skill_dir.is_dir():
        raise BuildError(f"{skill_dir} does not exist; run build first")
    return skill_dir


def write_skill_archives(
    config: Config, bundles: list[Bundle], out_dir: Path | None = None
) -> list[Path]:
    """One upload-ready ``dist/skills/<name>.skill`` per distinct skill.

    Contract section 5b: the built skill folder at the archive root, plus the
    licence and the notice, because Apache-2.0 travels with every
    distribution and a skill uploaded on its own is one.
    """
    root_files = [(Path(rel).name, config.root / rel) for rel in config.root_files]
    for rel, source in root_files:
        if not source.is_file():
            raise BuildError(f"{rel}: root file not found")
    written: list[Path] = []
    for name, bundle_ids in skill_bundles(bundles).items():
        source = _built_skill_dir(config, bundle_ids[0], name, out_dir)
        entries = [
            (path.relative_to(source).as_posix(), path)
            for path in source.rglob("*")
            if path.is_file()
        ]
        entries += root_files
        written.append(
            _write_archive(skill_archive_path(config, name, out_dir), entries)
        )
    return written


def validate_skill_archives(
    config: Config,
    bundles: list[Bundle],
    archives: list[Path],
    out_dir: Path | None = None,
) -> list[Issue]:
    """LQC-U001..U005 against the single-skill archives we just wrote."""
    shipped = skill_bundles(bundles)
    issues: list[Issue] = []
    for archive in archives:
        name = archive.stem
        bundle_ids = shipped.get(name)
        if not bundle_ids:
            continue
        skill_dir = _built_skill_dir(config, bundle_ids[0], name, out_dir)
        issues += validate_skill_archive(archive, name, skill_dir)
    return issues


def _escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def expected_handoff(bundle: Bundle, target: str) -> str:
    """Render a negative trigger's ``-> target`` for the checklist table.

    A target outside this bundle cannot take the request, so the honest
    expectation there is that nothing activates.
    """
    if not target:
        return "must not activate"
    if target.lower() == "none":
        return "must not activate; expect `none`"
    builtin = builtin_name(target)
    if builtin is not None:
        return f"must not activate; expect built-in {builtin}"
    if target in bundle.skills:
        return f"must not activate; expect `{target}`"
    return f"must not activate; expect none ({target} is not in this bundle)"


def write_trigger_tests(
    config: Config,
    bundle: Bundle,
    cards: dict[str, Card],
    out_dir: Path | None = None,
) -> Path:
    """One checklist table per skill, with an empty Result column."""
    lines = [
        f"# Trigger tests — {bundle.name_full}",
        "",
        f"Bundle `{bundle.id}`, version {config.version}, "
        f"upstream `{config.sha7}`.",
        "",
        "Sideload the package, then type each prompt into Cowork in a fresh",
        "session and record what actually activated. A positive prompt must",
        "activate the named skill; a negative prompt must not — the arrow says",
        "which skill should take it instead.",
        "",
    ]
    for name in bundle.skills:
        card = cards.get(name)
        if card is None:
            continue
        lines += [
            f"## {name}",
            "",
            "| Prompt | Expected | Result |",
            "| --- | --- | --- |",
        ]
        for prompt in card.triggers.positive:
            lines.append(f"| {_escape(prompt)} | activate `{name}` |  |")
        for prompt in card.triggers.negative:
            text, target = split_negative(prompt)
            lines.append(f"| {_escape(text)} | {expected_handoff(bundle, target)} |  |")
        lines.append("")
    target = trigger_path(config, bundle, out_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return target


def _issue_table(title: str, issues: list[Issue]) -> list[str]:
    if not issues:
        return [f"{title}: none.", ""]
    lines = [
        title + ":",
        "",
        "| Code | Bundle | Skill | Where | Detail |",
        "| --- | --- | --- | --- | --- |",
    ]
    for issue in issues:
        lines.append(
            f"| {issue.code} | {issue.bundle or ''} | {issue.skill or ''} | "
            f"{issue.location or ''} | {_escape(issue.message)} |"
        )
    lines.append("")
    return lines


def _suppressed_table(suppressed: list[Suppression]) -> list[str]:
    """Every warning a card accepted, so the decision stays auditable."""
    if not suppressed:
        return ["## Suppressed warnings: none.", ""]
    lines = [
        "## Suppressed warnings",
        "",
        "Accepted in the card, with the reason given there.",
        "",
        "| Bundle | Skill | Code | File | Reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in suppressed:
        issue = entry.issue
        lines.append(
            f"| {issue.bundle or ''} | {issue.skill or ''} | {issue.code} | "
            f"{entry.pattern or issue.location or 'any'} | {_escape(entry.reason)} |"
        )
    lines.append("")
    return lines


def _archive_table(result: BuildResult, archives: list[Path]) -> list[str]:
    """What each ``dist/skills/<name>.skill`` holds, and who ships that skill."""
    if not archives:
        return []
    shipped = skill_bundles([built.bundle for built in result.bundles])
    lines = [
        "## Single-skill archives",
        "",
        "Upload-ready, one per skill, for Cowork's Upload skill control",
        "(contract section 5b).",
        "",
        "| Archive | Entries | Compressed | Uncompressed | Bundles |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for archive in archives:
        name = archive.stem
        with zipfile.ZipFile(archive) as opened:
            infos = opened.infolist()
        bundles = ", ".join(shipped.get(name, []))
        lines.append(
            f"| `skills/{archive.name}` | {len(infos)} | "
            f"{archive.stat().st_size:,} | "
            f"{sum(info.file_size for info in infos):,} | {bundles} |"
        )
    lines.append("")
    return lines


def write_build_report(
    config: Config,
    result: BuildResult,
    *,
    errors: list[Issue] | None = None,
    warnings: list[Issue] | None = None,
    suppressed: list[Suppression] | None = None,
    archives: list[Path] | None = None,
    out_dir: Path | None = None,
) -> Path:
    """dist/build-report.md — per skill and per bundle, plus every issue."""
    errors = errors or []
    warnings = list(warnings or []) + list(result.warnings)
    lines = [
        "# Build report",
        "",
        f"Upstream `LegalQuants/lq-plugin-oss@{config.sha7}`, "
        f"package version {config.version}.",
        "",
    ]
    for built in result.bundles:
        manifest = build_manifest(config, built.bundle)
        lines += [
            f"## {built.bundle.id}",
            "",
            f"- name: {manifest['name']['full']} ({manifest['name']['short']})",
            f"- id: `{manifest['id']}`",
            f"- manifestVersion: {manifest['manifestVersion']}, "
            f"version: {manifest['version']}",
            f"- skills: {len(built.skills)}",
            "",
            "| Skill | Bucket | Files | Bytes | Warnings |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
        for skill in built.skills:
            count = sum(
                1
                for w in warnings
                if w.skill == skill.name and w.bundle == built.bundle.id
            )
            lines.append(
                f"| {skill.name} | {skill.card.bucket} | {len(skill.files)} | "
                f"{skill.total_bytes} | {count} |"
            )
        lines.append("")
        unnoticed = [s for s in built.skills if s.unnoticed]
        if unnoticed:
            lines += [
                "### Companions changed without an in-file notice",
                "",
                "Non-Markdown companions the build cannot annotate; the card's",
                "`notes` must account for each one.",
                "",
                "| Skill | Path |",
                "| --- | --- |",
            ]
            for skill in unnoticed:
                for rel in skill.unnoticed:
                    lines.append(f"| {skill.name} | {rel} |")
            lines.append("")

        amber = [s for s in built.skills if s.card.bucket == "amber" and s.card.notes]
        if amber:
            lines += ["### Adaptation notes", ""]
            for skill in amber:
                note = " ".join((skill.card.notes or "").split())
                lines.append(f"- **{skill.name}** — {note}")
            lines.append("")

    lines += _archive_table(result, list(archives or []))
    lines += _suppressed_table(suppressed or [])
    lines += _issue_table("## Errors", errors)
    lines += _issue_table("## Anchor failures", result.anchors)
    lines += _issue_table("## Warnings", warnings)
    target = report_path(config, out_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return target


def summarise(built: BundleBuild) -> str:
    """The one-line per-bundle summary every command prints."""
    files = sum(len(skill.files) for skill in built.skills)
    size = sum(skill.total_bytes for skill in built.skills)
    return (
        f"{built.bundle.id}: {len(built.skills)} skills, {files} files, "
        f"{size:,} bytes"
    )
