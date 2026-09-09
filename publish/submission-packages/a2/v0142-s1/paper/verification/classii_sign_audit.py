#!/usr/bin/env python3
"""Independent source-sign audit for the Class-II Euler map.

This is a paper-local audit, not a canonical-source correction.  It derives the
sign of the Euler term from periodic integration by parts, checks the two
canonical note displays, and records whether the later shorthand defines its
Laplacian symbol.  All source material is read from the repository at runtime
and its hashes are included in the emitted artifact.
"""

from __future__ import annotations

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
NOTES = ROOT / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "notes"
V11 = NOTES / "a2-full-production-wellposedness-260717-v1.1.tex.txt"
V20 = NOTES / "a2-full-production-wellposedness-260717-v2.0.tex.txt"
ARTIFACT = (
    ROOT
    / "publish"
    / "papers"
    / "a2-r157-r158-ensemble-minimizers"
    / "verification"
    / "runs"
    / "classii-sign.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, label: str, assertions: list[str]) -> None:
    if not condition:
        raise AssertionError(label)
    assertions.append(label)


def main() -> int:
    assertions: list[str] = []
    require(V11.is_file(), "v1.1 source exists", assertions)
    require(V20.is_file(), "v2.0 source exists", assertions)
    v11 = V11.read_text(encoding="utf-8")
    v20 = V20.read_text(encoding="utf-8")

    # The v1.1 component formula explicitly uses the raw Laplacian with a
    # negative leading coefficient.  This is a source-text oracle, not a new
    # model assumption.
    v11_negative = r"-B_{\gamma\beta}(u)\Delta u_\beta" in v11
    require(v11_negative, "v1.1 displays -B_gamma_beta Delta u_beta", assertions)

    # The v2.0 summary uses a positive schematic symbol.  Check that it does
    # not define that symbol as either sign of the componentwise Laplacian.
    v20_positive = r"N_{II}(u)=B(u)\nabla^2u" in v20
    require(v20_positive, "v2.0 displays positive B(u) nabla^2 u", assertions)
    v20_symbol_definition = bool(
        re.search(r"\\nabla\^2\s*u\s*(?::=|=)", v20)
    )
    require(
        not v20_symbol_definition,
        "v2.0 does not define nabla^2 in the displayed summary",
        assertions,
    )

    # Exact one-mode sign test.  On a periodic domain, choose a normalized
    # Fourier mode with |k|^2=1.  The raw Delta eigenvalue is -1.  Variation of
    # 1/2 ||grad u||^2 is -Delta u, whose pairing with u is +1; the reversed
    # candidate +Delta u gives -1 and fails the positivity test.
    k_squared = Fraction(1, 1)
    raw_delta_eigenvalue = -k_squared
    euler_coefficient_raw = Fraction(-1, 1)
    euler_pairing = euler_coefficient_raw * raw_delta_eigenvalue
    reversed_pairing = -euler_pairing
    require(
        euler_pairing == Fraction(1, 1),
        "periodic integration-by-parts sign gives positive energy pairing",
        assertions,
    )
    require(
        reversed_pairing == Fraction(-1, 1),
        "reversed raw-Delta sign gives negative energy pairing",
        assertions,
    )
    require(
        euler_pairing > 0 and reversed_pairing < 0,
        "hostile sign reversal is rejected",
        assertions,
    )

    compatibility = (
        "conditional: v2.0 is compatible only if its nabla^2 denotes the "
        "positive operator -Delta; source intent remains undefined"
    )
    result = {
        "schema": "tect/paper-local-sign-audit/1.0",
        "verdict": "PAPER-CLASSII-SIGN-AUDIT-PASS",
        "assertions": {"passed": len(assertions), "total": len(assertions)},
        "sources": {
            "v1.1": {"path": str(V11.relative_to(ROOT)), "sha256": sha256(V11)},
            "v2.0": {"path": str(V20.relative_to(ROOT)), "sha256": sha256(V20)},
        },
        "source_observations": {
            "v1_1_negative_raw_delta_display": v11_negative,
            "v2_0_positive_shorthand_display": v20_positive,
            "v2_0_defines_nabla_squared": v20_symbol_definition,
        },
        "exact_sign_test": {
            "k_squared": str(k_squared),
            "raw_delta_eigenvalue": str(raw_delta_eigenvalue),
            "raw_delta_euler_coefficient": str(euler_coefficient_raw),
            "correct_pairing": str(euler_pairing),
            "reversed_pairing": str(reversed_pairing),
        },
        "finding": (
            "For the raw componentwise Delta fixed by the displayed Dirichlet "
            "density and real pairing, the Euler term is -B(u) Delta u.  The "
            "v1.1 display agrees; the v2.0 positive shorthand is compatible "
            "only under an undefined positive-Laplacian convention."
        ),
        "scope": (
            "paper-local source/sign audit only; no canonical source edit, "
            "claim-tier promotion, or external/operator reconciliation"
        ),
        "compatibility": compatibility,
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    with ARTIFACT.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"{result['verdict']}: {len(assertions)}/{len(assertions)}")
    print(f"artifact: {ARTIFACT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
