# Installing a skill or a bundle in Microsoft 365 Copilot Cowork

How to get a single `<name>.skill` archive, or a whole bundle
(`legalquants-litigation-cowork.zip` or
`legalquants-transactional-cowork.zip`), from a
[release](https://github.com/houfu/lq-plugin-cowork/releases/latest) into
Copilot Cowork. If you only want to try one skill, [Route
0](#route-0-upload-a-single-skill) needs no admin and no terminal — start
there. Every Microsoft page this is built on is listed, with the date it was
checked, in [Sources](#sources) at the end. Anything that could not be
confirmed from Microsoft's documentation is marked **unverified** rather than
guessed at.

Nothing in this file has been walked through in a live tenant. If a step is
wrong, or a button is not called what this says it is called, please
[say so](https://github.com/houfu/lq-plugin-cowork/issues/new?template=uat-report.yml)
— that is a useful bug.

## What you are installing

A Cowork plugin is a standard Microsoft 365 app package: a `.zip` holding
`manifest.json` (unified app manifest v1.28), `color.png`, `outline.png` and a
`skills/` folder with one `SKILL.md` per skill. These bundles are **skills
only** — they declare no `agentConnectors`, contact no server, and run no code.
That matters for installation in one concrete way: there is no connector
sign-in, no OAuth consent screen and no admin API consent to grant. What you
install is text the model reads.

## Before you start

| You need | Detail |
| --- | --- |
| Microsoft 365 Copilot licence | Users of Cowork plugins must have Copilot licences assigned. |
| Cowork enabled in the tenant | Cowork is managed in the Microsoft 365 admin center under **Agents** > **All Agents**; admins must enable usage-based billing before users can access it. |
| Permission to add a custom app | Whether you can upload a package yourself, or need an administrator to deploy it, depends on your tenant's policy. See [Who can install](#who-can-install). |
| A desktop or web client | **Custom plugins aren't supported in Cowork on mobile.** |

One tenant-level blocker worth knowing before you start: in tenants with
**Microsoft Purview Information Barriers** enabled, embedded knowledge file
uploads are blocked at the tenant level, which prevents affected plugins and
skills from being uploaded or published. If your tenant uses IB, expect the
upload to fail and talk to your admin first.

## Who can install

Four routes. If you only want one skill, Route 0 needs nothing else on this
page — it is not a plugin install at all. For a whole bundle, pick the first
of A/B/C that your tenant allows.

| Route | Who does it | Good for |
| --- | --- | --- |
| [Route 0. Upload a single skill](#route-0-upload-a-single-skill) | Any user — no admin, no terminal | Testing or using one skill, without installing a plugin |
| [A. Upload it yourself in Cowork](#a-upload-it-yourself-in-cowork) | Any user, if tenant policy allows uploading a plugin package | One tester, one laptop, today |
| [B. Admin deployment](#b-admin-deployment) | Tenant administrator or Copilot administrator | A pilot group, a firm, a controlled rollout |
| [C. The `atk` CLI](#c-the-atk-cli) | A developer with a work account | Scripted installs, repeatable test cycles |

Route A is the author's own fast loop: Microsoft's guidance to plugin authors is
to install your own package directly in Cowork, shared with **Only you**, before
distributing it more widely.

**Unverified:** Microsoft's Cowork pages do not say which tenant setting governs
the Cowork **Customize** upload control, or whether the Teams custom-app-upload
policy (*Allow members to upload custom apps*, and the *Upload custom apps*
option in an app setup policy) gates it. Cowork plugins use the same M365 app
package mechanism as Teams apps, so that policy is the obvious candidate and is
certainly what gates the Teams and `atk` paths — but treat the link as an
assumption. If your upload is refused, that policy is the first thing for an
admin to check.

## Route 0. Upload a single skill

The fastest way to try one skill: no plugin package, no administrator, no
`atk`. This is the route
[UAT issue 19](https://github.com/houfu/lq-plugin-cowork/issues/19) asked for.

1. Download `<name>.skill` (for example `pressuretest.skill`) from the
   [latest release](https://github.com/houfu/lq-plugin-cowork/releases/latest).
   It is a small `.skill` archive — `SKILL.md` at its root plus that skill's
   companion files, `LICENSE` and `NOTICE.md` — not a folder from this
   repository's `skills/` directory (see [skills/README.md](../skills/README.md)).
2. In Cowork, select the **+** button and then **Customize**.
3. Select the **Skills** tab.
4. Select the arrow next to **Add**, then **Upload skill**, and pick the file
   in the file picker.
5. Cowork validates the archive and saves it to your OneDrive
   `/Documents/Cowork/skills/`. It appears under **Your skills** after the
   next sync.
6. Test it in a **new conversation** — the same one-fresh-conversation
   discipline as [docs/TESTING.md](TESTING.md) Part A.

Re-uploading a skill with the same name does **not** replace the old copy:
Cowork keeps both, with a number appended to the new one's name. If you are
re-testing a fixed version, open the old skill's detail page and delete it
first, then upload the new archive.

**Limits** (contract section 8): the archive must be ≤ 10 MB compressed and
≤ 50 MB uncompressed, ≤ 100 files total, with each `.md` inside ≤ 1 MB.
Frontmatter must have both `name` and `description`. Custom skills — uploaded
singly or as part of a plugin — are not supported on mobile.

**Verified** (Microsoft's cowork-customize page, checked 19 September 2026):
the Skills tab, the arrow-next-to-Add path to **Upload skill**, the accepted
formats, the size and file-count limits, the OneDrive save path, and the
same-name-keeps-both re-upload behaviour.

**Unverified:** whether the "only upload skills from sources you trust"
reminder Cowork shows on first use looks exactly as Microsoft describes it,
and how long the OneDrive sync into **Your skills** typically takes.

### Upload troubleshooting checklist

Work through these in order before filing a report:

- **Is it the release asset, not a GitHub folder?** The file must be
  `<name>.skill` downloaded from the release page, never a "Download ZIP" of
  `skills/<name>/` from this repository — that folder is a build input with no
  `SKILL.md` in it (see [skills/README.md](../skills/README.md)).
- **Does `SKILL.md` sit at the archive root?** List the entries —
  `unzip -l <name>.skill` on a terminal, or open the archive in any zip viewer
  — and confirm `SKILL.md` is a top-level entry, not nested inside a folder.
- **Size and file-count limits.** ≤ 10 MB compressed, ≤ 50 MB uncompressed,
  ≤ 100 files, each `.md` ≤ 1 MB.
- **Frontmatter present.** `SKILL.md` must open with a `---`-delimited block
  containing `name` and `description`.
- **Microsoft Purview Information Barriers.** IB tenants block embedded
  knowledge file uploads at the tenant level, single-skill archives included —
  ask your admin.
- **Mobile.** Custom skills are not supported in Cowork on mobile; try a
  desktop or web client.

## A. Upload it yourself in Cowork

1. Download the bundle `.zip` from the
   [latest release](https://github.com/houfu/lq-plugin-cowork/releases/latest).
   Do not unzip it.
2. In Cowork, select the **+** button and then **Customize**.
3. Select the **Plugins** tab.
4. Select **Upload plugin** and choose the `.zip` in the file picker.
   (Microsoft's admin-facing page calls the same control **Add plugin**; expect
   one label or the other.)
5. The **Share** dialog opens. Choose **Only you** while you are testing.
   *Specific users in your organization* adds people by name or email.
6. Select **Apply** to publish it.

Nothing here needs approval from anyone while the share is **Only you**.
Publishing to your whole organization is a different thing: that request is held
pending until a tenant administrator approves it.

## B. Admin deployment

An administrator (tenant admin, or the Copilot administrator role) uploads the
package once and assigns it.

1. Sign in to the **Microsoft 365 admin center**.
2. Go to **Manage apps** > **Upload custom app**.
3. Select the ellipsis (**...**) > **Add agent**.
4. Upload the `.zip`.
5. Choose who the package is available to: specific users, specific groups, or
   the entire organization.

Then, to deploy it to those users: in the admin center, select **Agents** and
either **All agents** or **Tools**, find the plugin, open it, select **Installed
for**, choose **All users** or **Specific users/groups**, and select **Next** and
install. Deployed plugins are acquired automatically — users do not browse for
them — and appear in the user's **Added Plugins** tab with a **Managed by your
organization** label.

Two consequences worth telling testers about:

- A user **cannot remove** an admin-deployed plugin. They can still turn it off
  for their own conversations from the **Sources & Skills** panel.
- Packages distributed this way do not go through Microsoft 365 App Store
  validation. That is the right path for a pre-release like this one, and also
  the reason to read the `build-report.md` in the release yourself.

An admin can block the plugin at any time; blocking takes effect for new
conversations, and conversations already running continue to the end.

## C. The `atk` CLI

The Microsoft 365 Agents Toolkit CLI installs a package for your own account
without any UI. This is the path Microsoft documents for personal testing of a
Cowork plugin.

```sh
npm install -g @microsoft/m365agentstoolkit-cli
atk --version                     # Cowork plugin work needs 1.1.12 or later
atk auth login m365               # opens a browser; sign in with your work account
atk install --file-path ./legalquants-litigation-cowork.zip --scope Personal
```

- `atk auth login m365` names the service explicitly. Microsoft's Cowork page
  writes the bare `atk auth login`; the CLI's own commands take a service
  argument (`atk auth logout <service>`), and `atk auth login m365` is the form
  used in Microsoft's own add-in troubleshooting guidance. Use it.
- `--scope` accepts `Personal` and `Shared`. Use `Personal` for a tester.
- A successful install prints a **TitleId** and an **AppId**. Save both: they
  are what `atk uninstall` and `atk launchinfo` take later.
- On Windows, quote the path: `--file-path "C:/Users/you/bundle.zip"`.

**Unverified:** Microsoft documents `atk install --scope Personal` as the way to
sideload a Cowork plugin, but does not separately document how an `atk`-installed
package appears in the Cowork **Customize** page — for instance whether it can
be re-shared or removed from there rather than with `atk uninstall`.

## Confirm it is really there

1. **Find the plugin.** Open the **Sources & Skills** panel in a conversation.
   The plugin should be listed with a toggle; make sure the toggle is on. An
   admin-deployed package also appears in the **Added Plugins** tab of the
   Customize dialog with a **Managed by your organization** label. After an
   admin-centre upload, Microsoft's developer guidance says to look in **Cowork**
   > **Sources & Skills** > **Plugins**, where the plugin appears in the
   **Discover** section.
2. **Check the skills came with it.** When a plugin is enabled, its skills appear
   alongside Cowork's built-in skills as chips in the side panel. The litigation
   bundle should contribute 15; the transactional bundle 8.
3. **Make one activate.** Start a fresh conversation and type a prompt from the
   bundle's `*-trigger-tests.md` in the release, for example:

   > Which of these skills should I use for a contract I just got back from the
   > other side?

   `lq-start` should answer with a map of the LegalQuants skills, and its last
   line should be exactly: *"LegalQuants skills are a workflow aid, not legal
   advice. The judgement stays yours."*

4. **See which skill ran.** The session side panel has a **Skills** section
   listing the skills Cowork loaded during the session, shown as chips, and a
   skill notification appears in the chat when a plugin skill activates.

If the plugin is listed but no skill ever activates, that is a routing result
worth reporting, not an installation failure. Go to
[docs/TESTING.md](TESTING.md).

## Updating to a newer release

The safe recipe: **increase the version, then reinstall.**

Each bundle carries a `version` in its `manifest.json`, which comes from
`package.version` in `cowork.yaml` (`0.1.0` for the first release). Microsoft's
guidance for updating a Microsoft 365 app is to keep the app `id` unchanged and
increment the version number — this repository does exactly that, so every
release ships a higher version than the one before it, and installing a newer
release over an older one is an ordinary update.

- **Path A:** upload the new `.zip` on the **Customize** > **Plugins** tab. If
  you had shared the plugin, open its detail page and select **Re-share** to push
  the new version to everyone you shared it with.
- **Path B:** the admin uploads the new package the same way it was first
  uploaded.
- **Path C:** run `atk install --file-path <new zip> --scope Personal` again.

**Unverified:** no Microsoft page states what happens if you re-upload a package
whose version has *not* increased — whether it is rejected, silently ignored, or
replaces the installed copy. If you are testing a local build with the same
version number, the reliable move is to remove the plugin and install it again.
If you are building your own zip from this repo to test a change, bump
`package.version` in `cowork.yaml` first.

## Removing it

- **Path A (you uploaded it):** open the **Customize** dialog with the **+**
  button, find the plugin, and select **Remove from Cowork**. Its skills and
  connectors disappear from future conversations; conversations already running
  are not interrupted.
- **Path B (admin-deployed):** only the admin can remove it. You can toggle it
  off in the **Sources & Skills** panel; the admin can block or unassign it.
- **Path C (`atk`):** use the title ID the install printed:

  ```sh
  atk uninstall -i false --mode title-id --title-id U_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  ```

  `atk uninstall` also takes `--mode manifest-id --manifest-id <guid>`. The
  manifest ids for these bundles are in `cowork.yaml` and in each release's
  `build-report.md`.

Turning a plugin **off** in the Sources & Skills panel is not removal: it hides
the skills from new conversations and leaves the plugin in your account. For a
clean retest, off-and-on is usually enough; reinstalling is for version changes.

## If something goes wrong

| Symptom | First thing to check |
| --- | --- |
| Upload is refused outright | Tenant policy on custom apps (ask your admin), and whether Purview Information Barriers are enabled — IB blocks plugin upload at the tenant level. |
| Upload fails with a manifest error | You are installing a release zip, not a hand-edited one? The v1.28 schema sets `additionalProperties: false`, so any extra field is rejected. Re-download the release asset and check its SHA256 against `SHA256SUMS`. |
| Plugin installed, no skills visible | Confirm the plugin's toggle is on in **Sources & Skills**, and that you are not on mobile — custom plugins are not supported in Cowork on mobile. |
| Plugin visible, wrong skill answers | That is a routing result, not an install problem. Record it: [docs/TESTING.md](TESTING.md), Part A. |
| `atk install` fails to authenticate | Re-run `atk auth login m365`; check `atk auth list` shows the work account you expect. |

## Sources

Every page below was read on **18 September 2026**. Microsoft's documentation
changes; if a step here does not match what you see, the Microsoft page wins and
a correction here is welcome.

- Build plugins for Copilot Cowork — package shape, `atk` sideload commands, admin-centre upload path, Information Barriers, mobile limitation, validation rules: <https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugin-development>
- Use plugins with Copilot Cowork — Sources & Skills panel, enabling and disabling, uploading a package from the Customize page, admin-deployed behaviour, removing a plugin, how plugin skills activate: <https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-plugins>
- Manage plugins for Copilot Cowork — admin prerequisites and roles, deploying to users and groups, blocking, org-wide publication approval, tenant distribution, author self-test: <https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-manage-plugins>
- Customize Copilot Cowork — the Customize page, Plugins tab, **Upload plugin**, the Share dialog, the conversation Sources picker: <https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-customize>
- Customize Copilot Cowork — the **Skills** tab, the arrow next to **Add**,
  **Upload skill**, accepted `.md`/`.zip`/`.skill` formats, size and
  file-count limits, the OneDrive save path, same-name re-upload behaviour,
  the trust reminder, the mobile restriction (checked 19 September 2026):
  <https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-customize>
- Use Copilot Cowork — the session side panel: Progress, Input folder, Output folder, **Skills** (chips), Schedule, Permissions: <https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/use-cowork>
- Manage Copilot Cowork for your organization — Cowork in the admin center, usage-based billing as an access control: <https://learn.microsoft.com/en-us/microsoft-365/copilot/cowork/cowork-admin-governance>
- Introduction to Microsoft 365 Agents Toolkit CLI — `atk auth`, `atk install` (`--file-path`, `--scope Personal`/`Shared`), `atk uninstall` (`--mode title-id` / `manifest-id`), `atk launchinfo`: <https://learn.microsoft.com/en-us/microsoftteams/platform/toolkit/microsoft-365-agents-toolkit-cli>
- Activate your Outlook add-in without the Reading Pane — the documented `atk auth login m365` form: <https://learn.microsoft.com/en-us/office/dev/add-ins/outlook/contextless>
- Upload your custom app (Teams) — the Teams sideload path and its prerequisite that custom app uploading is enabled: <https://learn.microsoft.com/en-us/microsoftteams/platform/concepts/deploy-and-publish/apps-upload>
- Manage custom app policies and settings (Teams) — *Allow members to upload custom apps* and the app setup policy that controls uploading: <https://learn.microsoft.com/en-us/microsoftteams/teams-custom-app-policies-and-settings>
- Manage your apps in the Microsoft Teams admin center — allowing, blocking and uploading custom agents and apps: <https://learn.microsoft.com/en-us/microsoftteams/manage-apps>
- Maintain and support your published app — "Don't change your app ID. Increment your app's version number.": <https://learn.microsoft.com/en-us/microsoftteams/platform/concepts/deploy-and-publish/appsource/post-publish/overview>

### Marked unverified in this document

1. Which tenant setting gates the Cowork **Customize** upload control, and
   whether the Teams custom-app-upload policy governs it.
2. What happens when a package is re-uploaded without a version increase.
3. How an `atk`-installed package behaves in the Cowork Customize UI (re-share,
   remove).
4. Whether the upload control is labelled **Upload plugin** or **Add plugin** —
   Microsoft's own pages differ.
5. What Cowork does when two installed plugins contribute skills with the same
   name — relevant only if you install both bundles, which share six skill
   names. Microsoft documents only that plugin skills cannot override built-in
   skills of the same name.
6. Whether the "only upload skills from sources you trust" reminder on a
   single-skill upload looks exactly as Microsoft describes it, and how long
   the OneDrive sync into **Your skills** typically takes.
