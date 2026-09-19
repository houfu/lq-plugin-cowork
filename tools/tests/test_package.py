"""Zip assembly, the trigger-test checklist and the build report."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from lqcowork import package as pkg
from lqcowork.build import Builder
from lqcowork.cli import main
from lqcowork.config import load_cards, load_config


@pytest.fixture
def packaged(fixture_repo: Path, monkeypatch):
    monkeypatch.chdir(fixture_repo)
    assert main(["package"]) == 0
    return fixture_repo


class TestZip:
    def test_entries_are_at_the_root_and_sorted(self, packaged):
        with zipfile.ZipFile(packaged / "dist/test-bundle.zip") as archive:
            names = archive.namelist()
        assert names == sorted(names)
        assert "manifest.json" in names
        assert "color.png" in names
        assert "outline.png" in names
        assert "LICENSE" in names
        assert "NOTICE.md" in names
        assert "skills/alpha/SKILL.md" in names
        assert all("\\" not in name for name in names)
        assert not any(name.startswith("__MACOSX") for name in names)
        assert not any(
            part.startswith(".") for name in names for part in name.split("/")
        )

    def test_two_builds_produce_byte_identical_zips(self, fixture_repo, tmp_path):
        config = load_config(fixture_repo)
        archives = []
        for run in ("first", "second"):
            out = tmp_path / run
            Builder(config, out_dir=out).build()
            archives.append(pkg.write_zip(config, config.bundles[0], out).read_bytes())
        assert archives[0] == archives[1]

    def test_source_date_epoch_is_honoured(self, fixture_repo, tmp_path, monkeypatch):
        monkeypatch.setenv("SOURCE_DATE_EPOCH", "1234567890")
        config = load_config(fixture_repo)
        out = tmp_path / "dated"
        Builder(config, out_dir=out).build()
        archive = pkg.write_zip(config, config.bundles[0], out)
        with zipfile.ZipFile(archive) as zf:
            assert zf.infolist()[0].date_time == (2009, 2, 13, 23, 31, 30)

    def test_entries_are_dated_1980_by_default(self, packaged):
        with zipfile.ZipFile(packaged / "dist/test-bundle.zip") as archive:
            stamps = {info.date_time for info in archive.infolist()}
        assert stamps == {(1980, 1, 1, 0, 0, 0)}

    def test_notice_is_copied_verbatim(self, packaged):
        with zipfile.ZipFile(packaged / "dist/test-bundle.zip") as archive:
            shipped = archive.read("NOTICE.md").decode()
        assert shipped == (packaged / "NOTICE.md").read_text()


class TestTriggerTests:
    def test_table_shape(self, packaged):
        text = (packaged / "dist/test-bundle-trigger-tests.md").read_text()
        assert "| Prompt | Expected | Result |" in text
        assert "| Do the alpha pass on this folder. | activate `alpha` |  |" in text
        assert (
            "| Do the beta thing instead. | must not activate; expect `beta` |  |"
            in text
        )
        assert "## alpha" in text and "## beta" in text

    def test_out_of_bundle_target_expects_nothing(self, packaged):
        text = (packaged / "dist/test-bundle-trigger-tests.md").read_text()
        assert (
            "| Do the gamma thing. | must not activate; expect none "
            "(gamma is not in this bundle) |  |" in text
        )

    def test_builtin_target_is_named_as_a_builtin(self, packaged):
        text = (packaged / "dist/test-bundle-trigger-tests.md").read_text()
        assert (
            "| Turn this into a Word document. | must not activate; expect "
            "built-in Word |  |" in text
        )

    def test_none_target_is_unchanged(self, packaged):
        text = (packaged / "dist/test-bundle-trigger-tests.md").read_text()
        assert (
            "| Summarise this email thread. | must not activate; expect `none` |  |"
            in text
        )

    def test_builtin_match_is_case_insensitive(self, fixture_repo):
        from lqcowork.package import expected_handoff

        bundle = load_config(fixture_repo).bundles[0]
        assert expected_handoff(bundle, "word") == (
            "must not activate; expect built-in Word"
        )
        assert expected_handoff(bundle, "deep research") == (
            "must not activate; expect built-in Deep Research"
        )

    def test_unknown_target_is_a_config_error(self, fixture_repo, monkeypatch):
        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(card.read_text().replace("-> beta", "-> nosuchskill"))
        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 1

    def test_unknown_target_error_names_the_card(self, fixture_repo):
        from lqcowork.config import ConfigError, load_cards

        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(card.read_text().replace("-> beta", "-> nosuchskill"))
        config = load_config(fixture_repo)
        with pytest.raises(ConfigError, match="skills/alpha/skill.yaml"):
            load_cards(config, ["alpha", "beta"])

    def test_a_card_outside_the_bundles_is_a_valid_target(self, fixture_repo):
        from lqcowork.config import load_cards

        # gamma has a card but ships in no bundle; alpha may still name it
        load_cards(load_config(fixture_repo), ["alpha", "beta"])

    def test_triggers_command_writes_the_same_file(self, fixture_repo, monkeypatch):
        monkeypatch.chdir(fixture_repo)
        assert main(["triggers"]) == 0
        assert (fixture_repo / "dist/test-bundle-trigger-tests.md").is_file()


class TestBuildReport:
    def test_contents(self, packaged):
        text = (packaged / "dist/build-report.md").read_text()
        assert "# Build report" in text
        assert "## test-bundle" in text
        assert "| Skill | Bucket | Files | Bytes | Warnings |" in text
        assert "| alpha | amber |" in text
        assert "### Adaptation notes" in text
        assert "| Code | Bundle | Skill | Where | Detail |" in text
        assert "Dropped scripts/" in text
        assert "LQC-W004" in text  # the deliberate '../' reference

    def test_lists_companions_changed_without_a_notice(self, fixture_repo, monkeypatch):
        assets = fixture_repo / "skills/alpha/files/assets"
        assets.mkdir(parents=True, exist_ok=True)
        (assets / "template.html").write_text("<p>ours</p>\n")
        monkeypatch.chdir(fixture_repo)
        assert main(["package"]) == 0
        text = (fixture_repo / "dist/build-report.md").read_text()
        assert "### Companions changed without an in-file notice" in text
        assert "| alpha | assets/template.html |" in text

    def test_suppressed_warnings_are_listed(self, fixture_repo, monkeypatch):
        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(
            card.read_text()
            + "\nsuppress:\n"
            + "  - code: LQC-W010\n"
            + '    file: "references/extra.md"\n'
            + '    reason: "upstream-authored authority URL"\n',
            encoding="utf-8",
        )
        monkeypatch.chdir(fixture_repo)
        assert main(["package"]) == 0
        text = (fixture_repo / "dist/build-report.md").read_text()
        assert "## Suppressed warnings" in text
        assert "| Bundle | Skill | Code | File | Reason |" in text
        assert "| test-bundle | alpha | LQC-W010 | references/extra.md |" in text
        assert "upstream-authored authority URL" in text

    def test_no_suppressions_says_so(self, packaged):
        text = (packaged / "dist/build-report.md").read_text()
        assert "## Suppressed warnings: none." in text

    def test_no_such_section_when_every_companion_is_markdown(self, packaged):
        text = (packaged / "dist/build-report.md").read_text()
        assert "### Companions changed without an in-file notice" not in text


class TestExitCodes:
    def test_validate_returns_two_on_error(self, packaged, monkeypatch):
        (packaged / "dist/test-bundle/color.png").unlink()
        monkeypatch.chdir(packaged)
        assert main(["validate"]) == 2

    def test_build_returns_one_on_config_error(self, fixture_repo, monkeypatch):
        (fixture_repo / "skills/beta/skill.yaml").unlink()
        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 1

    def test_bundle_filter(self, fixture_repo, monkeypatch):
        monkeypatch.chdir(fixture_repo)
        assert main(["build", "--bundle", "test-bundle"]) == 0
        assert main(["build", "--bundle", "nope"]) == 1

    def test_build_validates_too(self, fixture_repo, monkeypatch):
        from conftest import write_png

        write_png(fixture_repo / "branding/color.png", 64, 64, (0, 0, 0))
        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 2  # LQC-I001

    def test_build_returns_two_on_anchor_failure(self, fixture_repo, monkeypatch):
        card = fixture_repo / "skills/alpha/skill.yaml"
        card.write_text(card.read_text().replace("expect: 1", "expect: 4"))
        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 2  # LQC-A001
        assert main(["build", "--report-anchors"]) == 2

    def test_runs_from_a_subdirectory(self, fixture_repo, monkeypatch):
        monkeypatch.chdir(fixture_repo / "skills" / "alpha")
        assert main(["package"]) == 0
        assert (fixture_repo / "dist/test-bundle.zip").is_file()


class TestSharedSkills:
    def test_a_skill_in_two_bundles_is_built_once_and_copied(self, fixture_repo):
        path = fixture_repo / "cowork.yaml"
        text = path.read_text()
        second = (
            text.split("bundles:\n")[1]
            .replace("id: test-bundle", "id: other-bundle")
            .replace(
                "guid: 5d40f9d0-bbfe-5aa7-a4e9-10b4e0b676bf",
                "guid: f53d5df8-3b69-55e8-a12b-fdf244f3df55",
            )
        )
        path.write_text(text + second, encoding="utf-8")
        config = load_config(fixture_repo)
        result = Builder(config).build()
        assert len(result.bundles) == 2
        first = (fixture_repo / "dist/test-bundle/skills/alpha/SKILL.md").read_text()
        again = (fixture_repo / "dist/other-bundle/skills/alpha/SKILL.md").read_text()
        assert first == again
        # the shared record is the same object in both bundles
        assert result.bundles[0].skills[0] is result.bundles[1].skills[0]


class TestSummary:
    def test_one_line_per_bundle(self, fixture_repo):
        config = load_config(fixture_repo)
        result = Builder(config).build()
        line = pkg.summarise(result.bundles[0])
        assert line.startswith("test-bundle: 2 skills,")
        load_cards(config, ["alpha", "beta"])


def second_bundle(root: Path) -> None:
    """Give the fixture a second bundle that shares both skills."""
    path = root / "cowork.yaml"
    text = path.read_text()
    extra = (
        text.split("bundles:\n")[1]
        .replace("id: test-bundle", "id: other-bundle")
        .replace(
            "guid: 5d40f9d0-bbfe-5aa7-a4e9-10b4e0b676bf",
            "guid: f53d5df8-3b69-55e8-a12b-fdf244f3df55",
        )
    )
    path.write_text(text + extra, encoding="utf-8")


class TestSkillArchives:
    def test_one_archive_per_distinct_skill(self, packaged):
        names = sorted(p.name for p in (packaged / "dist/skills").iterdir())
        assert names == ["alpha.skill", "beta.skill"]

    def test_a_shared_skill_is_archived_once(self, fixture_repo, monkeypatch):
        second_bundle(fixture_repo)
        monkeypatch.chdir(fixture_repo)
        assert main(["package"]) == 0
        names = sorted(p.name for p in (fixture_repo / "dist/skills").iterdir())
        assert names == ["alpha.skill", "beta.skill"]

    def test_entries_are_sorted_at_the_root_and_carry_the_notices(self, packaged):
        with zipfile.ZipFile(packaged / "dist/skills/alpha.skill") as archive:
            names = archive.namelist()
        assert names == sorted(names)
        assert "SKILL.md" in names
        assert "LICENSE" in names
        assert "NOTICE.md" in names
        assert "references/notes.md" in names
        assert not any(name.startswith("skills/") for name in names)
        assert not any(name.startswith("alpha/") for name in names)

    def test_skill_md_is_the_built_one_byte_for_byte(self, packaged):
        built = packaged / "dist/test-bundle/skills/alpha/SKILL.md"
        with zipfile.ZipFile(packaged / "dist/skills/alpha.skill") as archive:
            assert archive.read("SKILL.md") == built.read_bytes()

    def test_licence_and_notice_come_from_the_repository_root(self, packaged):
        with zipfile.ZipFile(packaged / "dist/skills/alpha.skill") as archive:
            assert (
                archive.read("LICENSE") == (packaged / "upstream/LICENSE").read_bytes()
            )
            assert archive.read("NOTICE.md") == (packaged / "NOTICE.md").read_bytes()

    def test_a_skill_with_no_companions_still_ships(self, packaged):
        with zipfile.ZipFile(packaged / "dist/skills/beta.skill") as archive:
            assert archive.namelist() == ["LICENSE", "NOTICE.md", "SKILL.md"]

    def test_two_builds_produce_byte_identical_archives(self, fixture_repo, tmp_path):
        config = load_config(fixture_repo)
        runs = []
        for run in ("first", "second"):
            out = tmp_path / run
            Builder(config, out_dir=out).build()
            written = pkg.write_skill_archives(config, list(config.bundles), out)
            runs.append([path.read_bytes() for path in written])
        assert runs[0] == runs[1]

    def test_entries_are_dated_1980_by_default(self, packaged):
        with zipfile.ZipFile(packaged / "dist/skills/alpha.skill") as archive:
            stamps = {info.date_time for info in archive.infolist()}
        assert stamps == {(1980, 1, 1, 0, 0, 0)}

    def test_source_date_epoch_is_honoured(self, fixture_repo, tmp_path, monkeypatch):
        monkeypatch.setenv("SOURCE_DATE_EPOCH", "1234567890")
        config = load_config(fixture_repo)
        out = tmp_path / "dated"
        Builder(config, out_dir=out).build()
        written = pkg.write_skill_archives(config, list(config.bundles), out)
        with zipfile.ZipFile(written[0]) as archive:
            assert archive.infolist()[0].date_time == (2009, 2, 13, 23, 31, 30)

    def test_package_prints_the_archive_summary(
        self, fixture_repo, monkeypatch, capsys
    ):
        monkeypatch.chdir(fixture_repo)
        assert main(["package"]) == 0
        out = capsys.readouterr().out
        assert "dist/skills/: 2 archives" in out
        assert "  dist/skills/alpha.skill" in out

    def test_package_exits_two_when_an_archive_is_invalid(
        self, fixture_repo, monkeypatch
    ):
        from lqcowork import validate as V

        monkeypatch.setattr(V, "MAX_ARCHIVE_COMPANIONS", 0)
        monkeypatch.chdir(fixture_repo)
        assert main(["package"]) == 2


class TestArchivesCommand:
    def test_writes_from_an_existing_build(self, fixture_repo, monkeypatch):
        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 0
        assert not (fixture_repo / "dist/skills").exists()
        assert main(["archives"]) == 0
        assert (fixture_repo / "dist/skills/alpha.skill").is_file()

    def test_bundle_filter(self, fixture_repo, monkeypatch):
        second_bundle(fixture_repo)
        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 0
        assert main(["archives", "--bundle", "other-bundle"]) == 0
        assert (fixture_repo / "dist/skills/alpha.skill").is_file()

    def test_without_a_build_it_says_to_build_first(
        self, fixture_repo, monkeypatch, capsys
    ):
        monkeypatch.chdir(fixture_repo)
        assert main(["archives"]) == 1
        assert "run build first" in capsys.readouterr().err

    def test_out_dir_is_honoured(self, fixture_repo, tmp_path, monkeypatch):
        monkeypatch.chdir(fixture_repo)
        out = tmp_path / "elsewhere"
        assert main(["build", "--out", str(out)]) == 0
        assert main(["archives", "--out", str(out)]) == 0
        assert (out / "skills/alpha.skill").is_file()

    def test_returns_two_when_an_archive_is_invalid(self, fixture_repo, monkeypatch):
        from lqcowork import validate as V

        monkeypatch.chdir(fixture_repo)
        assert main(["build"]) == 0
        monkeypatch.setattr(V, "MAX_ARCHIVE_ENTRIES", 1)
        assert main(["archives"]) == 2


class TestArchiveReport:
    def test_section_lists_every_archive(self, packaged):
        text = (packaged / "dist/build-report.md").read_text()
        assert "## Single-skill archives" in text
        assert "| Archive | Entries | Compressed | Uncompressed | Bundles |" in text
        assert "| `skills/alpha.skill` |" in text
        assert "| `skills/beta.skill` |" in text

    def test_a_shared_skill_names_both_bundles(self, fixture_repo, monkeypatch):
        second_bundle(fixture_repo)
        monkeypatch.chdir(fixture_repo)
        assert main(["package"]) == 0
        text = (fixture_repo / "dist/build-report.md").read_text()
        assert "| test-bundle, other-bundle |" in text


class TestStrayReadme:
    def test_a_readme_in_skills_changes_nothing(self, fixture_repo, monkeypatch):
        monkeypatch.chdir(fixture_repo)
        assert main(["package"]) == 0
        before = {
            path.relative_to(fixture_repo).as_posix(): path.read_bytes()
            for path in sorted((fixture_repo / "dist").rglob("*"))
            if path.is_file()
        }
        (fixture_repo / "skills/README.md").write_text(
            "These folders are build inputs, not skills.\n", encoding="utf-8"
        )
        assert main(["package"]) == 0
        after = {
            path.relative_to(fixture_repo).as_posix(): path.read_bytes()
            for path in sorted((fixture_repo / "dist").rglob("*"))
            if path.is_file()
        }
        assert after == before
