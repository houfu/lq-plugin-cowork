# skills/

Each folder here — `skills/<name>/` — is an **adaptation card**: a build
input for one skill, not the skill itself. It holds `skill.yaml` (the card,
required) and, optionally, `SKILL.md` (a full-file overlay), `sections/*.md`,
`patches/*.patch` and `files/**`. See
[docs/CONTRACT.md](../docs/CONTRACT.md) section 4 for the card format.

**There is no `SKILL.md` at the root of most of these folders, and nothing
here has the licence notice, the Cowork-facing `description` or the
`metadata.adapted-from`/`metadata.version` stamps the build adds.** Those only
exist after `make package` runs. Downloading or zipping a folder from this
directory on GitHub does not produce a working skill — it produces exactly
what [UAT issue 19](https://github.com/houfu/lq-plugin-cowork/issues/19)
reported: an archive with no `SKILL.md`, which Cowork's Upload skill control
cannot use.

## Getting a skill

Do not download these folders. Go to the
[latest release](https://github.com/houfu/lq-plugin-cowork/releases/latest)
instead:

- **One skill, no admin, no terminal** — download `<name>.skill` and use
  Cowork's **Upload skill** control. See
  [Route 0 in docs/INSTALL.md](../docs/INSTALL.md#route-0-upload-a-single-skill).
- **A whole plugin** — download one of the two bundle `.zip` files and install
  it as a plugin. See [docs/INSTALL.md](../docs/INSTALL.md).

## Building it yourself

If you are working on the adaptation, `make package` turns these cards into
finished `SKILL.md` files under `dist/<bundle>/skills/<name>/` and into
upload-ready archives at `dist/skills/<name>.skill` (contract section 5b).
