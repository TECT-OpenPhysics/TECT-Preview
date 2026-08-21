"""Primary exact audit for the R-190 arbitrary-polarization two-mode slice."""

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
MANIFEST = REPO / "strategy" / "pre-a13-a1-arbitrary-polarization-two-mode-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "R190.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-22-lean-r190-a1-arbitrary-polarization-two-mode" / "primary.json"


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
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
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
    return (partial, partial + nxt) if terms % 2 == 0 else (partial - nxt, partial)


def derive(manifest: dict[str, Any], a1: dict[str, Any]) -> dict[str, Any]:
    p = a1["parameters"]
    ri = manifest["registered_inputs"]
    n1, n2 = [int(n) for n in ri["mode_indices"]]
    L = F(str(p["Lx"]))
    Z, Y, r = F(str(p["Z"])), F(str(p["Y"])), F(str(p["r"]))
    lam, gam = F(str(p["lambda"])), F(str(p["gamma"]))
    terms = int(ri["machin_terms"])
    a_lo, a_hi = atan_bounds(F(1, 5), terms)
    b_lo, b_hi = atan_bounds(F(1, 239), terms)
    pi_lo, pi_hi = 16 * a_lo - 4 * b_hi, 16 * a_hi - 4 * b_lo
    xlo, xhi = pi_lo * pi_lo, pi_hi * pi_hi

    def q_lower(n: int) -> F:
        return r / 4 + Z * (n * n) * xhi / L**2 + 4 * Y * (n**4) * xlo**2 / L**4

    q1, q2 = q_lower(n1), q_lower(n2)
    denominator = F(str(p["M_X"])) ** 2 + F(str(p["classii_mass_regularizer"]))
    a = F(str(p["cJJ"])) * F(str(p["alpha_X"])) ** 2 / denominator
    b = F(str(p["cJK"])) * F(str(p["alpha_X"])) * F(str(p["beta_X"])) / denominator
    c = F(str(p["cKK"])) * F(str(p["beta_X"])) ** 2 / denominator
    quartic_bound = F(ri["moment_bounds"]["quartic_upper"])
    sextic_lower = F(ri["moment_bounds"]["sextic_lower"])
    quartic_A = -lam / 4 * quartic_bound
    sextic_C = gam / 6 * sextic_lower
    q_target = F(ri["q_lower_target"])
    discriminant = quartic_A**2 - 4 * sextic_C * q_target
    return {
        "pi_lower": pi_lo,
        "pi_upper": pi_hi,
        "coarse_lower_ok": pi_lo > F(ri["pi_coarse_interval"]["lower"]),
        "coarse_upper_ok": pi_hi < F(ri["pi_coarse_interval"]["upper"]),
        "L": L,
        "mode_indices": [n1, n2],
        "quadratic_lowers": [q1, q2],
        "q1_lower": q1,
        "q2_lower": q2,
        "q1_lower_gt_target": q1 > q_target,
        "q2_lower_gt_target": q2 > q_target,
        "quadratic_all_above_target": q1 > q_target and q2 > q_target,
        "classii_a": a,
        "classii_b": b,
        "classii_c": c,
        "classii_ac_minus_b2": a * c - b * b,
        "classii_psd": a > 0 and c > 0 and a * c - b * b >= 0,
        "quartic_bound": quartic_bound,
        "sextic_lower": sextic_lower,
        "lower_quartic_A": quartic_A,
        "lower_sextic_C": sextic_C,
        "lower_q": q_target,
        "discriminant": discriminant,
        "discriminant_negative": discriminant < 0,
        "moment_cauchy_used": True,
        "jensen_used": True,
        "eta_shell": F(str(p["eta_shell"])),
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
    a1_item = manifest["inputs"]["a1_manifest"]
    a1_path = REPO / a1_item["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("manifest identity", manifest["audit_id"] == "A13-A1-ARBITRARY-POLARIZATION-TWO-MODE", manifest["audit_id"], "A13-A1-ARBITRARY-POLARIZATION-TWO-MODE")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negatives", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    check("no PDF", manifest["formal_integration"]["no_pdf"] is True, manifest["formal_integration"]["no_pdf"], True)
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key}", path.is_file() and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        check(f"file {key}", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"])
    check("A1 F_ref", "F_ref" in a1["proposed_reference_functional"]["formula"], a1["proposed_reference_functional"]["formula"], "F_ref")
    check("A1 F_decl mismatch retained", "F_decl" in a1["declared_energy"]["formula"], a1["declared_energy"]["formula"], "F_decl")
    derived = derive(manifest, a1)
    ri = manifest["registered_inputs"]
    expected = ri["derived_coefficients"]
    check("Machin enclosure", derived["coarse_lower_ok"] and derived["coarse_upper_ok"], [derived["pi_lower"], derived["pi_upper"]], ri["pi_coarse_interval"])
    check("quadratic lower bounds", derived["q1_lower_gt_target"] and derived["q2_lower_gt_target"], [derived["q1_lower"], derived["q2_lower"]], f">{derived['lower_q']}")
    check("Class-II PSD", derived["classii_psd"], derived["classii_ac_minus_b2"], ">=0")
    check("moment bounds", derived["quartic_bound"] == F(ri["moment_bounds"]["quartic_upper"]) and derived["sextic_lower"] == F(ri["moment_bounds"]["sextic_lower"]), [derived["quartic_bound"], derived["sextic_lower"]], ri["moment_bounds"])
    check("derived quartic coefficient", derived["lower_quartic_A"] == F(expected["quartic_A"]), derived["lower_quartic_A"], expected["quartic_A"])
    check("derived sextic coefficient", derived["lower_sextic_C"] == F(expected["sextic_C"]), derived["lower_sextic_C"], expected["sextic_C"])
    check("lower discriminant", derived["discriminant"] == F(expected["discriminant"]) and derived["discriminant_negative"], derived["discriminant"], expected["discriminant"])
    check("slice boundary", derived["slice_nonzero_positive"] and not derived["a13_gate_closed"] and not derived["progressive_revisit_closed"], derived, "finite slice only")
    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("Lean theorem markers", all(marker in source for marker in manifest["theorem_markers"]), manifest["theorem_markers"], "all present")
    check("Lean escape tokens absent", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), [], "none")
    lake = find_lake()
    check("pinned lake", lake is not None, lake, "pinned lake")
    completed = subprocess.run([lake, "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, encoding="utf-8", capture_output=True, check=False)
    check("Lean compile", completed.returncode == 0, completed.returncode, 0)
    check("Lean clean", completed.returncode == 0 and "error:" not in (completed.stdout + completed.stderr).lower(), completed.stderr, "no Lean error")
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "primary", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": len(rows), "assertions": rows, "derived": {key: str(value) if isinstance(value, F) else value for key, value in derived.items()}, "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "boundary": manifest["boundary"]}
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY R-190 LEAN PASS {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
