#!/usr/bin/env python3
"""Primary five-condition audit of the exact Q3LOCK common-alpha gate.

An exit-zero result certifies the authority crosswalk and the honest
HOLD_FOR_EVIDENCE verdict.  It does not certify existence or nonexistence of
the thermodynamic real-time dynamics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/q3lock/Q3A-001-v1.json"
EXPLORATIONS = REPO / "explorations/log.jsonl"
NEGATIVES = REPO / "negative-results/registry.md"
GATES = REPO / "claims/GATES.md"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r477-q3-common-alpha/primary.json"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return sha256_bytes(payload)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected JSON object: {path}")
    return value


def read_explorations() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for raw in EXPLORATIONS.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        value = json.loads(raw)
        row_id = value.get("id")
        if isinstance(row_id, str):
            rows[row_id] = value
    return rows


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def anchored_section(text: str, marker: str, next_marker: str) -> str:
    start = text.index(marker)
    end = text.find(next_marker, start + len(marker))
    if end < 0:
        end = len(text)
    return text[start:end].rstrip("\n")


def negative_section(text: str, slug: str) -> str:
    marker = f'<a id="{slug}"></a>'
    return anchored_section(text, marker, "\n<a id=\"")


def gate_section(text: str, gate_id: str) -> str:
    marker = f"### **{gate_id}**"
    return anchored_section(text, marker, "\n### **")


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=True, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = read_json(MANIFEST)
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    check("schema", manifest.get("schema") == "tect/q3lock-common-alpha-gate-audit/1.0")
    check("audit-id", manifest.get("audit_id") == "Q3A-001")
    check("result-id", manifest.get("result_id") == "R-477")
    check("exploration-id", manifest.get("exploration_id") == "EXP-001358")
    check("task-id", manifest.get("task_id") == "T-054")
    check("claim-nonbearing", manifest.get("claim_bearing") is False)
    check("gate-unchanged", manifest.get("gate_changed") is False)
    check("no-scientific-transition", manifest.get("scientific_transition") is False)
    check("declared-verdict", manifest.get("verdict") == "HOLD_FOR_EVIDENCE")

    mutation = manifest.get("model_mutation", {})
    for key in (
        "new_hamiltonian",
        "new_counterterm",
        "new_carrier",
        "new_physical_projection",
    ):
        check(f"no-{key.replace('_', '-')}", mutation.get(key) is False)

    exact = manifest["exact_model"]
    candidate_ref = exact["candidate_source"]
    hamiltonian_ref = exact["hamiltonian_source"]
    candidate_path = REPO / candidate_ref["path"]
    hamiltonian_path = REPO / hamiltonian_ref["path"]
    check("candidate-source-hash", sha256_file(candidate_path) == candidate_ref["sha256"])
    check("hamiltonian-source-hash", sha256_file(hamiltonian_path) == hamiltonian_ref["sha256"])

    candidate = read_json(candidate_path)
    hamiltonian = read_json(hamiltonian_path)
    definition = candidate["definition"]
    setup = hamiltonian["setup"]
    check("candidate-identity", candidate.get("candidate_id") == exact["candidate_id"])
    check("dimension-three", exact.get("dimension") == 3)
    check("eight-components", exact.get("components_per_site") == 8)
    check("q3-species-graph", definition.get("species_graph") == exact["species_graph"])
    check("positive-lambda", "lambda>0" in definition.get("parameter_domain", ""))
    check("fixed-block-origin", definition.get("fixed_block_origin") is True)
    check("hamiltonian-exact-text", setup.get("hamiltonian") == exact["hamiltonian"])
    check("zero-source-target", "zero-source" in exact.get("source_scope", ""))
    check("fixed-lattice-only", exact.get("continuum_limit") == "not in scope; lattice spacing remains fixed")

    records = read_explorations()
    expected_records = {
        **manifest["historical_exploration_hashes"],
        **manifest["later_exploration_hashes"],
    }
    for record_id, expected_hash in expected_records.items():
        value = records.get(record_id)
        check(f"record-present-{record_id}", value is not None)
        if value is not None:
            check(
                f"record-hash-{record_id}",
                canonical_hash(value) == expected_hash,
                canonical_hash(value),
            )

    exp782 = records["EXP-000782"]
    exp790 = records["EXP-000790"]
    exp792 = records["EXP-000792"]
    exp846 = records["EXP-000846"]
    check(
        "exp782-excludes-real-time",
        "no infinite-volume real-time dynamics" in exp782.get("finding", "").lower(),
    )
    check(
        "exp790-no-common-alpha",
        "no common hamiltonian-derived alpha" in exp790.get("finding", "").lower(),
    )
    check(
        "exp792-only-local-derivation",
        "common alpha remains open" in exp792.get("finding", "").lower(),
    )
    check(
        "exp846-conditional-weights",
        "integrated-toggle weights are hypotheses, not exact-q3 estimates"
        in exp846.get("boundary", "").lower(),
    )

    for authority in manifest["pinned_authorities"]:
        path = REPO / authority["path"]
        check(
            "authority-hash-" + path.name,
            sha256_file(path) == authority["sha256"],
            authority["role"],
        )

    local = read_json(
        REPO
        / "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-manifest.json"
    )
    local_derivation = local["common_local_derivation"]
    first_energy = local["weighted_first_local_energy"]
    check("local-derivation-volume-independent", local_derivation.get("volume_independence") is True)
    check("local-derivation-phase-independent", local_derivation.get("phase_independent") is True)
    check("local-derivation-not-exponentiated", local_derivation.get("exponentiated_common_automorphism") is False)
    check("first-energy-common-alpha-open", first_energy.get("common_alpha_proved") is False)

    spatial = read_json(
        REPO
        / "strategy/pre-a-cp1-st8-q3lock-integrated-orbit-smear-spatial-quotient-ground-transfer-route-split-manifest.json"
    )
    toggle = spatial["conditional_integrated_toggle_hypothesis"]
    check("bsp-toggle-is-hypothesis", "theorem hypothesis" in toggle.get("status", "").lower())
    check("bsp-no-exact-q3-weight", "no exact-q3" in toggle.get("status", "").lower())

    cauchy = read_json(REPO / "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json")
    recurrence = read_json(REPO / "strategy/pre-a-cp1-st8-q3lock-history-resolvent-recurrence-manifest.json")
    check("cauchy-actual-q3-open", cauchy["scope"].get("actual_q3_history_closed") is False)
    check("cauchy-common-domain-open", cauchy["scope"].get("common_weighted_operator_domain_closed") is False)
    check("cauchy-exhaustion-open", cauchy["scope"].get("exhaustion_independence_closed") is False)
    check("recurrence-kappa-open", recurrence["scope"].get("source_owned_kappa_closed") is False)
    check("recurrence-common-alpha-open", recurrence["scope"].get("common_alpha_closed") is False)

    gates_text = normalized_text(GATES)
    parent_gate = gate_section(
        gates_text,
        "PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-COMMON-ALPHA-CLOSURE",
    )
    active_gate = gate_section(
        gates_text,
        "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    )
    kms_gate = gate_section(
        gates_text,
        "PA-CP1-ST8-Q3LOCK-DLR-TO-COMMON-ALPHA-KMS-IDENTIFICATION",
    )
    check("parent-gate-partial", "**Status:** PARTIALLY RESOLVED" in parent_gate)
    check("parent-common-alpha-open", "Common `alpha`" in parent_gate and "remain open" in parent_gate)
    check("active-gate-open", "**Status:** OPEN" in active_gate)
    check("active-no-nonexistence", "No exact Q3LOCK dynamics nonexistence is asserted" in active_gate)
    check("kms-gate-open", "**Status:** OPEN HISTORICALLY" in kms_gate)

    negatives_text = normalized_text(NEGATIVES)
    for slug, expected_hash in manifest["negative_section_hashes"].items():
        section = negative_section(negatives_text, slug)
        actual_hash = sha256_bytes(section.encode("utf-8"))
        check(f"negative-section-{slug}", actual_hash == expected_hash, actual_hash)

    conditions = manifest["required_conditions"]
    status_vector = [item["status"] for item in conditions]
    check("five-conditions", len(conditions) == 5)
    check("condition-ids", [item["id"] for item in conditions] == [f"Q3A-C{i}" for i in range(1, 6)])
    check(
        "condition-status-vector",
        status_vector
        == ["NOT_PROVED", "NOT_PROVED", "PARTIAL_NOT_CLOSED", "NOT_PROVED", "NOT_PROVED"],
    )
    all_closed = all(status == "PASSED" for status in status_vector)
    exact_no_go = False
    derived_vector = [status == "PASSED" for status in status_vector]
    derived_verdict = (
        "MAINLINE_ADVANCE" if all_closed else "NEGATIVE_RESULT" if exact_no_go else "HOLD_FOR_EVIDENCE"
    )
    check("derived-vector", derived_vector == manifest["decision_rule"]["derived_condition_vector"])
    check("derived-hold", derived_verdict == manifest["decision_rule"]["derived_verdict"])
    check("not-negative", "not a nonexistence" in manifest["reason_not_negative"].lower() or "no contradiction" in manifest["reason_not_negative"].lower())
    check("single-next-question", "kappa<1" in manifest.get("single_next_question", ""))
    check("five-nonclaims", len(manifest.get("non_claims", [])) >= 5)

    core = {
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "model_sha256": candidate_ref["sha256"],
        "hamiltonian_sha256": hamiltonian_ref["sha256"],
        "hamiltonian": exact["hamiltonian"],
        "condition_statuses": {
            item["id"]: item["status"] for item in conditions
        },
        "verdict": derived_verdict,
        "next_question": manifest["single_next_question"],
        "non_claims": manifest["non_claims"],
    }
    failed = [item for item in checks if not item["passed"]]
    payload = {
        "schema": "tect/q3lock-common-alpha-gate-audit-run/1.0",
        "run_kind": "primary",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "task_id": manifest["task_id"],
        "claim_ids": manifest["claim_ids"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "audit_integrity": "PASS" if not failed else "FAIL",
        "verdict": derived_verdict,
        "condition_vector": derived_vector,
        "assertion_count": len(checks),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "assertions": checks,
        "core_digest": canonical_hash(core),
        "core": core,
        "evidence_level": ["EXACT", "EXECUTED", "AUDIT", "CONDITIONAL"],
        "claim_bearing": False,
        "gate_changed": False,
        "scientific_transition": False,
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    print(
        "Q3A-001 PRIMARY "
        f"{payload['audit_integrity']} {payload['passed']}/{payload['assertion_count']}; "
        f"verdict={payload['verdict']}; core={payload['core_digest']}"
    )
    return 0 if payload["audit_integrity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
