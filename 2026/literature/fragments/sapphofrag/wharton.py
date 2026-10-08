"""Parse H. T. Wharton, Sappho (5th ed., John Lane 1908), Project Gutenberg #57390, HTML edition.

Each fragment starts at <div id="fragN">. Inside it:
  * Greek lines: <span class="fsn" title="transliteration">Greek</span>, before the literal translation;
  * Wharton's literal prose: the first <p> that starts with <i> after the Greek;
  * renderings by others (poem divs) and Wharton's prose notes (<p> outside poem divs), which name who quoted it.

Extraction = html.unescape of the element text, then every run of whitespace collapsed to one space. Nothing else is
changed, so tests can re-extract and compare byte for byte.
"""
from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from pathlib import Path


WS_RE = re.compile(r"\s+")


def clean(s: str) -> str:
    return WS_RE.sub(" ", html.unescape(s)).strip()


class _Collector(HTMLParser):
    """Walk the HTML and emit a flat event list per fragment."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.frags: dict[int, list] = {}
        self.order: list[int] = []
        self.cur: int | None = None
        self.stop = False
        self.poem_depth = 0  # depth inside <div class="poem ...">
        self.div_stack: list[bool] = []
        self.in_fsn = False
        self.in_pagenum = False
        self.in_p = False
        self.p_buf: list[str] = []
        self.p_starts_italic = None
        self.fsn_buf: list[str] = []
        self.span_stack: list[str] = []
        self.section = ""
        self.frag_section: dict[int, str] = {}
        self.in_larger = False
        self.label_buf: list[str] = []
        self.labels: dict[int, str] = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div":
            fid = a.get("id", "")
            m = re.fullmatch(r"frag(\d+)", fid)
            if m:
                self.cur = int(m.group(1))
                self.frags[self.cur] = []
                self.order.append(self.cur)
                self.frag_section[self.cur] = self.section
            is_poem = "poem" in (a.get("class") or "").split()
            self.div_stack.append(is_poem)
            if is_poem:
                self.poem_depth += 1
        elif tag in ("h2", "h3"):
            # a new section heading ends the current fragment
            self.cur = None
            self.section = a.get("title", "")
        elif tag == "span":
            cls = a.get("class") or ""
            self.span_stack.append(cls)
            if cls == "fsn":
                self.in_fsn = True
                self.fsn_buf = []
            elif cls == "pagenum":
                self.in_pagenum = True
            elif cls == "larger":
                self.in_larger = True
                self.label_buf = []
        elif tag == "p":
            self.in_p = True
            self.p_buf = []
            self.p_starts_italic = None
        elif tag == "i" and self.in_p and self.p_starts_italic is None:
            # "A. <i>..." (dialogue) and "'<i>...'" also open a literal translation
            self.p_starts_italic = len("".join(self.p_buf).strip()) <= 3
        if self.in_p and tag in ("i", "b", "span") and not self.in_pagenum:
            pass

    def handle_endtag(self, tag):
        if tag == "div":
            if self.div_stack:
                was_poem = self.div_stack.pop()
                if was_poem:
                    self.poem_depth -= 1
                    if self.cur is not None:
                        self.frags[self.cur].append(("poem_end", ""))
        elif tag == "span":
            cls = self.span_stack.pop() if self.span_stack else ""
            if cls == "fsn":
                self.in_fsn = False
                if self.cur is not None:
                    kind = "greek" if self.poem_depth > 0 else "greek_inline"
                    self.frags[self.cur].append((kind, "".join(self.fsn_buf)))
            elif cls == "pagenum":
                self.in_pagenum = False
            elif cls == "larger":
                self.in_larger = False
                if self.cur is not None:
                    self.labels[self.cur] = "".join(self.label_buf).strip()
        elif tag == "p":
            if self.in_p and self.cur is not None:
                text = "".join(self.p_buf)
                kind = "poem_p" if self.poem_depth > 0 else "prose_p"
                self.frags[self.cur].append((kind + ("_i" if self.p_starts_italic else ""), text))
            self.in_p = False

    def _data(self, data):
        if self.in_pagenum:
            return
        if self.in_fsn:
            self.fsn_buf.append(data)
        if self.in_larger:
            self.label_buf.append(data)
        if self.in_p:
            self.p_buf.append(data)

    def handle_data(self, data):
        self._data(data)

    def handle_entityref(self, name):
        self._data("&%s;" % name)

    def handle_charref(self, name):
        self._data("&#%s;" % name)


def parse(path: Path) -> list[dict]:
    raw = Path(path).read_text(encoding="utf-8")
    c = _Collector()
    c.feed(raw)
    out = []
    for idx, n in enumerate(c.order):
        ev = c.frags[n]
        shares_with = None
        label = c.labels.get(n)
        if not ev and idx + 1 < len(c.order):
            # an empty anchor directly followed by the next one: Wharton prints the two numbers as one entry ("7, 8")
            shares_with = c.order[idx + 1]
            ev = c.frags[shares_with]
            label = c.labels.get(shares_with)
        greek: list[str] = []
        inline: list[str] = []
        literal = None
        literal_open = False
        notes: list[str] = []
        for kind, text in ev:
            if literal_open and kind != "poem_p_i":
                literal_open = False
            if kind == "greek":
                if literal is None:
                    greek.append(clean(text))
            elif kind == "greek_inline":
                inline.append(clean(text))
            elif kind in ("poem_p_i", "prose_p_i") and literal is None and greek:
                literal = clean(text)
                literal_open = kind == "poem_p_i"
            elif kind == "poem_p_i" and literal_open:
                literal = literal + " " + clean(text)
            elif kind.startswith("prose_p"):
                t = clean(text)
                if t and t != label:
                    notes.append(t)
        layout = "verse" if greek else ("inline" if inline else "none")
        out.append({
            "wharton_no": n,
            "label": label,
            "shares_entry_with": shares_with,
            "section": c.frag_section.get(n, ""),
            "greek_layout": layout,
            "greek_lines": greek,
            "greek_inline": inline,
            "english_literal": literal,
            "notes": notes,
        })
    # the second number of a shared entry points back to the first
    for f in out:
        if f["shares_entry_with"]:
            for g in out:
                if g["wharton_no"] == f["shares_entry_with"]:
                    g["shares_entry_with"] = f["wharton_no"]
    return out
