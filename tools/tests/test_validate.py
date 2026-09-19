"""Every validation code we can provoke, against a built fixture bundle."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from lqcowork import validate as V
from lqcowork.build import Builder
from lqcowork.config import load_cards, load_config, upstream_skill_names


@pytest.fixture
def built_repo(fixture_repo: Path) -> Path:
    Builder(load_config(fixture_repo)).build()
    return fixture_repo


def run(root: Path) -> tuple[list[str], list[str]]:
    config = load_config(root)
    bundle = config.bundles[0]
    cards = load_cards(config, list(bundle.skills))
    errors, warnings = V.validate_bundle(
        config, bundle, cards=cards, skill_names=upstream_skill_names(config)
    )
    return [i.code for i in errors], [i.code for i in warnings]


def skill_md(root: Path, name: str = "alpha") -> Path:
    return root / "dist/test-bundle/skills" / name / "SKILL.md"


def edit_manifest(root: Path, **changes) -> None:
    path = root / "dist/test-bundle/manifest.json"
    data = json.loads(path.read_text())
    data.update(changes)
    path.write_text(json.dumps(data, indent=2) + "\n")


class TestCleanBuild:
    def test_no_errors(self, built_repo):
        errors, _ = run(built_repo)
        assert errors == []

    def test_only_the_expected_warnings(self, built_repo):
        _, warnings = run(built_repo)
        # alpha keeps an upstream '../beta/SKILL.md' reference on purpose, and
        # references/notes.md is modified so its URL is not exempt
        assert sorted(set(warnings)) == ["LQC-W004", "LQC-W010"]


class TestManifestErrors:
    def test_m001_unexpected_key(self, built_repo):
        edit_manifest(built_repo, surprise=1)
        assert "LQC-M001" in run(built_repo)[0]

    def test_m002_manifest_version(self, built_repo):
        edit_manifest(built_repo, manifestVersion="1.27")
        assert "LQC-M002" in run(built_repo)[0]

    def test_m002_schema_url(self, built_repo):
        edit_manifest(built_repo, **{"$schema": "https://example.invalid/x.json"})
        assert "LQC-M002" in run(built_repo)[0]

    def test_m002_version_and_id(self, built_repo):
        edit_manifest(built_repo, version="1.0", id="not-a-uuid")
        assert run(built_repo)[0].count("LQC-M002") == 2

    def test_m003_lengths(self, built_repo):
        edit_manifest(built_repo, name={"short": "x" * 31, "full": "ok"})
        assert "LQC-M003" in run(built_repo)[0]

    def test_m004_developer(self, built_repo):
        edit_manifest(
            built_repo,
            developer={
                "name": "X",
                "websiteUrl": "http://insecure.invalid",
                "privacyUrl": "https://a.invalid",
                "termsOfUseUrl": "https://b.invalid",
            },
        )
        assert "LQC-M004" in run(built_repo)[0]

    def test_m005_accent_colour(self, built_repo):
        edit_manifest(built_repo, accentColor="2D2D2D")
        assert "LQC-M005" in run(built_repo)[0]

    def test_askill_m001_missing_folder(self, built_repo):
        edit_manifest(built_repo, agentSkills=[{"folder": "./skills/alpha"}, {}])
        assert "ASKILL-M001" in run(built_repo)[0]

    def test_askill_m002_too_many(self, built_repo):
        edit_manifest(
            built_repo, agentSkills=[{"folder": f"./skills/s{i}"} for i in range(21)]
        )
        assert "ASKILL-M002" in run(built_repo)[0]

    def test_askill_m003_long_folder(self, built_repo):
        edit_manifest(built_repo, agentSkills=[{"folder": "./skills/" + "x" * 300}])
        assert "ASKILL-M003" in run(built_repo)[0]

    def test_askill_p001_missing_folder_in_package(self, built_repo):
        edit_manifest(built_repo, agentSkills=[{"folder": "./skills/nope"}])
        assert "ASKILL-P001" in run(built_repo)[0]

    def test_askill_p002_folder_without_skill_md(self, built_repo):
        (built_repo / "dist/test-bundle/skills/empty").mkdir()
        edit_manifest(built_repo, agentSkills=[{"folder": "./skills/empty"}])
        assert "ASKILL-P002" in run(built_repo)[0]

    def test_askill_p008_duplicate_folder(self, built_repo):
        edit_manifest(
            built_repo,
            agentSkills=[{"folder": "./skills/alpha"}, {"folder": "./skills/alpha"}],
        )
        assert "ASKILL-P008" in run(built_repo)[0]


class TestSkillErrors:
    def test_p003_broken_frontmatter(self, built_repo):
        skill_md(built_repo).write_text("# no frontmatter\n")
        assert "ASKILL-P003" in run(built_repo)[0]

    def test_p004_and_p005_missing_keys(self, built_repo):
        skill_md(built_repo).write_text("---\nlicense: Apache-2.0\n---\n\nbody\n")
        errors = run(built_repo)[0]
        assert "ASKILL-P004" in errors
        assert "ASKILL-P005" in errors

    def test_p006_name_mismatch(self, built_repo):
        path = skill_md(built_repo)
        path.write_text(path.read_text().replace("name: alpha", "name: other"))
        assert "ASKILL-P006" in run(built_repo)[0]

    def test_p007_not_kebab_case(self, built_repo):
        path = skill_md(built_repo)
        path.write_text(path.read_text().replace("name: alpha", "name: Alpha_One"))
        assert "ASKILL-P007" in run(built_repo)[0]

    def test_d001_description_too_long(self, built_repo):
        path = skill_md(built_repo)
        body = path.read_text().split("\n---\n", 1)[1]
        path.write_text(
            "---\nname: alpha\ndescription: " + "x" * 1100 + "\n---\n" + body
        )
        assert "LQC-D001" in run(built_repo)[0]

    def test_c001_too_many_companions(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_COMPANIONS", 1)
        assert "LQC-C001" in run(built_repo)[0]

    def test_c002_companion_too_large(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_COMPANION_BYTES", 4)
        assert "LQC-C002" in run(built_repo)[0]

    def test_c003_companions_too_large_in_total(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_SKILL_COMPANION_BYTES", 4)
        assert "LQC-C003" in run(built_repo)[0]

    def test_c004_hidden_file(self, built_repo):
        (built_repo / "dist/test-bundle/skills/alpha/.secret").write_text("x")
        assert "LQC-C004" in run(built_repo)[0]

    @pytest.mark.parametrize("filename", ["CON.md", "con.txt", "COM1", "lpt9.md"])
    def test_c005_reserved_name(self, built_repo, filename):
        (built_repo / "dist/test-bundle/skills/alpha" / filename).write_text("x")
        assert "LQC-C005" in run(built_repo)[0]

    def test_c005_leaves_ordinary_names_alone(self, built_repo):
        (built_repo / "dist/test-bundle/skills/alpha/console.md").write_text("x")
        assert "LQC-C005" not in run(built_repo)[0]

    def test_c006_illegal_characters(self, built_repo):
        (built_repo / "dist/test-bundle/skills/alpha/bad#name.md").write_text("x")
        assert "LQC-C006" in run(built_repo)[0]

    def test_s001_skill_md_too_large(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_SKILL_MD_BYTES", 10)
        assert "LQC-S001" in run(built_repo)[0]


class TestIcons:
    def test_i001_wrong_size(self, built_repo):
        from conftest import write_png

        write_png(built_repo / "dist/test-bundle/color.png", 64, 64, (0, 0, 0))
        assert "LQC-I001" in run(built_repo)[0]

    def test_i001_not_a_png(self, built_repo):
        (built_repo / "dist/test-bundle/outline.png").write_bytes(b"nope")
        assert "LQC-I001" in run(built_repo)[0]

    def test_i001_missing(self, built_repo):
        (built_repo / "dist/test-bundle/color.png").unlink()
        assert "LQC-I001" in run(built_repo)[0]


class TestWarnings:
    def _append(self, root: Path, text: str, name: str = "alpha") -> None:
        path = skill_md(root, name)
        path.write_text(path.read_text() + text)

    def test_w001_vendor_word(self, built_repo):
        self._append(built_repo, "\nRun it in Codex.\n")
        assert "LQC-W001" in run(built_repo)[1]

    def test_w001_ignores_substrings(self, built_repo):
        self._append(built_repo, "\nCodexicals are not vendors.\n")
        assert "LQC-W001" not in run(built_repo)[1]

    def test_w002_surviving_token(self, built_repo):
        self._append(built_repo, "\nType $gamma to start.\n")
        assert "LQC-W002" in run(built_repo)[1]

    def test_w003_out_of_bundle_reference(self, built_repo):
        self._append(built_repo, "\nHand off to the gamma skill.\n")
        assert "LQC-W003" in run(built_repo)[1]

    def test_w005_missing_scripts_folder(self, built_repo):
        self._append(built_repo, "\nRun scripts/alpha.py yourself.\n")
        assert "LQC-W005" in run(built_repo)[1]

    def test_w006_long_body(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_BODY_WORDS", 5)
        assert "LQC-W006" in run(built_repo)[1]

    def test_w007_host_specific_terms(self, built_repo):
        self._append(built_repo, "\nThe store lives in ~/.lq/ and uses hooks.\n")
        assert "LQC-W007" in run(built_repo)[1]

    def test_w008_amber_without_notes(self, built_repo):
        card = built_repo / "skills/alpha/skill.yaml"
        card.write_text(
            card.read_text().replace(
                "notes: |\n  Dropped scripts/; the chat path in the body is the"
                " documented fallback.\n",
                "",
            )
        )
        assert "LQC-W008" in run(built_repo)[1]


class TestWarningScope:
    """Contract section 6: W004/W005/W007/W009/W010 over every *.md, file:line."""

    def companion(self, root: Path) -> Path:
        return root / "dist/test-bundle/skills/alpha/references/extra.md"

    def warnings_at(self, root: Path) -> list:
        config = load_config(root)
        bundle = config.bundles[0]
        cards = load_cards(config, list(bundle.skills))
        _, warnings = V.validate_bundle(
            config, bundle, cards=cards, skill_names=upstream_skill_names(config)
        )
        return warnings

    def codes_at(self, root: Path, code: str) -> list[str]:
        config = load_config(root)
        bundle = config.bundles[0]
        cards = load_cards(config, list(bundle.skills))
        _, warnings = V.validate_bundle(
            config, bundle, cards=cards, skill_names=upstream_skill_names(config)
        )
        return [w.location or "" for w in warnings if w.code == code]

    def test_w005_fires_in_a_companion(self, built_repo):
        path = self.companion(built_repo)
        path.write_text(path.read_text() + "\nRun scripts/alpha.py yourself.\n")
        assert any(
            loc.startswith("references/extra.md:")
            for loc in self.codes_at(built_repo, "LQC-W005")
        )

    @pytest.mark.parametrize(
        "line",
        [
            "Run scripts/alpha.py yourself.",
            "Everything lives in scripts/ now.",
            "See `scripts/alpha.py` for the detail.",
            "(scripts/alpha.py) is the entry point.",
            "schemas/unit.json holds the contract.",
        ],
    )
    def test_w005_fires_on_a_real_path_segment(self, built_repo, line):
        path = self.companion(built_repo)
        path.write_text(path.read_text() + "\n" + line + "\n")
        assert self.codes_at(built_repo, "LQC-W005") != []

    @pytest.mark.parametrize(
        "line",
        [
            "Access to files and transcripts/online-files is restricted.",
            "The postscripts/ folder is someone else's.",
            "Our my-scripts/ directory is unrelated.",
            "See my_schemas/thing.json elsewhere.",
        ],
    )
    def test_w005_ignores_a_word_that_merely_ends_in_it(self, built_repo, line):
        path = self.companion(built_repo)
        path.write_text(path.read_text() + "\n" + line + "\n")
        assert self.codes_at(built_repo, "LQC-W005") == []

    def test_w007_fires_in_a_companion(self, built_repo):
        path = self.companion(built_repo)
        path.write_text(path.read_text() + "\nIt needs lifecycle hooks.\n")
        assert any(
            loc.startswith("references/extra.md:")
            for loc in self.codes_at(built_repo, "LQC-W007")
        )

    def test_warnings_carry_file_and_line(self, built_repo):
        path = self.companion(built_repo)
        original = path.read_text()
        path.write_text(original + "\nThe scribe owns it.\n")
        line = len(original.split("\n")) + 1
        assert f"references/extra.md:{line}" in self.codes_at(built_repo, "LQC-W009")

    def test_w009_is_case_insensitive_and_phrase_based(self, built_repo):
        path = self.companion(built_repo)
        path.write_text(path.read_text() + "\nCheck the EXIT CODE, then --dry-run.\n")
        assert len(self.codes_at(built_repo, "LQC-W009")) == 2

    def test_w009_silent_when_no_phrase_matches(self, built_repo):
        assert self.codes_at(built_repo, "LQC-W009") == []

    def test_w004_flags_a_dead_relative_link(self, built_repo):
        path = skill_md(built_repo)
        path.write_text(
            path.read_text() + "\nSee [the gone file](references/gone.md).\n"
        )
        assert any(
            loc.startswith("SKILL.md:") for loc in self.codes_at(built_repo, "LQC-W004")
        )

    def test_w004_accepts_a_live_relative_link(self, built_repo):
        path = skill_md(built_repo)
        before = len(self.codes_at(built_repo, "LQC-W004"))
        path.write_text(path.read_text() + "\nSee [the notes](references/notes.md).\n")
        assert len(self.codes_at(built_repo, "LQC-W004")) == before

    def test_w004_ignores_http_mailto_and_anchors(self, built_repo):
        path = skill_md(built_repo)
        before = len(self.codes_at(built_repo, "LQC-W004"))
        path.write_text(
            path.read_text()
            + "\n[a](https://example.invalid/x) [b](mailto:x@example.invalid) [c](#top)\n"
        )
        assert len(self.codes_at(built_repo, "LQC-W004")) == before

    def test_w004_resolves_links_relative_to_the_file(self, built_repo):
        path = self.companion(built_repo)
        before = len(self.codes_at(built_repo, "LQC-W004"))
        path.write_text(path.read_text() + "\nSee [notes](notes.md).\n")
        assert len(self.codes_at(built_repo, "LQC-W004")) == before

    def test_w010_exempts_an_upstream_authored_url(self, built_repo):
        shipped = built_repo / "dist/test-bundle/skills/alpha/references/beta.md"
        assert "https://example.invalid/authority" in shipped.read_text()
        locations = self.codes_at(built_repo, "LQC-W010")
        assert not any(loc.startswith("references/beta.md:") for loc in locations)

    def test_w010_exempts_a_url_moved_out_of_an_upstream_file(self, built_repo):
        # extra.md is ours, but this URL is upstream's, moved here
        extra = built_repo / "dist/test-bundle/skills/alpha/references/extra.md"
        assert "https://example.invalid/marketing" in extra.read_text()
        assert not any(
            "marketing" in w.message
            for w in self.warnings_at(built_repo)
            if w.code == "LQC-W010"
        )

    def test_w010_fires_on_a_url_the_adaptation_introduced(self, built_repo):
        introduced = [
            w
            for w in self.warnings_at(built_repo)
            if w.code == "LQC-W010" and "introduced" in w.message
        ]
        assert introduced
        assert introduced[0].location.startswith("references/extra.md:")

    def test_w010_exemption_is_per_url_not_per_file(self, built_repo):
        # the same file carries one exempt URL and one that warns
        locations = self.codes_at(built_repo, "LQC-W010")
        assert [loc for loc in locations if loc.startswith("references/extra.md:")]
        assert not any(loc.startswith("references/notes.md:") for loc in locations)

    def test_w010_allows_the_upstream_repository_url(self, built_repo):
        path = skill_md(built_repo)
        before = len(self.codes_at(built_repo, "LQC-W010"))
        path.write_text(
            path.read_text()
            + "\nSee https://github.com/LegalQuants/lq-plugin-oss for the source.\n"
        )
        assert len(self.codes_at(built_repo, "LQC-W010")) == before

    def test_w003_does_not_fire_on_plain_english(self, built_repo):
        path = skill_md(built_repo)
        path.write_text(path.read_text() + "\nA gamma inquiry is not a hand-off.\n")
        assert self.codes_at(built_repo, "LQC-W003") == []

    def test_w003_fires_on_a_backticked_out_of_bundle_skill(self, built_repo):
        path = skill_md(built_repo)
        path.write_text(path.read_text() + "\nHand off to `gamma` instead.\n")
        assert self.codes_at(built_repo, "LQC-W003") != []


class TestSuppression:
    """Contract section 4: an auditable per-card warning suppression."""

    def suppress(self, root: Path, block: str) -> None:
        card = root / "skills/alpha/skill.yaml"
        card.write_text(card.read_text() + block, encoding="utf-8")

    def run_with_suppressions(self, root: Path):
        config = load_config(root)
        bundle = config.bundles[0]
        cards = load_cards(config, list(bundle.skills))
        collected: list = []
        _, warnings = V.validate_bundle(
            config,
            bundle,
            cards=cards,
            skill_names=upstream_skill_names(config),
            suppressed=collected,
        )
        return [w.code for w in warnings], collected

    def test_file_scoped_suppression_drops_only_that_file(self, built_repo):
        self.suppress(
            built_repo,
            "\nsuppress:\n"
            "  - code: LQC-W010\n"
            '    file: "references/extra.md"\n'
            '    reason: "upstream-authored authority URL"\n',
        )
        codes, collected = self.run_with_suppressions(built_repo)
        assert "LQC-W010" not in codes
        assert len(collected) == 1
        assert collected[0].reason == "upstream-authored authority URL"
        assert collected[0].issue.location.startswith("references/extra.md:")

    def test_glob_file_matches(self, built_repo):
        self.suppress(
            built_repo,
            "\nsuppress:\n"
            "  - code: LQC-W010\n"
            '    file: "references/*.md"\n'
            '    reason: "authority links live in references"\n',
        )
        codes, collected = self.run_with_suppressions(built_repo)
        assert "LQC-W010" not in codes
        assert collected

    def test_wrong_file_does_not_suppress(self, built_repo):
        self.suppress(
            built_repo,
            "\nsuppress:\n"
            "  - code: LQC-W010\n"
            '    file: "references/other.md"\n'
            '    reason: "not this one"\n',
        )
        codes, collected = self.run_with_suppressions(built_repo)
        assert "LQC-W010" in codes
        assert collected == []

    def test_suppression_without_a_file_covers_the_whole_skill(self, built_repo):
        self.suppress(
            built_repo,
            "\nsuppress:\n"
            "  - code: LQC-W004\n"
            '    reason: "upstream cross-reference kept on purpose"\n',
        )
        codes, _ = self.run_with_suppressions(built_repo)
        assert "LQC-W004" not in codes

    def test_suppression_does_not_leak_to_another_skill(self, built_repo):
        self.suppress(
            built_repo,
            "\nsuppress:\n" "  - code: LQC-W004\n" '    reason: "alpha only"\n',
        )
        path = skill_md(built_repo, "beta")
        path.write_text(path.read_text() + "\nSee ../elsewhere/SKILL.md.\n")
        codes, _ = self.run_with_suppressions(built_repo)
        assert "LQC-W004" in codes

    def test_an_error_code_cannot_be_suppressed(self, built_repo):
        from lqcowork.config import ConfigError

        self.suppress(
            built_repo,
            "\nsuppress:\n" "  - code: LQC-I001\n" '    reason: "nice try"\n',
        )
        with pytest.raises(ConfigError, match="not a warning code"):
            load_cards(load_config(built_repo), ["alpha"])

    def test_reason_is_required(self, built_repo):
        from lqcowork.config import ConfigError

        self.suppress(built_repo, "\nsuppress:\n  - code: LQC-W010\n")
        with pytest.raises(ConfigError, match="reason"):
            load_cards(load_config(built_repo), ["alpha"])


class TestZip:
    def _zip(self, tmp_path: Path, names: list[str]) -> Path:
        target = tmp_path / "bundle.zip"
        with zipfile.ZipFile(target, "w") as archive:
            for name in names:
                archive.writestr(name, "x")
        return target

    def test_clean_zip_passes(self, tmp_path):
        archive = self._zip(
            tmp_path, ["manifest.json", "color.png", "skills/alpha/SKILL.md"]
        )
        assert (
            V.validate_zip(archive, "b", {"manifest.json", "color.png", "skills"}) == []
        )

    def test_nested_root_is_rejected(self, tmp_path):
        archive = self._zip(tmp_path, ["bundle/manifest.json"])
        codes = [i.code for i in V.validate_zip(archive, "b", {"manifest.json"})]
        assert codes.count("LQC-Z001") == 2  # missing at root + unexpected root

    def test_macosx_and_dotfiles_rejected(self, tmp_path):
        archive = self._zip(tmp_path, ["manifest.json", "__MACOSX/x", ".DS_Store"])
        codes = [i.code for i in V.validate_zip(archive, "b", {"manifest.json"})]
        assert len(codes) >= 3


class TestSkillArchive:
    """LQC-U001..U005, one provoked at a time against a written archive."""

    def archive(self, root: Path, name: str = "alpha") -> Path:
        from lqcowork.package import write_skill_archives

        config = load_config(root)
        written = write_skill_archives(config, list(config.bundles))
        return next(path for path in written if path.stem == name)

    def skill_dir(self, root: Path, name: str = "alpha") -> Path:
        return root / "dist/test-bundle/skills" / name

    def check(self, root: Path, archive: Path, name: str = "alpha") -> list[str]:
        issues = V.validate_skill_archive(archive, name, self.skill_dir(root, name))
        return [issue.code for issue in issues]

    def rewrite(self, archive: Path, entries: dict[str, bytes]) -> Path:
        """Replace the archive's contents, the way a tamperer would."""
        with zipfile.ZipFile(archive, "w") as opened:
            for name, payload in entries.items():
                opened.writestr(name, payload)
        return archive

    def contents(self, archive: Path) -> dict[str, bytes]:
        with zipfile.ZipFile(archive) as opened:
            return {name: opened.read(name) for name in opened.namelist()}

    def test_a_written_archive_is_clean(self, built_repo):
        archive = self.archive(built_repo)
        assert self.check(built_repo, archive) == []
        assert self.check(built_repo, self.archive(built_repo, "beta"), "beta") == []

    def test_u001_nested_top_level_folder(self, built_repo):
        archive = self.archive(built_repo)
        entries = {f"alpha/{k}": v for k, v in self.contents(archive).items()}
        codes = self.check(built_repo, self.rewrite(archive, entries))
        assert codes.count("LQC-U001") == len(entries) + 1  # + no SKILL.md at root

    def test_u001_dotfile_entry(self, built_repo):
        archive = self.archive(built_repo)
        entries = self.contents(archive) | {".DS_Store": b"junk"}
        assert "LQC-U001" in self.check(built_repo, self.rewrite(archive, entries))

    def test_u001_macosx_entry(self, built_repo):
        archive = self.archive(built_repo)
        entries = self.contents(archive) | {"__MACOSX/alpha": b"junk"}
        assert "LQC-U001" in self.check(built_repo, self.rewrite(archive, entries))

    def test_u002_skill_md_must_match_the_built_one(self, built_repo):
        archive = self.archive(built_repo)
        entries = self.contents(archive) | {"SKILL.md": b"---\nname: alpha\n---\n"}
        codes = self.check(built_repo, self.rewrite(archive, entries))
        assert codes == ["LQC-U002"]

    def test_u002_licence_and_notice_must_travel(self, built_repo):
        archive = self.archive(built_repo)
        entries = {
            k: v
            for k, v in self.contents(archive).items()
            if k not in {"LICENSE", "NOTICE.md"}
        }
        codes = self.check(built_repo, self.rewrite(archive, entries))
        assert codes.count("LQC-U002") == 2

    def test_u003_entry_count(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_ARCHIVE_ENTRIES", 2)
        assert "LQC-U003" in self.check(built_repo, self.archive(built_repo))

    def test_u004_compressed_limit(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_ARCHIVE_COMPRESSED_BYTES", 10)
        assert "LQC-U004" in self.check(built_repo, self.archive(built_repo))

    def test_u004_uncompressed_limit(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_ARCHIVE_UNCOMPRESSED_BYTES", 10)
        assert "LQC-U004" in self.check(built_repo, self.archive(built_repo))

    def test_u004_markdown_limit(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_ARCHIVE_MD_BYTES", 10)
        codes = self.check(built_repo, self.archive(built_repo))
        assert codes.count("LQC-U004") >= 2  # SKILL.md and its companions

    def test_u005_companion_budget(self, built_repo, monkeypatch):
        monkeypatch.setattr(V, "MAX_ARCHIVE_COMPANIONS", 1)
        codes = self.check(built_repo, self.archive(built_repo))
        assert codes == ["LQC-U005"]

    def test_u005_nothing_the_bundle_folder_does_not_have(self, built_repo):
        archive = self.archive(built_repo)
        entries = self.contents(archive) | {"references/smuggled.md": b"# No\n"}
        codes = self.check(built_repo, self.rewrite(archive, entries))
        assert codes == ["LQC-U005"]
