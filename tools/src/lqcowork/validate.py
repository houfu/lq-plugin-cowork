"""Validation rules from docs/CONTRACT.md section 6, run against dist/."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path, PurePosixPath

from . import transforms
from .build import MANIFEST_SCHEMA, MANIFEST_VERSION, Issue, Suppression, dist_root
from .config import GUID_RE, KEBAB_RE, SEMVER_RE, Bundle, Card, Config

MAX_SKILLS = 20
MAX_FOLDER_CHARS = 256
MAX_COMPANIONS = 20
MAX_COMPANION_BYTES = 5 * 1024 * 1024
MAX_SKILL_COMPANION_BYTES = 10 * 1024 * 1024
MAX_SKILL_MD_BYTES = 1024 * 1024
MAX_DESCRIPTION_CHARS = 1024
MAX_BODY_WORDS = 3000

# Cowork's Upload skill limits for a single-skill archive (contract section 8).
MAX_ARCHIVE_ENTRIES = 100
MAX_ARCHIVE_COMPRESSED_BYTES = 10 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_ARCHIVE_MD_BYTES = 1024 * 1024
MAX_ARCHIVE_COMPANIONS = 20
# The two Apache-2.0 notices a single-skill archive carries beyond the built
# skill folder; everything else in it must come from that folder.
ARCHIVE_ROOT_FILES = ("LICENSE", "NOTICE.md")

MANIFEST_KEYS = [
    "$schema",
    "manifestVersion",
    "version",
    "id",
    "developer",
    "name",
    "description",
    "icons",
    "accentColor",
    "agentSkills",
]
OPTIONAL_MANIFEST_KEYS = {"agentConnectors"}

NAME_RE = re.compile(r"^[A-Za-z0-9 _.!-]+$")
RESERVED = {"CON", "PRN", "AUX", "NUL"}
RESERVED |= {f"COM{i}" for i in range(1, 10)}
RESERVED |= {f"LPT{i}" for i in range(1, 10)}

HOST_LEAK_RE = re.compile(
    r"hooks|~/\.lq/|CLAUDE_PLUGIN_ROOT|argument-hint|disable-model-invocation"
)


def _issue(code: str, message: str, bundle: str, skill: str | None = None) -> Issue:
    return Issue(code=code, message=message, skill=skill, bundle=bundle)


def _is_dir(path: Path) -> bool:
    """``Path.is_dir`` that survives a manifest folder the OS refuses."""
    try:
        return path.is_dir()
    except OSError:
        return False


def _is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def validate_bundle(
    config: Config,
    bundle: Bundle,
    *,
    cards: dict[str, Card] | None = None,
    skill_names: list[str] | None = None,
    upstream_path: Path | None = None,
    out_dir: Path | None = None,
    suppressed: list[Suppression] | None = None,
) -> tuple[list[Issue], list[Issue]]:
    """Validate ``dist/<bundle>/``. Returns ``(errors, warnings)``."""
    errors: list[Issue] = []
    warnings: list[Issue] = []
    root = dist_root(config, out_dir) / bundle.id
    if not root.is_dir():
        errors.append(_issue("LQC-M001", f"{root} does not exist", bundle.id))
        return errors, warnings

    _validate_manifest(root, bundle, errors)
    _validate_icons(root, bundle, errors)

    upstream_root = config.upstream_skills_root(upstream_path)
    for name in bundle.skills:
        skill_dir = root / "skills" / name
        card = (cards or {}).get(name)
        upstream_dir = (upstream_root / card.upstream) if card is not None else None
        _validate_skill(
            config,
            bundle,
            name,
            skill_dir,
            card,
            skill_names or [],
            errors,
            warnings,
            upstream_dir,
        )
        if card is not None and card.bucket == "amber" and not card.notes:
            warnings.append(
                _issue("LQC-W008", "amber skill has no notes", bundle.id, name)
            )
    return errors, _apply_suppressions(warnings, cards or {}, suppressed)


def _apply_suppressions(
    warnings: list[Issue],
    cards: dict[str, Card],
    collected: list[Suppression] | None,
) -> list[Issue]:
    """Drop warnings a card accepted, recording each one with its reason."""
    kept: list[Issue] = []
    for issue in warnings:
        card = cards.get(issue.skill or "")
        rule = None
        if card is not None:
            rule = next(
                (r for r in card.suppress if r.matches(issue.code, issue.location)),
                None,
            )
        if rule is None:
            kept.append(issue)
            continue
        if collected is not None:
            collected.append(Suppression(issue, rule.file, rule.reason))
    return kept


def _validate_manifest(root: Path, bundle: Bundle, errors: list[Issue]) -> dict:
    path = root / "manifest.json"
    if not path.is_file():
        errors.append(_issue("LQC-M001", "manifest.json is missing", bundle.id))
        return {}
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(_issue("LQC-M001", f"manifest.json: {exc}", bundle.id))
        return {}

    keys = list(manifest)
    allowed = set(MANIFEST_KEYS) | OPTIONAL_MANIFEST_KEYS
    unexpected = [k for k in keys if k not in allowed]
    missing = [k for k in MANIFEST_KEYS if k not in keys]
    if unexpected or missing:
        errors.append(
            _issue(
                "LQC-M001",
                f"manifest keys wrong (missing {missing}, unexpected {unexpected})",
                bundle.id,
            )
        )

    if manifest.get("manifestVersion") != MANIFEST_VERSION:
        errors.append(_issue("LQC-M002", "manifestVersion must be '1.28'", bundle.id))
    if manifest.get("$schema") != MANIFEST_SCHEMA:
        errors.append(_issue("LQC-M002", "$schema must be the v1.28 URL", bundle.id))
    if not SEMVER_RE.match(str(manifest.get("version", ""))):
        errors.append(_issue("LQC-M002", "version must match x.y.z", bundle.id))
    if not GUID_RE.match(str(manifest.get("id", ""))):
        errors.append(_issue("LQC-M002", "id must be a UUID", bundle.id))

    limits = {
        ("name", "short"): 30,
        ("name", "full"): 100,
        ("description", "short"): 80,
        ("description", "full"): 4000,
    }
    for (outer, inner), limit in limits.items():
        value = (manifest.get(outer) or {}).get(inner)
        if not isinstance(value, str) or not value.strip():
            errors.append(_issue("LQC-M003", f"{outer}.{inner} is empty", bundle.id))
        elif len(value) > limit:
            errors.append(
                _issue(
                    "LQC-M003",
                    f"{outer}.{inner} is {len(value)} chars, limit {limit}",
                    bundle.id,
                )
            )

    developer = manifest.get("developer") or {}
    for key in ("name", "websiteUrl", "privacyUrl", "termsOfUseUrl"):
        value = developer.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(_issue("LQC-M004", f"developer.{key} is missing", bundle.id))
        elif key.endswith("Url") and not value.startswith("https://"):
            errors.append(
                _issue("LQC-M004", f"developer.{key} must be https", bundle.id)
            )

    if not re.match(r"^#[0-9A-Fa-f]{6}$", str(manifest.get("accentColor", ""))):
        errors.append(_issue("LQC-M005", "accentColor must be #RRGGBB", bundle.id))

    entries = manifest.get("agentSkills")
    if not isinstance(entries, list):
        errors.append(_issue("ASKILL-M001", "agentSkills must be a list", bundle.id))
        return manifest
    if len(entries) > MAX_SKILLS:
        errors.append(
            _issue(
                "ASKILL-M002",
                f"{len(entries)} agentSkills entries, limit {MAX_SKILLS}",
                bundle.id,
            )
        )
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        folder = entry.get("folder") if isinstance(entry, dict) else None
        if not isinstance(folder, str) or not folder:
            errors.append(
                _issue("ASKILL-M001", f"agentSkills[{index}] has no folder", bundle.id)
            )
            continue
        if len(folder) > MAX_FOLDER_CHARS:
            errors.append(
                _issue("ASKILL-M003", f"folder '{folder}' is too long", bundle.id)
            )
        if folder in seen:
            errors.append(
                _issue("ASKILL-P008", f"duplicate folder '{folder}'", bundle.id)
            )
        seen.add(folder)
        resolved = root / folder.lstrip("./")
        if not _is_dir(resolved):
            errors.append(
                _issue(
                    "ASKILL-P001", f"folder '{folder}' is not in the package", bundle.id
                )
            )
        elif not _is_file(resolved / "SKILL.md"):
            errors.append(
                _issue("ASKILL-P002", f"'{folder}' has no SKILL.md", bundle.id)
            )
    return manifest


def _validate_icons(root: Path, bundle: Bundle, errors: list[Issue]) -> None:
    from .icons import PngError, png_size

    for filename, expected in (("color.png", 192), ("outline.png", 32)):
        path = root / filename
        if not path.is_file():
            errors.append(_issue("LQC-I001", f"{filename} is missing", bundle.id))
            continue
        try:
            width, height = png_size(path)
        except PngError as exc:
            errors.append(_issue("LQC-I001", str(exc), bundle.id))
            continue
        if (width, height) != (expected, expected):
            errors.append(
                _issue(
                    "LQC-I001",
                    f"{filename} is {width}x{height}, expected "
                    f"{expected}x{expected}",
                    bundle.id,
                )
            )


def _validate_skill(
    config: Config,
    bundle: Bundle,
    name: str,
    skill_dir: Path,
    card: Card | None,
    skill_names: list[str],
    errors: list[Issue],
    warnings: list[Issue],
    upstream_dir: Path | None = None,
) -> None:
    if not skill_dir.is_dir():
        errors.append(_issue("ASKILL-P001", "skill folder missing", bundle.id, name))
        return
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(_issue("ASKILL-P002", "no SKILL.md", bundle.id, name))
        return

    files = sorted(p for p in skill_dir.rglob("*") if p.is_file())
    companions = [p for p in files if p != skill_md]
    if len(companions) > MAX_COMPANIONS:
        errors.append(
            _issue(
                "LQC-C001",
                f"{len(companions)} companion files, limit {MAX_COMPANIONS}",
                bundle.id,
                name,
            )
        )
    companion_bytes = 0
    for path in companions:
        size = path.stat().st_size
        companion_bytes += size
        if size > MAX_COMPANION_BYTES:
            rel = path.relative_to(skill_dir).as_posix()
            errors.append(
                _issue("LQC-C002", f"{rel} is {size} bytes (>5 MB)", bundle.id, name)
            )
    if companion_bytes > MAX_SKILL_COMPANION_BYTES:
        errors.append(
            _issue(
                "LQC-C003",
                f"companions total {companion_bytes} bytes (>10 MB)",
                bundle.id,
                name,
            )
        )

    for path in sorted(p for p in skill_dir.rglob("*")):
        rel = path.relative_to(skill_dir).as_posix()
        if path.is_symlink():
            errors.append(
                Issue(
                    "LQC-C007",
                    "symlink in skill folder",
                    skill=name,
                    bundle=bundle.id,
                    location=rel,
                )
            )
        for part in rel.split("/"):
            if part.startswith("."):
                errors.append(
                    _issue("LQC-C004", f"hidden path '{rel}'", bundle.id, name)
                )
                break
            stem = part.split(".", 1)[0].upper()
            if stem in RESERVED:
                errors.append(
                    _issue(
                        "LQC-C005",
                        f"'{rel}' uses a Windows reserved name",
                        bundle.id,
                        name,
                    )
                )
            if part == ".." or "\\" in part or not NAME_RE.match(part):
                errors.append(
                    _issue("LQC-C006", f"illegal path name '{rel}'", bundle.id, name)
                )

    if skill_md.stat().st_size > MAX_SKILL_MD_BYTES:
        errors.append(_issue("LQC-S001", "SKILL.md exceeds 1 MB", bundle.id, name))

    text = skill_md.read_text(encoding="utf-8")
    try:
        document = transforms.parse_document(text)
    except transforms.TransformError as exc:
        errors.append(_issue("ASKILL-P003", str(exc), bundle.id, name))
        return

    frontmatter = document.frontmatter
    fm_name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(fm_name, str) or not fm_name:
        errors.append(_issue("ASKILL-P004", "frontmatter has no name", bundle.id, name))
    else:
        if fm_name != name:
            errors.append(
                _issue(
                    "ASKILL-P006",
                    f"frontmatter name '{fm_name}' != folder '{name}'",
                    bundle.id,
                    name,
                )
            )
        if not KEBAB_RE.match(fm_name) or not 1 <= len(fm_name) <= 64:
            errors.append(
                _issue("ASKILL-P007", f"'{fm_name}' is not kebab-case", bundle.id, name)
            )
    if not isinstance(description, str) or not description.strip():
        errors.append(
            _issue("ASKILL-P005", "frontmatter has no description", bundle.id, name)
        )
    else:
        length = len(description.strip())
        if not 1 <= length <= MAX_DESCRIPTION_CHARS:
            errors.append(
                _issue(
                    "LQC-D001",
                    f"description is {length} chars, limit {MAX_DESCRIPTION_CHARS}",
                    bundle.id,
                    name,
                )
            )

    _warn_skill(
        config,
        bundle,
        name,
        skill_dir,
        card,
        document,
        text,
        skill_names,
        warnings,
        upstream_dir,
    )


def _warn_skill(
    config: Config,
    bundle: Bundle,
    name: str,
    skill_dir: Path,
    card: Card | None,
    document: transforms.Document,
    text: str,
    skill_names: list[str],
    warnings: list[Issue],
    upstream_dir: Path | None,
) -> None:
    """Every W-code except W008, which is about the card rather than the build.

    W001, W002, W004, W005, W007, W009 and W010 run over every ``*.md`` in the
    built skill and report ``file:line``.
    """

    def warn(code: str, message: str, rel: str, line: int) -> None:
        warnings.append(
            Issue(code, message, skill=name, bundle=bundle.id, location=f"{rel}:{line}")
        )

    md_files = sorted(skill_dir.rglob("*.md"))
    packaged = {p.relative_to(skill_dir).as_posix() for p in skill_dir.rglob("*")}

    upstream_urls = _upstream_urls(upstream_dir)

    for path in md_files:
        rel = path.relative_to(skill_dir).as_posix()
        content = path.read_text(encoding="utf-8")
        for number, line in enumerate(content.split("\n"), start=1):
            for word in config.transforms.vendor_words:
                if re.search(
                    rf"(?<![A-Za-z0-9]){re.escape(word)}(?![A-Za-z0-9])", line
                ):
                    warn("LQC-W001", f"vendor word '{word}'", rel, number)
            for token in transforms.surviving_tokens(line, skill_names):
                warn("LQC-W002", f"invocation token {token}", rel, number)
            if "../" in line:
                warn("LQC-W004", "path points outside the skill folder", rel, number)
            for target in _relative_links(line):
                resolved = _resolve_link(rel, target)
                if resolved is None or resolved not in packaged:
                    warn(
                        "LQC-W004",
                        f"link target '{target}' is not packaged",
                        rel,
                        number,
                    )
            for folder in ("scripts", "schemas"):
                if _mentions_folder(line, folder) and not (skill_dir / folder).is_dir():
                    warn(
                        "LQC-W005",
                        f"mentions {folder}/ but the folder is not packaged",
                        rel,
                        number,
                    )
            for leak in sorted(set(HOST_LEAK_RE.findall(line))):
                warn("LQC-W007", f"host-specific term '{leak}'", rel, number)
            lowered = line.lower()
            for phrase in config.transforms.host_words:
                if phrase.lower() in lowered:
                    warn("LQC-W009", f"host machinery '{phrase}'", rel, number)
            for url in _external_urls(line):
                if url not in upstream_urls:
                    warn("LQC-W010", f"external URL {url}", rel, number)

    others = [n for n in skill_names if n != name and n not in bundle.skills]
    for number, line in enumerate(text.split("\n"), start=1):
        for other in others:
            escaped = re.escape(other)
            if re.search(rf"`{escaped}`", line) or re.search(
                rf"\bthe {escaped} skill\b", line, re.IGNORECASE
            ):
                warn("LQC-W003", f"'{other}' is not in this bundle", "SKILL.md", number)

    words = len(document.body.split())
    if words > MAX_BODY_WORDS:
        warnings.append(
            Issue(
                "LQC-W006",
                f"body is {words} words (>{MAX_BODY_WORDS})",
                skill=name,
                bundle=bundle.id,
                location="SKILL.md",
            )
        )
    _ = card


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
URL_RE = re.compile(r"https?://[^\s)\]\"'`<>]+")
ALLOWED_URL_PREFIX = "https://github.com/LegalQuants/lq-plugin-oss"


def _relative_links(line: str) -> list[str]:
    """Markdown link targets that should resolve inside the skill folder."""
    out: list[str] = []
    for target in LINK_RE.findall(line):
        lowered = target.lower()
        if lowered.startswith(("http://", "https://", "mailto:", "#")):
            continue
        out.append(target)
    return out


def _resolve_link(rel: str, target: str) -> str | None:
    """Resolve ``target`` (relative to the file at ``rel``) inside the skill."""
    path = target.split("#", 1)[0].split("?", 1)[0]
    if not path:
        return None
    if path.startswith("/"):
        return None
    base = PurePosixPath(rel).parent
    parts: list[str] = []
    for part in (base / path).parts:
        if part == ".":
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    return "/".join(parts) if parts else None


def _external_urls(line: str) -> list[str]:
    return [
        url for url in URL_RE.findall(line) if not url.startswith(ALLOWED_URL_PREFIX)
    ]


def _mentions_folder(line: str, folder: str) -> bool:
    """``folder/`` only where it starts a path segment.

    ``transcripts/`` and ``my-scripts/`` are words that happen to end in the
    folder name, not references to it.
    """
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(folder)}/", line) is not None


def _upstream_urls(upstream_dir: Path | None) -> set[str]:
    """Every URL upstream itself wrote, anywhere in the skill folder.

    LQC-W010 is about links this adaptation introduced, not about where an
    upstream authority list happens to live now: a court or legislation URL
    moved from SKILL.md into a reference file is still upstream's. Every file
    type counts, decoded leniently, because these lists also sit in templates
    and other non-Markdown companions.
    """
    if upstream_dir is None or not upstream_dir.is_dir():
        return set()
    urls: set[str] = set()
    for path in upstream_dir.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_bytes().decode("utf-8", "ignore")
        except OSError:  # pragma: no cover - unreadable file
            continue
        urls.update(URL_RE.findall(text))
    return urls


def validate_zip(path: Path, bundle_id: str, allowed_roots: set[str]) -> list[Issue]:
    """LQC-Z001: entries live at the zip root, with no dotfiles or __MACOSX."""
    errors: list[Issue] = []
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    if "manifest.json" not in names:
        errors.append(
            _issue("LQC-Z001", "manifest.json is not at the zip root", bundle_id)
        )
    for entry in names:
        if entry.startswith("__MACOSX") or "/__MACOSX/" in entry:
            errors.append(_issue("LQC-Z001", f"__MACOSX entry '{entry}'", bundle_id))
        if any(part.startswith(".") for part in entry.split("/") if part):
            errors.append(_issue("LQC-Z001", f"dotfile entry '{entry}'", bundle_id))
        if entry.split("/", 1)[0] not in allowed_roots:
            errors.append(
                _issue("LQC-Z001", f"unexpected root entry '{entry}'", bundle_id)
            )
    return errors


def validate_skill_archive(archive: Path, name: str, skill_dir: Path) -> list[Issue]:
    """LQC-U001..U005 against one ``dist/skills/<name>.skill``.

    ``skill_dir`` is the built folder the archive was made from, which is what
    makes "carries nothing the bundle folder does not" checkable.
    """
    errors: list[Issue] = []

    def fail(code: str, message: str) -> None:
        errors.append(Issue(code, message, skill=name))

    with zipfile.ZipFile(archive) as opened:
        infos = opened.infolist()
        contents = {info.filename: opened.read(info.filename) for info in infos}
    names = [info.filename for info in infos]

    built = {
        path.relative_to(skill_dir).as_posix()
        for path in skill_dir.rglob("*")
        if path.is_file()
    }
    own_roots = {rel.split("/", 1)[0] for rel in built}

    # LQC-U001: SKILL.md at the root, and nothing outside the skill's own tree
    if "SKILL.md" not in names:
        fail("LQC-U001", "SKILL.md is not at the archive root")
    for entry in names:
        head = entry.split("/", 1)[0]
        if entry.startswith("./") or entry.startswith("/"):
            fail("LQC-U001", f"entry '{entry}' is not at the archive root")
        elif any(part.startswith(".") for part in entry.split("/") if part):
            fail("LQC-U001", f"dotfile entry '{entry}'")
        elif head == "__MACOSX":
            fail("LQC-U001", f"__MACOSX entry '{entry}'")
        elif head not in own_roots | set(ARCHIVE_ROOT_FILES):
            fail("LQC-U001", f"unexpected root entry '{entry}'")

    # LQC-U002: the SKILL.md a lawyer uploads is the one we built, and the
    # licence travels with it
    skill_md = skill_dir / "SKILL.md"
    if "SKILL.md" in contents and skill_md.is_file():
        if contents["SKILL.md"] != skill_md.read_bytes():
            fail("LQC-U002", "SKILL.md differs from the built skill folder")
    for required in ARCHIVE_ROOT_FILES:
        if required not in names:
            fail("LQC-U002", f"{required} is missing from the archive")

    # LQC-U003 / LQC-U004: Cowork's upload limits
    if len(names) > MAX_ARCHIVE_ENTRIES:
        fail(
            "LQC-U003",
            f"{len(names)} entries, limit {MAX_ARCHIVE_ENTRIES}",
        )
    compressed = archive.stat().st_size
    if compressed > MAX_ARCHIVE_COMPRESSED_BYTES:
        fail(
            "LQC-U004",
            f"{compressed} bytes compressed, limit " f"{MAX_ARCHIVE_COMPRESSED_BYTES}",
        )
    uncompressed = sum(info.file_size for info in infos)
    if uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
        fail(
            "LQC-U004",
            f"{uncompressed} bytes uncompressed, limit "
            f"{MAX_ARCHIVE_UNCOMPRESSED_BYTES}",
        )
    for info in infos:
        if info.filename.lower().endswith(".md") and (
            info.file_size > MAX_ARCHIVE_MD_BYTES
        ):
            fail(
                "LQC-U004",
                f"{info.filename} is {info.file_size} bytes, limit "
                f"{MAX_ARCHIVE_MD_BYTES}",
            )

    # LQC-U005: the companion budget, and nothing the bundle folder lacks
    extras = [n for n in names if n not in {"SKILL.md", *ARCHIVE_ROOT_FILES}]
    if len(extras) > MAX_ARCHIVE_COMPANIONS:
        fail(
            "LQC-U005",
            f"{len(extras)} files besides SKILL.md, LICENSE and NOTICE.md, "
            f"limit {MAX_ARCHIVE_COMPANIONS}",
        )
    for entry in names:
        if entry in ARCHIVE_ROOT_FILES:
            continue
        if entry not in built:
            fail("LQC-U005", f"'{entry}' is not in the built skill folder")
    return errors
