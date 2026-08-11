"""Deterministic structural differ for US state bill text.

The narrow claim: this aligns two normalised bill texts by the legislative
section/subsection labels they carry, where those labels can be identified
reliably, and reports added / removed / modified / unchanged / ambiguous
provisions. Where structure cannot be identified it says so and falls back to
block-level text comparison.

It is not semantic comparison, not legal interpretation, not a complete
legislative parser, and it does not guarantee correspondence. Two design rules
carry most of the weight:

1. **Identity is the full path, never the visible marker.** `(1)` under
   subsection 2 is a different provision from `(1)` under subsection 3.
2. **Reused labels are not silently collapsed, and never guessed at.** A path
   that occurs more than once keeps every node, and where the same path repeats
   on both sides the provisions are reported ambiguous rather than paired.
   Pairing them would require a positional or semantic guess, and neither is
   evidence. The same applies to a blank designator: a drafter who left the
   number to the code reviser has not told us the identity, so a blank can be
   paired on exact text and on nothing else.

Nesting is inferred from the local sequence of markers, not from a fixed
precedence: Tennessee runs `SECTION 1.` -> `(19)` -> `(A)`, Missouri runs
`1.2045.` -> `2.` -> `(1)`. A universal hierarchy would mis-nest one of them.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- preamble

# Everything through the enacting clause is boilerplate; comparing it produces
# noise about bill numbers and sponsors rather than about law.
ENACT_RE = re.compile(r"(BE IT ENACTED[^\n]*\n|Be it enacted[^\n]*\n"
                      r"|The people of the state of Wisconsin[^\n]*\n"
                      r"|by deleting all language after the enacting clause and substituting:)", re.I)


def strip_preamble(text: str) -> str:
    m = ENACT_RE.search(text)
    return text[m.end():] if m else text


# ---------------------------------------------------------------- normalisation

_QUOTES = {"“": '"', "”": '"', "‘": "'", "’": "'",
           "–": "-", "—": "-", " ": " ", "−": "-"}


def _unify(text: str) -> str:
    """Whitespace and Unicode variants only. Legally meaningful punctuation stays."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for k, v in _QUOTES.items():
        text = text.replace(k, v)
    return text.replace("\t", " ")


def _norm(s: str) -> str:
    """Comparison form: whitespace collapsed, nothing else removed."""
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- citation masking

# A statutory citation is not structure. `Section 1-3-105(a)` and
# `N.D. Cent. Code § 1-01-49(8)` must stay inside the sentence that cites them,
# so citations are masked out before markers are looked for. Masking preserves
# offsets, and uses a filler that is neither whitespace nor sentence punctuation
# so that context tests treat it as ordinary text.
FILL = "\x00"

CITE_RE = re.compile(
    r"""
      §+[ \t]*[\d][\d\-\.:]*(?:[ \t]*\([\w ]{1,4}\))*     # § 1-01-49(8)
    | \b[A-Z][a-z]*\.\s*(?:[A-Z][a-z]*\.\s*)*                 # N.D. Cent. Code § ...
        (?:Code|Stat|Stats|Laws)\.?\s*(?:Ann\.)?
        (?:[ \t]*§+[ \t]*[\d][\d\-\.:]*)?(?:[ \t]*\([\w ]{1,4}\))*
    | \b(?:[Ss]ection|[Ss]ections|[Ss]ubsection|[Ss]ubsections
        |[Ss]ubdivision|[Ss]ubdivisions|[Cc]hapter|[Cc]hapters
        |[Tt]itle|[Pp]aragraph|[Aa]rticle|[Cc]lause)
        [ \t]+[\d][\d\-\.]*(?:[ \t]*\([\w ]{1,4}\))*           # Section 1-3-105(a)
    | \b\d+[\-\.]\d[\d\-\.]*[ \t]*\([\w]{1,3}\)               # 39-17-2002(a)
    | \b(?:[Ss]ection|[Ss]ections|[Ss]ubsection|[Ss]ubsections
        |[Ss]ubdivision|[Ss]ubdivisions|[Pp]aragraph|[Ss]ubparagraph
        |[Cc]lause|[Ii]tem)s?
        [ \t]*\([ \t]*\w{1,4}[ \t]*\)(?:[ \t]*\([ \t]*\w{1,4}[ \t]*\))*   # subdivision (b)(1)
    | \b(?:ss?|subs?|pars?|subds?|subchs?|chs?|arts?)\.[ \t]*        # Wisconsin style:
        (?:\d[\d\-\.]*)?(?:[ \t]*\([ \t]*\w{1,4}[ \t]*\))*            # sub. (2) (c), s. 180.0103 (8)
    | \b(?:January|February|March|April|May|June|July|August|September
        |October|November|December)\s+\d{1,2}\b               # January 1. -> not a subsection
    """,
    re.X)


# Whatever opens a line is structure and must survive masking. South Carolina
# writes "Section 1-1-1910." as a section heading, which the citation pattern for
# "Section 1-3-105(a)" matches exactly; and a citation closing one line used to
# swallow the designator opening the next, deleting that provision outright.
PROTECTED_RE = re.compile(
    r"(?m)^[ \t]*("
    r"(?:SECTION|SEC\.|Section|Sec\.)[ \t]+[0-9A-Za-z][0-9A-Za-z\-\.]*\."
    r"|\([ \t]*[\w]{0,4}[ \t]*\)"
    r"|\d+[\-\.][\d\-\.]*\d\."
    r")")


def _mask_citations(text: str) -> str:
    protected = [(m.start(1), m.end(1)) for m in PROTECTED_RE.finditer(text)]
    out = list(text)
    for m in CITE_RE.finditer(text):
        if any(m.start() < pe and ps < m.end() for ps, pe in protected):
            continue                     # overlaps something that opens a line
        for i in range(m.start(), m.end()):
            if out[i] != "\n":          # keep line structure intact
                out[i] = FILL
    return "".join(out)


# ---------------------------------------------------------------- markers

MARKER_RE = re.compile(
    # A section marker, only at the start of a line. Mid-line it is prose or a
    # citation: Idaho's title recites "A NEW SECTION 5-346, IDAHO CODE", and a bill
    # may write "nothing in this SECTION 1. shall be construed".
    r"(?:(?m:^)[ \t]*)(?P<sec>(?:SECTION|SEC\.|Section|Sec\.)[ \t]+[0-9A-Za-z][0-9A-Za-z\-\.]*\.)"
    # A statute-style section number opening a line: "1.2045.", "39-17-2002."
    r"|(?:(?m:^)[ \t]*)(?P<statsec>\d+[\-\.][\d\-\.]*\d\.)"
    # A numbered subsection: "2. For purposes of this section..."
    r"|(?P<sub>\d{1,3}\.(?=[ \t]+[A-Z\"(]))"
    # Parenthesised designators, including Tennessee's blank "( )" placeholder and
    # the "(a-1)" form used for a subsection inserted between existing siblings.
    r"|(?P<par>\([ \t]*(?:\d{1,3}[a-z]?|[a-z]{1,2}-?\d{0,2}|[A-Z]{1,2}-?\d{0,2})?[ \t]*\))"
)

# A designator only opens a provision at the start of a line or after the close
# of the previous one. `(a)` following an alphanumeric token is part of a
# citation or a sentence, not structure.
_OPENERS = set(".;:)—") | {FILL}   # FILL: a masked citation may precede a designator

_TYPE = {"sec": "sec", "statsec": "sec", "sub": "sub"}


def _marker_type(kind: str, raw: str) -> str:
    if kind in _TYPE:
        return _TYPE[kind]
    inner = raw.strip("()").strip()
    if not inner:
        return "blank"
    if inner.isdigit():
        return "num"
    return "alpha" if inner.islower() else "ALPHA"


def _context_ok(masked: str, start: int, kind: str) -> bool:
    if kind in ("sec", "statsec"):
        return True
    i = start - 1
    while i >= 0 and masked[i] in " \t":
        i -= 1
    if i < 0 or masked[i] == "\n":
        return True                      # start of a line
    return masked[i] in _OPENERS         # ". (1)", "; (b)", ": (a)"


def _label_key(raw: str) -> str:
    lab = re.sub(r"\s+", "", raw)
    lab = re.sub(r"^(SECTION|SEC\.|Section|Sec\.)", "", lab)
    return lab.rstrip(".") or "()"


def _label_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw).strip()


# ---------------------------------------------------------------- nodes

@dataclass(frozen=True)
class LegislativeNode:
    path: tuple          # identity: ("1", "2", "(1)") — parent context included
    labels: tuple        # as printed: ("SECTION 1.", "2.", "(1)")
    level: int
    marker: str | None
    text: str            # comparison form
    raw_text: str        # display form
    start: int
    end: int
    confidence: str      # "labelled" | "blank_label"
    ordinal: int = 1     # position among provisions sharing this path, 1-based


@dataclass
class ParseResult:
    nodes: list
    structural: bool
    warnings: list = field(default_factory=list)


def parse(text: str) -> ParseResult:
    """Split legislative text into structurally identified provisions."""
    text = _unify(text)
    masked = _mask_citations(text)
    marks = []
    for m in MARKER_RE.finditer(masked):
        kind = m.lastgroup
        s, e = m.start(kind), m.end(kind)
        if not _context_ok(masked, s, kind):
            continue
        marks.append((s, e, kind, text[s:e]))

    warnings = []
    if len(marks) < 3:
        return ParseResult([], False, ["fewer than three structural markers found"])

    nodes, stack = [], []
    first_depth: dict = {}
    seen_paths: dict = {}
    for i, (s, e, kind, raw) in enumerate(marks):
        stop = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        t = _marker_type(kind, raw)
        body_raw = _norm(text[e:stop])
        entry = (t, _label_key(raw), _label_text(raw))
        if t == "sec":
            stack = [entry]
        else:
            types = [x[0] for x in stack]
            if t in types:                       # a sibling: unwind to its level
                stack = stack[:types.index(t)] + [entry]
            else:                                # a new depth beneath the current one
                stack = stack + [entry]
        # "(i)" is both the ninth letter and roman one. Nothing in the text settles
        # which, and the stack will treat it as a letter sibling — which is wrong if
        # the drafter meant a roman child. Say so rather than hide it.
        if t == "alpha" and raw.strip("()").strip() in ("i", "v", "x"):
            w = (f"designator '{_label_text(raw)}' is ambiguous between a letter and a "
                 f"roman numeral; its nesting may be wrong")
            if w not in warnings:
                warnings.append(w)

        depth = len(stack) - 1
        if t != "sec" and first_depth.setdefault(t, depth) != depth:
            w = f"designator type '{t}' is used at more than one depth in this text"
            if w not in warnings:
                warnings.append(w)

        if not body_raw:
            continue
        path = tuple(x[1] for x in stack)
        seen_paths[path] = seen_paths.get(path, 0) + 1
        nodes.append(LegislativeNode(
            path=path,
            labels=tuple(x[2] for x in stack),
            level=len(stack) - 1,
            marker=_label_text(raw),
            text=_norm(body_raw),
            raw_text=body_raw,
            start=s, end=stop,
            confidence="blank_label" if t == "blank" else "labelled",
            # Position among provisions sharing this path. Used to keep them
            # distinguishable for a reader — never to align them across versions,
            # which would be positional guessing.
            ordinal=seen_paths[path]))

    if not nodes:
        return ParseResult([], False, ["markers found but no provision bodies"])

    body_chars = sum(len(n.text) for n in nodes)
    total_chars = len(_norm(text)) or 1
    coverage = body_chars / total_chars
    if coverage < 0.5:
        warnings.append(f"structural markers cover only {coverage:.0%} of the text")
        return ParseResult(nodes, False, warnings)

    dup = len(nodes) - len({n.path for n in nodes})
    if dup:
        warnings.append(f"{dup} provision(s) share a structural path with another")
    return ParseResult(nodes, True, warnings)


# ---------------------------------------------------------------- alignment

@dataclass
class DiffEntry:
    kind: str            # unchanged | added | removed | modified | ambiguous
    label: str
    old: str | None
    new: str | None
    note: str = ""


@dataclass
class DiffResult:
    mode: str            # "structural" | "fallback"
    nodes_total: int = 0
    unchanged: int = 0
    added: int = 0
    removed: int = 0
    modified: int = 0
    renumbered: int = 0
    ambiguous: int = 0
    parser_warnings: list = field(default_factory=list)
    entries: list = field(default_factory=list)

    @property
    def changed(self):
        return self.added + self.removed + self.modified


_QUOTED = re.compile(r'"([^"]{2,60})"')


def _group(nodes):
    out = {}
    for n in nodes:
        out.setdefault(n.path, []).append(n)
    return out


def _lab(n):
    lab = " ".join(n.labels)
    return f"{lab} ·{n.ordinal}" if n.ordinal > 1 else lab


def diff_nodes(A, Z, warnings=None) -> DiffResult:
    """Align two provision lists, then classify each aligned slot.

    Two passes, in this order:

    **Text identity.** A provision whose exact normalised text occurs once in each
    version is the same provision, wherever it sits. This catches renumbering —
    the commonest legislative edit, since inserting one subdivision shifts every
    later one — which path identity alone would report as a removal plus an
    addition. Uniqueness on both sides is required, so boilerplate that recurs
    («Does not include artificial intelligence…» appears three times in
    Tennessee SB 837 as introduced) is never paired this way, and is reported as a
    removal and an addition instead. An earlier version inferred those pairings
    from an ancestor's move; that inference was withdrawn after external review,
    because a parent's redesignation is not evidence about its children.

    **Structural path.** Everything left is matched on the full path, parent
    context included, never on the visible marker. Where a path is reused, a
    secondary key is tried; if that cannot separate the nodes, they are reported
    ambiguous rather than compared.
    """
    r = DiffResult(mode="structural", parser_warnings=_dedupe(warnings))
    aidx = {id(n): i for i, n in enumerate(A)}
    zidx = {id(n): i for i, n in enumerate(Z)}

    ca, cz = {}, {}
    for n in A: ca[n.text] = ca.get(n.text, 0) + 1
    for n in Z: cz[n.text] = cz.get(n.text, 0) + 1
    zfirst = {}
    for n in Z: zfirst.setdefault(n.text, n)

    matches, taken_z = [], set()
    for a in A:
        if ca[a.text] == 1 and cz.get(a.text) == 1:
            z = zfirst[a.text]
            matches.append((a, z, "unchanged" if a.path == z.path else "renumbered"))
            taken_z.add(id(z))

    A2 = [a for a in A if not any(a is m[0] for m in matches)]
    Z2 = [z for z in Z if id(z) not in taken_z]

    removed, added, ambiguous = [], [], []

    # Definitions are identified by the term they define, not by their number. A
    # bill that inserts one definition renumbers every later one, and aligning
    # those by designator would report that "Emergent properties" was amended into
    # "Developer". Applied only where every sibling on both sides opens with a
    # quoted term and those terms are unique — otherwise it does not fire.
    A2, Z2, defmatches = _align_definitions(A2, Z2)
    matches += defmatches
    GA, GZ = _group(A2), _group(Z2)
    for path in list(GA) + [p for p in GZ if p not in GA]:
        a_list, z_list = GA.get(path, []), GZ.get(path, [])
        if any(n.confidence == "blank_label" for n in a_list + z_list):
            # A blank designator carries no identity — the drafter left the number to
            # the code reviser — so the path cannot pair it, and pairing the residue
            # would be a positional guess. Exact text already had its chance above.
            if a_list and z_list:
                ambiguous += a_list + z_list
                r.parser_warnings.append(
                    f"designator {'/'.join(path)} is blank in both versions; identity was "
                    f"not established")
            else:
                removed.extend(a_list)
                added.extend(z_list)
            continue

        if len(a_list) <= 1 and len(z_list) <= 1:
            if a_list and z_list:
                a, z = a_list[0], z_list[0]
                matches.append((a, z, "unchanged" if a.text == z.text else "modified"))
            elif a_list:
                removed.append(a_list[0])
            else:
                added.append(z_list[0])
            continue

        if not a_list or not z_list:
            # A reused designator with nothing on the other side to align to is
            # simply an addition or a removal. There is no ambiguity to report.
            removed.extend(a_list)
            added.extend(z_list)
            continue

        # A designator that repeats on both sides cannot be aligned without a
        # positional or semantic guess, and neither is evidence. Abstain: every
        # provision is retained and reported, none is paired.
        ambiguous += a_list + z_list
        r.parser_warnings.append(
            f"designator {'/'.join(path)} occurs {len(a_list)}x in the earlier version and "
            f"{len(z_list)}x in the later one; identity was not established")

    # Reading order: follow the earlier version, and place a provision that exists
    # only in the later version after whatever preceded it there.
    anchors = sorted(((zidx[id(z)], aidx[id(a)]) for a, z, _ in matches))

    def anchor(z):
        j, last = zidx[id(z)], -1
        for zj, ai in anchors:
            if zj < j: last = ai
            else: break
        return last

    slots = []
    for a, z, kind in matches:
        slots.append(((aidx[id(a)], 0), a, z, kind))
    for a in removed:
        slots.append(((aidx[id(a)], 0), a, None, "removed"))
    for z in added:
        slots.append(((anchor(z), 1, zidx[id(z)]), None, z, "added"))
    for n in ambiguous:
        key = ((aidx[id(n)], 0) if id(n) in aidx else (anchor(n), 1, zidx[id(n)]))
        slots.append((key, n, None, "ambiguous"))
    slots.sort(key=lambda s: (s[0][0], s[0][1], s[0][2] if len(s[0]) > 2 else 0))

    for _, a, z, kind in slots:
        r.nodes_total += 1
        setattr(r, kind, getattr(r, kind) + 1)
        if kind == "renumbered":
            r.entries.append(DiffEntry(kind, f"{_lab(a)} → {_lab(z)}", a.raw_text, z.raw_text,
                                       f"Same text, redesignated {_lab(a)} → {_lab(z)}."))
        elif kind == "ambiguous":
            r.entries.append(DiffEntry(kind, _lab(a), a.raw_text, None,
                                       "Repeated structural labels prevented a unique alignment "
                                       "for this provision."))
        elif kind == "modified" and a.path != z.path:
            r.entries.append(DiffEntry(kind, f"{_lab(a)} → {_lab(z)}", a.raw_text, z.raw_text,
                                       f"Redesignated {_lab(a)} → {_lab(z)} and amended."))
        else:
            r.entries.append(DiffEntry(kind, _lab(a or z),
                                       a.raw_text if a else None, z.raw_text if z else None))
    return r


def _defined_term(n):
    """The term a definitional provision defines, or None if it is not one."""
    t = n.text.lstrip()
    if not t.startswith('"'):
        return None
    m = _QUOTED.match(t)
    return m.group(1).strip().lower() if m else None


def _align_definitions(A, Z):
    """Match sibling definitions by defined term. Returns the unmatched remainder."""
    matches = []
    used = set()
    pa, pz = {}, {}
    for n in A: pa.setdefault(n.path[:-1], []).append(n)
    for n in Z: pz.setdefault(n.path[:-1], []).append(n)
    for parent, alist in pa.items():
        zlist = pz.get(parent)
        if not zlist or len(alist) < 2 or len(zlist) < 2:
            continue
        ta = [_defined_term(n) for n in alist]
        tz = [_defined_term(n) for n in zlist]
        if any(t is None for t in ta + tz):
            continue                                  # not a definitions list
        if len(set(ta)) != len(ta) or len(set(tz)) != len(tz):
            continue                                  # a term repeats; do not guess
        mz = dict(zip(tz, zlist))
        for t, a in zip(ta, alist):
            z = mz.get(t)
            if z is None:
                continue
            matches.append((a, z, "unchanged" if a.text == z.text else "modified"))
            used.add(id(a)); used.add(id(z))
    return ([n for n in A if id(n) not in used],
            [n for n in Z if id(n) not in used],
            matches)


def _dedupe(seq):
    out = []
    for x in (seq or []):
        if x not in out: out.append(x)
    return out


# ---------------------------------------------------------------- fallback

def _blocks(text):
    text = _unify(strip_preamble(text))
    return [_norm(b) for b in re.split(r"\n[ \t]*\n", text) if _norm(b)]


def fallback_diff(a_text, z_text, warnings=None) -> DiffResult:
    """Block-level comparison, used only when structure cannot be identified.

    Blocks carry no identity, so this reports additions and removals and makes no
    claim that any pair of them is the same provision changed.
    """
    r = DiffResult(mode="fallback", parser_warnings=list(warnings or []))
    A, Z = _blocks(a_text), _blocks(z_text)
    sm = difflib.SequenceMatcher(a=A, b=Z, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for t in A[i1:i2]:
                r.nodes_total += 1; r.unchanged += 1
                r.entries.append(DiffEntry("unchanged", "", t, t))
        else:
            for t in A[i1:i2]:
                r.nodes_total += 1; r.removed += 1
                r.entries.append(DiffEntry("removed", "", t, None))
            for t in Z[j1:j2]:
                r.nodes_total += 1; r.added += 1
                r.entries.append(DiffEntry("added", "", None, t))
    return r


# ---------------------------------------------------------------- entry point

def diff_texts(a_text: str, z_text: str) -> DiffResult:
    """Compare two bill texts, structurally where that is defensible."""
    pa, pz = parse(strip_preamble(a_text)), parse(strip_preamble(z_text))
    warn = []
    for side, p in (("earlier", pa), ("later", pz)):
        warn += [f"{side} version: {w}" for w in p.warnings]
    if pa.structural and pz.structural:
        return diff_nodes(pa.nodes, pz.nodes, warn)
    warn.insert(0, "structural parsing was not reliable; compared at text level")
    return fallback_diff(a_text, z_text, warn)
