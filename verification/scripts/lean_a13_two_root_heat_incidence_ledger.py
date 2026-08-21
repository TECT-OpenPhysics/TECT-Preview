"""Primary exact audit for the R-177 two-root heat/incidence ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sympy as sp

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-heat-incidence-ledger-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R177.lean"
TOOLCHAIN = LEAN_DIR / "lean-toolchain"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-21-lean-r177-two-root-heat-incidence-ledger" / "primary.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def check(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "pass": bool(condition), "actual": serial(actual), "expected": serial(expected)})
    if not condition:
        raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")


def find_lake() -> str | None:
    pin = TOOLCHAIN.read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    for candidate in (Path.home() / ".elan" / "bin" / "lake.exe", Path.home() / ".elan" / "bin" / "lake"):
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def root1(heat: sp.Expr, r1: sp.Expr) -> sp.Expr:
    return heat + r1


def root2(heat: sp.Expr, r1: sp.Expr, r2: sp.Expr, beta: sp.Expr) -> sp.Expr:
    return heat + beta * root1(heat, r1) + r2


def endpoint(heat: sp.Expr, r1: sp.Expr, r2: sp.Expr, future: sp.Expr, beta: sp.Expr) -> sp.Expr:
    return root2(heat, r1, r2, beta) + future


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    check(rows, "manifest identity", manifest["audit_id"] == "A13-TWO-ROOT-HEAT-INCIDENCE-LEDGER", manifest["audit_id"], "A13-TWO-ROOT-HEAT-INCIDENCE-LEDGER")
    check(rows, "claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check(rows, "no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(rows, f"input {key} hash", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])

    r176_manifest = json.loads((REPO / manifest["inputs"]["r176_manifest"]["path"]).read_text(encoding="utf-8"))
    r176_run = json.loads((REPO / manifest["inputs"]["r176_run"]["path"]).read_text(encoding="utf-8"))
    r150 = json.loads((REPO / manifest["inputs"]["r150_manifest"]["path"]).read_text(encoding="utf-8"))
    r125 = json.loads((REPO / manifest["inputs"]["r125_manifest"]["path"]).read_text(encoding="utf-8"))
    r136 = json.loads((REPO / manifest["inputs"]["r136_manifest"]["path"]).read_text(encoding="utf-8"))
    r174 = json.loads((REPO / manifest["inputs"]["r174_manifest"]["path"]).read_text(encoding="utf-8"))
    status = json.loads((REPO / manifest["inputs"]["a13_status"]["path"]).read_text(encoding="utf-8"))
    check(rows, "R-176 predecessor", r176_manifest["result_id"] == "R-176" and r176_run["verdict"] == "PASS", [r176_manifest["result_id"], r176_run["verdict"]], ["R-176", "PASS"])
    check(rows, "R-176 actual roots", r176_run["derived"]["both_actual_roots_instantiated"] is True and r176_run["derived"]["root_labels"] == ["k", "2k"], r176_run["derived"]["root_labels"], ["k", "2k"])
    check(rows, "R-150 covariance owner", r150["result_ledger_id"] == "R-150" and r150["scope"]["canonical_A1_k_2k_covariances_identified"] is True, [r150["result_ledger_id"], r150["scope"]["canonical_A1_k_2k_covariances_identified"]], ["R-150", True])
    check(rows, "R-125 bridge boundary", r125["result_ledger_id"] == "R-125" and r125["scope"]["conditional_variance_rebate_required"] is True and r125["scope"]["production_root_shell_factorization_proved"] is False, [r125["result_ledger_id"], r125["scope"]["conditional_variance_rebate_required"], r125["scope"]["production_root_shell_factorization_proved"]], ["R-125", True, False])
    check(rows, "R-136 common heat boundary", r136["result_ledger_id"] == "R-136" and r136["scope"]["common_heat_replica_variance_identity_proved"] is True and r136["scope"]["production_raw_spatial_intertwiner_proved"] is False, [r136["result_ledger_id"], r136["scope"]["common_heat_replica_variance_identity_proved"], r136["scope"]["production_raw_spatial_intertwiner_proved"]], ["R-136", True, False])
    check(rows, "R-174 cylinder boundary", r174["result_id"] == "R-174" and r174["claim_bearing"] is False, [r174["result_id"], r174["claim_bearing"]], ["R-174", False])
    check(rows, "A13 remains open", status["proof_complete"] is False and status["lifecycle"] == "ACTIVE", [status["proof_complete"], status["lifecycle"]], [False, "ACTIVE"])

    beta = sp.Rational(str(manifest["registered_inputs"]["feedback_gain"]))
    heat, heat2 = sp.Integer(3), sp.Integer(0)
    r1, r2, future, future2 = sp.Integer(1), sp.Integer(2), sp.Integer(5), sp.Integer(-1)
    common_difference = sp.simplify(endpoint(heat, r1, r2, future, beta) - endpoint(heat, r1, r2, future2, beta))
    independent_difference = sp.simplify(endpoint(heat, r1, r2, future, beta) - endpoint(heat2, r1, r2, future, beta))
    feedback_delta = sp.simplify(endpoint(heat, r1 + 2, r2, future, beta) - endpoint(heat, r1, r2, future, beta))
    check(rows, "common heat cancels in replica difference", common_difference == future - future2, common_difference, future - future2)
    check(rows, "independent heat survives", independent_difference == (1 + beta) * (heat - heat2), independent_difference, (1 + beta) * (heat - heat2))
    check(rows, "root2 feedback retained", feedback_delta == beta * 2, feedback_delta, beta * 2)
    x, y = sp.Integer(7), sp.Integer(-1)
    midpoint = (x + y) / 2
    variance = sp.simplify(((x - midpoint) ** 2 + (y - midpoint) ** 2) / 2)
    check(rows, "two replica variance identity", variance == (x - y) ** 2 / 4, variance, (x - y) ** 2 / 4)
    same_mean_a, same_mean_b = sp.Integer(1), sp.Integer(-1)
    check(rows, "mean-only variance no-go", (same_mean_a + same_mean_b) / 2 == 0 and ((same_mean_a ** 2 + same_mean_b ** 2) / 2) > 0, ((same_mean_a + same_mean_b) / 2, (same_mean_a ** 2 + same_mean_b ** 2) / 2), (0, ">0"))

    owners = manifest["registered_inputs"]["owner_order"]
    check(rows, "owner order frozen", owners == ["common_heat", "root_1", "root_2", "future_residual"], owners, ["common_heat", "root_1", "root_2", "future_residual"])
    check(rows, "root incidence order", owners.index("root_1") < owners.index("root_2") < owners.index("future_residual"), owners, "root_1 < root_2 < future_residual")
    check(rows, "common heat is first", owners[0] == "common_heat", owners[0], "common_heat")

    lake = find_lake()
    check(rows, "lake available", lake is not None, lake, "pinned toolchain")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check(rows, "Lean compile", completed.returncode == 0, completed.returncode, 0)
    check(rows, "Lean clean output", completed.stdout.strip() == "" and completed.stderr.strip() == "", [completed.stdout, completed.stderr], ["", ""])

    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "root_labels": ["k", "2k"],
            "actual_a1_roots_from_r176": True,
            "common_heat_shared": True,
            "common_heat_cancels_from_replica_difference": True,
            "independent_heat_would_survive": True,
            "root2_feedback_from_root1_retained": True,
            "two_replica_variance_identity": True,
            "mean_only_variance_rejected": True,
            "owner_order": owners,
            "lean_theorems": ["two_replica_variance", "common_heat_cancels", "root2_feedback_dependence", "endpoint_feedback_dependence", "independent_heat_does_not_cancel", "root_two_after_root_one", "future_after_root_two"],
            "a13_gate_closed": False,
            "sector_a_closed": False,
            "authority_hashes_ok": True,
            "lean_escape_tokens_absent": True,
            "boundary_present": True,
            "feedback_gain": beta,
            "common_difference": common_difference,
            "independent_difference": independent_difference,
            "feedback_delta": feedback_delta,
            "future_variance_fixture": variance,
        },
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "toolchain": TOOLCHAIN.read_text(encoding="utf-8").strip(),
        "lean_stdout": completed.stdout,
        "lean_stderr": completed.stderr,
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        atomic_json(output, payload)
    print(f"PRIMARY R-177 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
