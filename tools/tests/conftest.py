"""A miniature repository fixture that exercises every transform and rule.

``fixture_repo`` writes a self-contained tree into ``tmp_path``:

    upstream/skills/core/{alpha,beta}/...   two adapted skills
    upstream/skills/extra/gamma/...         an upstream skill in no bundle
    skills/{alpha,beta}/                    the adaptation cards
    branding/{color,outline}.png            correctly sized solid PNGs
    cowork.yaml                             one bundle, 'test-bundle'

Tests mutate a copy of it to provoke individual validation codes.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import pytest

FAKE_SHA = "a1b2c3d4" * 5
OTHER_SHA = "b" * 40

ALPHA_SKILL = """---
name: alpha
description: >-
  The upstream description for alpha, which the card replaces wholesale.
argument-hint: "[a thing]"
disable-model-invocation: true
compatibility: Requires local command execution and Python 3.12 or newer.
metadata:
  legalquants.python-requires: ">=3.12"
---

# Alpha

Run `scripts/alpha.py` to do the thing.

See [the beta notes](references/beta.md) and ../beta/SKILL.md for the rest.

Type $beta to switch, or `/beta` -- `/beta --fast` works too. Use /beta now.

<!-- vendor-neutral-waiver: this release's local packaged runner uses Codex. -->
Automation requires lifecycle support.

Read the notes <!-- vendor-neutral-waiver: an inline one. -->`references/notes.md`.

## Automation is an optional enhancement

Manual operation is the complete normal product.

### A subsection

Still inside the automation section.

## Finish well

Say goodbye.

## Keep this

The last section survives untouched.
"""

BETA_SKILL = """---
name: beta
description: The upstream beta description.
---

# Beta

Upstream body that our full-file overlay replaces.
"""

GAMMA_SKILL = """---
name: gamma
description: An upstream skill that ships in no bundle.
---

# Gamma
"""

BETA_OVERLAY = """---
name: beta
description: Documentation only; the build overwrites this from the card.
---

# Beta

Our own body. It hands off to the `alpha` skill and mentions $alpha once.
"""

ALPHA_SECTION = """## Automation is not available here

Everything alpha does is a reading-and-drafting step you can follow by hand.
"""

# Our own companion: one URL moved out of an upstream reference (exempt) and
# one this adaptation introduced (LQC-W010).
ALPHA_EXTRA = """# Extra

Body line.

Moved from upstream: https://example.invalid/marketing
Introduced here: https://example.invalid/introduced
"""

ALPHA_PATCH = (
    "--- a/references/extra.md\n"
    "+++ b/references/extra.md\n"
    "@@ -4,3 +4,4 @@\n"
    " \n"
    " Moved from upstream: https://example.invalid/marketing\n"
    " Introduced here: https://example.invalid/introduced\n"
    "+Patched line.\n"
)

COWORK_YAML = f"""upstream:
  repo: https://example.invalid/upstream
  sha: {FAKE_SHA}
  path: upstream
  skills_root: skills

developer:
  name: Test Developer
  websiteUrl: https://example.invalid
  privacyUrl: https://example.invalid/privacy
  termsOfUseUrl: https://example.invalid/terms

package:
  version: 0.1.0
  accentColor: "#2D2D2D"
  icons:
    color: branding/color.png
    outline: branding/outline.png
  root_files:
    - upstream/LICENSE
    - NOTICE.md

strip:
  - LICENSE
  - "agents/**"
  - ".*"
  - "**/.*"
  - "**/__pycache__/**"

transforms:
  drop_frontmatter: [disable-model-invocation, argument-hint, allowed-tools]
  strip_waivers: true
  skill_tokens: true
  vendor_words: [Codex, CODEX, ChatGPT, Claude]
  host_words: ["the scribe", "exit code", "--dry-run"]

replace: []

bundles:
  - id: test-bundle
    guid: 5d40f9d0-bbfe-5aa7-a4e9-10b4e0b676bf
    name:
      short: Test Bundle
      full: A test bundle for the lqcowork build
    description:
      short: A short description for the test bundle
      full: >-
        A long description. Adapted from LegalQuants/lq-plugin-oss under
        Apache-2.0; not an upstream release.
    skills:
      - alpha
      - beta
"""

ALPHA_CARD = f"""name: alpha
upstream: core/alpha
bucket: amber
anchored_to: {FAKE_SHA}

description: |
  Does the alpha thing without running anything locally.
  Use when the user asks to "do alpha", "run the alpha pass".
  Do not use for beta work (use the beta skill).

frontmatter:
  compatibility: null

exclude:
  - "scripts/**"

replace:
  - from: "Run `scripts/alpha.py`"
    to: "Open the alpha folder"
    expect: 1

sections:
  - match: "## Automation is an optional enhancement"
    file: sections/automation.md
  - match: "## Finish well"
    delete: true

patches:
  - patches/extra-note.patch

files: files

notes: |
  Dropped scripts/; the chat path in the body is the documented fallback.

triggers:
  positive:
    - "Do the alpha pass on this folder."
    - "Run alpha over these documents."
  negative:
    - "Do the beta thing instead. -> beta"
    - "Turn this into a Word document. -> Word"
    - "Do the gamma thing. -> gamma"
    - "Summarise this email thread. -> none"
"""

GAMMA_CARD = f"""name: gamma
upstream: extra/gamma
bucket: green
anchored_to: {FAKE_SHA}

description: |
  Does the gamma thing.
  Use when the user asks to "do gamma".
  Do not use for alpha work (use the alpha skill).

triggers:
  positive:
    - "Do the gamma thing."
  negative:
    - "Do the alpha pass. -> alpha"
"""

BETA_CARD = f"""name: beta
upstream: core/beta
bucket: green
anchored_to: {FAKE_SHA}

description: |
  Does the beta thing.
  Use when the user asks to "do beta".
  Do not use for alpha work (use the alpha skill).

triggers:
  positive:
    - "Do the beta thing."
  negative:
    - "Do the alpha pass. -> alpha"
"""


def write_png(path: Path, width: int, height: int, rgb: tuple[int, int, int]) -> None:
    """A tiny solid-colour PNG writer, so the fixture needs no binary blobs."""
    raw = bytearray()
    for _ in range(height):
        raw.append(0)
        raw += bytes(rgb) * width

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_repo(root: Path) -> Path:
    """Materialise the fixture repository at ``root``."""
    upstream = root / "upstream" / "skills"
    alpha = upstream / "core" / "alpha"
    _write(alpha / "SKILL.md", ALPHA_SKILL)
    _write(
        alpha / "references" / "notes.md",
        "# Notes\n\nSee $beta and `/beta`.\n"
        "Background: https://example.invalid/marketing\n",
    )
    # untouched by every transform, so it stays byte-identical to upstream and
    # its authority URL is exempt from LQC-W010
    _write(
        alpha / "references" / "beta.md",
        "# Beta notes\n\nAuthority: https://example.invalid/authority\n",
    )
    _write(alpha / "scripts" / "alpha.py", "print('hello')\n")
    _write(alpha / "agents" / "openai.yaml", "name: alpha\n")
    _write(alpha / "LICENSE", "Apache-2.0\n")
    _write(alpha / ".hidden", "secret\n")

    _write(upstream / "core" / "beta" / "SKILL.md", BETA_SKILL)
    _write(upstream / "extra" / "gamma" / "SKILL.md", GAMMA_SKILL)
    _write(root / "upstream" / "LICENSE", "Apache License 2.0 (upstream copy)\n")
    _write(root / "NOTICE.md", "# Notice\n\nAdapted from upstream.\n")

    _write(root / "cowork.yaml", COWORK_YAML)
    _write(root / "skills" / "alpha" / "skill.yaml", ALPHA_CARD)
    _write(root / "skills" / "alpha" / "sections" / "automation.md", ALPHA_SECTION)
    _write(root / "skills" / "alpha" / "files" / "references" / "extra.md", ALPHA_EXTRA)
    _write(root / "skills" / "alpha" / "patches" / "extra-note.patch", ALPHA_PATCH)
    _write(root / "skills" / "beta" / "skill.yaml", BETA_CARD)
    _write(root / "skills" / "gamma" / "skill.yaml", GAMMA_CARD)
    _write(root / "skills" / "beta" / "SKILL.md", BETA_OVERLAY)

    write_png(root / "branding" / "color.png", 192, 192, (45, 45, 45))
    write_png(root / "branding" / "outline.png", 32, 32, (255, 255, 255))
    return root


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    return make_repo(tmp_path / "repo")


@pytest.fixture
def real_root() -> Path:
    """The real repository root (tools/tests/../..)."""
    return Path(__file__).resolve().parents[2]
