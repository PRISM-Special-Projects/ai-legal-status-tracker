#!/usr/bin/env python3
"""One-shot parser repair for numbered subsections whose text starts lowercase."""
from pathlib import Path
root=Path(__file__).resolve().parent.parent
leg=root/'site'/'legdiff.py'; s=leg.read_text()
old='r"|(?P<sub>\\d{1,3}\\.(?=[ \\t]+[A-Z\\\"(]))"'
new='r"|(?P<sub>\\d{1,3}\\.(?=[ \\t]+[A-Za-z\\\"(]))"'
assert old in s and new not in s
leg.write_text(s.replace(old,new))

test=root/'site'/'test_diff.py'; s=test.read_text()
needle='    def test_nesting_order_is_not_hard_coded(self):\n'
case='''    def test_lowercase_text_after_numbered_subsection_is_structure(self):\n        t = ('1.2058. 1. following terms mean:\\n'\n             '(1) First definition.\\n'\n             '2. next subsection applies:\\n'\n             '(1) First operative requirement.\\n')\n        self.assertEqual(paths(t), [("1.2058", "1"), ("1.2058", "1", "(1)"),\n                                    ("1.2058", "2"), ("1.2058", "2", "(1)")])\n\n'''
assert needle in s and 'test_lowercase_text_after_numbered_subsection_is_structure' not in s
test.write_text(s.replace(needle,case+needle))
print('G3 parser fix applied')
