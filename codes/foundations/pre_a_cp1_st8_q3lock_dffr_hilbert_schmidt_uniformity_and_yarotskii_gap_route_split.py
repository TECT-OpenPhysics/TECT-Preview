#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.4 route-split package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-dffr-hilbert-schmidt-uniformity-and-yarotskii-gap-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = (
    "PA-CP1-ST8-Q3LOCK-CONDITIONAL-M-UNIFORM-DFFR-HILBERT-SCHMIDT-SIMULTANEOUS-ENTRY-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-FIXED-RITZ-YAROTSKII-RELATIVE-SPLIT-AND-CONDITIONAL-PHASEWISE-GNS-GAP-REDUCTION",
)
NEGATIVE = "NG-2026-08-13-PRE-A-ST8-Q3LOCK-UNIFORM-RELATIVE-FORM-AND-OPERATOR-BLOCK-BOUNDS-AUTOMATIC-M-UNIFORM-DFFR-HILBERT-SCHMIDT-ENTRY"

# Labelled simultaneous-entry inputs.
LAMBDA_ZERO = sp.Rational(1, 2)
N_REF = sp.Integer(1)
KAPPA_ZERO = sp.Integer(2)
GROWTH_C = sp.Integer(1)
OFFSET_C = sp.Integer(1)
EPSILON_STAR = sp.Rational(1, 4)
KAPPA_BAR_STAR = sp.Rational(1, 2)
ENTRY_N = sp.Integer(5)
A_LL = sp.Integer(2)
A_LH = sp.Integer(3)
A_HL = sp.Integer(3)
A_HH = sp.Integer(5)
THERMAL_MULTIPLIER = sp.Integer(6)

# Labelled relative-split inputs.
SPLIT_N = sp.Integer(10)
GROUND_MULTIPLICITY = sp.Integer(2)
LOCAL_GAP = sp.Integer(16)
ALPHA_POWER = sp.Integer(2)
BETA_POWER = sp.Integer(3)
GROUP_SIZE = sp.Integer(3)

# Labelled Hilbert--Schmidt obstruction inputs.
HS_N = sp.Integer(5)
HIGH_MULTIPLICITY = sp.Integer(4)
LOW_RANK = sp.Integer(2)
HS_KAPPA = sp.Integer(1)
SUPPORT_SIZE = sp.Integer(2)
HS_J = sp.Integer(1)
HS_PENALTY_POWER = sp.Integer(2)


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


def exact_text(value: sp.Expr) -> str:
    return str(sp.factor(value)).replace("**", "^").replace(" ", "")


def simultaneous_fixture() -> tuple[dict[str, Any], dict[str, sp.Expr]]:
    k_n = sp.simplify(KAPPA_ZERO + GROWTH_C * ENTRY_N**2 - OFFSET_C)
    low_low = sp.simplify(LAMBDA_ZERO * A_LL / (KAPPA_ZERO * ENTRY_N**2))
    paired = sp.simplify(
        LAMBDA_ZERO * sp.sqrt(A_LH * A_HL / (ENTRY_N**2 * KAPPA_ZERO * k_n))
    )
    high_high = sp.simplify(LAMBDA_ZERO * A_HH / k_n)
    high_low = sp.simplify(LAMBDA_ZERO * A_HL / (ENTRY_N * k_n))
    low_high = sp.simplify(LAMBDA_ZERO * A_LH / (ENTRY_N * k_n))
    beta = sp.simplify(THERMAL_MULTIPLIER * sp.log(2))
    thermal = sp.simplify(sp.exp(-beta * KAPPA_BAR_STAR))
    maximum = max(low_low, paired, high_high, high_low, low_high, thermal)
    inputs = {
        "lambda": exact_text(LAMBDA_ZERO),
        "N_ref": exact_text(N_REF),
        "kappa_0": exact_text(KAPPA_ZERO),
        "c": exact_text(GROWTH_C),
        "C_offset": exact_text(OFFSET_C),
        "epsilon_star": exact_text(EPSILON_STAR),
        "kappa_bar_star": exact_text(KAPPA_BAR_STAR),
        "N": exact_text(ENTRY_N),
        "A_ll": exact_text(A_LL),
        "A_lh": exact_text(A_LH),
        "A_hl": exact_text(A_HL),
        "A_hh": exact_text(A_HH),
        "beta": exact_text(beta),
    }
    derived = {
        "K_N": exact_text(k_n),
        "low_low": exact_text(low_low),
        "paired": exact_text(paired),
        "high_high": exact_text(high_high),
        "high_low": exact_text(high_low),
        "low_high": exact_text(low_high),
        "thermal": exact_text(thermal),
        "maximum": exact_text(maximum),
        "strict_entry": bool(maximum < EPSILON_STAR),
    }
    n = sp.symbols("N", positive=True)
    symbolic_k = KAPPA_ZERO + GROWTH_C * n**2 - OFFSET_C
    symbolic = {
        "low_low": LAMBDA_ZERO * A_LL / (KAPPA_ZERO * n**2),
        "paired": LAMBDA_ZERO * sp.sqrt(A_LH * A_HL / (n**2 * KAPPA_ZERO * symbolic_k)),
        "high_high": LAMBDA_ZERO * A_HH / symbolic_k,
        "high_low": LAMBDA_ZERO * A_HL / (n * symbolic_k),
        "low_high": LAMBDA_ZERO * A_LH / (n * symbolic_k),
    }
    return {"inputs": inputs, "derived": derived}, symbolic


def split_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    n = SPLIT_N
    alpha = n ** (-ALPHA_POWER)
    beta_edge = n ** (-BETA_POWER)
    epsilon = sp.simplify(GROUP_SIZE * beta_edge)
    h_diagonal = (sp.Integer(0), sp.Integer(0), LOCAL_GAP, n**2)
    positive = [value for value in h_diagonal if value > 0]
    gap = min(positive)
    ceiling = max(h_diagonal)
    a = sp.simplify(alpha + epsilon / gap)
    cross = sp.sqrt(sp.simplify(epsilon * (alpha * ceiling + epsilon)))
    b = sp.factor(epsilon + 2 * cross)

    b_diagonal = tuple(sp.simplify(alpha * value + epsilon) for value in h_diagonal)
    contraction = sp.zeros(len(h_diagonal))
    contraction[0, 0] = 1
    contraction[2, 2] = 1
    contraction[1, 3] = contraction[3, 1] = 1
    square_root_b = sp.diag(*(sp.sqrt(value) for value in b_diagonal))
    perturbation = sp.simplify(square_root_b * contraction * square_root_b)
    pvp_norm = sp.Abs(perturbation[0, 0])
    pvq_norm = sp.Abs(perturbation[1, 3])
    qvq_ratio = sp.simplify(perturbation[2, 2] / gap)
    vb_bound = sp.simplify(pvp_norm + 2 * pvq_norm)

    inputs = {
        "h_diagonal": [exact_text(value if index < GROUND_MULTIPLICITY + 1 else sp.Symbol("N") ** 2)
                       for index, value in enumerate(h_diagonal)],
        "N": exact_text(n),
        "alpha": f"1/N^{exact_text(ALPHA_POWER)}",
        "beta_edge": f"1/N^{exact_text(BETA_POWER)}",
        "group_size": exact_text(GROUP_SIZE),
    }
    derived = {
        "g": exact_text(gap),
        "L": exact_text(ceiling),
        "epsilon": exact_text(epsilon),
        "a": exact_text(a),
        "cross": exact_text(cross),
        "b": exact_text(b),
    }
    witness = {
        "contraction_squared_identity": contraction * contraction == sp.eye(len(h_diagonal)),
        "pvp_norm": pvp_norm,
        "pvq_norm": pvq_norm,
        "qvq_ratio": qvq_ratio,
        "vb_bound": vb_bound,
        "a": a,
        "b": b,
    }
    return {"inputs": inputs, "derived": derived}, witness


def obstruction_fixture() -> tuple[dict[str, Any], dict[str, sp.Expr]]:
    onsite_dimension = HIGH_MULTIPLICITY + LOW_RANK
    p_rank = LOW_RANK**SUPPORT_SIZE
    support_dimension = onsite_dimension**SUPPORT_SIZE
    q_rank = support_dimension - p_rank
    r_rank = HIGH_MULTIPLICITY**SUPPORT_SIZE
    relative_alpha = HS_N ** (-HS_PENALTY_POWER)
    projection_singular_values = [sp.Integer(1)] * int(r_rank) + [sp.Integer(0)] * int(q_rank - r_rank)
    operator_norm = max(projection_singular_values)
    hs_norm = sp.sqrt(sum(value**2 for value in projection_singular_values))
    epsilon_hh = sp.simplify(LAMBDA_ZERO ** (-SUPPORT_SIZE) * hs_norm)
    high_penalty = HS_N**HS_PENALTY_POWER
    entry = sp.simplify(LAMBDA_ZERO * epsilon_hh / (HS_KAPPA + high_penalty))
    inputs = {
        "N": exact_text(HS_N),
        "m": exact_text(HIGH_MULTIPLICITY),
        "J": exact_text(HS_J),
        "onsite_dimension": exact_text(onsite_dimension),
        "low_rank": exact_text(LOW_RANK),
        "lambda": exact_text(LAMBDA_ZERO),
        "support_size": exact_text(SUPPORT_SIZE),
        "kappa": exact_text(HS_KAPPA),
        "D": f"N^{exact_text(HS_PENALTY_POWER)}",
    }
    derived = {
        "P_rank": exact_text(p_rank),
        "Q_rank": exact_text(q_rank),
        "R_rank": exact_text(r_rank),
        "relative_alpha": exact_text(relative_alpha),
        "high_high_operator_norm": exact_text(operator_norm),
        "high_high_HS_norm": exact_text(hs_norm),
        "epsilon_hh": exact_text(epsilon_hh),
        "high_high_entry": exact_text(entry),
        "exceeds_epsilon_star": bool(entry > EPSILON_STAR),
    }
    m, n, kappa = sp.symbols("m N kappa", positive=True)
    symbolic_entry = sp.simplify(
        LAMBDA_ZERO
        * LAMBDA_ZERO ** (-SUPPORT_SIZE)
        * sp.sqrt(m**SUPPORT_SIZE)
        / (kappa + n**HS_PENALTY_POWER)
    )
    limits = {
        "fixed_m_large_n": sp.limit(symbolic_entry, n, sp.oo),
        "fixed_n_large_m": sp.limit(symbolic_entry, m, sp.oo),
    }
    return {"inputs": inputs, "derived": derived}, limits


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    simultaneous, asymptotics = simultaneous_fixture()
    split, split_witness = split_fixture()
    obstruction, obstruction_limits = obstruction_fixture()
    derived = {
        "simultaneous_entry": simultaneous,
        "relative_split": split,
        "hs_obstruction": obstruction,
    }
    audit = Audit()

    audit.check(
        "manifest identity",
        manifest["schema"] == "tect/pre-a-q3lock-dffr-hs-uniformity-yarotskii-gap/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.4"
        and manifest["date"] == "2026-08-13"
        and manifest["exploration_id"] == "EXP-000838"
        and manifest["prior_exploration_id"] == "EXP-000837"
        and manifest["claim_bearing"] is False,
        (manifest["schema"], manifest["version"], manifest["exploration_id"]),
        ("exact schema", "R-167 v3.4", "EXP-000838"),
        "manifest",
    )
    audit.check(
        "manifest scoped topology",
        tuple(manifest["closed_gate_ids"]) == CLOSED
        and manifest["negative_ids"] == [NEGATIVE]
        and len(manifest["open_parent_gate_ids"]) == 5,
        (manifest["closed_gate_ids"], manifest["negative_ids"], len(manifest["open_parent_gate_ids"])),
        (CLOSED, [NEGATIVE], 5),
        "manifest",
    )
    audit.check(
        "uniform N_ref premise",
        "N_ref independent of M" in manifest["conditional_simultaneous_dffr_entry"]["family"]
        and "N>=N_ref" in manifest["conditional_simultaneous_dffr_entry"]["conclusion"],
        manifest["conditional_simultaneous_dffr_entry"]["family"],
        "one common onset",
        "uniformity",
    )
    audit.check(
        "exact fixture agreement",
        derived == manifest["exact_fixture"],
        derived,
        manifest["exact_fixture"],
        "oracle",
    )
    audit.check(
        "simultaneous denominator",
        simultaneous["derived"]["K_N"]
        == exact_text(KAPPA_ZERO + GROWTH_C * ENTRY_N**2 - OFFSET_C),
        simultaneous["derived"]["K_N"],
        exact_text(KAPPA_ZERO + GROWTH_C * ENTRY_N**2 - OFFSET_C),
        "dffr",
    )
    sample_k = KAPPA_ZERO + GROWTH_C * ENTRY_N**2 - OFFSET_C
    nonthermal_values = (
        LAMBDA_ZERO * A_LL / (KAPPA_ZERO * ENTRY_N**2),
        LAMBDA_ZERO * sp.sqrt(A_LH * A_HL / (ENTRY_N**2 * KAPPA_ZERO * sample_k)),
        LAMBDA_ZERO * A_HH / sample_k,
        LAMBDA_ZERO * A_HL / (ENTRY_N * sample_k),
        LAMBDA_ZERO * A_LH / (ENTRY_N * sample_k),
    )
    audit.check(
        "simultaneous five nonthermal formula identities",
        list(simultaneous["derived"].values())[1:6]
        == [exact_text(value) for value in nonthermal_values],
        list(simultaneous["derived"].values())[1:6],
        [exact_text(value) for value in nonthermal_values],
        "dffr",
    )
    audit.check(
        "thermal and strict entry",
        simultaneous["derived"]["thermal"]
        == exact_text(sp.exp(-THERMAL_MULTIPLIER * sp.log(2) * KAPPA_BAR_STAR))
        and simultaneous["derived"]["maximum"]
        == exact_text(
            max(
                *(sp.sympify(value) for value in nonthermal_values),
                sp.exp(-THERMAL_MULTIPLIER * sp.log(2) * KAPPA_BAR_STAR),
            )
        )
        and simultaneous["derived"]["strict_entry"],
        simultaneous["derived"],
        "derived maximum below derived threshold",
        "dffr",
    )
    audit.check(
        "all DFFR majorants vanish",
        all(sp.limit(expr, sp.Symbol("N", positive=True), sp.oo) == 0 for expr in asymptotics.values()),
        asymptotics,
        "all zero limits",
        "dffr",
    )
    audit.check(
        "split spectral data",
        split["derived"]["g"] == exact_text(LOCAL_GAP)
        and split["derived"]["L"] == exact_text(SPLIT_N**2)
        and split["derived"]["epsilon"]
        == exact_text(GROUP_SIZE * SPLIT_N ** (-BETA_POWER)),
        split["derived"],
        "derived gap ceiling and grouped epsilon",
        "split",
    )
    audit.check(
        "split relative coefficient",
        split_witness["qvq_ratio"] == split_witness["a"]
        and exact_text(split_witness["a"]) == split["derived"]["a"],
        split_witness["qvq_ratio"],
        split_witness["a"],
        "split",
    )
    audit.check(
        "split bounded coefficient",
        split_witness["contraction_squared_identity"]
        and split_witness["pvp_norm"] <= GROUP_SIZE * SPLIT_N ** (-BETA_POWER)
        and sp.simplify(split_witness["vb_bound"] - split_witness["b"]) == 0
        and exact_text(split_witness["b"]) == split["derived"]["b"],
        split_witness,
        "contraction and exact triangle bound",
        "split",
    )
    n = sp.symbols("N", positive=True)
    alpha_n = n ** (-ALPHA_POWER)
    epsilon_n = GROUP_SIZE * n ** (-BETA_POWER)
    ceiling_n = n**2
    a_n = alpha_n + epsilon_n / LOCAL_GAP
    b_n = epsilon_n + 2 * sp.sqrt(epsilon_n * (alpha_n * ceiling_n + epsilon_n))
    audit.check(
        "split asymptotic rates",
        sp.limit(n**2 * a_n, n, sp.oo) == 1
        and sp.limit(n ** sp.Rational(3, 2) * b_n, n, sp.oo) == 2 * sp.sqrt(GROUP_SIZE),
        (sp.limit(n**2 * a_n, n, sp.oo), sp.limit(n ** sp.Rational(3, 2) * b_n, n, sp.oo)),
        (1, 2 * sp.sqrt(GROUP_SIZE)),
        "split",
    )
    audit.check(
        "obstruction ranks",
        obstruction["derived"]["P_rank"] == exact_text(LOW_RANK**SUPPORT_SIZE)
        and obstruction["derived"]["Q_rank"]
        == exact_text((HIGH_MULTIPLICITY + LOW_RANK) ** SUPPORT_SIZE - LOW_RANK**SUPPORT_SIZE)
        and obstruction["derived"]["R_rank"] == exact_text(HIGH_MULTIPLICITY**SUPPORT_SIZE),
        obstruction["derived"],
        "tensor ranks",
        "negative",
    )
    audit.check(
        "obstruction positive reference premise",
        HS_N >= 1
        and HIGH_MULTIPLICITY >= 1
        and HS_J > 0
        and "For integers m,N>=1" in manifest["hilbert_schmidt_obstruction"]["spaces"]
        and "Fix J>0" in manifest["hilbert_schmidt_obstruction"]["reference"]
        and "fixed `J>0`" in certificate,
        (HS_N, HIGH_MULTIPLICITY, HS_J),
        "m,N>=1 and J>0",
        "negative",
    )
    audit.check(
        "operator versus Hilbert-Schmidt separation",
        obstruction["derived"]["high_high_operator_norm"]
        == exact_text(max([sp.Integer(1)] * int(HIGH_MULTIPLICITY**SUPPORT_SIZE)))
        and obstruction["derived"]["high_high_HS_norm"] == exact_text(HIGH_MULTIPLICITY),
        obstruction["derived"],
        "operator one and HS multiplicity m",
        "negative",
    )
    audit.check(
        "obstruction criterion entry",
        obstruction["derived"]["epsilon_hh"]
        == exact_text(LAMBDA_ZERO ** (-SUPPORT_SIZE) * sp.sqrt(HIGH_MULTIPLICITY**SUPPORT_SIZE))
        and obstruction["derived"]["high_high_entry"]
        == exact_text(
            LAMBDA_ZERO
            * LAMBDA_ZERO ** (-SUPPORT_SIZE)
            * sp.sqrt(HIGH_MULTIPLICITY**SUPPORT_SIZE)
            / (HS_KAPPA + HS_N**HS_PENALTY_POWER)
        )
        and obstruction["derived"]["exceeds_epsilon_star"],
        obstruction["derived"],
        "derived entry above epsilon star",
        "negative",
    )
    audit.check(
        "obstruction two limit orders",
        obstruction_limits["fixed_m_large_n"] == 0
        and obstruction_limits["fixed_n_large_m"] == sp.oo,
        obstruction_limits,
        {"fixed_m_large_n": 0, "fixed_n_large_m": sp.oo},
        "negative",
    )
    theorem_tokens = (
        "DFFR Theorem 5.2",
        "actual Hilbert--Schmidt constants in DFFR (5.21)",
        "one integer `N_ref` independent of `M`",
        "a=alpha+epsilon/g",
        "b=epsilon+2 sqrt[epsilon(alpha L+epsilon)]",
        "phasewise GNS implementing spectral gap",
        "are not automatically the Yarotskii branches",
    )
    audit.check(
        "certificate theorem contract",
        all(token in certificate for token in theorem_tokens),
        [token for token in theorem_tokens if token not in certificate],
        [],
        "certificate",
    )
    boundary_tokens = (
        "no actual M-uniform DFFR entry for Q3",
        "no Yarotskii rectangle",
        "no DFFR/Yarotskii branch identity",
        "All five active parent gates remain OPEN",
        "No v3.4 PDF is issued",
    )
    audit.check(
        "certificate no-overclaim contract",
        all(token in certificate for token in boundary_tokens),
        [token for token in boundary_tokens if token not in certificate],
        [],
        "certificate",
    )
    audit.check(
        "literature scope separation",
        "finite-dimensional onsite spin space" in certificate
        and "possibly infinite-dimensional onsite spaces" in certificate
        and "do not establish zero-source two-phase coexistence" in certificate,
        "three source scopes",
        "distinct DFFR, Yarotsky and Yarotskii roles",
        "literature",
    )
    audit.check(
        "nonduplicate negative mechanism",
        "operator norm is exactly one" in certificate
        and "not the shrinking-radius fixture" in certificate,
        "HS multiplicity only",
        "not SW operator growth or theorem-radius shrinkage",
        "negative",
    )
    audit.check(
        "proof-first lifecycle",
        manifest["checkpoint_synthesis"]["pdf_issued"] is False
        and manifest["formal_integration_contract"]["event_id"] == 630
        and manifest["formal_integration_contract"]["theorem_map_version"] == "1.26.0",
        (manifest["checkpoint_synthesis"], manifest["formal_integration_contract"]),
        "no PDF and staged-first event 630",
        "lifecycle",
    )

    if not staged:
        texts = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        required = CLOSED + (NEGATIVE, "EXP-000838", "R-167 v3.4")
        audit.check(
            "formal authority aggregate",
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
    print(f"R-167 v3.4 PRIMARY PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
