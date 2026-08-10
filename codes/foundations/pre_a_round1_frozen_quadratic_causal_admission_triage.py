#!/usr/bin/env python3
"""Primary exact verifier for the frozen Pre-A Round-1 admission triage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-round1-frozen-quadratic-causal-admission-triage"
SCRIPT = Path(__file__).resolve()
EVIDENCE_SOURCE = REPO / "strategy/pre-a-round1-boundary-evidence-register-260809-v0.1.json"
EVIDENCE_FREEZE = REPO / "strategy/pre-a-round1-evidence-clue-freeze-260810-v1.0.json"
ADMISSION_FREEZE = REPO / "strategy/pre-a-round1-admission-discriminator-freeze-260810-v1.0.json"
MANIFEST = REPO / "strategy/pre-a-round1-frozen-quadratic-causal-admission-triage-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-primary-{SLUG}/result.json"
)


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected}
        )


def parse_target(source: dict[str, Any]) -> tuple[sp.Rational, sp.Rational, sp.Rational]:
    item = next(row for row in source["evidence_items"] if row["id"] == "PA-HO-T053-001")
    match = re.fullmatch(r"zeta = ([0-9.]+) \+/- ([0-9.]+) in the reported reanalysis", item["reported_value"])
    if match is None:
        raise AssertionError("unexpected visible-validation value format")
    centre = sp.Rational(match.group(1))
    error = sp.Rational(match.group(2))
    return centre, centre - error, centre + error


def derive_m2() -> dict[str, Any]:
    p1, p2, p3, c, q, chi = sp.symbols("p1 p2 p3 c q chi", positive=True)
    momenta = (q + p1, q + p2, q + p3)
    kernel = sp.expand(c * sum((q**2 - k**2) ** 2 for k in momenta))
    hessian = sp.hessian(kernel, (p1, p2, p3)).subs({p1: 0, p2: 0, p3: 0})
    scale = sp.symbols("scale", positive=True)
    ray = sp.expand(kernel.subs({p1: scale * p1, p2: scale * p2, p3: scale * p3}))
    leading = sp.simplify(sp.limit(ray / scale**2, scale, 0))
    expected_leading = 4 * c * q**2 * (p1**2 + p2**2 + p3**2)
    speed_squared = sp.simplify(leading / (chi * (p1**2 + p2**2 + p3**2)))
    return {
        "hessian": hessian,
        "expected_hessian": 8 * c * q**2 * sp.eye(3),
        "leading_kernel": leading,
        "expected_leading_kernel": expected_leading,
        "speed_squared": speed_squared,
        "expected_speed_squared": 4 * c * q**2 / chi,
    }


def derive_visible_prediction() -> dict[str, Any]:
    a, u, z, t = sp.symbols("a u z t", positive=True)
    amplitude_squared = a * t / u
    stiffness = sp.expand(z * amplitude_squared)
    leading_coefficient = sp.simplify(sp.diff(stiffness, t))
    return {
        "amplitude_squared": amplitude_squared,
        "stiffness": stiffness,
        "leading_coefficient": leading_coefficient,
        "exponent": 1,
    }


def run() -> dict[str, Any]:
    audit = Audit()
    source = load_json(EVIDENCE_SOURCE)
    evidence = load_json(EVIDENCE_FREEZE)
    admission = load_json(ADMISSION_FREEZE)
    manifest = load_json(MANIFEST)

    audit.check("evidence freeze schema", evidence["schema"].endswith("/1.0"), evidence["schema"], "*/1.0", "freeze")
    audit.check("admission freeze schema", admission["schema"].endswith("/1.0"), admission["schema"], "*/1.0", "freeze")
    audit.check("manifest result id", manifest["result_id"].startswith("PRE-A-ROUND1-"), manifest["result_id"], "PRE-A-ROUND1-*", "freeze")
    audit.check(
        "source register hash",
        normalized_sha256(EVIDENCE_SOURCE) == evidence["source_register"]["normalized_sha256"],
        normalized_sha256(EVIDENCE_SOURCE),
        evidence["source_register"]["normalized_sha256"],
        "provenance",
    )
    audit.check(
        "evidence freeze hash",
        normalized_sha256(EVIDENCE_FREEZE) == admission["evidence_freeze"]["normalized_sha256"],
        normalized_sha256(EVIDENCE_FREEZE),
        admission["evidence_freeze"]["normalized_sha256"],
        "provenance",
    )
    for row in admission["contestants"]:
        path = REPO / row["path"]
        audit.check(
            f"candidate hash {row['candidate_id']}",
            normalized_sha256(path) == row["normalized_sha256"],
            normalized_sha256(path),
            row["normalized_sha256"],
            "provenance",
        )

    source_ids = [row["id"] for row in source["evidence_items"]] + [row["id"] for row in source["calibration_authorities"]]
    role_ids = [row["id"] for row in evidence["evidence_roles"]]
    audit.check("evidence role coverage", sorted(role_ids) == sorted(source_ids), sorted(role_ids), sorted(source_ids), "evidence")
    audit.check("evidence role uniqueness", len(role_ids) == len(set(role_ids)), len(role_ids), len(set(role_ids)), "evidence")
    audit.check("clue ids unique", len({row["id"] for row in evidence["clue_items"]}) == len(evidence["clue_items"]), len(evidence["clue_items"]), "unique", "evidence")
    ev2 = next(row for row in evidence["evidence_roles"] if row["id"] == "PA-EV-T053-002")
    audit.check("GW timing is speed-only evidence", ev2["used_for"] == ["D04-SPEED-DISPERSION"], ev2["used_for"], ["D04-SPEED-DISPERSION"], "evidence")
    posthoc_role = next(row for row in evidence["evidence_roles"] if row["id"] == "PA-HO-T053-001")
    audit.check("target role is retrospective", posthoc_role["role"] == "VISIBLE_POSTHOC_DIAGNOSTIC_TARGET", posthoc_role["role"], "VISIBLE_POSTHOC_DIAGNOSTIC_TARGET", "evidence")
    audit.check("bounded freeze complete", evidence["completeness"]["round1_t053_boundary_role_freeze_complete"] is True, True, True, "evidence")
    audit.check("full evidence remains open", evidence["completeness"]["full_pre_a_evidence_register_complete"] is False, False, False, "scope")

    candidate_ids = [row["candidate_id"] for row in admission["contestants"]]
    audit.check("contestant set", candidate_ids == list(admission["normalized_candidate_contracts"]), candidate_ids, list(admission["normalized_candidate_contracts"]), "admission")
    required = set(admission["canonical_candidate_schema"])
    for candidate_id, contract in admission["normalized_candidate_contracts"].items():
        audit.check(
            f"canonical field coverage {candidate_id}",
            required.issubset(contract),
            sorted(required & set(contract)),
            sorted(required),
            "admission",
        )
    d00_question = next(row["question"] for row in admission["discriminators"] if row["id"] == "D00-ADMISSION")
    d00_is_label_scope = d00_question == "Are all nine canonical field labels present, with every absence and partial status explicit?"
    audit.check("field labels are not semantic completeness", d00_is_label_scope and admission["completeness"]["canonical_candidate_semantic_completeness"] is False, [d00_question, admission["completeness"]["canonical_candidate_semantic_completeness"]], ["nine-label explicit-absence scope", False], "scope")
    audit.check("per-parameter ledger remains open", admission["completeness"]["per_parameter_common_input_ledger_complete"] is False, False, False, "scope")
    audit.check("bridge not contestant", admission["noncontestant_bridges"][0]["score_eligible"] is False, False, False, "admission")
    audit.check("categorical outcomes", admission["allowed_outcomes"] == ["PASS", "FAIL", "NOT_TESTED", "NOT_ADMITTED", "INCOMPARABLE"], admission["allowed_outcomes"], "fixed five outcomes", "admission")
    freeze_text = ADMISSION_FREEZE.read_text(encoding="utf-8")
    leaked_tokens = [token for token in ("0.672", "0.671", "0.673", "+/- 0.001") if token in freeze_text]
    audit.check("visible target value not leaked into prediction freeze", not leaked_tokens, leaked_tokens, [], "validation")
    diagnostic = admission["visible_posthoc_diagnostic"]
    audit.check("diagnostic target was already public", diagnostic["target_was_public_before_contract"] is True, True, True, "validation")
    audit.check("diagnostic has no gate credit", diagnostic["validation_credit"] is False, False, False, "validation")

    m1 = load_json(REPO / admission["contestants"][1]["path"])
    audit.check("M1 gradient law", "gradient flow" in m1["law"]["evolution"], m1["law"]["evolution"], "gradient flow", "quadratic")
    audit.check("M1 canonical momentum absent", m1["state_and_degrees_of_freedom"]["canonical_momentum"].startswith("absent"), m1["state_and_degrees_of_freedom"]["canonical_momentum"], "absent", "quadratic")
    audit.check("M1 physical map absent", m1["observable_map"]["map_to_round1_measured_observables"] is False, False, False, "quadratic")

    m2 = derive_m2()
    audit.check("M2 node Hessian", m2["hessian"] == m2["expected_hessian"], str(m2["hessian"]), str(m2["expected_hessian"]), "quadratic")
    audit.check("M2 leading kernel", sp.simplify(m2["leading_kernel"] - m2["expected_leading_kernel"]) == 0, str(m2["leading_kernel"]), str(m2["expected_leading_kernel"]), "quadratic")
    audit.check("M2 speed squared", sp.simplify(m2["speed_squared"] - m2["expected_speed_squared"]) == 0, str(m2["speed_squared"]), str(m2["expected_speed_squared"]), "quadratic")

    m5 = load_json(REPO / admission["contestants"][3]["path"])
    audit.check("M5 rank-one obstruction", "rank-one" in m5["statement"], "rank-one" in m5["statement"], True, "quadratic")
    audit.check("M5 gauge completion absent", m5["scope"]["local_gauge_completion"] is False, False, False, "quadratic")

    prediction = derive_visible_prediction()
    audit.check("tree amplitude is linear", sp.degree(prediction["amplitude_squared"], sp.Symbol("t", positive=True)) == 1, str(prediction["amplitude_squared"]), "degree 1", "validation")
    audit.check("tree stiffness coefficient positive", prediction["leading_coefficient"].is_positive is True, str(prediction["leading_coefficient"]), "positive", "validation")
    audit.check("tree exponent", prediction["exponent"] == 1, prediction["exponent"], 1, "validation")
    centre, lower, upper = parse_target(source)
    audit.check("target centre", centre == sp.Rational(84, 125), str(centre), "84/125", "validation")
    audit.check("target interval", (lower, upper) == (sp.Rational(671, 1000), sp.Rational(673, 1000)), [str(lower), str(upper)], ["671/1000", "673/1000"], "validation")
    audit.check("frozen prediction fails interval", not (lower <= 1 <= upper), "1 outside interval", True, "validation")
    scored = manifest["visible_posthoc_diagnostic"]
    audit.check("retrospective formula conflicts with interval", scored["outcome"] == "RETROSPECTIVE_DIAGNOSTIC_CONFLICT", scored["outcome"], "RETROSPECTIVE_DIAGNOSTIC_CONFLICT", "validation")
    audit.check("comparison has no validation credit", scored["validation_credit"] is False, False, False, "validation")
    audit.check("prediction was not preregistered", scored["prediction_preregistered_before_target_disclosure"] is False, False, False, "validation")

    allowed = set(admission["allowed_outcomes"])
    for candidate_id, row in manifest["categorical_matrix"].items():
        values = [value for key, value in row.items() if key.startswith("D")]
        audit.check(f"matrix categories {candidate_id}", set(values) <= allowed, sorted(set(values)), sorted(allowed), "matrix")
    roles = {row["candidate_id"]: row["role"] for row in admission["contestants"]}
    eligible_roles = set(manifest["survival_rule"]["eligible_roles"])
    hard_rows = manifest["survival_rule"]["hard_rows"]
    derived_survivors = sorted(
        candidate_id
        for candidate_id, row in manifest["categorical_matrix"].items()
        if roles[candidate_id] in eligible_roles and all(row[gate] == "PASS" for gate in hard_rows)
    )
    audit.check("survivors derived from frozen matrix", derived_survivors == manifest["round1_verdict"]["admitted_microscopic_survivors"], derived_survivors, manifest["round1_verdict"]["admitted_microscopic_survivors"], "verdict")
    audit.check("no selected candidate", manifest["round1_verdict"]["selected_candidate"] is None, None, None, "verdict")
    audit.check("no admitted survivor", derived_survivors == [], derived_survivors, [], "verdict")
    audit.check("bounded inventory frozen", manifest["round1_verdict"]["bounded_role_and_contract_inventory_frozen"] is True, True, True, "verdict")
    audit.check("parent freeze gate remains open", manifest["round1_verdict"]["freeze_gate_closed"] is False, False, False, "verdict")
    audit.check("no Pre-A exit", manifest["round1_verdict"]["pre_a_exit_conditions_met"] is False, False, False, "scope")
    audit.check("no physical selection", manifest["scope"]["physical_functional_selected"] is False, False, False, "scope")

    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-round1-frozen-quadratic-causal-admission-triage-primary-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "derived": {
            "M2_node_hessian": str(m2["hessian"]),
            "M2_speed_squared": str(m2["speed_squared"]),
            "retrospective_formula_exponent": "1",
            "visible_target_interval": [str(lower), str(upper)],
            "validation_credit": False,
            "derived_survivors": derived_survivors,
            "round1_outcome": manifest["round1_verdict"]["outcome"],
        },
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, EVIDENCE_SOURCE, EVIDENCE_FREEZE, ADMISSION_FREEZE, MANIFEST)
        },
        "assertions": audit.rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"PASS {summary['passed']}/{summary['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
