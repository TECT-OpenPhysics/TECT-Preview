#!/usr/bin/env python3
"""Fixed-power locality audit for the unchanged PAH-OMC-013 lift.

This is a finite, conditional bridge.  It derives a growing support threshold
N_k for each fixed generator power; it does not claim that one N(f) works for
the exponential series or that the anchored-n target is identified.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-020-iterate-locality-contract-v1.json"
PAH = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC013 = ROOT / "strategy/pa-hyp/PAH-OMC-013-full-q-eventual-intertwining-v1.json"
OMC013_CODE = ROOT / "codes/foundations/pah_omc013_full_q_eventual_intertwining.py"
R550 = ROOT / "strategy/pa-hyp/PAH-OMC-020-finite-semigroup-lift-result-v1.json"
R551 = ROOT / "strategy/pa-hyp/PAH-OMC-020-second-order-defect-result-v1.json"
R551_CODE = ROOT / "verification/scripts/pah_omc020_second_order_defect.py"
LEAN = ROOT / "verification/lean/Tect/PahOmc020FiniteSemigroup.lean"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-08-pah-omc020-iterate-locality/primary.json"

PINS = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-013": "e2d2aa4beeb67c535ab19bbed48fb51253e9b08d407d67e96e12978ecf7170bc",
    "R-550": "a3e24dc96e3ca6fb01f991ab7d1062da06af82b3252100148f365c094b03c35c",
    "R-551": "c0bb72f9cbb409c4474d3adc3b0754f10cc0825378443f9a61ad162a7febe134",
    "OMC013-code": "bda0c7bd7ed5f8b3871fd7590b600458589c4b5feBA0a147219e94cdae0526a0".lower(),
    "R551-code": "",
    "Lean-finite-semigroup": "",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_omc013() -> Any:
    spec = importlib.util.spec_from_file_location("pah_omc013_iterate_locality", OMC013_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen OMC-013 implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def closure(module: Any, support: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Conservative one-step dependency closure from root supports."""
    level = max(2, max((vertex[0] for vertex in support), default=0) + 5)
    result = set(support)
    for root in module.root_catalog(level):
        if set(root["core_vertices"]) & support:
            result.update(root["support_vertices"])
    return result


def support_rows(module: Any, depth: int) -> list[dict[str, Any]]:
    support = {(0, 0)}
    rows: list[dict[str, Any]] = []
    for k in range(depth + 1):
        max_column = max((vertex[0] for vertex in support), default=0)
        expected = {(column, row) for column in range(2 * k + 1) for row in (0, 1)}
        # At depth zero the observable has one vertex; later closures fill the
        # two-row strip through column 2k.  These are structural test oracles,
        # while the support itself is derived from the frozen root catalog.
        rows.append({
            "k": k,
            "support_size": len(support),
            "max_column": max_column,
            "expected_max_column": 0 if k == 0 else 2 * k,
            "N_k": max(2, max_column + 1),
            "expected_N_k": max(2, 2 * k + 1),
            "support_matches_expected": support == ({(0, 0)} if k == 0 else expected),
        })
        support = closure(module, support)
    return rows


def check(rows: list[dict[str, Any]], name: str, ok: bool, detail: Any) -> None:
    rows.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})


def finite_second_order_boundary_check(module: Any) -> dict[str, Any]:
    """Replay the already frozen R-551 helper at its safe threshold witness."""
    spec = importlib.util.spec_from_file_location("pah_omc020_r551_helper", R551_CODE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R-551 helper")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    out: dict[str, Any] = {}
    for n in (3, 5):
        fine = helper.state_key(module.sample_state(n + 1, 3))
        coarse = helper.state_key(module.project_state(n, helper.state_from_key(fine))[0])
        residual = helper.poly_sub(
            helper.second_poly(module, n + 1, fine, 1, lift_to=n),
            helper.second_poly(module, n, coarse, 1),
        )
        out[str(n)] = {
            "terms": helper.poly_text(residual),
            "numeric": helper.numeric(residual),
            "zero": not bool(residual),
        }
    return out


def run(output: Path | None = None) -> dict[str, Any]:
    contract = load(CONTRACT)
    module = load_omc013()
    PINS["R551-code"] = sha(R551_CODE)
    PINS["Lean-finite-semigroup"] = sha(LEAN)
    actual = {
        "PAH-001": sha(PAH),
        "PAH-OMC-013": sha(OMC013),
        "R-550": sha(R550),
        "R-551": sha(R551),
        "OMC013-code": sha(OMC013_CODE),
        "R551-code": sha(R551_CODE),
        "Lean-finite-semigroup": sha(LEAN),
    }
    rows: list[dict[str, Any]] = []
    check(rows, "source pins", actual["PAH-001"] == PINS["PAH-001"] and actual["PAH-OMC-013"] == PINS["PAH-OMC-013"], actual)
    check(rows, "contract identity", contract.get("contract_id") == "PAH-OMC-020-ITERATE-LOCALITY" and contract.get("result_id") == "R-561", contract.get("contract_id"))
    source = load(PAH)
    check(rows, "unchanged PAH generator", source["dynamics"]["generator"].startswith("(L_rho f)(x)=sum_r"), source["dynamics"]["generator"])
    check(rows, "external Markov time", "external stochastic" in source["dynamics"]["time"].lower(), source["dynamics"]["time"])
    check(rows, "finite semigroup bridge remains conditional", contract["decision_rule"]["HOLD_FOR_EVIDENCE"].startswith("Keep the PAH-OMC-020"), contract["decision_rule"])

    radius_rows = [{"level": level, "radius": module.root_radius(level), "root_count": len(module.root_catalog(level))} for level in range(2, 10)]
    check(rows, "derived root radius", all(item["radius"] == 2 for item in radius_rows), radius_rows)
    supports = support_rows(module, 5)
    check(rows, "fixed-power support closure", all(item["support_matches_expected"] for item in supports), supports)
    check(rows, "growing threshold", all(item["N_k"] == item["expected_N_k"] for item in supports), supports)
    check(rows, "threshold strictly grows", all(supports[index]["N_k"] < supports[index + 1]["N_k"] for index in range(len(supports) - 1)), supports)

    separation_rows = []
    for row in supports:
        k = row["k"]
        n = row["N_k"]
        prior_support = {(0, 0)}
        for _ in range(max(0, k - 1)):
            prior_support = closure(module, prior_support)
        coarse_labels = {root["label"] for root in module.root_catalog(n) if set(root["core_vertices"]) & prior_support}
        fine_labels = {root["label"] for root in module.root_catalog(n + 1) if set(root["core_vertices"]) & prior_support and max(v[0] for v in root["support_vertices"]) <= n}
        separation_rows.append({"k": k, "n": n, "matched": coarse_labels == fine_labels, "coarse_active": len(coarse_labels), "fine_active": len(fine_labels)})
    check(rows, "frontier separated at N_k", all(item["matched"] for item in separation_rows), separation_rows)

    boundary = finite_second_order_boundary_check(module)
    check(rows, "R-551 threshold diagnostic", bool(boundary["3"]["terms"]) and boundary["5"]["zero"], boundary)
    check(rows, "Lean source is present", LEAN.is_file(), str(LEAN))
    check(rows, "non-promotion firewall", not contract["provenance"]["claim_bearing"] and not contract["provenance"]["active_gate_change"] and not contract["provenance"]["physical_promotion"], contract["provenance"])
    failed = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/pah-omc020-iterate-locality-primary/1.0",
        "result_id": "R-561",
        "task_id": "T-086",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "PASS_CONDITIONAL" if not failed else "HOLD_FOR_EVIDENCE",
        "classification": "auxiliary_support",
        "claim_bearing": False,
        "active_gate_change": False,
        "physical_promotion": False,
        "source_hashes": actual,
        "support_rows": supports,
        "radius_rows": radius_rows,
        "separation_rows": separation_rows,
        "boundary_diagnostic": boundary,
        "checks": rows,
        "checks_passed": len(rows) - len(failed),
        "checks_failed": len(failed),
        "finding": contract["conditional_statement"],
        "missing_assumptions": contract["missing_assumptions"],
        "non_claims": contract["non_claims"],
        "reproduction": contract["reproduction"],
        "code_sha256": sha(Path(__file__)),
    }
    if output is not None:
        atomic_json(output, payload)
    print(f"PAH-OMC-020 ITERATE LOCALITY: {payload['verification']} {payload['checks_passed']}/{len(rows)}; verdict={payload['verdict']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = None if args.check else (args.output if args.output.is_absolute() else ROOT / args.output)
    return 0 if run(output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
