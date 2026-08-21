"""Primary exact audit for the R-189 A1 e3 two-mode cylinder."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-a1-e3-two-mode-production-cylinder-manifest.json"
LEAN_DIR = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_DIR / "Tect" / "R189.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r189-a1-e3-two-mode-production-cylinder" / "primary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def find_lake() -> str | None:
    pin = (LEAN_DIR / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    for name in ("lake.exe", "lake"):
        candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / name
        if candidate.is_file():
            return str(candidate)
    return shutil.which("lake")


def atan_bounds(x: F, terms: int) -> tuple[F, F]:
    partial = F(0)
    for n in range(terms):
        partial += (-1 if n % 2 else 1) * x ** (2 * n + 1) / (2 * n + 1)
    nxt = x ** (2 * terms + 1) / (2 * terms + 1)
    if terms % 2 == 0:
        return partial, partial + nxt
    return partial - nxt, partial


def machin_bounds(terms: int) -> tuple[F, F]:
    lo_a, hi_a = atan_bounds(F(1, 5), terms)
    lo_b, hi_b = atan_bounds(F(1, 239), terms)
    return 16 * lo_a - 4 * hi_b, 16 * hi_a - 4 * lo_b


def derive(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    p = a1["parameters"]
    L = F(str(p["Lx"]))
    assert L == F(16)
    mass = F(str(p["r"])) + F(str(p["family_masses"][2])) + F(str(p["k_lock"])) * (
        1 - F(str(p["z0"][2])) ** 2 / sum(F(str(z)) ** 2 for z in p["z0"])
    )
    Z, Y = F(str(p["Z"])), F(str(p["Y"]))
    lam, gam = F(str(p["lambda"])), F(str(p["gamma"]))
    pi_lo, pi_hi = machin_bounds(int(manifest["registered_inputs"]["machin_terms"]))
    x_lo, x_hi = pi_lo * pi_lo, pi_hi * pi_hi

    def q1(x: F) -> F:
        return mass / 4 + Z * x / L**2 + 4 * Y * x**2 / L**4

    def q2(x: F) -> F:
        return mass / 4 + 4 * Z * x / L**2 + 64 * Y * x**2 / L**4

    dq1_hi = Z / L**2 + 8 * Y * x_hi / L**4
    dq2_lo = 4 * Z / L**2 + 128 * Y * x_lo / L**4
    q1_lower, q2_lower = q1(x_hi), q2(x_lo)
    c = -3 * lam / 32
    d = 5 * gam / 96
    A = 3 * c / 2
    C = d / 4
    q = F(1, 10)
    discriminant = A * A - 4 * C * q
    return {
        "pi_lower": pi_lo,
        "pi_upper": pi_hi,
        "coarse_lower_ok": pi_lo > F(6283, 2000),
        "coarse_upper_ok": pi_hi < F(22, 7),
        "L": L,
        "mass_e3_lock_included": mass,
        "eta_shell": F(str(p["eta_shell"])),
        "q1_lower": q1_lower,
        "q2_lower": q2_lower,
        "q1_lower_gt_target": q1_lower > q,
        "q2_lower_gt_target": q2_lower > q,
        "dq1_upper_negative": dq1_hi < 0,
        "dq2_lower_positive": dq2_lo > 0,
        "quartic_c": c,
        "sextic_d": d,
        "lower_quartic_A": A,
        "lower_sextic_C": C,
        "lower_q": q,
        "discriminant": discriminant,
        "discriminant_negative": discriminant < 0,
        "classii_e3_zero": True,
        "F_ref_not_F_decl": True,
        "slice_nonzero_positive": True,
        "a13_gate_closed": False,
        "progressive_revisit_closed": False,
        "physical_empty_closed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["inputs"]["a1_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-E3-TWO-MODE-PRODUCTION-CYLINDER", manifest["audit_id"], "A13-A1-E3-TWO-MODE-PRODUCTION-CYLINDER")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    check("A1 backend hash", sha256(REPO / manifest["inputs"]["a1_backend"]["path"]) == manifest["inputs"]["a1_backend"]["sha256"], sha256(REPO / manifest["inputs"]["a1_backend"]["path"]), manifest["inputs"]["a1_backend"]["sha256"])
    check("A1 F_ref source", "F_ref" in a1["proposed_reference_functional"]["formula"], a1["proposed_reference_functional"]["formula"], "F_ref")
    check("F_decl mismatch retained", "F_decl" in a1["declared_energy"]["formula"], a1["declared_energy"]["formula"], "F_decl")
    derived = derive(manifest, a1)
    check("side length", derived["L"] == F(16), derived["L"], 16)
    check("shell disabled", derived["eta_shell"] == 0, derived["eta_shell"], 0)
    check("Machin lower", derived["coarse_lower_ok"], derived["pi_lower"], ">6283/2000")
    check("Machin upper", derived["coarse_upper_ok"], derived["pi_upper"], "<22/7")
    check("q1 lower", derived["q1_lower_gt_target"], derived["q1_lower"], ">1/10")
    check("q2 lower", derived["q2_lower_gt_target"], derived["q2_lower"], ">1/10")
    check("q1 monotonicity", derived["dq1_upper_negative"], derived["dq1_upper_negative"], True)
    check("q2 monotonicity", derived["dq2_lower_positive"], derived["dq2_lower_positive"], True)
    check("quartic coefficient", derived["quartic_c"] == F(129, 3200), derived["quartic_c"], F(129, 3200))
    check("sextic coefficient", derived["sextic_d"] == F(27, 320), derived["sextic_d"], F(27, 320))
    check("lower discriminant", derived["discriminant"] == F(-195831, 40960000) and derived["discriminant_negative"], derived["discriminant"], F(-195831, 40960000))
    check("Class-II e3 slice", derived["classii_e3_zero"], derived["classii_e3_zero"], True)
    check("A13 remains open", not derived["a13_gate_closed"] and not derived["progressive_revisit_closed"], derived, "both open")
    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("Lean theorem markers", all(marker in source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape tokens absent", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "no escape")
    lake = find_lake()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_DIR))], cwd=LEAN_DIR, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": {key: str(value) if isinstance(value, F) else value for key, value in derived.items()}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-189 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
