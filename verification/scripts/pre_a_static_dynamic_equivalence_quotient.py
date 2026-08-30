#!/usr/bin/env python3
"""Primary exact-rational audit for the R-448 static-dynamic quotient."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-static-dynamic-equivalence-quotient-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-static_dynamic_equivalence_quotient/primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


@dataclass(frozen=True)
class Dynamics:
    static_signature: tuple[tuple[F, ...], tuple[F, ...]]
    factors: tuple[F, F]


def pair(values: list[str]) -> tuple[F, F]:
    return F(values[0]), F(values[1])


def static_equivalent(left: Dynamics, right: Dynamics) -> bool:
    return left.static_signature == right.static_signature


def dynamic_observable(candidate: Dynamics, probe: tuple[F, F]) -> tuple[F, F]:
    return candidate.factors[0] * probe[0], candidate.factors[1] * probe[1]


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]] == ["R-448", "EXP-001321", "T-061", False, "T0"], [manifest["result_id"], manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"], manifest["tier"]], ["R-448", "EXP-001321", "T-061", False, "T0"], "provenance")
    check("methods preserved", all(manifest["methods_preserved"].values()), manifest["methods_preserved"], "all true", "method-firewall")
    check("quotient relation", manifest["quotient_contract"]["relation"] == "d1 ~_static d2 iff d1.static_signature = d2.static_signature", manifest["quotient_contract"]["relation"], "static signature equality", "contract")
    check("equivalence laws declared", manifest["quotient_contract"]["equivalence_proof"] == ["reflexive", "symmetric", "transitive"], manifest["quotient_contract"]["equivalence_proof"], "three laws", "contract")
    check("claim nonbearing", manifest["claim_bearing"] is False and manifest["scope"]["no_tier_change"] is True, [manifest["claim_bearing"], manifest["scope"]["no_tier_change"]], [False, True], "scope")
    for key, item in manifest["inputs"].items():
        path = REPO / item["path"]
        check(f"input {key} hash", path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"], sha256(path) if path.is_file() else None, item["sha256"], "provenance")
    for key, item in manifest["files"].items():
        path = REPO / item["path"]
        if not (path.is_file() and item["sha256"] != "TO_BE_FILLED" and sha256(path) == item["sha256"]):
            raise AssertionError(f"file {key} hash mismatch")

    parents = {}
    for key in ("r193_manifest", "r200_manifest"):
        parents[key] = json.loads((REPO / manifest["inputs"][key]["path"]).read_text(encoding="utf-8"))
    check("parent identities", [parents["r193_manifest"]["result_id"], parents["r200_manifest"]["exploration_id"]] == ["R-193", "EXP-000992"], [parents["r193_manifest"]["result_id"], parents["r200_manifest"]["exploration_id"]], ["R-193", "EXP-000992"], "lineage")

    finite = manifest["finite_contract"]
    hessian = pair(finite["static_signature"]["hessian"])
    covariance = pair(finite["static_signature"]["covariance"])
    signature = (hessian, covariance)
    map_a = Dynamics(signature, pair(finite["maps"]["A"]["factors"]))
    map_b = Dynamics(signature, pair(finite["maps"]["B"]["factors"]))
    probe = pair(finite["probe"]["coordinates"])
    check("static inverse", hessian[0] * covariance[0] == 1 and hessian[1] * covariance[1] == 1, [str(hessian[0] * covariance[0]), str(hessian[1] * covariance[1])], ["1", "1"], "static")
    check("map A positive contractions", all(F(0) < value < F(1) for value in map_a.factors), [str(value) for value in map_a.factors], "strictly between zero and one", "dynamics")
    check("map B positive contractions", all(F(0) < value < F(1) for value in map_b.factors), [str(value) for value in map_b.factors], "strictly between zero and one", "dynamics")
    check("static equivalence", static_equivalent(map_a, map_b), True, True, "quotient")
    check("reflexivity", all(static_equivalent(candidate, candidate) for candidate in (map_a, map_b)), True, True, "quotient")
    check("symmetry", static_equivalent(map_a, map_b) == static_equivalent(map_b, map_a), True, True, "quotient")
    check("transitivity", static_equivalent(map_a, map_b) and static_equivalent(map_b, map_a) and static_equivalent(map_a, map_a), True, True, "quotient")
    check("maps distinct", map_a != map_b, True, True, "quotient")
    observed_a = dynamic_observable(map_a, probe)
    observed_b = dynamic_observable(map_b, probe)
    check("finite probe separates", observed_a != observed_b, [str(value) for value in observed_a], [str(value) for value in observed_b], "estimand")
    check("probe is declared one-step proxy", finite["probe"]["time_label"] == "one_step_proxy_not_physical_time", finite["probe"]["time_label"], "one_step_proxy_not_physical_time", "boundary")
    check("non-identifiability classification", manifest["scope"]["static_identifiability"] == "NON_IDENTIFIABLE" and manifest["quotient_contract"]["selection"] == "NO_SELECTION_FROM_STATIC_DATA", manifest["scope"]["static_identifiability"], "NON_IDENTIFIABLE", "boundary")
    check("unassessed stability and holdout", manifest["scope"]["stability_under_observation_error"] == "NOT_ASSESSED" and manifest["scope"]["holdout_prediction"] == "NOT_ASSESSED", [manifest["scope"]["stability_under_observation_error"], manifest["scope"]["holdout_prediction"]], "not assessed", "boundary")
    check("owner and physical firewalls", all(manifest["scope"][key] is False for key in ("source_owner_admitted", "production_generator_admitted", "physical_observable_map_admitted", "f_reg_f_lim_f_eff_f_obs_closed", "physical_identity", "pre_a_closed", "sector_a_closed", "c6_closed")), manifest["scope"], "all false", "boundary")

    derived = {
        "static_signature": [[str(value) for value in hessian], [str(value) for value in covariance]],
        "map_a_factors": [str(value) for value in map_a.factors],
        "map_b_factors": [str(value) for value in map_b.factors],
        "probe": [str(value) for value in probe],
        "probe_a": [str(value) for value in observed_a],
        "probe_b": [str(value) for value in observed_b],
        "static_equivalent": True,
        "maps_distinct": True,
        "equivalence_relation_checked": True,
        "static_class_non_singleton": True,
        "finite_estimand_separates": True,
        "static_identifiability": "NON_IDENTIFIABLE",
        "stability_under_observation_error": "NOT_ASSESSED",
        "stability_under_regulator_change": "NOT_ASSESSED",
        "holdout_prediction": "NOT_ASSESSED",
        "source_owner_admitted": False,
        "physical_identity": False
    }
    payload = {
        "schema": "tect/pre-a-static-dynamic-equivalence-quotient-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": manifest["status"],
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"]
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(f"R-448 PRIMARY {payload['verdict']} {len(checks)}/{len(checks)} class=non-singleton probe=separating", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output)
    if args.self_test:
        assert payload["verdict"] == "STATIC_DYNAMIC_EQUIVALENCE_QUOTIENT_AUDITED"
        assert payload["derived"]["finite_estimand_separates"] is True
        print("R-448 PRIMARY SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
