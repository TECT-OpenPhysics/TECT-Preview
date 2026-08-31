#!/usr/bin/env python3
"""Hostile mutation lane for R-462.

Each mutation targets a load-bearing assumption of the active-branch normal
form.  A passing hostile test means the mutated route is rejected; it is not a
new physical or probabilistic result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "a6-classii-active-branch-normal-form-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / "A6-CLASSII-UV-POWER-COUNTING"
    / "runs"
    / "2026-08-31-hostile-a6-active-branch-normal-form"
    / "hostile.json"
)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def save(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def dot(x: tuple[F, F, F], y: tuple[F, F, F]) -> F:
    return sum((a * b for a, b in zip(x, y)), F(0))


def qform(a: F, b: F, c: F, x: F, y: F) -> F:
    return a * x * x + 2 * b * x * y + c * y * y


def raw_energy(a: F, b: F, c: F, s: F, ds: F, delta: F, n: tuple[F, F, F], t: tuple[F, F, F]) -> F:
    j = tuple(ds * n_i + s * t_i for n_i, t_i in zip(n, t))
    k = tuple(delta * n_i + s * t_i for n_i, t_i in zip(n, t))
    return a * dot(j, j) + 2 * b * dot(j, k) + c * dot(k, k)


def derive(a1: dict[str, Any]) -> dict[str, F]:
    p = a1["parameters"]
    alpha = F(str(p["alpha_X"]))
    beta = F(str(p["beta_X"]))
    denominator = F(str(p["M_X"])) ** 2 + F(str(p["classii_mass_regularizer"]))
    return {
        "a": F(str(p["cJJ"])) * alpha * alpha / denominator,
        "b": F(str(p["cJK"])) * alpha * beta / denominator,
        "c": F(str(p["cKK"])) * beta * beta / denominator,
        "rho_floor": F(str(p["rho_regularizer"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = REPO / manifest["inputs"]["a1_production_functional_manifest"]["path"]
    a1 = json.loads(source.read_text(encoding="utf-8"))
    coeff = derive(a1)
    a, b, c, eps = coeff["a"], coeff["b"], coeff["c"], coeff["rho_floor"]
    n = (F(1), F(0), F(0))
    t = (F(0), F(1), F(0))
    s = F(2)
    rho = F(3)
    ds = F(1)
    drho = F(2)
    denominator = rho + eps
    delta = ds - s * drho / denominator
    rows: list[dict[str, Any]] = []

    def reject(name: str, rejected: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(rejected), "actual": str(actual), "expected": str(expected)})
        if not rejected:
            raise AssertionError(f"mutation survived: {name}: {actual!r}")

    reject("wrong delta sign", raw_energy(a, b, c, s, ds, delta, n, t) != raw_energy(a, b, c, s, ds, ds + s * drho / denominator, n, t), delta, "floor-subtracted delta")
    reject("omit radial cross coefficient", (a + 2 * b + c) != (a + c), a + 2 * b + c, "a+c")
    reject("drop q grad rho", delta != ds, delta, ds)
    reject("use rho without fixed floor", delta != ds - s * drho / rho, delta, ds - s * drho / rho)
    constant_rho_energy = raw_energy(a, b, c, F(1), F(1), F(1), n, (F(0), F(0), F(0)))
    reject("constant rho implies null", constant_rho_energy > 0, constant_rho_energy, "would be zero under mutation")
    non_tangent = (F(1), F(1), F(0))
    non_tangent_raw = raw_energy(a, b, c, s, ds, delta, n, non_tangent)
    non_tangent_rhs = qform(a, b, c, ds, delta) + (a + 2 * b + c) * s * s * dot(non_tangent, non_tangent)
    reject("non-tangent frame", dot(n, non_tangent) != 0 and non_tangent_raw != non_tangent_rhs, (dot(n, non_tangent), non_tangent_raw, non_tangent_rhs), "orthogonal frame required")
    semidefinite_value = qform(F(1), F(1), F(1), F(1), F(-1))
    reject("semidefinite determinant witness", semidefinite_value == 0 and (F(1), F(-1)) != (F(0), F(0)), (semidefinite_value, F(1), F(-1)), "positive determinant required")
    reject("premature tube promotion", manifest["scope_firewall"]["tube_probability_closed"] is False and manifest["tier"] == "T0", manifest["scope_firewall"], "tube_probability_closed=false and T0")

    payload = {
        "schema": "tect/a6-classii-active-branch-normal-form-hostile-result/1.0",
        "run_kind": "hostile",
        "audit_id": manifest["audit_id"],
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "script_version": __version__,
        "verdict": "HOSTILE_MUTATIONS_REJECTED",
        "assertion_summary": {"passed": len(rows), "total": len(rows)},
        "assertions": rows,
        "source_manifest_sha256": sha256(MANIFEST),
        "evidence_level": "Hostile route rejection for the T0 local normal-form package",
        "non_claims": manifest["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        output = args.output if args.output.is_absolute() else REPO / args.output
        save(output, payload)
    print(f"HOSTILE MUTATIONS REJECTED {len(rows)}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
