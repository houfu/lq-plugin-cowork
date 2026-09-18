"""Unit tests for the pure text transforms."""

from __future__ import annotations

import pytest
import yaml

from lqcowork import transforms as t

NAMES = sorted(
    ["wiki", "cite-check", "lq-start", "beta", "docreview", "closing-bible"],
    key=lambda n: (-len(n), n),
)


class TestPathMatches:
    @pytest.mark.parametrize(
        "path,patterns",
        [
            ("LICENSE", ["LICENSE"]),
            ("nested/LICENSE", ["LICENSE"]),
            ("agents/openai.yaml", ["agents/**"]),
            (".hidden", [".*"]),
            ("references/.keep", ["**/.*"]),
            ("a/__pycache__/x.pyc", ["**/__pycache__/**"]),
            ("__pycache__/x.pyc", ["**/__pycache__/**"]),
            ("scripts/sub/tool.py", ["scripts/**"]),
            ("references/automation.md", ["references/automation.md"]),
        ],
    )
    def test_matches(self, path, patterns):
        assert t.path_matches(path, patterns)

    @pytest.mark.parametrize(
        "path,patterns",
        [
            ("SKILL.md", ["LICENSE"]),
            ("references/agents.md", ["agents/**"]),
            ("references/notes.md", ["references/automation.md"]),
            ("scripts.md", ["scripts/**"]),
        ],
    )
    def test_does_not_match(self, path, patterns):
        assert not t.path_matches(path, patterns)


class TestFrontmatter:
    def test_round_trip_orders_and_blocks(self):
        document = t.parse_document(
            "---\nzeta: 1\nname: wiki\ndescription: short\n---\n\nbody\n"
        )
        document.frontmatter["description"] = "line one\nline two"
        rendered = t.render_document(document)
        assert rendered.startswith("---\nname: wiki\ndescription: |-\n")
        assert "zeta: 1" in rendered
        assert rendered.index("name:") < rendered.index("description:")
        assert rendered.index("description:") < rendered.index("zeta:")
        again = t.parse_document(rendered)
        assert again.frontmatter["description"] == "line one\nline two"
        assert again.body.strip() == "body"

    def test_single_line_description_still_block(self):
        rendered = t.dump_frontmatter({"name": "a", "description": "one line"})
        assert "description: |-\n  one line\n" in rendered

    def test_trailing_spaces_do_not_break_block_style(self):
        rendered = t.dump_frontmatter({"name": "a", "description": "one \ntwo "})
        assert "description: |-" in rendered
        assert yaml.safe_load(rendered)["description"] == "one\ntwo"

    def test_missing_frontmatter_raises(self):
        with pytest.raises(t.TransformError):
            t.parse_document("# No frontmatter\n")

    def test_description_round_trips_exactly_after_normalising(self):
        raw = "  first line   \n\tsecond line \t\nthird\n\n"
        value = t.normalise_block(raw)
        rendered = t.dump_frontmatter({"name": "a", "description": value})
        assert "description: |" in rendered
        assert yaml.safe_load(rendered)["description"] == value

    def test_normalise_block_strips_both_ends_of_every_line(self):
        raw = "first line\n      indented deeper than the block\n   third   \n"
        assert t.normalise_block(raw) == (
            "first line\nindented deeper than the block\nthird"
        )

    def test_stamped_description_has_no_leading_space_on_any_line(self):
        value = t.normalise_block("one\n    two\n\tthree\n")
        rendered = t.dump_frontmatter({"name": "a", "description": value})
        parsed = yaml.safe_load(rendered)["description"]
        assert parsed == value
        assert all(line == line.strip() for line in parsed.split("\n"))

    def test_normalise_block_is_idempotent(self):
        once = t.normalise_block("a  \n b \n")
        assert t.normalise_block(once) == once

    def test_crlf_frontmatter_parses(self):
        document = t.parse_document(
            "---\r\nname: wiki\r\ndescription: one\r\n---\r\n\r\nbody\r\n"
        )
        assert document.frontmatter == {"name": "wiki", "description": "one"}
        assert document.body.strip() == "body"
        assert "\r" not in t.render_document(document)

    def test_unicode_survives(self):
        rendered = t.dump_frontmatter({"name": "a", "description": "judgement — yours"})
        assert "—" in rendered


class TestWaivers:
    def test_line_alone_is_removed_entirely(self):
        text = "before\n<!-- vendor-neutral-waiver: because. -->\nafter\n"
        assert t.strip_waivers(text) == "before\nafter\n"

    def test_inline_waiver_is_removed_in_place(self):
        text = "also read <!-- vendor-neutral-waiver: why. -->`references/x.md`.\n"
        assert t.strip_waivers(text) == "also read `references/x.md`.\n"

    def test_other_comments_survive(self):
        text = "<!-- keep me -->\n"
        assert t.strip_waivers(text) == text

    def test_mid_line_waiver_leaves_one_space(self):
        text = "it went well <!-- vendor-neutral-waiver: why. --> for everyone\n"
        assert t.strip_waivers(text) == "it went well for everyone\n"

    def test_waiver_with_no_surrounding_space_closes_up(self):
        text = "a<!-- vendor-neutral-waiver: why. -->b\n"
        assert t.strip_waivers(text) == "ab\n"

    def test_waiver_at_the_end_of_a_line_leaves_no_trailing_space(self):
        text = "a sentence. <!-- vendor-neutral-waiver: why. -->\nnext\n"
        assert t.strip_waivers(text) == "a sentence.\nnext\n"

    def test_multi_line_waiver_is_removed(self):
        text = (
            "before\n"
            "<!-- vendor-neutral-waiver: a reason that\n"
            "     runs over two lines. -->\n"
            "after\n"
        )
        assert t.strip_waivers(text) == "before\nafter\n"

    def test_waiver_inside_a_fenced_block_is_removed_too(self):
        # the contract scopes waiver stripping to every *.md, fences included
        text = "```\n<!-- vendor-neutral-waiver: why. -->\ncode\n```\n"
        assert t.strip_waivers(text) == "```\ncode\n```\n"


class TestTokens:
    @pytest.mark.parametrize(
        "before,after",
        [
            ("Type $wiki now", "Type wiki now"),
            ("Use `/wiki` here", "Use `wiki` here"),
            ("Use `/wiki add a note` here", "Use `wiki` here"),
            ("Run /wiki now", "Run wiki now"),
            ("/wiki at line start", "wiki at line start"),
            ("(/wiki) in parens", "(wiki) in parens"),
            ('"/wiki" quoted', '"wiki" quoted'),
            ("ends with /wiki", "ends with wiki"),
            ("stop /wiki.", "stop wiki."),
            ("$cite-check and $lq-start", "cite-check and lq-start"),
        ],
    )
    def test_rewrites(self, before, after):
        assert t.rewrite_tokens(before, NAMES) == after

    @pytest.mark.parametrize(
        "text",
        [
            "see references/wiki.md for more",
            "see ../docreview/SKILL.md for more",
            "the path a/wiki/b is untouched",
            "$wikipedia stays",
            "/wikipedia stays",
            # the contract's negative cases
            "https://example.invalid/transcripts/wiki/page.html",
            "scripts/cite_check.py is a path",
            "scripts/cite-check.py is also a path",
            "a cite-checker is a person, not a token",
            "$HOME is an environment variable",
            "$1 is a shell positional",
            "/usr/bin is a directory",
            "$wiki-page is a different word",
            "abc$wiki has no left boundary",
            "x/wiki is not at a boundary either",
        ],
    )
    def test_leaves_paths_alone(self, text):
        assert t.rewrite_tokens(text, NAMES) == text

    def test_backticked_dollar_token_is_rewritten(self):
        assert t.rewrite_tokens("a `$lq-apply` b", ["lq-apply"]) == "a `lq-apply` b"
        assert t.rewrite_tokens("`$wiki`", NAMES) == "`wiki`"

    def test_dollar_token_needs_a_left_boundary(self):
        assert t.rewrite_tokens("abc$wiki", NAMES) == "abc$wiki"
        assert t.rewrite_tokens("abc $wiki", NAMES) == "abc wiki"
        assert t.rewrite_tokens("($wiki)", NAMES) == "(wiki)"
        assert t.rewrite_tokens("$wiki", NAMES) == "wiki"

    def test_surviving_tokens_honours_the_same_boundary(self):
        assert t.surviving_tokens("abc$wiki", NAMES) == []
        assert t.surviving_tokens("abc $wiki", NAMES) == ["$wiki"]

    def test_longest_name_wins(self):
        assert t.rewrite_tokens("$closing-bible", NAMES) == "closing-bible"

    def test_surviving_tokens_reports(self):
        assert t.surviving_tokens("$wiki and `/beta x`", NAMES) == ["$wiki", "`/beta`"]


SECTIONED = """# Title

intro

## One

alpha

### One.a

nested

## Two

beta

```
## Not a heading
```

## Three

gamma
"""


class TestSections:
    def test_span_stops_at_same_level(self):
        start, end = t.find_section(SECTIONED, "## One")
        lines = SECTIONED.split("\n")
        assert lines[start] == "## One"
        assert lines[end] == "## Two"

    def test_fenced_heading_is_ignored(self):
        assert t.find_section(SECTIONED, "## Not a heading") is None
        start, end = t.find_section(SECTIONED, "## Two")
        assert SECTIONED.split("\n")[end] == "## Three"

    def test_last_section_runs_to_eof(self):
        _, end = t.find_section(SECTIONED, "## Three")
        assert end == len(SECTIONED.split("\n"))

    def test_replacement_splices_and_keeps_one_blank(self):
        out = t.apply_section(SECTIONED, "## One", "## Renamed\n\nnew body\n")
        assert "## Renamed" in out
        assert "### One.a" not in out
        assert "\n\n\n" not in out
        assert "## Two" in out

    def test_delete_removes_the_section(self):
        out = t.apply_section(SECTIONED, "## Two", None)
        assert "## Two" not in out
        assert "beta" not in out
        assert "## Three" in out
        assert "\n\n\n" not in out

    def test_missing_heading_raises(self):
        with pytest.raises(t.TransformError):
            t.apply_section(SECTIONED, "## Nope", None)
