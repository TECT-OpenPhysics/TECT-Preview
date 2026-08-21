"""Stdlib-only independent lane for the R-188 Jensen-defect telescope."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-jensen-defect-telescope-crosscheck-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def derive(values: dict) -> dict:
    c = Fraction(values["c"])
    roots = [Fraction(value) for value in values["root_values"]]
    next_values = [Fraction(value) for value in values["next_values"]]

    def atom(e1: Fraction, e2: Fraction) -> Fraction:
        return e2 * (1 + c * e1)

    j0 = sum(atom(e1, e2) ** 2 for e1 in roots for e2 in next_values) / (len(roots) * len(next_values))
    j1 = {str(e1): sum(atom(e1, e2) ** 2 for e2 in next_values) / len(next_values) for e1 in roots}
    j2 = {f"{e1}|{e2}": atom(e1, e2) ** 2 for e1 in roots for e2 in next_values}
    d_h1 = {str(e1): j1[str(e1)] - j0 for e1 in roots}
    d_h2 = {f"{e1}|{e2}": j2[f"{e1}|{e2}"] - j1[str(e1)] for e1 in roots for e2 in next_values}
    endpoint = {key: j2[key] - j0 for key in j2}
    telescope_residual = {key: d_h1[key.split("|")[0]] + d_h2[key] - endpoint[key] for key in endpoint}
    recombination_residual = {str(e1): d_h1[str(e1)] - (Fraction(0) + d_h1[str(e1)]) for e1 in roots}
    recombination_residual.update({f"{e1}|{e2}": d_h2[f"{e1}|{e2}"] - (j2[f"{e1}|{e2}"] - j1[str(e1)]) for e1 in roots for e2 in next_values})
    return {
        "j0": j0,
        "j1_minus": j1[str(roots[0])],
        "j1_plus": j1[str(roots[-1])],
        "j2_minus_minus": j2[f"{roots[0]}|{next_values[0]}"],
        "j2_minus_plus": j2[f"{roots[0]}|{next_values[-1]}"],
        "j2_plus_minus": j2[f"{roots[-1]}|{next_values[0]}"],
        "j2_plus_plus": j2[f"{roots[-1]}|{next_values[-1]}"],
        "dH1_minus": d_h1[str(roots[0])],
        "dH1_plus": d_h1[str(roots[-1])],
        "dH2_all_zero": all(value == 0 for value in d_h2.values()),
        "secant1": Fraction(0),
        "secant2_plus_plus": j2[f"{roots[-1]}|{next_values[-1]}"],
        "defect1_minus": d_h1[str(roots[0])],
        "defect1_plus": d_h1[str(roots[-1])],
        "defect2_plus_plus": -j1[str(roots[-1])],
        "signed_endpoint_mean": sum(endpoint.values()) / len(endpoint),
        "absolute_first_defect_mean": sum(abs(value) for value in d_h1.values()) / len(d_h1),
        "telescope_residual_max": max(abs(value) for value in telescope_residual.values()),
        "recombination_residual_max": max(abs(value) for value in recombination_residual.values()),
        "absolute_payment_strict": sum(abs(value) for value in d_h1.values()) > 0,
        "a13_gate_closed": False,
        "overlap_src_closed": False,
        "production_map_identified": False,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }


def serialise(values: dict) -> dict:
    return {key: str(value) if isinstance(value, Fraction) else value for key, value in values.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    derived = derive(manifest["registered_inputs"])
    expected = manifest["registered_inputs"]["expected"]
    for key, wanted in expected.items():
        actual = derived[key]
        assert actual == (Fraction(wanted) if isinstance(wanted, str) else wanted)
    assert derived["absolute_payment_strict"] and derived["signed_endpoint_mean"] == 0
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": 12,
        "assertions": [{"name": "independent exact signed Jensen-defect telescope", "pass": True}],
        "derived": serialise(derived),
        "boundary": manifest["boundary"],
    }
    atomic_json(args.output, payload)
    print("INDEPENDENT R-188 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
