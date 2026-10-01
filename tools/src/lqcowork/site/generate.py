"""Render the static site from a built ``dist/``.

The site is documentation of a *build*: it reads the same sources the
packages are made from — ``cowork.yaml``, the cards, ``probes.yaml``,
upstream's release manifest and skill frontmatter — plus the tree ``package``
wrote, for the file lists and the warnings. It never builds anything itself,
which is why a missing build is an error rather than a thinner site.

Everything it writes is reproducible: no timestamp, no generated id, no
ordering that depends on the filesystem. The only build-specific values on a
page are the package version and the upstream SHA, both of which come from
``cowork.yaml``.
"""

from __future__ import annotations

import posixpath
import re
import shutil
import zipfile
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, Sequence

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markdown_it import MarkdownIt
from markupsafe import Markup, escape

from ..build import BuildError, dist_root
from ..config import (
    Bundle,
    Card,
    Config,
    KnownIssue,
    Workaround,
    load_available_cards,
    split_negative,
)
from ..package import expected_handoff, report_path
from ..transforms import TransformError, parse_document

# This repository, which is not in cowork.yaml: cowork.yaml pins the upstream
# we adapt, not the place the adaptation lives. The release assets, the UAT
# issues and the "help wanted" list are all here.
PROJECT_REPO = "https://github.com/houfu/lq-plugin-cowork"
RELEASES_URL = f"{PROJECT_REPO}/releases/latest"
RELEASES_INDEX_URL = f"{PROJECT_REPO}/releases"
# Every published asset has a second URL that names no version: GitHub
# resolves `releases/latest/download/<asset>` to the same file on the most
# recent release that is not a pre-release. The site links those rather than
# a tagged URL, so a page published today still points at the right file
# after the next tag, and publishing a release rebuilds nothing here.
LATEST_DOWNLOAD_URL = f"{RELEASES_URL}/download"
HELP_WANTED_URL = (
    f"{PROJECT_REPO}/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22"
)

# The two assets that belong to the release rather than to one bundle.
# `release.yml` checksums every other asset into the first.
CHECKSUMS_ASSET = "SHA256SUMS"
REPORT_ASSET = "build-report.md"

SITE_TITLE = "LegalQuants skills for Copilot Cowork"

# The README's own sentence, kept here as a constant so that two builds of the
# same commit say the same thing whatever else the README is doing.
NOT_OFFICIAL = (
    "An independent adaptation of the LegalQuants skills under Apache-2.0: "
    "not an official LegalQuants release, not endorsed by the upstream "
    "project, and not supported by it. LegalQuants skills are a workflow aid, "
    "not legal advice. The judgement stays yours."
)

# docs/CONTRACT.md section 4's rubric, in the words a lawyer reads.
TIER_LEGEND: dict[int, str] = {
    0: "shipped as written, apart from the description and the mechanics",
    1: "documented capabilities only; a wrong result would be loud",
    2: "one named probe, or shipped now with an announced degrade",
    3: "re-scoped: the promise changed",
    4: "needs a connector — no shipped card may say this",
}
STATUS_LEGEND: dict[str, str] = {
    "shipped": "in the package as it stands",
    "probe-gated": (
        "in the package with an announced degrade until a named probe settles "
        "the question it depends on"
    ),
}

NAV: tuple[tuple[str, str], ...] = (
    ("index.html", "Overview"),
    ("differences.html", "What changed"),
    ("known-issues.html", "Known issues"),
    ("probes.html", "Probes"),
    ("verdicts.html", "Verdicts"),
    ("install.html", "Install"),
    ("downloads.html", "Downloads"),
    ("testing.html", "Testing"),
    ("changelog.html", "Changelog"),
)

# Markdown pages: site page -> (repo-relative source, page title).
DOCUMENTS: tuple[tuple[str, str, str], ...] = (
    ("install.html", "docs/INSTALL.md", "Install"),
    ("testing.html", "docs/TESTING.md", "Testing"),
    ("changelog.html", "CHANGELOG.md", "Changelog"),
)
_DOC_BY_SOURCE = {source: page for page, source, _ in DOCUMENTS}

_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
_TICKS = re.compile(r"`([^`]+)`")
_SCHEME = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)
_SLUG_DROP = re.compile(r"[^\w\- ]+", re.UNICODE)
_CELL_SPLIT = re.compile(r"(?<!\\)\|")


class SiteError(BuildError):
    """The tree the site was pointed at is not one it can render."""


# ---------------------------------------------------------------------------
# small text helpers


def download_url(asset: str) -> str:
    """One release asset's URL on whatever the latest release turns out to be."""
    return f"{LATEST_DOWNLOAD_URL}/{asset}"


def latest_note(version: str) -> str:
    """The caveat every download block repeats: what "latest" resolves to."""
    return (
        "\u201cLatest\u201d is GitHub's own pointer at the most recent release "
        "that is not a pre-release, so these links resolve only once "
        f"{version} is published."
    )


def first_sentence(text: str) -> str:
    """The first sentence of a card paragraph, whitespace collapsed."""
    flat = " ".join((text or "").split())
    if not flat:
        return ""
    return _SENTENCE_END.split(flat, maxsplit=1)[0]


def shorten(text: str, limit: int = 150) -> str:
    """``text`` cut at a word boundary, with an ellipsis when it was cut."""
    flat = " ".join((text or "").split())
    if len(flat) <= limit:
        return flat
    head = flat[: limit - 1]
    cut = head.rsplit(" ", 1)[0] if " " in head else head
    return cut.rstrip(" ,;:—-") + "…"


def paragraphs(text: str) -> list[str]:
    """A block scalar split into paragraphs, each one whitespace-collapsed."""
    blocks = re.split(r"\n\s*\n", (text or "").strip())
    return [" ".join(block.split()) for block in blocks if block.strip()]


def ticks(text: str) -> Markup:
    """Escape ``text``, then turn its `backticked` runs into ``<code>``.

    The trigger-test renderer writes expectations like ``expect `wiki` ``; the
    site shows the same strings, so it reads them the same way.
    """
    return Markup(_TICKS.sub(r"<code>\1</code>", str(escape(text))))


def slug(text: str, seen: dict[str, int] | None = None) -> str:
    """A GitHub-style heading anchor, so in-document links keep working."""
    base = _SLUG_DROP.sub("", (text or "").strip().lower()).replace(" ", "-")
    base = base or "section"
    if seen is None:
        return base
    count = seen.get(base, 0)
    seen[base] = count + 1
    return base if count == 0 else f"{base}-{count}"


# ---------------------------------------------------------------------------
# Markdown


def _markdown() -> MarkdownIt:
    """CommonMark plus tables, with raw HTML escaped rather than passed on.

    ``html: False`` is not a guess about what our own documents contain: it is
    the rule that keeps the only script on this site the one in the
    known-issues template, whatever a Markdown source grows later.
    """
    return MarkdownIt("commonmark", {"html": False}).enable("table")


def _repo_url(rel: str) -> str:
    return f"{PROJECT_REPO}/blob/main/{rel}"


def _rewrite_href(href: str, doc_dir: str) -> str:
    """Point a repository-relative link at the site, or at the repository."""
    if not href or href.startswith("#") or _SCHEME.match(href):
        return href
    path, sep, tail = href.partition("#")
    if not path:
        return href
    query, qsep, qtail = path.partition("?")
    resolved = posixpath.normpath(posixpath.join(doc_dir, query))
    page = _DOC_BY_SOURCE.get(resolved)
    if page is not None:
        return page + sep + tail
    return _repo_url(resolved) + qsep + qtail + sep + tail


def _walk(tokens: Iterable[Any]) -> Iterable[Any]:
    for token in tokens:
        yield token
        if getattr(token, "children", None):
            yield from _walk(token.children)


def render_markdown(text: str, source: str) -> Markup:
    """Render one repository Markdown file for the site.

    Two things happen beyond CommonMark: headings get GitHub-style anchors, so
    a document's own ``#section`` links still land; and a link to another file
    in the repository becomes either the matching site page or a link to the
    file on GitHub, because a relative path into a source tree means nothing
    once the page is published.
    """
    md = _markdown()
    tokens = md.parse(text)
    doc_dir = posixpath.dirname(source)
    seen: dict[str, int] = {}
    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        inline = tokens[index + 1] if index + 1 < len(tokens) else None
        label = inline.content if inline is not None else ""
        token.attrSet("id", slug(label, seen))
    for token in _walk(tokens):
        if token.type != "link_open":
            continue
        href = token.attrGet("href")
        if isinstance(href, str):
            token.attrSet("href", _rewrite_href(href, doc_dir))
    return Markup(md.renderer.render(tokens, md.options, {}))


# ---------------------------------------------------------------------------
# the built tree


_SIZE_UNITS = ("KB", "MB", "GB")


def human_size(size: int) -> str:
    """A byte count in the unit a reader thinks in, rounded the same way twice.

    No locale and no clock: the same number of bytes always renders the same
    string, which is what lets a size sit on a reproducible page at all.
    """
    if size < 1024:
        return f"{size} bytes"
    value = float(size)
    unit = _SIZE_UNITS[0]
    for unit in _SIZE_UNITS:
        value /= 1024
        if value < 1024:
            break
    return f"{value:.1f} {unit}"


def skill_archive(out: Path, name: str) -> Path:
    """Where ``package`` writes one skill's upload archive, if it wrote one."""
    return out / "skills" / f"{name}.skill"


def read_archive(path: Path) -> tuple[int, int] | None:
    """One built ``.skill`` archive's size in bytes and its count of files.

    Defensive for the same reason the report parser is, and for one more: the
    archives are `package`'s to write, and the site has to render before they
    exist. An archive that is absent or unreadable costs the page a size, not
    the page.
    """
    if not path.is_file():
        return None
    try:
        size = path.stat().st_size
        with zipfile.ZipFile(path) as archive:
            files = sum(1 for info in archive.infolist() if not info.is_dir())
    except (OSError, zipfile.BadZipFile):
        return None
    return size, files


def _skill_files(tree: Path) -> tuple[str, ...]:
    """Every file in one built skill folder, as sorted relative paths."""
    if not tree.is_dir():
        return ()
    return tuple(
        sorted(
            path.relative_to(tree).as_posix()
            for path in tree.rglob("*")
            if path.is_file()
        )
    )


@dataclass(frozen=True)
class ReportWarning:
    """One row of the build report's warnings table."""

    code: str
    bundle: str
    skill: str
    location: str
    message: str


def _unescape_cell(cell: str) -> str:
    return cell.strip().replace("\\|", "|")


def read_report_warnings(path: Path) -> tuple[ReportWarning, ...]:
    """Parse the ``## Warnings`` table out of ``dist/build-report.md``.

    Defensive on purpose: the report is a document for people, and a site
    that cannot parse one section of it should still be a site.
    """
    if not path.is_file():
        return ()
    rows: list[ReportWarning] = []
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_table = line.startswith("## Warnings")
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if rows:
                break
            continue
        cells = [_unescape_cell(cell) for cell in _CELL_SPLIT.split(line)[1:-1]]
        if len(cells) != 5 or cells[0] in {"Code", "---"}:
            continue
        rows.append(
            ReportWarning(
                code=cells[0],
                bundle=cells[1],
                skill=cells[2],
                location=cells[3],
                message=cells[4],
            )
        )
    return tuple(rows)


# ---------------------------------------------------------------------------
# view models — what the templates see, and nothing else


@dataclass(frozen=True)
class ArchiveView:
    """One skill's ``.skill`` upload archive, built or not.

    The link is the same either way, because it points at the release and not
    at this working tree; only the size and the file count need an archive on
    disk to read.
    """

    asset: str
    url: str
    size: int | None = None
    files: int | None = None

    @property
    def built(self) -> bool:
        return self.size is not None

    @property
    def size_label(self) -> str:
        return "" if self.size is None else human_size(self.size)

    @property
    def detail(self) -> str:
        """``12.3 KB, 4 files``, or nothing when no archive was on disk."""
        if self.size is None or self.files is None:
            return ""
        plural = "" if self.files == 1 else "s"
        return f"{human_size(self.size)}, {self.files} file{plural}"


def _archive_view(out: Path, name: str) -> ArchiveView:
    """One skill's archive as a page sees it, measured where one was built."""
    asset = f"{name}.skill"
    measured = read_archive(skill_archive(out, name))
    return ArchiveView(
        asset=asset,
        url=download_url(asset),
        size=None if measured is None else measured[0],
        files=None if measured is None else measured[1],
    )


@dataclass(frozen=True)
class MirrorView:
    plugin_id: str
    display_name: str
    short_description: str
    line: str
    excludes: tuple[Any, ...]


@dataclass(frozen=True)
class TriggerRow:
    prompt: str
    expected: str


@dataclass(frozen=True)
class TriggerGroup:
    name: str
    rows: tuple[TriggerRow, ...]


@dataclass(frozen=True)
class HandoffVariant:
    where: str
    expected: str


@dataclass(frozen=True)
class Handoff:
    prompt: str
    variants: tuple[HandoffVariant, ...]


@dataclass(frozen=True)
class BundleView:
    id: str
    guid: str
    name_short: str
    name_full: str
    description_short: str
    description_full: str
    asset: str
    mirror: MirrorView | None
    skills: tuple["SkillView", ...] = ()
    trigger_groups: tuple[TriggerGroup, ...] = ()

    @property
    def asset_url(self) -> str:
        return download_url(self.asset)

    @property
    def triggers_asset(self) -> str:
        return f"{self.id}-trigger-tests.md"

    @property
    def triggers_url(self) -> str:
        return download_url(self.triggers_asset)

    @property
    def known_issue_count(self) -> int:
        return sum(len(skill.known_issues) for skill in self.skills)

    @property
    def tier_summary(self) -> str:
        counts: dict[str, int] = {}
        for skill in self.skills:
            counts[skill.tier_label] = counts.get(skill.tier_label, 0) + 1
        return ", ".join(f"{n} at tier {tier}" for tier, n in sorted(counts.items()))


@dataclass(frozen=True)
class SkillView:
    name: str
    upstream: str
    bucket: str
    tier: int | None
    status: str | None
    purpose: str
    differs: str
    notes: str | None
    known_issues: tuple[KnownIssue, ...]
    workarounds: tuple[Workaround, ...]
    positive_triggers: tuple[str, ...]
    handoffs: tuple[Handoff, ...]
    upstream_description: str
    upstream_url: str
    issue_search_url: str
    files: tuple[str, ...]
    warnings: tuple[ReportWarning, ...]
    archive: ArchiveView
    bundles: tuple[BundleView, ...] = ()

    @property
    def tier_label(self) -> str:
        return "—" if self.tier is None else str(self.tier)

    @property
    def status_label(self) -> str:
        return self.status or "—"

    @property
    def tier_legend(self) -> str:
        return TIER_LEGEND.get(self.tier, "no tier on the card")

    @property
    def status_legend(self) -> str:
        return STATUS_LEGEND.get(self.status_label, "no status on the card")

    @property
    def purpose_short(self) -> str:
        return shorten(self.purpose, 120)

    @property
    def differs_excerpt(self) -> str:
        return shorten(first_sentence(self.differs), 170)

    @property
    def bundle_shorts(self) -> tuple[str, ...]:
        return tuple(bundle.name_short for bundle in self.bundles)


@dataclass(frozen=True)
class IssueRow:
    id: str
    skill: str
    tier_label: str
    title: str
    detail: str
    failure: str
    probe: str | None

    @property
    def detail_short(self) -> str:
        """Enough to judge the row by; the whole thing is on the skill page."""
        return shorten(self.detail, 180)


@dataclass(frozen=True)
class IssueRef:
    id: str
    skill: str


@dataclass(frozen=True)
class ProbeView:
    id: str
    title: str
    settles: str
    setup: str | None
    prompt: str
    passes: str
    fails: str
    bad_outcome: str
    unlocks: tuple[str, ...]
    issues: tuple[IssueRef, ...]
    tests: tuple[str, ...] = ()
    cost: str = ""
    method: str = ""
    steps: str = ""


@dataclass(frozen=True)
class TierRow:
    number: int
    legend: str
    count: int


@dataclass(frozen=True)
class DocumentView:
    title: str
    source: str
    body: Markup | None
    repo_url: str


@dataclass
class SiteResult:
    """What one ``lqcowork site`` run produced."""

    root: Path
    pages: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    skills: int = 0
    bundles: int = 0

    def summary(self) -> str:
        return (
            f"{len(self.pages)} pages, {len(self.assets)} asset(s) "
            f"({self.bundles} bundles, {self.skills} skills)"
        )


# ---------------------------------------------------------------------------
# gathering


def _upstream_description(config: Config, card: Card) -> str:
    """Upstream's own ``description``, read from its authored SKILL.md."""
    path = config.upstream_skills_root() / card.upstream / "SKILL.md"
    if not path.is_file():
        return ""
    try:
        document = parse_document(path.read_text(encoding="utf-8"))
    except (TransformError, OSError):
        return ""
    value = document.frontmatter.get("description")
    return " ".join(str(value).split()) if isinstance(value, str) else ""


def _handoffs(card: Card, bundles: Sequence[Bundle]) -> tuple[Handoff, ...]:
    """Negative triggers, with the expectation the checklist would print.

    A skill in two bundles can have two honest answers — the hand-off target
    may be in one bundle and not the other — so where they differ, both are
    given rather than one of them chosen.
    """
    out: list[Handoff] = []
    for prompt in card.triggers.negative:
        text, target = split_negative(prompt)
        grouped: dict[str, list[str]] = {}
        for bundle in bundles:
            grouped.setdefault(expected_handoff(bundle, target), []).append(
                bundle.name_short
            )
        variants = tuple(
            HandoffVariant(where=", ".join(names), expected=expected)
            for expected, names in grouped.items()
        )
        out.append(Handoff(prompt=text, variants=variants))
    return tuple(out)


def _trigger_groups(bundle: Bundle, cards: dict[str, Card]) -> tuple[TriggerGroup, ...]:
    """The bundle's checklist, as the trigger-test renderer decides it."""
    groups: list[TriggerGroup] = []
    for name in bundle.skills:
        card = cards.get(name)
        if card is None:
            continue
        rows = [
            TriggerRow(prompt=prompt, expected=f"activate `{name}`")
            for prompt in card.triggers.positive
        ]
        for prompt in card.triggers.negative:
            text, target = split_negative(prompt)
            rows.append(
                TriggerRow(prompt=text, expected=expected_handoff(bundle, target))
            )
        groups.append(TriggerGroup(name=name, rows=tuple(rows)))
    return tuple(groups)


def _mirror_view(bundle: Bundle) -> MirrorView | None:
    if bundle.mirror is None:
        return None
    return MirrorView(
        plugin_id=bundle.mirror.plugin_id,
        display_name=bundle.mirror.display_name,
        short_description=bundle.mirror.short_description,
        line=bundle.mirror.line(),
        excludes=tuple(bundle.mirror.excludes),
    )


def _issue_search_url(name: str) -> str:
    return f"{PROJECT_REPO}/issues?q=is%3Aissue+%22UAT%3A+{name}%22"


def _upstream_url(config: Config, upstream: str) -> str:
    repo = config.repo.rstrip("/")
    return f"{repo}/tree/{config.sha}/{config.skills_root}/{upstream}"


def site_root(config: Config, out_dir: Path | None = None) -> Path:
    """Where the rendered site lands: ``<out>/site/``."""
    return dist_root(config, out_dir) / "site"


def _require_build(config: Config, out: Path) -> None:
    """A site describes a build; without one there is nothing to describe."""
    missing: list[str] = []
    report = report_path(config, out)
    if not report.is_file():
        missing.append(report.name)
    for bundle in config.bundles:
        tree = out / bundle.id / "skills"
        if not tree.is_dir():
            missing.append(f"{bundle.id}/skills/")
    if missing:
        raise SiteError(
            f"{out} does not hold a build: "
            + ", ".join(missing)
            + " is missing. Run `make package` first (or `lqcowork package "
            f"--out {out}`), then build the site from the same directory."
        )


def gather(config: Config, out: Path) -> dict[str, Any]:
    """Everything the templates need, read once and shared between pages."""
    names = sorted({name for bundle in config.bundles for name in bundle.skills})
    cards, missing = load_available_cards(config, names)
    if missing:
        raise SiteError(
            "no adaptation card for: "
            + ", ".join(missing)
            + ". The build these pages describe cannot be complete; run "
            "`make package` and fix what it reports first."
        )

    warnings = read_report_warnings(report_path(config, out))
    warnings_by_skill: dict[str, list[ReportWarning]] = {}
    for warning in warnings:
        warnings_by_skill.setdefault(warning.skill, []).append(warning)

    bundle_views: dict[str, BundleView] = {}
    for bundle in config.bundles:
        bundle_views[bundle.id] = BundleView(
            id=bundle.id,
            guid=bundle.guid,
            name_short=bundle.name_short,
            name_full=bundle.name_full,
            description_short=bundle.description_short,
            description_full=bundle.description_full,
            asset=f"{bundle.id}.zip",
            mirror=_mirror_view(bundle),
            trigger_groups=_trigger_groups(bundle, cards),
        )

    skill_views: dict[str, SkillView] = {}
    for name in names:
        card = cards[name]
        in_bundles = [b for b in config.bundles if name in b.skills]
        files: tuple[str, ...] = ()
        for bundle in in_bundles:
            files = _skill_files(out / bundle.id / "skills" / name)
            if files:
                break
        block = card.cowork
        skill_views[name] = SkillView(
            name=name,
            upstream=card.upstream,
            bucket=card.bucket,
            tier=block.tier if block else None,
            status=block.status if block else None,
            purpose=first_sentence(card.description),
            differs=block.differs if block else "",
            notes=card.notes,
            known_issues=block.known_issues if block else (),
            workarounds=block.workarounds if block else (),
            positive_triggers=card.triggers.positive,
            handoffs=_handoffs(card, in_bundles),
            upstream_description=_upstream_description(config, card),
            upstream_url=_upstream_url(config, card.upstream),
            issue_search_url=_issue_search_url(name),
            files=files,
            warnings=tuple(warnings_by_skill.get(name, ())),
            archive=_archive_view(out, name),
            bundles=tuple(bundle_views[b.id] for b in in_bundles),
        )

    # A bundle lists its skills and a skill lists its bundles, so each view
    # is built first and then closed over the other.
    for bundle in config.bundles:
        bundle_views[bundle.id] = replace(
            bundle_views[bundle.id],
            skills=tuple(skill_views[name] for name in bundle.skills),
        )
    for name, skill in skill_views.items():
        skill_views[name] = replace(
            skill,
            bundles=tuple(
                bundle_views[b.id] for b in config.bundles if name in b.skills
            ),
        )

    ordered_skills = [skill_views[name] for name in names]
    issue_rows = tuple(
        IssueRow(
            id=issue.id,
            skill=skill.name,
            tier_label=skill.tier_label,
            title=issue.title,
            detail=" ".join(issue.detail.split()),
            failure=issue.failure,
            probe=issue.probe,
        )
        for skill in ordered_skills
        for issue in skill.known_issues
    )

    issues_by_probe: dict[str, list[IssueRef]] = {}
    for row in issue_rows:
        if row.probe:
            issues_by_probe.setdefault(row.probe, []).append(
                IssueRef(id=row.id, skill=row.skill)
            )

    probe_views = tuple(
        ProbeView(
            id=probe.id,
            title=probe.title,
            settles=probe.settles,
            setup=probe.setup,
            prompt=probe.prompt,
            passes=probe.passes,
            fails=probe.fails,
            bad_outcome=probe.bad_outcome,
            unlocks=probe.unlocks,
            issues=tuple(issues_by_probe.get(probe.id, ())),
            tests=probe.tests,
            cost=probe.cost or "",
            method=str((probe.harness or {}).get("method") or ""),
            steps=" ".join(str((probe.harness or {}).get("steps") or "").split()),
        )
        for probe in config.probes
    )

    from ..harness import harness_reports, load_capabilities

    verdict_reports = [
        {
            "slug": item.slug,
            "baseline": item.slug.startswith("baseline-"),
            "source": (
                ""
                if item.slug.startswith("baseline-")
                else item.source.relative_to(config.root).as_posix()
            ),
            **item.report,
        }
        for item in harness_reports(config, load_capabilities(config.root))
    ]

    tier_counts: dict[int, int] = {}
    for skill in ordered_skills:
        if skill.tier is not None:
            tier_counts[skill.tier] = tier_counts.get(skill.tier, 0) + 1
    tier_rows = tuple(
        TierRow(number=tier, legend=legend, count=tier_counts.get(tier, 0))
        for tier, legend in sorted(TIER_LEGEND.items())
    )

    return {
        "site_title": SITE_TITLE,
        "version": config.version,
        "sha7": config.sha7,
        "upstream_tree_url": f"{config.repo.rstrip('/')}/tree/{config.sha}",
        "not_official": NOT_OFFICIAL,
        "releases_url": RELEASES_URL,
        "releases_index_url": RELEASES_INDEX_URL,
        "checksums_asset": CHECKSUMS_ASSET,
        "checksums_url": download_url(CHECKSUMS_ASSET),
        "report_asset": REPORT_ASSET,
        "report_url": download_url(REPORT_ASSET),
        "latest_note": latest_note(config.version),
        "help_wanted_url": HELP_WANTED_URL,
        "nav": [{"href": href, "label": label} for href, label in NAV],
        "bundles": [bundle_views[b.id] for b in config.bundles],
        "skills": ordered_skills,
        "skill_names": set(names),
        "known_issues": issue_rows,
        "probes": probe_views,
        "probe_ids": set(config.probe_ids),
        "probe_span": _probe_span(probe_views),
        "verdict_reports": verdict_reports,
        "verdict_titles": {
            "as-intended": "Runs as intended",
            "fallback": "Runs on a fallback",
            "cannot-run": "Cannot run",
            "untested": "Untested",
        },
        "tiers": tier_rows,
        "transforms": config.transforms,
        "archives_built": any(skill.archive.built for skill in ordered_skills),
    }


def _probe_span(probes: Sequence[ProbeView]) -> str:
    if not probes:
        return "none yet"
    if len(probes) == 1:
        return probes[0].id
    return f"{probes[0].id} to {probes[-1].id}"


# ---------------------------------------------------------------------------
# writing


def _environment() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=False,
        lstrip_blocks=False,
        keep_trailing_newline=True,
    )
    env.globals["paragraphs"] = paragraphs
    env.filters["ticks"] = ticks
    return env


def _write(root: Path, rel: str, text: str, result: SiteResult) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    body = text if text.endswith("\n") else text + "\n"
    target.write_text(body, encoding="utf-8")
    result.pages.append(rel)


def _document_view(config: Config, source: str, title: str) -> DocumentView:
    path = config.root / source
    body: Markup | None = None
    if path.is_file():
        body = render_markdown(path.read_text(encoding="utf-8"), source)
    return DocumentView(
        title=title, source=source, body=body, repo_url=_repo_url(source)
    )


def build_site(config: Config, out_dir: Path | None = None) -> SiteResult:
    """Render ``<out>/site/`` from the build in ``<out>/``."""
    out = dist_root(config, out_dir)
    _require_build(config, out)
    context = gather(config, out)

    root = site_root(config, out_dir)
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    env = _environment()
    result = SiteResult(
        root=root,
        skills=len(context["skills"]),
        bundles=len(context["bundles"]),
    )

    def render(template: str, rel: str, **extra: Any) -> None:
        depth = rel.count("/")
        page = env.get_template(template).render(
            **context,
            **extra,
            base="../" * depth,
            here=rel if depth == 0 else "",
        )
        _write(root, rel, page, result)

    render("index.html", "index.html")
    render("differences.html", "differences.html")
    render("known-issues.html", "known-issues.html")
    render("probes.html", "probes.html")
    render("verdicts.html", "verdicts.html")
    render("downloads.html", "downloads.html")
    for bundle in context["bundles"]:
        render("bundle.html", f"bundles/{bundle.id}.html", bundle=bundle)
    for skill in context["skills"]:
        render("skill.html", f"skills/{skill.name}.html", skill=skill)
    for page, source, title in DOCUMENTS:
        render("document.html", page, doc=_document_view(config, source, title))

    assets = Path(__file__).parent / "assets"
    for asset in sorted(assets.glob("*")):
        if asset.is_file():
            target = root / "assets" / asset.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(asset, target)
            result.assets.append(f"assets/{asset.name}")

    return result
