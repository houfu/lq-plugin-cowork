"""Write docs/research/harness-capability-research.md from capabilities.yaml.

A standalone, shareable write-up of the capability-to-skill research. Every
level and quote comes from the data; upstream references become permalinks
into the pinned upstream commit. Re-run after changing capabilities.yaml:

    uv run --project tools python tools/scripts/research_doc.py
"""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "src"))
sys.path.insert(0, str(ROOT / "harness-probe" / "scripts"))

from lqcowork.config import load_config  # noqa: E402
from lqcowork.harness import (  # noqa: E402
    aux_markdown,
    column_levels,
    facet_markdown,
    ladder_markdown,
    load_capabilities,
    matrix_markdown,
)
import hprobe_engine as engine  # noqa: E402

config = load_config(ROOT)
caps = load_capabilities(ROOT)
probes = {p.id: p for p in config.probes}
SHA = config.sha
UP = f"https://github.com/LegalQuants/lq-plugin-oss/blob/{SHA}/"
SYM = {"R": "●", "D": "◐", "O": "○"}
GROUPS = ("core", "companion", "litigation", "transactional")
CODES = caps.code_ids
COLUMNS = caps.column_codes()


def upstream_group(name):
    for g in GROUPS:
        if (ROOT / "upstream" / "skills" / g / name).is_dir():
            return g
    return ""


def purpose(name):
    text = (
        ROOT / "upstream/skills" / upstream_group(name) / name / "SKILL.md"
    ).read_text()
    desc = " ".join(yaml.safe_load(text.split("---")[1])["description"].split())
    first = re.split(r"(?<=[.!?])\s", desc)[0]
    return first if len(first) <= 240 else first[:237].rstrip() + "..."


def link_ref(ref):
    """Turn a file:line reference into something a reader outside the repo can use."""
    ref = ref.strip()
    if not ref:
        return ""
    if ref.startswith("upstream/"):
        out = []
        for part in re.split(r";\s*", ref):
            m = re.match(r"upstream/(\S+?)(?::([\d,\- ]+))?$", part.strip())
            if not m:
                out.append(part)
                continue
            path, lines = m.group(1), m.group(2)
            short = path.split("/", 2)[-1] if path.startswith("skills/") else path
            anchor = ""
            if lines:
                first = re.match(r"(\d+)(?:-(\d+))?", lines.strip())
                anchor = f"#L{first.group(1)}" + (
                    f"-L{first.group(2)}" if first.group(2) else ""
                )
            label = f"{short}:{lines.strip()}" if lines else short
            out.append(f"[{label}]({UP}{path}{anchor})")
        return "; ".join(out)
    m = re.match(r"dist/[^/]+/skills/([^/]+)/(\S+?)(?::([\d,\- ]+))?$", ref)
    if m:
        where = f"{m.group(2)} line {m.group(3)}" if m.group(3) else m.group(2)
        return f"Cowork card `{m.group(1)}`, built {where}"
    m = re.match(r"skills/([^/]+)/skill\.yaml \((KI-[\w-]+): (.*)\)$", ref)
    if m:
        return f"Cowork card `{m.group(1)}`, known issue {m.group(2)} (“{m.group(3)}”)"
    return ref


def level_cell(levels, code):
    keys = [k for k in levels if k.split(":")[0] == code]
    parts = []
    for k in sorted(keys, key=lambda k: (":" in k, k)):
        label = SYM[levels[k]]
        if ":" in k:
            label += f" `{k.split(':', 1)[1]}`"
        parts.append(label)
    return " ".join(parts)


def evidence(skill, profile, key):
    code = key.split(":")[0]
    primary = (
        []
        if ":" in key
        else next(c for c in caps.codes if c["id"] == code).get("evidence", [])
    )
    extra = (skill[profile].get("evidence") or {}).get(key) or []
    return list(dict.fromkeys(list(primary) + list(extra)))


def counts(profile):
    out = {}
    for name, skill in caps.skills.items():
        lv = column_levels((skill.get(profile) or {}).get("levels") or {})
        for code, level in lv.items():
            out.setdefault(code, {"R": [], "D": [], "O": []})[level].append(name)
    return out


up_counts = counts("upstream")
cw_counts = counts("cowork")

catalog = json.loads((ROOT / "harness-probe/data/catalog.json").read_text())
baseline = {
    p: engine.build_report(catalog, engine.new_results("none", p), p)["summary"]
    for p in ("upstream", "cowork")
}
no_required = {
    p: sorted(
        n
        for n, s in caps.skills.items()
        if "R" not in (s[p].get("levels") or {}).values()
    )
    for p in ("upstream", "cowork")
}
measured = json.loads((ROOT / "probe-results/claude-code-web.json").read_text())
measured_report = engine.build_report(catalog, measured, "upstream")

L = []
w = L.append

w("# Which harness capabilities each LegalQuants skill needs")
w("")
w(
    "*A capability-to-skill study of the 31 open-source LegalQuants legal skills, and of their adaptations "
    "for Microsoft 365 Copilot Cowork. 2 October 2026.*"
)
w("")
w("## Summary")
w("")
w(
    f"The LegalQuants skills ([LegalQuants/lq-plugin-oss]({UP.replace('/blob/', '/tree/')}), pinned at `{SHA[:7]}`) "
    "are Agent Skills: folders holding a `SKILL.md` with instructions, reference documents, and in many cases "
    "Python scripts, schemas and templates. Whether one runs depends on the **harness** - the agent product that "
    "loads it - and harnesses differ widely in what they can do beyond chatting. This study asks, for each of "
    "the 31 skills: **starting from a chat model that can load skills, what more must the harness provide, "
    "how badly does the skill need it, and what does the skill do without it?**"
)
w("")
w("Each skill was read in full and rated against 19 capability codes, at three levels:")
w("")
w(
    "- **● required**: without it the skill cannot produce its core deliverable, or it stops;"
)
w("- **◐ degradable**: the skill documents a fallback, and says what is lost;")
w("- **○ optional**: an enhancement.")
w("")
w(
    "The same codes were rated twice: for the skills as published upstream, and for the adapted cards an "
    "independent project ships for Microsoft 365 Copilot Cowork, which removes every script."
)
w("")
w("What stands out:")
w("")
w(
    f"- **Tool execution decides most of it.** {len(up_counts['TOOLS']['R'])} of the 31 upstream skills cannot "
    f"run in a chat-only harness that executes no tool calls; {len(up_counts['TOOLS']['D'])} more fall back "
    "without it. Every capability that acts rather than reads (files, folders, scripts, fetch, search, workers) "
    "arrives through a tool call."
)
w(
    f"- **A real filesystem and a script runtime come next.** {len(up_counts['IN']['R'])} skills require reading "
    f"supplied files, {len(up_counts['OUT']['R'])} require handing files back and {len(up_counts['FS']['R'])} require "
    "a real folder structure (a data room, a production, a closing folder). The scripts are almost all "
    "standard-library Python; the version floor is **3.12**, and only a handful need third-party packages "
    "(pypdf, pdfplumber, python-docx, Pillow) or programs (Poppler, LibreOffice)."
)
w(
    "- **MCP is never required.** One skill falls back without its named connector (`lq-ask` and lq-mcp); "
    f"{len(up_counts['MCP']['O'])} more use a connection if one is present and authorised, and five refuse to use "
    "publishing, email, docketing or e-signature connectors at all."
)
w(
    f"- **Few skills need nothing.** {len(no_required['upstream'])} upstream skills have no required capability and "
    "run, degraded where they have degradable ones, on the baseline alone: "
    + ", ".join(f"`{n}`" for n in no_required["upstream"])
    + "."
)
w(
    f"- **The Cowork adaptation trades scripts for host features.** Script execution drops from "
    f"{len(up_counts['EXEC']['R'] + up_counts['EXEC']['D'])} skills to "
    f"{len(cw_counts.get('EXEC', {'R': [], 'D': []})['R'] + cw_counts.get('EXEC', {'R': [], 'D': []})['D'])}; "
    "the host's own Word, Excel and PDF handling, web search and organisational search carry what is left. "
    f"{len(no_required['cowork'])} Cowork cards need nothing beyond the baseline."
)
w(
    "- **Capability is not enough on its own.** Several skills also need their folder present on disk with "
    "sibling skills installed, a call-by-name invocation, a choice of model per worker, or provider-specific "
    "layouts; and any tool that touches client material must stay inside an approved data boundary."
)
w("")
w(
    "A companion tool, the `harness-probe` skill, turns this table into a measurement: it runs 27 probes on a "
    "real harness and reports which skills run as intended, run on a fallback, cannot run, or are untested "
    "([section 10](#10-measuring-a-real-harness))."
)
w("")

w("## Contents")
w("")
for i, t in enumerate(
    [
        "Question and baseline",
        "Method",
        "The capability codes",
        "Results: the upstream skills",
        "Results: the Cowork cards",
        "Capability by capability",
        "Skill by skill",
        "Requirements that are not a single capability",
        "Supplying capabilities through tools and MCP",
        "Measuring a real harness",
        "Build-out order for a harness",
        "Limitations",
    ],
    start=1,
):
    anchor = re.sub(r"[^a-z0-9 -]", "", f"{i}. {t}".lower()).replace(" ", "-")
    w(f"{i}. [{t}](#{anchor})")
w("")

w("## 1. Question and baseline")
w("")
w(
    "The baseline harness is assumed to have exactly two things, so neither is listed per skill:"
)
w("")
w(
    '- **Multi-turn chat with the user**, including every approval gate, "stop and wait" checkpoint and '
    "short intake interview the skills use."
)
w(
    "- **Agent Skills support**: it discovers skills by their description, loads `SKILL.md`, and loads the "
    "skill's own text files (references, schemas, prompts) into context on demand."
)
w("")
w(
    "It returns text only: no tool calls, no files, no network. Everything else is a capability the harness "
    "must add. A reliable clock is not rated, because every skill that needs a date accepts one from the user "
    "or gets it from a script."
)
w("")

w("## 2. Method")
w("")
w(
    "1. **First audit.** Six reviewer agents each read one slice of the upstream skills in full - every "
    "`SKILL.md`, reference, schema and script, and every script import - against a fixed list of capability "
    'codes. Each level was taken from the skill\'s own language ("fallback", "if the host...", "tool '
    'cascade", "if unavailable") and recorded with a file and line.'
)
w(
    "2. **Spot checks.** The heaviest claims were checked across the whole tree: third-party imports appear only "
    "in read-redline, sigpack, closing-bible, playbook-builder, playbook-review and legaldesign's optional "
    "`exhibit.py`; network calls only in regulatory's `fetch_source.py` and legalquants' `evidence.py`; the "
    "programs invoked are exactly Poppler, LibreOffice, tesseract, Chromium, Inkscape, `rsvg-convert` and `codex`."
)
w(
    "3. **Second audit.** Four reviewer agents rated the adapted Cowork cards as built, rated three auxiliary "
    "codes for both profiles, quoted the skill's own fallback wording for every degradable level, and disputed "
    "the first audit where the text disagreed. Accepted corrections: regulatory's network and filesystem needs "
    'are degradable (it answers in a labelled "provisional and unverified" form); definition-check\'s '
    "filesystem and file input are degradable (it has a reduced-assurance text-only profile); playbook-review's "
    "persistence is degradable (a playbook can be supplied by path); four skills rate the HTML hand-back; and "
    "nine skills, not six, are explicit-invocation only."
)
w(
    "4. **Derivation.** The TOOLS level is not audited separately: it is the strongest level among the codes "
    "that act through a tool call. A **facet** (for example `OUT:pdf-assemble`) narrows a code to the one thing a "
    "particular probe tests, so that a skill needing only to write a text file is not judged on PDF assembly."
)
w(
    "5. **Probe ties.** Every code and facet is tied to the probe that measures it (section 10), and every "
    "known issue on a Cowork card that cites a probe was checked to rate something that probe measures."
)
w("")
w(
    "No skill was executed during the audits. The levels describe what each skill says about itself; what a "
    "particular harness actually does is measured separately."
)
w("")

w("## 3. The capability codes")
w("")
w("| Code | Capability | What counts |")
w("| --- | --- | --- |")
extra_note = {
    "TOOLS": "Derived: the strongest of the action codes (everything except IN, HTML and INVOKE).",
    "IN": "Needs no tool when the harness places attachments in context.",
    "NET": "Skills that hash what they fetch (regulatory) also need the raw bytes, not a model's summary.",
    "EXEC": "Python 3.8 to 3.12 depending on the skill; almost all standard library.",
    "MCP": "Includes equivalent connector mechanisms (OpenAPI tools, Copilot agent connectors, claude.ai connectors).",
    "HASH": "Auxiliary. Only where no bundled script does the hashing for the skill.",
    "SKILLDIR": "Auxiliary. Scripts import siblings, read ../assets, and call other skills' scripts by path.",
    "INVOKE": "Auxiliary. `disable-model-invocation: true` or `allow_implicit_invocation: false`.",
}
for code in caps.codes:
    w(
        f"| **{code['id']}** | {code['name']} | {code['summary']} {extra_note.get(code['id'], '')} |"
    )
w("")


def matrix_section(profile, title, intro):
    w(title)
    w("")
    w(intro)
    w("")
    w(matrix_markdown(caps, profile))
    w("")
    w(
        "Levels: ● required, ◐ degradable, ○ optional, blank not used. A cell shows the strongest level of a code "
        "and its facets. Auxiliary codes and facets:"
    )
    w("")
    w(aux_markdown(caps, profile))
    w("")
    w(facet_markdown(caps, profile))
    w("")


matrix_section(
    "upstream",
    "## 4. Results: the upstream skills",
    "The skills as published upstream, scripts included.",
)
matrix_section(
    "cowork",
    "## 5. Results: the Cowork cards",
    "The adapted cards as built for Microsoft 365 Copilot Cowork. They ship no scripts and call no external "
    "service; they rely on the host's own document handling, web search and organisational search instead.",
)

w("## 6. Capability by capability")
w("")
w(
    "The same data read the other way: for each capability, which skills need it. Upstream first; the Cowork "
    "count follows in brackets."
)
w("")
for code in CODES:
    u = up_counts.get(code, {"R": [], "D": [], "O": []})
    c = cw_counts.get(code, {"R": [], "D": [], "O": []})
    name = next(x["name"] for x in caps.codes if x["id"] == code)
    w(
        f"**{code} - {name}.** "
        f"● {len(u['R'])} ({len(c['R'])}) · ◐ {len(u['D'])} ({len(c['D'])}) · ○ {len(u['O'])} ({len(c['O'])})"
    )
    w("")
    for lv, label in (("R", "Required"), ("D", "Degradable"), ("O", "Optional")):
        if u[lv]:
            w(f"- {label} upstream: " + ", ".join(f"`{n}`" for n in sorted(u[lv])))
    w("")

w("## 7. Skill by skill")
w("")
w(
    "Each entry gives the skill's purpose in its own words, its levels under both profiles with the probes "
    "that decide each one, the exact runtime its scripts need, and - for every degradable level - the skill's "
    "own words for what happens without it. Upstream references link to the pinned commit."
)
w("")
for group in GROUPS:
    names = sorted(n for n, s in caps.skills.items() if s.get("group") == group)
    w(f"### {group.capitalize()}")
    w("")
    for name in names:
        skill = caps.skills[name]
        up, cw = skill["upstream"], skill["cowork"]
        w(f"#### {name}")
        w("")
        w(f"*{purpose(name)}*")
        w("")
        keys = []
        for prof in (up, cw):
            for k in prof.get("levels") or {}:
                if k not in keys:
                    keys.append(k)
        order = {c: i for i, c in enumerate(CODES)}
        keys.sort(key=lambda k: (order.get(k.split(":")[0], 99), k))
        if keys:
            w("| Capability | Upstream | Cowork card | Decided by |")
            w("| --- | --- | --- | --- |")
            for k in keys:
                ul = (up.get("levels") or {}).get(k)
                cl = (cw.get("levels") or {}).get(k)
                ev = (
                    evidence(skill, "upstream", k)
                    if ul
                    else evidence(skill, "cowork", k)
                )
                if ul and cl:
                    ev = list(
                        dict.fromkeys(
                            evidence(skill, "upstream", k)
                            + evidence(skill, "cowork", k)
                        )
                    )
                label = f"`{k}`" if ":" in k else k
                w(
                    f"| {label} | {SYM.get(ul, '')} | {SYM.get(cl, '')} | {', '.join(ev)} |"
                )
            w("")
        else:
            w("Needs nothing beyond the baseline under either profile.")
            w("")
        needs = up.get("needs") or {}
        if needs:
            bits = []
            if needs.get("python"):
                bits.append(f"Python ≥{needs['python']}")
            if needs.get("packages"):
                bits.append(
                    "packages " + ", ".join(f"`{p}`" for p in needs["packages"])
                )
            if needs.get("binaries"):
                bits.append(
                    "programs " + ", ".join(f"`{p}`" for p in needs["binaries"])
                )
            if needs.get("binaries_any"):
                bits.append(
                    "one of " + ", ".join(f"`{p}`" for p in needs["binaries_any"])
                )
            w("**Script runtime (upstream):** " + "; ".join(bits) + ".")
            w("")
        for prof_name, prof in (("upstream", up), ("Cowork card", cw)):
            fb = prof.get("fallbacks") or {}
            if fb:
                w(f"**Without its degradable capabilities ({prof_name}):**")
                w("")
                for k in sorted(fb, key=lambda k: (order.get(k.split(":")[0], 99), k)):
                    text = fb[k].get("text", "").strip()
                    ref = link_ref(fb[k].get("ref", ""))
                    w(f"- **{k}**: “{text}”" + (f" ({ref})" if ref else ""))
                w("")
        if cw.get("notes"):
            w(f"**What the Cowork adaptation changed:** {cw['notes']}")
            w("")

w("## 8. Requirements that are not a single capability")
w("")
w(
    "- **The skill folder must exist on disk, with its siblings.** Scripts import sibling modules and read "
    "`../assets` and `../schemas`. Several call another skill's scripts by relative path: every companion skill "
    "calls `legalquants/scripts/onboarding.py` and writes its store through `lq-reflect/scripts/profile_store.py`; "
    "legalquants, lq-reflect and lq-mirror call `lq-start/scripts/catalog.py`; conform calls "
    "`definition-check/scripts/normalize_terms.py`. Loading `SKILL.md` as text is not enough (code SKILLDIR)."
)
w(
    "- **Skill-to-skill data.** conform needs definition-check ledgers (schema 0.14.0); playbook-review needs a "
    "playbook-builder registry; closing-bible optionally reads the sigpack ledger; legaldesign optionally reads "
    "cite-check output; organize-case-docs hands off to docreview."
)
w(
    "- **Calling a skill by name.** Nine upstream skills are explicit-invocation only (code INVOKE): "
    + ", ".join(
        f"`{n}`"
        for n in sorted(
            n
            for n, s in caps.skills.items()
            if (s["upstream"].get("levels") or {}).get("INVOKE")
        )
    )
    + "."
)
w(
    "- **A model per worker.** docreview and diligence require one fixed, higher-capability model at medium "
    "effort or above for their finding workers; the packaged worker runners pin a model. A harness whose "
    "subagents cannot choose a model fails these contracts."
)
w(
    "- **Provider-specific assumptions.** `lq-start` reads `.claude-plugin` and `.codex-plugin` layouts and "
    "`$CODEX_HOME`; lq-reflect parses Codex and Claude Code transcript files; the worker runners shell out to "
    "`codex exec`; wiki's automatic retrieval expects Codex lifecycle hooks. Another harness needs equivalents or "
    "falls back."
)
w(
    "- **Python version.** The floor across the set is 3.12: definition-check, conform and closing-bible gate on "
    "it and pressuretest declares it; most of the rest need 3.11."
)
w("")

w("## 9. Supplying capabilities through tools and MCP")
w("")
w(
    "A harness can provide a capability natively or through a tool attached over MCP; the skills accept "
    "either. Most describe a *tool cascade* - bundled scripts first, then host-native tools, then a service the "
    "user or firm selects. Three conditions in the skills' own text decide whether a given tool counts:"
)
w("")
w(
    '1. **It must actually perform the operation.** "Do not claim SHA-256 identity ... automated count '
    'reconciliation unless a host-native tool actually performed it." A tool that summarises a page or '
    "describes a file does not count; regulatory rejects a fetch tool's rendering as \"a model's summary of the "
    'text, not the text".'
)
w(
    '2. **Client material stays inside an approved boundary.** Remote processing only where the "connector, '
    'network, DMS, or hosted-service data boundary is already authorized". cite-check sends only citation '
    'metadata to public services; client-update never uploads matter material "merely to format or summarize '
    'it"; wiki\'s position notes "never leave the machine". For the matter skills, any tool touching documents '
    "must run locally or inside the firm's own approved system."
)
w(
    "3. **Scripts only see a filesystem.** A code-execution tool counts only if the skill folders and the user's "
    "workspace are both inside it."
)
w("")
w(
    "Connectors the skills name: **lq-mcp** (lq-ask, degradable), **CourtListener MCP** (cite-check, optional, "
    'citation metadata only), and "network/connectors/MCP/DMS" integrations (definition-check and conform, '
    "optional, already-authorised only). About a dozen more accept a firm-selected DMS, docket, e-discovery or "
    "legal-research system. my-lq-moment, correspondence, sigpack, playbook-review and diligence refuse to "
    "publish, send, docket or run e-signature even when such a connector exists."
)
w("")

w("## 10. Measuring a real harness")
w("")
w(
    "The levels say what each skill needs; a probe measures whether a harness has it. Each code has primary "
    "probes, and a skill can add probes for a facet:"
)
w("")
w("| Code | Decided by | Probe question |")
w("| --- | --- | --- |")
for code in caps.codes:
    ev = code.get("evidence") or []
    qs = "; ".join(probes[p].title for p in ev if p in probes)
    w(f"| {code['id']} | {', '.join(ev)} | {qs} |")
facet_probes = sorted(
    {
        p
        for s in caps.skills.values()
        for prof in ("upstream", "cowork")
        for k, v in (s[prof].get("evidence") or {}).items()
        for p in v
        if p not in {e for c in caps.codes for e in c.get("evidence", [])}
    },
    key=engine.probe_sort_key,
)
w("")
w(
    "P1 to P14 were first written for Microsoft 365 Copilot Cowork and keep their original titles; the "
    "harness-probe skill runs every one of them on any harness."
)
w("")
w(
    "Facet and extra probes: "
    + "; ".join(f"**{p}** {probes[p].title}" for p in facet_probes)
    + "."
)
w("")
w("A skill's verdict on a harness follows from the probe results:")
w("")
w("| Verdict | Rule |")
w("| --- | --- |")
w(
    "| Runs as intended | every required and every degradable capability has a passing probe |"
)
w(
    "| Runs on a fallback | every required capability passes; at least one degradable one failed or is unprobed |"
)
w("| Cannot run | at least one required capability failed |")
w("| Untested | no required capability failed, but at least one has no result yet |")
w("")
w(
    f"Before any probe has run, the upstream skills stand at {baseline['upstream']['as-intended']} as intended, "
    f"{baseline['upstream']['fallback']} on a fallback and {baseline['upstream']['untested']} untested; the Cowork "
    f"cards at {baseline['cowork']['as-intended']}, {baseline['cowork']['fallback']} and {baseline['cowork']['untested']}."
)
w("")
s = measured_report["summary"]
w(
    f"**One measured harness.** Claude Code on the web, probing its own cloud container on 1 October 2026: "
    f"{s['as-intended']} skills run as intended, {s['fallback']} on a fallback, {s['cannot-run']} cannot run and "
    f"{s['untested']} remain untested. The blocks were concrete: the container's default `python3` is 3.11, below "
    "the 3.12 floor of closing-bible and conform; its egress allow-list blocks the public pages lq-connect reads; "
    "and the PDF libraries read-redline expects are absent, so it runs on its documented fallback. The untested "
    "skills wait on probes that need a person (opening a page, calling a skill by name, judging a quotation) or a "
    "second session."
)
w("")
w(
    "The probe skill is `harness-probe` in the "
    "[houfu/lq-plugin-cowork](https://github.com/houfu/lq-plugin-cowork) repository; the levels in this study "
    "are its `capabilities.yaml`."
)
w("")

w("## 11. Build-out order for a harness")
w("")
w(
    "If a harness were built up one capability group at a time, this is where each skill would start to run "
    "(every ● met) and run as intended (every ● and ◐ met)."
)
w("")
w("**Upstream skills**")
w("")
w(ladder_markdown(caps, "upstream"))
w("")
w("**Cowork cards**")
w("")
w(ladder_markdown(caps, "cowork"))
w("")

w("## 12. Limitations")
w("")
w(
    "- Levels come from reading the skills, not running them. A skill can promise a fallback it handles badly, "
    "or need something its text does not mention; only a probe run on a real harness shows that."
)
w(
    "- The audits were done by AI reviewer agents with file-and-line evidence, then spot-checked and "
    "cross-audited. A level is a judgement where a skill's text is ambiguous; those calls are recorded with the "
    "quote they rest on."
)
w(
    "- The upstream skills change. This study is pinned to commit "
    f"[`{SHA[:7]}`]({UP.replace('/blob/', '/tree/')}); a later upstream version may need different levels."
)
w(
    "- The Cowork profile describes cards as built by one independent adaptation project at version "
    f"{config.version}; it is not an official LegalQuants or Microsoft statement."
)
w("- LegalQuants skills are a workflow aid, not legal advice.")
w("")

w("---")
w("")
w(
    "*Generated from `capabilities.yaml` and `probes.yaml` in "
    "[houfu/lq-plugin-cowork](https://github.com/houfu/lq-plugin-cowork) by "
    "`tools/scripts/research_doc.py`. The interactive version of these tables, with every probe and the "
    "recorded harness verdicts, is the project site's Probes and Verdicts pages.*"
)

out = ROOT / "docs/research/harness-capability-research.md"
out.write_text("\n".join(L).rstrip() + "\n", encoding="utf-8")
print(out, len(L), "lines")
