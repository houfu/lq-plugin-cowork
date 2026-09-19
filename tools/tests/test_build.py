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

    def test_metadata_version_is_the_package_version_as_a_string(
        self, fixture_repo, built
    ):
        config, _, _ = built
        fm = transforms.parse_document(read_skill(fixture_repo, "alpha")).frontmatter
        version = fm["metadata"]["version"]
        assert isinstance(version, str)
        assert version == config.version == "0.1.0"

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
