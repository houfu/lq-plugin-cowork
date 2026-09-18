"""Build the real bundles. Skipped until the skill cards exist."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from lqcowork.build import Builder
from lqcowork.config import load_cards, load_config, upstream_skill_names
from lqcowork.package import write_zip
from lqcowork.validate import validate_bundle


@pytest.fixture(scope="module")
def real_config(request):
    root = Path(__file__).resolve().parents[2]
    if not (root / "upstream" / "skills").is_dir():
        pytest.skip("the upstream submodule is not checked out")
    config = load_config(root)
    missing = [
        name
        for bundle in config.bundles
        for name in bundle.skills
        if not (root / "skills" / name / "skill.yaml").is_file()
    ]
    if missing:
        pytest.skip(f"skill cards not written yet: {', '.join(sorted(set(missing)))}")
    return config


@pytest.fixture(scope="module")
def real_out(tmp_path_factory):
    """Build somewhere of our own, never the shared dist/."""
    return tmp_path_factory.mktemp("lqcowork-e2e")


@pytest.fixture(scope="module")
def real_build(real_config, real_out):
    # report_anchors keeps a card that is mid-edit from turning into a fixture
    # error; the assertion below still fails, but readably.
    builder = Builder(real_config, report_anchors=True, out_dir=real_out)
    return real_config, builder, builder.build()


def test_upstream_tree_has_the_expected_skills(real_config):
    names = upstream_skill_names(real_config)
    assert len(names) == 31
    assert "wiki" in names and "lq-start" in names


def test_every_bundle_builds_and_validates(real_build, real_out):
    config, builder, result = real_build
    assert [i.render() for i in result.anchors] == []
    assert [i.render() for i in result.errors] == []
    cards = load_cards(config, [n for b in config.bundles for n in b.skills])
    for built in result.bundles:
        errors, _ = validate_bundle(
            config,
            built.bundle,
            cards=cards,
            skill_names=builder.skill_names,
            out_dir=real_out,
        )
        assert errors == [], [e.render() for e in errors]


def test_manifests_and_zips(real_build, real_out):
    config, _, result = real_build
    for built in result.bundles:
        manifest = json.loads((built.path / "manifest.json").read_text())
        assert manifest["id"] == built.bundle.guid
        assert len(manifest["agentSkills"]) == len(built.bundle.skills)
        archive = write_zip(config, built.bundle, real_out)
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
        assert "manifest.json" in names
        assert "LICENSE" in names
        assert "NOTICE.md" in names


def test_no_vendor_words_survive_in_shipped_skills(real_build):
    config, _, result = real_build
    offenders: list[str] = []
    for built in result.bundles:
        for skill in built.skills:
            for path in sorted(skill.path.rglob("*.md")):
                text = path.read_text(encoding="utf-8")
                for word in config.transforms.vendor_words:
                    if f" {word} " in text or text.startswith(word):
                        offenders.append(f"{path.name}: {word}")
    assert offenders == [], offenders
