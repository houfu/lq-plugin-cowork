"""Config and card loading, including the shape errors we refuse to build on."""

from __future__ import annotations

from pathlib import Path

import pytest

from lqcowork.config import (
    ConfigError,
    find_repo_root,
    load_card,
    load_cards,
    load_config,
    upstream_skill_names,
)


def edit(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text().replace(old, new), encoding="utf-8")


class TestRepoRoot:
    def test_walks_up_to_cowork_yaml(self, fixture_repo):
        deep = fixture_repo / "skills" / "alpha" / "sections"
        assert find_repo_root(deep) == fixture_repo.resolve()

    def test_missing_config_raises(self, tmp_path):
        with pytest.raises(ConfigError, match="no cowork.yaml"):
            find_repo_root(tmp_path)


class TestConfig:
    def test_loads(self, fixture_repo):
        config = load_config(fixture_repo)
        assert config.sha7 == "a1b2c3d"
        assert [b.id for b in config.bundles] == ["test-bundle"]
        assert config.bundles[0].skills == ("alpha", "beta")
        assert config.developer["name"] == "Test Developer"

    def test_upstream_skill_names_are_longest_first(self, fixture_repo):
        names = upstream_skill_names(load_config(fixture_repo))
        assert names == ["alpha", "gamma", "beta"]

    def test_bad_sha_rejected(self, fixture_repo):
        edit(fixture_repo / "cowork.yaml", "sha: a1b2c3d4", "sha: short")
        with pytest.raises(ConfigError, match="upstream.sha"):
            load_config(fixture_repo)

    def test_bad_version_rejected(self, fixture_repo):
        edit(fixture_repo / "cowork.yaml", "version: 0.1.0", "version: 0.1")
        with pytest.raises(ConfigError, match="package.version"):
            load_config(fixture_repo)

    def test_bad_guid_rejected(self, fixture_repo):
        edit(fixture_repo / "cowork.yaml", "guid: 5d40f9d0", "guid: nope-")
        with pytest.raises(ConfigError, match="guid"):
            load_config(fixture_repo)

    def test_manifest_length_limit_rejected(self, fixture_repo):
        edit(fixture_repo / "cowork.yaml", "short: Test Bundle", "short: " + "x" * 31)
        with pytest.raises(ConfigError, match="name.short"):
            load_config(fixture_repo)

    def test_unknown_bundle(self, fixture_repo):
        with pytest.raises(ConfigError, match="unknown bundle"):
            load_config(fixture_repo).bundle("nope")


class TestCards:
    def test_loads(self, fixture_repo):
        card = load_card(load_config(fixture_repo), "alpha")
        assert card.upstream == "core/alpha"
        assert card.bucket == "amber"
        assert card.notes
        assert card.exclude == ("scripts/**",)
        assert card.replace[0].expect == 1
        assert card.replace[0].files == ("SKILL.md",)
        assert card.sections[1].delete is True
        assert card.triggers.negative[0] == "Do the beta thing instead. -> beta"
        assert "-> none" in card.triggers.negative[-1]

    def test_missing_card_is_named(self, fixture_repo):
        (fixture_repo / "skills/beta/skill.yaml").unlink()
        with pytest.raises(ConfigError, match="missing adaptation cards for: beta"):
            load_cards(load_config(fixture_repo), ["alpha", "beta"])

    def test_name_must_match_the_folder(self, fixture_repo):
        edit(fixture_repo / "skills/alpha/skill.yaml", "name: alpha", "name: other")
        with pytest.raises(ConfigError, match="does not match folder"):
            load_card(load_config(fixture_repo), "alpha")

    def test_triggers_are_required(self, fixture_repo):
        path = fixture_repo / "skills/beta/skill.yaml"
        path.write_text(path.read_text().split("triggers:")[0], encoding="utf-8")
        with pytest.raises(ConfigError, match="triggers"):
            load_card(load_config(fixture_repo), "beta")

    def test_section_needs_file_or_delete(self, fixture_repo):
        edit(
            fixture_repo / "skills/alpha/skill.yaml",
            "    file: sections/automation.md",
            "",
        )
        with pytest.raises(ConfigError, match="file' or 'delete"):
            load_card(load_config(fixture_repo), "alpha")

    def test_replace_rule_needs_from_and_to(self, fixture_repo):
        edit(
            fixture_repo / "skills/alpha/skill.yaml",
            '    to: "Open the alpha folder"',
            "",
        )
        with pytest.raises(ConfigError, match="missing required key 'to'"):
            load_card(load_config(fixture_repo), "alpha")
