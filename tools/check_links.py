#!/usr/bin/env python3
"""Offline checks for the documentation of nobel-2026-lab (stdlib only, no network).

    python3 tools/check_links.py            # report; exit 1 on any error
    python3 tools/check_links.py --strict   # also treat "pending" targets as errors

What it checks
  1. Every relative link, image and srcset path in every Markdown file points to a file or folder
     that exists, and every #anchor points to a heading that exists (GitHub's slug rules).
  2. Every image has alt text (Markdown images and HTML <img>).
  3. External links are well formed (https, a host, no localhost). They are not fetched.
  4. Every SVG parses as XML and has a <title> (pictures also need a <desc>), and every
     "-dark.svg" has a matching "-light.svg".
  5. In each CLAIMS.md: ids are unique and in order, each row has all five columns, and every
     source URL also appears in the FACTS.md next to it.
  6. No markers of private or unfinished notes in any public file.

"Pending" targets: files that live on another branch and arrive when it is merged. They are listed,
not failed, unless --strict is given. Remove an entry once the file exists on main.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "work"}

# Files that arrive from another branch (the simulator is built separately): path -> git ref that has it.
# Remove an entry once the file is on main.
PENDING = {
    "2026/medicine/simulator/README.md": "origin/b-simulator",
}

# Phrases that must never appear in a public file (built from parts so this file does not trip itself).
FORBIDDEN = [
    "/Us" + "ers/",
    "showtime-" + "local",
    "Co-Authored" + "-By",
    "Generated " + "with",
    "do not " + "use on screen",
]

errors: list[str] = []
pending: list[str] = []
notes: list[str] = []


def rel(p: pathlib.Path) -> str:
    return p.relative_to(ROOT).as_posix()


def files(suffixes: tuple[str, ...]) -> list[pathlib.Path]:
    out = []
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and p.suffix.lower() in suffixes and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS):
            out.append(p)
    return out


# ------------------------------------------------------------------ Markdown parsing
FENCE = re.compile(r"^(```|~~~).*?^\1[ \t]*$", re.S | re.M)
CODE_SPAN = re.compile(r"`[^`\n]*`")


def strip_code(text: str) -> str:
    text = FENCE.sub("", text)
    return CODE_SPAN.sub("", text)


MD_LINK = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*(<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
HTML_ATTR = re.compile(r"""\b(href|src|srcset)\s*=\s*("([^"]*)"|'([^']*)')""", re.I)
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
ALT_ATTR = re.compile(r"""\balt\s*=\s*("([^"]*)"|'([^']*)')""", re.I)


def slugify(heading: str) -> str:
    h = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # links -> text
    h = re.sub(r"[`*~]", "", h)
    h = re.sub(r"<[^>]+>", "", h).strip().lower()
    h = unicodedata.normalize("NFC", h)
    h = re.sub(r"[^\w\- ]", "", h, flags=re.U)
    return h.replace(" ", "-")


def anchors_of(md_path: pathlib.Path) -> set[str]:
    text = strip_code(md_path.read_text(encoding="utf-8"))
    seen: dict[str, int] = {}
    out: set[str] = set()
    for m in re.finditer(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", text, re.M):
        slug = slugify(m.group(1))
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        out.add(slug if n == 0 else f"{slug}-{n}")
    for m in re.finditer(r"""<a\s[^>]*\b(?:id|name)\s*=\s*["']([^"']+)["']""", text, re.I):
        out.add(m.group(1))
    return out


_anchor_cache: dict[pathlib.Path, set[str]] = {}


def check_target(src: pathlib.Path, target: str, kind: str, stats: dict[str, int]) -> None:
    target = target.strip().strip("<>")
    if not target or target.startswith(("mailto:", "tel:", "data:")):
        return
    parsed = urlparse(target)
    if parsed.scheme in ("http", "https"):
        stats["external"] += 1
        if not parsed.netloc or parsed.netloc.split(":")[0] in ("localhost", "127.0.0.1"):
            errors.append(f"{rel(src)}: bad external link {target!r}")
        if parsed.scheme == "http":
            errors.append(f"{rel(src)}: use https instead of http: {target!r}")
        return
    if parsed.scheme:
        errors.append(f"{rel(src)}: unsupported link scheme {target!r}")
        return
    stats["internal"] += 1
    path_part, frag = unquote(parsed.path), parsed.fragment
    dest = src if not path_part else (src.parent / path_part).resolve()
    try:
        dest_rel = dest.relative_to(ROOT).as_posix()
    except ValueError:
        errors.append(f"{rel(src)}: link leaves the repository {target!r}")
        return
    if not dest.exists():
        if dest_rel in PENDING:
            ref = PENDING[dest_rel]
            ok = subprocess.run(["git", "cat-file", "-e", f"{ref}:{dest_rel}"], cwd=ROOT,
                                capture_output=True).returncode == 0
            if ok:
                pending.append(f"{rel(src)} -> {dest_rel} (exists on {ref}; arrives when that branch is merged)")
            else:
                errors.append(f"{rel(src)}: pending target {dest_rel} is not on {ref} either")
            return
        errors.append(f"{rel(src)}: {kind} target not found: {target!r}")
        return
    if frag and dest.suffix.lower() == ".md":
        if dest not in _anchor_cache:
            _anchor_cache[dest] = anchors_of(dest)
        if frag.lower() not in {a.lower() for a in _anchor_cache[dest]}:
            errors.append(f"{rel(src)}: anchor #{frag} not found in {dest_rel}")


def check_markdown(md: pathlib.Path, stats: dict[str, int]) -> None:
    raw = md.read_text(encoding="utf-8")
    text = strip_code(raw)
    for m in MD_LINK.finditer(text):
        is_img, label, target = m.group(1), m.group(2), m.group(3)
        if is_img:
            stats["images"] += 1
            if not label.strip():
                errors.append(f"{rel(md)}: image without alt text: {target}")
        check_target(md, target, "image" if is_img else "link", stats)
    for m in IMG_TAG.finditer(text):
        stats["images"] += 1
        alt = ALT_ATTR.search(m.group(0))
        if not alt or not (alt.group(2) or alt.group(3) or "").strip():
            errors.append(f"{rel(md)}: <img> without alt text: {m.group(0)[:80]}...")
    for m in HTML_ATTR.finditer(text):
        attr, val = m.group(1).lower(), m.group(3) if m.group(3) is not None else m.group(4)
        parts = [p.strip().split()[0] for p in val.split(",") if p.strip()] if attr == "srcset" else [val]
        for t in parts:
            check_target(md, t, attr, stats)
    for phrase in FORBIDDEN:
        if phrase in raw:
            errors.append(f"{rel(md)}: contains a forbidden marker {phrase!r}")
    if md.name in ("FACTS.md", "CLAIMS.md") and ("UN" + "VERIFIED") in raw:
        errors.append(f"{rel(md)}: the fact sheet and the ledger must not carry unverified claims")


# ------------------------------------------------------------------ SVG
def check_svg(svg: pathlib.Path) -> None:
    try:
        root = ET.parse(svg).getroot()
    except ET.ParseError as e:
        errors.append(f"{rel(svg)}: not valid XML ({e})")
        return
    ns = "{http://www.w3.org/2000/svg}"
    if root.tag != f"{ns}svg":
        errors.append(f"{rel(svg)}: root element is not <svg>")
        return
    if not root.get("viewBox"):
        errors.append(f"{rel(svg)}: missing viewBox")
    title = root.find(f"{ns}title")
    if title is None or not (title.text or "").strip():
        errors.append(f"{rel(svg)}: missing <title>")
    is_icon = "icons" in svg.parts
    desc = root.find(f"{ns}desc")
    if not is_icon and (desc is None or len((desc.text or "").strip()) < 40):
        errors.append(f"{rel(svg)}: missing or very short <desc>")
    if root.get("role") != "img":
        errors.append(f"{rel(svg)}: role=\"img\" missing")
    text = svg.read_text(encoding="utf-8")
    for phrase in FORBIDDEN:
        if phrase in text:
            errors.append(f"{rel(svg)}: contains a forbidden marker {phrase!r}")
    if svg.name.endswith("-dark.svg"):
        twin = svg.with_name(svg.name.replace("-dark.svg", "-light.svg"))
        if not twin.exists():
            errors.append(f"{rel(svg)}: no light variant {twin.name}")
    if svg.name.endswith("-light.svg"):
        twin = svg.with_name(svg.name.replace("-light.svg", "-dark.svg"))
        if not twin.exists():
            errors.append(f"{rel(svg)}: no dark variant {twin.name}")


# ------------------------------------------------------------------ claims ledger
URL = re.compile(r"https?://[^\s)>\]|]+")


def check_claims(claims: pathlib.Path) -> int:
    facts = claims.with_name("FACTS.md")
    facts_urls = set(u.rstrip(".,;") for u in URL.findall(facts.read_text(encoding="utf-8"))) if facts.exists() else set()
    ids: list[int] = []
    rows = 0
    for line in claims.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(C(\d+))\s*\|", line)
        if not m:
            continue
        rows += 1
        ids.append(int(m.group(2)))
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) != 5 or not all(cells):
            errors.append(f"{rel(claims)}: {m.group(1)} must have 5 non-empty columns, found {len(cells)}")
            continue
        urls = URL.findall(cells[2])
        if not urls:
            errors.append(f"{rel(claims)}: {m.group(1)} has no source URL")
        for u in urls:
            if u.rstrip(".,;") not in facts_urls:
                errors.append(f"{rel(claims)}: {m.group(1)} cites {u} which is not in FACTS.md")
        if not re.search(r"\b20\d\d-\d\d-\d\d\b", cells[4]):
            errors.append(f"{rel(claims)}: {m.group(1)} status has no check date")
    if ids != list(range(1, len(ids) + 1)):
        errors.append(f"{rel(claims)}: claim ids are not C01, C02, ... in order: {ids}")
    return rows


def main() -> int:
    strict = "--strict" in sys.argv[1:]
    stats = {"external": 0, "internal": 0, "images": 0}
    mds = files((".md",))
    for md in mds:
        check_markdown(md, stats)
    svgs = files((".svg",))
    for svg in svgs:
        check_svg(svg)
    claim_rows = 0
    for claims in ROOT.rglob("CLAIMS.md"):
        if not (set(claims.relative_to(ROOT).parts) & SKIP_DIRS):
            claim_rows += check_claims(claims)
    if pending and strict:
        errors.extend(f"pending target (strict): {p}" for p in sorted(set(pending)))
    print(f"markdown files: {len(mds)}   svg files: {len(svgs)}   claim rows: {claim_rows}")
    print(f"internal links/paths checked: {stats['internal']}   images: {stats['images']}   "
          f"external links (syntax only, not fetched): {stats['external']}")
    if pending:
        print("pending (not failed):")
        for p in sorted(set(pending)):
            print("  -", p)
    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print("  -", e)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
