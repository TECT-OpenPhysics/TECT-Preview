#!/usr/bin/env python3
"""Eight mutation tests guarding the R-461 null-branch classification.

Every row below is a deliberately wrong inference or formula.  A PASS means
the mutation was rejected by an explicit counterexample or scope firewall.
This is an adversarial boundary audit, not a new physical result.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-null-branch-dichotomy-manifest.json"
DEFAULT_OUTPUT = (
    REPO / "claims" / "A6-CLASSII-UV-POWER-COUNTING" / "runs"
    / "2026-08-31-hostile-a6-null-branch-dichotomy" / "hostile.json"
)


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def pauli(axis: int, z: tuple[complex, complex]) -> tuple[complex, complex]:
    if axis == 1:
        return z[1], z[0]
    if axis == 2:
        return -1j * z[1], 1j * z[0]
    if axis == 3:
        return z[0], -z[1]
    raise ValueError(axis)


def inner(x: tuple[complex, ...], y: tuple[complex, ...]) -> complex:
    return sum(a.conjugate() * b for a, b in zip(x, y))


def moments(field: tuple[complex, complex, complex], derivative: tuple[complex, complex, complex], eps: float) -> tuple[float, list[tuple[float, float, float, float]]]:
    z, dz = (field[0], field[1]), (derivative[0], derivative[1])
    rho = float(inner(field, field).real)
    drho = 2.0 * float(inner(field, derivative).real)
    values = []
    for axis in (1, 2, 3):
        sz = pauli(axis, z)
        m = float(inner(z, sz).real)
        dm = 2.0 * float(inner(sz, dz).real)
        q = m / (rho + eps)
        values.append((m, dm, q, dm - q * drho))
    return drho, values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads((REPO / manifest["inputs"]["a1_production_functional_manifest"]["path"]).read_text(encoding="utf-8"))
    p = a1["parameters"]
    den = F(str(p["M_X"])) ** 2 + F(str(p["classii_mass_regularizer"]))
    aa = F(str(p["cJJ"])) * F(str(p["alpha_X"])) ** 2 / den
    bb = F(str(p["cJK"])) * F(str(p["alpha_X"])) * F(str(p["beta_X"])) / den
    cc = F(str(p["cKK"])) * F(str(p["beta_X"])) ** 2 / den
    eps = float(F(str(p["rho_regularizer"])))
    threshold = float(manifest["audit"]["strict_positive_threshold"])
    rows: list[dict[str, Any]] = []

    def reject(name: str, condition: bool, witness: Any, expected: Any) -> None:
        rows.append({"mutation": name, "pass": bool(condition), "witness": str(witness), "expected": str(expected)})
        if not condition:
            raise AssertionError(f"mutation survived: {name}: {witness!r}")

    # 1. A sign-flipped m3 fails the Pauli reconstruction orientation even
    # though squaring alone would hide this mistake.
    x1, y1, x2, y2 = 1, 0, 0, 0
    s = F(x1 * x1 + y1 * y1 + x2 * x2 + y2 * y2)
    true_m3 = F(x1 * x1 + y1 * y1 - x2 * x2 - y2 * y2)
    wrong_m3 = -true_m3
    reject("wrong-m3-sign", wrong_m3 != s and true_m3 == s, wrong_m3, f"m3={s}")

    # 2. A sign-flipped m2 is caught by the direct complex expectation, not by
    # the squared Bloch identity.
    z = (1 + 0j, 1j)
    direct_m2 = float(inner(z, pauli(2, z)).real)
    wrong_m2 = -direct_m2
    reject("wrong-m2-sign", not math.isclose(wrong_m2, direct_m2, abs_tol=threshold), wrong_m2, direct_m2)

    # 3. Positive definiteness is essential: a semidefinite matrix has a
    # nonzero zero-form direction.
    deg_a, deg_b, deg_c, j, k = F(1), F(1), F(1), F(-1), F(1)
    deg_form = deg_a * j * j + 2 * deg_b * j * k + deg_c * k * k
    deg_det = deg_a * deg_c - deg_b * deg_b
    reject("nonpositive-determinant-form", deg_form == 0 and (j, k) != (0, 0) and deg_det <= 0, (deg_form, deg_det, j, k), "precondition rejected")

    # 4. Constant rho does not imply a null field: an internal rotation has a
    # nonzero J even with drho=0.
    rotating = (1 + 0j, 0j, 0j)
    rotating_d = (0j, 1 + 0j, 0j)
    drho, rot_rows = moments(rotating, rotating_d, eps)
    rot_energy = 0.5 * float(aa) * sum(row[1] ** 2 for row in rot_rows)
    reject("constant-rho-only", abs(drho) <= threshold and rot_energy > threshold, (drho, rot_energy), "rotation non-null")

    # 5. Dropping or changing the q*grad(rho) term changes the quotient
    # derivative on a generic field.  This fixture is intentionally not called
    # a null field.
    field = (0.9 + 0.2j, -0.3 + 0.4j, 0.5 - 0.1j)
    derivative = (0.17 - 0.08j, -0.05 + 0.12j, 0.21 + 0.03j)
    drho, data = moments(field, derivative, eps)
    mismatch = max(abs(row[3] - (row[1] + row[2] * drho)) for row in data)
    reject("quotient-derivative-sign", mismatch > threshold, mismatch, ">0")

    # 6. The assertion that a nonzero doublet can have all Bloch moments zero
    # is rejected by an exact finite grid enumeration.
    zero_nonzero = []
    for a in range(-2, 3):
        for b in range(-2, 3):
            for c0 in range(-2, 3):
                for d in range(-2, 3):
                    m1 = 2 * (a * c0 + b * d)
                    m2 = 2 * (a * d - b * c0)
                    m3 = a * a + b * b - c0 * c0 - d * d
                    if (m1, m2, m3) == (0, 0, 0) and (a, b, c0, d) != (0, 0, 0, 0):
                        zero_nonzero.append((a, b, c0, d))
    reject("nonzero-zero-Bloch", not zero_nonzero, zero_nonzero, "empty witness set")

    # 7. A common-phase plane wave has pathwise Class-II energy zero but the
    # registered W_epsilon is positive; W=0 cannot replace the pathwise null
    # set.
    pw = (0.8 + 0.1j, -0.25 + 0.6j, 0.4 - 0.3j)
    pw_d = tuple(1j * 1.7 * value for value in pw)
    _, pw_rows = moments(pw, pw_d, eps)
    pw_energy = 0.5 * sum(float(aa) * row[1] ** 2 + 2 * float(bb) * row[1] * row[3] + float(cc) * row[3] ** 2 for row in pw_rows)
    rho = float(inner(pw, pw).real)
    ss = float(inner((pw[0], pw[1]), (pw[0], pw[1])).real)
    ww = 9.0 * (float(aa) + 2 * float(bb) + float(cc)) * ss
    ww -= 6.0 * float(bb) * ss * ss / (rho + eps)
    ww -= 3.0 * float(cc) * ss * ss * (rho + 2 * eps) / ((rho + eps) ** 2)
    reject("conditional-W-zero-substitution", pw_energy <= threshold and ww > threshold, (pw_energy, ww), "pathwise zero but W>0")

    # 8. Any attempted physical/continuum/source-owner promotion is blocked
    # by the manifest's explicit scope firewall.
    firewall = manifest["scope_firewall"]
    protected = (not firewall["gibbs_concentration_closed"] and not firewall["continuum_closed"]
                 and not firewall["source_owner_admitted"] and not firewall["pre_a_closed"]
                 and not firewall["sector_a_closed"] and not firewall["yang_mills_identity_closed"]
                 and not firewall["mass_gap_closed"])
    reject("premature-promotion", protected, firewall, "all downstream flags false")

    payload = {
        "schema": "tect/a6-classii-null-branch-dichotomy-hostile-result/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "mutations_rejected": rows,
        "scope_firewall": firewall,
        "evidence_level": "T0 adversarial formula/scope mutation audit",
        "non_claims": manifest["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        save(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"HOSTILE MUTATIONS REJECTED {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
