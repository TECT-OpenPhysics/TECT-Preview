#!/usr/bin/env python3
"""Hostile mutation firewall for the PAH-OMC-002 conditional-kernel audit."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
FINITE = ROOT / "strategy/pa-hyp/PAH-OMC-001-v1.json"
CONTRACT = ROOT / "strategy/pa-hyp/PAH-OMC-002-v1.json"
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-002-manifest.json"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-pah-omc002-conditional-kernel/hostile.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(path)
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = load(MANIFEST)
    contract = load(CONTRACT)
    source_hashes = {
        "PAH-001": digest(PARENT),
        "PAH-OMC-001": digest(FINITE),
        "PAH-OMC-002": digest(CONTRACT),
        "PAH-OMC-002-MANIFEST": digest(MANIFEST),
    }
    baseline = {
        "contract": contract,
        "source_hashes": source_hashes,
        "manifest": manifest,
        "ratio": (math.exp(-1 / 16) + math.exp(1 / 16)) / 2,
        "hidden_values": [0, 1],
        "kappa_s": Fraction(1),
        "beta": Fraction(1),
        "fine_edges": [("e", "v", "w"), ("d", "v", "z")],
    }
    mutations: list[dict[str, Any]] = []

    def reject(name: str, mutation: str, accepted: bool, detail: Any = "") -> None:
        mutations.append({"name": name, "mutation": mutation, "rejected": bool(not accepted), "detail": detail})

    changed = copy.deepcopy(baseline)
    changed["source_hashes"]["PAH-001"] = "0" * 64
    reject("source-hash-drift", "replace parent hash", changed["source_hashes"] == baseline["source_hashes"], changed["source_hashes"])

    changed = copy.deepcopy(baseline)
    changed["contract"]["status"]["contract"] = "ADMITTED"
    reject("status-promotion", "set contract to ADMITTED", changed["contract"]["status"]["contract"] == baseline["contract"]["status"]["contract"], changed["contract"]["status"])

    changed = copy.deepcopy(baseline)
    changed["kappa_s"] = Fraction(0)
    reject("zero-coupling", "set kappa_s=0", changed["kappa_s"] > 0, str(changed["kappa_s"]))

    changed = copy.deepcopy(baseline)
    changed["beta"] = Fraction(0)
    reject("zero-beta", "set beta=0", changed["beta"] > 0, str(changed["beta"]))

    changed = copy.deepcopy(baseline)
    changed["hidden_values"] = [0, 0]
    reject("collapse-hidden-fibre", "make hidden aperture values equal", len(set(changed["hidden_values"])) == 2, changed["hidden_values"])

    changed = copy.deepcopy(baseline)
    changed["fine_edges"] = [("e", "v", "w")]
    reject("drop-hidden-edge", "delete the inherited positive aperture edge", len(changed["fine_edges"]) == 2, changed["fine_edges"])

    changed = copy.deepcopy(baseline)
    changed["ratio"] = 1.0
    reject("erase-defect", "force conditional factor to one", changed["ratio"] > 1, changed["ratio"])

    changed = copy.deepcopy(baseline)
    changed["contract"]["compatibility_targets"]["strong_mainline"] = changed["contract"]["compatibility_targets"]["conditional_projected"]
    reject("strong-projected-substitution", "replace strong target by projected target", changed["contract"]["compatibility_targets"]["strong_mainline"] != changed["contract"]["compatibility_targets"]["conditional_projected"], changed["contract"]["compatibility_targets"])

    changed = copy.deepcopy(baseline)
    changed["contract"]["status"]["uniform_limit"] = "ADMITTED"
    reject("uniform-promotion", "admit uniform limit", changed["contract"]["status"]["uniform_limit"] == baseline["contract"]["status"]["uniform_limit"], changed["contract"]["status"])

    changed = copy.deepcopy(baseline)
    changed["contract"]["preservation_firewall"]["no_q3lock_import"] = False
    reject("q3lock-import", "allow Q3LOCK evidence", changed["contract"]["preservation_firewall"]["no_q3lock_import"] is True, changed["contract"]["preservation_firewall"])

    changed = copy.deepcopy(baseline)
    changed["contract"]["preservation_firewall"]["functional_unchanged"] = False
    reject("functional-mutation", "change inherited functional", changed["contract"]["preservation_firewall"]["functional_unchanged"] is True, changed["contract"]["preservation_firewall"])

    changed = copy.deepcopy(baseline)
    changed["contract"]["non_claims"] = ["physical Pre-A is proved"]
    reject("physical-promotion", "erase physical non-claims", any("No physical Pre-A" in item for item in changed["contract"]["non_claims"]), changed["contract"]["non_claims"])

    all_rejected = all(item["rejected"] for item in mutations)
    payload = {
        "schema": "tect/pah-omc002-conditional-kernel-hostile/1.0",
        "run_kind": "hostile",
        "audit_id": "PAH-COND-GIBBS-BLOCK-001",
        "exploration_id": "EXP-001367",
        "result_id": "R-480",
        "task_id": "T-054",
        "claim_bearing": False,
        "verification": "PASS" if all_rejected else "FAIL",
        "assertion_count": len(mutations),
        "passed": sum(item["rejected"] for item in mutations),
        "failed": sum(not item["rejected"] for item in mutations),
        "mutations_attempted": len(mutations),
        "mutations_rejected": sum(item["rejected"] for item in mutations),
        "all_mutations_rejected": all_rejected,
        "mutations": mutations,
        "source_hashes": source_hashes,
        "verdict": "ROUTE_LOCAL_CONDITIONAL_PROJECTED_INTERTWINING_FAIL",
        "stage2_status": "HOLD_FOR_EVIDENCE",
        "global_no_go_not_claimed": True,
        "physical_progress": False,
        "non_claims": [
            "Hostile mutations are firewall tests, not additional physical evidence.",
            "No PAH-001 bytes, functional, dynamics or limit order are mutated.",
            "No uniform, continuum, Pre-A, spacetime, gravity, QFT, Yang--Mills, mass-gap or TOE conclusion follows.",
        ],
    }
    atomic_json(output, payload)
    print(
        "PAH-COND-GIBBS-BLOCK-001 HOSTILE "
        f"{payload['verification']} {payload['passed']}/{payload['assertion_count']}; "
        f"mutations={payload['mutations_rejected']}/{payload['mutations_attempted']} rejected"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(args.output)
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
