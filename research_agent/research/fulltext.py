"""Full text as a citable structure, not a blob.

A source used to be one string: whatever the HTML cleaner returned, truncated,
with no notion of where a sentence sat in the document. That is enough to judge
relevance and it is not enough to make a claim. A scientist writing "the
heritability estimate rose with age" has to be able to say which section, which
page, and which sentence they mean - otherwise the sentence is a paraphrase of a
research summary, and nobody can check it.

This module is deliberately dependency-free and deterministic: section
detection, paragraph chunks with offsets, and the search for a quoted passage in
the text. It is run on every extracted fact, so it must be cheap and it must
never depend on the LLM being reachable.

Known limitation: two-column PDFs come out of the text extractor interleaved, so
a heading can end up in the middle of a line. Section detection then finds fewer
sections than the paper has. Offsets and quotes stay correct either way - they
refer to the extracted text, which is what gets stored and shown.
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


# Canonical section names and the spellings they appear under. Order matters
# only for readability; the longest alias wins in `_canonical_section`.
SECTION_ALIASES: Dict[str, Tuple[str, ...]] = {
    "abstract": ("abstract", "summary", "structured abstract"),
    "introduction": ("introduction", "background", "background and aims"),
    "methods": (
        "methods", "method", "materials and methods", "methods and materials",
        "methodology", "patients and methods", "subjects and methods",
        "experimental procedures", "study design", "data and methods",
    ),
    "results": ("results", "findings", "results and discussion"),
    "discussion": ("discussion", "general discussion", "interpretation"),
    "conclusion": ("conclusion", "conclusions", "concluding remarks",
                   "limitations", "strengths and limitations"),
    "references": ("references", "bibliography", "literature cited",
                   "works cited", "reference list"),
    "acknowledgements": (
        "acknowledgements", "acknowledgments", "funding", "author contributions",
        "conflict of interest", "conflicts of interest", "competing interests",
        "data availability", "code availability", "supplementary material",
        "supplementary information",
    ),
}

# Priority used when a long document has to be trimmed to a prompt budget: what a
# scientist reads first is not the same as what comes first in the file.
SECTION_PRIORITY: Dict[str, float] = {
    "abstract": 3.0,
    "results": 2.5,
    "discussion": 2.0,
    "conclusion": 1.8,
    "methods": 1.5,
    "introduction": 1.0,
    "acknowledgements": 0.1,
    "references": 0.0,
}

_HEADING_MAX_CHARS = 90
_HEADING_MAX_WORDS = 12
_NUMBERING_RE = re.compile(
    r"^\s*(?:\d{1,2}(?:\.\d{1,2})*\.?|[IVXLC]{1,6}\.)\s+", re.IGNORECASE
)
_TRANSLATE = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2032": "'",
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-",
    "\u2014": "-", "\u2212": "-", "\u00ad": "", "\u00a0": " ",
    "\u2026": " ", "\u200b": "", "\t": " ",
})
_ELLIPSIS_RE = re.compile(r"\[\.+\]|\(\.+\)|\.\.\.")
_WORD_RE = re.compile(r"[^\s]+")


@dataclass
class QuoteSpan:
    """Where a quoted passage sits in the extracted text."""

    start: int
    end: int
    exact: bool = True

    @property
    def length(self) -> int:
        return max(0, self.end - self.start)


def _canonical_section(line: str) -> str:
    """Canonical name for a heading line ('' when it is not a heading)."""
    raw = (line or "").strip()
    if not raw or len(raw) > _HEADING_MAX_CHARS:
        return ""
    stripped = _NUMBERING_RE.sub("", raw).strip(" .:—-–")
    if not stripped or len(stripped.split()) > _HEADING_MAX_WORDS:
        return ""
    candidate = re.sub(r"\s+", " ", stripped).strip().lower()
    best = ""
    best_alias = 0
    for name, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if candidate == alias or candidate.startswith(alias + " "):
                if len(alias) > best_alias:
                    best, best_alias = name, len(alias)
    if best:
        return best
    # ALL-CAPS headings without a known name ("STATISTICAL ANALYSIS").
    if stripped.isupper() and 1 <= len(stripped.split()) <= 6:
        return candidate
    return ""


def split_sections(text: str) -> List[dict]:
    """Split a document into sections with character offsets.

    Returns ``[{"title", "key", "start", "end", "is_references"}]`` covering the
    whole text in order. A document without recognizable headings yields one
    section titled "Full text" - the caller can still cite offsets in it.
    """
    body = text or ""
    if not body.strip():
        return []

    lines = body.splitlines(keepends=True)
    offsets: List[int] = []
    pos = 0
    for line in lines:
        offsets.append(pos)
        pos += len(line)

    found: List[Tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        key = _canonical_section(line)
        if not key:
            continue
        found.append((offsets[index], line.strip(), key))

    if not found:
        return [{"title": "Full text", "key": "full_text", "start": 0,
                 "end": len(body), "is_references": False}]
    if len(found) == 1 and found[0][0] > len(body) * 0.15:
        # A single keyword late in the document is usually a mention, not a
        # heading; one block is more honest than a made-up split.
        return [{"title": "Full text", "key": "full_text", "start": 0,
                 "end": len(body), "is_references": False}]

    sections: List[dict] = []
    if found and found[0][0] > 0:
        sections.append({
            "title": "Front matter", "key": "front_matter", "start": 0,
            "end": found[0][0], "is_references": False,
        })
    for i, (start, title, key) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(body)
        if end <= start:
            continue
        sections.append({
            "title": title, "key": key, "start": start, "end": end,
            "is_references": key == "references",
        })
    return sections or [{"title": "Full text", "key": "full_text", "start": 0,
                         "end": len(body), "is_references": False}]


def section_for_offset(sections: Sequence[dict], offset: int) -> str:
    """Title of the section containing ``offset`` ('' when unknown)."""
    if offset < 0:
        return ""
    for section in sections or ():
        try:
            if int(section.get("start", 0)) <= offset < int(section.get("end", 0)):
                return str(section.get("title", ""))
        except (TypeError, ValueError):
            continue
    return ""


def page_offsets(
    pages: Sequence[str], prefix: int = 0, separator: str = "\n\n"
) -> List[List[int]]:
    """Character ranges for each page inside the joined document text.

    Must mirror how the extractor joins pages (stripped, separated by a blank
    line) plus the ``prefix`` of any title put in front of them. Used to turn a
    quote's offset into "page 4".
    """
    out: List[List[int]] = []
    pos = max(0, int(prefix))
    for number, page in enumerate(pages or (), start=1):
        segment = (page or "").strip()
        start = pos
        out.append([start, start + len(segment), number])
        pos = start + len(segment) + len(separator)
    return out


def page_for_offset(page_offsets: Optional[Sequence[Sequence[int]]], offset: int) -> int:
    """1-based page number for a character offset (-1 when unknown)."""
    if offset < 0 or not page_offsets:
        return -1
    for entry in page_offsets:
        try:
            start, end, page = int(entry[0]), int(entry[1]), int(entry[2])
        except (TypeError, ValueError, IndexError):
            continue
        if start <= offset < end:
            return page
    return -1


def paragraphs(text: str, start: int = 0, end: Optional[int] = None) -> List[dict]:
    """Paragraph-ish blocks inside ``text[start:end]`` with absolute offsets."""
    body = text or ""
    end = len(body) if end is None else min(int(end), len(body))
    start = max(0, min(int(start), end))
    chunks: List[dict] = []
    for match in re.finditer(r"[^\n]+(?:\n[^\n]+)*", body[start:end]):
        raw = match.group(0)
        left = len(raw) - len(raw.lstrip())
        right = len(raw.rstrip())
        if right <= left:
            continue
        chunk = raw[left:right]
        if len(chunk) < 40:
            continue
        chunks.append({
            "start": start + match.start() + left,
            "end": start + match.start() + right,
            "text": chunk,
        })
    return chunks


def _normalize_with_index(text: str) -> Tuple[str, List[int]]:
    """Lowercase, de-hyphenated, whitespace-collapsed text plus a back-map.

    The back-map turns a match in the normalized string into a range in the
    original, which is what gets stored and shown.
    """
    body = _ELLIPSIS_RE.sub(" ", text or "").translate(_TRANSLATE)
    out: List[str] = []
    index: List[int] = []
    i = 0
    n = len(body)
    pending_space = False
    while i < n:
        char = body[i]
        if char.isspace():
            pending_space = bool(out)
            i += 1
            continue
        # End-of-line hyphenation: "poly-\ngenic" is one word.
        if (char == "-" and i + 1 < n and body[i + 1] in "\r\n"
                and out and out[-1].isalpha()):
            j = i + 1
            while j < n and body[j] in "\r\n":
                j += 1
            if j < n and body[j].isalpha():
                i = j
                continue
        if pending_space:
            out.append(" ")
            index.append(i)
            pending_space = False
        out.append(char.lower())
        index.append(i)
        i += 1
    return "".join(out), index


def _words(text: str) -> List[str]:
    return _WORD_RE.findall(text or "")


def _anchor_pattern(words: Sequence[str]) -> Optional[re.Pattern]:
    if not words:
        return None
    return re.compile(r"\b" + r"\W+".join(re.escape(w) for w in words), re.IGNORECASE)


def locate_quote(text: str, quote: str, anchor_words: int = 6) -> Optional[QuoteSpan]:
    """Find ``quote`` in ``text`` and return its character range.

    Two passes: an exact match on normalized text (which already forgives line
    breaks, hyphenation, curly quotes and dropped ellipses), then an anchored
    fuzzy pass for quotes the model paraphrased slightly. The fuzzy pass only
    accepts a span when most of the quote's words actually occur in it, and it
    reports ``exact=False`` so the caller can treat the citation as weaker.
    """
    body = text or ""
    needle = (quote or "").strip()
    if not body or len(needle) < 12:
        return None

    norm_body, index = _normalize_with_index(body)
    norm_quote, _ = _normalize_with_index(needle)
    norm_quote = norm_quote.strip()
    if len(norm_quote) < 12:
        return None

    found = norm_body.find(norm_quote)
    if found >= 0:
        start = index[found]
        end = index[found + len(norm_quote) - 1] + 1
        return QuoteSpan(start=start, end=end, exact=True)

    words = _words(norm_quote)
    if len(words) < 4:
        return None
    head = words[:min(anchor_words, len(words))]
    tail = words[-min(anchor_words, len(words)):]
    head_pattern = _anchor_pattern(head)
    if head_pattern is None:
        return None
    match = head_pattern.search(norm_body)
    if not match:
        return None

    # Extend to the end of the quote's last words, but do not run away.
    window_end = min(len(norm_body), match.start() + len(norm_quote) * 3 + 200)
    window = norm_body[match.start():window_end]
    tail_pattern = _anchor_pattern(tail)
    tail_match = tail_pattern.search(window) if tail_pattern else None
    if tail_match:
        span_end_norm = match.start() + tail_match.end()
    else:
        span_end_norm = match.start() + len(norm_quote)

    candidate = norm_body[match.start():span_end_norm]
    candidate_words = _words(candidate)
    if not candidate_words:
        return None
    overlap = len(set(candidate_words) & set(words)) / max(1, len(set(words)))
    if overlap < 0.8:
        return None
    start = index[match.start()]
    end = index[min(len(index) - 1, span_end_norm - 1)] + 1
    return QuoteSpan(start=start, end=end, exact=False)


def _terms(terms: Optional[Iterable[str]]) -> List[str]:
    out = []
    for term in terms or ():
        value = (term or "").strip().lower()
        if len(value) >= 3 and value not in out:
            out.append(value)
    return out


def select_text(
    text: str,
    terms: Optional[Iterable[str]] = None,
    budget: int = 9000,
    sections: Optional[Sequence[dict]] = None,
) -> str:
    """The most informative slice of a long document within ``budget`` chars.

    Takes paragraphs from the sections that carry findings, ranked by how often
    the topic terms occur in them, and returns them in document order. Quotes are
    still located in the *full* text, so trimming the prompt does not shift any
    stored offset.
    """
    body = text or ""
    if budget <= 0 or len(body) <= budget:
        return body
    sections = list(sections or split_sections(body))
    wanted = _terms(terms)

    scored: List[dict] = []
    for section in sections:
        if section.get("is_references"):
            continue
        priority = SECTION_PRIORITY.get(str(section.get("key", "")), 0.5)
        for chunk in paragraphs(body, int(section.get("start", 0)),
                                int(section.get("end", len(body)))):
            lowered = chunk["text"].lower()
            hits = sum(lowered.count(term) for term in wanted)
            scored.append({**chunk, "score": priority + 2.0 * hits})

    if not scored:
        return body[:budget]

    chosen: List[dict] = []
    used = 0
    for chunk in sorted(scored, key=lambda c: (-c["score"], c["start"])):
        size = len(chunk["text"]) + 2
        if used + size > budget:
            # One paragraph can be bigger than the whole budget. That is the rule
            # rather than the exception in PDF text, where paragraph breaks are
            # often missing, and such a chunk used to be skipped outright - so a
            # long document could shrink to a few stray sentences. Take the part
            # that still fits instead.
            room = budget - used
            if room < 500:
                continue
            head = chunk["text"][: room - 2]
            chosen.append({**chunk, "text": head})
            used += len(head) + 2
            break
        chosen.append(chunk)
        used += size
        if used >= budget * 0.95:
            break
    if not chosen:
        return body[:budget]
    chosen.sort(key=lambda c: c["start"])
    return "\n\n".join(chunk["text"] for chunk in chosen)
