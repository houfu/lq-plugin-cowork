"""release-check: a tag held against cowork.yaml, CHANGELOG.md and dist/."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lqcowork.cli import main
from lqcowork.config import load_config
from lqcowork.release import changelog_versions, check_release, parse_tag

CHANGELOG = """# Changelog

## [Unreleased]

## [0.1.0] - 2026-09-18

### Added

- The first release.

[Unreleased]: https://example.invalid/compare/v0.1.0...HEAD
[0.1.0]: https://example.invalid/releases/tag/v0.1.0
"""


@pytest.fixture
def repo(fixture_repo: Path, monkeypatch) -> Path:
    """The fixture repository with a changelog, as the cwd."""
    (fixture_repo / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    monkeypatch.chdir(fixture_repo)
    return fixture_repo


@pytest.fixture
def built(repo: Path) -> Path:
    assert main(["build"]) == 0
    return repo


def run(capsys, *argv: str) -> tuple[int, str]:
    code = main(["release-check", *argv])
    return code, capsys.readouterr().out


class TestTagParsing:
    @pytest.mark.parametrize(
        "tag,version,core,prerelease",
        [
            ("v0.1.0", "0.1.0", "0.1.0", None),
            ("v1.2.3", "1.2.3", "1.2.3", None),
            ("v1.2.0-rc.1", "1.2.0-rc.1", "1.2.0", "rc.1"),
            ("v10.20.30-beta", "10.20.30-beta", "10.20.30", "beta"),
            ("v1.2.0+20260918", "1.2.0+20260918", "1.2.0", None),
        ],
    )
    def test_accepts_semver(self, tag, version, core, prerelease):
        parsed = parse_tag(tag)
        assert parsed is not None
        assert (parsed.version, parsed.core, parsed.prerelease) == (
            version,
            core,
            prerelease,
        )

    @pytest.mark.parametrize(
        "tag",
        ["0.1.0", "v1.2", "v1", "vX.Y.Z", "v01.2.0", "v1.2.0-", "v1.2.0.1", "v"],
    )
    def test_rejects_everything_else(self, tag):
        assert parse_tag(tag) is None

    def test_surrounding_whitespace_is_ignored(self):
        assert parse_tag("  v1.2.0\n") == parse_tag("v1.2.0")

    def test_changelog_versions_are_in_file_order(self):
        assert changelog_versions(CHANGELOG) == ["Unreleased", "0.1.0"]


class TestPasses:
    def test_before_anything_is_built(self, repo, capsys):
        code, out = run(capsys, "--tag", "v0.1.0")
        assert code == 0
        assert "release-check passed" in out
        assert "not built, so nothing to compare" in out

    def test_against_a_built_manifest(self, built, capsys):
        code, out = run(capsys, "--tag", "v0.1.0")
        assert code == 0
        assert "dist/test-bundle/manifest.json: version 0.1.0" in out
        assert "CHANGELOG.md has a '## [0.1.0]' section" in out

    def test_a_prerelease_tag_falls_back_to_the_core_section(self, built, capsys):
        code, out = run(capsys, "--tag", "v0.1.0-rc.1")
        assert code == 0
        assert "pre-release rc.1" in out
        assert "'## [0.1.0]' section" in out

    def test_a_prerelease_may_have_its_own_section(self, repo, capsys):
        path = repo / "CHANGELOG.md"
        path.write_text(
            path.read_text().replace("## [Unreleased]", "## [0.1.0-rc.1] - 2026-09-01"),
            encoding="utf-8",
        )
        code, out = run(capsys, "--tag", "v0.1.0-rc.1")
        assert code == 0
        assert "'## [0.1.0-rc.1]' section" in out

    def test_an_out_directory_is_what_gets_checked(self, repo, tmp_path, capsys):
        out_dir = tmp_path / "elsewhere"
        assert main(["build", "--out", str(out_dir)]) == 0
        code, out = run(capsys, "--tag", "v0.1.0", "--out", str(out_dir))
        assert code == 0
        assert str(out_dir / "test-bundle" / "manifest.json") in out


class TestFailures:
    def test_a_tag_that_is_not_semver_stops_there(self, built, capsys):
        code, out = run(capsys, "--tag", "release-1")
        assert code == 2
        assert "is not 'v' followed by a semver version" in out
        assert "1 of 1 checks" in out

    def test_a_version_the_manifest_does_not_carry(self, built, capsys):
        code, out = run(capsys, "--tag", "v0.2.0")
        assert code == 2
        assert "cowork.yaml package.version is 0.1.0" in out
        assert "but the tag says 0.2.0" in out

    def test_a_changelog_without_a_section_for_the_tag(self, repo, capsys):
        path = repo / "CHANGELOG.md"
        path.write_text(
            path.read_text().replace("[0.1.0]", "[0.0.9]"), encoding="utf-8"
        )
        code, out = run(capsys, "--tag", "v0.1.0")
        assert code == 2
        assert "has no '## [0.1.0]' section" in out
        assert "0.0.9" in out

    def test_no_changelog_at_all(self, repo, capsys):
        (repo / "CHANGELOG.md").unlink()
        code, out = run(capsys, "--tag", "v0.1.0")
        assert code == 2
        assert "CHANGELOG.md does not exist" in out

    def test_a_stale_built_manifest(self, built, capsys):
        manifest = built / "dist" / "test-bundle" / "manifest.json"
        data = json.loads(manifest.read_text())
        data["version"] = "0.0.9"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        code, out = run(capsys, "--tag", "v0.1.0")
        assert code == 2
        assert "version '0.0.9', but the tag says 0.1.0" in out


class TestUsageErrors:
    def test_a_missing_tag_is_exit_1(self, repo, capsys):
        assert main(["release-check"]) == 1
        assert "--tag vX.Y.Z is required" in capsys.readouterr().err

    def test_a_manifest_that_is_not_json_is_exit_1(self, built, capsys):
        manifest = built / "dist" / "test-bundle" / "manifest.json"
        manifest.write_text("{not json", encoding="utf-8")
        assert main(["release-check", "--tag", "v0.1.0"]) == 1
        assert "cannot be read as JSON" in capsys.readouterr().err


class TestApi:
    def test_every_check_is_reported_not_just_the_failures(self, repo):
        config = load_config(repo)
        result = check_release(config, "v9.9.9")
        assert [check.ok for check in result.checks] == [True, False, False, True]
        assert len(result.failures) == 2
        assert result.lines()[0] == "release-check v9.9.9"
        assert result.lines()[-1] == "release-check failed: 2 of 4 checks"
