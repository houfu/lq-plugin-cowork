"""The per-skill build pipeline described in docs/CONTRACT.md section 5."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import transforms
from .config import (
    Bundle,
    Card,
    Config,
    ReplaceRule,
    load_cards,
    upstream_skill_names,
)

NOTICE_TEMPLATE = (
    "<!-- Modified from LegalQuants/lq-plugin-oss@{sha7} (skills/{upstream}) "
    "for Microsoft 365 Copilot Cowork. Apache-2.0; see LICENSE and NOTICE.md "
    "at the package root. -->"
)
NOTICE_MARKER = "<!-- Modified from LegalQuants/lq-plugin-oss@"

COMPANION_MODIFIED = (
    "<!-- Modified from LegalQuants/lq-plugin-oss@{sha7} "
    "(skills/{upstream}/{relpath}) for Microsoft 365 Copilot Cowork. "
    "Apache-2.0; see LICENSE and NOTICE.md at the package root. -->"
)
COMPANION_ADDED = (
    "<!-- Added by the lq-plugin-cowork adaptation of "
    "LegalQuants/lq-plugin-oss@{sha7}; not an upstream LegalQuants file. "
    "Apache-2.0; see LICENSE and NOTICE.md at the package root. -->"
)
ADDED_MARKER = "<!-- Added by the lq-plugin-cowork adaptation of"


def strip_leading_notice(text: str) -> str:
    """Drop a build notice (and its blank line) from the top of a file.

    Text without a notice comes back byte for byte unchanged.
    """
    lines = text.split("\n")
    index = 0
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index >= len(lines):
        return text
    if not (
        lines[index].startswith(NOTICE_MARKER) or lines[index].startswith(ADDED_MARKER)
    ):
        return text
    index += 1
    while index < len(lines) and not lines[index].strip():
        index += 1
    return "\n".join(lines[index:])


MANIFEST_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/teams/v1.28/"
    "MicrosoftTeams.schema.json"
)
MANIFEST_VERSION = "1.28"


class BuildError(Exception):
    """The build cannot continue (missing source, unwritable output)."""


class AnchorFailure(BuildError):
    """An adaptation no longer applies (LQC-A001); exit code 2, not 1."""


@dataclass
class Issue:
    """One validation error, anchor failure or warning."""

    code: str
    message: str
    skill: str | None = None
    bundle: str | None = None
    # "<relative path>:<line>" inside the built skill, when the rule has one
    location: str | None = None

    def detail(self) -> str:
        return f"{self.location}: {self.message}" if self.location else self.message

    def render(self) -> str:
        scope = " ".join(p for p in (self.bundle, self.skill) if p)
        return (
            f"{self.code} {scope}: {self.detail()}"
            if scope
            else (f"{self.code}: {self.detail()}")
        )


@dataclass
class Suppression:
    """A warning a card chose to accept, kept for the build report."""

    issue: Issue
    pattern: str | None
    reason: str


@dataclass
class SkillBuild:
    name: str
    card: Card
    path: Path
    files: list[str] = field(default_factory=list)
    total_bytes: int = 0
    anchors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    # non-Markdown companions the build cannot annotate in place
    unnoticed: list[str] = field(default_factory=list)
    # symlinks refused on the way in (LQC-C007)
    symlinks: list[str] = field(default_factory=list)


@dataclass
class BundleBuild:
    bundle: Bundle
    path: Path
    skills: list[SkillBuild] = field(default_factory=list)


@dataclass
class BuildResult:
    bundles: list[BundleBuild] = field(default_factory=list)
    anchors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    errors: list[Issue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.anchors


class Builder:
    """Builds ``dist/<bundle>/`` trees from the vendored upstream skills."""

    def __init__(
        self,
        config: Config,
        *,
        upstream_path: Path | None = None,
        report_anchors: bool = False,
        out_dir: Path | None = None,
    ) -> None:
        self.config = config
        self.upstream_path = upstream_path
        self.out_dir = out_dir
        self.report_anchors = report_anchors
        self.skills_root = config.upstream_skills_root(upstream_path)
        self.skill_names = upstream_skill_names(config, upstream_path)
        self._records: dict[str, SkillBuild] = {}
        self._global_counts: dict[int, int] = {}
        self.result = BuildResult()

    # -- public ---------------------------------------------------------

    @property
    def dist(self) -> Path:
        return dist_root(self.config, self.out_dir)

    def build(self, bundle_id: str | None = None) -> BuildResult:
        bundles = self.config.select(bundle_id)
        names = sorted({name for b in bundles for name in b.skills})
        cards = load_cards(self.config, names)
        for bundle in bundles:
            self._build_bundle(bundle, cards)
        self._check_global_replace_counts()
        return self.result

    # -- internals ------------------------------------------------------

    def _anchor(self, issue: Issue) -> None:
        self.result.anchors.append(issue)
        if not self.report_anchors:
            raise AnchorFailure(issue.render())

    def _build_bundle(self, bundle: Bundle, cards: dict[str, Card]) -> None:
        dest = self.dist / bundle.id
        if dest.exists():
            shutil.rmtree(dest)
        (dest / "skills").mkdir(parents=True, exist_ok=True)

        record = BundleBuild(bundle=bundle, path=dest)
        for name in bundle.skills:
            card = cards[name]
            skill_dir = dest / "skills" / name
            cached = self._records.get(name)
            if cached is not None:
                shutil.copytree(cached.path, skill_dir)
                record.skills.append(cached)
                continue
            if not (self.skills_root / card.upstream).is_dir():
                message = (
                    f"upstream folder {self.config.skills_root}/{card.upstream} "
                    "does not exist"
                )
                if not self.report_anchors:
                    raise BuildError(f"skills/{name}: {message}")
                self.result.anchors.append(Issue("LQC-A001", message, name, bundle.id))
                continue
            built = self._build_skill(card, skill_dir, bundle)
            self._records[name] = built
            record.skills.append(built)

        self._copy_assets(dest)
        self._write_manifest(bundle, dest)
        self.result.bundles.append(record)

    def _copy_assets(self, dest: Path) -> None:
        root = self.config.root
        for rel, target in (
            (self.config.icon_color, "color.png"),
            (self.config.icon_outline, "outline.png"),
        ):
            source = root / rel
            if not source.is_file():
                raise BuildError(f"{rel}: icon not found")
            shutil.copy2(source, dest / target)
        for rel in self.config.root_files:
            source = self._resolve_root_file(rel)
            if not source.is_file():
                raise BuildError(f"{rel}: root file not found")
            shutil.copy2(source, dest / Path(rel).name)

    def _resolve_root_file(self, rel: str) -> Path:
        """Resolve a ``root_files`` entry, honouring ``--upstream-path``."""
        prefix = self.config.upstream_path.rstrip("/") + "/"
        if self.upstream_path is not None and rel.startswith(prefix):
            return self.upstream_path / rel[len(prefix) :]
        return self.config.root / rel

    def _write_manifest(self, bundle: Bundle, dest: Path) -> None:
        manifest = build_manifest(self.config, bundle)
        (dest / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # -- the per-skill pipeline ----------------------------------------

    def _build_skill(self, card: Card, dest: Path, bundle: Bundle) -> SkillBuild:
        source = self.skills_root / card.upstream
        if not source.is_dir():
            raise BuildError(
                f"skills/{card.name}: upstream folder "
                f"{self.config.skills_root}/{card.upstream} does not exist"
            )
        built = SkillBuild(name=card.name, card=card, path=dest)

        # 2. copy, honouring global strip + card exclude
        patterns = list(self.config.strip) + list(card.exclude)
        built.symlinks = _copy_tree(source, dest, patterns)

        # 3. full-file overlay
        if card.overlay.is_file():
            if not (source / "SKILL.md").is_file():
                self._anchor(
                    Issue(
                        "LQC-A001",
                        "overlay base missing: upstream has no SKILL.md",
                        card.name,
                        bundle.id,
                    )
                )
            shutil.copy2(card.overlay, dest / "SKILL.md")

        # 4. companion files directory
        if card.files:
            files_dir = card.directory / card.files
            if not files_dir.is_dir():
                raise BuildError(
                    f"skills/{card.name}: files directory '{card.files}' not found"
                )
            built.symlinks += _copy_tree(files_dir, dest, [])

        skill_md = dest / "SKILL.md"
        if not skill_md.is_file():
            raise BuildError(f"skills/{card.name}: no SKILL.md after copy")

        # 5. mechanical transforms
        self._drop_frontmatter(skill_md, card)
        for path in sorted(dest.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            original = text
            if self.config.transforms.strip_waivers:
                text = transforms.strip_waivers(text)
            if self.config.transforms.skill_tokens:
                text = transforms.rewrite_tokens(text, self.skill_names)
            if text != original:
                path.write_text(text, encoding="utf-8")

        # 6. replacements (global first, then the card's)
        for index, rule in enumerate(self.config.replace):
            count = self._apply_replace(dest, rule, card, bundle, check=False)
            self._global_counts[index] = self._global_counts.get(index, 0) + count
        for rule in card.replace:
            self._apply_replace(dest, rule, card, bundle, check=True)

        # 7. sections
        self._apply_sections(skill_md, card, bundle)

        # 8. patches
        self._apply_patches(dest, card, bundle)

        # 9-11. frontmatter overrides + stamp + serialise
        self._stamp(skill_md, card)

        # 10b. companion notices, and the non-Markdown companions we cannot
        # annotate in place.
        built.unnoticed = self._companion_notices(card, dest)

        for rel in sorted(set(built.symlinks)):
            self.result.errors.append(
                Issue(
                    "LQC-C007",
                    "symlink in skill folder (refused, not packaged)",
                    card.name,
                    bundle.id,
                    location=rel,
                )
            )

        built.files = sorted(
            p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()
        )
        built.total_bytes = sum((dest / rel).stat().st_size for rel in built.files)
        return built

    def _companion_notices(self, card: Card, dest: Path) -> list[str]:
        """Annotate changed/new Markdown companions; list the rest.

        A companion that is byte-identical to its upstream counterpart is left
        exactly as it is — that is what makes it exempt from LQC-W010 later.
        Non-Markdown companions are never rewritten by the build, so a changed
        or new one is reported instead.
        """
        source = self.skills_root / card.upstream
        unnoticed: list[str] = []
        for path in sorted(p for p in dest.rglob("*") if p.is_file()):
            rel = path.relative_to(dest).as_posix()
            if rel == "SKILL.md":
                continue
            upstream_file = source / rel
            upstream_bytes = (
                upstream_file.read_bytes() if upstream_file.is_file() else None
            )
            if path.suffix.lower() != ".md":
                if upstream_bytes is None or upstream_bytes != path.read_bytes():
                    unnoticed.append(rel)
                continue
            if upstream_bytes is not None and path.read_bytes() == upstream_bytes:
                continue
            body = strip_leading_notice(path.read_text(encoding="utf-8"))
            if upstream_bytes is not None:
                if body.encode("utf-8") == upstream_bytes:
                    path.write_text(body, encoding="utf-8")
                    continue
                notice = COMPANION_MODIFIED.format(
                    sha7=self.config.sha7, upstream=card.upstream, relpath=rel
                )
            else:
                notice = COMPANION_ADDED.format(sha7=self.config.sha7)
            path.write_text(notice + "\n\n" + body, encoding="utf-8")
        return unnoticed

    def _drop_frontmatter(self, skill_md: Path, card: Card) -> None:
        text = skill_md.read_text(encoding="utf-8")
        try:
            document = transforms.parse_document(text)
        except transforms.TransformError as exc:
            raise BuildError(f"skills/{card.name}/SKILL.md: {exc}") from exc
        for key in self.config.transforms.drop_frontmatter:
            document.frontmatter.pop(key, None)
        skill_md.write_text(transforms.render_document(document), encoding="utf-8")

    def _apply_replace(
        self,
        dest: Path,
        rule: ReplaceRule,
        card: Card,
        bundle: Bundle,
        *,
        check: bool,
    ) -> int:
        names = sorted(
            p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()
        )
        targets = transforms.glob_files(names, rule.files)
        total = 0
        for rel in targets:
            path = dest / rel
            text = path.read_text(encoding="utf-8")
            count = transforms.count_occurrences(text, rule.src)
            if count:
                total += count
                path.write_text(
                    transforms.replace_literal(text, rule.src, rule.dst),
                    encoding="utf-8",
                )
        if check:
            expected = rule.expect
            if (expected is not None and total != expected) or (
                expected is None and total == 0
            ):
                want = "at least 1" if expected is None else str(expected)
                self._anchor(
                    Issue(
                        "LQC-A001",
                        f"replace rule {rule.src!r} matched {total} time(s), "
                        f"expected {want}",
                        card.name,
                        bundle.id,
                    )
                )
        return total

    def _check_global_replace_counts(self) -> None:
        for index, rule in enumerate(self.config.replace):
            total = self._global_counts.get(index, 0)
            expected = rule.expect
            if (expected is not None and total != expected) or (
                expected is None and total == 0
            ):
                want = "at least 1" if expected is None else str(expected)
                self._anchor(
                    Issue(
                        "LQC-A001",
                        f"global replace rule {rule.src!r} matched {total} "
                        f"time(s) across the build, expected {want}",
                    )
                )

    def _apply_sections(self, skill_md: Path, card: Card, bundle: Bundle) -> None:
        for rule in card.sections:
            text = skill_md.read_text(encoding="utf-8")
            replacement: str | None = None
            if not rule.delete:
                assert rule.file is not None
                body_path = card.directory / rule.file
                if not body_path.is_file():
                    raise BuildError(
                        f"skills/{card.name}: section body '{rule.file}' not found"
                    )
                replacement = body_path.read_text(encoding="utf-8")
            try:
                skill_md.write_text(
                    transforms.apply_section(text, rule.match, replacement),
                    encoding="utf-8",
                )
            except transforms.TransformError as exc:
                self._anchor(Issue("LQC-A001", str(exc), card.name, bundle.id))

    def _apply_patches(self, dest: Path, card: Card, bundle: Bundle) -> None:
        for rel in card.patches:
            patch = card.directory / rel
            if not patch.is_file():
                raise BuildError(f"skills/{card.name}: patch '{rel}' not found")
            base = [
                "git",
                "apply",
                "--unsafe-paths",
                f"--directory={dest.resolve()}",
            ]
            check = subprocess.run(
                base + ["--check", str(patch.resolve())],
                cwd=self.config.root,
                capture_output=True,
                text=True,
            )
            if check.returncode != 0:
                self._anchor(
                    Issue(
                        "LQC-A001",
                        f"patch {rel} does not apply: "
                        f"{check.stderr.strip() or check.stdout.strip()}",
                        card.name,
                        bundle.id,
                    )
                )
                continue
            applied = subprocess.run(
                base + [str(patch.resolve())],
                cwd=self.config.root,
                capture_output=True,
                text=True,
            )
            if applied.returncode != 0:
                self._anchor(
                    Issue(
                        "LQC-A001",
                        f"patch {rel} failed: {applied.stderr.strip()}",
                        card.name,
                        bundle.id,
                    )
                )

    def _stamp(self, skill_md: Path, card: Card) -> None:
        text = skill_md.read_text(encoding="utf-8")
        try:
            document = transforms.parse_document(text)
        except transforms.TransformError as exc:
            raise BuildError(f"skills/{card.name}/SKILL.md: {exc}") from exc

        frontmatter = document.frontmatter
        for key, value in card.frontmatter.items():
            if value is None:
                frontmatter.pop(key, None)
            else:
                frontmatter[key] = value

        frontmatter["name"] = card.name
        # normalise before storing so the emitted YAML round-trips exactly
        frontmatter["description"] = transforms.normalise_block(card.description)
        frontmatter["license"] = "Apache-2.0"
        metadata = frontmatter.get("metadata")
        metadata = dict(metadata) if isinstance(metadata, dict) else {}
        metadata["adapted-from"] = (
            f"LegalQuants/lq-plugin-oss@{self.config.sha7} skills/{card.upstream}"
        )
        metadata["adapted-for"] = "Microsoft 365 Copilot Cowork"
        # A skill uploaded on its own still says which release it came from.
        metadata["version"] = str(self.config.version)
        frontmatter["metadata"] = metadata

        notice = NOTICE_TEMPLATE.format(sha7=self.config.sha7, upstream=card.upstream)
        body_lines = document.body.split("\n")
        while body_lines and not body_lines[0].strip():
            body_lines.pop(0)
        if body_lines and body_lines[0].startswith(NOTICE_MARKER):
            body_lines.pop(0)
            while body_lines and not body_lines[0].strip():
                body_lines.pop(0)
        document.body = "\n" + notice + "\n\n" + "\n".join(body_lines)
        skill_md.write_text(transforms.render_document(document), encoding="utf-8")


def dist_root(config: Config, out_dir: Path | None = None) -> Path:
    """Where built bundles land; ``dist/`` unless the caller says otherwise."""
    return Path(out_dir) if out_dir is not None else config.root / "dist"


def build_manifest(config: Config, bundle: Bundle) -> dict[str, Any]:
    """The Teams v1.28 manifest for one bundle, keys in contract order."""
    return {
        "$schema": MANIFEST_SCHEMA,
        "manifestVersion": MANIFEST_VERSION,
        "version": config.version,
        "id": bundle.guid,
        "developer": dict(config.developer),
        "name": {"short": bundle.name_short, "full": bundle.name_full},
        "description": {
            "short": bundle.description_short,
            "full": bundle.description_full,
        },
        "icons": {"color": "color.png", "outline": "outline.png"},
        "accentColor": config.accent_color,
        "agentSkills": [{"folder": f"./skills/{name}"} for name in bundle.skills],
    }


def _copy_tree(source: Path, dest: Path, patterns: Iterable[str]) -> list[str]:
    """Copy ``source`` into ``dest`` skipping gitignore-style ``patterns``.

    Symlinks are never followed and never copied: a link under a skill folder
    could otherwise pull arbitrary filesystem content into a shipped package.
    Their paths come back so the caller can raise LQC-C007.
    """
    patterns = list(patterns)
    dest.mkdir(parents=True, exist_ok=True)
    symlinks: list[str] = []
    for parent, dirnames, filenames in os.walk(source, followlinks=False):
        parent_path = Path(parent)
        dirnames.sort()
        for name in sorted(dirnames):
            candidate = parent_path / name
            if candidate.is_symlink():
                symlinks.append(candidate.relative_to(source).as_posix())
        dirnames[:] = [
            name for name in dirnames if not (parent_path / name).is_symlink()
        ]
        for name in sorted(filenames):
            path = parent_path / name
            rel = path.relative_to(source).as_posix()
            if path.is_symlink():
                symlinks.append(rel)
                continue
            if patterns and transforms.path_matches(rel, patterns):
                continue
            if not path.is_file():
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return sorted(symlinks)
