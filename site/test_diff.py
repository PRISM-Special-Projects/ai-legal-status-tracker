"""Adversarial and corpus tests for the structural differ.

Standard library only, like everything else here: run with

    python3 site/test_diff.py

The synthetic fixtures come first and matter most. They are designed to break the
parser, not to confirm it: statutory citations that look like designators, labels
reused under different parents, insertions that must not cascade, and text with no
usable structure at all. The corpus cases at the end are regression fixtures — they
record what the parser currently reports for Missouri and Tennessee, and exist to
catch drift, not to define correctness.
"""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import legdiff as L                                                  # noqa: E402

TEXTS = pathlib.Path(__file__).resolve().parent.parent / "registry" / "texts"


def paths(text):
    return [n.path for n in L.parse(text).nodes]


def bodies(text):
    return {n.path: n.text for n in L.parse(text).nodes}


class Citations(unittest.TestCase):
    """A citation is not structure."""

    def test_nd_century_code_stays_in_the_sentence(self):
        t = ('SECTION 1. Definitions.\n'
             '(a) A person as defined in N.D. Cent. Code § 1-01-49(8) is not a machine.\n'
             '(b) Nothing here applies to a corporation.\n'
             '(c) This section takes effect at once.\n')
        p = L.parse(t)
        # ("1",) is the section's own heading text, which is a provision too.
        self.assertEqual([n.path for n in p.nodes],
                         [("1",), ("1", "(a)"), ("1", "(b)"), ("1", "(c)")])
        body = bodies(t)[("1", "(a)")]
        self.assertIn("§ 1-01-49(8)", body)
        self.assertIn("N.D. Cent. Code", body)

    def test_statutory_section_reference_is_not_a_marker(self):
        t = ('SECTION 1. Tennessee Code Annotated, Section 1-3-105(a), is amended.\n'
             '(19) "Person" does not include artificial intelligence.\n'
             '(20) "Machine" retains its meaning.\n'
             '(21) Nothing in this act applies to a corporation.\n')
        self.assertEqual(paths(t),
                         [("1",), ("1", "(19)"), ("1", "(20)"), ("1", "(21)")])
        self.assertIn("Section 1-3-105(a)", bodies(t)[("1",)])

    def test_internal_cross_reference_is_not_a_marker(self):
        """"...risks identified under subdivision (b)(1);" — found live in Tennessee HB 1455."""
        t = ('SECTION 1. Study.\n'
             '(b) The study conducted pursuant to subsection (a) must:\n'
             '(1) Identify and assess the potential risks;\n'
             '(2) Explore methods to mitigate the risks identified under subdivision (b)(1);\n'
             '(3) Review standards for the risks identified under subdivision (b)(1);\n')
        got = paths(t)
        self.assertEqual(got, [("1",), ("1", "(b)"), ("1", "(b)", "(1)"),
                               ("1", "(b)", "(2)"), ("1", "(b)", "(3)")])
        self.assertEqual(len(set(got)), len(got))
        self.assertIn("subdivision (b)(1)", bodies(t)[("1", "(b)", "(2)")])

    def test_abbreviations_and_dates_do_not_create_provisions(self):
        t = ('SECTION 1. Findings.\n'
             '(a) Machines, e.g. computers, are not persons under U.S. law.\n'
             '(b) This act takes effect January 1. The department shall report.\n'
             '(c) See N.D. Cent. Code § 1-01-49(8).\n')
        self.assertEqual(paths(t), [("1",), ("1", "(a)"), ("1", "(b)"), ("1", "(c)")])
        self.assertIn("January 1. The department shall report.", bodies(t)[("1", "(b)")])


class Hierarchy(unittest.TestCase):

    def test_section_heading_keeps_its_body(self):
        t = ('SECTION 1. This section creates a new chapter.\n'
             'SECTION 2. This section is severable.\n'
             'SECTION 3. This act takes effect on passage.\n')
        p = L.parse(t)
        self.assertEqual([n.path for n in p.nodes], [("1",), ("2",), ("3",)])
        self.assertTrue(p.nodes[0].text.startswith("This section creates"))

    def test_siblings_are_siblings(self):
        t = 'SECTION 1. Definitions.\n(a) First provision here.\n(b) Second provision here.\n'
        self.assertEqual(paths(t), [("1",), ("1", "(a)"), ("1", "(b)")])

    def test_nested_items_attach_to_the_right_parent(self):
        t = ('SECTION 1. Definitions.\n'
             '(a) The first term means:\n'
             '(1) one thing; and\n'
             '(2) another thing.\n'
             '(b) The second term means something else.\n')
        self.assertEqual(paths(t), [("1",), ("1", "(a)"), ("1", "(a)", "(1)"),
                                    ("1", "(a)", "(2)"), ("1", "(b)")])

    def test_reused_labels_get_different_paths(self):
        t = ('SECTION 1. Definitions.\n'
             '(a) The first term means:\n'
             '(1) alpha one; and\n'
             '(b) The second term means:\n'
             '(1) beta one.\n')
        got = paths(t)
        self.assertIn(("1", "(a)", "(1)"), got)
        self.assertIn(("1", "(b)", "(1)"), got)
        self.assertEqual(len(set(got)), len(got))

    def test_nesting_order_is_not_hard_coded(self):
        """Tennessee runs SECTION -> (19) -> (A); Missouri runs section -> 2. -> (1)."""
        tn = 'SECTION 1. Amended.\n(19) "Person":\n(A) Includes a firm; and\n(B) Does not include a machine;\n'
        self.assertEqual(paths(tn), [("1",), ("1", "(19)"),
                                     ("1", "(19)", "(A)"), ("1", "(19)", "(B)")])
        mo = ('1.2045. 1. This section may be cited as the Act.\n'
              '2. For purposes of this section:\n'
              '(1) "AI", any software; and\n'
              '(2) "Developer", the party responsible.\n')
        self.assertEqual(paths(mo), [("1.2045", "1"), ("1.2045", "2"),
                                     ("1.2045", "2", "(1)"), ("1.2045", "2", "(2)")])


class Adversarial(unittest.TestCase):
    """Fixtures proposed by an external reviewer, not by the parser's author."""

    def test_usc_citations_do_not_become_provisions(self):
        t = ('SECTION 1. Findings.\n'
             '(a) Copyright vests under 17 U.S.C. 101 in a human author.\n'
             '(b) "AI" has the meaning used in 15 U.S.C. 9401(3).\n'
             '(c) Effective on passage.\n')
        self.assertEqual(paths(t), [("1",), ("1", "(a)"), ("1", "(b)"), ("1", "(c)")])
        self.assertIn("15 U.S.C. 9401(3)", bodies(t)[("1", "(b)")])

    def test_section_word_in_prose_is_not_a_marker(self):
        t = ('SECTION 1. Construction.\n'
             '(a) Nothing in this SECTION 1. shall be construed as a grant of status.\n'
             '(b) A machine is not a person.\n(c) Effective on passage.\n')
        p = L.parse(t)
        self.assertEqual(len([n for n in p.nodes if n.level == 0]), 1,
                         "only one section should be recognised")

    def test_decimal_number_opening_a_sentence(self):
        t = ('SECTION 1. Fees.\n'
             '(a) The fee is set at 2.50 per filing.\n'
             '(b) 3.75 is the reduced fee. The department shall publish it.\n'
             '(c) Effective on passage.\n')
        got = paths(t)
        self.assertEqual(got, [("1",), ("1", "(a)"), ("1", "(b)"), ("1", "(c)")])
        self.assertIn("3.75", bodies(t)[("1", "(b)")])

    def test_duplicate_identical_provision_under_same_parent(self):
        """Reviewer fixture A: both nodes must survive; neither may overwrite."""
        t = ('SECTION 1. Definitions.\n(1) First.\n(A) Alpha.\n(A) Duplicate alpha.\n')
        nodes = L.parse(t).nodes
        alphas = [n for n in nodes if n.path[-1] == "(A)"]
        self.assertEqual(len(alphas), 2)
        self.assertEqual([n.ordinal for n in alphas], [1, 2])
        self.assertEqual(alphas[0].path, alphas[1].path)          # same identity...
        self.assertNotEqual(alphas[0].text, alphas[1].text)       # ...different content

    def test_duplicate_paths_on_both_sides_are_not_aligned(self):
        a = 'SECTION 1. Definitions.\n(1) First.\n(A) Alpha one.\n(A) Alpha two.\n'
        z = 'SECTION 1. Definitions.\n(1) First.\n(A) Alpha three.\n(A) Alpha four.\n'
        r = L.diff_texts(a, z)
        self.assertEqual(r.modified, 0, "duplicates must not be paired positionally")
        self.assertEqual(r.ambiguous, 4)

    def test_roman_numeral_ambiguity_is_reported(self):
        t = ('SECTION 1. Definitions.\n(a) A term means:\n(i) one thing;\n(ii) another.\n')
        p = L.parse(t)
        self.assertTrue(any("roman numeral" in w for w in p.warnings),
                        "the letter/roman collision must be surfaced")


class Properties(unittest.TestCase):
    """Mutation properties: what must NOT change when something else does."""

    BASE = ('SECTION 1. Definitions.\n(a) First provision here.\n'
            '(b) Second provision here.\n(c) Third provision here.\n')

    def _kinds(self, a, z):
        return {e.label: e.kind for e in L.diff_texts(a, z).entries}

    def test_editing_one_provision_leaves_the_others_unchanged(self):
        z = self.BASE.replace("(b) Second provision here.", "(b) Second provision, amended.")
        k = self._kinds(self.BASE, z)
        self.assertEqual(k["SECTION 1. (b)"], "modified")
        self.assertEqual(k["SECTION 1. (a)"], "unchanged")
        self.assertEqual(k["SECTION 1. (c)"], "unchanged")

    def test_appending_a_provision_leaves_the_others_unchanged(self):
        z = self.BASE + "(d) Fourth provision here.\n"
        k = self._kinds(self.BASE, z)
        self.assertEqual(k["SECTION 1. (d)"], "added")
        for lab in ("SECTION 1. (a)", "SECTION 1. (b)", "SECTION 1. (c)"):
            self.assertEqual(k[lab], "unchanged")

    def test_removing_a_provision_does_not_alter_another_body(self):
        z = self.BASE.replace("(b) Second provision here.\n", "")
        r = L.diff_texts(self.BASE, z)
        for e in r.entries:
            if e.kind == "unchanged":
                self.assertEqual(e.old, e.new)
        self.assertEqual(r.removed, 1)
        self.assertEqual(r.modified, 0)

    def test_duplicating_a_label_never_reduces_the_node_count(self):
        """The failure the old differ had: dict() collapse loses provisions."""
        base = len(L.parse(self.BASE).nodes)
        dup = L.parse(self.BASE + "(c) A second provision labelled c.\n")
        self.assertEqual(len(dup.nodes), base + 1)

    def test_punctuation_change_does_not_alter_structural_identity(self):
        z = self.BASE.replace("First provision here.", "First provision here;")
        self.assertEqual(paths(self.BASE), paths(z))

    def test_renumbering_leaves_unrelated_provisions_alone(self):
        z = self.BASE.replace("(c) Third", "(d) Third")
        k = self._kinds(self.BASE, z)
        self.assertEqual(k["SECTION 1. (a)"], "unchanged")
        self.assertEqual(k["SECTION 1. (b)"], "unchanged")


class Alignment(unittest.TestCase):

    def test_same_path_changed_body_is_one_modification(self):
        a = ('SECTION 1. Definitions.\n(a) A machine may not be a person.\n'
             '(b) A corporation remains a person.\n(c) Effective on passage.\n')
        z = ('SECTION 1. Definitions.\n(a) A machine may not be a person unless a court so finds.\n'
             '(b) A corporation remains a person.\n(c) Effective on passage.\n')
        r = L.diff_texts(a, z)
        self.assertEqual(r.mode, "structural")
        self.assertEqual((r.modified, r.added, r.removed), (1, 0, 0))
        self.assertEqual(r.unchanged, 3)

    def test_identical_label_under_different_parent_does_not_align(self):
        a = ('SECTION 1. Definitions.\n(a) Term one means:\n(1) the original alpha text;\n'
             '(b) Term two means:\n(1) the original beta text;\n')
        z = ('SECTION 1. Definitions.\n(a) Term one means:\n(1) the original alpha text;\n'
             '(b) Term two means:\n(1) a rewritten beta text;\n')
        r = L.diff_texts(a, z)
        self.assertEqual((r.modified, r.added, r.removed), (1, 0, 0))
        mods = [e for e in r.entries if e.kind == "modified"]
        self.assertIn("beta", mods[0].old)

    def test_insertion_does_not_cascade(self):
        a = ('SECTION 1. Definitions.\n(a) First provision.\n(b) Second provision.\n'
             '(c) Third provision.\n')
        z = ('SECTION 1. Definitions.\n(a) First provision.\n(a1) Inserted provision.\n'
             '(b) Second provision.\n(c) Third provision.\n')
        r = L.diff_texts(a, z)
        self.assertEqual((r.added, r.removed, r.modified), (1, 0, 0))
        self.assertEqual(r.unchanged, 4)

    def test_ambiguity_is_surfaced_not_guessed(self):
        """Genuinely indistinguishable reused paths must not be compared."""
        a = ('SECTION 1. Definitions.\n( ) The unborn shall be included.\n'
             '( ) The unborn shall be included.\n( ) Effective on passage.\n')
        z = ('SECTION 1. Definitions.\n( ) The unborn shall be included.\n'
             '( ) The unborn shall be included.\n( ) Something else entirely.\n')
        r = L.diff_texts(a, z)
        self.assertGreater(r.ambiguous, 0)
        self.assertEqual(r.modified, 0)
        self.assertTrue(any("identity was not established" in w for w in r.parser_warnings))
        self.assertTrue(any("Repeated structural labels" in e.note
                            for e in r.entries if e.kind == "ambiguous"))

    def test_blank_designators_are_not_matched_by_defined_term(self):
        """A drafter who leaves the designator blank has not told us the identity.

        Matching these on the term they define would be reading legal structure out
        of a semantic cue. Where both versions carry blank designators, the correct
        answer is that identity is not established."""
        a = ('SECTION 2. Amended.\n( ) "Human being" means a member of the species.\n'
             '( ) "Life" means the condition that distinguishes animals.\n'
             '( ) "Natural person" means an individual.\n')
        z = ('SECTION 2. Amended.\n( ) "Human being" means a member of the species.\n'
             '( ) "Life" means something narrower.\n'
             '( ) "Natural person" means an individual.\n')
        r = L.diff_texts(a, z)
        self.assertGreater(r.ambiguous, 0, "blank designators must not be silently aligned")
        self.assertEqual(r.modified, 0)
        # Every provision must still survive parsing on both sides.
        self.assertEqual(len(L.parse(a).nodes), 4)
        self.assertEqual(len(L.parse(z).nodes), 4)

    def test_blank_designators_are_distinguishable_in_display(self):
        """Retained without semantics: position, not the defined term."""
        t = ('SECTION 2. Amended.\n( ) "Human being" means one thing.\n'
             '( ) "Life" means another.\n( ) "Natural person" means a third.\n')
        nodes = [n for n in L.parse(t).nodes if n.confidence == "blank_label"]
        self.assertEqual(len(nodes), 3)
        self.assertEqual([n.ordinal for n in nodes], [1, 2, 3])
        for n in nodes:
            self.assertNotIn("Human being", "".join(n.path))
            self.assertNotIn("Life", "".join(n.path))

    def test_parent_movement_does_not_imply_child_movement(self):
        """Route 2 was removed: an ancestor's move is not evidence about its children.

        The identical sentence under (19)(B) and (20)(B) is reported as a removal and
        an addition. That overstates the change, and is preferred to inferring a
        correspondence the documents do not state."""
        # The (B) sentence recurs verbatim under SECTION 2, exactly as in the real
        # bill, so exact-text pairing cannot fire and only an inherited inference
        # could pair it. There must be no such inference.
        a = ('SECTION 1. Amended.\n(19) "Person":\n(A) Includes a corporation; and\n'
             '(B) Does not include artificial intelligence;\n'
             'SECTION 2. Added.\n(1) "Life":\n'
             '(B) Does not include artificial intelligence;\n')
        z = ('SECTION 1. Amended.\n(20) "Person":\n(A) Includes a corporation; and\n'
             '(B) Does not include artificial intelligence;\n'
             'SECTION 2. Added.\n(1) "Life":\n'
             '(B) Does not include artificial intelligence;\n')
        r = L.diff_texts(a, z)
        kinds = [e.kind for e in r.entries]
        self.assertNotIn("renumbered", [e.kind for e in r.entries
                                        if "(B)" in e.label and "→" not in e.label])
        self.assertEqual(r.removed, 1, "the (B) clause is a removal, not an inheritance")
        self.assertEqual(r.added, 1)

    def test_modified_is_not_a_removal_plus_an_addition(self):
        a = 'SECTION 1. A.\n(a) may not be granted;\n(b) unchanged;\n(c) unchanged too;\n'
        z = 'SECTION 1. A.\n(a) may not be granted unless a court finds otherwise;\n(b) unchanged;\n(c) unchanged too;\n'
        r = L.diff_texts(a, z)
        kinds = [e.kind for e in r.entries]
        self.assertEqual(kinds.count("modified"), 1)
        self.assertEqual(kinds.count("removed"), 0)
        self.assertEqual(kinds.count("added"), 0)


class Fallback(unittest.TestCase):

    def test_unstructured_text_falls_back_rather_than_guessing(self):
        a = "This bill concerns machines. It says nothing structural at all.\n"
        z = "This bill concerns machines and devices. It says nothing structural.\n"
        r = L.diff_texts(a, z)
        self.assertEqual(r.mode, "fallback")
        self.assertEqual(r.modified, 0)
        self.assertTrue(any("not reliable" in w for w in r.parser_warnings))

    def test_fallback_when_only_one_side_parses(self):
        a = 'SECTION 1. A.\n(a) one;\n(b) two;\n(c) three;\n'
        z = "A paragraph of prose with no legislative structure whatsoever.\n"
        self.assertEqual(L.diff_texts(a, z).mode, "fallback")

    def test_punctuation_is_not_the_unit_of_comparison(self):
        """The old differ split on punctuation; N.D./U.S./e.g. broke it."""
        t = ('SECTION 1. Findings.\n'
             '(a) Under U.S. law, e.g. N.D. Cent. Code § 1-01-49(8), a machine is not a person.\n'
             '(b) Nothing changes for corporations.\n(c) Effective at once.\n')
        p = L.parse(t)
        self.assertEqual(len(p.nodes), 4)      # the heading plus (a), (b), (c)
        self.assertIn("e.g.", bodies(t)[("1", "(a)")])


class Corpus(unittest.TestCase):
    """Regression fixtures over the real registry texts."""

    def _diff(self, a, z):
        return L.diff_texts((TEXTS / a).read_text(), (TEXTS / z).read_text())

    def test_missouri_hcs_reports_structural_change(self):
        r = self._diff("mo-hb1462-2025--introduced.txt", "mo-hb1746-2026--hcs.txt")
        self.assertEqual(r.mode, "structural")
        self.assertEqual(
            (r.removed, r.added, r.modified, r.renumbered, r.unchanged, r.ambiguous),
            tuple(MO[k] for k in
                  ("removed", "added", "modified", "renumbered", "unchanged", "ambiguous")))

    def test_tennessee_hb849_reports_structural_change(self):
        r = self._diff("tn-sb837-2025--introduced.txt", "tn-sb837-2025--enacted-pc781.txt")
        self.assertEqual(r.mode, "structural")
        self.assertEqual(
            (r.removed, r.added, r.modified, r.renumbered, r.unchanged, r.ambiguous),
            tuple(TN[k] for k in
                  ("removed", "added", "modified", "renumbered", "unchanged", "ambiguous")))
        # The headline finding: the fetal-personhood section went away entirely, and the
        # surviving person definition was renumbered rather than rewritten.
        self.assertTrue(any(e.kind == "removed" and "Human being" in (e.old or "")
                            for e in r.entries))
        self.assertTrue(any(e.kind == "renumbered" for e in r.entries))

    def test_missouri_provisions_do_not_share_a_path(self):
        """The veil provision and the alignment-washing provision both contain "(1)"."""
        nodes = L.parse(L.strip_preamble(
            (TEXTS / "mo-hb1462-2025--introduced.txt").read_text())).nodes
        def find(word):
            return [n for n in nodes if word in n.text.lower()]
        veil = find("pierce") or find("corporate veil")
        align = find("alignment") or find("emergent")
        self.assertTrue(veil and align, "expected both provisions in the Missouri text")
        self.assertNotEqual(veil[0].path, align[0].path)
        self.assertEqual(len({n.path for n in nodes}), len(nodes),
                         "Missouri paths should be unique")

    def test_every_provision_is_accounted_for_exactly_once(self):
        """Conservation: a paired slot consumes one provision from each side, an
        unpaired one consumes one. Nothing may be dropped or double-counted, which
        is the failure a differ can hide most easily."""
        import json
        reg = json.loads((TEXTS.parent / "bills.json").read_text())
        for b in reg["bills"]:
            vs = [v for v in b["versions"] if v.get("text_path")]
            if len(vs) < 2:
                continue
            a_raw = (TEXTS.parent / vs[0]["text_path"]).read_text()
            z_raw = (TEXTS.parent / vs[-1]["text_path"]).read_text()
            r = L.diff_texts(a_raw, z_raw)
            if r.mode != "structural":
                continue
            na = len(L.parse(L.strip_preamble(a_raw)).nodes)
            nz = len(L.parse(L.strip_preamble(z_raw)).nodes)
            paired = r.unchanged + r.modified + r.renumbered
            self.assertEqual(na + nz, 2 * paired + r.removed + r.added + r.ambiguous,
                             f"{b['id']}: provisions lost or double-counted")
            self.assertEqual(len(r.entries), r.nodes_total, b["id"])

    def test_every_corpus_pair_reports_a_mode(self):
        import json
        reg = json.loads((TEXTS.parent / "bills.json").read_text())
        checked = 0
        for b in reg["bills"]:
            vs = [v for v in b["versions"] if v.get("text_path")]
            if len(vs) < 2:
                continue
            r = L.diff_texts((TEXTS.parent / vs[0]["text_path"]).read_text(),
                             (TEXTS.parent / vs[-1]["text_path"]).read_text())
            self.assertIn(r.mode, ("structural", "fallback"))
            self.assertGreater(r.nodes_total, 0, b["id"])
            checked += 1
        self.assertGreater(checked, 0)


# Recorded output, not a specification — these are what the parser reports today, so that a
# change in the parser has to be noticed and explained rather than silently absorbed. They are
# NOT the numbers the earlier punctuation differ produced (Missouri read 21 removed / 22 added),
# and they are not independently verified provision counts. Update deliberately, in a commit
# that says why.
MO = {"removed": 8, "added": 4, "modified": 11, "renumbered": 0, "unchanged": 7, "ambiguous": 0}
TN = {"removed": 9, "added": 1, "modified": 1, "renumbered": 3, "unchanged": 0, "ambiguous": 0}

if __name__ == "__main__":
    unittest.main(verbosity=2)
