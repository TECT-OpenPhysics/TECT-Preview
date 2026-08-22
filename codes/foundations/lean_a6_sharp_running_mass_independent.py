"""Non-importing Fraction-only audit for R-194."""

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

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a6-sharp-running-mass-counterterm-boundary-manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A6-CLASSII-K-COMPOSITE-DEFINITION" / "runs" / "2026-08-22-lean-r194-sharp-running-mass" / "independent.json"


def sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def derive_coefficients(a1: dict[str, Any]) -> tuple[F, F, F, F]:
    p = a1["parameters"]
    q = lambda key: F(str(p[key]))
    den = q("M_X") ** 2 + q("classii_mass_regularizer")
    return q("cJJ") * q("alpha_X") ** 2 / den, q("cJK") * q("alpha_X") * q("beta_X") / den, q("cKK") * q("beta_X") ** 2 / den, q("rho_regularizer")


def W(a: F, b: F, c: F, eps: F, s: F, r: F) -> F:
    rho = s + r
    return 9 * (a + 2 * b + c) * s - 6 * b * s * s / (rho + eps) - 3 * c * s * s * (rho + 2 * eps) / (rho + eps) ** 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    a1 = json.loads((REPO / manifest["inputs"]["a1_production"]["path"]).read_text(encoding="utf-8"))
    oracle = manifest["registered_inputs"]["test_oracles"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(condition), "actual": serial(actual), "expected": serial(expected)})
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    check("identity", manifest["audit_id"] == "A6-R194-SHARP-RUNNING-MASS-COUNTERTERM-BOUNDARY" and manifest["result_id"] == "R-194", [manifest["audit_id"], manifest["result_id"]], "R-194 identity")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False)
    check("no new negative", manifest["formal_integration"]["no_new_negative_ids"] == [], manifest["formal_integration"]["no_new_negative_ids"], [])
    a, b, c, eps = derive_coefficients(a1)
    h_min = 9 * (a + 2 * b + c)
    check("b positive", b > 0, b, ">0")
    check("c positive", c > 0, c, ">0")
    for s_raw, r_raw in oracle["endpoint_samples"]:
        s, r = F(s_raw), F(r_raw)
        rho = s + r
        diff = h_min * s - W(a, b, c, eps, s, r)
        correction = 6 * b * s * s / (rho + eps) + 3 * c * s * s * (rho + 2 * eps) / (rho + eps) ** 2
        check("endpoint identity", diff == correction, {"s": s, "r": r, "diff": diff, "correction": correction}, "exact equality")
        check("endpoint nonnegative", diff >= 0, diff, ">=0")
    sub_s, sub_r = F(oracle["subsharp_s"]), F(oracle["subsharp_r"])
    sub_h = h_min - F(oracle["subsharp_gap"])
    sub_difference = sub_h * sub_s - W(a, b, c, eps, sub_s, sub_r)
    check("subsharp witness", sub_difference < 0, sub_difference, "<0")
    ratios = [(h_min * sub_s - W(a, b, c, eps, sub_s, F(raw_r))) / sub_s for raw_r in oracle["escape_r_values"]]
    check("escape ratios positive", all(value > 0 for value in ratios), ratios, ">0")
    check("escape ratios decrease", all(left > right for left, right in zip(ratios, ratios[1:])), ratios, "strictly decreasing")
    check("escape formula limit", "rho=s+|Psi_3|^2" in manifest["registered_inputs"]["formula"] and "r" in manifest["next_action"], manifest["registered_inputs"]["formula"], "registered formula")
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS",
        "assertion_count": len(rows), "assertions": rows, "derived": serial({"a": a, "b": b, "c": c, "eps": eps, "h_min": h_min, "sub_difference": sub_difference, "ratios": ratios}),
        "boundary": manifest["boundary"], "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if not args.no_store:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT R-194 PASS {len(rows)}/{len(rows)} h_min={h_min}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
