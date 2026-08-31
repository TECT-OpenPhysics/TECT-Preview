#!/usr/bin/env python3
"""Non-importing Fraction audit of the R-472 exact algebra.

The independent lane reconstructs the constants from the A1 parameter file
without importing the primary lane or reading its output.  Lean compilation is
left to the integrated lane; this separation keeps the arithmetic check
independent.
"""

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
MANIFEST = REPO / "strategy/a2-r472-lean-crosscheck-manifest.json"
DEFAULT_OUTPUT = REPO / (
    "claims/A2-FULL-PRODUCTION-WELLPOSED/runs/"
    "2026-08-31-independent-r472-a2-lean-crosscheck/independent.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def q(value: Any) -> F:
    return F(str(value))


def oracle(text: Any) -> F:
    value = str(text)
    if "/" in value:
        n, d = value.split("/", 1)
        return F(int(n), int(d))
    return F(value)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1_path = REPO / manifest["authorities"]["a1_p1_manifest"]["path"]
    r157_path = REPO / manifest["authorities"]["r157_manifest"]["path"]
    r158_path = REPO / manifest["authorities"]["r158_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    r157 = json.loads(r157_path.read_text(encoding="utf-8"))
    r158 = json.loads(r158_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": str(actual), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]] == ["R-472", "EXP-001347", False], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], ["R-472", "EXP-001347", False])
    check("T0 sidecar", manifest["tier"] == "T0" and manifest["formal_integration"]["no_tier_change"], manifest["tier"], "T0/no tier change")
    check("method preservation", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true")
    for name, authority in manifest["authorities"].items():
        path = REPO / authority["path"]
        check(f"authority {name}", path.is_file() and digest(path) == authority["sha256"], digest(path) if path.is_file() else "MISSING", authority["sha256"])

    p = a1["parameters"]
    y, z, r = (q(p[key]) for key in ("Y", "Z", "r"))
    lam, gamma = q(p["lambda"]), q(p["gamma"])
    shell = r - z * z / (4 * y)
    total_mass = shell + F(7, 250)
    rho_star = -3 * lam / (4 * gamma)
    gap = total_mass / 2 - 3 * lam * lam / (32 * gamma)
    radial_gap = total_mass - lam * lam / (4 * gamma)
    check("eta shell zero", q(p["eta_shell"]) == 0, p["eta_shell"], 0)
    check("shell completion", y * (-z / (2 * y)) ** 2 + shell == r, shell, "r-z^2/(4Y)")
    check("R-157 shell oracle", str(shell) == r157["exact_constants"]["shell_minimum"], shell, r157["exact_constants"]["shell_minimum"])
    check("R-157 total oracle", str(total_mass) == r157["exact_constants"]["total_quadratic_mass_lower_bound"], total_mass, r157["exact_constants"]["total_quadratic_mass_lower_bound"])
    check("R-157 gap oracle", str(gap) == manifest["exact_targets"]["r157_gap"] and gap > F(1, 8), gap, ">1/8 and target")
    check("R-157 radial oracle", str(radial_gap) == manifest["exact_targets"]["r157_radial_gap"] and radial_gap > F(1, 4), radial_gap, ">1/4 and target")
    check("completion coefficient match", [total_mass / 2, lam / 4, gamma / 6] == [gap + gamma * rho_star * rho_star / 6, -gamma * rho_star / 3, gamma / 6], rho_star, "coefficient vectors equal")

    matrix = [[F(1, 10), -F(1, 20), -F(1, 20)], [-F(1, 20), F(13, 100), -F(1, 20)], [-F(1, 20), -F(1, 20), F(17, 100)]]
    trace = sum(matrix[i][i] for i in range(3))
    second = matrix[0][0] * matrix[1][1] - matrix[0][1] ** 2 + matrix[0][0] * matrix[2][2] - matrix[0][2] ** 2 + matrix[1][1] * matrix[2][2] - matrix[1][2] ** 2
    determinant = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] ** 2) - matrix[0][1] * (matrix[0][1] * matrix[2][2] - matrix[1][2] * matrix[0][2]) + matrix[0][2] * (matrix[0][1] * matrix[1][2] - matrix[1][1] * matrix[0][2])
    check("R-158 characteristic coefficients", [trace, second, determinant] == [F(2, 5), F(223, 5000), F(3, 3125)], [trace, second, determinant], [F(2, 5), F(223, 5000), F(3, 3125)])
    coexistence_drop = 3 * lam * lam / (16 * gamma)
    saddle_drop = lam * lam / (4 * gamma)
    charge = F(16) ** 3 * rho_star / 2
    check("R-158 density oracle", str(rho_star) == manifest["exact_targets"]["r158_coexistence_density"], rho_star, manifest["exact_targets"]["r158_coexistence_density"])
    check("R-158 charge oracle", str(charge) == manifest["exact_targets"]["r158_coexistence_charge"], charge, manifest["exact_targets"]["r158_coexistence_charge"])
    check("R-158 coexistence oracle", str(coexistence_drop) == manifest["exact_targets"]["r158_coexistence_drop"], coexistence_drop, manifest["exact_targets"]["r158_coexistence_drop"])
    check("R-158 saddle oracle", str(saddle_drop) == manifest["exact_targets"]["r158_saddle_node_drop"], saddle_drop, manifest["exact_targets"]["r158_saddle_node_drop"])
    check("R-158 density pair", [str(rho_star), str(rho_star / 3)] == r158["exact_constants"]["coexistence_stationary_densities"], [rho_star, rho_star / 3], r158["exact_constants"]["coexistence_stationary_densities"])
    check("R-158 first-order ordering", saddle_drop > coexistence_drop > 0, [saddle_drop, coexistence_drop], "saddle>coexistence>0")
    check("radial numerator endpoints", all(-81 * F(k) ** 2 + 128 * F(k) + 128 > 0 for k in (0, 1)), [128, 175], ">0")

    payload = {
        "schema": "tect/a2-r472-lean-crosscheck-independent/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"] + "-INDEPENDENT",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "tier": "T0",
        "methods_unchanged": True,
        "assertion_count": len(rows),
        "passed": len(rows),
        "assertions": rows,
        "derived": {"shell_minimum": str(shell), "total_mass": str(total_mass), "rho_star": str(rho_star), "gap": str(gap), "radial_gap": str(radial_gap), "coexistence_drop": str(coexistence_drop), "saddle_drop": str(saddle_drop), "charge": str(charge)},
        "scope": manifest["scope"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "falsifiers": manifest["falsifiers"],
        "evidence_level": manifest["evidence_level"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"manifest_sha256": digest(MANIFEST), "a1_sha256": digest(a1_path), "r157_sha256": digest(r157_path), "r158_sha256": digest(r158_path)},
    }
    atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-472 INDEPENDENT PASS {len(rows)}/{len(rows)}; methods unchanged")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
