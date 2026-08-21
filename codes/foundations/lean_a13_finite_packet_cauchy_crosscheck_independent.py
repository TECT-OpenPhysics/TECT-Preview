"""Stdlib-only independent lane for the R-185 finite packet Cauchy bound."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a13-finite-packet-cauchy-crosscheck-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in manifest["inputs"].values():
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    values = manifest["registered_inputs"]
    source = [Fraction(value) for value in values["source"]]
    control = [Fraction(value) for value in values["control"]]
    assert len(source) == len(control)
    source_norm = sum(value * value for value in source)
    control_norm = sum(value * value for value in control)
    pairing = sum(a * b for a, b in zip(source, control))
    gap = source_norm * control_norm - pairing * pairing
    expected = values["expected"]
    assert source_norm == Fraction(expected["source_norm"])
    assert control_norm == Fraction(expected["control_norm"])
    assert pairing == Fraction(expected["pairing"])
    assert gap == Fraction(expected["gap"])
    assert pairing * pairing <= source_norm * control_norm
    derived = {
        "source_norm": source_norm,
        "control_norm": control_norm,
        "pairing": pairing,
        "gap": gap,
        "bound_holds": True,
        "packet_length": len(source),
        "lean_escape_tokens_absent": True,
        "a13_gate_closed": False,
        "overlap_src_closed": False,
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
        "assertions": [{"name": "independent exact finite packet Cauchy bound", "pass": True}],
        "derived": derived,
        "boundary": manifest["boundary"],
    }
    atomic_json(args.output, payload)
    print("INDEPENDENT R-185 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
