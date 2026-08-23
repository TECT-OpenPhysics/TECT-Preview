"""Integrated verifier for the EXP-000961 finite QFT candidate screen."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-linear-galerkin-qft-screen-manifest.json"
PRIMARY = REPO / "codes" / "foundations" / "a13_linear_galerkin_qft_screen.py"
INDEPENDENT = REPO / "codes" / "foundations" / "a13_linear_galerkin_qft_screen_independent.py"
LEAN_ENTRYPOINT = REPO / "verification" / "lean" / "Tect" / "R196.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-integrated-linear-galerkin-qft-screen" / "result.json"


def sha256_normalized(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def core(derived: dict[str, Any]) -> dict[str, Any]:
    completed = derived.get("completed_square")
    if completed is None:
        completed = {
            "Y": "1",
            "mu_eff": derived.get("mu_eff"),
            "q_star_squared": derived.get("q_star_squared"),
        }
    return {
        "dimension": derived["dimension"],
        "pi_bounds": derived["pi_bounds"],
        "completed_square": completed,
        "generator_factor": derived["generator_factor"],
        "cutoffs": derived["cutoffs"],
        "finite_q_ledger": derived["finite_q_ledger"],
        "finite_q_nonnegative": derived["finite_q_nonnegative"],
        "finite_q_monotone": derived["finite_q_monotone"],
        "tail": derived["tail"],
        "conditional_qft_interface": derived["conditional_qft_interface"],
        "nonlinear_production_owner": derived["nonlinear_production_owner"],
        "r192_first_missing_slot_unchanged": derived["r192_first_missing_slot_unchanged"],
    }


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    completed = subprocess.run(
        [sys.executable, "-B", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(f"child failed: {script.name}\n{completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        assertions.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-LINEAR-GALERKIN-QFT-CURRENT-SCREEN", manifest["audit_id"], "A13-A1-LINEAR-GALERKIN-QFT-CURRENT-SCREEN")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("exploration identity", manifest["exploration_id"] == "EXP-000961", manifest["exploration_id"], "EXP-000961")
    check("eight hostile mutation contracts", len(manifest["hostile_mutations"]) == 8, len(manifest["hostile_mutations"]), 8)
    cert = (REPO / manifest["files"]["certificate"]["path"]).read_text(encoding="utf-8")
    scope_tokens = ("conditional", "does not prove that this OU", "heat_root_incidence", "No A13 gate")
    check("certificate conditional boundary", all(token in cert for token in scope_tokens), [token for token in scope_tokens if token in cert], "all scope tokens")
    for key, item in manifest["source_authorities"].items():
        path = REPO / item["path"]
        check(f"source {key}", path.is_file() and sha256_normalized(path) == item["sha256"], sha256_normalized(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"file {key}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256_normalized(path) == item["sha256"], sha256_normalized(path) if path.is_file() else None, item["sha256"])

    with tempfile.TemporaryDirectory(prefix="r196-") as temp:
        temp_path = Path(temp)
        primary_payload, primary_out = run_child(PRIMARY, temp_path / "primary.json")
        independent_payload, independent_out = run_child(INDEPENDENT, temp_path / "independent.json")
    check("primary PASS", primary_payload["verdict"] == "PASS", primary_payload["verdict"], "PASS")
    check("independent PASS", independent_payload["verdict"] == "PASS", independent_payload["verdict"], "PASS")
    check("derived lanes agree", core(primary_payload["derived"]) == core(independent_payload["derived"]), core(primary_payload["derived"]), core(independent_payload["derived"]))
    check("primary output label", "A1 LINEAR GALERKIN QFT PRIMARY PASS" in primary_out, primary_out, "PASS")
    check("independent output label", "A1 LINEAR GALERKIN QFT INDEPENDENT PASS" in independent_out, independent_out, "PASS")
    check("finite ledger positive", primary_payload["derived"]["finite_q_nonnegative"] is True, primary_payload["derived"]["finite_q_nonnegative"], True)
    check("finite ledger monotone", primary_payload["derived"]["finite_q_monotone"] is True, primary_payload["derived"]["finite_q_monotone"], True)
    check("linear candidate only", primary_payload["derived"]["conditional_qft_interface"] is True and primary_payload["derived"]["nonlinear_production_owner"] is False, primary_payload["derived"], "conditional")
    check("R-192 slot preserved", primary_payload["derived"]["r192_first_missing_slot_unchanged"] is True, primary_payload["derived"], "heat_root_incidence")

    independent_tree = ast.parse(INDEPENDENT.read_text(encoding="utf-8"))
    imported_names = {alias.name.split(".")[0] for node in ast.walk(independent_tree) if isinstance(node, ast.Import) for alias in node.names}
    imported_names |= {node.module.split(".")[0] for node in ast.walk(independent_tree) if isinstance(node, ast.ImportFrom) and node.module}
    check("independent no primary import", "a13_linear_galerkin_qft_screen" not in imported_names, imported_names, "no primary")
    check("Lean source clean", not any(token in LEAN_ENTRYPOINT.read_text(encoding="utf-8").split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")

    payload = {
        "schema": "tect/a13-linear-galerkin-qft-screen-integrated/1.0",
        "run_kind": "integrated",
        "audit_id": manifest["audit_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_id"],
        "verdict": "PASS",
        "assertion_count": len(assertions),
        "assertions": assertions,
        "cross_assertions": {"primary_independent_core_equal": True, "stored_children": False},
        "derived": primary_payload["derived"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"A1 LINEAR GALERKIN QFT INTEGRATED PASS {len(assertions)}/{len(assertions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
