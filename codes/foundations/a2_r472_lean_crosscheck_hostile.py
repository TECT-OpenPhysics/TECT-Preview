#!/usr/bin/env python3
"""Hostile mutation lane for the R-472 exact-algebra sidecar.

The mutations exercise the acceptance firewall rather than proposing a new
model.  A sign, denominator, density, charge, Lean marker, or method flag
change must be rejected.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/a2-r472-lean-crosscheck-manifest.json"
DEFAULT_OUTPUT = REPO / (
    "claims/A2-FULL-PRODUCTION-WELLPOSED/runs/"
    "2026-08-31-hostile-r472-a2-lean-crosscheck/hostile.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
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


def accepted(candidate: dict[str, Any], manifest: dict[str, Any], expected: dict[str, str]) -> bool:
    if candidate.get("claim_bearing") is not False or candidate.get("tier") != "T0":
        return False
    if not all(manifest["method_preservation"].values()):
        return False
    if candidate.get("methods_unchanged") is not True:
        return False
    exact = candidate.get("exact")
    return isinstance(exact, dict) and all(exact.get(key) == value for key, value in expected.items())


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads((REPO / manifest["authorities"]["a1_p1_manifest"]["path"]).read_text(encoding="utf-8"))
    p = a1["parameters"]
    y, z, r = (q(p[key]) for key in ("Y", "Z", "r"))
    lam, gamma = q(p["lambda"]), q(p["gamma"])
    shell = r - z * z / (4 * y)
    total = shell + F(7, 250)
    rho = -3 * lam / (4 * gamma)
    gap = total / 2 - 3 * lam * lam / (32 * gamma)
    radial = total - lam * lam / (4 * gamma)
    charge = F(16) ** 3 * rho / 2
    expected = {
        "gap": manifest["exact_targets"]["r157_gap"],
        "radial_gap": manifest["exact_targets"]["r157_radial_gap"],
        "density": manifest["exact_targets"]["r158_coexistence_density"],
        "charge": manifest["exact_targets"]["r158_coexistence_charge"],
    }
    base = {
        "claim_bearing": False,
        "tier": "T0",
        "methods_unchanged": True,
        "exact": {"gap": str(gap), "radial_gap": str(radial), "density": str(rho), "charge": str(charge)},
    }
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected_value: Any) -> None:
        rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": str(actual), "expected": str(expected_value)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected_value!r}")

    check("unmutated candidate accepted", accepted(base, manifest, expected), True, "accept exact T0 sidecar")
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("flip gap sign", lambda item: item["exact"].update(gap="-" + item["exact"]["gap"])),
        ("change gap denominator", lambda item: item["exact"].update(gap=str(gap + F(1, 10**9)))),
        ("change radial denominator", lambda item: item["exact"].update(radial_gap=str(radial + F(1, 10**9)))),
        ("change coexistence density", lambda item: item["exact"].update(density=str(rho + F(1, 100)))),
        ("change coexistence charge", lambda item: item["exact"].update(charge=str(charge + 1))),
        ("claim-bearing promotion", lambda item: item.update(claim_bearing=True)),
        ("tier promotion", lambda item: item.update(tier="T6")),
        ("method change", lambda item: item.update(methods_unchanged=False)),
        ("drop exact field", lambda item: item["exact"].pop("density")),
    ]
    for name, mutate in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        check(name, not accepted(candidate, manifest, expected), accepted(candidate, manifest, expected), False)

    lean_text = (REPO / manifest["files"]["lean_entrypoint"]["path"]).read_text(encoding="utf-8")
    check("Lean marker set is nonempty", all(marker in lean_text for marker in manifest["lean"]["declarations"]), manifest["lean"]["declarations"], "present")
    mutated_lean = lean_text.replace("r157_gap_exact", "r157_gap_theorem_removed", 1)
    check("deleted Lean marker rejected", not all(marker in mutated_lean for marker in manifest["lean"]["declarations"]), True, True)

    payload = {
        "schema": "tect/a2-r472-lean-crosscheck-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["audit_id"] + "-HOSTILE",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "tier": "T0",
        "methods_unchanged": True,
        "mutation_count": len(mutations) + 1,
        "all_mutations_rejected": True,
        "assertion_count": len(rows),
        "passed": len(rows),
        "assertions": rows,
        "scope": manifest["scope"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {"manifest_sha256": digest(MANIFEST)},
    }
    write_json(output if output.is_absolute() else REPO / output, payload)
    print(f"R-472 HOSTILE PASS {len(rows)}/{len(rows)}; mutations={len(mutations) + 1}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
