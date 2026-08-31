#!/usr/bin/env python3
"""Primary exact audit for the additive R-472 Lean sidecar.

R-472 re-derives the exact rational cores already accepted by R-157/R-158 and
checks the small Lean entrypoint.  It does not alter either research lane or
introduce a source-owned dynamics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/a2-r472-lean-crosscheck-manifest.json"
DEFAULT_OUTPUT = REPO / (
    "claims/A2-FULL-PRODUCTION-WELLPOSED/runs/"
    "2026-08-31-primary-r472-a2-lean-crosscheck/primary.json"
)
LEAN_ROOT = REPO / "verification/lean"
FORBIDDEN = ("sorry", "admit", "axiom", "unsafe")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path, *, normalise: bool = False) -> str:
    data = path.read_bytes()
    if normalise:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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


def fraction(value: Any) -> F:
    return F(str(value))


def parse_fraction(value: Any) -> F:
    text = str(value)
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return F(int(numerator), int(denominator))
    return F(text)


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def compile_lean() -> dict[str, Any]:
    registry = json.loads((LEAN_ROOT / "registry.json").read_text(encoding="utf-8"))
    toolchain = registry["toolchain"]["toolchain"]
    encoded = toolchain.replace("/", "--").replace(":", "---")
    executable = Path.home() / ".elan" / "toolchains" / encoded / "bin" / "lake.exe"
    if not executable.is_file():
        return {"status": "FAIL", "returncode": 1, "output": "pinned lake executable missing"}
    process = subprocess.run(
        [str(executable), "env", "lean", "Tect/R472.lean"],
        cwd=LEAN_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
        timeout=180,
    )
    output = (process.stdout + "\n" + process.stderr).strip()
    return {
        "status": "PASS" if process.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": process.returncode,
        "command": "lake env lean Tect/R472.lean",
        "output": output[-2000:],
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads((REPO / manifest["authorities"]["a1_p1_manifest"]["path"]).read_text(encoding="utf-8"))
    r157 = json.loads((REPO / manifest["authorities"]["r157_manifest"]["path"]).read_text(encoding="utf-8"))
    r158 = json.loads((REPO / manifest["authorities"]["r158_manifest"]["path"]).read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", (manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]) == ("R-472", "EXP-001347", False), [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], ["R-472", "EXP-001347", False])
    check("tier", manifest["tier"] == "T0", manifest["tier"], "T0")
    check("method preservation", all(manifest["method_preservation"].values()), manifest["method_preservation"], "all true")

    for name, authority in manifest["authorities"].items():
        path = REPO / authority["path"]
        check(f"authority hash {name}", path.is_file() and digest(path) == authority["sha256"], digest(path) if path.is_file() else "MISSING", authority["sha256"])

    lean_path = REPO / manifest["files"]["lean_entrypoint"]["path"]
    lean_text = lean_path.read_text(encoding="utf-8")
    check("Lean source hash", digest(lean_path, normalise=True) == manifest["files"]["lean_entrypoint"]["sha256"], digest(lean_path, normalise=True), manifest["files"]["lean_entrypoint"]["sha256"])
    check("Lean declarations", all(item in lean_text for item in manifest["lean"]["declarations"]), manifest["lean"]["declarations"], "all present")
    check("Lean escape absence", not any(re.search(rf"\b{re.escape(token)}\b", lean_text) for token in FORBIDDEN), FORBIDDEN, "none")
    lean = compile_lean()
    check("Lean compile", lean["status"] == "PASS", lean, "PASS")

    params = a1["parameters"]
    y, z, r = (fraction(params[key]) for key in ("Y", "Z", "r"))
    lam, gamma = (fraction(params[key]) for key in ("lambda", "gamma"))
    shell = r - z * z / (4 * y)
    internal_lower = F(7, 250)
    total_mass = shell + internal_lower
    rho_star = -3 * lam / (4 * gamma)
    gap = total_mass / 2 - 3 * lam * lam / (32 * gamma)
    radial_gap = total_mass - lam * lam / (4 * gamma)
    r157_constants = r157["exact_constants"]
    check("R-157 shell minimum", shell == parse_fraction(r157_constants["shell_minimum"]), shell, r157_constants["shell_minimum"])
    check("R-157 total mass", total_mass == parse_fraction(r157_constants["total_quadratic_mass_lower_bound"]), total_mass, r157_constants["total_quadratic_mass_lower_bound"])
    check("R-157 vertex", rho_star == F(43, 216), rho_star, F(43, 216))
    check("R-157 gap", gap == parse_fraction(manifest["exact_targets"]["r157_gap"]), gap, manifest["exact_targets"]["r157_gap"])
    check("R-157 gap threshold", gap > F(1, 8), gap, ">1/8")
    check("R-157 radial gap", radial_gap == parse_fraction(manifest["exact_targets"]["r157_radial_gap"]), radial_gap, manifest["exact_targets"]["r157_radial_gap"])
    check("R-157 radial threshold", radial_gap > F(1, 4), radial_gap, ">1/4")
    lhs_coefficients = [total_mass / 2, lam / 4, gamma / 6]
    rhs_coefficients = [gap + gamma * rho_star * rho_star / 6, -gamma * rho_star / 3, gamma / 6]
    check("R-157 completion coefficients", lhs_coefficients == rhs_coefficients, lhs_coefficients, rhs_coefficients)
    check("R-157 Class-II input determinant", F(1, 5) * F(3, 20) - F(1, 10) ** 2 == F(1, 50), F(1, 50), F(1, 50))

    matrix = [[F(1, 10), -F(1, 20), -F(1, 20)], [-F(1, 20), F(13, 100), -F(1, 20)], [-F(1, 20), -F(1, 20), F(17, 100)]]
    trace = sum(matrix[i][i] for i in range(3))
    second = sum(matrix[i][i] * matrix[j][j] - matrix[i][j] * matrix[j][i] for i, j in ((0, 1), (0, 2), (1, 2)))
    determinant = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    r158_constants = r158["exact_constants"]
    check("R-158 characteristic coefficients", [trace, second, determinant] == [F(2, 5), F(223, 5000), F(3, 3125)], [trace, second, determinant], [F(2, 5), F(223, 5000), F(3, 3125)])
    check("R-158 characteristic target", manifest["exact_targets"]["r158_characteristic"] == r158_constants["internal_characteristic_polynomial"], manifest["exact_targets"]["r158_characteristic"], r158_constants["internal_characteristic_polynomial"])
    coexistence_drop = 3 * lam * lam / (16 * gamma)
    saddle_drop = lam * lam / (4 * gamma)
    charge = F(16) ** 3 * rho_star / 2
    check("R-158 density", rho_star == parse_fraction(manifest["exact_targets"]["r158_coexistence_density"]), rho_star, manifest["exact_targets"]["r158_coexistence_density"])
    check("R-158 charge", charge == parse_fraction(manifest["exact_targets"]["r158_coexistence_charge"]), charge, manifest["exact_targets"]["r158_coexistence_charge"])
    check("R-158 coexistence drop", coexistence_drop == parse_fraction(manifest["exact_targets"]["r158_coexistence_drop"]), coexistence_drop, manifest["exact_targets"]["r158_coexistence_drop"])
    check("R-158 saddle drop", saddle_drop == parse_fraction(manifest["exact_targets"]["r158_saddle_node_drop"]), saddle_drop, manifest["exact_targets"]["r158_saddle_node_drop"])
    check("R-158 drop ordering", saddle_drop > coexistence_drop > 0, [saddle_drop, coexistence_drop], ">0 and saddle>coexistence")
    check("R-158 stationary densities", [rho_star, rho_star / 3] == [F(43, 216), F(43, 648)], [rho_star, rho_star / 3], [F(43, 216), F(43, 648)])
    numerator_values = [-81 * F(k, 10) ** 2 + 128 * F(k, 10) + 128 for k in range(11)]
    check("R-157 radial numerator grid", min(numerator_values) > 0, min(numerator_values), ">0 on 0..1 grid")
    check("methods unchanged", manifest["formal_integration"]["methods_unchanged"] is True and manifest["formal_integration"]["no_tier_change"] is True, manifest["formal_integration"], "unchanged")

    payload = {
        "schema": "tect/a2-r472-lean-crosscheck-primary/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"] + "-PRIMARY",
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
        "lean": lean,
        "derived": serial({"shell_minimum": shell, "total_mass": total_mass, "rho_star": rho_star, "gap": gap, "radial_gap": radial_gap, "coexistence_drop": coexistence_drop, "saddle_drop": saddle_drop, "charge": charge}),
        "scope": manifest["scope"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "non_claims": manifest["non_claims"],
        "falsifiers": manifest["falsifiers"],
        "evidence_level": manifest["evidence_level"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"manifest_sha256": digest(MANIFEST), "a1_sha256": digest(REPO / manifest["authorities"]["a1_p1_manifest"]["path"]), "r157_sha256": digest(REPO / manifest["authorities"]["r157_manifest"]["path"]), "r158_sha256": digest(REPO / manifest["authorities"]["r158_manifest"]["path"])},
    }
    atomic_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-472 PRIMARY PASS {len(rows)}/{len(rows)}; Lean={lean['status']}; methods unchanged")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
