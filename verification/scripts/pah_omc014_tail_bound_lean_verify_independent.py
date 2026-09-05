#!/usr/bin/env python3
"""Independent replay of the conditional R506 weighted-tail bound."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-tail-bound-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
R503 = ROOT / "strategy/pa-hyp/PAH-OMC-014-mixture-cauchy-lean-manifest.json"
R504 = ROOT / "strategy/pa-hyp/PAH-OMC-014-separator-lean-manifest.json"
R505 = ROOT / "strategy/pa-hyp/PAH-OMC-014-sign-change-lean-manifest.json"
PROJECTIVE = ROOT / "strategy/pa-hyp/PAH-OMC-014-projective-kernel-obligation-260905.md"
Q0 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-q0-projective-obstruction/integrated.json"
LEAN = ROOT / "verification/lean/Tect/R506.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-tail-bound-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "1156ed970d985df2bded2ce5bea399e0502128fc608883802c88c19e74827b51"
DECLARATIONS = ["weighted_tail_abs_bound", "tail_bound_zero"]
PINS = {
    PAH001: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    OMC014: "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0",
    R503: "25ae1c3e67444c4dcca73c93bb2ecb82b30d2750daf477feb0b7cafe4a393d2a",
    R504: "83f0c578fb44de7e33b646ef2cee3a7d757c6ede6db40c60da31b9651e463186",
    R505: "b7918dec2224b66523c5ed872c23b67a0a331d36d3765df65a242ae0457f8497",
    PROJECTIVE: "ea8495c9e12e464506ece41f4e75fe3044c922c1da71ea56dea0e387d8ac5d1e",
    Q0: "3938987009c2ccf1a81272655277f1fa21dbfddc47fd49e2497975dc86e7f6fe",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def compile_lean() -> dict[str, Any]:
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    lake = next((base / name for name in ("lake.exe", "lake") if (base / name).is_file()), None)
    if lake is None:
        found = shutil.which("lake")
        lake = Path(found) if found else None
    if lake is None:
        return {"status": "FAIL", "returncode": None, "output": "pinned lake executable missing"}
    result = subprocess.run(
        [str(lake), "env", "lean", "Tect/R506.lean"],
        cwd=LEAN.parent.parent,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    return {
        "status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": result.returncode,
        "command": "lake env lean Tect/R506.lean",
        "output": output[-2000:],
    }


def run(output: Path = RUN_DIR / "independent.json") -> dict[str, Any]:
    manifest = read(MANIFEST)
    omc014 = read(OMC014)
    r503 = read(R503)
    r504 = read(R504)
    r505 = read(R505)
    registry = read(REGISTRY)
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    actual_pins = {str(path): sha(path) for path in PINS}
    expected_pins = {str(path): expected for path, expected in PINS.items()}
    check("all parent hashes", actual_pins == expected_pins, actual_pins, expected_pins)
    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check(
        "manifest remains conditional HOLD",
        status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("claim_bearing") is False
        and status.get("active_gate_change") is False
        and provenance.get("source_law_present") is False
        and status.get("physical_promotion") is False,
        {"status": status, "provenance": provenance},
        "HOLD/no law/no gate change",
    )
    check(
        "parent full-Q remains undefined",
        omc014.get("status", {}).get("omega_status") == "NOT_DEFINED",
        omc014.get("status", {}).get("omega_status"),
        "NOT_DEFINED",
    )
    check(
        "prior conditional bridges remain open",
        all(item.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" for item in (r503, r504, r505)),
        {name: item.get("status", {}).get("verdict") for name, item in (("R503", r503), ("R504", r504), ("R505", r505))},
        "all HOLD",
    )
    check(
        "fixed roles retained",
        "16/9" in manifest.get("boundary_and_uniformity", {}).get("R-484", "")
        and "540" in manifest.get("boundary_and_uniformity", {}).get("R-490", "")
        and "domination-only" in manifest.get("boundary_and_uniformity", {}).get("R-490", ""),
        manifest.get("boundary_and_uniformity"),
        "defect retained; domination only",
    )
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    check(
        "Lean declarations and registry",
        all(name in declared for name in DECLARATIONS)
        and sha(LEAN) == LEAN_PIN
        and next(
            (
                item
                for item in registry.get("entrypoints", [])
                if item.get("path") == "verification/lean/Tect/R506.lean"
            ),
            {},
        ).get("sha256")
        == LEAN_PIN,
        {"declarations": DECLARATIONS, "sha256": sha(LEAN)},
        "exact declarations/hash",
    )
    check(
        "Lean source policy",
        b"\r" not in source_bytes
        and source_bytes.endswith(b"\n")
        and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")),
        {"lf": b"\r" not in source_bytes, "final_newline": source_bytes.endswith(b"\n")},
        "LF/no escape",
    )
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")

    weights = (Fraction(1, 5), Fraction(2, 5), Fraction(2, 5))
    values = (Fraction(-3), Fraction(1), Fraction(2))
    c = Fraction(3)
    tau = Fraction(1)
    tail_mass = sum(weights)
    weighted_tail = sum(weight * value for weight, value in zip(weights, values))
    triangle_sum = sum(weight * abs(value) for weight, value in zip(weights, values))
    envelope_sum = sum(weight * c for weight in weights)
    bound = c * tau
    check(
        "independent hypotheses",
        all(weight >= 0 for weight in weights)
        and c >= 0
        and all(abs(value) <= c for value in values)
        and tail_mass <= tau,
        {
            "weights": [str(item) for item in weights],
            "values": [str(item) for item in values],
            "tail_mass": str(tail_mass),
            "c": str(c),
            "tau": str(tau),
        },
        "w>=0, c>=0, |a_i|<=c, sum(w)<=tau",
    )
    check(
        "triangle and envelope chain",
        abs(weighted_tail) <= triangle_sum <= envelope_sum <= bound,
        {
            "absolute_tail": str(abs(weighted_tail)),
            "triangle_sum": str(triangle_sum),
            "envelope_sum": str(envelope_sum),
            "bound": str(bound),
        },
        "abs(sum)<=sum(w*abs(a))<=c*sum(w)<=c*tau",
    )
    zero_tail = sum(weight * Fraction(0) for weight in weights)
    check("independent zero-tail corollary", abs(zero_tail) == 0, str(zero_tail), "zero")
    check(
        "non-claim firewall",
        manifest.get("status", {}).get("physical_promotion") is False
        and any("limit" in item.lower() for item in manifest.get("non_claims", []))
        and any("physical" in item.lower() for item in manifest.get("non_claims", [])),
        manifest.get("non_claims", []),
        "no limit or physical promotion",
    )

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-tail-bound-lean-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-OMC-014-TAIL-BOUND-LEAN-INDEPENDENT-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_FINITE_TAIL_BOUND",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {
            "manifest": sha(MANIFEST),
            "lean": sha(LEAN),
            **{path.name: expected for path, expected in PINS.items()},
        },
        "scope": {
            "tail_card": len(weights),
            "weights": [str(item) for item in weights],
            "component_values": [str(item) for item in values],
            "common_envelope": str(c),
            "tail_mass_bound": str(tau),
            "source_owned_tail_law": "not supplied",
        },
        "derived": {
            "tail_mass": str(tail_mass),
            "weighted_tail": str(weighted_tail),
            "absolute_tail": str(abs(weighted_tail)),
            "triangle_sum": str(triangle_sum),
            "envelope_sum": str(envelope_sum),
            "certified_upper_bound": str(bound),
            "formula": "|sum_i w_i a_i| <= c * tau",
        },
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
        "non_claims": manifest.get("non_claims", []),
        "next_question": manifest.get("next_question"),
        "reproduction": manifest.get("reproduction", {}),
        "lean": lean,
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "independent.json")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
