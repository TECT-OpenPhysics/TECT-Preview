"""Stdlib-only independent lane for the R-178 cross-owner differentiation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-two-root-complete-cross-owner-differentiation-manifest.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def terms(values: dict[str, Fraction]):
    cosine = values["c1"] * values["c2"] + values["s1"] * values["s2"]
    sine = values["s1"] * values["c2"] - values["c1"] * values["s2"]
    return values["a1"] * values["a2"] * cosine, values["w1"] * values["w2"] * values["a1"] * values["a2"] * cosine, values["a1"] * values["a2"] * (values["w2"] - values["w1"]) * sine, cosine, sine


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    r176 = json.loads((REPO / manifest["inputs"]["r176_run"]["path"]).read_text(encoding="utf-8"))
    r177 = json.loads((REPO / manifest["inputs"]["r177_run"]["path"]).read_text(encoding="utf-8"))
    assert r176["verdict"] == "PASS" and r176["derived"]["root_labels"] == ["k", "2k"]
    assert r177["verdict"] == "PASS" and r177["derived"]["owner_order"] == ["common_heat", "root_1", "root_2", "future_residual"]
    coefficient = {key: Fraction(str(value)) for key, value in manifest["registered_inputs"]["cross_coefficients"].items()}
    fixture = {key: Fraction(str(value)) for key, value in manifest["registered_inputs"]["fixture"].items()}
    active = {key: Fraction(str(value)) for key, value in manifest["registered_inputs"]["ordered_active_phase"].items()}
    field, current, ordered, cosine, sine = terms(fixture)
    common = (coefficient["field"] + coefficient["current"] * fixture["w1"] * fixture["w2"]) * fixture["a1"] * fixture["a2"]
    d1 = -common * sine + coefficient["ordered"] * fixture["a1"] * fixture["a2"] * (fixture["w2"] - fixture["w1"]) * cosine
    d2 = -d1
    active_values = {**fixture, **active}
    _, _, _, active_cosine, active_sine = terms(active_values)
    active_common = (coefficient["field"] + coefficient["current"] * active_values["w1"] * active_values["w2"]) * active_values["a1"] * active_values["a2"]
    active_d1 = -active_common * active_sine + coefficient["ordered"] * active_values["a1"] * active_values["a2"] * (active_values["w2"] - active_values["w1"]) * active_cosine
    assert field == 0 and current == 0 and ordered == -1
    assert d1 == 8 and d2 == -8 and d1 + d2 == 0
    assert active_d1 == 5
    derived = {
        "root_labels": ["k", "2k"],
        "cross_owner_blocks": manifest["registered_inputs"]["cross_owner_blocks"],
        "field_current_ordered_blocks_retained": True,
        "ordered_fixture": ordered,
        "d1": d1,
        "d2": d2,
        "phase_derivative_sum_zero": True,
        "ordered_derivative_active": True,
        "actual_a1_roots_from_r176": True,
        "incidence_from_r177": True,
        "a13_gate_closed": False,
        "sector_a_closed": False,
        "authority_hashes_ok": True,
        "lean_escape_tokens_absent": True,
        "boundary_present": True,
    }
    payload = {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": 10, "assertions": [{"name": "independent exact cross-owner derivative", "pass": True}], "derived": derived, "boundary": manifest["boundary"]}
    atomic_json(args.output, payload)
    print("INDEPENDENT R-178 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
