"""Load and validate ``cowork.yaml`` and the per-skill adaptation cards.

Everything in this module is pure data loading plus shape validation. It
raises :class:`ConfigError` with a human-readable message; the CLI turns that
into exit code 1.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml

from .transforms import DEFAULT_CLAIM_WORDS

CONFIG_NAME = "cowork.yaml"
CARD_NAME = "skill.yaml"
PROBES_NAME = "probes.yaml"
RELEASE_NAME = "plugin.release.yaml"

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}" r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
WARNING_CODE_RE = re.compile(r"^LQC-W\d{3}$")

MANIFEST_LIMITS = {
    "name.short": 30,
    "name.full": 100,
    "description.short": 80,
    "description.full": 4000,
}

# The September assessment's bucket, carried on every card (informational).
BUCKETS = ("green", "amber", "red")
# `cowork.status`: probe-gated means shipped with an announced degrade until
# the probe named by one of its known issues passes.
CARD_STATUSES = ("shipped", "probe-gated")
# Whether a wrong result would look right.
FAILURE_SHAPES = ("silent", "loud")
# The shape of a probe's worst outcome, in the research document's vocabulary.
BAD_OUTCOMES = ("refusal", "fluent-fake", "silent", "loud")
MIN_TIER, MAX_TIER = 0, 4


class ConfigError(Exception):
    """A problem in cowork.yaml or in a skill card."""


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from ``start`` (default: cwd) until ``cowork.yaml`` is found."""
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / CONFIG_NAME).is_file():
            return candidate
    raise ConfigError(
        f"no {CONFIG_NAME} found in {here} or any parent directory; "
        "run from inside the repository"
    )


def _require(mapping: Any, key: str, where: str) -> Any:
    if not isinstance(mapping, dict) or key not in mapping:
        raise ConfigError(f"{where}: missing required key '{key}'")
    return mapping[key]


def _str(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{where}: expected a non-empty string")
    return value


def _str_list(value: Any, where: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        raise ConfigError(f"{where}: expected a list of strings")
    return list(value)


@dataclass(frozen=True)
class ReplaceRule:
    """A literal string replacement, applied to every occurrence."""

    src: str
    dst: str
    files: tuple[str, ...] = ("SKILL.md",)
    expect: int | None = None
    origin: str = "card"

    @staticmethod
    def parse(raw: Any, where: str, origin: str) -> "ReplaceRule":
        if not isinstance(raw, dict):
            raise ConfigError(f"{where}: each replace rule must be a mapping")
        src = _require(raw, "from", where)
        dst = _require(raw, "to", where)
        if not isinstance(src, str) or not src:
            raise ConfigError(f"{where}: 'from' must be a non-empty string")
        if not isinstance(dst, str):
            raise ConfigError(f"{where}: 'to' must be a string")
        files = tuple(_str_list(raw.get("files"), f"{where}.files")) or ("SKILL.md",)
        expect = raw.get("expect")
        if expect is not None and (not isinstance(expect, int) or expect < 0):
            raise ConfigError(f"{where}: 'expect' must be a non-negative integer")
        unknown = set(raw) - {"from", "to", "files", "expect"}
        if unknown:
            raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
        return ReplaceRule(src, dst, files, expect, origin)


@dataclass(frozen=True)
class SectionRule:
    """A heading-anchored replacement (or deletion) inside SKILL.md."""

    match: str
    file: str | None = None
    delete: bool = False

    @staticmethod
    def parse(raw: Any, where: str) -> "SectionRule":
        if not isinstance(raw, dict):
            raise ConfigError(f"{where}: each section rule must be a mapping")
        match = _str(_require(raw, "match", where), f"{where}.match")
        file = raw.get("file")
        delete = bool(raw.get("delete", False))
        unknown = set(raw) - {"match", "file", "delete"}
        if unknown:
            raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
        if delete and file:
            raise ConfigError(f"{where}: use either 'file' or 'delete', not both")
        if not delete and not file:
            raise ConfigError(f"{where}: needs either 'file' or 'delete: true'")
        if file is not None and not isinstance(file, str):
            raise ConfigError(f"{where}: 'file' must be a string")
        return SectionRule(match.rstrip(), file, delete)


@dataclass(frozen=True)
class SuppressRule:
    """An auditable, per-card decision to accept one warning."""

    code: str
    reason: str
    file: str | None = None

    @staticmethod
    def parse(raw: Any, where: str) -> "SuppressRule":
        if not isinstance(raw, dict):
            raise ConfigError(f"{where}: each suppress entry must be a mapping")
        unknown = set(raw) - {"code", "file", "reason"}
        if unknown:
            raise ConfigError(f"{where}: unknown keys {sorted(unknown)}")
        code = _str(_require(raw, "code", where), f"{where}.code").strip()
        if not WARNING_CODE_RE.match(code):
            raise ConfigError(
                f"{where}.code: '{code}' is not a warning code; only LQC-Wnnn "
                "warnings may be suppressed, never an error"
            )
        reason = _str(_require(raw, "reason", where), f"{where}.reason").strip()
        file = raw.get("file")
        if file is not None and not isinstance(file, str):
            raise ConfigError(f"{where}.file: expected a glob relative to the skill")
        return SuppressRule(code=code, reason=reason, file=file or None)

    def matches(self, code: str, location: str | None) -> bool:
        if code != self.code:
            return False
        if self.file is None:
            return True
        if location is None:
            return False
        return _location_file(location) == self.file or fnmatch(
            _location_file(location), self.file
        )


def _location_file(location: str) -> str:
    """The file part of a ``file:line`` warning location."""
    head, _, tail = location.rpartition(":")
    return head if head and tail.isdigit() else location


@dataclass(frozen=True)
class KnownIssue:
    """One thing that can go wrong, written for the lawyer who would see it."""

    id: str
    title: str
    detail: str
    failure: str
    probe: str | None = None


@dataclass(frozen=True)
class Workaround:
    """What the adaptation does instead of a piece of upstream machinery."""

    instead_of: str
    cowork: str


@dataclass(frozen=True)
class CoworkBlock:
    """A card's ``cowork:`` block: how this skill differs, and what it costs.

    ``tier`` is the risk rubric of docs/CONTRACT.md section 4:

    0  shipped as written apart from description and mechanics
    1  documented capabilities only, loud failures
    2  one named probe, or shipped now with an announced degrade
    3  re-scoped: the promise changed
    4  needs a connector -- a shipped card may not say 4 (LQC-K002)
    """

    tier: int
    status: str
    differs: str
    known_issues: tuple[KnownIssue, ...] = ()
    workarounds: tuple[Workaround, ...] = ()

    @property
    def probes(self) -> tuple[str, ...]:
        """Every probe id named by a known issue, in card order."""
        seen: list[str] = []
        for issue in self.known_issues:
            if issue.probe and issue.probe not in seen:
                seen.append(issue.probe)
        return tuple(seen)


def parse_cowork(raw: Any, where: str) -> tuple[CoworkBlock | None, list[str]]:
    """Parse a card's ``cowork:`` block, collecting LQC-K001 reasons.

    Nothing here raises: a card whose block is missing or malformed is an
    error the build reports per card (LQC-K001), so one unfinished card does
    not hide the state of the other thirty.
    """
    problems: list[str] = []
    if raw is None:
        return None, [f"{where}: the required `cowork` block is missing"]
    if not isinstance(raw, dict):
        return None, [f"{where}.cowork: expected a mapping"]

    unknown = set(raw) - {"tier", "status", "differs", "known_issues", "workarounds"}
    if unknown:
        problems.append(f"{where}.cowork: unknown keys {sorted(unknown)}")

    tier = raw.get("tier")
    if isinstance(tier, bool) or not isinstance(tier, int):
        problems.append(f"{where}.cowork.tier: expected an integer 0 to 4")
        tier = None
    elif not MIN_TIER <= tier <= MAX_TIER:
        problems.append(f"{where}.cowork.tier: {tier} is not in the range 0 to 4")
        tier = None

    status = raw.get("status")
    if not isinstance(status, str) or status not in CARD_STATUSES:
        problems.append(
            f"{where}.cowork.status: expected one of {', '.join(CARD_STATUSES)}"
        )
        status = None

    differs = raw.get("differs")
    if not isinstance(differs, str) or not differs.strip():
        problems.append(
            f"{where}.cowork.differs: expected a paragraph for a lawyer saying "
            "how this skill differs from the original"
        )
        differs = None

    known_issues: list[KnownIssue] = []
    raw_issues = raw.get("known_issues") or []
    if not isinstance(raw_issues, list):
        problems.append(f"{where}.cowork.known_issues: expected a list")
        raw_issues = []
    for index, item in enumerate(raw_issues):
        spot = f"{where}.cowork.known_issues[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{spot}: expected a mapping")
            continue
        missing = [
            key
            for key in ("id", "title", "detail", "failure")
            if not isinstance(item.get(key), str) or not str(item.get(key)).strip()
        ]
        if missing:
            problems.append(f"{spot}: missing {', '.join(missing)}")
            continue
        failure = str(item["failure"]).strip()
        if failure not in FAILURE_SHAPES:
            problems.append(
                f"{spot}.failure: expected one of {', '.join(FAILURE_SHAPES)}"
            )
            continue
        probe = item.get("probe")
        if probe is not None and not isinstance(probe, str):
            problems.append(f"{spot}.probe: expected a probe id such as P3")
            probe = None
        known_issues.append(
            KnownIssue(
                id=str(item["id"]).strip(),
                title=str(item["title"]).strip(),
                detail=str(item["detail"]).strip(),
                failure=failure,
                probe=probe.strip() if isinstance(probe, str) else None,
            )
        )

    workarounds: list[Workaround] = []
    raw_workarounds = raw.get("workarounds") or []
    if not isinstance(raw_workarounds, list):
        problems.append(f"{where}.cowork.workarounds: expected a list")
        raw_workarounds = []
    for index, item in enumerate(raw_workarounds):
        spot = f"{where}.cowork.workarounds[{index}]"
        if not isinstance(item, dict):
            problems.append(f"{spot}: expected a mapping")
            continue
        missing = [
            key
            for key in ("instead_of", "cowork")
            if not isinstance(item.get(key), str) or not str(item.get(key)).strip()
        ]
        if missing:
            problems.append(f"{spot}: missing {', '.join(missing)}")
            continue
        workarounds.append(
            Workaround(
                instead_of=str(item["instead_of"]).strip(),
                cowork=str(item["cowork"]).strip(),
            )
        )

    if tier is None or status is None or differs is None:
        return None, problems
    return (
        CoworkBlock(
            tier=tier,
            status=status,
            differs=differs.strip(),
            known_issues=tuple(known_issues),
            workarounds=tuple(workarounds),
        ),
        problems,
    )


@dataclass(frozen=True)
class Probe:
    """One capability probe from ``probes.yaml``."""

    id: str
    title: str
    settles: str
    prompt: str
    passes: str
    fails: str
    bad_outcome: str
    setup: str | None = None
    unlocks: tuple[str, ...] = ()


def load_probes(root: Path) -> tuple[Probe, ...]:
    """Parse ``<root>/probes.yaml``; an absent file means no probes.

    Absence is tolerated rather than fatal: a card that names a probe then
    gets LQC-K003, which says precisely that the id is not defined.
    """
    path = root / PROBES_NAME
    if not path.is_file():
        return ()
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{PROBES_NAME}: invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{PROBES_NAME}: expected a top-level mapping")
    items = raw.get("probes")
    if not isinstance(items, list):
        raise ConfigError(f"{PROBES_NAME}.probes: expected a list")

    probes: list[Probe] = []
    seen: set[str] = set()
    for index, item in enumerate(items):
        where = f"{PROBES_NAME}.probes[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{where}: expected a mapping")
        probe_id = _str(_require(item, "id", where), f"{where}.id").strip()
        if probe_id in seen:
            raise ConfigError(f"{where}.id: duplicate probe id '{probe_id}'")
        seen.add(probe_id)
        bad_outcome = _str(
            _require(item, "bad_outcome", where), f"{where}.bad_outcome"
        ).strip()
        if bad_outcome not in BAD_OUTCOMES:
            raise ConfigError(
                f"{where}.bad_outcome: expected one of {', '.join(BAD_OUTCOMES)}"
            )
        setup = item.get("setup")
        if setup is not None and not isinstance(setup, str):
            raise ConfigError(f"{where}.setup: expected a string")
        probes.append(
            Probe(
                id=probe_id,
                title=_str(_require(item, "title", where), f"{where}.title").strip(),
                settles=_str(
                    _require(item, "settles", where), f"{where}.settles"
                ).strip(),
                prompt=_str(_require(item, "prompt", where), f"{where}.prompt").strip(),
                passes=_str(_require(item, "pass", where), f"{where}.pass").strip(),
                fails=_str(_require(item, "fail", where), f"{where}.fail").strip(),
                bad_outcome=bad_outcome,
                setup=setup.strip() if isinstance(setup, str) else None,
                unlocks=tuple(_str_list(item.get("unlocks"), f"{where}.unlocks")),
            )
        )
    return tuple(probes)


@dataclass(frozen=True)
class Triggers:
    positive: tuple[str, ...]
    negative: tuple[str, ...]


@dataclass(frozen=True)
class Card:
    """One ``skills/<name>/skill.yaml`` adaptation card."""

    name: str
    upstream: str
    directory: Path
    description: str
    anchored_to: str
    bucket: str = "green"
    frontmatter: dict[str, Any] = field(default_factory=dict)
    exclude: tuple[str, ...] = ()
    replace: tuple[ReplaceRule, ...] = ()
    sections: tuple[SectionRule, ...] = ()
    patches: tuple[str, ...] = ()
    files: str | None = None
    notes: str | None = None
    suppress: tuple[SuppressRule, ...] = ()
    triggers: Triggers = field(default_factory=lambda: Triggers((), ()))
    cowork: CoworkBlock | None = None
    # LQC-K001 reasons found while parsing `cowork:`; empty on a good card.
    cowork_problems: tuple[str, ...] = ()

    @property
    def overlay(self) -> Path:
        return self.directory / "SKILL.md"

    @property
    def upstream_group(self) -> str:
        return self.upstream.split("/", 1)[0]

    @property
    def tier(self) -> int | None:
        return self.cowork.tier if self.cowork else None

    @property
    def status(self) -> str | None:
        return self.cowork.status if self.cowork else None

    @property
    def known_issues(self) -> tuple[KnownIssue, ...]:
        return self.cowork.known_issues if self.cowork else ()


@dataclass(frozen=True)
class ExcludedSkill:
    """One ``exclude_skills`` entry: a skill left out, and why (LQC-B002)."""

    name: str
    reason: str


@dataclass(frozen=True)
class Mirror:
    """What a mirrored bundle took from upstream's release manifest."""

    plugin_id: str
    groups: tuple[str, ...]
    includes: tuple[str, ...]
    excludes: tuple[ExcludedSkill, ...]
    display_name: str
    short_description: str

    def line(self) -> str:
        """The build report's one-line account of the derivation."""
        parts = [f"Mirrors upstream plugin {self.plugin_id}"]
        parts.append(f"groups {', '.join(self.groups) or 'none'}")
        parts.append(f"includes {', '.join(self.includes) or 'none'}")
        parts.append(
            "excludes "
            + (", ".join(e.name for e in self.excludes) if self.excludes else "none")
        )
        return f"{parts[0]}: {'; '.join(parts[1:])}"


@dataclass(frozen=True)
class Bundle:
    id: str
    guid: str
    name_short: str
    name_full: str
    description_short: str
    description_full: str
    skills: tuple[str, ...]
    mirror: Mirror | None = None


@dataclass(frozen=True)
class Transforms:
    drop_frontmatter: tuple[str, ...]
    strip_waivers: bool
    skill_tokens: bool
    vendor_words: tuple[str, ...]
    host_words: tuple[str, ...] = ()
    claim_words: tuple[str, ...] = ()


@dataclass(frozen=True)
class Config:
    root: Path
    repo: str
    sha: str
    upstream_path: str
    skills_root: str
    developer: dict[str, str]
    version: str
    accent_color: str
    icon_color: str
    icon_outline: str
    root_files: tuple[str, ...]
    strip: tuple[str, ...]
    transforms: Transforms
    replace: tuple[ReplaceRule, ...]
    bundles: tuple[Bundle, ...]
    probes: tuple[Probe, ...] = ()

    @property
    def sha7(self) -> str:
        return self.sha[:7]

    @property
    def probe_ids(self) -> set[str]:
        return {probe.id for probe in self.probes}

    def probe(self, probe_id: str) -> Probe | None:
        return next((p for p in self.probes if p.id == probe_id), None)

    def upstream_root(self, override: Path | None = None) -> Path:
        base = override if override is not None else self.root / self.upstream_path
        return Path(base)

    def upstream_skills_root(self, override: Path | None = None) -> Path:
        return self.upstream_root(override) / self.skills_root

    def bundle(self, bundle_id: str) -> Bundle:
        for bundle in self.bundles:
            if bundle.id == bundle_id:
                return bundle
        known = ", ".join(b.id for b in self.bundles)
        raise ConfigError(f"unknown bundle '{bundle_id}'; known bundles: {known}")

    def select(self, bundle_id: str | None) -> list[Bundle]:
        return [self.bundle(bundle_id)] if bundle_id else list(self.bundles)

    @property
    def card_root(self) -> Path:
        return self.root / "skills"


def _release_plugins(release_path: Path) -> list[dict[str, Any]]:
    """The ``plugins:`` list out of upstream's ``plugin.release.yaml``."""
    if not release_path.is_file():
        raise ConfigError(
            f"{release_path}: upstream's {RELEASE_NAME} is not there, so a "
            "bundle cannot mirror it; check the submodule out first"
        )
    try:
        raw = yaml.safe_load(release_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{release_path}: invalid YAML: {exc}") from exc
    plugins = (raw or {}).get("plugins") if isinstance(raw, dict) else None
    if not isinstance(plugins, list):
        raise ConfigError(f"{release_path}: no 'plugins' list")
    return [p for p in plugins if isinstance(p, dict)]


def _group_skills(group_dir: Path) -> list[str]:
    """Skill folder names under one upstream group, alphabetically."""
    if not group_dir.is_dir():
        raise ConfigError(f"{group_dir}: upstream skill group not found")
    return sorted(
        path.name
        for path in group_dir.iterdir()
        if path.is_dir()
        and not path.name.startswith(".")
        and (path / "SKILL.md").is_file()
    )


def derive_mirror(
    skills_root: Path,
    release_path: Path,
    plugin_id: str,
    excludes: tuple[ExcludedSkill, ...],
    where: str,
) -> tuple[Mirror, tuple[str, ...]]:
    """Membership for a bundle that mirrors an upstream release plugin.

    Groups in the order the manifest lists them, alphabetically within a
    group; then ``include_skills`` in the order listed; then the card's
    ``exclude_skills`` removed. That list is the bundle's ``skills`` for every
    purpose — manifest order, build, triggers, report and site.
    """
    plugins = _release_plugins(release_path)
    match = next((p for p in plugins if p.get("id") == plugin_id), None)
    if match is None:
        known = ", ".join(str(p.get("id")) for p in plugins)
        raise ConfigError(
            f"{where}.mirror: '{plugin_id}' is not a plugin in "
            f"{RELEASE_NAME}; it defines: {known}"
        )

    groups = tuple(_str_list(match.get("skill_groups"), f"{where}.mirror.skill_groups"))
    includes = tuple(
        _str_list(match.get("include_skills"), f"{where}.mirror.include_skills")
    )

    names: list[str] = []
    for group in groups:
        for name in _group_skills(skills_root / group):
            if name not in names:
                names.append(name)
    for entry in includes:
        if entry.count("/") != 1:
            raise ConfigError(
                f"{where}.mirror: include_skills entry '{entry}' is not "
                "'<group>/<name>'"
            )
        name = entry.split("/", 1)[1]
        if name not in names:
            names.append(name)

    excluded = {entry.name for entry in excludes}
    mirror = Mirror(
        plugin_id=plugin_id,
        groups=groups,
        includes=includes,
        excludes=excludes,
        display_name=str(match.get("display_name") or plugin_id),
        short_description=str(match.get("short_description") or ""),
    )
    return mirror, tuple(name for name in names if name not in excluded)


def _parse_excludes(raw: Any, where: str) -> tuple[ExcludedSkill, ...]:
    """``exclude_skills:`` — each entry needs a name and a stated reason."""
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ConfigError(f"{where}.exclude_skills: expected a list")
    out: list[ExcludedSkill] = []
    for index, item in enumerate(raw):
        spot = f"{where}.exclude_skills[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{spot}: expected a mapping with 'name' and 'reason'")
        unknown = set(item) - {"name", "reason"}
        if unknown:
            raise ConfigError(f"{spot}: unknown keys {sorted(unknown)}")
        out.append(
            ExcludedSkill(
                name=_str(_require(item, "name", spot), f"{spot}.name").strip(),
                reason=_str(_require(item, "reason", spot), f"{spot}.reason").strip(),
            )
        )
    return tuple(out)


def load_config(root: Path) -> Config:
    """Parse ``<root>/cowork.yaml`` into a :class:`Config`."""
    path = root / CONFIG_NAME
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - message passthrough
        raise ConfigError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: expected a top-level mapping")

    upstream = _require(raw, "upstream", CONFIG_NAME)
    sha = _str(_require(upstream, "sha", "upstream"), "upstream.sha")
    if not SHA_RE.match(sha):
        raise ConfigError("upstream.sha: expected a full 40-character lowercase SHA")

    developer_raw = _require(raw, "developer", CONFIG_NAME)
    developer = {
        key: _str(_require(developer_raw, key, "developer"), f"developer.{key}")
        for key in ("name", "websiteUrl", "privacyUrl", "termsOfUseUrl")
    }

    package = _require(raw, "package", CONFIG_NAME)
    version = _str(_require(package, "version", "package"), "package.version")
    if not SEMVER_RE.match(version):
        raise ConfigError("package.version: expected x.y.z")
    icons = _require(package, "icons", "package")

    transforms_raw = raw.get("transforms") or {}
    transforms = Transforms(
        drop_frontmatter=tuple(
            _str_list(
                transforms_raw.get("drop_frontmatter"),
                "transforms.drop_frontmatter",
            )
        ),
        strip_waivers=bool(transforms_raw.get("strip_waivers", True)),
        skill_tokens=bool(transforms_raw.get("skill_tokens", True)),
        vendor_words=tuple(
            _str_list(transforms_raw.get("vendor_words"), "transforms.vendor_words")
        ),
        host_words=tuple(
            _str_list(transforms_raw.get("host_words"), "transforms.host_words")
        ),
        claim_words=(
            tuple(
                _str_list(transforms_raw.get("claim_words"), "transforms.claim_words")
            )
            if transforms_raw.get("claim_words") is not None
            else DEFAULT_CLAIM_WORDS
        ),
    )

    replace = tuple(
        ReplaceRule.parse(item, f"replace[{i}]", "global")
        for i, item in enumerate(raw.get("replace") or [])
    )

    bundles_raw = raw.get("bundles")
    if not isinstance(bundles_raw, list) or not bundles_raw:
        raise ConfigError("bundles: expected a non-empty list")

    upstream_path = str(upstream.get("path", "upstream"))
    skills_root_name = str(upstream.get("skills_root", "skills"))
    upstream_dir = root / upstream_path

    bundles: list[Bundle] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(bundles_raw):
        where = f"bundles[{index}]"
        bundle_id = _str(_require(item, "id", where), f"{where}.id")
        if bundle_id in seen_ids:
            raise ConfigError(f"{where}: duplicate bundle id '{bundle_id}'")
        seen_ids.add(bundle_id)
        guid = _str(_require(item, "guid", where), f"{where}.guid")
        if not GUID_RE.match(guid):
            raise ConfigError(f"{where}.guid: expected a UUID")
        name = _require(item, "name", where)
        description = _require(item, "description", where)
        values = {
            "name.short": _str(
                _require(name, "short", f"{where}.name"), f"{where}.name.short"
            ),
            "name.full": _str(
                _require(name, "full", f"{where}.name"), f"{where}.name.full"
            ),
            "description.short": _str(
                _require(description, "short", f"{where}.description"),
                f"{where}.description.short",
            ),
            "description.full": _str(
                _require(description, "full", f"{where}.description"),
                f"{where}.description.full",
            ),
        }
        for key, limit in MANIFEST_LIMITS.items():
            if len(values[key]) > limit:
                raise ConfigError(
                    f"{where}.{key}: {len(values[key])} characters, limit is {limit}"
                )
        mirror_id = item.get("mirror")
        has_skills = item.get("skills") is not None
        if mirror_id is not None and has_skills:
            raise ConfigError(
                f"{where}: 'mirror' and 'skills' on the same bundle; a "
                "mirrored bundle derives its membership from upstream"
            )
        if mirror_id is None and not has_skills:
            raise ConfigError(f"{where}: needs either 'mirror' or 'skills'")

        mirror: Mirror | None = None
        if mirror_id is not None:
            mirror, derived = derive_mirror(
                upstream_dir / skills_root_name,
                upstream_dir / RELEASE_NAME,
                _str(mirror_id, f"{where}.mirror").strip(),
                _parse_excludes(item.get("exclude_skills"), where),
                where,
            )
            skills = list(derived)
        else:
            if item.get("exclude_skills") is not None:
                raise ConfigError(
                    f"{where}.exclude_skills: only a mirrored bundle excludes; "
                    "an explicit 'skills' list is already the membership"
                )
            skills = _str_list(_require(item, "skills", where), f"{where}.skills")
        if not skills:
            raise ConfigError(f"{where}.skills: expected at least one skill")
        if len(skills) != len(set(skills)):
            raise ConfigError(f"{where}.skills: duplicate skill names")
        bundles.append(
            Bundle(
                id=bundle_id,
                guid=guid,
                name_short=values["name.short"],
                name_full=values["name.full"],
                description_short=values["description.short"],
                description_full=values["description.full"],
                skills=tuple(skills),
                mirror=mirror,
            )
        )

    return Config(
        root=root,
        repo=_str(_require(upstream, "repo", "upstream"), "upstream.repo"),
        sha=sha,
        upstream_path=str(upstream.get("path", "upstream")),
        skills_root=str(upstream.get("skills_root", "skills")),
        developer=developer,
        version=version,
        accent_color=_str(
            _require(package, "accentColor", "package"), "package.accentColor"
        ),
        icon_color=_str(_require(icons, "color", "package.icons"), "icons.color"),
        icon_outline=_str(_require(icons, "outline", "package.icons"), "icons.outline"),
        root_files=tuple(_str_list(package.get("root_files"), "package.root_files")),
        strip=tuple(_str_list(raw.get("strip"), "strip")),
        transforms=transforms,
        replace=replace,
        bundles=tuple(bundles),
        probes=load_probes(root),
    )


def load_card(config: Config, name: str) -> Card:
    """Parse ``skills/<name>/skill.yaml``."""
    directory = config.card_root / name
    path = directory / CARD_NAME
    if not path.is_file():
        raise ConfigError(f"skills/{name}/{CARD_NAME}: no adaptation card for '{name}'")
    where = f"skills/{name}/{CARD_NAME}"
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"{where}: invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigError(f"{where}: expected a top-level mapping")

    card_name = _str(_require(raw, "name", where), f"{where}.name")
    if card_name != name:
        raise ConfigError(f"{where}.name: '{card_name}' does not match folder '{name}'")
    if not KEBAB_RE.match(card_name) or len(card_name) > 64:
        raise ConfigError(f"{where}.name: must be kebab-case, 1-64 characters")

    upstream = _str(_require(raw, "upstream", where), f"{where}.upstream")
    if upstream.count("/") != 1:
        raise ConfigError(f"{where}.upstream: expected '<group>/<name>'")

    anchored_to = _str(_require(raw, "anchored_to", where), f"{where}.anchored_to")
    if not SHA_RE.match(anchored_to):
        raise ConfigError(f"{where}.anchored_to: expected a full 40-character SHA")

    description = _str(_require(raw, "description", where), f"{where}.description")

    bucket = str(raw.get("bucket", "green"))
    if bucket not in BUCKETS:
        raise ConfigError(f"{where}.bucket: expected one of {', '.join(BUCKETS)}")

    cowork, cowork_problems = parse_cowork(raw.get("cowork"), where)

    frontmatter = raw.get("frontmatter") or {}
    if not isinstance(frontmatter, dict):
        raise ConfigError(f"{where}.frontmatter: expected a mapping")

    triggers_raw = _require(raw, "triggers", where)
    if not isinstance(triggers_raw, dict):
        raise ConfigError(f"{where}.triggers: expected a mapping")
    triggers = Triggers(
        positive=tuple(
            _str_list(triggers_raw.get("positive"), f"{where}.triggers.positive")
        ),
        negative=tuple(
            _str_list(triggers_raw.get("negative"), f"{where}.triggers.negative")
        ),
    )
    if not triggers.positive:
        raise ConfigError(f"{where}.triggers.positive: expected at least one prompt")

    notes = raw.get("notes")
    if notes is not None and not isinstance(notes, str):
        raise ConfigError(f"{where}.notes: expected a string")

    files = raw.get("files")
    if files is not None and not isinstance(files, str):
        raise ConfigError(f"{where}.files: expected a directory name")

    return Card(
        name=card_name,
        upstream=upstream,
        directory=directory,
        description=description,
        anchored_to=anchored_to,
        bucket=bucket,
        frontmatter=frontmatter,
        exclude=tuple(_str_list(raw.get("exclude"), f"{where}.exclude")),
        replace=tuple(
            ReplaceRule.parse(item, f"{where}.replace[{i}]", "card")
            for i, item in enumerate(raw.get("replace") or [])
        ),
        sections=tuple(
            SectionRule.parse(item, f"{where}.sections[{i}]")
            for i, item in enumerate(raw.get("sections") or [])
        ),
        patches=tuple(_str_list(raw.get("patches"), f"{where}.patches")),
        files=files,
        suppress=tuple(
            SuppressRule.parse(item, f"{where}.suppress[{i}]")
            for i, item in enumerate(raw.get("suppress") or [])
        ),
        notes=notes.strip() if isinstance(notes, str) else None,
        triggers=triggers,
        cowork=cowork,
        cowork_problems=tuple(cowork_problems),
    )


def load_cards(config: Config, names: list[str]) -> dict[str, Card]:
    """Load every named card, reporting all missing cards at once."""
    cards: dict[str, Card] = {}
    missing: list[str] = []
    for name in names:
        try:
            cards[name] = load_card(config, name)
        except ConfigError as exc:
            if "no adaptation card" in str(exc):
                missing.append(name)
            else:
                raise
    if missing:
        raise ConfigError("missing adaptation cards for: " + ", ".join(sorted(missing)))
    validate_trigger_targets(config, cards)
    return cards


def load_available_cards(
    config: Config, names: list[str]
) -> tuple[dict[str, Card], list[str]]:
    """Load the cards that exist; report the names that have none.

    The companion to :func:`load_cards` for callers that turn a missing card
    into an issue rather than an exception — a mirrored bundle derives its
    membership from upstream, so "no card for this skill" is LQC-B001, a
    reviewable error naming the skill, not a crash.
    """
    cards: dict[str, Card] = {}
    missing: list[str] = []
    for name in names:
        try:
            cards[name] = load_card(config, name)
        except ConfigError as exc:
            if "no adaptation card" in str(exc):
                missing.append(name)
            else:
                raise
    validate_trigger_targets(config, cards, extra_known=set(names))
    return cards, sorted(missing)


def upstream_skill_names(config: Config, override: Path | None = None) -> list[str]:
    """Every authored upstream skill folder name, sorted longest first.

    Longest-first keeps token rewriting from matching a shorter name that is a
    prefix of a longer one.
    """
    root = config.upstream_skills_root(override)
    if not root.is_dir():
        raise ConfigError(f"{root}: upstream skills tree not found")
    names = {
        skill.name
        for group in sorted(root.iterdir())
        if group.is_dir() and not group.name.startswith(".")
        for skill in sorted(group.iterdir())
        if skill.is_dir() and (skill / "SKILL.md").is_file()
    }
    return sorted(names, key=lambda n: (-len(n), n))


# Cowork's built-in skills (contract section 8). A negative trigger prompt may
# hand off to one of these instead of to a sibling skill.
COWORK_BUILTINS: tuple[str, ...] = (
    "Word",
    "Excel",
    "PowerPoint",
    "PDF",
    "Email",
    "Scheduling",
    "Calendar Management",
    "Meetings",
    "Daily Briefing",
    "Enterprise Search",
    "Deep Research",
    "Communications",
    "Adaptive Cards",
    "App",
)
_BUILTINS_BY_KEY = {name.lower(): name for name in COWORK_BUILTINS}


def builtin_name(target: str) -> str | None:
    """The canonical spelling of a Cowork built-in, or None."""
    return _BUILTINS_BY_KEY.get(target.strip().lower())


def split_negative(prompt: str) -> tuple[str, str]:
    """Split ``"prompt -> target"`` into ``(prompt, target)``; target may be ''."""
    text, _, target = prompt.partition("->")
    return text.strip(), target.strip()


def known_card_names(config: Config) -> set[str]:
    """Every skill that has a card on disk, whether or not it is bundled."""
    root = config.card_root
    if not root.is_dir():
        return set()
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / CARD_NAME).is_file()
    }


def validate_trigger_targets(
    config: Config,
    cards: dict[str, Card],
    extra_known: set[str] | None = None,
) -> None:
    """Every ``-> target`` must name a card, a built-in, or ``none``.

    ``extra_known`` are skills a bundle already claims whose card is not
    written yet: naming one is not a typo, it is LQC-B001 on the other card,
    and that is the error worth reading.
    """
    known = known_card_names(config) | set(cards) | (extra_known or set())
    problems: list[str] = []
    for name in sorted(cards):
        for prompt in cards[name].triggers.negative:
            _, target = split_negative(prompt)
            if not target or target.lower() == "none":
                continue
            if target in known or builtin_name(target) is not None:
                continue
            problems.append(
                f"skills/{name}/{CARD_NAME}: negative trigger hands off to "
                f"'{target}', which is not a skill card, a Cowork built-in, "
                "or 'none'"
            )
    if problems:
        raise ConfigError("\n".join(problems))
