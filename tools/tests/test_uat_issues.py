"""The UAT issue renderer: one body per shipped skill, and nothing lost."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from lqcowork.config import ConfigError, load_cards, load_config, split_negative


def _load_script(root: Path) -> ModuleType:
    """Import ``tools/scripts/uat_issues.py``, which is not a package module."""
    path = root / "tools/scripts/uat_issues.py"
    spec = importlib.util.spec_from_file_location("uat_issues", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolve annotations through sys.modules[cls.__module__].
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def script(real_root: Path) -> ModuleType:
    return _load_script(real_root)


@pytest.fixture
def issues(script: ModuleType, real_root: Path) -> list:
    config = load_config(real_root)
    try:
        load_cards(config, script.shipped_skills(config))
    except ConfigError as exc:  # a card in cowork.yaml is not written yet
        pytest.skip(str(exc))
    return script.build_issues(config)


def test_one_issue_per_shipped_skill(script: ModuleType, real_root: Path, issues):
    config = load_config(real_root)
    assert [issue.name for issue in issues] == script.shipped_skills(config)
    assert issues, "cowork.yaml lists no skills"


def test_every_issue_has_a_body(issues):
    for issue in issues:
        assert issue.body.strip(), f"{issue.name}: empty body"
        assert "## Part A — routing" in issue.body
        assert "## Part B — behaviour" in issue.body
        assert f"`{issue.name}`" in issue.body


def test_titles_are_unique_and_shaped(issues):
    titles = [issue.title for issue in issues]
    assert len(titles) == len(set(titles))
    for issue in titles:
        assert issue.startswith("UAT: ")
    both = [i for i in issues if len(i.bundles) > 1]
    assert both, "expected at least one skill shared between bundles"
    for issue in both:
        assert " + " in issue.title


def test_every_trigger_prompt_appears_in_its_body(real_root: Path, issues):
    config = load_config(real_root)
    cards = load_cards(config, [issue.name for issue in issues])
    for issue in issues:
        card = cards[issue.name]
        for prompt in card.triggers.positive:
            assert prompt in issue.body, f"{issue.name}: missing positive {prompt!r}"
        for raw in card.triggers.negative:
            prompt, _ = split_negative(raw)
            assert prompt in issue.body, f"{issue.name}: missing negative {prompt!r}"


def test_negative_prompts_say_they_must_not_activate(real_root: Path, issues):
    config = load_config(real_root)
    cards = load_cards(config, [issue.name for issue in issues])
    for issue in issues:
        if cards[issue.name].triggers.negative:
            assert "must not activate" in issue.body


def test_labels_cover_every_bundle_the_skill_ships_in(script: ModuleType, issues):
    for issue in issues:
        assert "help wanted" in issue.labels
        assert "uat" in issue.labels
        for bundle in issue.bundles:
            assert script.bundle_label(bundle) in issue.labels


def test_behaviour_link_points_at_a_real_testing_heading(
    script: ModuleType, real_root: Path, issues
):
    testing = (real_root / "docs/TESTING.md").read_text(encoding="utf-8")
    headings = {
        script.anchor(line.lstrip("#").strip())
        for line in testing.splitlines()
        if line.startswith("#")
    }
    for issue in issues:
        fragment = script.anchor(issue.name)
        assert fragment in headings, f"docs/TESTING.md has no section for {issue.name}"
        assert f"#{fragment})" in issue.body


def test_notes_are_carried_for_amber_cards(real_root: Path, issues):
    config = load_config(real_root)
    cards = load_cards(config, [issue.name for issue in issues])
    for issue in issues:
        notes = cards[issue.name].notes
        if notes:
            assert " ".join(notes.split())[:60] in issue.body


def test_first_sentence_stops_at_the_first_full_stop(script: ModuleType):
    assert script.first_sentence("One thing. Two things.") == "One thing."
    assert script.first_sentence("No full stop here") == "No full stop here"
    assert script.first_sentence("Wrapped\nover lines. Next.") == "Wrapped over lines."


def test_anchor_matches_github_slugging(script: ModuleType):
    assert script.anchor("cite-check") == "cite-check"
    assert script.anchor("Part A — routing") == "part-a--routing"


def test_writes_index_and_one_file_per_skill(
    script: ModuleType, real_root: Path, issues, tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(real_root)
    assert script.main(["--out", str(tmp_path)]) == 0
    written = {path.name for path in tmp_path.iterdir()}
    assert "index.md" in written
    for issue in issues:
        assert issue.filename in written
    index = (tmp_path / "index.md").read_text(encoding="utf-8")
    for issue in issues:
        assert issue.title in index
    assert "| Bundle | Skill | Routing | Behaviour |" in index
    assert "not tested" in index


def test_tracking_body_links_known_issues_and_flags_missing_ones(
    script: ModuleType, real_root: Path, issues
):
    config = load_config(real_root)
    first, rest = issues[0], issues[1:]
    urls = {first.title: "https://github.com/houfu/lq-plugin-cowork/issues/1"}
    body = script.render_tracking(config, issues, urls)
    assert "https://github.com/houfu/lq-plugin-cowork/issues/1" in body
    for issue in rest:
        assert f"not filed yet: `{issue.title}`" in body
    assert "| Bundle | Skill | Routing | Behaviour |" in body
