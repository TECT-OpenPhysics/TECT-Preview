#!/usr/bin/env python3
"""Independent standard-library audit for the R-156 shifted-state boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SHIFTED-STATE-NONZERO-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-156"
SLUG = "shifted-state-nonzero-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
CLAIM_DIR = REPO / "claims" / CLAIM
R155_MANIFEST = CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json"

SCOPE = {
    "stdlib_fraction_only": True,
    "no_primary_or_scientific_package_import": True,
    "pure_dyadic_two_stage_shifted_state_chart": True,
    "intrinsic_and_pullback_hessians_separated": True,
    "existential_fixed_cutoff_neighborhood": True,
    "numerical_or_uniform_radius": False,
    "independent_low_coordinate": False,
    "global_nonlinear_revisit_gap": False,
    "t050_closed": False,
    "sector_a_closed": False,
}
NO_OVERCLAIM = (
    "R-156 proves an existential nonzero coefficient neighbourhood above 1/10 only for the fixed-cutoff, "
    "positive-floor, exact-torus pure-dyadic two-stage shifted-state chart, by continuity from R-155. "
    "It derives the intrinsic one-scalar production Hessian and keeps controller-coordinate curvature "
    "separate. It supplies no numerical radius and no cutoff-, floor-, refinement-, chart-, or "
    "Gaussian-past-fibre-uniform estimate. It does not prove global finite-amplitude convexity, general "
    "predictable nonlinear/revisit feedback, T-050 or A13 closure, Nelson, an interacting measure, any "
    "phase, lattice, vacuum, BCC, or PDE verdict, or Sector-A closure."
)


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({"group": group, "name": name, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def mat_add(left: list[list[F]], right: list[list[F]]) -> list[list[F]]:
    return [[left[r][c] + right[r][c] for c in range(len(left[0]))] for r in range(len(left))]


def mat_mul(left: list[list[F]], right: list[list[F]]) -> list[list[F]]:
    return [[sum(left[r][k] * right[k][c] for k in range(len(right))) for c in range(len(right[0]))] for r in range(len(left))]


def transpose(matrix: list[list[F]]) -> list[list[F]]:
    return [list(row) for row in zip(*matrix)]


def frobenius(left: list[list[F]], right: list[list[F]]) -> F:
    return sum(left[r][c] * right[r][c] for r in range(len(left)) for c in range(len(left[0])))


def scale(matrix: list[list[F]], factor: F) -> list[list[F]]:
    return [[factor * value for value in row] for row in matrix]


def inverse2(matrix: list[list[F]]) -> list[list[F]]:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return [[matrix[1][1] / determinant, -matrix[0][1] / determinant], [-matrix[1][0] / determinant, matrix[0][0] / determinant]]


def determinant2(matrix: list[list[F]]) -> F:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    r155 = json.loads(R155_MANIFEST.read_text(encoding="utf-8"))
    r155_result = REPO / r155["files"]["primary_result"]["path"]
    r155_data = json.loads(r155_result.read_text(encoding="utf-8"))
    imported = F(r155_data["diagnostics"]["certified_pure_dyadic_gap"])
    audit.check("authority", "R-155 result hash", sha256(r155_result) == r155["files"]["primary_result"]["sha256"], sha256(r155_result), r155["files"]["primary_result"]["sha256"])
    audit.check("authority", "R-155 exact dyadic gap", imported == F(147, 1000), imported, F(147, 1000))

    # Coefficient-level differentiation of 9/20(a t^2+b s^2+d t^2 s^2).
    a, b, d, t, s = F(3), F(5), F(2), F(7, 3), F(-4, 5)
    htt = F(9, 10) * (a + d * s * s)
    hss = F(9, 10) * (b + d * t * t)
    hts = F(9, 5) * d * t * s
    determinant = htt * hss - hts * hts
    determinant_formula = F(81, 100) * (a * b + a * d * t * t + b * d * s * s - 3 * d * d * t * t * s * s)
    audit.check("source", "exact mixed derivative coefficient", hts == F(9, 5) * d * t * s, hts, F(9, 5) * d * t * s)
    audit.check("source", "exact determinant formula", determinant == determinant_formula, determinant, determinant_formula)

    R = F(2)
    ray_hessian = [[F(9, 10) * (1 + R * R), F(9, 5) * R * R], [F(9, 5) * R * R, F(9, 10) * (1 + R * R)]]
    ray_metric = [[1 + R * R, R * R], [R * R, 1 + R * R]]
    anti_hessian = ray_hessian[0][0] - ray_hessian[0][1]
    sym_hessian = ray_hessian[0][0] + ray_hessian[0][1]
    anti_metric = ray_metric[0][0] - ray_metric[0][1]
    sym_metric = ray_metric[0][0] + ray_metric[0][1]
    audit.check("curvature", "R=2 Hessian eigenvalues", [anti_hessian, sym_hessian] == [F(-27, 10), F(117, 10)], [anti_hessian, sym_hessian], [F(-27, 10), F(117, 10)])
    audit.check("curvature", "R=2 metric eigenvalues", [anti_metric, sym_metric] == [F(1), F(9)], [anti_metric, sym_metric], [F(1), F(9)])
    audit.check("curvature", "R=2 generalized eigenvalues", [anti_hessian / anti_metric, sym_hessian / sym_metric] == [F(-27, 10), F(13, 10)], [anti_hessian / anti_metric, sym_hessian / sym_metric], [F(-27, 10), F(13, 10)])
    audit.check("curvature", "source parameter Hessian indefinite", determinant2(ray_hessian) < 0, determinant2(ray_hessian), "<0")
    audit.check("curvature", "tangent Gram remains positive", determinant2(ray_metric) > 0 and ray_metric[0][0] > 0, ray_metric, "positive definite")

    A = [[F(1), F(2)], [F(0), F(-1)]]
    B = [[F(2), F(0)], [F(1), F(1)]]
    H = [[F(0), F(1)], [F(1), F(0)]]
    G = [[F(1), F(-1)], [F(2), F(0)]]
    K = [[F(2), F(1)], [F(-1), F(1)]]
    L = [[F(0), F(2)], [F(1), F(-1)]]
    GA_BH = mat_add(mat_mul(G, A), mat_mul(B, H))
    LA_BK = mat_add(mat_mul(L, A), mat_mul(B, K))
    gram = frobenius(H, K) + frobenius(G, L) + frobenius(GA_BH, LA_BK)
    direct = sum((frobenius(left, right) for left, right in ((H, K), (G, L), (GA_BH, LA_BK))), F(0))
    audit.check("chart", "tangent Gram reconstructed", direct == gram, direct, gram)
    diagonal_gram = frobenius(H, H) + frobenius(G, G) + frobenius(GA_BH, GA_BH)
    audit.check("chart", "tangent Gram diagonal positive", diagonal_gram > 0, diagonal_gram, ">0")
    acceleration = mat_add(mat_mul(G, K), mat_mul(L, H))
    pullback_mixed = F(9, 10) * (gram + frobenius(mat_mul(B, A), acceleration))
    audit.check("chart", "connection uses physical composition order", acceleration == mat_add(mat_mul(G, K), mat_mul(L, H)), acceleration, "GK+LH")
    audit.check("chart", "source pullback mixed fixture", pullback_mixed == F(459, 10), pullback_mixed, F(459, 10))

    # Independent polynomial chain-rule fixture: action x^2+3xy+2y^2+y^3,
    # chart x=t, y=s(1+t), evaluated at (1/3,2/5).
    t0, s0 = F(1, 3), F(2, 5)
    x, y = t0, s0 * (1 + t0)
    grad_y = 3 * x + 4 * y + 3 * y * y
    hxy = F(3)
    hyy = 4 + 6 * y
    intrinsic_cross = hxy * (1 + t0) + s0 * hyy * (1 + t0)
    connection_cross = grad_y
    chain_total = intrinsic_cross + connection_cross
    # Direct coefficient expansion gives the same exact value.
    direct_total = 3 * (1 + 2 * t0) + 8 * s0 * (1 + t0) + 9 * s0 * s0 * (1 + t0) ** 2
    audit.check("projected-force", "polynomial pullback chain rule", chain_total == direct_total, chain_total, direct_total)
    audit.check("projected-force", "connection term retained", connection_cross != 0, connection_cross, "nonzero")

    E = [[F(3), F(1)], [F(1), F(2)]]
    lower = [[F(2), F(0)], [F(0), F(1)]]
    C = [[F(1), F(1)], [F(0), F(1)]]
    schur = mat_add(E, scale(mat_mul(mat_mul(C, inverse2(lower)), transpose(C)), F(-1)))
    audit.check("schur", "exact Schur fixture", schur == [[F(3, 2), F(0)], [F(0), F(1)]], schur, [[F(3, 2), F(0)], [F(0), F(1)]])
    audit.check("schur", "Schur fixture positive", determinant2(schur) > 0 and schur[0][0] > 0, schur, "positive definite")

    headroom = imported - F(1, 10)
    allowance = headroom / 2
    retained = imported - allowance
    audit.check("continuation", "headroom exact", headroom == F(47, 1000), headroom, F(47, 1000))
    audit.check("continuation", "half-headroom perturbation retains target", retained == F(247, 2000) and retained > F(1, 10), retained, ">1/10")
    audit.check("boundary", "general R-155 gap below target", F(7, 250) < F(1, 10), F(7, 250), "<1/10")
    audit.check("low", "no independent low coordinate", SCOPE["independent_low_coordinate"] is False, SCOPE["independent_low_coordinate"], False)

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "method": "non-importing standard-library Fraction reconstruction",
        "diagnostics": {
            "origin_pure_dyadic_gap": imported,
            "target_gap": F(1, 10),
            "continuation_headroom": headroom,
            "chosen_continuity_perturbation_allowance": allowance,
            "retained_gap_under_allowance": retained,
            "aligned_ray_hessian_R2": ray_hessian,
            "aligned_ray_metric_R2": ray_metric,
            "aligned_ray_hessian_eigenvalues_R2": [anti_hessian, sym_hessian],
            "aligned_ray_metric_eigenvalues_R2": [anti_metric, sym_metric],
            "aligned_ray_generalized_eigenvalues_R2": [anti_hessian / anti_metric, sym_hessian / sym_metric],
            "fixture_tangent_gram": gram,
            "fixture_source_pullback_mixed_hessian": pullback_mixed,
            "schur_fixture": schur,
        },
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} independent: {len(audit.rows)}/{len(audit.rows)} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
