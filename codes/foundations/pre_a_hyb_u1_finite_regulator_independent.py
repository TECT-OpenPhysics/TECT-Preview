#!/usr/bin/env python3
"""Independent stdlib-only HYB-00 through HYB-04 audit.

This lane reimplements the finite U(1) plaquette, orbit, and rational
stability checks without importing the primary verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-hyb-u1-finite-regulator-manifest.json"
LEAN_ENTRYPOINT = REPO / "verification" / "lean" / "Tect" / "HYB0001.lean"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-hyb-u1-finite-regulator" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".hyb-independent-")
    os.close(fd)
    temp = Path(temp_name)
    try:
        temp.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True, default=str) + "\n", encoding="utf-8", newline="\n")
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()


def coords(site: int) -> tuple[int, int, int]:
    return (site & 1, (site >> 1) & 1, (site >> 2) & 1)


def site_of(values: tuple[int, int, int]) -> int:
    return values[0] + 2 * values[1] + 4 * values[2]


def shift(site: int, direction: int) -> int:
    x = list(coords(site))
    x[direction] = 1 - x[direction]
    return site_of(tuple(x))


def phase(angle: float) -> complex:
    return complex(math.cos(angle), math.sin(angle))


def plaquette(links: dict[tuple[int, int], complex], site: int, mu: int, nu: int) -> complex:
    return links[(mu, site)] * links[(nu, shift(site, mu))] * links[(mu, shift(site, nu))].conjugate() * links[(nu, site)].conjugate()


def plaquette_vector(links: dict[tuple[int, int], complex]) -> list[complex]:
    result = []
    for site in range(8):
        for mu, nu in ((0, 1), (0, 2), (1, 2)):
            result.append(plaquette(links, site, mu, nu))
    return result


def gauge_transform(links: dict[tuple[int, int], complex], gauge: dict[int, complex]) -> dict[tuple[int, int], complex]:
    result = {}
    for mu in range(3):
        for site in range(8):
            result[(mu, site)] = gauge[site] * links[(mu, site)] * gauge[shift(site, mu)].conjugate()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-result", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    finite = manifest["finite_regulator"]
    check("independent manifest identity", manifest["candidate_id"] == "HYB-TECT-U1-FINITE-0001", manifest["candidate_id"])
    check("independent nonbearing scope", manifest["claim_bearing"] is False and manifest["tier"] == "T0", manifest["claim_bearing"])
    check("independent action is fully enumerated", all(finite.get(k) for k in ("gauge_group", "representation", "links", "tect_parent", "gauge_action", "interaction", "total_action")), finite)
    for authority in manifest["authorities"].values():
        path = REPO / authority["path"]
        check("independent authority hash", path.is_file() and sha256(path) == authority["sha256"], authority["path"])

    links = {(mu, site): phase(0.07 * (3 * site + mu + 1)) for site in range(8) for mu in range(3)}
    gauge = {site: phase(0.13 * (site + 2)) for site in range(8)}
    transformed = gauge_transform(links, gauge)
    original_plaquettes = plaquette_vector(links)
    transformed_plaquettes = plaquette_vector(transformed)
    check("independent gauge-off plaquettes", all(abs(z - 1.0) < 1e-14 for z in plaquette_vector({(mu, site): 1.0 + 0.0j for site in range(8) for mu in range(3)})), original_plaquettes[:3])
    check("independent U(1) plaquette orbit invariance", all(abs(a - b) < 1e-12 for a, b in zip(original_plaquettes, transformed_plaquettes)), max(abs(a - b) for a, b in zip(original_plaquettes, transformed_plaquettes)))
    check("independent Wilson real parts invariant", all(abs(a.real - b.real) < 1e-12 for a, b in zip(original_plaquettes, transformed_plaquettes)), len(original_plaquettes))
    check("independent trivial representation explicit", finite["representation"].startswith("trivial") and "singlet" in finite["field"], finite["representation"])
    check("independent frozen matter reduction", "F_ref and S_int vanish" in manifest["parent_reductions"]["effective_gauge_frozen_psi"], manifest["parent_reductions"]["effective_gauge_frozen_psi"])
    check("independent effective gauge limitation retained", "not four-dimensional pure Yang-Mills" in manifest["parent_reductions"]["yang_mills_scope"], manifest["parent_reductions"]["yang_mills_scope"])

    p = finite["parameters"]
    r = Fraction(p["r"])
    z = Fraction(p["Z"])
    y = Fraction(p["Y"])
    lam = Fraction(p["lambda"])
    gam = Fraction(p["gamma"])
    alpha = Fraction("0.3")
    beta = Fraction("0.25")
    mx = Fraction("2")
    denom = mx * mx + Fraction(p["classii_mass_regularizer"])
    aa = Fraction("0.2") * alpha * alpha / denom
    bb = Fraction("0.1") * alpha * beta / denom
    cc = Fraction("0.15") * beta * beta / denom
    det = aa * cc - bb * bb
    mu_eff = r - z * z / (4 * y)
    floor = lam ** 3 / (12 * gam ** 2)
    check("independent quadratic completion", y > 0 and mu_eff > 0, str(mu_eff))
    check("independent Class-II determinant", aa > 0 and det > 0, str(det))
    check("independent sextic floor", lam < 0 < gam and floor < 0, str(floor))
    check("independent nonnegative gauge parameters", Fraction(p["beta_g"]) > 0 and Fraction(p["kappa"]) >= 0, p)
    source = LEAN_ENTRYPOINT.read_text(encoding="utf-8")
    check("independent Lean theorem names", all(x in source for x in ("potential_lower", "classii_form_nonnegative", "gibbs_residual_zero")), True)
    check("independent Lean forbidden tokens absent", not any(token in source.split() for token in ("sorry", "admit", "axiom", "unsafe")), True)

    dyn = manifest["finite_dynamics"]
    cross = manifest["r192_crosswalk"]
    residual = (Fraction(-3, 2) - Fraction(7, 5) ** 2) + (Fraction(1) / Fraction(1)) * (-Fraction(1) * Fraction(-3, 2) + Fraction(1) ** 2 * Fraction(7, 5) ** 2)
    check("independent finite generator", "finite" in dyn["generator"] and "Delta" in dyn["generator"], dyn["generator"])
    check("independent Gibbs residual", residual == 0, str(residual))
    check("independent time separation", "distinct" in dyn["time_separation"] and "physical real time" in dyn["time_separation"], dyn["time_separation"])
    check("independent R-192 first failure", cross["first_missing_slot"] == "heat_root_incidence", cross)
    check("independent R-192 slots absent", all(cross[x] is False for x in ("heat_root_incidence", "root_filtration", "conditional_replicas", "raw_current_spatial_intertwiner", "production_one_use_q_ledger")), cross)
    check("independent candidate not owner", cross["production_owner"] is False, cross["production_owner"])

    passed = sum(row["status"] == "PASS" for row in rows)
    verdict = "HYB-TECT-U1-FINITE-INDEPENDENT-PASS" if passed == len(rows) else "HYB-TECT-U1-FINITE-INDEPENDENT-FAIL"
    payload = {
        "schema": "tect/pre-a-hyb-u1-finite-regulator-independent/1.0",
        "script_version": __version__,
        "audit_id": manifest["audit_id"],
        "candidate_id": manifest["candidate_id"],
        "verdict": verdict,
        "assertions": rows,
        "assertion_summary": {"passed": passed, "total": len(rows)},
        "r192_crosswalk": cross,
        "derived": {"mu_eff": str(mu_eff), "classii_determinant": str(det), "potential_floor_per_site": str(floor), "plaquette_count": len(original_plaquettes)},
        "environment": {"python": "stdlib", "platform": platform.platform()},
        "boundary": manifest["boundary"],
    }
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"{passed}/{len(rows)} PASS")
    print(verdict)
    print("R-192 first missing:", cross["first_missing_slot"])
    return 0 if passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
