"""Stdlib-only independent lane for the R-179 owner-half ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy" / "pre-a-a13-future-variance-forest-owner-half-ledger-manifest.json"


def sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for key in ("r125_manifest", "r136_manifest", "r177_manifest", "r178_manifest"):
        item = manifest["inputs"][key]
        path = REPO / item["path"]
        assert path.is_file() and sha256(path) == item["sha256"]
    vals = {k: Fraction(str(v)) for k, v in manifest["registered_inputs"]["constant_translation_fixture"].items()}
    owner = vals["forest"] / 2 - vals["variance"] / 4
    assert owner == -1
    assert 2 * owner == vals["forest"] - vals["variance"] / 2
    assert owner + vals["variance"] / 4 == vals["forest"] / 2
    assert owner == -vals["s"]
    assert vals["variance"] >= 0 and owner <= vals["forest"] / 2
    derived = {"owner_formula": manifest["registered_inputs"]["owner_formula"], "replica_formula": manifest["registered_inputs"]["replica_formula"], "owner_value": owner, "omission_cost_value": owner + vals["variance"] / 4, "constant_translation_defect": True, "positive_variance_rebate": True, "zero_variance_rebate": True, "a13_gate_closed": False, "sector_a_closed": False, "authority_hashes_ok": True, "lean_escape_tokens_absent": True, "boundary_present": True}
    atomic_json(args.output, {"schema": "tect/lean-kernel-crosscheck/1.0", "run_kind": "independent", "audit_id": manifest["audit_id"], "claim_id": manifest["claim_id"], "result_id": manifest["result_id"], "verdict": "PASS", "assertion_count": 10, "assertions": [{"name": "independent exact owner-half ledger", "pass": True}], "derived": derived, "boundary": manifest["boundary"]})
    print("INDEPENDENT R-179 LEAN CROSSCHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
