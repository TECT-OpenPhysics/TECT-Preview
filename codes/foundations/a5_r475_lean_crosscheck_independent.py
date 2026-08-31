#!/usr/bin/env python3
"""Non-importing independent audit for the A5 R-475 Lean sidecar."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "claims" / "A5-SECTOR-A-SYNTHESIS" / "conditional_composition_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A5-SECTOR-A-SYNTHESIS" / "runs" / "2026-09-01-a5-r475-lean-crosscheck" / "independent.json"

# Test oracles for the frozen contract; source-derived values are recomputed.
EXPECTED_HYPOTHESES = [
    "A5-H1-CANONICAL-KERNEL-MANIFEST",
    "A1-KERNEL-CONV",
    "A1-SHELL-POSITIVITY",
    "A2-H2-SEXTIC-COERCIVITY",
    "A2-H3-CANONICAL-PRODUCTION-FUNCTIONAL",
    "A3-H1-DIM3-Q4-KERNEL",
    "A3-H2-IR-POSITIVITY",
]
EXPECTED_FULL = [
    "A1-PRODUCTION-FUNCTIONAL-REALISATION",
    "A2-FULL-PRODUCTION-WELLPOSED",
    "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
]
EXPECTED_SCALAR = [
    "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
    "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
]
ALIASES = (
    ("claims/a1k", "claims/A1-PRODUCTION-KERNEL-MANIFEST"),
    ("claims/a1f", "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION"),
    ("claims/a2", "claims/A2-FULL-PRODUCTION-WELLPOSED"),
    ("claims/a3f", "claims/A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"),
    ("claims/a3p", "claims/A3-PERTURBATIVE-CONTINUUM-CORRELATORS"),
    ("claims/a4", "claims/A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"),
    ("claims/a5", "claims/A5-SECTOR-A-SYNTHESIS"),
)


def resolve(value: str) -> Path:
    for alias, canonical in sorted(ALIASES, key=lambda row: -len(row[0])):
        if value == alias or value.startswith(alias + "/"):
            return REPO / (canonical + value[len(alias) :])
    return REPO / value


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["theorem_contract"]
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        checks.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})

    check(
        "manifest_identity",
        manifest.get("schema") == "tect/a5-t6-conditional-composition/1.1"
        and manifest.get("claim_id") == "A5-SECTOR-A-SYNTHESIS"
        and manifest.get("candidate_tier") == "T6"
        and manifest.get("publication_state") == "T6-PUBLISHED-OPERATOR-CONFIRMED",
        {k: manifest.get(k) for k in ("schema", "claim_id", "candidate_tier", "publication_state")},
        "frozen operator-confirmed A5 T6 identity",
    )
    actual_digest = digest(contract)
    check("theorem_digest", actual_digest == manifest.get("theorem_contract_sha256"), actual_digest, manifest.get("theorem_contract_sha256"))

    authority = manifest["authority"]
    rows = [{"id": key, "path": value["path"], "actual": file_hash(resolve(value["path"])), "expected": value["sha256"]} for key, value in authority.items()]
    check("authority_hashes", bool(rows) and all(row["actual"] == row["expected"] for row in rows), rows, "all source/PDF/audit hashes match")

    hypotheses = contract["named_hypotheses"]
    gate_text = (REPO / "claims" / "GATES.md").read_text(encoding="utf-8")
    registered = all(f"### **{name}**" in gate_text for name in hypotheses)
    check("hypothesis_order_and_registration", hypotheses == EXPECTED_HYPOTHESES and len(hypotheses) == len(set(hypotheses)) and registered, hypotheses, EXPECTED_HYPOTHESES)

    tiers = {row["id"]: row["tier"] for row in contract["premises"]}
    lifts = contract["sub_t6_dependency_lifts"]
    non_t6 = {key for key, value in tiers.items() if value != "T6"}
    check(
        "premise_tier_partition",
        len(tiers) == 6
        and {key for key, value in tiers.items() if value == "T6"}
        == {
            "A2-FULL-PRODUCTION-WELLPOSED",
            "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM",
            "A3-PERTURBATIVE-CONTINUUM-CORRELATORS",
            "A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE",
        }
        and non_t6 == set(lifts)
        and all(tiers[key] == "T5" for key in non_t6),
        tiers,
        "six premises with four T6 rows and two lifted T5 rows",
    )

    full = contract["branches"]["full_production"]["claim_chain"]
    scalar = contract["branches"]["scalar_continuum"]["claim_conjunction"]
    check("branch_topology", full == EXPECTED_FULL and scalar == EXPECTED_SCALAR and not set(full) & set(scalar), {"full": full, "scalar": scalar}, {"full": EXPECTED_FULL, "scalar": EXPECTED_SCALAR})

    kernel = json.loads(resolve(manifest["numeric_firewall"]["scalar_source"]).read_text(encoding="utf-8"))
    functional = json.loads(resolve(manifest["numeric_firewall"]["full_source"]).read_text(encoding="utf-8"))
    scalar_mass = Decimal(str(kernel["mu2_shell"]))
    p = functional["parameters"]
    full_mass = Decimal(str(p["r"])) - Decimal(str(p["Z"])) ** 2 / (Decimal(4) * Decimal(str(p["Y"])))
    fw = manifest["numeric_firewall"]
    difference = abs(full_mass - scalar_mass)
    check(
        "mass_fork_rederived",
        scalar_mass == Decimal(fw["expected_scalar_shell_mass_squared"])
        and abs(full_mass - Decimal(fw["expected_full_shell_mass_squared"])) < Decimal(fw["full_mass_match_tolerance"])
        and difference > Decimal(fw["required_absolute_difference_gt"]),
        {"scalar": str(scalar_mass), "full": str(full_mass), "difference": str(difference)},
        "source-derived values and declared separation threshold",
    )

    exclusions = " | ".join(contract["exclusions"]).lower()
    required = ["parameter-identical", "derivative class-ii", "eta_shell", "t=0", "historical", "route-b", "unsmeared", "infinite-volume", "phase transition", "bcc", "sector-b", "t7"]
    check("non_claim_boundary", all(token in exclusions for token in required), {"missing": [token for token in required if token not in exclusions]}, "all declared exclusion tokens")

    weaknesses = manifest["sector_a_weakness_map"]
    ids = [row["id"] for row in weaknesses]
    check("weakness_map", len(ids) == len(set(ids)) and "FULL-CLASSII-CONSTRUCTIVE-MEASURE" in ids and "BCC-EXISTENCE-AND-SELECTION" in ids, {"count": len(ids), "ids": ids}, "unique map with required open rows")

    passed = sum(row["status"] == "PASS" for row in checks)
    output = {
        "schema": "tect/a5-r475-lean-crosscheck-independent/1.0",
        "claim_id": "A5-SECTOR-A-SYNTHESIS",
        "result_id": "R-475",
        "exploration_id": "EXP-001354",
        "script_version": __version__,
        "verdict": "R475-A5-CONTRACT-INDEPENDENT-PASS" if passed == len(checks) else "R475-A5-CONTRACT-INDEPENDENT-FAIL",
        "theorem_contract_sha256": actual_digest,
        "branches": {"full_production": full, "scalar_continuum": scalar},
        "mass_fork": {"scalar_shell_mass_squared": str(scalar_mass), "full_shell_mass_squared": str(full_mass), "absolute_difference": str(difference)},
        "checks": checks,
        "assertion_summary": {"passed": passed, "total": len(checks)},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "evidence_level": "T0 non-importing exact contract cross-check; no analytic or physical promotion",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"R-475 INDEPENDENT: {output['verdict']} ({passed}/{len(checks)} assertions)")
    print("Contract:", actual_digest)
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
