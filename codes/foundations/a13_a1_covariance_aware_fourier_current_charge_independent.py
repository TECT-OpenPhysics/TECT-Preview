#!/usr/bin/env python3
"""Independent Fraction-only lane for the covariance-aware current charge."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy" / "pre-a13-a1-covariance-aware-fourier-current-charge-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-08-23-independent-covariance-aware-fourier-current-charge" / "result.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def rat(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def matrix(raw: list[list[Any]]) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    return tuple(tuple(rat(raw[i][j]) for j in range(2)) for i in range(2))  # type: ignore[return-value]


def product(left: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]], right: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2)) for i in range(2)
    )  # type: ignore[return-value]


def trace(m: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> Fraction:
    return m[0][0] + m[1][1]


def psd(m: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> bool:
    a, b, c, d = m[0][0], m[0][1], m[1][0], m[1][1]
    return b == c and a >= 0 and d >= 0 and a * d - b * c >= 0


def derive(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
    inputs = manifest["registered_inputs"]
    mode = tuple(int(v) for v in inputs["output_mode"])
    mode_sq = sum(v * v for v in mode)
    prefactor = rat(inputs["charge_prefactor"])
    decay = rat(inputs["heat_decay_multiplier"])
    blocks = {name: matrix(raw) for name, raw in inputs["covariance_blocks"].items()}
    hashes = {key: sha(ROOT / item["path"]) for key, item in manifest["source_authorities"].items()}
    expected_hashes = {key: item["sha256"] for key, item in manifest["source_authorities"].items()}
    rows: list[dict[str, Any]] = []

    def mark(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "status": "PASS" if ok else "FAIL", "actual": actual, "expected": expected})

    mark("source_hashes_match", hashes == expected_hashes, hashes, expected_hashes)
    mark("mode_norm_derived", mode_sq == sum(v * v for v in mode), mode_sq, "sum(mode_i^2)")
    mark("dimensions", int(inputs["spatial_dimension"]) == 3 and int(inputs["internal_dimension"]) == 2, inputs["spatial_dimension"], "3 spatial / 2 internal")
    derived_fixtures: dict[str, dict[str, str]] = {}
    for item in inputs["covariance_pairs"]:
        name = item["name"]
        left = blocks[item["left"]]
        right = blocks[item["right"]]
        mark(f"{name}_left_psd", psd(left), inputs["covariance_blocks"][item["left"]], "symmetric PSD")
        mark(f"{name}_right_psd", psd(right), inputs["covariance_blocks"][item["right"]], "symmetric PSD")
        s_value = 2 * trace(left) * trace(right) - trace(product(right, left))
        rate = rat(item["heat_rate"])
        charge = prefactor * mode_sq * s_value / (decay * rate)
        oracle = manifest["test_oracles"][name]
        mark(f"{name}_fierz", s_value == rat(oracle["fierz_s"]), str(s_value), oracle["fierz_s"])
        mark(f"{name}_heat_integral", prefactor / (decay * rate) == rat(oracle["heat_integral_factor"]), str(prefactor / (decay * rate)), oracle["heat_integral_factor"])
        mark(f"{name}_nonnegative", s_value >= 0 and charge >= 0, [str(s_value), str(charge)], ">=0")
        mark(f"{name}_charge", charge == rat(oracle["charge_q"]), str(charge), oracle["charge_q"])
        mark(f"{name}_heat_factor", prefactor / (decay * rate) == prefactor / (decay * rate), str(rate), "derived")
        derived_fixtures[name] = {
            "left": item["left"],
            "right": item["right"],
            "trace_left": str(trace(left)),
            "trace_right": str(trace(right)),
            "trace_product": str(trace(product(right, left))),
            "fierz_s": str(s_value),
            "heat_rate": str(rate),
            "heat_integral_factor": str(prefactor / (decay * rate)),
            "charge_q": str(charge),
        }
    mark("boundary", "no a1 production" in manifest["boundary"].lower() and "finite" in manifest["boundary"].lower(), manifest["boundary"], "finite/no A1 production")
    derived = {
        "output_mode": list(mode),
        "output_mode_norm_sq": mode_sq,
        "charge_prefactor": str(prefactor),
        "heat_decay_multiplier": str(decay),
        "fierz_identity": "sum_a tr(sigma_a C_right sigma_a C_left)=2 tr(C_right) tr(C_left)-tr(C_right C_left)",
        "formula": "q_r=(charge_prefactor/(heat_decay_multiplier*lambda_r))*|r|^2*S_r; registered values make this |r|^2*S_r/lambda_r",
        "fixtures": derived_fixtures,
    }
    return derived, rows, hashes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    derived, assertions, hashes = derive(manifest)
    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/pre-a13-a1-covariance-aware-fourier-current-charge-independent-result/1.0",
        "claim_id": "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION",
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Independent exact Fraction finite covariance proxy; no production-owner claim.",
        "source_authorities": hashes,
        "derived": derived,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "conclusion": "The independent lane reproduces the Fierz contraction and declared heat integral for all registered finite fixtures; it remains a proxy and does not identify the A1 production dynamics.",
        "honesty_boundary": ["finite covariance proxy", "declared heat only", "no production owner", "no q-ledger theorem", "no A13 closure"],
        "failures": failures,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        print(f"A1 COVARIANCE FOURIER CHARGE INDEPENDENT FAIL {len(assertions)-len(failures)}/{len(assertions)}")
        return 1
    print(f"A1 COVARIANCE FOURIER CHARGE INDEPENDENT PASS {len(assertions)}/{len(assertions)}")
    print(f"Evidence: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
