"""The static site: the pages, the links, and the promise that it repeats.

Everything here runs against ``mirror_repo``, the fixture whose bundle derives
its membership from upstream's release manifest, because that is the shape the
three real bundles have.
"""

from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

import pytest

from lqcowork.cli import main
from lqcowork.config import load_config
from lqcowork.site import SiteError, build_site
from lqcowork.site.generate import (
    LATEST_DOWNLOAD_URL,
    PROJECT_REPO,
    ReportWarning,
    download_url,
    first_sentence,
    human_size,
    read_archive,
    read_report_warnings,
    render_markdown,
    shorten,
    slug,
    ticks,
)

CHANGELOG = """# Changelog

## [0.1.0] - 2026-09-20

The first release. See [installing a bundle](docs/INSTALL.md).
"""

INSTALL = """# Installing a bundle

## Before you start

Read [the testing guide](TESTING.md) first, and [the contract](CONTRACT.md)
if you want to know why. Jump to [what to do](#before-you-start).

| Step | What |
| --- | --- |
| 1 | Upload it |
"""

TESTING = """# Testing

Back to [installing](INSTALL.md), and to [the changelog](../CHANGELOG.md).
"""

LINK_RE = re.compile(r'(?:href|src)="([^"]+)"')
_SCHEME = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def _write_docs(root: Path) -> None:
    """The three Markdown pages the site renders, which the fixture lacks."""
    (root / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "INSTALL.md").write_text(INSTALL, encoding="utf-8")
    (docs / "TESTING.md").write_text(TESTING, encoding="utf-8")


@pytest.fixture
def site(mirror_repo: Path, monkeypatch) -> Path:
    """A packaged fixture repository with its site rendered into dist/."""
    _write_docs(mirror_repo)
    monkeypatch.chdir(mirror_repo)
    assert main(["package"]) == 0
    assert main(["site"]) == 0
    return mirror_repo / "dist" / "site"


def _pages(site: Path) -> list[str]:
    return sorted(p.relative_to(site).as_posix() for p in site.rglob("*.html"))


def _write_archives(out: Path, *names: str) -> None:
    """Stand in for what ``package`` writes into ``<out>/skills/``.

    The sizes on the site come from these files, so the tests make their own
    rather than depend on whether the build wrote any.
    """
    for name in names:
        path = out / "skills" / f"{name}.skill"
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("SKILL.md", f"---\nname: {name}\n---\n\n# {name}\n")
            archive.writestr("LICENSE", "Apache License 2.0\n")


class TestPages:
    def test_every_page_in_the_contract_is_written(self, site):
        assert _pages(site) == [
            "bundles/test-bundle.html",
            "changelog.html",
            "differences.html",
            "downloads.html",
            "index.html",
            "install.html",
            "known-issues.html",
            "probes.html",
            "skills/alpha.html",
            "skills/beta.html",
            "skills/gamma.html",
            "testing.html",
            "verdicts.html",
        ]

    def test_the_stylesheet_is_the_only_asset(self, site):
        assert [p.name for p in sorted((site / "assets").iterdir())] == ["site.css"]

    def test_every_page_carries_the_landmarks(self, site):
        for page in site.rglob("*.html"):
            text = page.read_text(encoding="utf-8")
            assert '<a class="skip" href="#main">' in text, page
            assert '<main class="page" id="main">' in text, page
            assert "<nav aria-label=" in text, page
            assert "<footer" in text, page

    def test_the_footer_names_the_version_the_sha_and_the_licence(self, site):
        text = (site / "index.html").read_text(encoding="utf-8")
        assert "Package version 0.1.0" in text
        assert "<code>a1b2c3d</code>" in text
        assert "Apache-2.0" in text
        assert "not an official LegalQuants release" in text
        assert "/tree/" + "a1b2c3d4" * 5 in text

    def test_the_index_says_what_this_is_not(self, site):
        text = (site / "index.html").read_text(encoding="utf-8")
        assert "not an official LegalQuants release" in text
        assert "pre-release" in text
        assert "live tenant" in text
        assert "Sources" in text  # how routing works
        assert "no slash grammar" in text
        assert f"{PROJECT_REPO}/releases/latest" in text
        assert "test-bundle.zip" in text  # the asset by name
        assert 'href="testing.html"' in text

    def test_the_downloads_page_lists_every_package_and_every_archive(self, site):
        text = (site / "downloads.html").read_text(encoding="utf-8")
        assert f"{LATEST_DOWNLOAD_URL}/test-bundle.zip" in text
        assert f"{LATEST_DOWNLOAD_URL}/test-bundle-trigger-tests.md" in text
        for name in ("alpha", "beta", "gamma"):
            assert f"{LATEST_DOWNLOAD_URL}/{name}.skill" in text, name
            assert f'href="skills/{name}.html"' in text, name
        assert f"{LATEST_DOWNLOAD_URL}/SHA256SUMS" in text
        assert f"{LATEST_DOWNLOAD_URL}/build-report.md" in text
        assert f'href="{PROJECT_REPO}/releases"' in text
        assert "Customize" in text  # where a .skill archive is uploaded
        assert "not a pre-release" in text

    def test_every_page_offers_the_downloads_page(self, site):
        for page in sorted(site.rglob("*.html")):
            assert "downloads.html" in page.read_text(encoding="utf-8"), page

    def test_the_index_links_the_packages_rather_than_naming_them(self, site):
        text = (site / "index.html").read_text(encoding="utf-8")
        assert f'href="{LATEST_DOWNLOAD_URL}/test-bundle.zip"' in text
        assert f'href="{LATEST_DOWNLOAD_URL}/SHA256SUMS"' in text
        assert f'href="{PROJECT_REPO}/releases"' in text
        assert 'href="downloads.html"' in text
        assert "<code>.skill</code>" in text
        assert "not a pre-release" in text

    def test_the_bundle_page_carries_the_manifest_and_the_mirror(self, site):
        text = (site / "bundles/test-bundle.html").read_text(encoding="utf-8")
        assert "A test bundle for the lqcowork build" in text
        assert "Mirrors upstream plugin test-plugin" in text
        assert "The Upstream Test Plugin" in text  # upstream's display name
        assert "test-bundle.zip" in text
        assert "activate <code>alpha</code>" in text
        assert "must not activate; expect built-in Word" in text

    def test_the_bundle_page_downloads_the_package_and_its_checklist(self, site):
        text = (site / "bundles/test-bundle.html").read_text(encoding="utf-8")
        assert 'id="download"' in text
        assert f'href="{LATEST_DOWNLOAD_URL}/test-bundle.zip"' in text
        assert f'href="{LATEST_DOWNLOAD_URL}/test-bundle-trigger-tests.md"' in text
        assert f'href="{LATEST_DOWNLOAD_URL}/SHA256SUMS"' in text
        # every row of the skills table offers that skill on its own
        for name in ("alpha", "beta"):
            assert f'href="{LATEST_DOWNLOAD_URL}/{name}.skill"' in text, name

    def test_the_skill_page_has_every_section(self, site):
        text = (site / "skills/alpha.html").read_text(encoding="utf-8")
        for anchor in (
            "what-it-does",
            "when-to-use-it",
            "not-for",
            "bundles",
            "differs",
            "known-issues",
            "workarounds",
            "upstream",
            "files",
        ):
            assert f'id="{anchor}"' in text, anchor
        assert "Does the alpha thing without running anything locally." in text
        assert "Do the alpha pass on this folder." in text
        assert "The original ran a bundled program over the folder." in text
        assert "<summary>Build notes</summary>" in text
        assert "Dropped scripts/" in text  # the card's `notes`
        assert "The upstream description for alpha" in text
        assert "<code>SKILL.md</code>" in text
        assert "<code>references/notes.md</code>" in text
        assert "<code>scripts/alpha.py</code>" not in text  # excluded by the card
        assert f"{PROJECT_REPO}/issues?q=is%3Aissue+%22UAT%3A+alpha%22" in text
        assert "/tree/" + "a1b2c3d4" * 5 + "/skills/core/alpha" in text

    def test_the_skill_page_offers_the_skill_on_its_own(self, site):
        text = (site / "skills/alpha.html").read_text(encoding="utf-8")
        assert 'id="get-this-skill"' in text
        assert f'href="{LATEST_DOWNLOAD_URL}/alpha.skill"' in text
        assert "<code>alpha.skill</code>" in text
        assert "Customize" in text
        assert "<code>SKILL.md</code>" in text
        # and the bundles it ships in, as zips rather than as names
        assert f'href="{LATEST_DOWNLOAD_URL}/test-bundle.zip"' in text

    def test_a_skill_page_without_known_issues_says_so(self, site):
        text = (site / "skills/beta.html").read_text(encoding="utf-8")
        assert "None declared on the card." in text
        assert "None: nothing upstream did here needed replacing." in text

    def test_tier_and_status_badges_carry_the_legend(self, site):
        text = (site / "skills/alpha.html").read_text(encoding="utf-8")
        assert "one named probe, or shipped now with an announced degrade" in text
        assert "Tier 2" in text and "probe-gated" in text

    def test_known_issue_ids_appear_with_their_failure_and_probe(self, site):
        text = (site / "known-issues.html").read_text(encoding="utf-8")
        assert "KI-alpha-1" in text
        assert "A document it cannot open reads as an empty one" in text
        assert 'class="badge badge-silent"' in text
        assert 'href="probes.html#P3"' in text
        assert 'href="skills/alpha.html#KI-alpha-1"' in text

    def test_the_filter_degrades_to_the_whole_table(self, site):
        text = (site / "known-issues.html").read_text(encoding="utf-8")
        # the controls are built by the script, so there is no dead widget
        assert "<select" not in text
        assert text.count("<script>") == 1
        assert 'data-failure="silent"' in text

    def test_the_probe_page_lists_every_probe(self, site, mirror_repo):
        config = load_config(mirror_repo)
        text = (site / "probes.html").read_text(encoding="utf-8")
        assert config.probes
        for probe in config.probes:
            assert f'id="{probe.id}"' in text, probe.id
            assert probe.title in text
            assert probe.prompt in text
            assert probe.passes in text
        assert 'href="skills/alpha.html"' in text  # what P3 unlocks

    def test_the_differences_page_covers_the_five_things(self, site):
        text = (site / "differences.html").read_text(encoding="utf-8")
        assert "No local disk" in text
        assert "Scripts: documented, but never specified" in text
        assert "Web reach exists" in text
        assert "Sessions" in text
        assert 'id="claim-words"' in text
        assert "<code>receipt</code>" in text  # the claim-word list
        assert 'id="tiers"' in text
        assert "Mirrors upstream plugin test-plugin" in text
        assert "the description and the mechanics" in text  # the rubric
        for name in ("alpha", "beta", "gamma"):
            assert f'href="skills/{name}.html"' in text

    def test_the_markdown_pages_render_with_tables(self, site):
        install = (site / "install.html").read_text(encoding="utf-8")
        assert '<h1 id="installing-a-bundle">' in install
        assert "<table>" in install
        assert "<td>Upload it</td>" in install
        assert 'href="testing.html"' in install  # TESTING.md -> the site page
        assert f'href="{PROJECT_REPO}/blob/main/docs/CONTRACT.md"' in install
        assert 'href="#before-you-start"' in install
        testing = (site / "testing.html").read_text(encoding="utf-8")
        assert 'href="install.html"' in testing
        assert 'href="changelog.html"' in testing
        assert "2026-09-20" in (site / "changelog.html").read_text(encoding="utf-8")

    def test_an_absent_markdown_source_still_writes_the_page(
        self, mirror_repo, monkeypatch
    ):
        monkeypatch.chdir(mirror_repo)
        assert main(["package"]) == 0
        assert main(["site"]) == 0
        text = (mirror_repo / "dist/site/changelog.html").read_text(encoding="utf-8")
        assert "is not in" in text and "nothing to show" in text
        assert f'href="{PROJECT_REPO}/blob/main/CHANGELOG.md"' in text


class TestSkillArchives:
    """The `.skill` archives are `package`'s to write; the site must not need them."""

    def _render(self, repo: Path) -> Path:
        build_site(load_config(repo))
        return repo / "dist" / "site"

    def test_the_site_renders_with_no_archives_built(self, mirror_repo, monkeypatch):
        _write_docs(mirror_repo)
        monkeypatch.chdir(mirror_repo)
        assert main(["package"]) == 0
        shutil.rmtree(mirror_repo / "dist" / "skills", ignore_errors=True)
        site = self._render(mirror_repo)

        downloads = (site / "downloads.html").read_text(encoding="utf-8")
        assert "no sizes are shown" in downloads
        # the link is the same either way: it points at the release, not here
        assert f'href="{LATEST_DOWNLOAD_URL}/alpha.skill"' in downloads
        assert downloads.count('<td class="num">\u2014</td>') == 3
        skill = (site / "skills/alpha.html").read_text(encoding="utf-8")
        assert f'href="{LATEST_DOWNLOAD_URL}/alpha.skill"' in skill
        assert " bytes" not in skill

    def test_a_built_archive_puts_its_size_and_file_count_on_the_page(
        self, mirror_repo, monkeypatch
    ):
        _write_docs(mirror_repo)
        monkeypatch.chdir(mirror_repo)
        assert main(["package"]) == 0
        _write_archives(mirror_repo / "dist", "alpha", "beta", "gamma")
        site = self._render(mirror_repo)

        size = (mirror_repo / "dist/skills/alpha.skill").stat().st_size
        skill = (site / "skills/alpha.html").read_text(encoding="utf-8")
        assert f"{size} bytes, 2 files" in skill
        downloads = (site / "downloads.html").read_text(encoding="utf-8")
        assert "Sizes are read from the archives" in downloads
        assert f"{size} bytes" in downloads

    def test_a_site_built_without_an_archive_still_links_it(
        self, mirror_repo, monkeypatch
    ):
        """Only two skills' archives exist; all three keep their link."""
        _write_docs(mirror_repo)
        monkeypatch.chdir(mirror_repo)
        assert main(["package"]) == 0
        shutil.rmtree(mirror_repo / "dist" / "skills", ignore_errors=True)
        _write_archives(mirror_repo / "dist", "alpha", "beta")
        site = self._render(mirror_repo)

        downloads = (site / "downloads.html").read_text(encoding="utf-8")
        assert f'href="{LATEST_DOWNLOAD_URL}/gamma.skill"' in downloads
        # only gamma's size cell is empty
        assert downloads.count('<td class="num">\u2014</td>') == 1

    def test_an_unreadable_archive_costs_the_size_not_the_page(
        self, mirror_repo, monkeypatch
    ):
        _write_docs(mirror_repo)
        monkeypatch.chdir(mirror_repo)
        assert main(["package"]) == 0
        broken = mirror_repo / "dist/skills/alpha.skill"
        broken.parent.mkdir(parents=True, exist_ok=True)
        broken.write_text("not a zip at all", encoding="utf-8")
        site = self._render(mirror_repo)

        skill = (site / "skills/alpha.html").read_text(encoding="utf-8")
        assert f'href="{LATEST_DOWNLOAD_URL}/alpha.skill"' in skill
        assert " bytes" not in skill


class TestLinks:
    def test_every_internal_link_resolves_to_a_file(self, site):
        missing: list[tuple[str, str]] = []
        for page in sorted(site.rglob("*.html")):
            for href in LINK_RE.findall(page.read_text(encoding="utf-8")):
                if href.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target = href.partition("#")[0]
                if target and not (page.parent / target).resolve().is_file():
                    missing.append((page.name, href))
        assert missing == []

    def test_no_link_is_rooted_at_the_server(self, site):
        """The site is served under /lq-plugin-cowork/, so nothing may be /-rooted."""
        rooted = [
            (page.name, href)
            for page in sorted(site.rglob("*.html"))
            for href in LINK_RE.findall(page.read_text(encoding="utf-8"))
            if href.startswith("/")
        ]
        assert rooted == []

    def test_no_asset_comes_from_off_the_site(self, site):
        """A reader fetches the stylesheet and nothing else."""
        for page in sorted(site.rglob("*.html")):
            text = page.read_text(encoding="utf-8")
            for tag in re.findall(r"<(?:script|link|img)\b[^>]*>", text):
                for ref in LINK_RE.findall(tag):
                    assert not _SCHEME.match(ref), (page.name, tag)
                    assert ref.replace("../", "") == "assets/site.css", (
                        page.name,
                        tag,
                    )


class TestReproducible:
    def test_two_runs_are_byte_identical(self, mirror_repo, tmp_path, monkeypatch):
        _write_docs(mirror_repo)
        monkeypatch.chdir(mirror_repo)
        config = load_config(mirror_repo)
        digests = []
        for run in ("first", "second"):
            out = tmp_path / run
            assert main(["package", "--out", str(out)]) == 0
            # the sizes on the pages come from these, so they are in the check
            _write_archives(out, "alpha", "beta", "gamma")
            build_site(config, out)
            root = out / "site"
            digests.append(
                {
                    path.relative_to(root).as_posix(): path.read_bytes()
                    for path in sorted(root.rglob("*"))
                    if path.is_file()
                }
            )
        assert digests[0] == digests[1]

    def test_nothing_on_a_page_looks_like_a_date_stamp(self, site):
        """The only build-specific values are the version and the SHA."""
        for page in sorted(site.rglob("*.html")):
            if page.name in {"changelog.html", "install.html", "testing.html"}:
                continue  # the Markdown sources carry their own dates
            text = page.read_text(encoding="utf-8")
            assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text), page


class TestErrors:
    def test_a_missing_build_report_says_to_package_first(
        self, mirror_repo, monkeypatch
    ):
        monkeypatch.chdir(mirror_repo)
        assert main(["package"]) == 0
        (mirror_repo / "dist/build-report.md").unlink()
        config = load_config(mirror_repo)
        with pytest.raises(SiteError, match="build-report.md"):
            build_site(config)

    def test_a_missing_bundle_tree_says_to_package_first(self, mirror_repo):
        config = load_config(mirror_repo)
        with pytest.raises(SiteError, match="package"):
            build_site(config)

    def test_the_cli_reports_it_as_an_error(self, mirror_repo, monkeypatch):
        monkeypatch.chdir(mirror_repo)
        assert main(["site"]) == 1

    def test_the_out_directory_is_honoured(self, mirror_repo, tmp_path, monkeypatch):
        monkeypatch.chdir(mirror_repo)
        out = tmp_path / "elsewhere"
        assert main(["package", "--out", str(out)]) == 0
        assert main(["site", "--out", str(out)]) == 0
        assert (out / "site/index.html").is_file()
        assert not (mirror_repo / "dist/site").exists()


class TestHelpers:
    def test_first_sentence_stops_at_the_first_full_stop(self):
        assert first_sentence("One thing. Then another.") == "One thing."
        assert first_sentence("  A\n  wrapped one.  Next.") == "A wrapped one."
        assert first_sentence("") == ""

    def test_shorten_cuts_on_a_word_boundary(self):
        assert shorten("one two three", 40) == "one two three"
        assert shorten("one two three four", 12) == "one two…"

    def test_ticks_escapes_before_it_marks_up(self):
        assert str(ticks("expect `a`")) == "expect <code>a</code>"
        assert "&lt;b&gt;" in str(ticks("<b> `x`"))

    def test_a_download_url_names_no_version(self):
        assert download_url("alpha.skill") == (
            f"{PROJECT_REPO}/releases/latest/download/alpha.skill"
        )

    def test_human_size_rounds_the_same_way_twice(self):
        assert human_size(0) == "0 bytes"
        assert human_size(1023) == "1023 bytes"
        assert human_size(1024) == "1.0 KB"
        assert human_size(1536) == "1.5 KB"
        assert human_size(5 * 1024 * 1024) == "5.0 MB"
        assert human_size(3 * 1024**3) == "3.0 GB"

    def test_a_missing_or_broken_archive_reads_as_nothing(self, tmp_path):
        assert read_archive(tmp_path / "nope.skill") is None
        bad = tmp_path / "bad.skill"
        bad.write_text("not a zip", encoding="utf-8")
        assert read_archive(bad) is None

    def test_an_archive_reports_its_size_and_its_files(self, tmp_path):
        _write_archives(tmp_path, "alpha")
        path = tmp_path / "skills/alpha.skill"
        assert read_archive(path) == (path.stat().st_size, 2)

    def test_slug_matches_the_anchors_github_makes(self):
        assert (
            slug("A. Upload it yourself in Cowork") == "a-upload-it-yourself-in-cowork"
        )
        assert slug("Part D — What happens") == "part-d--what-happens"
        seen: dict[str, int] = {}
        assert [slug("Notes", seen), slug("Notes", seen)] == ["notes", "notes-1"]

    def test_markdown_leaves_an_external_link_alone(self):
        html = render_markdown("[x](https://example.invalid/a)", "docs/INSTALL.md")
        assert 'href="https://example.invalid/a"' in html

    def test_markdown_escapes_raw_html(self):
        assert "&lt;script&gt;" in render_markdown("<script>x</script>", "CHANGELOG.md")

    def test_report_warnings_survive_an_escaped_pipe(self, tmp_path):
        report = tmp_path / "build-report.md"
        report.write_text(
            "# Build report\n\n## Warnings:\n\n"
            "| Code | Bundle | Skill | Where | Detail |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| LQC-W001 | b | alpha | SKILL.md:3 | a \\| b |\n",
            encoding="utf-8",
        )
        assert read_report_warnings(report) == (
            ReportWarning("LQC-W001", "b", "alpha", "SKILL.md:3", "a | b"),
        )

    def test_no_report_means_no_warnings(self, tmp_path):
        assert read_report_warnings(tmp_path / "nope.md") == ()
