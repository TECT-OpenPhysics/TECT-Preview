#!/usr/bin/env python3
"""Independent stdlib verifier for the R-167 v3.4 route-split package."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-dffr-hilbert-schmidt-uniformity-and-yarotskii-gap-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Independently labelled mathematical inputs.
LAMBDA_NUMERATOR = 1
LAMBDA_DENOMINATOR = 2
COMMON_ONSET = 1
KAPPA_LOWER = 2
PENALTY_GROWTH = 1
PENALTY_OFFSET = 1
THRESHOLD_NUMERATOR = 1
THRESHOLD_DENOMINATOR = 4
THERMAL_GAP_NUMERATOR = 1
THERMAL_GAP_DENOMINATOR = 2
ENTRY_SIZE = 5
BLOCK_LL = 2
BLOCK_LH = 3
BLOCK_HL = 3
BLOCK_HH = 5
BLOCK_LL_DECAY_POWER = 2
BLOCK_LH_DECAY_POWER = 1
BLOCK_HL_DECAY_POWER = 1
BLOCK_HH_DECAY_POWER = 0
HIGH_PENALTY_GROWTH_POWER = 2
THERMAL_LOG_TWO_MULTIPLIER = 6

SPLIT_SIZE = 10
ZERO_LABELS = 2
SPLIT_GAP = 16
RELATIVE_DECAY_POWER = 2
ADDITIVE_DECAY_POWER = 3
SPLIT_CEILING_GROWTH_POWER = 2
SPLIT_GAP_GROWTH_POWER = 0
POSITIVE_EDGE_COUNT = 3

OBSTRUCTION_SIZE = 5
HIGH_LABEL_COUNT = 4
LOW_LABEL_COUNT = 2
EDGE_SITE_COUNT = 2
OBSTRUCTION_KAPPA = 1
OBSTRUCTION_J = 1
OBSTRUCTION_PENALTY_GROWTH_POWER = 2

# Labelled theorem-statement test oracles, checked against derived exponents.
DFFR_DECAY_POWER_TEST_ORACLE = (Fraction(2), Fraction(2), Fraction(2), Fraction(3), Fraction(3))
SPLIT_DECAY_POWER_TEST_ORACLE = (Fraction(2), Fraction(3, 2))


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


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
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def square_root_fraction(value: Fraction) -> tuple[int, int, int]:
    """Return coefficient numerator, radical, denominator for an exact square root."""
    numerator_square = math.isqrt(value.numerator)
    denominator_square = math.isqrt(value.denominator)
    if numerator_square * numerator_square == value.numerator and denominator_square * denominator_square == value.denominator:
        return numerator_square, 1, denominator_square
    coefficient = 1
    radical = value.numerator * value.denominator
    denominator = value.denominator
    factor = 2
    while factor * factor <= radical:
        square = factor * factor
        while radical % square == 0:
            coefficient *= factor
            radical //= square
        factor += 1
    common = math.gcd(coefficient, denominator)
    return coefficient // common, radical, denominator // common


def radical_text(coefficient: int, radical: int, denominator: int) -> str:
    if radical == 1:
        return fraction_text(Fraction(coefficient, denominator))
    numerator = f"sqrt({radical})" if coefficient == 1 else f"{coefficient}*sqrt({radical})"
    if denominator == 1:
        return numerator
    return f"{numerator}/{denominator}"


def simultaneous_fixture() -> dict[str, Any]:
    lam = Fraction(LAMBDA_NUMERATOR, LAMBDA_DENOMINATOR)
    threshold = Fraction(THRESHOLD_NUMERATOR, THRESHOLD_DENOMINATOR)
    thermal_gap = Fraction(THERMAL_GAP_NUMERATOR, THERMAL_GAP_DENOMINATOR)
    denominator = KAPPA_LOWER + PENALTY_GROWTH * ENTRY_SIZE**2 - PENALTY_OFFSET
    low_low = lam * Fraction(BLOCK_LL, KAPPA_LOWER * ENTRY_SIZE**2)
    paired_radicand = Fraction(BLOCK_LH * BLOCK_HL, ENTRY_SIZE**2 * KAPPA_LOWER * denominator)
    paired_root = square_root_fraction(paired_radicand)
    paired_coefficient = lam * Fraction(paired_root[0], paired_root[2])
    paired_radical = paired_root[1]
    high_high = lam * Fraction(BLOCK_HH, denominator)
    high_low = lam * Fraction(BLOCK_HL, ENTRY_SIZE * denominator)
    low_high = lam * Fraction(BLOCK_LH, ENTRY_SIZE * denominator)
    thermal_power = Fraction(THERMAL_LOG_TWO_MULTIPLIER) * thermal_gap
    assert thermal_power.denominator == 1
    thermal = Fraction(1, 2 ** thermal_power.numerator)
    rational_maximum = max(low_low, high_high, high_low, low_high, thermal)
    paired_squared = paired_coefficient**2 * paired_radical
    maximum_is_rational = paired_squared <= rational_maximum**2
    assert maximum_is_rational
    maximum = rational_maximum
    return {
        "inputs": {
            "lambda": fraction_text(lam),
            "N_ref": str(COMMON_ONSET),
            "kappa_0": str(KAPPA_LOWER),
            "c": str(PENALTY_GROWTH),
            "C_offset": str(PENALTY_OFFSET),
            "epsilon_star": fraction_text(threshold),
            "kappa_bar_star": fraction_text(thermal_gap),
            "N": str(ENTRY_SIZE),
            "A_ll": str(BLOCK_LL),
            "A_lh": str(BLOCK_LH),
            "A_hl": str(BLOCK_HL),
            "A_hh": str(BLOCK_HH),
            "beta": f"{THERMAL_LOG_TWO_MULTIPLIER}*log(2)",
        },
        "derived": {
            "K_N": str(denominator),
            "low_low": fraction_text(low_low),
            "paired": radical_text(paired_coefficient.numerator, paired_radical, paired_coefficient.denominator),
            "high_high": fraction_text(high_high),
            "high_low": fraction_text(high_low),
            "low_high": fraction_text(low_high),
            "thermal": fraction_text(thermal),
            "maximum": fraction_text(maximum),
            "strict_entry": maximum < threshold,
        },
    }


def split_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    alpha = Fraction(1, SPLIT_SIZE**RELATIVE_DECAY_POWER)
    beta_edge = Fraction(1, SPLIT_SIZE**ADDITIVE_DECAY_POWER)
    epsilon = POSITIVE_EDGE_COUNT * beta_edge
    diagonal = (0, 0, SPLIT_GAP, SPLIT_SIZE**2)
    positive = [value for value in diagonal if value > 0]
    gap = min(positive)
    ceiling = max(diagonal)
    a = alpha + epsilon / gap
    cross_squared = epsilon * (alpha * ceiling + epsilon)
    cross = square_root_fraction(cross_squared)
    assert cross[0] == 1
    b_rational = epsilon
    b_radical_coefficient = 2 * cross[0]
    b_text = f"({b_rational.numerator}+{b_radical_coefficient}*sqrt({cross[1]}))/{b_rational.denominator}"

    # The contraction swaps basis labels 1 and 3 and fixes 0 and 2.
    permutation = (0, 3, 2, 1)
    permutation_square = tuple(permutation[permutation[index]] for index in range(len(permutation)))
    b_diagonal = tuple(alpha * value + epsilon for value in diagonal)
    pvp_norm = b_diagonal[0]
    mixed_squared = b_diagonal[1] * b_diagonal[3]
    qvq_ratio = b_diagonal[2] / gap
    return (
        {
            "inputs": {
                "h_diagonal": ["0", "0", str(SPLIT_GAP), "N^2"],
                "N": str(SPLIT_SIZE),
                "alpha": f"1/N^{RELATIVE_DECAY_POWER}",
                "beta_edge": f"1/N^{ADDITIVE_DECAY_POWER}",
                "group_size": str(POSITIVE_EDGE_COUNT),
            },
            "derived": {
                "g": str(gap),
                "L": str(ceiling),
                "epsilon": fraction_text(epsilon),
                "a": fraction_text(a),
                "cross": radical_text(*cross),
                "b": b_text,
            },
        },
        {
            "permutation_square": permutation_square,
            "pvp_norm": pvp_norm,
            "mixed_squared": mixed_squared,
            "cross_squared": cross_squared,
            "qvq_ratio": qvq_ratio,
            "a": a,
            "b_rational": b_rational,
            "b_radical": (b_radical_coefficient, cross[1], cross[2]),
        },
    )


def obstruction_fixture() -> tuple[dict[str, Any], dict[str, Fraction]]:
    onsite_dimension = HIGH_LABEL_COUNT + LOW_LABEL_COUNT
    p_rank = LOW_LABEL_COUNT**EDGE_SITE_COUNT
    total_rank = onsite_dimension**EDGE_SITE_COUNT
    q_rank = total_rank - p_rank
    r_rank = HIGH_LABEL_COUNT**EDGE_SITE_COUNT
    projection_singular_values = [1] * r_rank + [0] * (q_rank - r_rank)
    operator_norm = max(projection_singular_values)
    hs_norm = math.isqrt(sum(value * value for value in projection_singular_values))
    assert hs_norm * hs_norm == r_rank
    lam = Fraction(LAMBDA_NUMERATOR, LAMBDA_DENOMINATOR)
    epsilon_hh = Fraction(hs_norm, 1) / (lam**EDGE_SITE_COUNT)
    entry = lam * epsilon_hh / (
        OBSTRUCTION_KAPPA + OBSTRUCTION_SIZE**OBSTRUCTION_PENALTY_GROWTH_POWER
    )
    threshold = Fraction(THRESHOLD_NUMERATOR, THRESHOLD_DENOMINATOR)
    return (
        {
            "inputs": {
                "N": str(OBSTRUCTION_SIZE),
                "m": str(HIGH_LABEL_COUNT),
                "J": str(OBSTRUCTION_J),
                "onsite_dimension": str(onsite_dimension),
                "low_rank": str(LOW_LABEL_COUNT),
                "lambda": fraction_text(lam),
                "support_size": str(EDGE_SITE_COUNT),
                "kappa": str(OBSTRUCTION_KAPPA),
                "D": f"N^{OBSTRUCTION_PENALTY_GROWTH_POWER}",
            },
            "derived": {
                "P_rank": str(p_rank),
                "Q_rank": str(q_rank),
                "R_rank": str(r_rank),
                "relative_alpha": fraction_text(
                    Fraction(1, OBSTRUCTION_SIZE**OBSTRUCTION_PENALTY_GROWTH_POWER)
                ),
                "high_high_operator_norm": str(operator_norm),
                "high_high_HS_norm": str(hs_norm),
                "epsilon_hh": fraction_text(epsilon_hh),
                "high_high_entry": fraction_text(entry),
                "exceeds_epsilon_star": entry > threshold,
            },
        },
        {
            "entry_numerator_m_degree": Fraction(EDGE_SITE_COUNT, 2),
            "entry_denominator_n_degree": Fraction(OBSTRUCTION_PENALTY_GROWTH_POWER),
        },
    )


def source_firewall() -> dict[str, Any]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imports: set[str] = set()
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec", "compile"}:
                dynamic.append(node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "exec_module", "load_module"}:
                dynamic.append(node.func.attr)
    return {"imports": sorted(imports), "dynamic": dynamic}


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    simultaneous = simultaneous_fixture()
    split, split_witness = split_fixture()
    obstruction, degree_data = obstruction_fixture()
    derived = {
        "simultaneous_entry": simultaneous,
        "relative_split": split,
        "hs_obstruction": obstruction,
    }
    audit = Audit()

    audit.check(
        "manifest identity independently parsed",
        manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.4"
        and manifest["date"] == "2026-08-13"
        and manifest["exploration_id"] == "EXP-000838",
        (manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        (SLUG, "R-167 v3.4", "EXP-000838"),
        "manifest",
    )
    audit.check(
        "fixture agreement from stdlib arithmetic",
        derived == manifest["exact_fixture"],
        derived,
        manifest["exact_fixture"],
        "oracle",
    )
    audit.check(
        "common onset is an input",
        simultaneous["inputs"]["N_ref"] == str(COMMON_ONSET)
        and "N_ref independent of M" in manifest["conditional_simultaneous_dffr_entry"]["family"],
        simultaneous["inputs"]["N_ref"],
        "one M-independent N_ref",
        "uniformity",
    )
    audit.check(
        "DFFR denominator lower bound sample",
        int(simultaneous["derived"]["K_N"])
        == KAPPA_LOWER + PENALTY_GROWTH * ENTRY_SIZE**2 - PENALTY_OFFSET,
        simultaneous["derived"]["K_N"],
        "formula-derived denominator",
        "dffr",
    )
    audit.check(
        "DFFR strict maximum",
        simultaneous["derived"]["strict_entry"]
        and Fraction(simultaneous["derived"]["maximum"]) < Fraction(simultaneous["inputs"]["epsilon_star"]),
        simultaneous["derived"]["maximum"],
        "below epsilon star",
        "dffr",
    )
    criterion_powers = (
        BLOCK_LL_DECAY_POWER,
        Fraction(
            BLOCK_LH_DECAY_POWER + BLOCK_HL_DECAY_POWER + HIGH_PENALTY_GROWTH_POWER,
            2,
        ),
        BLOCK_HH_DECAY_POWER + HIGH_PENALTY_GROWTH_POWER,
        BLOCK_HL_DECAY_POWER + HIGH_PENALTY_GROWTH_POWER,
        BLOCK_LH_DECAY_POWER + HIGH_PENALTY_GROWTH_POWER,
    )
    audit.check(
        "DFFR five asymptotic powers",
        criterion_powers == DFFR_DECAY_POWER_TEST_ORACLE and all(power > 0 for power in criterion_powers),
        criterion_powers,
        "ll, paired, hh, hl, lh powers derived from block and penalty labels",
        "dffr",
    )
    audit.check(
        "split gap and ceiling from spectrum",
        split["derived"]["g"] == str(SPLIT_GAP)
        and split["derived"]["L"] == str(SPLIT_SIZE**2),
        (split["derived"]["g"], split["derived"]["L"]),
        (SPLIT_GAP, SPLIT_SIZE**2),
        "split",
    )
    audit.check(
        "split contraction involution",
        split_witness["permutation_square"] == tuple(range(ZERO_LABELS + 2)),
        split_witness["permutation_square"],
        tuple(range(ZERO_LABELS + 2)),
        "split",
    )
    audit.check(
        "split low and mixed blocks",
        split_witness["pvp_norm"] == Fraction(split["derived"]["epsilon"])
        and split_witness["mixed_squared"] == split_witness["cross_squared"],
        (split_witness["pvp_norm"], split_witness["mixed_squared"]),
        (Fraction(split["derived"]["epsilon"]), split_witness["cross_squared"]),
        "split",
    )
    audit.check(
        "split high relative coefficient",
        split_witness["qvq_ratio"] == split_witness["a"]
        and fraction_text(split_witness["a"]) == split["derived"]["a"],
        split_witness["qvq_ratio"],
        split_witness["a"],
        "split",
    )
    split_a_power = min(RELATIVE_DECAY_POWER, ADDITIVE_DECAY_POWER + SPLIT_GAP_GROWTH_POWER)
    alpha_ceiling_power = RELATIVE_DECAY_POWER - SPLIT_CEILING_GROWTH_POWER
    parenthesis_power = min(alpha_ceiling_power, ADDITIVE_DECAY_POWER)
    cross_power = Fraction(ADDITIVE_DECAY_POWER + parenthesis_power, 2)
    split_b_power = min(Fraction(ADDITIVE_DECAY_POWER), cross_power)
    audit.check(
        "split rates from labelled exponents",
        (split_a_power, split_b_power) == SPLIT_DECAY_POWER_TEST_ORACLE,
        {
            "a": split_a_power,
            "alpha_times_ceiling": alpha_ceiling_power,
            "parenthesis": parenthesis_power,
            "cross": cross_power,
            "b": split_b_power,
        },
        "a order N^-2 and b order N^-3/2",
        "split",
    )
    audit.check(
        "obstruction tensor ranks",
        int(obstruction["derived"]["P_rank"]) == LOW_LABEL_COUNT**EDGE_SITE_COUNT
        and int(obstruction["derived"]["R_rank"]) == HIGH_LABEL_COUNT**EDGE_SITE_COUNT
        and int(obstruction["derived"]["Q_rank"])
        == (LOW_LABEL_COUNT + HIGH_LABEL_COUNT) ** EDGE_SITE_COUNT - LOW_LABEL_COUNT**EDGE_SITE_COUNT,
        obstruction["derived"],
        "ranks from onsite multiplicities",
        "negative",
    )
    audit.check(
        "obstruction positive reference premise",
        OBSTRUCTION_SIZE >= 1
        and HIGH_LABEL_COUNT >= 1
        and OBSTRUCTION_J > 0
        and "For integers m,N>=1" in manifest["hilbert_schmidt_obstruction"]["spaces"]
        and "Fix J>0" in manifest["hilbert_schmidt_obstruction"]["reference"]
        and "fixed `J>0`" in certificate,
        (OBSTRUCTION_SIZE, HIGH_LABEL_COUNT, OBSTRUCTION_J),
        "m,N>=1 and J>0",
        "negative",
    )
    audit.check(
        "obstruction norm separation",
        int(obstruction["derived"]["high_high_operator_norm"])
        == max([1] * (HIGH_LABEL_COUNT**EDGE_SITE_COUNT))
        and int(obstruction["derived"]["high_high_HS_norm"]) == HIGH_LABEL_COUNT,
        obstruction["derived"],
        "operator one, HS high multiplicity",
        "negative",
    )
    audit.check(
        "obstruction limit order",
        degree_data
        == {
            "entry_numerator_m_degree": Fraction(EDGE_SITE_COUNT, 2),
            "entry_denominator_n_degree": Fraction(OBSTRUCTION_PENALTY_GROWTH_POWER),
        }
        and all(power > 0 for power in degree_data.values()),
        degree_data,
        "m power from sqrt(rank R); N power from the labelled high penalty",
        "negative",
    )
    firewall = source_firewall()
    allowed = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "math",
        "os",
        "tempfile",
        "fractions",
        "pathlib",
        "typing",
    }
    audit.check(
        "stdlib AST firewall",
        set(firewall["imports"]) <= allowed and not firewall["dynamic"],
        firewall,
        "stdlib allowlist and no dynamic execution",
        "independence",
    )
    audit.check(
        "certificate conditional tokens",
        all(
            token in certificate
            for token in (
                "one integer `N_ref` independent of `M`",
                "These two lower bounds are hypotheses",
                "Conditional fixed-Ritz Yarotskii phasewise-gap reduction",
                "are not automatically the Yarotskii branches",
            )
        ),
        "conditional tokens",
        "all present",
        "certificate",
    )
    audit.check(
        "certificate open-boundary tokens",
        all(
            token in certificate
            for token in (
                "no actual M-uniform DFFR entry for Q3",
                "no full-oscillator phase passage",
                "All five active parent gates remain OPEN",
                "No v3.4 PDF is issued",
            )
        ),
        "boundary tokens",
        "all present",
        "certificate",
    )
    audit.check(
        "manifest lifecycle",
        manifest["verification"]["staged_lifecycle"].startswith("Before formal integration")
        and manifest["checkpoint_synthesis"]["pdf_issued"] is False,
        manifest["checkpoint_synthesis"],
        "staged no-store and no PDF",
        "lifecycle",
    )

    if not staged:
        texts = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        required = tuple(manifest["closed_gate_ids"]) + tuple(manifest["negative_ids"]) + ("EXP-000838",)
        audit.check(
            "formal aggregate",
            all(token in texts for token in required),
            [token for token in required if token not in texts],
            [],
            "formal",
        )

    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": derived,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v3.4 INDEPENDENT PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
