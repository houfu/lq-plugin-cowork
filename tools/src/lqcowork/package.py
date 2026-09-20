"""Zip assembly, trigger-test checklists and the build report."""

from __future__ import annotations

import os
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .build import (
    SKILL_ARCHIVE_DIR,
    SKILL_ARCHIVE_SUFFIX,
    BuildResult,
    BundleBuild,
    Issue,
    SkillBuild,
    Suppression,
    build_manifest,
    dist_root,
)
from .config import Bundle, Card, Config, builtin_name, split_negative
from .validate import validate_zip


def zip_path(config: Config, bundle: Bundle, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / f"{bundle.id}.zip"


def trigger_path(config: Config, bundle: Bundle, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / f"{bundle.id}-trigger-tests.md"


def report_path(config: Config, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / "build-report.md"


def allowed_roots(config: Config) -> set[str]:
    roots = {"manifest.json", "color.png", "outline.png", "skills"}
    roots |= {Path(rel).name for rel in config.root_files}
    return roots


def skill_archive_dir(config: Config, out_dir: Path | None = None) -> Path:
    return dist_root(config, out_dir) / SKILL_ARCHIVE_DIR


def skill_archive_path(config: Config, name: str, out_dir: Path | None = None) -> Path:
    return skill_archive_dir(config, out_dir) / f"{name}{SKILL_ARCHIVE_SUFFIX}"


@dataclass(frozen=True)
class SkillArchive:
    """One written ``<out>/skills/<name>.skill`` and its measurements."""

    name: str
    path: Path
    files: int
    compressed_bytes: int

    def summary(self) -> str:
        """The one-line summary `package` prints under the bundle lines."""
        return (
            f"{SKILL_ARCHIVE_DIR}/{self.path.name}: {self.files} files, "
            f"{self.compressed_bytes:,} bytes"
        )


def _packable(rel: str) -> bool:
    """Paths a package never carries: dotfiles and macOS resource forks."""
    if any(part.startswith(".") for part in rel.split("/")):
        return False
    return rel.split("/", 1)[0] != "__MACOSX"


def _tree_entries(source: Path) -> list[tuple[str, bytes]]:
    """Every packable file under ``source``, keyed by its archive path."""
    return [
        (rel, path.read_bytes())
        for rel, path in (
            (p.relative_to(source).as_posix(), p)
            for p in source.rglob("*")
            if p.is_file()
        )
        if _packable(rel)
    ]


def _write_archive(target: Path, entries: list[tuple[str, bytes]]) -> Path:
    """Write a deterministic zip: sorted entries, fixed stamps, fixed modes.

    Two builds of the same tree produce equal bytes, which is what the
    release workflow re-checks before it publishes anything.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    stamp = _zip_timestamp()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for rel, payload in sorted(entries, key=lambda entry: entry[0]):
            info = zipfile.ZipInfo(rel, date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, payload)
    return target


def write_zip(config: Config, bundle: Bundle, out_dir: Path | None = None) -> Path:
    """Zip ``<out>/<bundle>/`` with everything at the archive root."""
    source = dist_root(config, out_dir) / bundle.id
    return _write_archive(zip_path(config, bundle, out_dir), _tree_entries(source))


def root_file_entries(config: Config, bundle_dir: Path) -> list[tuple[str, bytes]]:
    """`LICENSE` and `NOTICE.md` as the built package already carries them."""
    entries: list[tuple[str, bytes]] = []
    for rel in config.root_files:
        path = bundle_dir / Path(rel).name
        if path.is_file():
            entries.append((path.name, path.read_bytes()))
    return entries


def write_skill_archive(
    config: Config,
    skill: SkillBuild,
    root_files: list[tuple[str, bytes]],
    out_dir: Path | None = None,
) -> SkillArchive:
    """Write ``<out>/skills/<name>.skill``: one skill, ready to upload.

    Contents sit at the archive root exactly as they sit in the bundle tree —
    the built SKILL.md and its companions — plus the package's own root
    files, because an archive uploaded on its own carries no package around
    it to hold the licence and the notice.
    """
    entries = _tree_entries(skill.path) + list(root_files)
    target = _write_archive(skill_archive_path(config, skill.name, out_dir), entries)
    return SkillArchive(
        name=skill.name,
        path=target,
        files=len(entries),
        compressed_bytes=target.stat().st_size,
    )


def write_skill_archives(
    config: Config, result: BuildResult, out_dir: Path | None = None
) -> list[SkillArchive]:
    """One archive per distinct skill in the build, in name order.

    A skill that ships in several bundles is built once and archived once.
    """
    archives: list[SkillArchive] = []
    seen: set[str] = set()
    for built in result.bundles:
        root_files = root_file_entries(config, built.path)
        for skill in built.skills:
            if skill.name in seen:
                continue
            seen.add(skill.name)
            archives.append(write_skill_archive(config, skill, root_files, out_dir))
    return sorted(archives, key=lambda archive: archive.name)


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


def _mirror_lines(bundle: Bundle) -> list[str]:
    """How a mirrored bundle got its membership, and what upstream calls it."""
    if bundle.mirror is None:
        return ["- membership: an explicit `skills` list in cowork.yaml"]
    mirror = bundle.mirror
    lines = [f"- {mirror.line()}"]
    lines.append(f"- upstream name: {mirror.display_name}")
    if mirror.short_description:
        lines.append(f"- upstream description: {mirror.short_description}")
    for entry in mirror.excludes:
        lines.append(f"  - excluded `{entry.name}`: {entry.reason}")
    return lines


def _known_issue_lines(built: BundleBuild) -> list[str]:
    """Every known issue the bundle's cards declare, in bundle order."""
    rows = [
        (skill.name, known)
        for skill in built.skills
        for known in (skill.card.cowork.known_issues if skill.card.cowork else ())
    ]
    if not rows:
        return []
    lines = [
        "### Known issues",
        "",
        "Declared on the cards; the site and the UAT programme read the same list.",
        "",
        "| Id | Skill | Title | Failure | Probe |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name, known in rows:
        lines.append(
            f"| `{known.id}` | {name} | {_escape(known.title)} | "
            f"{known.failure} | {known.probe or ''} |"
        )
    lines.append("")
    return lines


def _archive_table(archives: list[SkillArchive]) -> list[str]:
    """Every per-skill upload archive the build wrote, with its size."""
    if not archives:
        return []
    lines = [
        "## Skill archives",
        "",
        "One upload-ready archive per skill, for Cowork's Customize page.",
        "",
        "| Skill | Files | Bytes |",
        "| --- | ---: | ---: |",
    ]
    for archive in archives:
        lines.append(
            f"| {archive.name} | {archive.files} | {archive.compressed_bytes:,} |"
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
    archives: list[SkillArchive] | None = None,
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
        ]
        lines += _mirror_lines(built.bundle)
        lines += [
            "",
            "| Skill | Bucket | Tier | Status | Known issues | Files | Bytes "
            "| Warnings |",
            "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: |",
        ]
        for skill in built.skills:
            count = sum(
                1
                for w in warnings
                if w.skill == skill.name and w.bundle == built.bundle.id
            )
            block = skill.card.cowork
            tier = str(block.tier) if block else "—"
            status = block.status if block else "—"
            known = len(block.known_issues) if block else 0
            lines.append(
                f"| {skill.name} | {skill.card.bucket} | {tier} | {status} | "
                f"{known} | {len(skill.files)} | {skill.total_bytes} | {count} |"
            )
        lines.append("")
        lines += _known_issue_lines(built)
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

    lines += _archive_table(archives or [])
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
