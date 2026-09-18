"""Drift collection, pin rewriting and anchoring, against a local git upstream."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from lqcowork import bump
from lqcowork.config import load_cards, load_config

GIT_ENV = [
    "-c",
    "user.email=test@example.invalid",
    "-c",
    "user.name=Test",
    "-c",
    "commit.gpgsign=false",
]


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *GIT_ENV, *args], cwd=cwd, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.fixture
def git_upstream(fixture_repo: Path):
    """Turn the fixture's upstream tree into a two-commit git repository."""
    upstream = fixture_repo / "upstream"
    git(upstream, "init", "-b", "main")
    git(upstream, "add", "-A")
    git(upstream, "commit", "-m", "v1")
    first = git(upstream, "rev-parse", "HEAD")

    for path, old, new in (
        ("cowork.yaml", "sha: " + "a1b2c3d4" * 5, f"sha: {first}"),
        (
            "skills/alpha/skill.yaml",
            "anchored_to: " + "a1b2c3d4" * 5,
            f"anchored_to: {first}",
        ),
        (
            "skills/beta/skill.yaml",
            "anchored_to: " + "a1b2c3d4" * 5,
            f"anchored_to: {first}",
        ),
    ):
        target = fixture_repo / path
        target.write_text(target.read_text().replace(old, new), encoding="utf-8")

    skill = upstream / "skills/core/alpha/SKILL.md"
    skill.write_text(
        skill.read_text().replace(
            "The upstream description for alpha, which the card replaces wholesale.",
            "A completely rewritten upstream description.",
        ),
        encoding="utf-8",
    )
    (upstream / "skills/core/alpha/references/new.md").write_text("# New\n")
    (upstream / "skills/core/alpha/references/beta.md").unlink()
    git(upstream, "add", "-A")
    git(upstream, "commit", "-m", "v2")
    second = git(upstream, "rev-parse", "HEAD")
    return fixture_repo, upstream, first, second


def collect(fixture_repo: Path, upstream: Path, sha: str):
    config = load_config(fixture_repo)
    cards = load_cards(config, ["alpha", "beta"])
    tmp = Path(tempfile.mkdtemp(prefix="lqcowork-test-"))
    worktree = tmp / "upstream"
    try:
        git(upstream, "worktree", "add", "--detach", str(worktree), sha)
        return config, bump.collect_drift(
            config, upstream, sha, cards, worktree=worktree
        )
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(worktree)],
            cwd=upstream,
            capture_output=True,
        )
        shutil.rmtree(tmp, ignore_errors=True)


class TestCollectDrift:
    def test_sees_what_moved(self, git_upstream):
        fixture_repo, upstream, _, second = git_upstream
        _, report = collect(fixture_repo, upstream, second)
        alpha = next(s for s in report.skills if s.name == "alpha")
        beta = next(s for s in report.skills if s.name == "beta")
        assert alpha.skill_md_changed
        assert alpha.description_changed
        assert alpha.companions_added == ["references/new.md"]
        assert alpha.companions_removed == ["references/beta.md"]
        assert alpha.diffstat
        assert not beta.interesting
        assert report.has_changes

    def test_full_file_overlay_is_flagged_when_its_base_moves(self, git_upstream):
        fixture_repo, upstream, _, second = git_upstream
        skill = upstream / "skills/core/beta/SKILL.md"
        skill.write_text(skill.read_text() + "\nAn upstream addition.\n")
        git(upstream, "add", "-A")
        git(upstream, "commit", "-m", "v3")
        third = git(upstream, "rev-parse", "HEAD")
        _, report = collect(fixture_repo, upstream, third)
        beta = next(s for s in report.skills if s.name == "beta")
        assert beta.overlay_stale

    def test_lists_upstream_skills_in_no_bundle(self, git_upstream):
        fixture_repo, upstream, _, second = git_upstream
        _, report = collect(fixture_repo, upstream, second)
        assert report.unbundled == ["gamma"]

    def test_report_renders(self, git_upstream):
        fixture_repo, upstream, _, second = git_upstream
        config, report = collect(fixture_repo, upstream, second)
        text = bump.render_report(config, report)
        assert "# Upstream drift report" in text
        assert "| alpha | `core/alpha` |" in text
        assert "description changed" in text
        assert "## Upstream skills in no bundle" in text
        assert "- gamma" in text
        assert "## Next steps" in text

    def test_anchor_failures_are_collected_not_raised(self, git_upstream):
        fixture_repo, upstream, _, second = git_upstream
        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(card.read_text().replace("expect: 1", "expect: 9"))
        _, report = collect(fixture_repo, upstream, second)
        assert [i.code for i in report.anchors] == ["LQC-A001"]
        assert report.broken

    def test_missing_upstream_folder_is_reported(self, git_upstream):
        fixture_repo, upstream, _, second = git_upstream
        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(
            card.read_text().replace("upstream: core/alpha", "upstream: core/zeta")
        )
        _, report = collect(fixture_repo, upstream, second)
        alpha = next(s for s in report.skills if s.name == "alpha")
        assert alpha.missing
        assert "LQC-A001" in [i.code for i in report.anchors]


@pytest.fixture
def git_upstream_with_remote(git_upstream, tmp_path):
    """The two-commit upstream, plus a bare 'origin' it can fetch from."""
    fixture_repo, upstream, first, second = git_upstream
    remote = tmp_path / "remote.git"
    git(upstream, "clone", "--bare", str(upstream), str(remote))
    git(upstream, "remote", "add", "origin", str(remote))
    git(upstream, "fetch", "origin")
    # roll the checkout back so the pin really is behind origin/main
    for path, old, new in (
        ("cowork.yaml", f"sha: {second}", f"sha: {first}"),
        ("skills/alpha/skill.yaml", f"anchored_to: {second}", f"anchored_to: {first}"),
    ):
        target = fixture_repo / path
        target.write_text(target.read_text().replace(old, new), encoding="utf-8")
    return fixture_repo, upstream, first, second


class TestBumpUpstreamDryRun:
    def test_reports_without_moving_anything(self, git_upstream_with_remote):
        fixture_repo, upstream, first, second = git_upstream_with_remote
        head_before = git(upstream, "rev-parse", "HEAD")
        config = load_config(fixture_repo)
        status, target, report = bump.bump_upstream(config, dry_run=True)

        assert status == 0
        assert report.from_sha == first
        assert report.to_sha == second
        assert target == fixture_repo / "dist" / "upstream-drift.md"

        text = target.read_text()
        assert f"- from: `{first}`" in text
        assert f"- to: `{second}`" in text
        assert "- changed: yes" in text
        assert "| alpha | `core/alpha` |" in text
        assert "description changed" in text
        assert "- gamma" in text

        # the submodule and the pin are exactly where they were
        assert git(upstream, "rev-parse", "HEAD") == head_before
        assert f"sha: {first}" in (fixture_repo / "cowork.yaml").read_text()

    def test_cleans_up_its_worktree(self, git_upstream_with_remote):
        fixture_repo, upstream, _, _ = git_upstream_with_remote
        bump.bump_upstream(load_config(fixture_repo), dry_run=True)
        listing = git(upstream, "worktree", "list")
        assert len(listing.strip().split("\n")) == 1
        assert not (upstream / ".git" / "worktrees").exists()

    def test_exit_two_when_a_card_no_longer_applies(self, git_upstream_with_remote):
        fixture_repo, _, _, _ = git_upstream_with_remote
        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(card.read_text().replace("expect: 1", "expect: 7"))
        status, target, report = bump.bump_upstream(
            load_config(fixture_repo), dry_run=True
        )
        assert status == 2
        assert report.broken
        assert "LQC-A001" in target.read_text()

    def test_custom_report_path(self, git_upstream_with_remote, tmp_path):
        fixture_repo, _, _, _ = git_upstream_with_remote
        target_path = tmp_path / "reports" / "drift.md"
        _, target, _ = bump.bump_upstream(
            load_config(fixture_repo), dry_run=True, report_path=target_path
        )
        assert target == target_path
        assert target_path.is_file()


class TestPinAndAnchor:
    def test_write_pin_keeps_comments(self, fixture_repo):
        path = fixture_repo / "cowork.yaml"
        path.write_text("# a comment\n" + path.read_text(), encoding="utf-8")
        config = load_config(fixture_repo)
        bump.write_pin(config, "c" * 40)
        text = path.read_text()
        assert text.startswith("# a comment\n")
        assert f"sha: {'c' * 40}" in text

    def test_anchor_updates_every_card(self, fixture_repo):
        path = fixture_repo / "cowork.yaml"
        path.write_text(
            path.read_text().replace("sha: " + "a1b2c3d4" * 5, "sha: " + "d" * 40),
            encoding="utf-8",
        )
        config = load_config(fixture_repo)
        assert sorted(bump.anchor(config)) == ["alpha", "beta"]
        for name in ("alpha", "beta"):
            text = (fixture_repo / "skills" / name / "skill.yaml").read_text()
            assert f"anchored_to: {'d' * 40}" in text
        assert bump.anchor(load_config(fixture_repo)) == []

    def test_anchor_one_skill(self, fixture_repo):
        path = fixture_repo / "cowork.yaml"
        path.write_text(
            path.read_text().replace("sha: " + "a1b2c3d4" * 5, "sha: " + "e" * 40),
            encoding="utf-8",
        )
        config = load_config(fixture_repo)
        assert bump.anchor(config, "beta") == ["beta"]
        assert "a1b2c3d4" in (fixture_repo / "skills/alpha/skill.yaml").read_text()
