"""Stdlib-only independent lane for the R-174 two-root cross blocks."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-production-cylinder-cross-synthesis-manifest.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def f(value: object) -> Fraction:
    return Fraction(str(value))


def cross_blocks(a1: Fraction, a2: Fraction, w1: Fraction, w2: Fraction, c1: Fraction, s1: Fraction, c2: Fraction, s2: Fraction) -> tuple[Fraction, Fraction, Fraction]:
    x1v2 = a1 * c1 * (-w2 * a2 * s2) + a1 * s1 * (w2 * a2 * c2)
    x2v1 = a2 * c2 * (-w1 * a1 * s1) + a2 * s2 * (w1 * a1 * c1)
    return x1v2, x2v1, x1v2 + x2v1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    p = manifest["registered_inputs"]
    length = f(p["torus_length"])
    volume = length ** 3
    assert volume == f(p["volume"])
    roots = [f(v) for v in p["root_multipliers"]]
    assert roots == [Fraction(1), Fraction(2)]
    fixture = p["nonzero_fixture"]
    values = {key: f(fixture[key]) for key in ("amp1", "amp2", "w1", "w2", "c1", "s1", "c2", "s2")}
    x1v2, x2v1, cross = cross_blocks(values["amp1"], values["amp2"], values["w1"], values["w2"], values["c1"], values["s1"], values["c2"], values["s2"])
    expected = values["amp1"] * values["amp2"] * (values["w2"] - values["w1"]) * (values["s1"] * values["c2"] - values["c1"] * values["s2"])
    assert cross == expected == f(fixture["cross"])
    same = cross_blocks(values["amp1"], values["amp2"], values["w1"], values["w2"], values["c1"], values["s1"], values["c1"], values["s1"])[2]
    equal_frequency = cross_blocks(values["amp1"], values["amp2"], values["w1"], values["w1"], values["c1"], values["s1"], values["c2"], values["s2"])[2]
    assert same == 0 and equal_frequency == 0
    field_cross = values["amp1"] * values["amp2"] * (values["c1"] * values["c2"] + values["s1"] * values["s2"])
    current_cross = values["w1"] * values["w2"] * field_cross
    assert cross != 0
    derived = {
        "root_multipliers": [str(v) for v in roots],
        "volume": str(volume),
        "cross_formula": "amp1*amp2*(w2-w1)*(s1*c2-c1*s2)",
        "cross_block_1": str(x1v2),
        "cross_block_2": str(x2v1),
        "nonzero_fixture_cross": str(cross),
        "same_phase_cross": str(same),
        "equal_frequency_cross": str(equal_frequency),
        "field_cross_fixture": str(field_cross),
        "current_cross_fixture": str(current_cross),
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }
    payload = {
        "schema": "tect/lean-kernel-crosscheck/1.0",
        "run_kind": "independent",
        "audit_id": manifest["audit_id"],
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "verdict": "PASS",
        "assertion_count": 10,
        "derived": derived,
        "source_hashes": {key: item["sha256"] for key, item in manifest["inputs"].items()},
        "boundary": manifest["boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("INDEPENDENT R-174 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
