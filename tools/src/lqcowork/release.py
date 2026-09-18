"""``release-check``: does a tag agree with the tree? (contract section 7).

Nothing here builds and nothing here writes. It answers one question — is this
tag safe to publish — and prints what it looked at, pass or fail.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .build import dist_root
from .config import Config

CHANGELOG_NAME = "CHANGELOG.md"

# Semver 2.0.0 behind the `v` a git tag carries. The MAJOR.MINOR.PATCH core is
# captured on its own because that, and not the pre-release, is the only shape
# the Teams manifest version can take (LQC-M002).
TAG_RE = re.compile(
    r"""^v
    (?P<version>
      (?P<core>(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*))
      (?:-(?P<prerelease>
        (?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)
        (?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*
      ))?
      (?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?
    )$""",
    re.VERBOSE,
)

# `## [1.2.0] - 2026-09-18`, Keep a Changelog's release heading.
HEADING_RE = re.compile(r"^##\s+\[([^\]]+)\]", re.MULTILINE)


class ReleaseCheckError(Exception):
    """The tree cannot be read — exit 1, as opposed to a tag that is wrong."""


@dataclass(frozen=True)
class Tag:
    """A release tag, split into the parts the checks compare."""

    text: str
    version: str
    core: str
    prerelease: str | None = None


def parse_tag(tag: str) -> Tag | None:
    """``v1.2.0-rc.1`` -> a :class:`Tag`; anything else -> ``None``."""
    match = TAG_RE.match(tag.strip())
    if match is None:
        return None
    return Tag(
        text=tag.strip(),
        version=match.group("version"),
        core=match.group("core"),
        prerelease=match.group("prerelease"),
    )


def changelog_versions(text: str) -> list[str]:
    """Every version named by a ``## [X.Y.Z]`` heading, in file order."""
    return HEADING_RE.findall(text)


@dataclass
class Check:
    """One thing that was looked at, and how it came out."""

    ok: bool
    message: str

    def render(self) -> str:
        return f"  {'ok  ' if self.ok else 'FAIL'}  {self.message}"


@dataclass
class ReleaseCheck:
    tag: str
    checks: list[Check] = field(default_factory=list)

    def ok(self, message: str) -> None:
        self.checks.append(Check(True, message))

    def fail(self, message: str) -> None:
        self.checks.append(Check(False, message))

    @property
    def failures(self) -> list[Check]:
        return [check for check in self.checks if not check.ok]

    def lines(self) -> list[str]:
        summary = (
            f"release-check failed: {len(self.failures)} of "
            f"{len(self.checks)} checks"
            if self.failures
            else f"release-check passed: {len(self.checks)} checks"
        )
        return [
            f"release-check {self.tag}",
            *(check.render() for check in self.checks),
            summary,
        ]


def _rel(config: Config, path: Path) -> str:
    try:
        return str(path.relative_to(config.root))
    except ValueError:
        return str(path)


def _check_changelog(config: Config, tag: Tag, result: ReleaseCheck) -> None:
    """The tag's own version, or — for a suffixed tag — the core it precedes."""
    wanted = [tag.version]
    if tag.core != tag.version:
        wanted.append(tag.core)
    path = config.root / CHANGELOG_NAME
    if not path.is_file():
        result.fail(
            f"{CHANGELOG_NAME} does not exist; every release needs a section "
            f"describing {tag.version}"
        )
        return
    found = changelog_versions(path.read_text(encoding="utf-8"))
    hit = next((version for version in wanted if version in found), None)
    if hit is not None:
        result.ok(f"{CHANGELOG_NAME} has a '## [{hit}]' section")
        return
    sought = " or ".join(f"'## [{version}]'" for version in wanted)
    has = ", ".join(found[:5]) if found else "no version headings at all"
    result.fail(
        f"{CHANGELOG_NAME} has no {sought} section; it has {has}. Move the "
        "Unreleased entries into a dated section for this version"
    )


def _check_manifests(
    config: Config, tag: Tag, result: ReleaseCheck, out_dir: Path | None
) -> None:
    """A built manifest that still carries the previous version ships as an
    update Cowork will not take, so it fails the tag rather than the build."""
    dist = dist_root(config, out_dir)
    for bundle in config.bundles:
        manifest = dist / bundle.id / "manifest.json"
        where = _rel(config, manifest)
        if not manifest.is_file():
            result.ok(f"{where}: not built, so nothing to compare")
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ReleaseCheckError(f"{where}: cannot be read as JSON: {exc}")
        version = data.get("version") if isinstance(data, dict) else None
        if version == tag.core:
            result.ok(f"{where}: version {version}")
        else:
            result.fail(
                f"{where}: version {version!r}, but the tag says {tag.core}; "
                "re-run `make package` after bumping cowork.yaml"
            )


def check_release(
    config: Config, tag: str, out_dir: Path | None = None
) -> ReleaseCheck:
    """Run every contract section 7 release check against ``tag``."""
    result = ReleaseCheck(tag=tag.strip())
    parsed = parse_tag(tag)
    if parsed is None:
        result.fail(
            f"'{tag.strip()}' is not 'v' followed by a semver version "
            "(v0.1.0, v1.2.0-rc.1); nothing else could be checked"
        )
        return result
    note = f" (pre-release {parsed.prerelease})" if parsed.prerelease else ""
    result.ok(f"tag names version {parsed.version}{note}")

    if config.version == parsed.core:
        result.ok(f"cowork.yaml package.version is {config.version}")
    else:
        result.fail(
            f"cowork.yaml package.version is {config.version}, but the tag "
            f"says {parsed.core}; Cowork only updates an installed app when "
            "that number goes up, so fix one or the other"
        )

    _check_changelog(config, parsed, result)
    _check_manifests(config, parsed, result, out_dir)
    return result
