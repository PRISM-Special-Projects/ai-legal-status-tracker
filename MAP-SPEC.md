# Specification — geographic state map for the AI Legal Status Tracker

> **Status: implemented in-house, not handed out.** This was written as a brief for an external
> implementer and then built here instead, in the commit that adds this file. It is kept because it
> is the design record — the reasoning, the rejected alternatives, and the acceptance criteria the
> build was checked against — and because it is the basis for red-teaming the result. Where it
> disagrees with `site/build.py`, the artefact governs; §10 lists every departure.

You are being asked to build one component: a recognisable map of the United States that replaces
the abstract tile grid currently used for orientation on the tracker's landing page. This document
is the whole brief. It states the constraints you must not break, the contract the component must
satisfy, and the tests it must pass. Where it is silent, ask rather than choose.

Repository: `https://github.com/PRISM-Special-Projects/ai-legal-status-tracker` (public).
Read against commit `088654c` or later.

```
Deliverable    a function in site/build.py that returns the map's HTML, plus its CSS, a vendored
               geometry file, its licence notice, and one provenance entry
Language       Python 3.12, standard library only. No pip install, at build time or ever
Runtime        static HTML/CSS/JS. No fetch, no CDN, no external font, no build step
Existing code  site/build.py — 1,225 lines, emits 58 files into site/dist/
Local preview  launch config `ai-legal-status` on :5201, or serve site/dist/ any way you like
Geometry       do NOT write a projection — adapt us-atlas, which ships one pre-applied (§3)
```

---

## 1. Why this is being built, and what was wrong with the argument against it

The tracker holds 23 bills across 12 states. The landing page currently orients the reader with an
**equal-area tile grid** — a 12-column lattice of squares, one per state, geography approximate,
built as a filter control rather than a map. The pre-build design document rejected a map on the
grounds that a choropleth "shows 12 of 50 states, renders Missouri's six bills as one flat colour,
and says nothing about the amendment diffs that are our actual differentiator."

That argument is sound about a **colour ramp** and wrong about **geography**. It was later extended,
by me, into a rejection of any real map, which conflated the two. The separable facts:

- Encoding a **quantity** by area or by shade is genuinely bad here. Eight of the twelve states hold
  exactly one bill, so a ramp encodes noise as intensity; and Missouri's six bills disagree with
  each other, so one shade for Missouri asserts a homogeneity that does not exist.
- **None of that applies to a recognisable outline with categorical fill.** The map's assigned job
  is orientation and navigation. Recognition is the entire value of that job, and an abstract
  lattice is worse at it than the shape of the country: a journalist or legislative staffer finds
  Tennessee on a US map instantly and has to decode a grid to find it on ours.
- The tile grid's own justification — equal-area cells stop small states vanishing — does not bind
  this registry. The smallest of the twelve states are South Carolina and Ohio, both comfortably
  large enough to click. The design solves a problem this data does not have.

So: build the map. Keep the ramp out of it.

## 2. The rule that governs every design decision here

This project is **descriptive, not evaluative**. It records what bills say; it does not rank, score,
or grade them, and it does not imply an ordering it has not established. In practice, for this
component:

- **No sequential or diverging colour scale. No graded fill of any kind.** Fill is categorical and
  two-valued: the state holds at least one bill in this registry, or it does not.
- **Counts appear as numerals, not as intensity.** `MO 6` is exact and cannot be misread as
  temperature. A six-step shade ramp from 1 to 6 can.
- **No third fill state that implies a judgement** — nothing for "active", "leading", "most
  advanced", "strongest". If you find yourself wanting one, that is the signal to stop and ask.
- **A blank state means "no bill in this registry", never "no legislation exists".** The registry's
  inclusion methodology is not yet established, so absence in it is not a finding about the world.
  The existing caveat copy must be carried over; §5 gives it verbatim.

A reviewer will check this component against that rule specifically. A beautiful choropleth is a
rejected deliverable, not a near miss.

## 3. Geometry: adapt `us-atlas`, do not project anything yourself

Do not write a projection. Do not download and simplify Census shapefiles. Use **`us-atlas`**
(`https://github.com/topojson/us-atlas`), which publishes exactly the asset this component needs,
already projected. I verified the following against `us-atlas@3` rather than recalling it:

```
File        states-albers-10m.json        (https://unpkg.com/us-atlas@3/states-albers-10m.json)
Size        82,031 bytes
Projection  ALREADY APPLIED — d3.geoAlbersUsa().scale(1300).translate([487.5, 305]),
            fitted to a 975×610 viewport, with the Alaska and Hawaii insets baked in
            (Alaska lands near y≈551, Hawaii near y≈584 — bottom-left, as wanted)
Contents    objects.states → 51 geometries: the 50 states + District of Columbia.
            No Puerto Rico, which matches this registry's scope exactly
Identity    geometry.id = two-digit FIPS code · geometry.properties.name = "Missouri"
Encoding    TopoJSON: quantized, delta-encoded arcs plus a transform {scale, translate}
Licence     ISC, Copyright 2013-2019 Michael Bostock; underlying data is US Census, public domain
```

This deletes the whole projection problem. What remains is a TopoJSON decode, which is thirty lines
of standard library. **This is verified working code, not a sketch** — it decoded all 51 geometries
and the output lands in the expected coordinate space:

```python
def decode(topo):
    """TopoJSON -> {fips: (name, svg_path_d)}. Standard library only."""
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:                       # delta-encoded and quantized
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx; y += dy
            p = (round(x * sx + tx), round(y * sy + ty))
            if not pts or p != pts[-1]:            # integer precision: see note below
                pts.append(p)
        arcs.append(pts)

    def ring(idxs):
        out = []
        for i in idxs:                             # negative index = arc traversed backwards
            seg = arcs[~i][::-1] if i < 0 else arcs[i]
            out.extend(seg if not out else seg[1:])
        return out

    def path(geom):
        polys = geom["arcs"] if geom["type"] == "MultiPolygon" else [geom["arcs"]]
        return "".join("M" + "L".join(f"{x},{y}" for x, y in ring(r)) + "Z"
                       for poly in polys for r in poly)

    return {g["id"]: (g["properties"]["name"], path(g))
            for g in topo["objects"]["states"]["geometries"]}
```

Three findings from running it, all of which you would otherwise hit yourself:

- **Do not hard-code `viewBox="0 0 975 610"`.** The file's own bbox is
  `[-57.66, 12.98, 957.52, 606.57]` — some Aleutian geometry sits left of zero, and a 975×610 box
  clips it. Derive the `viewBox` from `topo["bbox"]`, rounded outwards.
- **Round to integers.** The rendered map is about 720 CSS px wide against a 975-unit viewBox, so
  sub-pixel precision buys nothing: full precision is 108 KB of inline path data, two decimals is
  126 KB, integers are **69 KB — 22.8 KB gzipped**, which is the number that matters since GitHub
  Pages serves compressed. The landing page is 63 KB today. If you want it smaller, Alaska's
  Aleutian arcs alone are ~12 KB of the total and a point-tolerance filter is the lever; say so
  rather than silently degrading the lower 48.
- **`id` is FIPS, and this registry keys on postal codes.** You need a 51-row FIPS→USPS table.
  Put it in `site/build.py` beside the geometry loader, derive it from a citable source rather than
  typing it from memory, and assert its completeness against the decoded geometries (§7).

Provenance, following the standard this repository already applies to bill texts:

1. **Vendor the file** at `site/geo/states-albers-10m.json`, committed, unmodified. Record which
   version you took and from where.
2. **Record it** in `registry/source_manifest.json`, in a new `geometry` group beside the existing
   `documents` and `texts` groups, with `path`, `sha256` and `bytes`. Extend the hash loop in
   `registry/validate.py` (near line 195, currently `for group in ("documents", "texts")`) to cover
   the new group, so altered geometry fails validation exactly as an altered bill text does.
3. **Satisfy the licence.** ISC requires the copyright and permission notice to appear in all
   copies. Vendor it as `site/geo/LICENSE-us-atlas` and reference it from `LICENSE-DATA`, which is
   where this repository already accounts for third-party data terms.
4. **No network at build time or run time.** The file is fetched once, by hand, and committed. A
   refresh script may live in the repo but must never run in CI or in `build.py`.

If you conclude `us-atlas` is the wrong base, that is a legitimate finding — say why, and name what
you would use instead. What is not acceptable is hand-rolling a projection because it was not
checked whether a projected asset exists.

**Alternatives considered and rejected**, so the next person can attack the reasoning rather than
repeat the search:

| Candidate | Why not |
|---|---|
| `pdil/usmap` | An R package — `Depends: R (>= 3.5.0)`, `Imports: rlang, usmapdata`, **GPL (>= 3)**. Three problems: CI installs no dependencies by design, so R is a large concession for one SVG; its output is a ggplot2 figure, which cannot carry the per-state buttons and ARIA state §5 requires, so it would serve as a geometry source only; and vendoring GPL-derived coordinates raises a copyleft question that ISC does not. It also ships Puerto Rico, which we would strip. It is the right tool for a static choropleth figure in R — the one output §2 forbids here. |
| Census `cb_20m` shapefiles direct | Public domain and authoritative, but unprojected: it puts the Albers composite and the Alaska/Hawaii insets back on us. `us-atlas` is this data, already projected. |
| `d3-geo` / `topojson-client` at runtime | Client-side projection means a JavaScript dependency and a CDN request. Both are excluded. |
| A public-domain blank US SVG (e.g. Wikimedia) | Tempting because the paths already exist, but provenance and projection are usually undocumented, state identifiers are inconsistent, and there is no version to pin. |

## 4. Layout

- **Output inline `<svg>`** with one `<path>` per state, generated at build time from the vendored
  TopoJSON. No client-side projection, no JavaScript geometry, no `<img>`, no external file request.
- **Mark the insets as insets.** `geoAlbersUsa` places Alaska and Hawaii bottom-left at reduced
  scale, but it does not tell the reader that. Add a thin separator or bounding rule around them so
  the composite is not read as geography.
- **A `viewBox` and no fixed pixel width**, so the map scales. It must be legible from roughly
  320 CSS px wide up to the site's `--maxw` of 1180px. The map should occupy no more than about
  720px of that, matching the tile grid's current visual weight.
- **Labels.** Print the postal code and, for states that hold bills, the count. Twelve states are
  labelled today; the design must not break when the registry gains a small north-eastern state, so
  build offset labels with **leader lines** for the DE/NJ/MD/RI/CT/NH/DC cluster from the start,
  rather than centring every label and discovering the collision later.
- **Print.** The site has no print stylesheet and does not need one, but do not make the map depend
  on hover to be readable: a screenshot of it must carry the same information as the live page,
  because that is how it will travel in a news story.

## 5. Behavioural and DOM contract

The map **replaces** `tile_map()` as the landing page's state filter. Do not ship both — two
geographies on one page is worse than either alone. The existing filter script binds to the tile
grid's DOM, so match this contract exactly or update the script in the same commit.

Current contract, from `site/build.py`:

```
Buttons        <button type="button" class="tile has" data-state="MO" aria-pressed="false">
Inert states   <div class="tile" aria-label="WY, no bills in this registry">
Script         FILTER_JS toggles sel.state on click, then sets aria-pressed on every .tile.has,
               and filters the rows of <table id="matrix"> by row.dataset.state
Insertion      the landing page body interpolates {tile_map(bills)} directly after the lede
Live count     <span class="rowcount" id="rowcount"> is updated by the script, not by you
```

Requirements:

- **Every state that holds bills is a real `<button>`**, keyboard-focusable, in the tab order, with
  a visible `:focus-visible` outline. An SVG `<path>` with a click handler is not acceptable; use
  `<a>`/`<button>` wrappers or `<path tabindex="0" role="button">` with full keyboard handling —
  Enter and Space both activate.
- **Selection is a toggle**, and the selected state is indicated by something other than colour
  alone (a stroke weight or an inset outline, in addition to fill), so it survives greyscale and
  colour-blind viewing.
- **`aria-pressed` semantics are preserved**, and every state carries an accessible name of the form
  `"Missouri, 6 bills. Filter."` for states with bills and `"Wyoming, no bills in this registry"`
  for the rest. Spell the state name; a screen reader should not read `MO`.
- **The whole map has `role="group"` and an `aria-label`**, as the tile grid does.
- **A text alternative is required, not optional.** Provide the same information as a list or table
  adjacent to the map — a `<details>` element holding "states and bill counts" is fine. The map is
  not the only way to reach a state.
- **Caveat copy, carried over verbatim:**

  > Numbers are bills held. States without a number: no bills in this registry — which is not the
  > same as none existing, since the inclusion methodology is not yet established.

  You may reword only the phrase about tile positioning, which no longer applies.

## 6. Styling

Use the existing CSS custom properties; do not introduce a palette. The site defines light and dark
themes via `prefers-color-scheme` **and** `:root[data-theme=...]` overrides, and your CSS must work
in all four combinations.

```
--bg --fg --muted --line --card --accent --accent-weak --maxw --radius
```

- States with bills: `--accent-weak` fill, `--accent` stroke, label in `--fg`, count in `--accent`.
- States without: `--card` fill, `--line` stroke, label in `--muted`.
- Hover and selected: `--accent` fill with `--bg` text, as the tiles do now.
- Keep the CSS in the same stylesheet block as the tile-grid rules it replaces, and delete those
  rules — leaving dead CSS behind is a defect a lint pass has already caught once in this project.

## 7. Tests and acceptance

The repository gates on this command, which must stay green:

```bash
python3 registry/validate.py && python3 registry/test_regressions.py \
  && python3 site/test_diff.py && python3 audit/test_audit.py && python3 site/build.py
```

CI additionally runs `ruff check --select F,E9 registry site audit`, and a post-build assertion block
in `.github/workflows/validate.yml` that counts pages, resolves every relative link, and checks a
few content invariants. **Add assertions there for the map**, at minimum:

1. The landing page contains exactly **51** state paths (50 states + DC), each with a `data-state`.
2. Every state postal code present in `registry/bills.json` appears as an interactive control, and
   its label carries the correct count. Derive both sides from the registry; do not hard-code 12.
3. No state that holds no bills is interactive.
4. The caveat sentence is present.
5. **No `linearGradient`, no `fill-opacity` ramp, and no more than two distinct state fill values
   in the generated SVG.** This is the mechanical form of §2, and it is the assertion a future
   contributor will thank you for.
6. The geometry file's hash matches its `source_manifest.json` entry — via the validator extension
   in §3, not a separate check.
7. The FIPS→USPS table covers every geometry in the vendored file, and every postal code in
   `registry/bills.json` resolves to one. A missing row must fail the build, not silently drop a
   state from the map.
8. `site/geo/LICENSE-us-atlas` exists and `LICENSE-DATA` references it.

Write the invariants as assertions in the workflow, in the style already there. If an assertion is
awkward to express, say so in your notes rather than dropping it silently.

## 8. Out of scope

Do not build these; they are separate decisions that have not been made.

- Any per-provision, per-family or per-year facet of the map. It has been discussed and deferred.
- Any time animation or year slider. The registry's clearest temporal fact — 1, 1, 1, 8, 12 bills
  introduced in 2022 through 2026 — is invisible on a map and will get its own non-map view.
- Changes to the provision matrix, the bill pages, the lineage diagram or the differ.
- Any new dependency, any client-side framework, any icon set.
- Any wording that characterises a state's legislation as strong, weak, leading, behind, or first.

## 9. What to hand back

1. The diff, as a branch or a patch against `088654c` or later, including the vendored geometry, its
   licence notice, and the manifest entry.
2. A screenshot of the landing page at 1280px and at 375px, light and dark.
3. A short note covering: which geometry file and version you vendored and its licence; the raw and
   gzipped weight the map added to the landing page; every place you departed from this spec and
   why; and what you did **not** verify. The last item matters more than it sounds — this project
   has shipped one confident inference that turned out to be a false correction of another
   researcher's published work, and the standing expectation is that you separate what you checked
   from what you assumed.

Note that a reviewer will attack the rejections in your note harder than the code, because a wrong
rejection ships with an argument that suppresses the next person who raises it. That is how this
document came to exist.

---

## 10. Departures in the built version

Recorded because a spec that quietly diverges from the artefact is the failure this project has
already been caught by once. Each of these was a deliberate choice made during the build.

| Spec said | Built instead | Why |
|---|---|---|
| §4: print the postal code on every state, count on those with bills | Label only the states that hold bills | Fifty labels at 720px is noise, and many small states cannot hold one. The state's identity is available on hover, and every state appears in the list below the map. |
| §5: every state carries an accessible name | The 39 states with no bills are `aria-hidden`; the 12 with bills are named | Announcing thirty-nine "no bills in this registry" nodes is worse for a screen-reader user than the list that follows, which names every state and is a real text alternative. |
| §5: an SVG `<path>` with a click handler is not acceptable | Interactive states are `<g role="button" tabindex="0">` with hand-wired Enter/Space | The spec allowed this variant; noting it because it means the keyboard path is bespoke and is exactly where a reviewer should push. |
| §7: 51 state paths **each with a `data-state`** | 51 shapes, `data-state` on the 12 interactive ones | Follows from labelling and exposing only bill-holding states. The assertion was rewritten to count shapes and to compare the interactive set against the registry. |
| — | The fallback list is also a filter, not just text | South Carolina's outline is ~15px wide on a phone, well under a usable tap target. Both controls share one selector and stay in sync. |
| — | Non-bill states are stroked in `--muted` at 45% opacity, not `--line` | `--line` against `--card` is a two-step difference in both themes; at map scale the country stopped reading as a country. |

**Verified after the build:** 51 shapes; 12 interactive, all matching the registry; 0 inert
focusables; exactly 2 fill values and no gradients; click, Enter, Space and Clear all filter the
matrix correctly from either control; light and dark, 1280px and 375px. The map added 68 KB raw to
the landing page — 63 KB to 131 KB — which is 29.5 KB gzipped, the number that reaches a reader.

**Not verified:** the assertions ran locally, not on CI; no screen reader was used, only the
accessibility tree; no real browser other than the one driven here; and the label positions were
checked by eye at two widths rather than computed for collisions.

## 11. Added after review (2026-08-11)

Two changes made in response to reviewing the built map, neither of which the spec anticipated.

**The selection indicator was a box, not a border.** Focus and selection used
`stroke-dasharray: 4 2`. At this scale the dashes stop reading as a boundary: on a
near-rectangular state such as Tennessee the result looks like an arbitrary rectangle laid over
the map. Both indicators are now a solid stroke on the state's own path, so the highlight is the
border. `outline:none` also moved from `:focus-visible` to `:focus`, because the other thing that
draws a box is the browser's own focus ring, which is the element's bounding box and appears on
mouse focus where `:focus-visible` does not match.

**Clicking a state appeared to do nothing.** It did filter the matrix — verified 23 rows to 6 —
but the matrix begins a full viewport below the bottom of the map, so every consequence of the
click was off-screen. §5 specified the filter contract and never asked where the feedback lands,
which is the more important question for a reader. A panel now sits directly under the map: the
state's name, its bill count, and each bill as a link with its year, status and family, ordered
chronologically then by number so no ranking is implied. It carries a link into the provisions
table and a control to clear the selection. Twelve panels are pre-rendered and hidden; the
selection unhides one. With JavaScript off nothing is lost that the matrix does not already
carry.

CI asserts one panel per state holding bills, each listing exactly that state's bills, all hidden
by default, plus the no-selection hint. Each assertion was checked by breaking it.
