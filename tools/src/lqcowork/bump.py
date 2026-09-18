"""``bump-upstream`` and ``anchor``: track upstream and report the drift."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from . import transforms
from .build import Builder, BuildError, Issue
from .config import Card, Config, ConfigError, load_cards
from .validate import validate_bundle

SHA_LINE_RE = re.compile(r"^(\s*sha:\s*)[0-9a-f]{40}", re.M)
ANCHOR_LINE_RE = re.compile(r"^(\s*anchored_to:\s*)[0-9a-f]{40}", re.M)


class BumpError(Exception):
    """git could not be driven to completion."""


@dataclass
class SkillDrift:
    name: str
    upstream: str
    anchored_to: str
    missing: bool = False
    skill_md_changed: bool = False
    diffstat: str = ""
    description_changed: bool = False
    overlay_stale: bool = False
    companions_added: list[str] = field(default_factory=list)
    companions_removed: list[str] = field(default_factory=list)

    @property
    def interesting(self) -> bool:
        return bool(
            self.missing
            or self.skill_md_changed
            or self.description_changed
            or self.overlay_stale
            or self.companions_added
            or self.companions_removed
        )


@dataclass
class DriftReport:
    from_sha: str
    to_sha: str
    skills: list[SkillDrift] = field(default_factory=list)
    anchors: list[Issue] = field(default_factory=list)
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    unbundled: list[str] = field(default_factory=list)
    build_error: str | None = None

    @property
    def broken(self) -> bool:
        return bool(self.anchors or self.errors or self.build_error)

    @property
    def has_changes(self) -> bool:
        return bool(
            self.from_sha != self.to_sha
            or any(skill.interesting for skill in self.skills)
            or self.broken
        )


def _git(args: list[str], cwd: Path, *, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise BumpError(
            f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout}"
        )
    return result.stdout


def _git_ok(args: list[str], cwd: Path) -> tuple[bool, str]:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout


def resolve_ref(upstream: Path, ref: str) -> str:
    out = _git(["rev-parse", f"{ref}^{{commit}}"], upstream).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", out):
        raise BumpError(f"could not resolve '{ref}' to a commit")
    return out


def _tree_files(upstream: Path, sha: str, path: str) -> set[str]:
    ok, out = _git_ok(["ls-tree", "-r", "--name-only", sha, "--", path], upstream)
    if not ok:
        return set()
    prefix = path.rstrip("/") + "/"
    return {line[len(prefix) :] for line in out.splitlines() if line.startswith(prefix)}


def _show(upstream: Path, sha: str, path: str) -> str | None:
    ok, out = _git_ok(["show", f"{sha}:{path}"], upstream)
    return out if ok else None


def _description_of(text: str | None) -> str | None:
    if text is None:
        return None
    try:
        return str(transforms.parse_document(text).frontmatter.get("description", ""))
    except transforms.TransformError:
        return None


def collect_drift(
    config: Config,
    upstream: Path,
    to_sha: str,
    cards: dict[str, Card],
    *,
    worktree: Path,
) -> DriftReport:
    """Build against ``worktree`` and gather everything the report needs."""
    report = DriftReport(from_sha=config.sha, to_sha=to_sha)

    for name in sorted(cards):
        card = cards[name]
        rel = f"{config.skills_root}/{card.upstream}"
        drift = SkillDrift(
            name=name, upstream=card.upstream, anchored_to=card.anchored_to
        )
        if not (worktree / rel).is_dir():
            drift.missing = True
            report.skills.append(drift)
            continue
        ok, stat = _git_ok(
            ["diff", "--stat", f"{card.anchored_to}..{to_sha}", "--", rel], upstream
        )
        if ok:
            drift.diffstat = stat.strip()
        before = _show(upstream, card.anchored_to, f"{rel}/SKILL.md")
        after = _show(upstream, to_sha, f"{rel}/SKILL.md")
        drift.skill_md_changed = before != after
        old_desc = _description_of(before)
        new_desc = _description_of(after)
        drift.description_changed = old_desc is not None and old_desc != new_desc
        if card.overlay.is_file() and drift.skill_md_changed:
            drift.overlay_stale = True
        old_files = _tree_files(upstream, card.anchored_to, rel)
        new_files = _tree_files(upstream, to_sha, rel)
        drift.companions_added = sorted(new_files - old_files)
        drift.companions_removed = sorted(old_files - new_files)
        report.skills.append(drift)

    try:
        builder = Builder(config, upstream_path=worktree, report_anchors=True)
        result = builder.build()
        report.anchors = list(result.anchors)
        report.errors.extend(result.errors)
        for built in result.bundles:
            errors, warnings = validate_bundle(
                config,
                built.bundle,
                cards=cards,
                skill_names=builder.skill_names,
                upstream_path=worktree,
            )
            report.errors.extend(errors)
            report.warnings.extend(warnings)
        bundled = {n for bundle in config.bundles for n in bundle.skills}
        report.unbundled = [n for n in sorted(builder.skill_names) if n not in bundled]
    except (BuildError, ConfigError) as exc:
        report.build_error = str(exc)
    return report


def render_report(config: Config, report: DriftReport) -> str:
    lines = [
        "# Upstream drift report",
        "",
        f"- from: `{report.from_sha}`",
        f"- to: `{report.to_sha}`",
        f"- repo: {config.repo}",
        # a machine-readable marker the drift workflow greps for
        f"- changed: {'yes' if report.has_changes else 'no'}",
        "",
    ]
    if report.from_sha == report.to_sha:
        lines += ["The pin is already current.", ""]
    if report.build_error:
        lines += ["## Build failed", "", "```", report.build_error, "```", ""]

    changed = [s for s in report.skills if s.interesting]
    lines += ["## Skills that moved upstream", ""]
    if not changed:
        lines += ["No adapted skill changed upstream.", ""]
    else:
        lines += ["| Skill | Upstream | What changed |", "| --- | --- | --- |"]
        for skill in changed:
            notes = []
            if skill.missing:
                notes.append("**upstream folder is gone**")
            if skill.skill_md_changed:
                notes.append("SKILL.md changed")
            if skill.description_changed:
                notes.append("description changed")
            if skill.overlay_stale:
                notes.append("full-file overlay may be stale")
            if skill.companions_added:
                notes.append(f"added: {', '.join(skill.companions_added)}")
            if skill.companions_removed:
                notes.append(f"removed: {', '.join(skill.companions_removed)}")
            lines.append(f"| {skill.name} | `{skill.upstream}` | {'; '.join(notes)} |")
        lines.append("")

    for title, issues in (
        ("## Anchor failures", report.anchors),
        ("## Validation errors", report.errors),
        ("## Warnings", report.warnings),
    ):
        lines += [title, ""]
        if not issues:
            lines += ["None.", ""]
            continue
        lines += ["| Code | Bundle | Skill | Detail |", "| --- | --- | --- | --- |"]
        for issue in issues:
            detail = issue.detail().replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {issue.code} | {issue.bundle or ''} | {issue.skill or ''} "
                f"| {detail} |"
            )
        lines.append("")

    lines += ["## Upstream skills in no bundle", ""]
    if report.unbundled:
        lines += [f"- {name}" for name in report.unbundled]
    else:
        lines.append("None.")
    lines += [
        "",
        "## Next steps",
        "",
        "1. Read the rows above and decide what each change means for the card.",
        "2. Fix any anchor failure in `skills/<name>/skill.yaml`.",
        "3. Re-run `make package`.",
        "4. Run `make anchor` to record the new pin in every card you reviewed.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def bump_upstream(
    config: Config,
    *,
    to: str = "origin/main",
    dry_run: bool = False,
    report_path: Path | None = None,
) -> tuple[int, Path, DriftReport]:
    """Fetch, diff against a temporary worktree, write the report, maybe pin."""
    upstream = config.root / config.upstream_path
    if not (upstream / ".git").exists():
        raise BumpError(f"{upstream}: not a git checkout (is the submodule init'd?)")
    _git(["fetch", "origin", "--tags"], upstream)
    to_sha = resolve_ref(upstream, to)

    names = sorted({name for bundle in config.bundles for name in bundle.skills})
    cards = load_cards(config, names)

    tmp = Path(tempfile.mkdtemp(prefix="lqcowork-upstream-"))
    worktree = tmp / "upstream"
    try:
        _git(["worktree", "add", "--detach", str(worktree), to_sha], upstream)
        report = collect_drift(config, upstream, to_sha, cards, worktree=worktree)
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree)],
            cwd=upstream,
            capture_output=True,
            text=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)

    target = report_path or (config.root / "dist" / "upstream-drift.md")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_report(config, report), encoding="utf-8")

    if not dry_run and report.from_sha != report.to_sha:
        _git(["checkout", "--detach", to_sha], upstream)
        write_pin(config, to_sha)

    if report.build_error:
        return 1, target, report
    return (2 if report.broken else 0), target, report


def write_pin(config: Config, sha: str) -> None:
    """Rewrite ``upstream.sha`` in cowork.yaml, leaving comments intact."""
    path = config.root / "cowork.yaml"
    text = path.read_text(encoding="utf-8")
    new_text, count = SHA_LINE_RE.subn(rf"\g<1>{sha}", text, count=1)
    if count != 1:
        raise BumpError("cowork.yaml: could not find the upstream.sha line")
    path.write_text(new_text, encoding="utf-8")


def anchor(config: Config, skill: str | None = None) -> list[str]:
    """Set ``anchored_to`` to the current pin in one card or in every card."""
    names = (
        [skill]
        if skill
        else sorted({name for bundle in config.bundles for name in bundle.skills})
    )
    cards = load_cards(config, names)
    updated: list[str] = []
    for name in names:
        card = cards[name]
        if card.anchored_to == config.sha:
            continue
        path = card.directory / "skill.yaml"
        text = path.read_text(encoding="utf-8")
        new_text, count = ANCHOR_LINE_RE.subn(rf"\g<1>{config.sha}", text, count=1)
        if count != 1:
            raise BumpError(f"{path}: could not find the anchored_to line")
        path.write_text(new_text, encoding="utf-8")
        updated.append(name)
    return updated
