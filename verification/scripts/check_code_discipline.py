"""Check the repository's executable code-discipline invariants.

The checker is intentionally conservative.  It fails on syntax errors and on
known derived quantities (currently ``MARGIN``/``RHO`` families) assigned from
numeric literals, while reporting the historical codebase's self-test and JSON
coverage as diagnostics.  New proof code can opt into strict coverage with
``--strict``; the normal release gate remains compatible with older archived
scripts that predate the policy.

The scanner itself has no numerical inputs.  ``--selftest`` exercises the AST
rules on tiny in-memory fixtures, so the checker can be tested without writing
an artefact into the repository.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
CODE_ROOT = REPO / "codes"
DERIVED_NAMES = frozenset(("MARGIN", "RHO", "RHO_END"))
JSON_MARKERS = (
    "json.dump",
    "json.dumps",
    "result.json",
    "JSON_ARTIFACT",
    "--json",
)


def _relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def _is_derived_name(name: str) -> bool:
    return name in DERIVED_NAMES


def _literal_only(node: ast.AST) -> bool:
    """Whether *node* is a container made solely from numeric literals."""
    if isinstance(node, ast.Constant):
        return isinstance(node.value, (int, float, complex)) and not isinstance(node.value, bool)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return bool(node.elts) and all(_literal_only(item) for item in node.elts)
    if isinstance(node, ast.Dict):
        return bool(node.values) and all(
            value is not None and _literal_only(value) for value in node.values
        )
    return False


def _derived_literal_violations(tree: ast.AST) -> list[str]:
    violations: list[str] = []
    for node in ast.walk(tree):
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        if value is None or not _literal_only(value):
            continue
        for target in targets:
            if isinstance(target, ast.Name) and _is_derived_name(target.id):
                violations.append(f"line {node.lineno}: {target.id} assigned from numeric literal")
    return violations


def _has_selftest(tree: ast.AST, source: str) -> bool:
    return bool(
        any(isinstance(node, ast.Assert) for node in ast.walk(tree))
        or re.search(r"def\s+(?:_?selftest|test_[A-Za-z0-9_]+)\s*\(", source)
        or "--selftest" in source
    )


def _has_json_artifact(source: str) -> bool:
    return any(marker in source for marker in JSON_MARKERS)


def scan(root: Path = CODE_ROOT, strict: bool = False) -> dict[str, object]:
    files = sorted(root.rglob("*.py"), key=lambda path: path.as_posix())
    parse_errors: list[str] = []
    derived: list[str] = []
    missing_selftest: list[str] = []
    missing_artifact: list[str] = []
    for path in files:
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            parse_errors.append(f"{_relative(path)}: {exc}")
            continue
        for item in _derived_literal_violations(tree):
            derived.append(f"{_relative(path)}: {item}")
        if not _has_selftest(tree, source):
            missing_selftest.append(_relative(path))
        if not _has_json_artifact(source):
            missing_artifact.append(_relative(path))
    errors = parse_errors + derived
    if strict:
        errors += [f"{path}: no self-test/assert" for path in missing_selftest]
        errors += [f"{path}: no JSON-artifact marker" for path in missing_artifact]
    return {
        "files": len(files),
        "parse_errors": parse_errors,
        "derived_literal_violations": derived,
        "missing_selftest": missing_selftest,
        "missing_json_artifact": missing_artifact,
        "strict": strict,
        "errors": errors,
    }


def _selftest() -> int:
    bad = ast.parse("MARGIN = 0.00432\nRHO = {1: 2.6}")
    assert len(_derived_literal_violations(bad)) == 2
    good = ast.parse("MARGIN = common.margin_of(mu2)['margin']\nRHO = {x: round(f(x), 1) for x in xs}")
    assert _derived_literal_violations(good) == []
    assert _has_selftest(ast.parse("assert value > 0"), "assert value > 0")
    assert _has_json_artifact("json.dump(result, handle)")
    print("CODE-DISCIPLINE SELFTEST: PASS (literal firewall, self-test and JSON markers)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="scan codes (default action)")
    parser.add_argument("--strict", action="store_true", help="fail legacy coverage diagnostics too")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return _selftest()
    report = scan(strict=args.strict)
    print(
        "CODE-DISCIPLINE: "
        f"{'PASS' if not report['errors'] else 'FAIL'} "
        f"files={report['files']} "
        f"derived={len(report['derived_literal_violations'])} "
        f"missing_selftest={len(report['missing_selftest'])} "
        f"missing_json={len(report['missing_json_artifact'])}"
    )
    for key in ("parse_errors", "derived_literal_violations"):
        for item in report[key]:
            print(f"  ERR {item}")
    if args.strict:
        for key in ("missing_selftest", "missing_json_artifact"):
            for item in report[key]:
                print(f"  ERR {item}")
    else:
        print("  WARN legacy coverage diagnostics are nonblocking; use --strict for new-code enforcement")
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
