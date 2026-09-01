#!/usr/bin/env python3
"""Integrated and hostile verification for the Q3A-001 common-alpha audit.

This verifier reruns the primary and independent implementations in isolated
temporary outputs, compares their reconstructed scientific core, and checks
that scope- or verdict-changing mutations are rejected.  A PASS certifies the
HOLD_FOR_EVIDENCE audit record, not existence or nonexistence of the requested
infinite-volume dynamics.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SPEC_PATH = REPO / "strategy/q3lock/Q3A-001-v1.json"
PRIMARY = REPO / "codes/foundations/q3a001_common_alpha_audit.py"
INDEPENDENT = REPO / "codes/foundations/q3a001_common_alpha_audit_independent.py"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r477-q3-common-alpha/integrated.json"
)

EXPECTED_MODEL_HASH = "7ff6f2dd7877fc7d01da0421939ceab8f37c9b97adeedb3c063f6e16dc2ac38c"
EXPECTED_HAMILTONIAN_HASH = "48889ebc8d251ee1c45a7a185a96b487bc59c8d574e8c2d61c724dce00048535"
EXPECTED_STATUSES = {
    "Q3A-C1": "NOT_PROVED",
    "Q3A-C2": "NOT_PROVED",
    "Q3A-C3": "PARTIAL_NOT_CLOSED",
    "Q3A-C4": "NOT_PROVED",
    "Q3A-C5": "NOT_PROVED",
}


def canonical_hash(value: Any) -> str:
    data = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def report_is_admissible(report: dict[str, Any], run_kind: str) -> bool:
    core = report.get("core")
    if not isinstance(core, dict):
        return False
    non_claims = core.get("non_claims")
    return bool(
        report.get("schema") == "tect/q3lock-common-alpha-gate-audit-run/1.0"
        and report.get("run_kind") == run_kind
        and report.get("audit_id") == "Q3A-001"
        and report.get("result_id") == "R-477"
        and report.get("audit_integrity") == "PASS"
        and report.get("failed") == 0
        and report.get("passed") == report.get("assertion_count")
        and report.get("verdict") == "HOLD_FOR_EVIDENCE"
        and report.get("condition_vector") == [False, False, False, False, False]
        and report.get("claim_bearing") is False
        and report.get("gate_changed") is False
        and report.get("scientific_transition") is False
        and report.get("core_digest") == canonical_hash(core)
        and core.get("audit_id") == "Q3A-001"
        and core.get("result_id") == "R-477"
        and core.get("model_sha256") == EXPECTED_MODEL_HASH
        and core.get("hamiltonian_sha256") == EXPECTED_HAMILTONIAN_HASH
        and core.get("condition_statuses") == EXPECTED_STATUSES
        and core.get("verdict") == "HOLD_FOR_EVIDENCE"
        and "kappa<1" in str(core.get("next_question", ""))
        and "without introducing a new carrier"
        in str(core.get("next_question", ""))
        and isinstance(non_claims, list)
        and any("No common infinite-volume" in str(item) for item in non_claims)
        and any("No nonexistence theorem" in str(item) for item in non_claims)
        and any("No QFT" in str(item) and "TOE" in str(item) for item in non_claims)
    )


def spec_is_admissible(spec: dict[str, Any]) -> bool:
    exact = spec.get("exact_model")
    conditions = spec.get("required_conditions")
    decision = spec.get("decision_rule")
    mutation = spec.get("model_mutation")
    non_claims = spec.get("non_claims")
    if not all(
        isinstance(value, dict)
        for value in (exact, decision, mutation)
    ) or not isinstance(conditions, list) or not isinstance(non_claims, list):
        return False
    statuses = {item.get("id"): item.get("status") for item in conditions}
    candidate_source = exact.get("candidate_source", {})
    hamiltonian_source = exact.get("hamiltonian_source", {})
    return bool(
        spec.get("schema") == "tect/q3lock-common-alpha-gate-audit/1.0"
        and spec.get("audit_id") == "Q3A-001"
        and spec.get("result_id") == "R-477"
        and spec.get("verdict") == "HOLD_FOR_EVIDENCE"
        and spec.get("classification") == "HOLD_FOR_EVIDENCE"
        and spec.get("claim_bearing") is False
        and spec.get("gate_changed") is False
        and spec.get("scientific_transition") is False
        and not any(mutation.values())
        and candidate_source.get("sha256") == EXPECTED_MODEL_HASH
        and hamiltonian_source.get("sha256") == EXPECTED_HAMILTONIAN_HASH
        and statuses == EXPECTED_STATUSES
        and decision.get("derived_condition_vector")
        == [False, False, False, False, False]
        and decision.get("derived_verdict") == "HOLD_FOR_EVIDENCE"
        and "zero-source" in str(exact.get("source_scope", "")).lower()
        and "may not enter" in str(exact.get("beta_scope", "")).lower()
        and "direct sum is excluded" in str(exact.get("phase_scope", "")).lower()
        and "kappa<1" in str(spec.get("single_next_question", ""))
        and "without introducing a new carrier"
        in str(spec.get("single_next_question", ""))
        and any("No common infinite-volume" in str(item) for item in non_claims)
        and any("No nonexistence theorem" in str(item) for item in non_claims)
        and any("No QFT" in str(item) and "TOE" in str(item) for item in non_claims)
        and (
            "not a nonexistence" in str(spec.get("reason_not_negative", "")).lower()
            or "no contradiction" in str(spec.get("reason_not_negative", "")).lower()
        )
    )


def refresh_core_digest(report: dict[str, Any]) -> None:
    report["core_digest"] = canonical_hash(report["core"])


def run_child(script: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=False,
    )


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    spec = read_json(SPEC_PATH)
    with tempfile.TemporaryDirectory(prefix="q3a001-") as directory:
        root = Path(directory)
        primary_path = root / "primary.json"
        independent_path = root / "independent.json"
        primary_process = run_child(PRIMARY, primary_path)
        independent_process = run_child(INDEPENDENT, independent_path)
        check("primary-exit-zero", primary_process.returncode == 0, primary_process.stdout + primary_process.stderr)
        check(
            "independent-exit-zero",
            independent_process.returncode == 0,
            independent_process.stdout + independent_process.stderr,
        )
        primary = read_json(primary_path)
        independent = read_json(independent_path)

    check("spec-admissible", spec_is_admissible(spec))
    check("primary-admissible", report_is_admissible(primary, "primary"))
    check("independent-admissible", report_is_admissible(independent, "independent"))
    check("primary-116-of-116", (primary.get("passed"), primary.get("assertion_count")) == (116, 116))
    check("independent-62-of-62", (independent.get("passed"), independent.get("assertion_count")) == (62, 62))
    check("identical-core", primary.get("core") == independent.get("core"))
    check("identical-core-digest", primary.get("core_digest") == independent.get("core_digest"))
    check("identical-hold-verdict", primary.get("verdict") == independent.get("verdict") == "HOLD_FOR_EVIDENCE")

    report_mutations: list[tuple[str, dict[str, Any], str]] = []

    mutated = copy.deepcopy(primary)
    mutated["verdict"] = "MAINLINE_ADVANCE"
    report_mutations.append(("reject-mainline-promotion", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["core"]["verdict"] = "NEGATIVE_RESULT"
    refresh_core_digest(mutated)
    report_mutations.append(("reject-no-go-promotion", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["core"]["condition_statuses"]["Q3A-C1"] = "PASSED"
    refresh_core_digest(mutated)
    report_mutations.append(("reject-unproved-c1", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["condition_vector"][0] = True
    report_mutations.append(("reject-condition-vector-flip", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["core"]["hamiltonian_sha256"] = "0" * 64
    refresh_core_digest(mutated)
    report_mutations.append(("reject-hamiltonian-drift", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["core"]["model_sha256"] = "f" * 64
    refresh_core_digest(mutated)
    report_mutations.append(("reject-model-drift", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["core"]["next_question"] = "Try another finite table."
    refresh_core_digest(mutated)
    report_mutations.append(("reject-next-question-drift", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["claim_bearing"] = True
    report_mutations.append(("reject-claim-bearing", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["gate_changed"] = True
    report_mutations.append(("reject-false-gate-change", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["scientific_transition"] = True
    report_mutations.append(("reject-scientific-promotion", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["core"]["non_claims"] = []
    refresh_core_digest(mutated)
    report_mutations.append(("reject-removed-nonclaims", mutated, "primary"))

    mutated = copy.deepcopy(primary)
    mutated["core_digest"] = "1" * 64
    report_mutations.append(("reject-core-tamper", mutated, "primary"))

    for name, candidate, kind in report_mutations:
        check(name, not report_is_admissible(candidate, kind))

    spec_mutations: list[tuple[str, dict[str, Any]]] = []

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["model_mutation"]["new_hamiltonian"] = True
    spec_mutations.append(("reject-new-hamiltonian", mutated_spec))

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["model_mutation"]["new_counterterm"] = True
    spec_mutations.append(("reject-new-counterterm", mutated_spec))

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["model_mutation"]["new_carrier"] = True
    spec_mutations.append(("reject-new-carrier", mutated_spec))

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["model_mutation"]["new_physical_projection"] = True
    spec_mutations.append(("reject-new-physical-projection", mutated_spec))

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["exact_model"]["phase_scope"] = "A plus/minus direct sum is accepted."
    spec_mutations.append(("reject-posthoc-direct-sum", mutated_spec))

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["exact_model"]["beta_scope"] = "Beta selects the action."
    spec_mutations.append(("reject-beta-dependent-action", mutated_spec))

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["single_next_question"] = "Repeat a finite-volume carrier calculation."
    spec_mutations.append(("reject-finite-repeat", mutated_spec))

    mutated_spec = copy.deepcopy(spec)
    mutated_spec["non_claims"] = ["QFT and Pre-A are now proved."]
    spec_mutations.append(("reject-qft-prea-promotion", mutated_spec))

    for name, candidate in spec_mutations:
        check(name, not spec_is_admissible(candidate))

    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/q3lock-common-alpha-gate-integrated-verification/1.0",
        "audit_id": "Q3A-001",
        "result_id": "R-477",
        "exploration_id": "EXP-001358",
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "primary_assertions": primary["assertion_count"],
        "independent_assertions": independent["assertion_count"],
        "integrated_assertions": len(checks),
        "integrated_passed": len(checks) - len(failed),
        "integrated_failed": len(failed),
        "hostile_mutations_rejected": len(report_mutations) + len(spec_mutations),
        "core_digest": primary["core_digest"],
        "checks": checks,
        "non_claim": (
            "PASS verifies the evidence audit and its HOLD_FOR_EVIDENCE scope only; "
            "it proves neither existence nor nonexistence of the target dynamics."
        ),
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    print(
        "Q3A-001 INTEGRATED "
        f"{result['verification']} {result['integrated_passed']}/"
        f"{result['integrated_assertions']}; hostile="
        f"{result['hostile_mutations_rejected']}; verdict={result['verdict']}; "
        f"core={result['core_digest']}"
    )
    return 0 if result["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
