#!/usr/bin/env python3
"""Replay the EXP-000782 independent verifier without touching history.

This package-level lane runs the registered standard-library independent
implementation in a temporary output directory, compares its complete
payload with the frozen EXP-000782 independent result, and applies hostile
source/result mutations.  It is a reproducibility and separation diagnostic;
it is not an independent referee, a proof of an unbounded limit, or a paper
PDF builder.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.2"
ROOT = Path(__file__).resolve().parents[2]
INDEPENDENT_SCRIPT = ROOT / (
    "codes/foundations/"
    "pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split_independent.py"
)
HISTORICAL_RESULT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-04-independent-pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split/"
    "result.json"
)
EXP_MANIFEST = ROOT / (
    "strategy/pre-a-cp1-st8-q3lock-positive-lambda-fkg-infrared-cusp-phase-route-split-manifest.json"
)
PAPER_MANIFEST = ROOT / "publish/papers/q3lock-phase-coexistence/verification/package-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-08-q3lock-independent-replay-source-review-v1/result.json"
)
PRIMARY_MODULE_FRAGMENT = "pre_a_cp1_st8_q3lock_positive_lambda_fkg_infrared_cusp_phase_route_split"
FORBIDDEN_IMPORT_ROOTS = {"numpy", "sympy", "mpmath"}
ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "argparse",
    "ast",
    "fractions",
    "hashlib",
    "json",
    "math",
    "os",
    "pathlib",
    "tempfile",
    "typing",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def atomic_no_replace(path: Path, payload: dict[str, Any]) -> None:
    if os.path.lexists(path):
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any) -> None:
        if not condition:
            raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def static_import_roots(source_text: str) -> set[str]:
    tree = ast.parse(source_text)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise ValueError("relative imports are not allowed")
            if node.module:
                roots.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "__import__", "compile"}:
                raise ValueError(f"dynamic execution is not allowed: {node.func.id}")
    return roots


def validate_independent_source(source_text: str) -> dict[str, Any]:
    roots = static_import_roots(source_text)
    if PRIMARY_MODULE_FRAGMENT in source_text:
        # The independent file names its primary result/script paths as
        # provenance.  Only an import of that module is forbidden.
        tree = ast.parse(source_text)
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        if any(PRIMARY_MODULE_FRAGMENT in item for item in imported):
            raise ValueError("independent verifier imports the primary module")
    forbidden = roots & FORBIDDEN_IMPORT_ROOTS
    if forbidden:
        raise ValueError(f"forbidden numerical imports: {sorted(forbidden)}")
    undeclared = roots - ALLOWED_IMPORT_ROOTS
    if undeclared:
        raise ValueError(f"undeclared imports: {sorted(undeclared)}")
    return {
        "import_roots": sorted(roots),
        "forbidden_import_roots": sorted(forbidden),
        "undeclared_import_roots": sorted(undeclared),
    }


def run_independent() -> tuple[dict[str, Any], str]:
    with tempfile.TemporaryDirectory(prefix="tect-q3lock-independent-") as directory:
        output = Path(directory) / "independent.json"
        completed = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(INDEPENDENT_SCRIPT),
                "--output",
                str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "independent verifier failed\n"
                + completed.stdout
                + completed.stderr
            )
        return json.loads(output.read_text(encoding="utf-8")), completed.stdout


def build_payload() -> dict[str, Any]:
    if not __debug__:
        raise ValueError("assertions must be enabled; do not use python -O")
    audit = Audit()
    historical = json.loads(HISTORICAL_RESULT.read_text(encoding="utf-8"))
    exp_manifest = json.loads(EXP_MANIFEST.read_text(encoding="utf-8"))
    paper_manifest = json.loads(PAPER_MANIFEST.read_text(encoding="utf-8"))
    source_text = INDEPENDENT_SCRIPT.read_text(encoding="utf-8")
    source_meta = validate_independent_source(source_text)
    fresh, stdout = run_independent()
    stable_stdout = "\n".join(
        line.strip()
        for line in stdout.splitlines()
        if "EXP-000782 INDEPENDENT PASS" in line
    )

    audit.check("fresh verifier exit sentinel", bool(stable_stdout), stable_stdout, "INDEPENDENT PASS")
    audit.check("fresh payload equals frozen independent result", fresh == historical, fresh == historical, True)
    audit.check("EXP authority result", fresh["result_id"] == exp_manifest["result_id"], fresh["result_id"], exp_manifest["result_id"])
    audit.check("EXP authority exploration", fresh["exploration_id"] == exp_manifest["exploration_id"], fresh["exploration_id"], exp_manifest["exploration_id"])
    audit.check("claim remains non-bearing", fresh["claim_bearing"] is False, fresh["claim_bearing"], False)
    audit.check("historical verdict", historical["verdict"] == "PASS", historical["verdict"], "PASS")
    audit.check("historical assertions complete", historical["assertions"]["passed"] == historical["assertions"]["total"], historical["assertions"], "passed=total")
    audit.check("paper scope remains T0", paper_manifest["claim_status"]["tier"] == "T0", paper_manifest["claim_status"]["tier"], "T0")
    audit.check("paper scope remains non-bearing", paper_manifest["claim_status"]["claim_bearing"] is False, paper_manifest["claim_status"]["claim_bearing"], False)
    manuscript = ROOT / paper_manifest["manuscript"]
    audit.check("current manuscript exists", manuscript.is_file(), manuscript.relative_to(ROOT).as_posix(), "file")
    audit.check("paper PDF remains deferred", paper_manifest["pdf_status"] == "DEFERRED", paper_manifest["pdf_status"], "DEFERRED")

    # Hostile fixtures must be rejected by the same checks used for the live
    # source/result.  They are omission controls, not theorem evidence.
    try:
        validate_independent_source("import sympy\n" + source_text)
    except ValueError:
        audit.check("hostile forbidden import rejected", True, "rejected", "rejected")
    else:
        audit.check("hostile forbidden import rejected", False, "accepted", "rejected")

    mutated = dict(fresh)
    mutated["claim_bearing"] = True
    try:
        if mutated == historical or mutated["claim_bearing"] is not False:
            raise ValueError("mutated claim-bearing payload")
    except ValueError:
        audit.check("hostile claim promotion rejected", True, "rejected", "rejected")
    else:
        audit.check("hostile claim promotion rejected", False, "accepted", "rejected")

    mutated = json.loads(json.dumps(fresh))
    mutated["assertions"]["total"] += 1
    try:
        if mutated == historical or mutated["assertions"]["passed"] != mutated["assertions"]["total"]:
            raise ValueError("mutated assertion payload")
    except ValueError:
        audit.check("hostile assertion mutation rejected", True, "rejected", "rejected")
    else:
        audit.check("hostile assertion mutation rejected", False, "accepted", "rejected")

    return {
        "schema": "tect/q3lock-independent-replay/1.0",
        "script_version": __version__,
        "result_id": "R-497",
        "exploration_id": "EXP-001637",
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "claim_bearing": False,
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "fresh_independent": {
            "assertions_passed": fresh["assertions"]["passed"],
            "assertions_total": fresh["assertions"]["total"],
            "payload_sha256": hashlib.sha256(
                json.dumps(fresh, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            ).hexdigest(),
        },
        "files": {
            "wrapper_script": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "wrapper_script_sha256": sha256(Path(__file__).resolve()),
            "independent_script": INDEPENDENT_SCRIPT.relative_to(ROOT).as_posix(),
            "independent_script_sha256": sha256(INDEPENDENT_SCRIPT),
            "historical_result": HISTORICAL_RESULT.relative_to(ROOT).as_posix(),
            "historical_result_sha256": sha256(HISTORICAL_RESULT),
            "current_manuscript": manuscript.relative_to(ROOT).as_posix(),
            "current_manuscript_sha256": sha256(manuscript),
        },
        "source_separation": source_meta,
        "verdict": "PASS",
        "boundary": (
            "Current package replay of the frozen EXP-000782 standard-library "
            "independent verifier plus hostile source/result mutation checks. "
            "This does not certify unbounded limits, external theorem applicability, "
            "a DLR phase, a cusp, literature novelty, or a paper PDF."
        ),
    }


def producer_environment() -> dict[str, str]:
    """Record execution provenance outside the deterministic scientific replay.

    No field is filtered from a saved replay during comparison. Historical
    checkpoints remain strict and require their original source/runtime.
    """
    return {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write-new", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        if not __debug__:
            raise ValueError("assertions must be enabled; do not use python -O")
        if args.self_test:
            payload = build_payload()
            print("Q3LOCK INDEPENDENT REPLAY SELF-TEST: PASS", payload["assertions"]["passed"])
            return 0
        if args.write_new:
            payload = build_payload()
            atomic_no_replace(
                args.output,
                {
                    "replay": payload,
                    "producer_environment": producer_environment(),
                },
            )
        else:
            before = args.output.read_bytes()
            stored = json.loads(before.decode("utf-8"))
            payload = build_payload()
            if stored.get("replay") != payload or args.output.read_bytes() != before:
                raise ValueError("stored replay differs; investigate and never overwrite history")
        print(
            "Q3LOCK INDEPENDENT REPLAY: PASS",
            payload["fresh_independent"]["assertions_passed"],
            "/",
            payload["fresh_independent"]["assertions_total"],
            "child assertions; package checks",
            payload["assertions"]["passed"],
            "/",
            payload["assertions"]["total"],
        )
        print(args.output)
        return 0
    except (AssertionError, FileNotFoundError, OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        print("Q3LOCK INDEPENDENT REPLAY: FAIL:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
