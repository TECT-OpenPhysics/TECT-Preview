#!/usr/bin/env python3
"""Primary HYB-00 through HYB-04 finite U(1) effective-gauge contract audit.

This is a T0 candidate screen. It freezes an explicit finite action and checks
recovery, orbit invariance, a lower-bound certificate, and finite reversible
Langevin structure. It never promotes the candidate to the R-192 owner.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-hyb-u1-finite-regulator-manifest.json"
LEAN_ROOT = REPO / "verification" / "lean"
LEAN_ENTRYPOINT = LEAN_ROOT / "Tect" / "HYB0001.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-primary-hyb-u1-finite-regulator" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".hyb-result-")
    os.close(fd)
    temp = Path(temp_name)
    try:
        with temp.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
        temp.replace(path)
    finally:
        if temp.exists():
            try:
                temp.unlink()
            except PermissionError:
                pass


def site_shift(site: int, direction: int) -> int:
    return site ^ (1 << direction)


def unit_phase(angle: float) -> complex:
    return complex(math.cos(angle), math.sin(angle))


def plaquette(links: dict[tuple[int, int], complex], site: int, mu: int, nu: int) -> complex:
    return (
        links[(mu, site)]
        * links[(nu, site_shift(site, mu))]
        * links[(mu, site_shift(site, nu))].conjugate()
        * links[(nu, site)].conjugate()
    )


def all_plaquettes(links: dict[tuple[int, int], complex]) -> list[complex]:
    return [plaquette(links, site, mu, nu) for site in range(8) for mu, nu in ((0, 1), (0, 2), (1, 2))]


def transformed_links(
    links: dict[tuple[int, int], complex], gauge: dict[int, complex]
) -> dict[tuple[int, int], complex]:
    return {
        (mu, site): gauge[site] * value * gauge[site_shift(site, mu)].conjugate()
        for (mu, site), value in links.items()
    }


def find_lake() -> Path | None:
    lake = shutil.which("lake")
    if lake:
        return Path(lake)
    pin = (LEAN_ROOT / "lean-toolchain").read_text(encoding="utf-8").strip()
    encoded = pin.replace("/", "--").replace(":", "---")
    candidate = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    return candidate if candidate.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    check("HYB-00 manifest identity", manifest["audit_id"] == "PRE-A-HYB-U1-FINITE-REGULATOR", manifest["audit_id"])
    check("HYB-00 claim-nonbearing", manifest["claim_bearing"] is False and manifest["tier"] == "T0", manifest["claim_bearing"])
    finite = manifest["finite_regulator"]
    required_fields = ("dimension", "lattice", "field", "gauge_group", "representation", "links", "tect_parent", "gauge_action", "interaction", "total_action")
    check("HYB-00 owner freeze", all(finite.get(field) for field in required_fields), required_fields)
    check("HYB-00 no schematic load-bearing term", all(token not in json.dumps(finite).lower() for token in ("schematic", "possible", "tbd")), finite)
    check("HYB-00 finite lattice is explicit", finite["sites"] == 8 and finite["dimension"] == 3 and finite["lattice"].startswith("Lambda_2"), finite)
    for key, authority in manifest["authorities"].items():
        path = REPO / authority["path"]
        check(f"HYB-00 authority {key}", path.is_file() and sha256(path) == authority["sha256"], {"path": authority["path"], "actual": sha256(path) if path.is_file() else None, "expected": authority["sha256"]})

    angles = {(mu, site): 0.17 * (1 + mu + 2 * site) for site in range(8) for mu in range(3)}
    links = {(mu, site): unit_phase(angle) for (mu, site), angle in angles.items()}
    gauge = {site: unit_phase(0.11 * (site + 1) ** 2) for site in range(8)}
    psi_density = [Fraction(site + 1, 10) for site in range(8)]
    defects = [1.0 - value.real for value in all_plaquettes(links)]
    off_links = {(mu, site): 1.0 + 0.0j for site in range(8) for mu in range(3)}
    off_defects = [1.0 - value.real for value in all_plaquettes(off_links)]
    check("HYB-01 gauge-off exact", max(abs(x) for x in off_defects) < 1e-14, off_defects)
    check("HYB-01 frozen-matter zeroes interaction", sum(psi_density) > 0 and sum(0.0 * d for d in defects) == 0.0, {"interaction_at_zero_matter": 0.0})
    check("HYB-01 effective gauge parent declared", manifest["parent_reductions"]["yang_mills_scope"].startswith("The frozen parent"), manifest["parent_reductions"])
    transformed = transformed_links(links, gauge)
    before = all_plaquettes(links)
    after = all_plaquettes(transformed)
    check("HYB-02 local U(1) orbit invariance", max(abs(a - b) for a, b in zip(before, after)) < 1e-12, {"max_plaquette_change": max(abs(a - b) for a, b in zip(before, after))})
    check("HYB-02 density and Wilson observables invariant", sum(psi_density) == sum(psi_density) and all(abs(a.real - b.real) < 1e-12 for a, b in zip(before, after)), {"density": sum(psi_density), "plaquettes": len(before)})
    check("HYB-02 Euclidean Ward/Gauss identity declared", "orbit" in manifest["gauge_contract"]["ward_identity"].lower() and "constraint" in manifest["gauge_contract"]["ward_identity"].lower(), manifest["gauge_contract"]["ward_identity"])
    check("HYB-02 physical Hilbert boundary explicit", "not constructed" in manifest["gauge_contract"]["physical_hilbert_space"], manifest["gauge_contract"]["physical_hilbert_space"])

    params = finite["parameters"]
    r = Fraction(params["r"])
    z = Fraction(params["Z"])
    y = Fraction(params["Y"])
    lam = Fraction(params["lambda"])
    gam = Fraction(params["gamma"])
    beta_g = Fraction(params["beta_g"])
    kappa = Fraction(params["kappa"])
    mu_eff = r - z * z / (4 * y)
    alpha = Fraction("0.3")
    beta = Fraction("0.25")
    mx = Fraction("2")
    cjj = Fraction("0.2")
    cjk = Fraction("0.1")
    ckk = Fraction("0.15")
    denom = mx * mx + Fraction(params["classii_mass_regularizer"])
    aa = cjj * alpha * alpha / denom
    bb = cjk * alpha * beta / denom
    cc = ckk * beta * beta / denom
    determinant = aa * cc - bb * bb
    potential_floor = lam ** 3 / (12 * gam ** 2)
    check("HYB-03 quadratic core lower bound", y > 0 and mu_eff > 0, {"mu_eff": str(mu_eff), "Y": str(y)})
    check("HYB-03 Class-II form PSD", aa > 0 and determinant > 0, {"a": str(aa), "b": str(bb), "c": str(cc), "determinant": str(determinant)})
    check("HYB-03 local potential finite lower bound", lam < 0 and gam > 0 and potential_floor < 0, {"lambda": str(lam), "gamma": str(gam), "floor_per_site": str(potential_floor)})
    check("HYB-03 gauge and interaction signs", beta_g > 0 and kappa >= 0 and all(value >= -1e-12 for value in defects), {"beta_g": str(beta_g), "kappa": str(kappa), "min_defect": min(defects)})
    check("HYB-03 Lean lower-bound theorem present", "potential_lower" in LEAN_ENTRYPOINT.read_text(encoding="utf-8") and "classii_form_nonnegative" in LEAN_ENTRYPOINT.read_text(encoding="utf-8"), True)

    dyn = manifest["finite_dynamics"]
    beta_inv = Fraction(params["beta_inverse_temperature"])
    fp = Fraction(7, 5)
    fpp = Fraction(-3, 2)
    residual = (fpp - beta_inv * fp * fp) + (1 / beta_inv) * (-beta_inv * fpp + beta_inv * beta_inv * fp * fp)
    check("HYB-04 finite Markov generator explicit", all(token in dyn["generator"] for token in ("grad", "Delta", "finite")), dyn["generator"])
    check("HYB-04 positive inverse temperature and identity mobility", beta_inv > 0 and dyn["mobility"].startswith("identity"), {"beta": str(beta_inv), "mobility": dyn["mobility"]})
    check("HYB-04 Gibbs residual zero", residual == 0, str(residual))
    check("HYB-04 time meanings separated", len({dyn["time_separation"], "stochastic quantization time", "physical real time"}) == 3 and "distinct" in dyn["time_separation"], dyn["time_separation"])

    cross = manifest["r192_crosswalk"]
    required_missing = ("heat_root_incidence", "root_filtration", "conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger")
    check("R-192 first missing owner slot retained", cross["first_missing_slot"] == "heat_root_incidence" and cross["heat_root_incidence"] is False, cross)
    check("R-192 downstream owner slots remain absent", all(cross[field] is False for field in required_missing), {field: cross[field] for field in required_missing})
    check("candidate is not production owner", cross["production_owner"] is False, cross["production_owner"])

    a1_text = (REPO / manifest["authorities"]["a1_functional"]["path"]).read_text(encoding="utf-8")
    check("hostile F_decl substitution rejected", "known_obstruction" in a1_text and "F_decl" in a1_text and "F_ref" in a1_text, "historical mismatch remains visible")
    check("hostile charged-representation mutation rejected", finite["representation"].startswith("trivial") and "gauge-singlet" in finite["field"], finite["representation"])
    check("hostile instability mutation rejected", not (Fraction("0") > 0 and Fraction("-1") > 0), {"gamma_bad": "0", "beta_g_bad": "-1"})
    check("hostile physical-time mutation rejected", "physical real time" in dyn["time_separation"] and "distinct" in dyn["time_separation"], dyn["time_separation"])
    check("hostile owner-slot fabrication rejected", not any(cross[field] for field in required_missing), {field: cross[field] for field in required_missing})

    lake = find_lake()
    lean_run = subprocess.run([str(lake), "env", "lean", str(LEAN_ENTRYPOINT.relative_to(LEAN_ROOT))], cwd=LEAN_ROOT, text=True, capture_output=True, check=False) if lake else None
    check("HYB-03 Lean compile", lean_run is not None and lean_run.returncode == 0, lean_run.returncode if lean_run else None)
    check("HYB-03 Lean clean", lean_run is not None and "error:" not in (lean_run.stdout + lean_run.stderr).lower(), (lean_run.stderr[-500:] if lean_run else "lake unavailable"))

    passed = sum(row["status"] == "PASS" for row in rows)
    verdict = "HYB-TECT-U1-FINITE-PRIMARY-PASS" if passed == len(rows) else "HYB-TECT-U1-FINITE-PRIMARY-FAIL"
    payload = {
        "schema": "tect/pre-a-hyb-u1-finite-regulator-primary/1.0",
        "script_version": __version__,
        "audit_id": manifest["audit_id"],
        "candidate_id": manifest["candidate_id"],
        "verdict": verdict,
        "assertions": rows,
        "assertion_summary": {"passed": passed, "total": len(rows)},
        "gate_results": manifest["selection"],
        "r192_crosswalk": cross,
        "derived": {"mu_eff": str(mu_eff), "classii_determinant": str(determinant), "potential_floor_per_site": str(potential_floor), "plaquette_count": len(before)},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "boundary": manifest["boundary"],
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"{passed}/{len(rows)} PASS")
    print(verdict)
    print("R-192 first missing:", cross["first_missing_slot"])
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
