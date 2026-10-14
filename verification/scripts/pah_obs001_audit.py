"""PAH-OBS-001 source and scope replay, not a physical-law verifier.

The illustrative Bernoulli instrument is an UNADOPTED input hypothesis.
Exact algebra tests its half-factor, quadrature sign and per-face calibration.
No PAH dynamics, experiment, physical time or error bound is computed.
--write issues a deterministic receipt after separate reviewers accept hashes.
--source-cache optionally checks the original versioned primary PDF bytes.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
BASE = "strategy/pa-hyp/PAH-OBS-001-"
ADMISSION = BASE + "admission-v1.json"
ASSESSMENT = BASE + "assessment-v1.json"
PROPOSAL = BASE + "instrument-proposal-v0.1.json"
REVIEW = BASE + "review-v1.json"
SCRIPT = "verification/scripts/pah_obs001_audit.py"
OUTPUT = "claims/C6-SPACETIME-SIGNATURE/runs/2026-10-14-pah-obs001/audit.json"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def firewall(a, p):
    assert a["verdict"] == "HOLD_FOR_EVIDENCE"
    assert a["classification"] == "auxiliary_support"
    assert a["new_result_id"] is None
    for key in ("claim_bearing", "active_gate_change", "physical_promotion"):
        assert a[key] is False, key
    assert a["missing_input"]["status"] == "NOT_SUPPLIED_OR_ADOPTED"
    assert a["distinct_judgments"]["static_W_readability"] == "UNRESOLVED_NOT_REFUTED"
    assert a["follow_on"]["attempts_remaining"] == 0
    assert a["follow_on"]["automatic_successor"] is False
    assert p["status"] == "UNADOPTED_HYPOTHESIS_ONLY"
    assert p["adopted"] is False
    assert p["parent_model_changed"] is False
    assert all(value is None for value in p["unfilled_inputs"].values())


def algebra_controls():
    # All rational constants below are definition coefficients or test INPUTS.
    # They are not fitted/derived physical numbers.
    controls = []
    a, b, theta, vis, offset = sp.symbols("a b theta vis offset", real=True)
    z = a + sp.I * b
    q = sp.expand_complex(sp.exp(sp.I * theta) * z)
    signal = sp.re(q)
    assert sp.simplify(signal - (a * sp.cos(theta) - b * sp.sin(theta))) == 0
    controls.append("reference_quadrature_sign")
    plus = (1 + offset + vis * signal) / 2
    minus = 1 - plus
    mean = plus - minus
    assert sp.simplify((mean - offset) / vis - signal) == 0
    assert plus.subs({a: 1, b: 0, theta: 0, vis: 1, offset: 0}) == 1
    assert plus.subs({a: -1, b: 0, theta: 0, vis: 1, offset: 0}) == 0
    assert plus.subs({a: 0, b: 1, theta: sp.pi/2, vis: 1, offset: 0}) == 0
    controls.append("half_factor_and_anchor_cases")
    assert sp.simplify(sp.expand_complex(z * sp.conjugate(z)) - (a*a+b*b)) == 0
    # Unit-modulus scalar phase leaves the population unchanged.
    phi = sp.symbols("phi", real=True)
    phased = sp.exp(sp.I * phi) * z
    assert sp.simplify(phased * sp.conjugate(phased) - z * sp.conjugate(z)) == 0
    controls.append("population_only_has_no_scalar_phase_response")

    def probability(real_signal, contrast, bias=F(0)):
        assert F(0) <= contrast <= F(1)
        assert abs(bias) + contrast <= F(1)
        assert F(-1) <= real_signal <= F(1)
        result = (F(1) + bias + contrast * real_signal) / F(2)
        assert F(0) <= result <= F(1)
        return result

    def reconstruct(prob, contrast, bias=F(0)):
        assert contrast > 0
        return (F(2)*prob-F(1)-bias)/contrast

    # Two face-input oracle, not a finite-carrier evolution experiment.
    face_inputs = [(F(1), F(1)), (F(-1), F(1, 2))]
    probs = [probability(u, v) for u, v in face_inputs]
    correct = sum(reconstruct(p0, v) for p0, (_, v) in zip(probs, face_inputs))/len(probs)
    desired = sum(u for u, _ in face_inputs)/len(face_inputs)
    mean_vis = sum(v for _, v in face_inputs)/len(face_inputs)
    wrong = (F(2)*sum(probs)/len(probs)-F(1))/mean_vis
    assert correct == desired
    assert wrong != desired
    controls.append("individual_calibration_before_equal_face_average")
    rejected = []
    for name, fn in (
        ("zero_visibility", lambda: reconstruct(F(1, 2), F(0))),
        ("negative_visibility", lambda: probability(F(0), F(-1))),
        ("invalid_offset_contrast", lambda: probability(F(1), F(1), F(1, 2))),
    ):
        try:
            fn()
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError(name)
    assert len(rejected) == 3  # Named negative-test oracle.
    controls.extend(rejected)
    return controls


def metadata_mutations(a, p):
    rejected = []
    for key, bad in (("verdict", "ADMISSIBLE_FOR_TEST"), ("new_result_id", "FORBIDDEN"),
                     ("claim_bearing", True), ("active_gate_change", True),
                     ("physical_promotion", True)):
        changed = copy.deepcopy(a)
        changed[key] = bad
        try:
            firewall(changed, p)
        except AssertionError:
            rejected.append(key)
        else:
            raise AssertionError("metadata mutation escaped: " + key)
    for key in ("adopted", "parent_model_changed"):
        changed = copy.deepcopy(p)
        changed[key] = True
        try:
            firewall(a, changed)
        except AssertionError:
            rejected.append(key)
        else:
            raise AssertionError("proposal mutation escaped: " + key)
    changed = copy.deepcopy(p)
    changed["unfilled_inputs"]["physical_probe_coupling"] = "invented"
    try:
        firewall(a, changed)
    except AssertionError:
        rejected.append("invented_coupling")
    else:
        raise AssertionError("invented coupling escaped")
    return rejected


def audit(with_review=True):
    if not __debug__:
        raise RuntimeError("Assertions must be enabled")
    pre, a, p = read(ADMISSION), read(ASSESSMENT), read(PROPOSAL)
    firewall(a, p)
    assert a["admission"]["sha256"] == sha(ADMISSION)
    assert pre["attempt_budget"] == 1  # Tooling admission budget.
    assert {r["id"] for r in a["source_crosswalk"]} == set(pre["required_fields"])
    checked = {}
    for path, expected in pre["source_pins"].items():
        assert sha(path) == expected, path
        checked[path] = expected
    parent = read("strategy/pa-hyp/PAH-001-v1.json")
    assert "external stochastic time" in parent["dynamics"]["time"]
    assert "neutral tagged probe" in parent["microscopic_degrees_of_freedom"]["probe"]
    assert "kappa_0 s_v^nu" in parent["horizon_collapse_tests"]["probe_rates"]
    assert p["parent_sha256"] == sha(p["parent"])
    assert a["unadopted_proposal"] == PROPOSAL
    artifacts = (ADMISSION, ASSESSMENT, PROPOSAL, SCRIPT)
    if with_review:
        review = read(REVIEW)
        for path in artifacts:
            assert review["artifact_hashes"][path] == sha(path), path
        assert {r["role"] for r in review["reviews"]} == {"independent", "hostile"}
        assert all(r["verdict"] == "ACCEPT_SCOPED_AUDIT" for r in review["reviews"])
        artifacts += (REVIEW,)
    return {
        "schema": "tect/pah-observation-audit-replay/1.0",
        "status": "PASS_PROVENANCE_AND_CONDITIONAL_ALGEBRA_ONLY",
        "scientific_verdict": a["verdict"],
        "source_hashes": checked,
        "artifact_hashes": {path: sha(path) for path in artifacts},
        "algebra_controls": algebra_controls(),
        "metadata_mutations_rejected": metadata_mutations(a, p),
        "external_source_expected_sha256": pre["external_source"]["sha256"],
        "external_source_boundary": "Primary source read/review is separate; optional --source-cache validates PDF bytes. Offline hashes do not prove source applicability.",
        "non_claims": "No realized instrument, physical identity, observed data, error envelope, dynamics computation, Lean theorem or mainline advance.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--selftest", action="store_true")
    parser.add_argument("--source-cache", type=Path)
    args = parser.parse_args()
    result = audit(with_review=not args.selftest)
    if args.source_cache:
        data = (args.source_cache / "1805.08248v1.pdf").read_bytes()
        assert data.startswith(b"%PDF")
        assert hashlib.sha256(data).hexdigest() == read(ADMISSION)["external_source"]["sha256"]
        print("OBS-001 PRIMARY PDF BYTES: PASS")
    if args.write:
        out = ROOT / OUTPUT
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    elif not args.selftest:
        assert read(OUTPUT) == result, "deterministic receipt drift"
    print("OBS-001 AUDIT: PASS (scope/hash/conditional instrument algebra only);",
          len(result["algebra_controls"]), "algebra controls;",
          len(result["metadata_mutations_rejected"]), "metadata controls;",
          result["scientific_verdict"])


if __name__ == "__main__":
    main()
