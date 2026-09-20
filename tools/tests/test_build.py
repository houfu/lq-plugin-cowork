"""The per-skill pipeline, end to end, against the fixture repository."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lqcowork import transforms
from lqcowork.build import Builder, BuildError
from lqcowork.config import load_config


@pytest.fixture
def built(fixture_repo: Path):
    config = load_config(fixture_repo)
    builder = Builder(config)
    result = builder.build()
    return config, builder, result


def read_skill(fixture_repo: Path, name: str) -> str:
    path = fixture_repo / "dist" / "test-bundle" / "skills" / name / "SKILL.md"
    return path.read_text(encoding="utf-8")


class TestCopyAndStrip:
    def test_strip_and_exclude_drop_the_right_files(self, fixture_repo, built):
        skill = fixture_repo / "dist" / "test-bundle" / "skills" / "alpha"
        names = sorted(p.relative_to(skill).as_posix() for p in skill.rglob("*"))
        assert "SKILL.md" in names
        assert "references/notes.md" in names
        assert "references/extra.md" in names  # from the card's files/ directory
        assert not any(n.startswith("scripts") for n in names)
        assert not any(n.startswith("agents") for n in names)
        assert "LICENSE" not in names
        assert ".hidden" not in names

    def test_root_files_and_icons_travel(self, fixture_repo, built):
        bundle = fixture_repo / "dist" / "test-bundle"
        for name in ("LICENSE", "NOTICE.md", "color.png", "outline.png"):
            assert (bundle / name).is_file()


class TestFrontmatter:
    def test_dropped_claude_only_keys(self, fixture_repo, built):
        text = read_skill(fixture_repo, "alpha")
        assert "argument-hint" not in text
        assert "disable-model-invocation" not in text

    def test_card_frontmatter_override_deletes(self, fixture_repo, built):
        fm = transforms.parse_document(read_skill(fixture_repo, "alpha")).frontmatter
        assert "compatibility" not in fm

    def test_stamped_keys(self, fixture_repo, built):
        config, _, _ = built
        fm = transforms.parse_document(read_skill(fixture_repo, "alpha")).frontmatter
        assert fm["name"] == "alpha"
        assert fm["description"].startswith("Does the alpha thing")
        assert fm["license"] == "Apache-2.0"
        assert fm["metadata"]["adapted-from"] == (
            f"LegalQuants/lq-plugin-oss@{config.sha7} skills/core/alpha"
        )
        assert fm["metadata"]["adapted-for"] == "Microsoft 365 Copilot Cowork"
        assert fm["metadata"]["legalquants.python-requires"] == ">=3.12"

    def test_key_order_and_block_scalar(self, fixture_repo, built):
        lines = read_skill(fixture_repo, "alpha").split("\n")
        assert lines[0] == "---"
        assert lines[1] == "name: alpha"
        assert lines[2].startswith("description: |")

    def test_modification_notice_is_the_first_body_line(self, fixture_repo, built):
        config, _, _ = built
        document = transforms.parse_document(read_skill(fixture_repo, "alpha"))
        first = document.body.lstrip("\n").split("\n")[0]
        assert first == (
            f"<!-- Modified from LegalQuants/lq-plugin-oss@{config.sha7} "
            "(skills/core/alpha) for Microsoft 365 Copilot Cowork. Apache-2.0; "
            "see LICENSE and NOTICE.md at the package root. -->"
        )

    def test_notice_is_not_duplicated_on_rebuild(self, fixture_repo):
        config = load_config(fixture_repo)
        Builder(config).build()
        first = read_skill(fixture_repo, "alpha")
        Builder(config).build()
        assert read_skill(fixture_repo, "alpha") == first
        assert first.count("<!-- Modified from") == 1


class TestMechanicalTransforms:
    def test_waivers_are_gone_everywhere(self, fixture_repo, built):
        skill = fixture_repo / "dist" / "test-bundle" / "skills" / "alpha"
        for path in skill.rglob("*.md"):
            assert "vendor-neutral-waiver" not in path.read_text(encoding="utf-8")

    def test_tokens_rewritten_but_paths_kept(self, fixture_repo, built):
        text = read_skill(fixture_repo, "alpha")
        assert (
            "Type beta to switch, or `beta` -- `beta` works too. Use beta now." in text
        )
        assert "references/beta.md" in text
        assert "../beta/SKILL.md" in text
        assert "$beta" not in text

    def test_companion_markdown_is_transformed_too(self, fixture_repo, built):
        config, _, _ = built
        notes = (
            fixture_repo / "dist/test-bundle/skills/alpha/references/notes.md"
        ).read_text(encoding="utf-8")
        assert notes == (
            f"<!-- Modified from LegalQuants/lq-plugin-oss@{config.sha7} "
            "(skills/core/alpha/references/notes.md) for Microsoft 365 Copilot "
            "Cowork. Apache-2.0; see LICENSE and NOTICE.md at the package "
            "root. -->\n\n# Notes\n\nSee beta and `beta`.\n"
            "Background: https://example.invalid/marketing\n"
        )


class TestCompanionNotices:
    """Contract section 5, step 10b."""

    def test_modified_companion_gets_the_modified_notice(self, fixture_repo, built):
        text = (
            fixture_repo / "dist/test-bundle/skills/alpha/references/notes.md"
        ).read_text(encoding="utf-8")
        assert text.startswith("<!-- Modified from LegalQuants/lq-plugin-oss@")
        assert "(skills/core/alpha/references/notes.md)" in text
        assert text.split("\n")[1] == ""

    def test_added_companion_gets_the_added_notice(self, fixture_repo, built):
        config, _, _ = built
        text = (
            fixture_repo / "dist/test-bundle/skills/alpha/references/extra.md"
        ).read_text(encoding="utf-8")
        assert text.startswith(
            "<!-- Added by the lq-plugin-cowork adaptation of "
            f"LegalQuants/lq-plugin-oss@{config.sha7}; not an upstream "
            "LegalQuants file."
        )
        assert text.split("\n")[1] == ""
        assert "Patched line." in text

    def test_identical_companion_is_untouched(self, fixture_repo, built):
        shipped = fixture_repo / "dist/test-bundle/skills/alpha/references/beta.md"
        upstream = fixture_repo / "upstream/skills/core/alpha/references/beta.md"
        assert shipped.read_bytes() == upstream.read_bytes()

    def test_notices_are_not_stacked_on_rebuild(self, fixture_repo, built):
        config, _, _ = built
        Builder(config).build()
        text = (
            fixture_repo / "dist/test-bundle/skills/alpha/references/notes.md"
        ).read_text(encoding="utf-8")
        assert text.count("<!-- Modified from") == 1

    def test_non_markdown_companions_are_listed_not_modified(self, fixture_repo):
        skill = fixture_repo / "skills/alpha/files"
        (skill / "assets").mkdir(parents=True, exist_ok=True)
        (skill / "assets" / "template.html").write_text("<p>ours</p>\n")
        config = load_config(fixture_repo)
        result = Builder(config).build()
        alpha = next(s for s in result.bundles[0].skills if s.name == "alpha")
        assert alpha.unnoticed == ["assets/template.html"]
        shipped = fixture_repo / "dist/test-bundle/skills/alpha/assets/template.html"
        assert shipped.read_text() == "<p>ours</p>\n"


class TestOverlaysAndOverrides:
    def test_replace_rule_applied(self, fixture_repo, built):
        text = read_skill(fixture_repo, "alpha")
        assert "Open the alpha folder" in text
        assert "scripts/alpha.py" not in text

    def test_section_replaced_and_deleted(self, fixture_repo, built):
        text = read_skill(fixture_repo, "alpha")
        assert "## Automation is not available here" in text
        assert "## Automation is an optional enhancement" not in text
        assert "### A subsection" not in text
        assert "## Finish well" not in text
        assert "Say goodbye." not in text
        assert "## Keep this" in text

    def test_patch_applied(self, fixture_repo, built):
        extra = (
            fixture_repo / "dist/test-bundle/skills/alpha/references/extra.md"
        ).read_text(encoding="utf-8")
        assert extra.endswith("Patched line.\n")

    def test_full_file_overlay_replaces_the_body(self, fixture_repo, built):
        text = read_skill(fixture_repo, "beta")
        assert "Our own body" in text
        assert "Upstream body" not in text
        # the overlay still goes through the mechanical transforms
        assert "$alpha" not in text
        # ...and its frontmatter is documentation only
        fm = transforms.parse_document(text).frontmatter
        assert fm["description"].startswith("Does the beta thing")


class TestSymlinks:
    """Contract section 6, LQC-C007."""

    def test_symlinked_file_is_refused_and_not_packaged(self, fixture_repo, tmp_path):
        secret = tmp_path / "secret.md"
        secret.write_text("# not ours\n")
        link = fixture_repo / "upstream/skills/core/alpha/references/leak.md"
        link.symlink_to(secret)
        result = Builder(load_config(fixture_repo)).build()
        codes = [(i.code, i.location) for i in result.errors]
        assert ("LQC-C007", "references/leak.md") in codes
        shipped = fixture_repo / "dist/test-bundle/skills/alpha/references"
        assert not (shipped / "leak.md").exists()

    def test_symlinked_directory_is_not_followed(self, fixture_repo, tmp_path):
        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "secret.md").write_text("# not ours\n")
        link = fixture_repo / "upstream/skills/core/alpha/leaked"
        link.symlink_to(outside, target_is_directory=True)
        result = Builder(load_config(fixture_repo)).build()
        assert ("LQC-C007", "leaked") in [(i.code, i.location) for i in result.errors]
        shipped = fixture_repo / "dist/test-bundle/skills/alpha"
        assert not (shipped / "leaked").exists()

    def test_symlink_in_a_card_files_directory_is_refused(self, fixture_repo, tmp_path):
        secret = tmp_path / "secret.md"
        secret.write_text("# not ours\n")
        link = fixture_repo / "skills/alpha/files/references/leak.md"
        link.symlink_to(secret)
        result = Builder(load_config(fixture_repo)).build()
        assert "LQC-C007" in [i.code for i in result.errors]

    def test_symlink_makes_the_cli_exit_two(self, fixture_repo, tmp_path, monkeypatch):
        from lqcowork.cli import main

        secret = tmp_path / "secret.md"
        secret.write_text("# not ours\n")
        (fixture_repo / "upstream/skills/core/alpha/references/leak.md").symlink_to(
            secret
        )
        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 2


GLOB_RULE = "\n".join(
    [
        '  - from: "Notes"',
        '    to: "Reference notes"',
        '    files: ["references/*.md"]',
        "    expect: {count}",
    ]
)
ANCHOR_RULE = "    expect: 1"


class TestReplaceGlobs:
    """A `files:` glob spanning several files, with `expect` aggregated."""

    def _use_glob_rule(self, fixture_repo: Path, count: int) -> None:
        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(
            card.read_text().replace(
                ANCHOR_RULE, ANCHOR_RULE + "\n" + GLOB_RULE.format(count=count), 1
            ),
            encoding="utf-8",
        )
        # "Notes" now appears once in notes.md and once in the added extra.md
        extra = fixture_repo / "skills/alpha/files/references/extra.md"
        extra.write_text("# Extra\n\nBody line.\n\nNotes follow.\n", encoding="utf-8")
        patch = fixture_repo / "skills/alpha/patches/extra-note.patch"
        patch.write_text(
            "--- a/references/extra.md\n"
            "+++ b/references/extra.md\n"
            "@@ -1,5 +1,6 @@\n"
            " # Extra\n"
            " \n"
            " Body line.\n"
            " \n"
            " Reference notes follow.\n"
            "+Patched line.\n",
            encoding="utf-8",
        )

    def test_expect_is_aggregated_across_globbed_files(self, fixture_repo):
        self._use_glob_rule(fixture_repo, 2)
        Builder(load_config(fixture_repo)).build()
        skill = fixture_repo / "dist/test-bundle/skills/alpha/references"
        assert "# Reference notes" in (skill / "notes.md").read_text()
        assert "Reference notes follow." in (skill / "extra.md").read_text()

    def test_aggregate_mismatch_is_an_anchor_failure(self, fixture_repo):
        self._use_glob_rule(fixture_repo, 5)
        with pytest.raises(BuildError, match="LQC-A001"):
            Builder(load_config(fixture_repo)).build()


class TestManifest:
    def test_manifest_shape(self, fixture_repo, built):
        manifest = json.loads(
            (fixture_repo / "dist/test-bundle/manifest.json").read_text("utf-8")
        )
        assert list(manifest) == [
            "$schema",
            "manifestVersion",
            "version",
            "id",
            "developer",
            "name",
            "description",
            "icons",
            "accentColor",
            "agentSkills",
        ]
        assert manifest["manifestVersion"] == "1.28"
        assert manifest["icons"] == {"color": "color.png", "outline": "outline.png"}
        assert manifest["agentSkills"] == [
            {"folder": "./skills/alpha"},
            {"folder": "./skills/beta"},
        ]


class TestAnchorFailures:
    def _rewrite_card(self, fixture_repo: Path, old: str, new: str) -> None:
        path = fixture_repo / "skills" / "alpha" / "skill.yaml"
        path.write_text(path.read_text().replace(old, new), encoding="utf-8")

    def test_replace_count_mismatch_fails(self, fixture_repo):
        self._rewrite_card(fixture_repo, "expect: 1", "expect: 3")
        with pytest.raises(BuildError, match="LQC-A001"):
            Builder(load_config(fixture_repo)).build()

    def test_missing_anchor_text_fails(self, fixture_repo):
        self._rewrite_card(fixture_repo, "Run `scripts/alpha.py`", "Nothing like this")
        with pytest.raises(BuildError, match="LQC-A001"):
            Builder(load_config(fixture_repo)).build()

    def test_missing_section_heading_fails(self, fixture_repo):
        self._rewrite_card(fixture_repo, '"## Finish well"', '"## Never written"')
        with pytest.raises(BuildError, match="LQC-A001"):
            Builder(load_config(fixture_repo)).build()

    def test_failing_patch_fails(self, fixture_repo):
        patch = fixture_repo / "skills/alpha/patches/extra-note.patch"
        patch.write_text(
            patch.read_text().replace(
                " Introduced here:", " A line that is not there:"
            ),
            encoding="utf-8",
        )
        with pytest.raises(BuildError, match="LQC-A001"):
            Builder(load_config(fixture_repo)).build()

    def test_report_anchors_collects_instead_of_raising(self, fixture_repo):
        self._rewrite_card(fixture_repo, "expect: 1", "expect: 3")
        result = Builder(load_config(fixture_repo), report_anchors=True).build()
        assert [issue.code for issue in result.anchors] == ["LQC-A001"]

    def test_missing_upstream_folder_errors(self, fixture_repo):
        self._rewrite_card(fixture_repo, "upstream: core/alpha", "upstream: core/none")
        with pytest.raises(BuildError, match="does not exist"):
            Builder(load_config(fixture_repo)).build()


class TestGlobalReplace:
    def test_global_rule_counted_across_the_build(self, fixture_repo):
        path = fixture_repo / "cowork.yaml"
        path.write_text(
            path.read_text().replace(
                "replace: []",
                'replace:\n  - from: "the thing"\n    to: "the work"\n',
            ),
            encoding="utf-8",
        )
        Builder(load_config(fixture_repo)).build()
        assert "the work" in read_skill(fixture_repo, "alpha")

    def test_global_rule_that_never_matches_fails(self, fixture_repo):
        path = fixture_repo / "cowork.yaml"
        path.write_text(
            path.read_text().replace(
                "replace: []",
                'replace:\n  - from: "absent anchor"\n    to: "x"\n',
            ),
            encoding="utf-8",
        )
        with pytest.raises(BuildError, match="LQC-A001"):
            Builder(load_config(fixture_repo)).build()


def codes(issues) -> list[str]:
    return [i.code for i in issues]


class TestMissingCards:
    def test_b001_names_the_skill_and_the_bundle(self, mirror_repo):
        (mirror_repo / "skills/gamma/skill.yaml").unlink()
        result = Builder(load_config(mirror_repo)).build()
        assert codes(result.errors) == ["LQC-B001"]
        message = result.errors[0].message
        assert result.errors[0].skill == "gamma"
        assert "skills/gamma/" in message
        assert "exclude it from test-bundle with a reason" in message
        assert result.bundles == []

    def test_one_error_per_missing_card_not_per_bundle(self, mirror_repo):
        (mirror_repo / "skills/alpha/skill.yaml").unlink()
        (mirror_repo / "skills/beta/skill.yaml").unlink()
        result = Builder(load_config(mirror_repo)).build()
        assert sorted(i.skill for i in result.errors) == ["alpha", "beta"]

    def test_an_excluded_skill_needs_no_card(self, mirror_repo):
        (mirror_repo / "skills/gamma/skill.yaml").unlink()
        card = mirror_repo / "skills/alpha/skill.yaml"
        card.write_text(
            card.read_text().replace('    - "Do the gamma thing. -> gamma"\n', ""),
            encoding="utf-8",
        )
        path = mirror_repo / "cowork.yaml"
        path.write_text(
            path.read_text().replace(
                "    exclude_skills: []",
                "    exclude_skills:\n      - name: gamma\n"
                '        reason: "no card, and none wanted"',
            ),
            encoding="utf-8",
        )
        result = Builder(load_config(mirror_repo)).build()
        assert result.errors == []
        assert [s.name for s in result.bundles[0].skills] == ["alpha", "beta"]


class TestCardChecks:
    def _build(self, repo: Path):
        return Builder(load_config(repo)).build()

    def test_k001_missing_block(self, fixture_repo):
        path = fixture_repo / "skills/beta/skill.yaml"
        path.write_text(
            path.read_text().replace("cowork:", "unused:"), encoding="utf-8"
        )
        result = self._build(fixture_repo)
        assert codes(result.errors) == ["LQC-K001"]
        assert "`cowork` block is missing" in result.errors[0].message

    def test_k001_duplicate_known_issue_id(self, fixture_repo):
        path = fixture_repo / "skills/beta/skill.yaml"
        path.write_text(
            path.read_text().replace(
                "  status: shipped\n",
                "  status: shipped\n"
                "  known_issues:\n"
                "    - id: KI-alpha-1\n"
                '      title: "Borrowed id"\n'
                '      detail: "Also declared by alpha."\n'
                "      failure: loud\n",
            ),
            encoding="utf-8",
        )
        result = self._build(fixture_repo)
        assert codes(result.errors) == ["LQC-K001", "LQC-K001"]
        assert all("KI-alpha-1" in i.message for i in result.errors)

    def test_k002_tier_four_cannot_ship(self, fixture_repo):
        path = fixture_repo / "skills/gamma/skill.yaml"
        path.write_text(path.read_text().replace("tier: 1", "tier: 4"), "utf-8")
        result = Builder(load_config(fixture_repo)).build_skill_only(["gamma"])
        assert "LQC-K002" in codes(result.errors)

    def test_k002_tier_two_needs_a_known_issue(self, fixture_repo):
        path = fixture_repo / "skills/gamma/skill.yaml"
        path.write_text(path.read_text().replace("tier: 1", "tier: 2"), "utf-8")
        result = Builder(load_config(fixture_repo)).build_skill_only(["gamma"])
        assert "LQC-K002" in codes(result.errors)
        assert "no known issue" in result.errors[0].message

    def test_k002_probe_gated_needs_a_probe(self, fixture_repo):
        path = fixture_repo / "skills/alpha/skill.yaml"
        path.write_text(path.read_text().replace("      probe: P3\n", ""), "utf-8")
        result = self._build(fixture_repo)
        assert "LQC-K002" in codes(result.errors)
        assert "probe-gated" in result.errors[0].message

    def test_k003_warns_on_an_undefined_probe(self, fixture_repo):
        path = fixture_repo / "skills/alpha/skill.yaml"
        path.write_text(path.read_text().replace("probe: P3", "probe: P99"), "utf-8")
        result = self._build(fixture_repo)
        assert result.errors == []
        assert codes(result.warnings) == ["LQC-K003"]
        assert "P99" in result.warnings[0].message

    def test_a_clean_tree_has_no_card_issues(self, fixture_repo):
        result = self._build(fixture_repo)
        assert result.errors == []
        assert result.warnings == []


class TestSkillOnlyBuild:
    def test_writes_skills_only_and_skips_the_manifest(self, fixture_repo):
        config = load_config(fixture_repo)
        result = Builder(config).build_skill_only(["alpha"])
        root = fixture_repo / "dist" / "skills-only"
        assert (root / "alpha" / "SKILL.md").is_file()
        assert not (fixture_repo / "dist" / "test-bundle").exists()
        assert not (root / "manifest.json").exists()
        assert [s.name for s in result.bundles[0].skills] == ["alpha"]

    def test_every_card_transform_still_runs(self, fixture_repo):
        Builder(load_config(fixture_repo)).build_skill_only(["alpha"])
        text = (fixture_repo / "dist/skills-only/alpha/SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "Open the alpha folder" in text  # the card's replace rule
        assert "## Automation is not available here" in text  # the section overlay
        assert "## Finish well" not in text  # the section deletion
        assert "Modified from LegalQuants/lq-plugin-oss@" in text

    def test_repeatable(self, fixture_repo):
        result = Builder(load_config(fixture_repo)).build_skill_only(["alpha", "beta"])
        assert [s.name for s in result.bundles[0].skills] == ["alpha", "beta"]
        assert (fixture_repo / "dist/skills-only/beta/SKILL.md").is_file()

    def test_a_skill_without_a_card_is_a_usage_error(self, fixture_repo):
        from lqcowork.config import ConfigError

        with pytest.raises(ConfigError, match="no adaptation card for: nope"):
            Builder(load_config(fixture_repo)).build_skill_only(["nope"])

    def test_cli_runs_the_per_skill_checks(self, fixture_repo, monkeypatch, capsys):
        from lqcowork.cli import main

        monkeypatch.chdir(fixture_repo)
        assert main(["build", "--skill", "alpha"]) == 0
        out = capsys.readouterr().out
        assert "alpha: 4 files" in out
        assert "dist/skills-only/alpha" in out

    def test_cli_refuses_skill_with_bundle(self, fixture_repo, monkeypatch):
        from lqcowork.cli import main

        monkeypatch.chdir(fixture_repo)
        assert main(["build", "--skill", "alpha", "--bundle", "test-bundle"]) == 1
