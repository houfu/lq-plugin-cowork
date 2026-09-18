#!/usr/bin/env python3
"""Render one GitHub issue per shipped skill, so "help wanted" is real.

Nothing in this repository has been exercised in a live Microsoft 365 Copilot
Cowork tenant. The tester programme in ``docs/TESTING.md`` describes what to
run; this script turns it into one claimable issue per skill, each carrying
that skill's own routing checklist built from its card's ``triggers``.

    uv run --project tools python tools/scripts/uat_issues.py
    uv run --project tools python tools/scripts/uat_issues.py --out /tmp/uat
    uv run --project tools python tools/scripts/uat_issues.py --create
    uv run --project tools python tools/scripts/uat_issues.py --tracking

Without flags it only writes Markdown to ``dist/uat-issues/``. ``--create``
and ``--tracking`` talk to GitHub through the ``gh`` CLI and are safe to
re-run: an issue whose exact title is already open is skipped, and the status
board is edited in place rather than duplicated.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from lqcowork.config import (
    Bundle,
    Card,
    Config,
    ConfigError,
    find_repo_root,
    load_cards,
    load_config,
    split_negative,
)
from lqcowork.package import expected_handoff

REPO_URL = "https://github.com/houfu/lq-plugin-cowork"
TESTING_DOC = f"{REPO_URL}/blob/main/docs/TESTING.md"
INSTALL_DOC = f"{REPO_URL}/blob/main/docs/INSTALL.md"
ISSUE_FORM = f"{REPO_URL}/issues/new?template=uat-report.yml"
LATEST_RELEASE = f"{REPO_URL}/releases/latest"
TRACKING_TITLE = "UAT status board"
DEFAULT_OUT = "dist/uat-issues"

BUCKET_NOTE = {
    "amber": (
        "**amber** — machinery (scripts, schemas, validators, local apps) was "
        "removed by this adaptation and replaced with instructions. Amber is where "
        "the risk is, so read the notes below before you start."
    ),
    "green": (
        "**green** — little had to change from upstream, so this one should "
        "behave much as its description says. Worth confirming exactly that."
    ),
}


@dataclass(frozen=True)
class Label:
    name: str
    color: str
    description: str


BASE_LABELS = (
    Label(
        "help wanted",
        "008672",
        "Anyone with a Microsoft 365 Copilot tenant can pick this up",
    ),
    Label(
        "uat",
        "0e8a16",
        "Acceptance testing of a shipped skill in a live Cowork tenant",
    ),
)

BUNDLE_LABEL_COLORS = {
    "litigation": "5319e7",
    "transactional": "1d76db",
}
FALLBACK_LABEL_COLOR = "ededed"


class GhError(RuntimeError):
    """The ``gh`` CLI is missing, unauthenticated, or returned an error."""


@dataclass(frozen=True)
class SkillIssue:
    """One skill's issue: its title, its body, and where it ships."""

    name: str
    title: str
    body: str
    bundles: tuple[Bundle, ...]

    @property
    def filename(self) -> str:
        return f"{self.name}.md"

    @property
    def labels(self) -> tuple[str, ...]:
        bundle_labels = tuple(bundle_label(b) for b in self.bundles)
        return ("help wanted", "uat", *bundle_labels)


def bundle_key(bundle: Bundle) -> str:
    """``legalquants-litigation-cowork`` -> ``litigation``."""
    key = bundle.id
    for prefix in ("legalquants-",):
        key = key.removeprefix(prefix)
    return key.removesuffix("-cowork") or bundle.id


def bundle_label(bundle: Bundle) -> str:
    return f"bundle:{bundle_key(bundle)}"


def labels_for(config: Config) -> list[Label]:
    """Every label ``--create`` needs, including one per bundle."""
    labels = list(BASE_LABELS)
    for bundle in config.bundles:
        key = bundle_key(bundle)
        labels.append(
            Label(
                bundle_label(bundle),
                BUNDLE_LABEL_COLORS.get(key, FALLBACK_LABEL_COLOR),
                f"Affects the {bundle.id} bundle",
            )
        )
    return labels


def first_sentence(text: str) -> str:
    """The first sentence of a card description, whitespace normalised."""
    flat = " ".join(text.split())
    match = re.search(r"(?<!\b[A-Z])\.\s", flat)
    return flat[: match.start() + 1] if match else flat


def anchor(heading: str) -> str:
    """The fragment GitHub generates for a Markdown heading.

    GitHub drops punctuation and then turns each remaining whitespace
    character into a hyphen; it does not collapse runs, so a heading with an
    em dash between spaces yields a double hyphen.
    """
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    return re.sub(r"\s", "-", slug)


def bundles_for(config: Config, name: str) -> tuple[Bundle, ...]:
    return tuple(b for b in config.bundles if name in b.skills)


def shipped_skills(config: Config) -> list[str]:
    """Every skill in any bundle, in bundle then membership order."""
    names: list[str] = []
    for bundle in config.bundles:
        for name in bundle.skills:
            if name not in names:
                names.append(name)
    return names


def skill_title(name: str, bundles: tuple[Bundle, ...]) -> str:
    joined = " + ".join(b.name_short for b in bundles)
    return f"UAT: {name} ({joined})"


def _negative_expectation(bundles: tuple[Bundle, ...], target: str) -> str:
    """One expectation line, or one per bundle where they disagree."""
    rendered = {b.name_short: expected_handoff(b, target) for b in bundles}
    distinct = set(rendered.values())
    if len(distinct) == 1:
        return distinct.pop()
    return " · ".join(f"{short}: {text}" for short, text in rendered.items())


def routing_checklist(card: Card, bundles: tuple[Bundle, ...]) -> list[str]:
    lines: list[str] = []
    for prompt in card.triggers.positive:
        lines.append(f"- [ ] `{prompt}`")
        lines.append(f"      → activate `{card.name}`")
    for raw in card.triggers.negative:
        prompt, target = split_negative(raw)
        lines.append(f"- [ ] `{prompt}`")
        lines.append(f"      → {_negative_expectation(bundles, target)}")
    return lines


def render_body(config: Config, card: Card, bundles: tuple[Bundle, ...]) -> str:
    ships_in = ", ".join(f"{b.name_short} (`{b.id}`)" for b in bundles)
    bucket = BUCKET_NOTE.get(card.bucket, f"**{card.bucket}**")
    testing_link = f"{TESTING_DOC}#{anchor(card.name)}"

    lines = [
        f"**What it does.** {first_sentence(card.description)}",
        "",
        f"- **Ships in:** {ships_in}",
        f"- **Package version:** {config.version} — "
        f"[download the packages]({LATEST_RELEASE})",
        f"- **Upstream pin:** `{config.sha7}` ({config.repo})",
        f"- **Adaptation bucket:** {bucket}",
        "",
        f"Install a bundle first ([docs/INSTALL.md]({INSTALL_DOC})). The whole "
        f"programme, including how to tell which skill actually activated, is "
        f"[docs/TESTING.md]({TESTING_DOC}). **Claim this issue in a comment** "
        "so two people do not test the same skill.",
        "",
        "## Part A — routing",
        "",
        "One fresh conversation per prompt. Attach nothing unless the prompt "
        "implies a file; where it does, attach one short synthetic document. "
        "Type each prompt exactly as written, then tick the box if it did what "
        "the line under it says.",
        "",
        *routing_checklist(card, bundles),
        "",
        "## Part B — behaviour",
        "",
        f"The smoke test for this skill is [docs/TESTING.md ‣ "
        f"{card.name}]({testing_link}). It gives the synthetic inputs to "
        "prepare, the exact prompt, what a pass looks like and what to watch "
        "for.",
        "",
        "- [ ] Prepared the synthetic inputs it describes",
        "- [ ] Ran the prompt in a fresh conversation",
        "- [ ] Checked every pass criterion, one at a time",
        "- [ ] Recorded the result — pass or defect — with a trimmed excerpt",
        "",
        "## Notes for testers",
        "",
    ]

    if card.notes:
        lines += [
            "What the adaptation changed from upstream, and therefore what "
            "most needs checking:",
            "",
            f"> {' '.join(card.notes.split())}",
        ]
    else:
        lines.append(
            "This card records no adaptation notes: the skill is close to "
            "upstream, and the question is simply whether it does what its "
            "description promises inside Cowork."
        )

    lines += [
        "",
        "## How to report",
        "",
        f"File one [UAT report]({ISSUE_FORM}) per result — passes too — or "
        "tick the boxes above and summarise in a comment here. Either way, a "
        "misfire needs the exact prompt you typed: that prompt becomes a new "
        "line in the card's `triggers`.",
        "",
        "**Sanitise everything.** No client material, no matter or party "
        "names, nothing from a live system, in text or in screenshots. Every "
        "document these tests use is invented on purpose.",
        "",
    ]
    return "\n".join(lines)


def build_issues(config: Config) -> list[SkillIssue]:
    names = shipped_skills(config)
    cards = load_cards(config, names)
    issues: list[SkillIssue] = []
    for name in names:
        card = cards[name]
        bundles = bundles_for(config, name)
        issues.append(
            SkillIssue(
                name=name,
                title=skill_title(name, bundles),
                body=render_body(config, card, bundles),
                bundles=bundles,
            )
        )
    return issues


def status_board(config: Config) -> list[str]:
    """The bundle/skill table, every cell 'not tested'."""
    lines = [
        "| Bundle | Skill | Routing | Behaviour |",
        "| --- | --- | --- | --- |",
    ]
    for bundle in config.bundles:
        for name in bundle.skills:
            lines.append(
                f"| {bundle_key(bundle)} | `{name}` | not tested | not tested |"
            )
    return lines


def render_index(config: Config, issues: list[SkillIssue]) -> str:
    lines = [
        "# UAT issues",
        "",
        f"One issue per shipped skill, package version {config.version}, "
        f"upstream `{config.sha7}`. Rendered by "
        "`tools/scripts/uat_issues.py`; do not edit these files by hand.",
        "",
        "`--create` files them on GitHub with the labels `help wanted`, `uat` "
        "and one per bundle, skipping any whose exact title is already open. "
        "`--tracking` creates or updates the single "
        f'"{TRACKING_TITLE}" issue.',
        "",
        "| Skill | Bundles | File | Issue title |",
        "| --- | --- | --- | --- |",
    ]
    for issue in issues:
        bundles = ", ".join(bundle_key(b) for b in issue.bundles)
        lines.append(
            f"| `{issue.name}` | {bundles} | "
            f"[{issue.filename}]({issue.filename}) | {issue.title} |"
        )
    lines += [
        "",
        "## Status board",
        "",
        "The same table as `docs/TESTING.md`, updated from closed UAT issues.",
        "",
        *status_board(config),
        "",
    ]
    return "\n".join(lines)


def render_tracking(
    config: Config,
    issues: list[SkillIssue],
    urls: dict[str, str],
) -> str:
    lines = [
        "Nothing in this repository has been exercised in a live Microsoft "
        "365 Copilot Cowork tenant. This issue tracks that, and links the "
        "per-skill issues where the work happens.",
        "",
        f"Package version **{config.version}**, upstream `{config.sha7}`. The "
        f"programme is [docs/TESTING.md]({TESTING_DOC}); installing a bundle "
        f"is [docs/INSTALL.md]({INSTALL_DOC}).",
        "",
        "## One issue per skill",
        "",
    ]
    for issue in issues:
        url = urls.get(issue.title)
        bundles = ", ".join(bundle_key(b) for b in issue.bundles)
        if url:
            lines.append(f"- [ ] {url} — `{issue.name}` ({bundles})")
        else:
            lines.append(
                f"- [ ] `{issue.name}` ({bundles}) — not filed yet: " f"`{issue.title}`"
            )
    lines += [
        "",
        "## Status board",
        "",
        "Updated from closed UAT issues. A skill passes routing when all "
        "eight of its trigger-test rows have been run and recorded in one "
        "tenant, and passes behaviour when its smoke test has been run with a "
        "result of pass.",
        "",
        *status_board(config),
        "",
    ]
    return "\n".join(lines)


def write_files(out_dir: Path, config: Config, issues: list[SkillIssue]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for issue in issues:
        target = out_dir / issue.filename
        target.write_text(issue.body, encoding="utf-8")
        written.append(target)
    index = out_dir / "index.md"
    index.write_text(render_index(config, issues), encoding="utf-8")
    written.append(index)
    return written


def gh(args: list[str]) -> str:
    """Run ``gh`` and return its stdout, raising :class:`GhError` on failure."""
    try:
        proc = subprocess.run(
            ["gh", *args],
            check=True,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise GhError(
            "the GitHub CLI (gh) is not installed; install it and run "
            "`gh auth login` before using --create or --tracking"
        ) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise GhError(f"gh {' '.join(args)} failed: {detail}") from exc
    return proc.stdout or ""


def list_issues(state: str) -> list[dict[str, object]]:
    raw = gh(
        [
            "issue",
            "list",
            "--state",
            state,
            "--limit",
            "500",
            "--json",
            "number,title,url",
        ]
    )
    return json.loads(raw or "[]")


def ensure_labels(config: Config) -> None:
    for label in labels_for(config):
        gh(
            [
                "label",
                "create",
                label.name,
                "--color",
                label.color,
                "--description",
                label.description,
                "--force",
            ]
        )


def create_issues(config: Config, issues: list[SkillIssue], out_dir: Path) -> int:
    ensure_labels(config)
    open_titles = {str(row["title"]) for row in list_issues("open")}
    created = 0
    for issue in issues:
        if issue.title in open_titles:
            print(f"skip   {issue.name}: an open issue already has that title")
            continue
        args = [
            "issue",
            "create",
            "--title",
            issue.title,
            "--body-file",
            str(out_dir / issue.filename),
        ]
        for label in issue.labels:
            args += ["--label", label]
        url = gh(args).strip()
        created += 1
        print(f"create {issue.name}: {url or 'created'}")
    print(f"{created} issue(s) created, {len(issues) - created} skipped")
    return created


def sync_tracking(config: Config, issues: list[SkillIssue], out_dir: Path) -> None:
    existing = list_issues("all")
    urls = {str(row["title"]): str(row["url"]) for row in existing}
    body_path = out_dir / "status-board.md"
    body_path.write_text(render_tracking(config, issues, urls), encoding="utf-8")

    match = next((row for row in existing if row["title"] == TRACKING_TITLE), None)
    if match is None:
        args = [
            "issue",
            "create",
            "--title",
            TRACKING_TITLE,
            "--body-file",
            str(body_path),
            "--label",
            "uat",
        ]
        print(f"create tracking issue: {gh(args).strip() or TRACKING_TITLE}")
        return
    gh(["issue", "edit", str(match["number"]), "--body-file", str(body_path)])
    print(f"update tracking issue: {match['url']}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render one GitHub issue per shipped skill from cowork.yaml and "
            "the skill cards."
        )
    )
    parser.add_argument(
        "--out",
        metavar="DIR",
        default=DEFAULT_OUT,
        help=f"where to write the Markdown (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="file the issues on GitHub with `gh`, skipping titles already open",
    )
    parser.add_argument(
        "--tracking",
        action="store_true",
        help=f'create or update the single "{TRACKING_TITLE}" issue',
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        root = find_repo_root()
        config = load_config(root)
        issues = build_issues(config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    written = write_files(out_dir, config, issues)
    print(f"wrote {len(written)} file(s) to {out_dir}")

    if not (args.create or args.tracking):
        return 0

    try:
        if args.create:
            create_issues(config, issues, out_dir)
        if args.tracking:
            sync_tracking(config, issues, out_dir)
    except GhError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
