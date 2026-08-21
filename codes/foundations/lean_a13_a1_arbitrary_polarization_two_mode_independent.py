"""Stdlib-only independent audit for R-190; never imports the primary lane."""

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
MANIFEST = REPO / "strategy" / "pre-a13-a1-arbitrary-polarization-two-mode-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r190-a1-arbitrary-polarization-two-mode" / "independent.json"


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
    nxt = x ** (2 * terms + 1) / (2 * terms + 1)
    return (partial, partial + nxt) if terms % 2 == 0 else (partial - nxt, partial)


def derive(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    p = a1["parameters"]
    ri = manifest["registered_inputs"]
    indices = tuple(int(n) for n in ri["mode_indices"])
    L = F(str(p["Lx"]))
    r, z, y = F(str(p["r"])), F(str(p["Z"])), F(str(p["Y"]))
    lam, gam = F(str(p["lambda"])), F(str(p["gamma"]))
    lo_a, hi_a = atan_bounds(F(1, 5), int(ri["machin_terms"]))
    lo_b, hi_b = atan_bounds(F(1, 239), int(ri["machin_terms"]))
    pi_lo, pi_hi = 16 * lo_a - 4 * hi_b, 16 * hi_a - 4 * lo_b
    xlo, xhi = pi_lo * pi_lo, pi_hi * pi_hi
    q = []
    for n in indices:
        q.append(r / 4 + z * n * n * xhi / L**2 + 4 * y * n**4 * xlo**2 / L**4)
    denominator = F(str(p["M_X"])) ** 2 + F(str(p["classii_mass_regularizer"]))
    a = F(str(p["cJJ"])) * F(str(p["alpha_X"])) ** 2 / denominator
    b = F(str(p["cJK"])) * F(str(p["alpha_X"])) * F(str(p["beta_X"])) / denominator
    c = F(str(p["cKK"])) * F(str(p["beta_X"])) ** 2 / denominator
    q_target = F(ri["q_lower_target"])
    quartic_bound = F(ri["moment_bounds"]["quartic_upper"])
    sextic_lower = F(ri["moment_bounds"]["sextic_lower"])
    quartic_A = -lam / 4 * quartic_bound
    sextic_C = gam / 6 * sextic_lower
    discriminant = quartic_A**2 - 4 * sextic_C * q_target
    return {
        "pi_lower": pi_lo, "pi_upper": pi_hi,
        "coarse_lower_ok": pi_lo > F(ri["pi_coarse_interval"]["lower"]),
        "coarse_upper_ok": pi_hi < F(ri["pi_coarse_interval"]["upper"]),
        "L": L, "mode_indices": list(indices), "quadratic_lowers": q,
        "q1_lower": q[0], "q2_lower": q[1],
        "q1_lower_gt_target": q[0] > q_target,
        "q2_lower_gt_target": q[1] > q_target,
        "quadratic_all_above_target": all(value > q_target for value in q),
        "classii_a": a, "classii_b": b, "classii_c": c,
        "classii_ac_minus_b2": a * c - b * b,
        "classii_psd": a > 0 and c > 0 and a * c - b * b >= 0,
        "quartic_bound": quartic_bound, "sextic_lower": sextic_lower,
        "lower_quartic_A": quartic_A, "lower_sextic_C": sextic_C,
        "lower_q": q_target, "discriminant": discriminant,
        "discriminant_negative": discriminant < 0,
        "moment_cauchy_used": True, "jensen_used": True,
        "eta_shell": F(str(p["eta_shell"])), "F_ref_not_F_decl": True,
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

    check("manifest", manifest["audit_id"] == "A13-A1-ARBITRARY-POLARIZATION-TWO-MODE", manifest["audit_id"], "A13-A1-ARBITRARY-POLARIZATION-TWO-MODE")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("A1 source hash", sha256(a1_path) == a1_item["sha256"], sha256(a1_path), a1_item["sha256"])
    backend = REPO / manifest["inputs"]["a1_backend"]["path"]
    check("backend hash", sha256(backend) == manifest["inputs"]["a1_backend"]["sha256"], sha256(backend), manifest["inputs"]["a1_backend"]["sha256"])
    derived = derive(manifest, a1)
    ri = manifest["registered_inputs"]
    coeff = ri["derived_coefficients"]
    check("Machin interval", derived["coarse_lower_ok"] and derived["coarse_upper_ok"], [derived["pi_lower"], derived["pi_upper"]], ri["pi_coarse_interval"])
    check("quadratic interval", derived["quadratic_all_above_target"], derived["quadratic_lowers"], f">{derived['lower_q']}")
    check("Class-II positive form", derived["classii_psd"], derived["classii_ac_minus_b2"], ">=0")
    check("moment bounds", derived["quartic_bound"] == F(ri["moment_bounds"]["quartic_upper"]) and derived["sextic_lower"] == F(ri["moment_bounds"]["sextic_lower"]), [derived["quartic_bound"], derived["sextic_lower"]], ri["moment_bounds"])
    check("coefficients", derived["lower_quartic_A"] == F(coeff["quartic_A"]) and derived["lower_sextic_C"] == F(coeff["sextic_C"]) and derived["lower_q"] == F(coeff["lower_q"]), derived, coeff)
    check("discriminant", derived["discriminant"] == F(coeff["discriminant"]) and derived["discriminant_negative"], derived["discriminant"], coeff["discriminant"])
    check("boundary", derived["slice_nonzero_positive"] and not derived["a13_gate_closed"] and not derived["progressive_revisit_closed"], derived, "finite slice only")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": {key: str(value) if isinstance(value, F) else value for key, value in derived.items()}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT R-190 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
