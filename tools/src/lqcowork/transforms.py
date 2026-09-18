"""Pure text transforms: frontmatter, waivers, tokens, replacements, sections.

Nothing here touches the filesystem, which keeps the rules easy to unit test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import yaml

# --------------------------------------------------------------------------
# gitignore-style path matching
# --------------------------------------------------------------------------

_GLOB_CACHE: dict[str, re.Pattern[str]] = {}


def _translate(pattern: str) -> re.Pattern[str]:
    """Translate one gitignore-ish glob into an anchored regex."""
    cached = _GLOB_CACHE.get(pattern)
    if cached is not None:
        return cached
    out: list[str] = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif char == "*":
            out.append("[^/]*")
            i += 1
        elif char == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(char))
            i += 1
    compiled = re.compile("".join(out))
    _GLOB_CACHE[pattern] = compiled
    return compiled


def path_matches(rel_path: str, patterns: Iterable[str]) -> bool:
    """True when ``rel_path`` (posix, relative) is covered by any pattern.

    A pattern without a slash matches a name at any depth (gitignore
    semantics); a pattern with a slash is anchored at the skill folder. A
    directory match covers everything beneath it.
    """
    rel_path = rel_path.strip("/")
    if not rel_path:
        return False
    parts = rel_path.split("/")
    prefixes = ["/".join(parts[: i + 1]) for i in range(len(parts))]
    for pattern in patterns:
        stripped = pattern.rstrip("/")
        if not stripped:
            continue
        regex = _translate(stripped)
        if any(regex.fullmatch(prefix) for prefix in prefixes):
            return True
        if "/" not in stripped and any(regex.fullmatch(part) for part in parts):
            return True
    return False


def glob_files(names: Sequence[str], patterns: Iterable[str]) -> list[str]:
    """Select posix-relative ``names`` matching any of ``patterns``."""
    out: list[str] = []
    for name in names:
        for pattern in patterns:
            if _translate(pattern).fullmatch(name):
                out.append(name)
                break
    return out


# --------------------------------------------------------------------------
# frontmatter
# --------------------------------------------------------------------------


class TransformError(Exception):
    """A transform could not be applied (bad frontmatter, bad section file)."""


@dataclass
class Document:
    """A SKILL.md split into frontmatter mapping and body."""

    frontmatter: dict[str, Any]
    body: str


def split_document(text: str) -> tuple[str | None, str]:
    """Return ``(raw_frontmatter, body)``; raw is None when there is none."""
    normalised = text.replace("\r\n", "\n")
    if not normalised.startswith("---\n"):
        return None, normalised
    lines = normalised.split("\n")
    for index in range(1, len(lines)):
        if lines[index].rstrip() == "---":
            raw = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return raw, body
    return None, normalised


def parse_document(text: str) -> Document:
    """Parse a SKILL.md into frontmatter + body, raising on malformed YAML."""
    raw, body = split_document(text)
    if raw is None:
        raise TransformError("no YAML frontmatter between '---' delimiters")
    try:
        data = yaml.safe_load(raw) if raw.strip() else {}
    except yaml.YAMLError as exc:
        raise TransformError(f"invalid YAML frontmatter: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise TransformError("frontmatter is not a mapping")
    return Document(frontmatter=data, body=body)


class _Literal(str):
    """A string that must be emitted as a ``|`` block scalar."""


class _FrontmatterDumper(yaml.SafeDumper):
    pass


def normalise_block(text: str) -> str:
    """Make ``text`` safe for, and stable under, YAML literal block style.

    PyYAML refuses literal style for a string whose lines end in whitespace and
    silently drops those spaces when it does emit one, so a round trip is only
    exact if the value has already been normalised. The stamp step calls this
    before storing the description, so what is in memory is what is on disk.

    Each line is stripped at both ends: a card whose later sentences sit deeper
    than the opening of its YAML block would otherwise ship those extra spaces
    inside the description string.
    """
    normalised = text.replace("\r\n", "\n").replace("\t", "    ")
    return "\n".join(line.strip() for line in normalised.split("\n")).strip("\n")


def _represent_literal(dumper: yaml.Dumper, data: _Literal) -> Any:
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")


def _represent_str(dumper: yaml.Dumper, data: str) -> Any:
    if "\n" in data:
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", normalise_block(data), style="|"
        )
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_FrontmatterDumper.add_representer(_Literal, _represent_literal)
_FrontmatterDumper.add_representer(str, _represent_str)


def order_frontmatter(data: dict[str, Any]) -> dict[str, Any]:
    """``name`` first, ``description`` second, then the original order."""
    ordered: dict[str, Any] = {}
    for key in ("name", "description"):
        if key in data:
            ordered[key] = data[key]
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def dump_frontmatter(data: dict[str, Any]) -> str:
    """Serialise frontmatter, description as a literal block scalar."""
    ordered = order_frontmatter(data)
    payload = dict(ordered)
    if isinstance(payload.get("description"), str):
        payload["description"] = _Literal(normalise_block(payload["description"]))
    text = yaml.dump(
        payload,
        Dumper=_FrontmatterDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=10_000,
    )
    return text


def render_document(document: Document) -> str:
    """Rebuild a SKILL.md from frontmatter + body."""
    body = document.body
    if body and not body.startswith("\n"):
        body = "\n" + body
    return "---\n" + dump_frontmatter(document.frontmatter) + "---" + body


# --------------------------------------------------------------------------
# waivers
# --------------------------------------------------------------------------

_WAIVER_LINE_RE = re.compile(
    r"(?m)^[ \t]*<!--\s*vendor-neutral-waiver:.*?-->[ \t]*\n?", re.DOTALL
)
_WAIVER_INLINE_RE = re.compile(
    r"(?P<lead>[ \t]*)<!--\s*vendor-neutral-waiver:.*?-->(?P<trail>[ \t]*)",
    re.DOTALL,
)


def _close_waiver_gap(match: re.Match[str]) -> str:
    """Leave one space where a mid-line comment was, and none at an edge."""
    whole = match.string
    at_line_start = match.start() == 0 or whole[match.start() - 1] == "\n"
    at_line_end = match.end() >= len(whole) or whole[match.end()] == "\n"
    if at_line_start or at_line_end:
        return ""
    return " " if (match.group("lead") or match.group("trail")) else ""


def strip_waivers(text: str) -> str:
    """Remove vendor-neutral-waiver comments; drop the line when alone."""
    text = _WAIVER_LINE_RE.sub("", text)
    return _WAIVER_INLINE_RE.sub(_close_waiver_gap, text)


# --------------------------------------------------------------------------
# skill-name tokens
# --------------------------------------------------------------------------

# A bare `/name` must be followed by whitespace, punctuation or end of line —
# never by `/`, which would make it a path.
_FOLLOW = r"(?=[\s)\]},.;:!?\"'`*]|$)"
# ...and preceded by start of input, whitespace, `(` or a quote.
_PRECEDE = r"(?<![^\s(\"'])"
# `$name` takes the same left boundary, plus a backtick: `$lq-apply` is a
# token in code style, not a literal a reader would type.
_PRECEDE_DOLLAR = r"(?<![^\s(\"'`])"


def rewrite_tokens(text: str, names: Sequence[str]) -> str:
    """Rewrite ``$name`` / ``/name`` invocation grammar to plain names.

    ``names`` must be ordered longest first so that a shorter skill name
    cannot shadow a longer one.
    """
    for name in names:
        esc = re.escape(name)
        text = re.sub(rf"`/{esc}(?![A-Za-z0-9-])[^`\n]*`", f"`{name}`", text)
        text = re.sub(rf"(?m){_PRECEDE}/{esc}(?![A-Za-z0-9-]){_FOLLOW}", name, text)
        text = re.sub(rf"(?m){_PRECEDE_DOLLAR}\${esc}(?![A-Za-z0-9_-])", name, text)
    return text


def surviving_tokens(text: str, names: Sequence[str]) -> list[str]:
    """Tokens the rewrite would still consider live (for LQC-W002)."""
    found: list[str] = []
    for name in names:
        esc = re.escape(name)
        if re.search(rf"(?m){_PRECEDE_DOLLAR}\${esc}(?![A-Za-z0-9_-])", text):
            found.append(f"${name}")
        if re.search(rf"`/{esc}(?![A-Za-z0-9-])[^`\n]*`", text):
            found.append(f"`/{name}`")
    return sorted(set(found))


# --------------------------------------------------------------------------
# literal replacement
# --------------------------------------------------------------------------


def count_occurrences(text: str, needle: str) -> int:
    return text.count(needle)


def replace_literal(text: str, needle: str, value: str) -> str:
    return text.replace(needle, value)


# --------------------------------------------------------------------------
# section overlays
# --------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_HEADING_RE = re.compile(r"^(#{1,6})\s")


def _heading_levels(lines: Sequence[str]) -> list[int | None]:
    """Heading level per line; None for non-headings and fenced content."""
    levels: list[int | None] = []
    fence: str | None = None
    for line in lines:
        match = _FENCE_RE.match(line)
        if match:
            token = match.group(1)[0]
            if fence is None:
                fence = token
                levels.append(None)
                continue
            if token == fence:
                fence = None
            levels.append(None)
            continue
        if fence is not None:
            levels.append(None)
            continue
        heading = _HEADING_RE.match(line)
        levels.append(len(heading.group(1)) if heading else None)
    return levels


def find_section(text: str, heading: str) -> tuple[int, int] | None:
    """Return the ``[start, end)`` line span of the section under ``heading``."""
    lines = text.split("\n")
    levels = _heading_levels(lines)
    target = heading.rstrip()
    for index, line in enumerate(lines):
        if levels[index] is None or line.rstrip() != target:
            continue
        level = levels[index]
        assert level is not None
        end = len(lines)
        for probe in range(index + 1, len(lines)):
            probe_level = levels[probe]
            if probe_level is not None and probe_level <= level:
                end = probe
                break
        return index, end
    return None


def apply_section(text: str, heading: str, replacement: str | None) -> str:
    """Replace (or delete when ``replacement`` is None) a whole section."""
    span = find_section(text, heading)
    if span is None:
        raise TransformError(f"section heading not found: {heading}")
    start, end = span
    lines = text.split("\n")
    head, tail = lines[:start], lines[end:]
    if replacement is None:
        body: list[str] = []
    else:
        body = replacement.replace("\r\n", "\n").rstrip("\n").split("\n")
        if tail and tail[0].strip():
            body = body + [""]
    return "\n".join(_seam(head, body, tail))


def _seam(head: list[str], body: list[str], tail: list[str]) -> list[str]:
    """Join three line runs, leaving at most one blank line at each seam."""
    out = list(head)
    for run in (body, tail):
        chunk = list(run)
        while out and not out[-1].strip() and chunk and not chunk[0].strip():
            chunk.pop(0)
        out.extend(chunk)
    return out
