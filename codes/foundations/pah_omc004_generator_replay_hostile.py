#!/usr/bin/env python3
"""Hostile mutations for the PAH-OMC-004 generator replay sidecar."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
PARENT = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
SIDECAR = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-004-generator-replay-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-03-pah-omc004-generator-replay/hostile.json"
)

AUDIT_ID = "PAH-GENERATOR-REPLAY-001"
EXPLORATION_ID = "EXP-001371"
RESULT_ID = "R-484"
TASK_ID = "T-054"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def baseline_validator(sidecar: dict[str, Any], manifest: dict[str, Any], source_hash: str, parent_hash: str, sidecar_hash: str) -> bool:
    exact = sidecar.get("exact_scope", {})
    target = sidecar.get("compatibility_target", {})
    provenance = sidecar.get("provenance", {})
    return (
        sidecar.get("contract_id") == "PAH-OMC-004-GEN-001"
        and sidecar.get("parent", {}).get("sha256") == parent_hash
        and sidecar.get("parent", {}).get("path") == "strategy/pa-hyp/PAH-OMC-004-v1.json"
        and manifest.get("sidecar", {}).get("sha256") == sidecar_hash
        and manifest.get("parent", {}).get("sha256") == parent_hash
        and source_hash == "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37"
        and exact.get("levels") == [1, 2]
        and "d_0" in exact.get("anchor_patch", "")
        and "two split faces" in exact.get("anchor_patch", "")
        and "unchanged pah" in exact.get("generator", "").lower()
        and "exp(-beta DeltaF/2)" in exact.get("generator", "")
        and "counterterm" not in exact.get("generator", "").lower()
        and "fitting" not in exact.get("generator", "").lower()
        and exact.get("state", "").startswith("All four patch apertures")
        and "Q=0" in exact.get("state", "")
        and "Q=1" not in exact.get("state", "")
        and exact.get("projection", "").startswith("The one-step projection retains the patch variables")
        and "average" not in exact.get("projection", "").lower()
        and exact.get("normalization", "").startswith("The unchanged finite counting-measure")
        and target.get("exact_row_identity", "").startswith("The exact tuple")
        and provenance.get("physical_authority") is False
        and provenance.get("external_source") is False
        and sidecar.get("lean_entrypoint") == "verification/lean/Tect/R484.lean"
        and len(sidecar.get("non_claims", [])) == 3
        and any("physical" in item.lower() for item in sidecar.get("non_claims", []))
        and any("continuum" in item.lower() for item in sidecar.get("non_claims", []))
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    source = load(SOURCE)
    parent = load(PARENT)
    sidecar = load(SIDECAR)
    manifest = load(MANIFEST)
    source_hash = sha(SOURCE)
    parent_hash = sha(PARENT)
    sidecar_hash = sha(SIDECAR)
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: Any = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("baseline-packet-accepted", baseline_validator(sidecar, manifest, source_hash, parent_hash, sidecar_hash))
    check("parent-identity", parent.get("contract_id") == "PAH-OMC-004" and source.get("packet_id") == "PAH-001")

    Mutation = tuple[str, Callable[[dict[str, Any], dict[str, Any]], None]]
    mutations: list[Mutation] = [
        ("parent-hash-drift", lambda s, m: s["parent"].update(sha256="0" * 64)),
        ("sidecar-contract-drift", lambda s, m: s.update(contract_id="PAH-OMC-004-GEN-002")),
        ("manifest-sidecar-drift", lambda s, m: m["sidecar"].update(sha256="f" * 64)),
        ("manifest-parent-drift", lambda s, m: m["parent"].update(sha256="f" * 64)),
        ("source-hash-drift-oracle", lambda s, m: s["parent"].update(path="strategy/pa-hyp/PAH-001-v2.json")),
        ("remove-diagonal", lambda s, m: s["exact_scope"].update(anchor_patch="a,b,c,d with edges h00,v0,h01,v1 and two faces")),
        ("color-only-substitution", lambda s, m: s["exact_scope"].update(anchor_patch="same square with a color label only")),
        ("new-counterterm", lambda s, m: s["exact_scope"].update(generator="unchanged PAH plus a counterterm exp(-beta DeltaF/2)")),
        ("rate-fitting", lambda s, m: s["exact_scope"].update(generator="fit the rate to equality after projection")),
        ("wrong-levels", lambda s, m: s["exact_scope"].update(levels=[1, 3])),
        ("wrong-projection", lambda s, m: s["exact_scope"].update(projection="average remote variables conditionally")),
        ("wrong-normalization", lambda s, m: s["exact_scope"].update(normalization="conditional Gibbs average")),
        ("nonzero-q", lambda s, m: s["exact_scope"].update(state="All four patch apertures and matter states with Q=1")),
        ("physical-promotion", lambda s, m: s["provenance"].update(physical_authority=True)),
        ("lean-path-drift", lambda s, m: s.update(lean_entrypoint="verification/lean/Tect/R483.lean")),
        ("drop-nonclaims", lambda s, m: s.update(non_claims=["generator equality proves the physical continuum"])),
    ]
    mutation_rows: list[dict[str, Any]] = []
    for name, mutate in mutations:
        candidate_sidecar = copy.deepcopy(sidecar)
        candidate_manifest = copy.deepcopy(manifest)
        mutate(candidate_sidecar, candidate_manifest)
        accepted = baseline_validator(candidate_sidecar, candidate_manifest, source_hash, parent_hash, sidecar_hash)
        mutation_rows.append({"name": name, "accepted_by_baseline": accepted, "rejected": not accepted})
    rejected = sum(1 for row in mutation_rows if row["rejected"])
    check("all-hostile-mutations-rejected", rejected == len(mutations), {"rejected": rejected, "attempted": len(mutations)})

    failed = [item for item in checks if not item["passed"]]
    payload: dict[str, Any] = {
        "schema": "tect/pah-omc004-generator-replay-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": AUDIT_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "task_id": TASK_ID,
        "verification": "PASS" if not failed else "FAIL",
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "source_hashes": {"PAH-001": source_hash, "PAH-OMC-004": parent_hash, "PAH-OMC-004-GEN-001": sidecar_hash, "PAH-OMC-004-GEN-MANIFEST": sha(MANIFEST)},
        "mutations_attempted": len(mutations),
        "mutations_rejected": rejected,
        "all_mutations_rejected": rejected == len(mutations),
        "mutations": mutation_rows,
        "verdict": "EXPLICIT_LOCAL_GENERATOR_ROW_EQUALITY",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "claim_bearing": False,
        "scientific_transition": False,
        "physical_progress": False,
        "non_claims": sidecar.get("non_claims", []),
        "next_question": sidecar.get("single_next_question"),
    }
    atomic_json(output, payload)
    print(f"{AUDIT_ID} HOSTILE {payload['verification']} {payload['passed']}/{payload['assertion_count']}; mutations={rejected}/{len(mutations)} rejected")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
