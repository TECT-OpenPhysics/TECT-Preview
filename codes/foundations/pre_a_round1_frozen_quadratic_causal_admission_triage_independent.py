#!/usr/bin/env python3
"""Independent stdlib verifier for the frozen Pre-A Round-1 triage.

This implementation deliberately does not import the primary verifier and does
not use a computer-algebra or array package.  Its quadratic calculation uses a
small exact Laurent-polynomial engine whose coefficients are ``Fraction``
objects.  The visible validation value is parsed only after the tree-level
prediction has been derived from exact scaling ratios.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


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
    / f"2026-08-10-independent-{SLUG}/result.json"
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


# Exact Laurent polynomials in c, q, chi, p1, p2, p3.  Negative exponents
# occur only when the derived kernel is divided by the inertial coefficient.
VARIABLES = ("c", "q", "chi", "p1", "p2", "p3")
MOMENTUM_INDICES = (3, 4, 5)
Monomial = tuple[int, int, int, int, int, int]


class ExactLaurent:
    def __init__(self, terms: dict[Monomial, Fraction] | None = None) -> None:
        self.terms = {monomial: coefficient for monomial, coefficient in (terms or {}).items() if coefficient}

    @classmethod
    def scalar(cls, value: int | Fraction) -> "ExactLaurent":
        coefficient = Fraction(value)
        return cls({(0, 0, 0, 0, 0, 0): coefficient}) if coefficient else cls()

    @classmethod
    def variable(cls, index: int) -> "ExactLaurent":
        powers = [0] * len(VARIABLES)
        powers[index] = 1
        return cls({tuple(powers): Fraction(1)})

    @staticmethod
    def coerce(other: object) -> "ExactLaurent":
        if isinstance(other, ExactLaurent):
            return other
        if isinstance(other, (int, Fraction)):
            return ExactLaurent.scalar(other)
        return NotImplemented

    def __add__(self, other: object) -> "ExactLaurent":
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        terms = dict(self.terms)
        for monomial, coefficient in rhs.terms.items():
            terms[monomial] = terms.get(monomial, Fraction(0)) + coefficient
            if not terms[monomial]:
                del terms[monomial]
        return ExactLaurent(terms)

    __radd__ = __add__

    def __neg__(self) -> "ExactLaurent":
        return ExactLaurent({monomial: -coefficient for monomial, coefficient in self.terms.items()})

    def __sub__(self, other: object) -> "ExactLaurent":
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        return self + (-rhs)

    def __rsub__(self, other: object) -> "ExactLaurent":
        lhs = self.coerce(other)
        if lhs is NotImplemented:
            return NotImplemented
        return lhs - self

    def __mul__(self, other: object) -> "ExactLaurent":
        rhs = self.coerce(other)
        if rhs is NotImplemented:
            return NotImplemented
        terms: dict[Monomial, Fraction] = {}
        for left_monomial, left_coefficient in self.terms.items():
            for right_monomial, right_coefficient in rhs.terms.items():
                monomial = tuple(a + b for a, b in zip(left_monomial, right_monomial))
                terms[monomial] = terms.get(monomial, Fraction(0)) + left_coefficient * right_coefficient
        return ExactLaurent(terms)

    __rmul__ = __mul__

    def __pow__(self, power: int) -> "ExactLaurent":
        if not isinstance(power, int) or power < 0:
            raise ValueError("only non-negative integer powers are supported")
        result = ExactLaurent.scalar(1)
        factor = self
        exponent = power
        while exponent:
            if exponent & 1:
                result = result * factor
            factor = factor * factor
            exponent //= 2
        return result

    def derivative(self, index: int) -> "ExactLaurent":
        terms: dict[Monomial, Fraction] = {}
        for monomial, coefficient in self.terms.items():
            power = monomial[index]
            if power == 0:
                continue
            reduced = list(monomial)
            reduced[index] -= 1
            terms[tuple(reduced)] = coefficient * power
        return ExactLaurent(terms)

    def homogeneous_momentum_part(self, degree: int) -> "ExactLaurent":
        return ExactLaurent(
            {
                monomial: coefficient
                for monomial, coefficient in self.terms.items()
                if sum(monomial[index] for index in MOMENTUM_INDICES) == degree
            }
        )

    def at_zero_momentum(self) -> "ExactLaurent":
        return ExactLaurent(
            {
                monomial: coefficient
                for monomial, coefficient in self.terms.items()
                if all(monomial[index] == 0 for index in MOMENTUM_INDICES)
            }
        )

    def coefficient_of_momentum_square(self, momentum_index: int) -> "ExactLaurent":
        wanted = [0, 0, 0]
        wanted[momentum_index] = 2
        terms: dict[Monomial, Fraction] = {}
        for monomial, coefficient in self.terms.items():
            if [monomial[index] for index in MOMENTUM_INDICES] != wanted:
                continue
            stripped = list(monomial)
            for index in MOMENTUM_INDICES:
                stripped[index] = 0
            terms[tuple(stripped)] = coefficient
        return ExactLaurent(terms)

    def divide_by_variable(self, index: int) -> "ExactLaurent":
        terms: dict[Monomial, Fraction] = {}
        for monomial, coefficient in self.terms.items():
            divided = list(monomial)
            divided[index] -= 1
            terms[tuple(divided)] = coefficient
        return ExactLaurent(terms)

    def __eq__(self, other: object) -> bool:
        rhs = self.coerce(other)
        return rhs is not NotImplemented and self.terms == rhs.terms

    def __bool__(self) -> bool:
        return bool(self.terms)


def one_term_formula(polynomial: ExactLaurent) -> str:
    if len(polynomial.terms) != 1:
        raise AssertionError(f"expected one monomial, found {polynomial.terms!r}")
    monomial, coefficient = next(iter(polynomial.terms.items()))
    sign = "-" if coefficient < 0 else ""
    magnitude = abs(coefficient)
    numerator: list[str] = []
    denominator: list[str] = []
    if magnitude.numerator != 1 or not any(power for power in monomial):
        numerator.append(str(magnitude.numerator))
    if magnitude.denominator != 1:
        denominator.append(str(magnitude.denominator))
    for variable, power in zip(VARIABLES, monomial):
        if power > 0:
            numerator.append(variable if power == 1 else f"{variable}**{power}")
        elif power < 0:
            positive = -power
            denominator.append(variable if positive == 1 else f"{variable}**{positive}")
    top = "*".join(numerator) if numerator else "1"
    if denominator:
        bottom = "*".join(denominator)
        return f"{sign}{top}/{bottom}"
    return sign + top


def derive_m2_exact() -> dict[str, Any]:
    c = ExactLaurent.variable(0)
    q = ExactLaurent.variable(1)
    momenta = [ExactLaurent.variable(index) for index in MOMENTUM_INDICES]
    kernel = sum((c * (q**2 - (q + momentum) ** 2) ** 2 for momentum in momenta), ExactLaurent())

    # These components are obtained by exact convolution of Fraction-valued
    # coefficient maps, not by substituting the result declared in the manifest.
    quadratic = kernel.homogeneous_momentum_part(2)
    cubic = kernel.homogeneous_momentum_part(3)
    quartic = kernel.homogeneous_momentum_part(4)
    lower = kernel.homogeneous_momentum_part(0) + kernel.homogeneous_momentum_part(1)
    higher = sum((kernel.homogeneous_momentum_part(degree) for degree in range(5, 9)), ExactLaurent())

    hessian: list[list[ExactLaurent]] = []
    for left in MOMENTUM_INDICES:
        row: list[ExactLaurent] = []
        for right in MOMENTUM_INDICES:
            row.append(kernel.derivative(left).derivative(right).at_zero_momentum())
        hessian.append(row)

    diagonal = [hessian[index][index] for index in range(3)]
    off_diagonal = [hessian[i][j] for i in range(3) for j in range(3) if i != j]
    leading_coefficients = [quadratic.coefficient_of_momentum_square(index) for index in range(3)]
    speed_coefficients = [coefficient.divide_by_variable(2) for coefficient in leading_coefficients]

    expected_diagonal = ExactLaurent({(1, 2, 0, 0, 0, 0): Fraction(8)})
    expected_leading = ExactLaurent({(1, 2, 0, 0, 0, 0): Fraction(4)})
    expected_speed = ExactLaurent({(1, 2, -1, 0, 0, 0): Fraction(4)})
    expected_cubic_terms = {
        tuple([1, 1, 0] + [3 if index == axis else 0 for index in range(3)]): Fraction(4)
        for axis in range(3)
    }
    expected_quartic_terms = {
        tuple([1, 0, 0] + [4 if index == axis else 0 for index in range(3)]): Fraction(1)
        for axis in range(3)
    }

    if lower or higher:
        raise AssertionError("expanded M2 node kernel has an unexpected momentum degree")
    if cubic.terms != expected_cubic_terms or quartic.terms != expected_quartic_terms:
        raise AssertionError("exact node expansion does not have the expected separable cubic/quartic tails")
    if diagonal != [expected_diagonal] * 3 or any(off_diagonal):
        raise AssertionError("exact node Hessian is not the derived isotropic diagonal matrix")
    if leading_coefficients != [expected_leading] * 3:
        raise AssertionError("quadratic node coefficients disagree across axes")
    if speed_coefficients != [expected_speed] * 3:
        raise AssertionError("inertial dispersion coefficients disagree across axes")

    diagonal_formula = one_term_formula(diagonal[0])
    speed_formula = one_term_formula(speed_coefficients[0])
    matrix_formula = "Matrix([[{0}, 0, 0], [0, {0}, 0], [0, 0, {0}]])".format(diagonal_formula)
    leading_formula = one_term_formula(leading_coefficients[0]) + "*(p1**2 + p2**2 + p3**2)"
    return {
        "kernel_term_count": len(kernel.terms),
        "quadratic_term_count": len(quadratic.terms),
        "cubic_term_count": len(cubic.terms),
        "quartic_term_count": len(quartic.terms),
        "hessian_factor": diagonal_formula,
        "hessian": matrix_formula,
        "leading_kernel": leading_formula,
        "speed_squared": speed_formula,
    }


def derive_tree_stiffness_prediction() -> dict[str, Any]:
    # INPUT fixtures test the generic rho(tau)=Z*a*tau/u scaling without any
    # floating-point logarithm.  tau is the positive distance below onset.
    a = Fraction(7, 5)
    u_effective = Fraction(11, 6)
    z_factor = Fraction(13, 9)
    tau = Fraction(2, 7)

    def stiffness(distance: Fraction) -> Fraction:
        amplitude_squared = a * distance / u_effective
        return z_factor * amplitude_squared

    scaling_rows: list[dict[str, str | int]] = []
    inferred_exponents: list[int] = []
    for scale in (Fraction(2), Fraction(3), Fraction(5, 2)):
        ratio = stiffness(scale * tau) / stiffness(tau)
        candidates = [power for power in range(0, 7) if scale**power == ratio]
        if len(candidates) != 1:
            raise AssertionError(f"scaling ratio did not identify one integer exponent: {scale=}, {ratio=}")
        inferred_exponents.append(candidates[0])
        scaling_rows.append({"scale": str(scale), "stiffness_ratio": str(ratio), "inferred_power": candidates[0]})

    if len(set(inferred_exponents)) != 1:
        raise AssertionError("tree-stiffness scaling tests disagree")
    return {
        "exponent": inferred_exponents[0],
        "amplitude_power": inferred_exponents[0],
        "scaling_rows": scaling_rows,
    }


TARGET_PATTERN = re.compile(
    r"zeta\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*\+/-\s*([0-9]+(?:\.[0-9]+)?)\s+in the reported reanalysis"
)


def parse_visible_target_after_prediction(source: dict[str, Any]) -> dict[str, Any]:
    rows = [row for row in source["evidence_items"] if row["id"] == "PA-HO-T053-001"]
    if len(rows) != 1:
        raise AssertionError("visible validation target must occur exactly once")
    reported = rows[0]["reported_value"]
    match = TARGET_PATTERN.fullmatch(reported)
    if match is None:
        raise AssertionError("unexpected visible-validation value format")
    centre_text, error_text = match.groups()
    centre = Fraction(centre_text)
    error = Fraction(error_text)
    return {
        "reported": reported,
        "centre": centre,
        "error": error,
        "lower": centre - error,
        "upper": centre + error,
        "centre_text": centre_text,
        "error_text": error_text,
    }


def by_id(rows: Iterable[dict[str, Any]], key: str, identifier: str) -> dict[str, Any]:
    matches = [row for row in rows if row[key] == identifier]
    if len(matches) != 1:
        raise AssertionError(f"expected one {key}={identifier!r}, found {len(matches)}")
    return matches[0]


def run() -> dict[str, Any]:
    audit = Audit()

    # Load every freeze and candidate authority, but deliberately defer loading
    # the evidence source containing the visible target until after prediction.
    evidence = load_json(EVIDENCE_FREEZE)
    admission = load_json(ADMISSION_FREEZE)
    manifest = load_json(MANIFEST)
    evidence_text = EVIDENCE_FREEZE.read_text(encoding="utf-8")
    admission_text = ADMISSION_FREEZE.read_text(encoding="utf-8")

    syntax_tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(syntax_tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    allowed_imports = {
        "__future__", "argparse", "ast", "hashlib", "json", "os", "re", "tempfile",
        "fractions", "pathlib", "typing",
    }
    audit.check("independent implementation is stdlib-only", imported_roots <= allowed_imports, sorted(imported_roots), sorted(allowed_imports), "independence")
    audit.check("evidence freeze is non-claim-bearing", evidence["claim_bearing"] is False, evidence["claim_bearing"], False, "scope")
    audit.check("admission freeze is non-claim-bearing", admission["claim_bearing"] is False, admission["claim_bearing"], False, "scope")
    audit.check("triage manifest is non-claim-bearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    source_hash = normalized_sha256(EVIDENCE_SOURCE)
    evidence_hash = normalized_sha256(EVIDENCE_FREEZE)
    admission_hash = normalized_sha256(ADMISSION_FREEZE)
    audit.check("source register hash", source_hash == evidence["source_register"]["normalized_sha256"], source_hash, evidence["source_register"]["normalized_sha256"], "provenance")
    audit.check("evidence freeze hash in admission", evidence_hash == admission["evidence_freeze"]["normalized_sha256"], evidence_hash, admission["evidence_freeze"]["normalized_sha256"], "provenance")
    audit.check("evidence freeze hash in result", evidence_hash == manifest["parent_freezes"]["evidence_clue"]["normalized_sha256"], evidence_hash, manifest["parent_freezes"]["evidence_clue"]["normalized_sha256"], "provenance")
    audit.check("admission freeze hash in result", admission_hash == manifest["parent_freezes"]["admission_discriminator"]["normalized_sha256"], admission_hash, manifest["parent_freezes"]["admission_discriminator"]["normalized_sha256"], "provenance")

    contestant_ids: list[str] = []
    candidates: dict[str, dict[str, Any]] = {}
    provenance_paths: list[Path] = []
    for row in admission["contestants"]:
        path = REPO / row["path"]
        candidate = load_json(path)
        candidate_id = row["candidate_id"]
        contestant_ids.append(candidate_id)
        candidates[candidate_id] = candidate
        provenance_paths.append(path)
        audit.check(f"candidate hash {candidate_id}", normalized_sha256(path) == row["normalized_sha256"], normalized_sha256(path), row["normalized_sha256"], "provenance")
        audit.check(f"candidate identity {candidate_id}", candidate["candidate_id"] == candidate_id, candidate["candidate_id"], candidate_id, "provenance")
        audit.check(f"candidate claim boundary {candidate_id}", candidate["claim_bearing"] is False, candidate["claim_bearing"], False, "scope")

    bridge_ids: list[str] = []
    for row in admission["noncontestant_bridges"]:
        path = REPO / row["path"]
        bridge = load_json(path)
        bridge_ids.append(row["id"])
        provenance_paths.append(path)
        audit.check(f"bridge hash {row['id']}", normalized_sha256(path) == row["normalized_sha256"], normalized_sha256(path), row["normalized_sha256"], "provenance")
        audit.check(f"bridge excluded {row['id']}", row["score_eligible"] is False, row["score_eligible"], False, "admission")
        bridge_identity = bridge.get("candidate_id", bridge.get("package_id"))
        audit.check(f"bridge identity {row['id']}", bridge_identity == row["id"], bridge_identity, row["id"], "provenance")

    contracts = admission["normalized_candidate_contracts"]
    required_fields = admission["canonical_candidate_schema"]
    audit.check("contestant identities are unique", len(contestant_ids) == len(set(contestant_ids)), len(contestant_ids), len(set(contestant_ids)), "admission")
    audit.check("contract identities equal contestants", set(contracts) == set(contestant_ids), sorted(contracts), sorted(contestant_ids), "admission")
    audit.check("bridge identities are disjoint", set(bridge_ids).isdisjoint(contestant_ids), bridge_ids, "disjoint from contestants", "admission")
    for candidate_id, contract in contracts.items():
        actual_fields = set(contract) - {"admission_status"}
        audit.check(f"exact contract fields {candidate_id}", actual_fields == set(required_fields), sorted(actual_fields), sorted(required_fields), "contract")
        audit.check(f"explicit admission status {candidate_id}", bool(contract["admission_status"]), contract["admission_status"], "nonempty", "contract")

    discriminator_ids = [row["id"] for row in admission["discriminators"]]
    expected_discriminators = [f"D{index:02d}-{suffix}" for index, suffix in enumerate((
        "ADMISSION", "SAME-REFERENCE", "KINETIC-TENSOR", "PHYSICAL-ZERO-MODES", "SPEED-DISPERSION",
        "COMPACT-WINDING", "CRITICAL-DATA", "VALIDATION", "ROBUSTNESS", "PREDICTION-COST",
    ))]
    allowed_outcomes = ["PASS", "FAIL", "NOT_TESTED", "NOT_ADMITTED", "INCOMPARABLE"]
    d00_question = admission["discriminators"][0]["question"]
    d00_is_label_scope = d00_question == "Are all nine canonical field labels present, with every absence and partial status explicit?"
    audit.check("discriminator sequence", discriminator_ids == expected_discriminators and d00_is_label_scope, [discriminator_ids, d00_question], [expected_discriminators, "nine-label explicit-absence scope"], "contract")
    audit.check("allowed categorical outcomes", admission["allowed_outcomes"] == allowed_outcomes, admission["allowed_outcomes"], allowed_outcomes, "contract")
    posthoc_contract = admission["visible_posthoc_diagnostic"]
    audit.check("posthoc freeze declares target value absent", posthoc_contract["target_value_present_in_this_freeze"] is False, posthoc_contract["target_value_present_in_this_freeze"], False, "anti_leakage")
    audit.check("posthoc formula forbids target parameter choice", posthoc_contract["parameter_choice_uses_target"] is False, posthoc_contract["parameter_choice_uses_target"], False, "anti_leakage")
    audit.check("posthoc formula receives no preregistration credit", posthoc_contract["prediction_preregistered_before_target_disclosure"] is False and posthoc_contract["validation_credit"] is False, [posthoc_contract["prediction_preregistered_before_target_disclosure"], posthoc_contract["validation_credit"]], [False, False], "scope")

    m1_id = "PA-M1-CURRENT-PINNED-PRODUCTION-FUNCTIONAL-v0"
    m1 = candidates[m1_id]
    m1_result = manifest["exact_derived_relations"]["M1"]
    audit.check("M1 registered gradient law", "canonical L2 gradient flow" in m1["law"]["evolution"], m1["law"]["evolution"], "canonical L2 gradient flow", "M1")
    audit.check("M1 canonical momentum absent", m1["state_and_degrees_of_freedom"]["canonical_momentum"].startswith("absent"), m1["state_and_degrees_of_freedom"]["canonical_momentum"], "absent", "M1")
    audit.check("M1 measured-observable map absent", m1["observable_map"]["map_to_round1_measured_observables"] is False, m1["observable_map"]["map_to_round1_measured_observables"], False, "M1")
    audit.check("M1 neutral order exact boundary", m1["tournament_status"]["same_reference_neutral_test"] == "FAIL FOR NONZERO ORDER", m1["tournament_status"]["same_reference_neutral_test"], "FAIL FOR NONZERO ORDER", "M1")
    audit.check("M1 result law matches authority", m1_result["registered_law"] == "canonical first-order L2 gradient flow", m1_result["registered_law"], "canonical first-order L2 gradient flow", "M1")
    audit.check("M1 result does not invent momentum", m1_result["canonical_momentum"] == "absent", m1_result["canonical_momentum"], "absent", "M1")
    audit.check("M1 repair creates a new version", "new candidate version" in m1_result["repair_boundary"], m1_result["repair_boundary"], "contains new candidate version", "M1")

    # First exact calculation: derive the M2 kernel rather than importing or
    # evaluating the primary implementation.
    m2 = derive_m2_exact()
    m2_id = "PA-M2-CI8-RS-v0"
    m2_authority = candidates[m2_id]
    m2_result = manifest["exact_derived_relations"]["M2"]
    m2_parameter_domain = m2_authority["functional"]["parameter_domain"]
    m2_inertial_law = m2_authority["functional"]["lane_q_hamiltonian"]
    audit.check("M2 source declares positive kernel and inertial parameters", "c>0" in m2_parameter_domain and "m>=1" in m2_parameter_domain and "chi>0" in m2_inertial_law, [m2_parameter_domain, m2_inertial_law], "c>0, q nonzero through m>=1, chi>0", "M2")
    audit.check("M2 source kernel matches expanded operator", "c sum_i((partial_i^2+q^2)phi)^2" in m2_authority["functional"]["static_energy"] and m2_result["critical_kernel"] == "K(k)=r+c*sum_i(q^2-k_i^2)^2", [m2_authority["functional"]["static_energy"], m2_result["critical_kernel"]], "declared separable squared kernel", "M2")
    audit.check("M2 exact expansion partitions by degree", m2["kernel_term_count"] == sum(m2[f"{degree}_term_count"] for degree in ("quadratic", "cubic", "quartic")), m2["kernel_term_count"], "sum of homogeneous term counts", "M2")
    derived_hessian_relation = f"D_k^2 K(k_star)={m2['hessian_factor'].replace('**', '^')}*I_3"
    audit.check("M2 node Hessian matches result", m2_result["node_hessian"] == derived_hessian_relation, m2_result["node_hessian"], derived_hessian_relation, "M2")
    audit.check("M2 speed matches result", m2_result["tree_speed_squared"] == m2["speed_squared"].replace("**", "^"), m2_result["tree_speed_squared"], m2["speed_squared"].replace("**", "^"), "M2")
    audit.check("M2 exact leading dispersion", m2_result["small_momentum_dispersion"].startswith(f"omega^2=({m2['speed_squared'].replace('**', '^')})*|p|^2"), m2_result["small_momentum_dispersion"], f"omega^2=({m2['speed_squared']})*|p|^2+...", "M2")
    m2_inserted_inputs = m2_authority["input_prediction_accounting"]["inserted_inputs"]
    audit.check("M2 inertial time remains inserted", "inertial time law for Lane Q" in m2_inserted_inputs, m2_inserted_inputs, "contains inertial time law for Lane Q", "M2")

    m5_id = "PA-M5-NL3-SV-v0"
    m5 = candidates[m5_id]
    m5_result = manifest["exact_derived_relations"]["M5"]
    audit.check("M5 rank-one Hessian boundary", "rank-one spatial quadratic Hessian" in m5["statement"], m5["statement"], "rank-one spatial quadratic Hessian", "M5")
    audit.check("M5 evolution not declared", m5["functional"]["declared_evolution_law"] is False, m5["functional"]["declared_evolution_law"], False, "M5")
    audit.check("M5 local gauge completion absent", m5["scope"]["local_gauge_completion"] is False, m5["scope"]["local_gauge_completion"], False, "M5")
    audit.check("M5 common cone failed", m5["mathematical_status"]["common_isotropic_critical_cone"].startswith("FAILED"), m5["mathematical_status"]["common_isotropic_critical_cone"], "FAILED", "M5")
    audit.check("M5 result preserves bare scope", "bare continuous isotropic shell" in m5_result["causal_verdict"], m5_result["causal_verdict"], "bare continuous isotropic shell", "M5")
    audit.check("M5 repair creates a new version", "new candidate version" in m5_result["repair_boundary"], m5_result["repair_boundary"], "contains new candidate version", "M5")

    # Second exact calculation.  This happens before the evidence source is
    # loaded and before any visible target number is parsed.
    prediction = derive_tree_stiffness_prediction()
    frozen_prediction = admission["visible_posthoc_diagnostic"]
    audit.check("tree stiffness exponent derived consistently", prediction["exponent"] == prediction["amplitude_power"], prediction["exponent"], prediction["amplitude_power"], "validation")
    audit.check("frozen prediction agrees with exact scaling", frozen_prediction["prediction"] == f"zeta_tree={prediction['exponent']} exactly", frozen_prediction["prediction"], f"zeta_tree={prediction['exponent']} exactly", "validation")

    # Only now is the source JSON containing PA-HO-T053-001 loaded and its
    # public value interpreted as an interval.
    source = load_json(EVIDENCE_SOURCE)
    source_ids = [row["id"] for row in source["evidence_items"]] + [row["id"] for row in source["calibration_authorities"]]
    role_ids = [row["id"] for row in evidence["evidence_roles"]]
    audit.check("source role coverage", sorted(source_ids) == sorted(role_ids), sorted(role_ids), sorted(source_ids), "evidence")
    audit.check("source roles are one-to-one", len(role_ids) == len(set(role_ids)) == len(source_ids), len(role_ids), len(source_ids), "evidence")
    audit.check("all omitted families are classified", all(row.get("status") and row.get("reason") for row in evidence["round_scope"]["excluded_or_deferred_families"]), True, True, "evidence")
    audit.check("bounded evidence freeze closes only Round 1", evidence["completeness"]["round1_t053_boundary_role_freeze_complete"] is True and evidence["completeness"]["full_pre_a_evidence_register_complete"] is False, evidence["completeness"], "Round 1 true and full Pre-A false", "scope")

    target = parse_visible_target_after_prediction(source)
    lower = target["lower"]
    upper = target["upper"]
    predicted = Fraction(prediction["exponent"])
    audit.check("derived prediction lies outside visible interval", not (lower <= predicted <= upper), str(predicted), f"outside [{lower}, {upper}]", "validation")
    leaked_tokens = sorted(
        token
        for token in {
            target["reported"],
            target["centre_text"],
            target["error_text"],
        }
        if token in evidence_text or token in admission_text
    )
    audit.check("visible target values absent from both freezes", leaked_tokens == [], leaked_tokens, [], "anti_leakage")

    score = manifest["visible_posthoc_diagnostic"]
    score_interval = [Fraction(value) for value in score["reported_interval_used_for_categorical_test"]]
    audit.check("result target interval matches source", score_interval == [lower, upper], [str(value) for value in score_interval], [str(lower), str(upper)], "validation")
    audit.check("result prediction matches derivation", Fraction(score["predicted_exponent"]) == predicted, score["predicted_exponent"], str(predicted), "validation")
    audit.check("posthoc conflict follows interval", score["outcome"] == "RETROSPECTIVE_DIAGNOSTIC_CONFLICT", score["outcome"], "RETROSPECTIVE_DIAGNOSTIC_CONFLICT", "validation")
    audit.check("result awards no validation credit", score["prediction_preregistered_before_target_disclosure"] is False and score["validation_credit"] is False, [score["prediction_preregistered_before_target_disclosure"], score["validation_credit"]], [False, False], "scope")
    audit.check("no sigma overclaim", score["sigma_claimed"] is False, score["sigma_claimed"], False, "scope")

    matrix = manifest["categorical_matrix"]
    audit.check("matrix contestants exactly frozen", set(matrix) == set(contestant_ids), sorted(matrix), sorted(contestant_ids), "matrix")
    expected_matrix_keys = set(discriminator_ids) | {"overall"}
    for candidate_id, row in matrix.items():
        audit.check(f"matrix field coverage {candidate_id}", set(row) == expected_matrix_keys, sorted(row), sorted(expected_matrix_keys), "matrix")
        categories = [row[identifier] for identifier in discriminator_ids]
        audit.check(f"matrix categories {candidate_id}", set(categories) <= set(allowed_outcomes), sorted(set(categories)), allowed_outcomes, "matrix")
    audit.check("M1 matrix follows exact boundaries", matrix[m1_id]["D01-SAME-REFERENCE"] == "FAIL" and matrix[m1_id]["D02-KINETIC-TENSOR"] == "NOT_ADMITTED", [matrix[m1_id]["D01-SAME-REFERENCE"], matrix[m1_id]["D02-KINETIC-TENSOR"]], ["FAIL", "NOT_ADMITTED"], "matrix")
    m2_d04_note = manifest["matrix_evidence_notes"]["M2_internal_tree_cone"]
    m2_d04_match = re.search(r"D04 remains (PASS|FAIL|NOT_TESTED|NOT_ADMITTED|INCOMPARABLE)", m2_d04_note)
    if m2_d04_match is None:
        raise AssertionError("M2 D04 evidence note does not declare its categorical status")
    m2_expected_d04 = m2_d04_match.group(1)
    audit.check("M2 matrix preserves internal cone without validation credit", matrix[m2_id]["D02-KINETIC-TENSOR"] == "PASS" and matrix[m2_id]["D04-SPEED-DISPERSION"] == m2_expected_d04 and matrix[m2_id]["D07-VALIDATION"] == "NOT_TESTED", [matrix[m2_id]["D02-KINETIC-TENSOR"], matrix[m2_id]["D04-SPEED-DISPERSION"], matrix[m2_id]["D07-VALIDATION"]], ["PASS", m2_expected_d04, "NOT_TESTED"], "matrix")
    m5_boundary_ids = ("D02-KINETIC-TENSOR", "D03-PHYSICAL-ZERO-MODES", "D04-SPEED-DISPERSION", "D05-COMPACT-WINDING")
    m5_expected = ["NOT_ADMITTED", "NOT_ADMITTED", "FAIL", "FAIL"]
    audit.check("M5 matrix follows bare-shell boundary", [matrix[m5_id][identifier] for identifier in m5_boundary_ids] == m5_expected, [matrix[m5_id][identifier] for identifier in m5_boundary_ids], m5_expected, "matrix")

    verdict = manifest["round1_verdict"]
    audit.check("bounded role and contract inventory is frozen", verdict["bounded_role_and_contract_inventory_frozen"] is True, verdict["bounded_role_and_contract_inventory_frozen"], True, "verdict")
    audit.check("parent freeze gate remains open", verdict["freeze_gate_closed"] is False, verdict["freeze_gate_closed"], False, "verdict")
    audit.check("prospective validation preregistration remains open", verdict["visible_validation_preregistration_complete"] is False, verdict["visible_validation_preregistration_complete"], False, "verdict")
    audit.check("weighted ranking was not performed", verdict["weighted_ranking_performed"] is False, verdict["weighted_ranking_performed"], False, "verdict")
    audit.check("no candidate selected", verdict["selected_candidate"] is None, verdict["selected_candidate"], None, "verdict")
    audit.check("no shortlist manufactured", verdict["shortlist"] == [], verdict["shortlist"], [], "verdict")
    audit.check("no admitted microscopic survivor", verdict["admitted_microscopic_survivors"] == [], verdict["admitted_microscopic_survivors"], [], "verdict")
    audit.check("full Pre-A evidence remains open", verdict["full_pre_a_evidence_complete"] is False, verdict["full_pre_a_evidence_complete"], False, "scope")
    audit.check("Pre-A exit remains open", verdict["pre_a_exit_conditions_met"] is False, verdict["pre_a_exit_conditions_met"], False, "scope")

    false_scope_keys = (
        "current_round1_winner",
        "current_round1_shortlist",
        "current_admitted_microscopic_survivor",
        "full_pre_a_evidence_complete",
        "physical_functional_selected",
        "physical_vacuum_selected",
        "common_real_time_dynamics",
        "continuum_limit",
        "physical_empty_reference",
        "c6_closed",
        "a13_t050_or_sector_a_closed",
    )
    false_scope_values = {key: manifest["scope"][key] for key in false_scope_keys}
    audit.check("all downstream scope flags remain false", not any(false_scope_values.values()), false_scope_values, "all false", "scope")
    no_overclaim = manifest["no_overclaim"]
    required_boundaries = ["not evidence that every possible", "does not complete", "physical law or vacuum", "Sector A or Pre-A"]
    audit.check("explicit no-overclaim boundary", all(fragment in no_overclaim for fragment in required_boundaries), required_boundaries, "all present", "scope")

    source_paths = [SCRIPT, EVIDENCE_SOURCE, EVIDENCE_FREEZE, ADMISSION_FREEZE, MANIFEST, *provenance_paths]
    passed = len(audit.rows)
    return {
        "schema": "tect/pre-a-round1-frozen-quadratic-causal-admission-triage-independent-result/1.0",
        "script_version": __version__,
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "summary": {"passed": passed, "failed": 0, "total": passed},
        "derived": {
            "M2_node_hessian": m2["hessian"],
            "M2_leading_kernel": m2["leading_kernel"],
            "M2_speed_squared": m2["speed_squared"],
            "visible_prediction": str(predicted),
            "visible_target_interval": [str(lower), str(upper)],
            "scaling_rows": prediction["scaling_rows"],
            "round1_outcome": verdict["outcome"],
        },
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in source_paths
        },
        "assertions": audit.rows,
    }


def self_test_exact_engine() -> None:
    x = ExactLaurent.variable(3)
    expanded = (x + 1) ** 3
    expected = ExactLaurent(
        {
            (0, 0, 0, 0, 0, 0): Fraction(1),
            (0, 0, 0, 1, 0, 0): Fraction(3),
            (0, 0, 0, 2, 0, 0): Fraction(3),
            (0, 0, 0, 3, 0, 0): Fraction(1),
        }
    )
    if expanded != expected or expanded.derivative(3).derivative(3).at_zero_momentum() != 6:
        raise AssertionError("exact Laurent engine self-test failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    self_test_exact_engine()
    payload = run()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"PASS {summary['passed']}/{summary['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
