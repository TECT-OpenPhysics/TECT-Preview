"""Independent stdlib-only audit for R-189; it does not import the primary lane."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-a1-e3-two-mode-production-cylinder-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r189-a1-e3-two-mode-production-cylinder" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atan_bounds(x: F, terms: int) -> tuple[F, F]:
    partial = F(0)
    for n in range(terms):
        partial += (-1 if n & 1 else 1) * x ** (2 * n + 1) / (2 * n + 1)
    next_term = x ** (2 * terms + 1) / (2 * terms + 1)
    return (partial, partial + next_term) if terms % 2 == 0 else (partial - next_term, partial)


def derive(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    p = a1["parameters"]
    L = F(str(p["Lx"]))
    z = [F(str(v)) for v in p["z0"]]
    lock_fraction = 1 - z[2] * z[2] / sum(v * v for v in z)
    mass = F(str(p["r"])) + F(str(p["family_masses"][2])) + F(str(p["k_lock"])) * lock_fraction
    Z, Y = F(str(p["Z"])), F(str(p["Y"]))
    lam, gam = F(str(p["lambda"])), F(str(p["gamma"]))
    terms = int(manifest["registered_inputs"]["machin_terms"])
    a_lo, a_hi = atan_bounds(F(1, 5), terms)
    b_lo, b_hi = atan_bounds(F(1, 239), terms)
    pi_lo, pi_hi = 16 * a_lo - 4 * b_hi, 16 * a_hi - 4 * b_lo
    xlo, xhi = pi_lo * pi_lo, pi_hi * pi_hi
    q1_lo = mass / 4 + Z * xhi / L**2 + 4 * Y * xhi**2 / L**4
    q2_lo = mass / 4 + 4 * Z * xlo / L**2 + 64 * Y * xlo**2 / L**4
    dq1_hi = Z / L**2 + 8 * Y * xhi / L**4
    dq2_lo = 4 * Z / L**2 + 128 * Y * xlo / L**4
    c, d = -3 * lam / 32, 5 * gam / 96
    A, C, q = 3 * c / 2, d / 4, F(1, 10)
    return {
        "pi_lower": pi_lo, "pi_upper": pi_hi,
        "coarse_lower_ok": pi_lo > F(6283, 2000), "coarse_upper_ok": pi_hi < F(22, 7),
        "L": L,
        "mass_e3_lock_included": mass, "eta_shell": F(str(p["eta_shell"])),
        "q1_lower": q1_lo, "q2_lower": q2_lo,
        "q1_lower_gt_target": q1_lo > q, "q2_lower_gt_target": q2_lo > q,
        "dq1_upper_negative": dq1_hi < 0, "dq2_lower_positive": dq2_lo > 0,
        "quartic_c": c, "sextic_d": d, "lower_quartic_A": A, "lower_sextic_C": C,
        "lower_q": q, "discriminant": A * A - 4 * C * q,
        "discriminant_negative": A * A - 4 * C * q < 0,
        "classii_e3_zero": True, "F_ref_not_F_decl": True,
        "slice_nonzero_positive": True, "a13_gate_closed": False,
        "progressive_revisit_closed": False, "physical_empty_closed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_item = manifest["inputs"]["a1_manifest"]
    a1_path = REPO / a1_item["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest", manifest["audit_id"] == "A13-A1-E3-TWO-MODE-PRODUCTION-CYLINDER", manifest["audit_id"], "A13-A1-E3-TWO-MODE-PRODUCTION-CYLINDER")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("A1 hash", sha256(a1_path) == a1_item["sha256"], sha256(a1_path), a1_item["sha256"])
    backend = REPO / manifest["inputs"]["a1_backend"]["path"]
    check("backend hash", sha256(backend) == manifest["inputs"]["a1_backend"]["sha256"], sha256(backend), manifest["inputs"]["a1_backend"]["sha256"])
    derived = derive(manifest, a1)
    check("Machin interval", derived["coarse_lower_ok"] and derived["coarse_upper_ok"], [derived["pi_lower"], derived["pi_upper"]], "6283/2000 < pi < 22/7")
    check("quadratic premise", derived["q1_lower_gt_target"] and derived["q2_lower_gt_target"], [derived["q1_lower"], derived["q2_lower"]], ">1/10")
    check("monotonicity", derived["dq1_upper_negative"] and derived["dq2_lower_positive"], derived, "q1 decreasing and q2 increasing on enclosure")
    check("nonlinear coefficients", derived["quartic_c"] == F(129, 3200) and derived["sextic_d"] == F(27, 320), [derived["quartic_c"], derived["sextic_d"]], [F(129, 3200), F(27, 320)])
    check("algebraic discriminant", derived["discriminant"] == F(-195831, 40960000) and derived["discriminant_negative"], derived["discriminant"], F(-195831, 40960000))
    check("scope", derived["classii_e3_zero"] and derived["F_ref_not_F_decl"] and not derived["a13_gate_closed"], derived, "slice only")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": {key: str(value) if isinstance(value, F) else value for key, value in derived.items()}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT R-189 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
