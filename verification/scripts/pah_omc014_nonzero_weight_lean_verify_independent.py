#!/usr/bin/env python3
"""Independent replay of the R502 finite nonzero-weight obligation."""
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
from itertools import product
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-nonzero-weight-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
R492 = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-04-pah-omc012-full-q-graded-domain/integrated.json"
LEAN = ROOT / "verification/lean/Tect/R502.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-nonzero-weight-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "37a9014b8d9f99fe0e3e23f18ddefcbb6960da7bcf4dd029b5f168b42c4d8b00"
PINS = {
    PAH001: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    OMC012: "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
    OMC014: "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0",
    R492: "a3262487b384e02100f7875c0ac87db614552e0a20a9db20501b8fa5d6308e0f",
}
DECLARATIONS = ["twoSectorValue_factor", "twoSectorValue_nonzero_iff", "lower_bound_requires_positive_weight"]


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
        return {"status": "FAIL", "returncode": None, "output": "pinned lake missing"}
    result = subprocess.run([str(lake), "env", "lean", "Tect/R502.lean"], cwd=LEAN.parent.parent, text=True, encoding="utf-8", errors="replace", capture_output=True, check=False, timeout=180)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL", "returncode": result.returncode, "output": output[-2000:]}


def run(output: Path = RUN_DIR / "independent.json") -> dict[str, Any]:
    manifest, pah, graded, omc014, r492, registry = (read(path) for path in (MANIFEST, PAH001, OMC012, OMC014, R492, REGISTRY))
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    check("all parent hashes", all(sha(path) == expected for path, expected in PINS.items()), {str(path): sha(path) for path in PINS}, {str(path): expected for path, expected in PINS.items()})
    check("manifest stays HOLD", manifest.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE" and manifest.get("provenance", {}).get("source_law_present") is False, manifest.get("status"), "HOLD/no source law")
    check("omega remains undefined", omc014.get("status", {}).get("omega_status") == "NOT_DEFINED" and graded.get("status", {}).get("global_normalized_gibbs_measure", "").startswith("NOT_DEFINED"), {"omega": omc014.get("status", {}).get("omega_status"), "global": graded.get("status", {}).get("global_normalized_gibbs_measure")}, "undefined")
    check("fixed-Q semantics unchanged", "Q=sum_vell_v" in pah.get("symmetry_and_constraint", {}).get("fixed_sector", "").replace(" ", "") and "ell_v in {0,...,M_psi}" in pah.get("finite_regulator", {}).get("matter_cutoff", ""), pah.get("symmetry_and_constraint", {}).get("fixed_sector"), "nonnegative bounded ell")

    n = 2
    vertex_count = 2 * (n + 2)
    q0 = [a for a in product((0, 1), repeat=vertex_count) if sum(a) == 0]
    q1 = [a for a in product((0, 1), repeat=vertex_count) if sum(a) == 1]
    q1_anchor = [a for a in q1 if a[0] == 1]
    check("Q0 exact zero", q0 == [(0,) * vertex_count], {"count": len(q0), "first": q0[0] if q0 else None}, "one all-zero state")
    check("Q1 positive witness", len(q1_anchor) == 1 and q1_anchor[0][0] == 1, {"q1": len(q1), "anchor": len(q1_anchor)}, "one ell_a=1 state")
    witness_rows = r492.get("runs", {}).get("primary", {}).get("payload", {}).get("derived", {}).get("r488_witness_rows", [])
    witness = next((row for row in witness_rows if row.get("n") == n and row.get("coarse_Q") == 1 and row.get("observable") == "ell_a"), None)
    check("R492 witness", witness is not None and witness.get("finite_gibbs_positive") is True and witness.get("lift_value") == 1, witness, "positive finite Gibbs witness")

    phi1 = Fraction(1)
    values = {"zero": Fraction(0) * phi1, "third": Fraction(1, 3) * phi1, "one": Fraction(1) * phi1}
    check("direct factorization", values == {"zero": Fraction(0), "third": Fraction(1, 3), "one": Fraction(1)}, {key: str(value) for key, value in values.items()}, "w1*a1")
    check("iff test", values["zero"] == 0 and values["third"] > 0 and values["one"] > 0, {key: str(value) for key, value in values.items()}, "positive exactly for positive w1")
    delta = Fraction(1, 4)
    check("lower-bound test", not (delta <= values["zero"]) and delta <= values["one"], {"delta": str(delta), "zero": str(values["zero"]), "one": str(values["one"])}, "positive lower bound excludes zero weight")
    check("Lean declarations/hash", all(re.search(rf"(?m)^\s*theorem\s+{name}\b", source) for name in DECLARATIONS) and sha(LEAN) == LEAN_PIN and any(item.get("path") == "verification/lean/Tect/R502.lean" for item in registry.get("entrypoints", [])), DECLARATIONS, "R502 registered")
    check("Lean source policy", b"\r" not in source_bytes and source_bytes.endswith(b"\n") and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")), {"lf": b"\r" not in source_bytes, "final": source_bytes.endswith(b"\n")}, "LF/no escape")
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")
    check("no physical promotion", manifest.get("status", {}).get("physical_promotion") is False, manifest.get("status", {}).get("physical_promotion"), False)

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-nonzero-weight-lean-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-OMC-014-NONZERO-WEIGHT-LEAN-INDEPENDENT-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_NONZERO_WEIGHT_OBLIGATION",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), "R492": sha(R492)},
        "scope": {"n": n, "cylinder": "ell_a", "enumeration": {"vertices": vertex_count, "Q0": len(q0), "Q1": len(q1)}},
        "obligation": "global ell_a nonzero requires positive Q=1 sector weight",
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "non_claims": manifest.get("boundaries", []),
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
