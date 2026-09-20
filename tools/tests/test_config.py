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


class TestMirroredBundles:
    def test_derives_groups_then_includes(self, mirror_repo):
        config = load_config(mirror_repo)
        bundle = config.bundles[0]
        # core alphabetically, then the include_skills entry
        assert bundle.skills == ("alpha", "beta", "gamma")
        assert bundle.mirror is not None
        assert bundle.mirror.plugin_id == "test-plugin"
        assert bundle.mirror.groups == ("core",)
        assert bundle.mirror.includes == ("extra/gamma",)
        assert bundle.mirror.display_name == "The Upstream Test Plugin"
        assert (
            bundle.mirror.short_description == "An upstream plugin a bundle can mirror"
        )

    def test_report_line_names_the_derivation(self, mirror_repo):
        line = load_config(mirror_repo).bundles[0].mirror.line()
        assert line == (
            "Mirrors upstream plugin test-plugin: groups core; "
            "includes extra/gamma; excludes none"
        )

    def test_exclude_removes_the_skill_and_keeps_the_reason(self, mirror_repo):
        edit(
            mirror_repo / "cowork.yaml",
            "    exclude_skills: []",
            "    exclude_skills:\n"
            "      - name: gamma\n"
            '        reason: "needs a connector we do not ship"',
        )
        bundle = load_config(mirror_repo).bundles[0]
        assert bundle.skills == ("alpha", "beta")
        assert [e.name for e in bundle.mirror.excludes] == ["gamma"]
        assert bundle.mirror.excludes[0].reason == "needs a connector we do not ship"

    def test_exclude_without_a_reason_is_refused(self, mirror_repo):
        edit(
            mirror_repo / "cowork.yaml",
            "    exclude_skills: []",
            "    exclude_skills:\n      - name: gamma",
        )
        with pytest.raises(ConfigError, match="reason"):
            load_config(mirror_repo)

    def test_mirror_and_skills_together_is_refused(self, mirror_repo):
        edit(
            mirror_repo / "cowork.yaml",
            "    exclude_skills: []",
            "    skills:\n      - alpha",
        )
        with pytest.raises(ConfigError, match="'mirror' and 'skills'"):
            load_config(mirror_repo)

    def test_unknown_plugin_id_is_refused(self, mirror_repo):
        edit(mirror_repo / "cowork.yaml", "mirror: test-plugin", "mirror: nope")
        with pytest.raises(ConfigError, match="not a plugin in plugin.release.yaml"):
            load_config(mirror_repo)

    def test_exclude_on_an_explicit_list_is_refused(self, fixture_repo):
        edit(
            fixture_repo / "cowork.yaml",
            "    skills:\n      - alpha",
            "    exclude_skills:\n      - name: gamma\n"
            '        reason: "x"\n    skills:\n      - alpha',
        )
        with pytest.raises(ConfigError, match="only a mirrored bundle excludes"):
            load_config(fixture_repo)

    def test_an_explicit_list_still_works(self, fixture_repo):
        bundle = load_config(fixture_repo).bundles[0]
        assert bundle.mirror is None
        assert bundle.skills == ("alpha", "beta")


class TestCoworkBlock:
    def test_parsed_onto_the_card(self, fixture_repo):
        card = load_card(load_config(fixture_repo), "alpha")
        assert card.cowork is not None
        assert card.cowork_problems == ()
        assert card.tier == 2
        assert card.status == "probe-gated"
        assert card.cowork.differs.startswith("The original ran a bundled program")
        assert [k.id for k in card.known_issues] == ["KI-alpha-1"]
        assert card.known_issues[0].failure == "silent"
        assert card.known_issues[0].probe == "P3"
        assert card.cowork.probes == ("P3",)
        assert card.cowork.workarounds[0].instead_of.startswith("a bundled script")

    def test_missing_block_is_collected_not_raised(self, fixture_repo):
        path = fixture_repo / "skills/beta/skill.yaml"
        path.write_text(
            path.read_text().replace("cowork:", "unused:"), encoding="utf-8"
        )
        card = load_card(load_config(fixture_repo), "beta")
        assert card.cowork is None
        assert any("`cowork` block is missing" in p for p in card.cowork_problems)

    def test_bad_tier_and_status_are_collected(self, fixture_repo):
        path = fixture_repo / "skills/gamma/skill.yaml"
        path.write_text(
            path.read_text()
            .replace("tier: 1", "tier: 9")
            .replace("status: shipped", "status: maybe"),
            encoding="utf-8",
        )
        card = load_card(load_config(fixture_repo), "gamma")
        assert card.cowork is None
        assert any("tier" in p for p in card.cowork_problems)
        assert any("status" in p for p in card.cowork_problems)

    def test_known_issue_needs_every_key(self, fixture_repo):
        path = fixture_repo / "skills/alpha/skill.yaml"
        path.write_text(
            path.read_text().replace("      failure: silent\n", ""), encoding="utf-8"
        )
        card = load_card(load_config(fixture_repo), "alpha")
        assert any("missing failure" in p for p in card.cowork_problems)

    def test_workaround_needs_both_keys(self, fixture_repo):
        path = fixture_repo / "skills/alpha/skill.yaml"
        path.write_text(
            path.read_text().replace(
                '      cowork: "the skill lists every document it read, so the '
                'count is visible"\n',
                "",
            ),
            encoding="utf-8",
        )
        card = load_card(load_config(fixture_repo), "alpha")
        assert any("missing cowork" in p for p in card.cowork_problems)

    def test_red_is_a_bucket(self, fixture_repo):
        edit(fixture_repo / "skills/alpha/skill.yaml", "bucket: amber", "bucket: red")
        assert load_card(load_config(fixture_repo), "alpha").bucket == "red"

    def test_an_unknown_bucket_is_refused(self, fixture_repo):
        edit(fixture_repo / "skills/alpha/skill.yaml", "bucket: amber", "bucket: puce")
        with pytest.raises(ConfigError, match="bucket"):
            load_card(load_config(fixture_repo), "alpha")


class TestProbes:
    def test_loaded_onto_the_config(self, fixture_repo):
        config = load_config(fixture_repo)
        assert [p.id for p in config.probes] == ["P3"]
        probe = config.probe("P3")
        assert probe.title.startswith("Does Cowork report tracked changes")
        assert probe.bad_outcome == "silent"
        assert probe.unlocks == ("alpha",)
        assert probe.setup.startswith("A synthetic DOCX")
        assert probe.passes.startswith("Insertions and deletions")
        assert probe.fails == "It reports no changes."

    def test_absent_file_means_no_probes(self, fixture_repo):
        (fixture_repo / "probes.yaml").unlink()
        assert load_config(fixture_repo).probes == ()

    def test_duplicate_ids_refused(self, fixture_repo):
        path = fixture_repo / "probes.yaml"
        body = path.read_text()
        path.write_text(body + body.split("probes:\n", 1)[1], encoding="utf-8")
        with pytest.raises(ConfigError, match="duplicate probe id"):
            load_config(fixture_repo)

    def test_unknown_bad_outcome_refused(self, fixture_repo):
        edit(fixture_repo / "probes.yaml", "bad_outcome: silent", "bad_outcome: odd")
        with pytest.raises(ConfigError, match="bad_outcome"):
            load_config(fixture_repo)

    def test_the_real_repository_defines_p1_to_p14(self, real_root):
        from lqcowork.config import load_probes

        probes = load_probes(real_root)
        assert [p.id for p in probes] == [f"P{n}" for n in range(1, 15)]
        for probe in probes:
            assert probe.title and probe.settles and probe.prompt
            assert probe.passes and probe.fails
