"""Render the capability-by-skill matrix as a shareable PNG.

    uv run --project tools python tools/scripts/capability_matrix.py [--profile upstream|cowork] [--out PATH]

Reads capabilities.yaml, writes an HTML page, and screenshots it with
headless Chromium. Columns are sorted by how many skills require the
capability, so the left-most columns are the ones that unblock the most
skills; the bars above them count skills unblocked (required) and improved
(degradable).
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "src"))

from lqcowork.harness import column_levels, load_capabilities  # noqa: E402

GROUPS = ("core", "companion", "litigation", "transactional")
TITLES = {
    "upstream": "the 31 LegalQuants skills",
    "cowork": "the 31 LegalQuants skills, as adapted for Copilot Cowork",
}
CELL_W, CELL_H, NAME_W, BAR_H = 66, 26, 200, 120
# Ordinal ramp (one hue, validated with the dataviz validator --ordinal).
COLOURS = {"R": "#184f95", "D": "#3987e5", "O": "#86b6ef"}
GLYPH = {
    "R": '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">'
    '<circle cx="7" cy="7" r="5.5" fill="currentColor"/></svg>',
    "D": '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">'
    '<circle cx="7" cy="7" r="5" fill="none" stroke="currentColor" stroke-width="1.6"/>'
    '<path d="M7 2 A5 5 0 0 0 7 12 Z" fill="currentColor"/></svg>',
    "O": '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">'
    '<circle cx="7" cy="7" r="4.8" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
}
INK = {"R": "#ffffff", "D": "#ffffff", "O": "#0b0b0b"}


def build(profile: str) -> tuple[str, int, int]:
    caps = load_capabilities(ROOT)
    labels = {c["id"]: c.get("label") or c["name"] for c in caps.codes}
    codes = list(caps.column_codes())
    rows = {
        name: column_levels((skill.get(profile) or {}).get("levels") or {})
        for name, skill in caps.skills.items()
    }
    req = {c: sum(1 for r in rows.values() if r.get(c) == "R") for c in codes}
    deg = {c: sum(1 for r in rows.values() if r.get(c) == "D") for c in codes}
    codes.sort(key=lambda c: (-req[c], -deg[c], c))
    peak = max(req[c] + deg[c] for c in codes) or 1
    chat_only = {n for n, r in rows.items() if "R" not in r.values()}

    def bar(code: str) -> str:
        r_h = round(BAR_H * req[code] / peak)
        d_h = round(BAR_H * deg[code] / peak)
        parts = [f'<div class="num">{req[code]}<span>+{deg[code]}</span></div>']
        if d_h:
            parts.append(f'<div class="seg deg" style="height:{d_h}px"></div>')
        if r_h:
            parts.append(f'<div class="seg req" style="height:{r_h}px"></div>')
        return f'<div class="bar">{"".join(parts)}</div>'

    head = "".join(
        f'<th class="cap"><div class="barwrap">{bar(c)}</div>'
        f'<div class="label">{html.escape(labels[c])}</div></th>'
        for c in codes
    )
    body = []
    groups = {}
    for name, skill in caps.skills.items():
        groups.setdefault(skill.get("group", ""), []).append(name)
    n_rows = 0
    for group in [g for g in GROUPS if g in groups]:
        body.append(
            f'<tr class="group"><th colspan="{len(codes) + 1}">{group.capitalize()}</th></tr>'
        )
        n_rows += 1
        for name in sorted(groups[group]):
            levels = rows[name]
            mark = (
                '<span class="chat" title="runs on plain chat">✓</span>'
                if name in chat_only
                else ""
            )
            cells = []
            for c in codes:
                lv = levels.get(c)
                if lv:
                    cells.append(
                        f'<td><span class="cell" style="background:{COLOURS[lv]};'
                        f'color:{INK[lv]}">{GLYPH[lv]}</span></td>'
                    )
                else:
                    cells.append('<td><span class="cell empty"></span></td>')
            body.append(f'<tr><th class="name">{name}{mark}</th>{"".join(cells)}</tr>')
            n_rows += 1

    width = NAME_W + CELL_W * len(codes) + 64
    height = 300 + BAR_H + 70 + n_rows * (CELL_H + 4) + 150
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Capability matrix</title>
<style>
:root {{
  --surface: #fcfcfb; --text-primary: #0b0b0b; --text-secondary: #52514e;
  --text-muted: #77756f; --rule: #e6e4de; --empty: #f0efec;
  --req: {COLOURS['R']}; --deg: {COLOURS['D']}; --opt: {COLOURS['O']};
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; background: var(--surface); }}
body {{ width: {width}px; padding: 36px 32px 28px; color: var(--text-primary);
  font: 14px/1.4 "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif; }}
h1 {{ font-size: 26px; margin: 0 0 6px; letter-spacing: -0.01em; }}
.sub {{ color: var(--text-secondary); font-size: 15px; margin: 0 0 18px; max-width: 1000px; }}
.legend {{ display: flex; gap: 22px; flex-wrap: wrap; margin: 0 0 22px; font-size: 13.5px;
  color: var(--text-secondary); }}
.legend b {{ color: var(--text-primary); font-weight: 600; }}
.key {{ display: inline-flex; align-items: center; gap: 8px; }}
.swatch {{ width: 24px; height: 22px; border-radius: 4px; display: inline-flex;
  align-items: center; justify-content: center; font-size: 12px; }}
table {{ border-collapse: separate; border-spacing: 0 4px; }}
th.cap {{ width: {CELL_W}px; vertical-align: bottom; padding: 0 2px 8px; font-weight: 500; }}
.barwrap {{ height: {BAR_H + 26}px; display: flex; align-items: flex-end; justify-content: center; }}
.bar {{ display: flex; flex-direction: column; align-items: center; gap: 2px; width: 30px; }}
.seg {{ width: 30px; }}
.seg.req {{ background: var(--req); border-radius: 0; }}
.seg.deg {{ background: var(--deg); border-radius: 4px 4px 0 0; }}
.bar .seg:first-of-type {{ border-radius: 4px 4px 0 0; }}
.num {{ font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 3px;
  white-space: nowrap; font-variant-numeric: tabular-nums; }}
.num span {{ font-weight: 400; color: var(--text-muted); font-size: 11.5px; margin-left: 1px; }}
.label {{ font-size: 12px; line-height: 1.25; color: var(--text-primary); text-align: center;
  height: 46px; display: flex; align-items: flex-start; justify-content: center;
  border-top: 1px solid var(--rule); padding-top: 7px; }}
th.corner {{ width: {NAME_W}px; text-align: left; vertical-align: bottom; padding: 0 12px 8px 0;
  font-size: 12px; font-weight: 400; color: var(--text-secondary); }}
th.name {{ width: {NAME_W}px; text-align: left; font-weight: 500; font-size: 13.5px;
  padding-right: 12px; white-space: nowrap; }}
.chat {{ font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-left: 6px; }}
tbody tr:not(.group) {{ height: {CELL_H}px; }}
tr.group th {{ text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: .08em;
  color: var(--text-secondary); padding: 12px 0 2px; border-bottom: 1px solid var(--rule); }}
td {{ padding: 0; text-align: center; }}
.cell {{ display: inline-flex; align-items: center; justify-content: center; width: {CELL_W - 8}px;
  height: {CELL_H}px; border-radius: 4px; font-size: 13px; }}
.cell.empty {{ background: var(--empty); }}
.foot {{ margin-top: 20px; color: var(--text-secondary); font-size: 13px; max-width: 1080px; }}
.foot p {{ margin: 0 0 6px; }}
.ask {{ margin: 0 0 16px; padding: 12px 16px; border: 1px solid var(--rule); border-radius: 8px;
  background: #ffffff; font-size: 14.5px; max-width: 1000px; }}
</style></head><body>
<h1>Which capability should we build next?</h1>
<p class="sub">What an AI harness must be able to do to run {TITLES[profile]}, starting from a plain chat
model that can load skills. Capabilities are sorted left to right by how many skills cannot run without them.</p>
<div class="ask"><b>How to choose:</b> the bar above each capability counts the skills it <b>unblocks</b>
(dark: they cannot run without it) and, after the +, the skills it <b>upgrades</b> from a weaker fallback
(light). Read down a column to see exactly which skills move.</div>
<div class="legend">
  <span class="key"><span class="swatch" style="background:var(--req);color:#fff">{GLYPH['R']}</span><b>Required</b> &nbsp;the skill cannot run without it</span>
  <span class="key"><span class="swatch" style="background:var(--deg);color:#fff">{GLYPH['D']}</span><b>Degradable</b> &nbsp;it runs, on a weaker documented fallback</span>
  <span class="key"><span class="swatch" style="background:var(--opt);color:#0b0b0b">{GLYPH['O']}</span><b>Optional</b> &nbsp;a nice-to-have</span>
  <span class="key"><span class="swatch" style="background:var(--empty)"></span>not used</span>
  <span class="key"><b>✓</b>&nbsp; the skill already runs on plain chat</span>
</div>
<table>
<thead><tr><th class="corner">Skill</th>{head}</tr></thead>
<tbody>{"".join(body)}</tbody>
</table>
<div class="foot">
<p>{len(chat_only)} skills (marked ✓) need nothing beyond plain chat. Every other capability arrives through tool calling, which is why it comes first.</p>
<p>Source: each skill's own text, read in full and cross-checked by a second audit; levels in <i>capabilities.yaml</i>,
github.com/houfu/lq-plugin-cowork. Skills: github.com/LegalQuants/lq-plugin-oss at fa5a668.</p>
</div>
<script>document.body.setAttribute("data-h",
  String(Math.ceil(document.documentElement.getBoundingClientRect().height)));</script>
</body></html>
"""
    return doc, width, height


def chromium() -> str:
    for candidate in sorted(
        Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome")
    ):
        return str(candidate)
    for name in ("chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit("no Chromium found to take the screenshot")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profile", choices=("upstream", "cowork"), default="upstream")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    out = Path(args.out or ROOT / f"docs/research/capability-matrix-{args.profile}.png")
    doc, width, height = build(args.profile)
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "matrix.html"
        page.write_text(doc, encoding="utf-8")
        dom = subprocess.run(
            [
                chromium(),
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                f"--window-size={width + 64},1000",
                "--dump-dom",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        measured = re.search(r'data-h="(\d+)"', dom)
        if measured:
            height = int(measured.group(1)) + 48
        subprocess.run(
            [
                chromium(),
                "--headless",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=2",
                f"--window-size={width + 64},{height}",
                f"--screenshot={out}",
                page.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
