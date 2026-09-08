"""Source-only regression for the Q3LOCK bare-infinity typesetting defect.

This recognizes the math delimiters/environments used by this manuscript.
It is not a TeX macro interpreter, compile test, PDF review, or proof audit.
No file is written and no TeX engine is invoked.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "publish/papers/q3lock-phase-coexistence/manuscript.tex"
MATH_ENVIRONMENTS = {
    "equation", "equation*", "align", "align*", "alignat", "alignat*",
    "gather", "gather*", "multline", "multline*", "displaymath", "math",
    "aligned", "alignedat", "gathered", "split", "cases", "array",
}
TOKENS = re.compile(
    r"%[^\n]*|\\(?:begin|end)\{[^}]+\}|\\[A-Za-z]+|\\.|\$\$|\$"
)


def math_delimiter_issues(source):
    """Return located lexical issues in the supported source subset only."""
    stack = []
    issues = []
    for match in TOKENS.finditer(source):
        token = match.group()
        line = source.count("\n", 0, match.start()) + 1
        if token.startswith("%"):
            continue
        if token.startswith((r"\begin{", r"\end{")):
            environment = token[token.index("{") + 1:-1]
            if environment not in MATH_ENVIRONMENTS:
                continue
            if token.startswith(r"\begin{"):
                stack.append((environment, line))
            elif stack and stack[-1][0] == environment:
                stack.pop()
            else:
                issues.append((line, "unmatched math environment " + token))
        elif token in ("$", "$$"):
            if stack and stack[-1][0] == token:
                stack.pop()
            else:
                stack.append((token, line))
        elif token in (r"\(", r"\["):
            stack.append((token, line))
        elif token in (r"\)", r"\]"):
            opener = {r"\)": r"\(", r"\]": r"\["}[token]
            if stack and stack[-1][0] == opener:
                stack.pop()
            else:
                issues.append((line, "unmatched math delimiter " + token))
        elif token == r"\infty" and not stack:
            issues.append((line, "infinity command outside math mode"))
    issues.extend((line, "unclosed math delimiter " + token) for token, line in stack)
    return issues


class ManuscriptMathDelimiters(unittest.TestCase):
    def test_current_manuscript(self):
        self.assertEqual(math_delimiter_issues(MANUSCRIPT.read_text(encoding="utf-8")), [])

    def test_actual_table_and_prose_regression(self):
        source = MANUSCRIPT.read_text(encoding="utf-8")
        corrected = r"$n=1,2,\infty$"
        # Test oracle: the reported defect occurred once in the table and once
        # in the prose. This count is not a derived mathematical quantity.
        self.assertEqual(source.count(corrected), 2)
        mutated = source.replace(corrected, r"n=1,2,\infty")
        issues = math_delimiter_issues(mutated)
        self.assertEqual(len(issues), 2)
        self.assertTrue(all(message == "infinity command outside math mode"
                            for _, message in issues))

    def test_supported_math_modes(self):
        for source in (r"$\infty$", r"$$\infty$$", r"\(\infty\)",
                       r"\[\infty\]", r"\begin{equation}\infty\end{equation}",
                       r"\begin{align*}\begin{aligned}\infty\end{aligned}\end{align*}"):
            with self.subTest(source=source):
                self.assertEqual(math_delimiter_issues(source), [])

    def test_comments_and_escaped_dollars(self):
        self.assertEqual(math_delimiter_issues("% \\infty $\n" + r"cost \$5; $\infty$"), [])
        self.assertEqual(math_delimiter_issues(r"cost \$5; \infty"),
                         [(1, "infinity command outside math mode")])

    def test_unmatched_delimiters_rejected(self):
        for source in (r"$\infty", r"\infty\]", r"\begin{equation}\infty",
                       r"\end{align}"):
            with self.subTest(source=source):
                self.assertTrue(math_delimiter_issues(source))


if __name__ == "__main__":
    unittest.main()
