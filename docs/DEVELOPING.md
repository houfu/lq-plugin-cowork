# Developing the build tooling

[docs/CONTRACT.md](CONTRACT.md) is the specification. This file is only about
the code that implements it.

## Layout

`tools/` is a uv project whose single package is `lqcowork`:

| Module | Responsibility |
| --- | --- |
| `config.py` | load and shape-check `cowork.yaml` and `skills/<name>/skill.yaml`; find the repo root by walking up for `cowork.yaml` |
| `transforms.py` | pure text: gitignore-style path matching, frontmatter parse/serialise, waiver stripping, `$name`/`/name` rewriting, literal replacement, section overlays |
| `build.py` | the per-skill pipeline from contract section 5, plus manifest emission |
| `validate.py` | every error and warning code from contract section 6, run against `dist/` |
| `package.py` | zip assembly, the trigger-test checklist, the build report |
| `bump.py` | `bump-upstream` (fetch, temporary worktree, drift report, pin) and `anchor` |
| `release.py` | `release-check`: a tag against `cowork.yaml`, `CHANGELOG.md` and any built manifest |
| `icons.py` | PNG signature + IHDR parsing, for the 192x192 / 32x32 check |
| `cli.py` | argparse; maps exceptions to exit codes 0 / 1 / 2 |

`tools/scripts/make_icons.py` is a one-off generator, not part of the package:
it decodes, box-filters and re-encodes PNGs with nothing but the standard
library (Pillow is deliberately not a dependency; `sips` is used only to
normalise a source PNG the decoder cannot read). Re-run it with
`uv run --project tools python tools/scripts/make_icons.py` and commit the two
files under `branding/`.

Everything in `transforms.py` is filesystem-free on purpose, which is what
makes the fiddly rules — token rewriting that must not touch
`references/wiki.md`, section spans that must ignore fenced code — cheap to
test directly.

## Tests

```sh
make test                                   # pytest
uv run --project tools pytest               # the same thing
make fmt-check                              # formatting, line length 88
uv run --project tools black --check tools  # the same thing
```

The root `pytest.ini` sets `testpaths = tools/tests`, which is what keeps a
bare `pytest` from sweeping the whole tree — upstream vendors its own large
test suite under `upstream/packages/`. Do not move that file into `tools/`:
pytest resolves its rootdir from the invocation directory, so the config has
to sit at the repository root to take effect.

## How the fixtures work

`tools/tests/conftest.py` builds a miniature repository in `tmp_path` — its own
`cowork.yaml`, one bundle, a fake upstream tree and two cards — and returns its
root as the `fixture_repo` fixture. There are no binary blobs: the two branding
icons are written by a ten-line PNG writer in the same file.

The fixture is built to trip every mechanical rule at once. `core/alpha` has a
waiver comment alone on a line and another inline, `$beta` plus backticked and
bare `/beta` tokens next to path-like `references/beta.md` and `../beta/` that
must survive untouched, Claude-only frontmatter keys, a `scripts/` folder to
exclude, an `agents/` folder and a `LICENSE` for the global strip, a section to
replace and another to delete, a `replace` anchor, a `files/` companion and a
patch against it. `core/beta` exercises the full-file overlay path.
`extra/gamma` exists upstream and is in no bundle, which is what the drift
report's "in no bundle" list and the out-of-bundle reference warning need.

`skills/gamma/` is a card with no bundle, which is what the trigger-target
rules need: a hand-off to a real card that this bundle does not ship must
render as "expect none", while a hand-off to something with no card at all is
a config error. `references/beta.md` is the one companion no transform
touches, so it stays byte-identical to upstream — that is what makes it the
fixture for the step 10b "leave it alone" branch and for the LQC-W010
authority-URL exemption.

Tests mutate that tree before building to provoke one rule at a time: rewrite a
card's `expect:` to force an anchor failure, drop a file, tamper with the
built `manifest.json`, or `monkeypatch` a size constant in `validate` so a
limit can be crossed without writing megabytes.

`tools/tests/test_bump.py` turns the fixture's `upstream/` into a real
two-commit git repository and drives `collect_drift` over a real worktree, so
the drift logic is covered without touching the network.

`tools/tests/test_e2e.py` builds the real bundles from the real submodule into
a `tmp_path_factory` directory via `Builder(..., out_dir=...)`, never the shared
`dist/`, so it neither depends on a previous build nor races anyone else's. It
skips itself when a card named in `cowork.yaml` does not exist yet, so the
suite stays green while skills are still being written.

`tools/tests/test_bump.py` also stands up a bare clone as `origin`, which lets
`bump-upstream --dry-run` run end to end — fetch, worktree, report, cleanup —
with no network.

## Releasing

[docs/RELEASING.md](RELEASING.md) is the maintainer's procedure — bump
`package.version`, move the `CHANGELOG.md` entries into a dated section,
`make package`, commit, then `make release TAG=vX.Y.Z`, which refuses a dirty
tree or a tag that already exists, runs `release-check` and pushes the tag.
`.github/workflows/release.yml` takes it from there: it tests, packages, builds
a second time to prove the zips are byte-identical, and publishes them with the
trigger-test checklists, the build report and `SHA256SUMS`.

`release-check` itself is specified in contract section 7 and lives in
`release.py`; `tools/tests/test_release.py` drives it through `main()` the way
the Makefile does, over a fixture repository with a changelog written into it.
