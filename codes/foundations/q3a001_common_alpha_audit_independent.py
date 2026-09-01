#!/usr/bin/env python3
"""Independent reconstruction of the Q3A-001 five-condition verdict.

This implementation does not import the primary auditor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "strategy/q3lock/Q3A-001-v1.json"
LOG = ROOT / "explorations/log.jsonl"
GATE_FILE = ROOT / "claims/GATES.md"
NEGATIVE_FILE = ROOT / "negative-results/registry.md"
DEFAULT_OUTPUT = ROOT / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-02-r477-q3-common-alpha/independent.json"
)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest_file(relative: str) -> str:
    return digest_bytes((ROOT / relative).read_bytes())


def object_digest(value: Any) -> str:
    encoded = json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    return digest_bytes(encoded)


def load_object(relative: str) -> dict[str, Any]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if type(value) is not dict:
        raise ValueError(f"object required: {relative}")
    return value


def normalized(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def find_gate(text: str, name: str) -> str:
    pattern = re.compile(
        re.escape(f"### **{name}**") + r".*?(?=\n### \*\*|\Z)", re.DOTALL
    )
    match = pattern.search(text)
    if match is None:
        raise KeyError(name)
    return match.group(0).rstrip("\n")


def find_negative(text: str, slug: str) -> str:
    marker = f'<a id="{slug}"></a>'
    start = text.find(marker)
    if start < 0:
        raise KeyError(slug)
    following = text.find("\n<a id=\"", start + len(marker))
    if following < 0:
        following = len(text)
    return text[start:following].rstrip("\n")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, staging = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(staging, path)
    except BaseException:
        try:
            os.unlink(staging)
        except FileNotFoundError:
            pass
        raise


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    spec = load_object("strategy/q3lock/Q3A-001-v1.json")
    tests: list[dict[str, Any]] = []

    def test(label: str, value: bool, observed: str = "") -> None:
        tests.append({"name": label, "passed": bool(value), "observed": observed})

    test("identity", (spec.get("audit_id"), spec.get("result_id")) == ("Q3A-001", "R-477"))
    test("honest-tier", spec.get("tier") == "T0" and spec.get("claim_bearing") is False)
    test("declared-hold", spec.get("classification") == "HOLD_FOR_EVIDENCE")
    test("no-mutations", not any(spec.get("model_mutation", {}).values()))

    exact = spec["exact_model"]
    for field in ("candidate_source", "hamiltonian_source"):
        item = exact[field]
        actual = digest_file(item["path"])
        test(f"{field}-digest", actual == item["sha256"], actual)

    base = load_object(exact["candidate_source"]["path"])
    fixed = load_object(exact["hamiltonian_source"]["path"])
    test("base-candidate", base.get("candidate_id") == "PA-CP1-ST8-Q3LOCK-v0")
    test("base-lambda-positive", "lambda>0" in base["definition"].get("parameter_domain", ""))
    test("fixed-origin", base["definition"].get("fixed_block_origin") is True)
    test("exact-formula", fixed["setup"].get("hamiltonian") == exact.get("hamiltonian"))
    test("fixed-dimension", exact.get("dimension") == 3 and exact.get("components_per_site") == 8)
    test("zero-source-action", "zero-source" in exact.get("source_scope", "").lower())
    test("beta-is-state-label", "may not enter" in exact.get("beta_scope", "").lower())

    selected = {
        **spec["historical_exploration_hashes"],
        **spec["later_exploration_hashes"],
    }
    rows: dict[str, dict[str, Any]] = {}
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        value = json.loads(line)
        if value.get("id") in selected:
            rows[value["id"]] = value
    test("all-selected-records", set(rows) == set(selected))
    for key in sorted(selected):
        actual = object_digest(rows[key])
        test(f"record-{key}", actual == selected[key], actual)

    for item in spec["pinned_authorities"]:
        actual = digest_file(item["path"])
        test("source-" + Path(item["path"]).stem, actual == item["sha256"], actual)

    negative_text = normalized("negative-results/registry.md")
    for slug, expected in spec["negative_section_hashes"].items():
        actual = digest_bytes(find_negative(negative_text, slug).encode("utf-8"))
        test("negative-" + slug, actual == expected, actual)

    local = load_object(
        "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-weighted-energy-route-split-manifest.json"
    )
    spatial = load_object(
        "strategy/pre-a-cp1-st8-q3lock-integrated-orbit-smear-spatial-quotient-ground-transfer-route-split-manifest.json"
    )
    cauchy = load_object(
        "strategy/pre-a-cp1-st8-q3lock-two-sided-history-cauchy-transfer-manifest.json"
    )
    recurrence = load_object(
        "strategy/pre-a-cp1-st8-q3lock-history-resolvent-recurrence-manifest.json"
    )
    derivation = local["common_local_derivation"]
    energy = local["weighted_first_local_energy"]
    cauchy_scope = cauchy["scope"]
    recurrence_scope = recurrence["scope"]
    toggle_status = spatial["conditional_integrated_toggle_hypothesis"]["status"].lower()

    gates = normalized("claims/GATES.md")
    parent = find_gate(
        gates,
        "PA-CP1-ST8-Q3LOCK-RESOLVENT-ALGEBRA-EXACT-POLYNOMIAL-COMMON-ALPHA-CLOSURE",
    )
    active = find_gate(
        gates,
        "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    )
    kms = find_gate(
        gates,
        "PA-CP1-ST8-Q3LOCK-DLR-TO-COMMON-ALPHA-KMS-IDENTIFICATION",
    )
    test("parent-not-closed", "**Status:** PARTIALLY RESOLVED" in parent)
    test("active-open", "**Status:** OPEN" in active)
    test("kms-open", "**Status:** OPEN HISTORICALLY" in kms)

    c1_closed = bool(
        cauchy_scope.get("actual_q3_history_closed")
        and cauchy_scope.get("common_weighted_operator_domain_closed")
        and cauchy_scope.get("exhaustion_independence_closed")
        and recurrence_scope.get("source_owned_kappa_closed")
    )
    c2_closed = bool(
        "no exact-q3" not in toggle_status
        and "**Status:** OPEN" not in active
    )
    c3_partial = bool(
        derivation.get("volume_independence")
        and derivation.get("phase_independent")
        and not derivation.get("exponentiated_common_automorphism")
    )
    c4_closed = bool("**Status:** OPEN HISTORICALLY" not in kms)
    c5_closed = bool(
        energy.get("common_alpha_proved")
        and cauchy_scope.get("source_uniformity_closed")
        and cauchy_scope.get("beta_uniformity_closed")
        and cauchy_scope.get("volume_uniformity_closed")
        and cauchy_scope.get("cutoff_uniformity_closed")
    )
    statuses = {
        "Q3A-C1": "PASSED" if c1_closed else "NOT_PROVED",
        "Q3A-C2": "PASSED" if c2_closed else "NOT_PROVED",
        "Q3A-C3": "PASSED" if not c3_partial else "PARTIAL_NOT_CLOSED",
        "Q3A-C4": "PASSED" if c4_closed else "NOT_PROVED",
        "Q3A-C5": "PASSED" if c5_closed else "NOT_PROVED",
    }
    declared = {item["id"]: item["status"] for item in spec["required_conditions"]}
    test("independent-status-reconstruction", statuses == declared, json.dumps(statuses, sort_keys=True))

    target_level_no_go = False
    all_five = all(value == "PASSED" for value in statuses.values())
    verdict = (
        "MAINLINE_ADVANCE"
        if all_five
        else "NEGATIVE_RESULT"
        if target_level_no_go
        else "HOLD_FOR_EVIDENCE"
    )
    test("independent-verdict", verdict == spec["verdict"], verdict)
    test("next-question-is-single-recurrence", "H_R <= kappa H_(R-1)" in spec["single_next_question"])
    test("next-question-no-new-carrier", "without introducing a new carrier" in spec["single_next_question"])

    core = {
        "audit_id": spec["audit_id"],
        "result_id": spec["result_id"],
        "model_sha256": exact["candidate_source"]["sha256"],
        "hamiltonian_sha256": exact["hamiltonian_source"]["sha256"],
        "hamiltonian": exact["hamiltonian"],
        "condition_statuses": statuses,
        "verdict": verdict,
        "next_question": spec["single_next_question"],
        "non_claims": spec["non_claims"],
    }
    failures = [row for row in tests if not row["passed"]]
    result = {
        "schema": "tect/q3lock-common-alpha-gate-audit-run/1.0",
        "run_kind": "independent",
        "audit_id": spec["audit_id"],
        "result_id": spec["result_id"],
        "exploration_id": spec["exploration_id"],
        "task_id": spec["task_id"],
        "claim_ids": spec["claim_ids"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "audit_integrity": "PASS" if not failures else "FAIL",
        "verdict": verdict,
        "condition_vector": [value == "PASSED" for value in statuses.values()],
        "assertion_count": len(tests),
        "passed": len(tests) - len(failures),
        "failed": len(failures),
        "assertions": tests,
        "core_digest": object_digest(core),
        "core": core,
        "claim_bearing": False,
        "gate_changed": False,
        "scientific_transition": False,
    }
    write_json(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    result = run(options.output)
    print(
        "Q3A-001 INDEPENDENT "
        f"{result['audit_integrity']} {result['passed']}/{result['assertion_count']}; "
        f"verdict={result['verdict']}; core={result['core_digest']}"
    )
    return 0 if result["audit_integrity"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
