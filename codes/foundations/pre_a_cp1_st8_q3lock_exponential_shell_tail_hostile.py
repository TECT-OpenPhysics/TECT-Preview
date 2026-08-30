#!/usr/bin/env python3
"""Adversarial mutation firewall for the R-444 scalar tail contract."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pre-a-cp1-st8-q3lock-exponential-shell-tail-manifest.json"
PRIMARY = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-exponential_shell_tail/primary.json"
INDEPENDENT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-exponential_shell_tail/independent.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-hostile-exponential_shell_tail/hostile.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def accepts(candidate: dict[str, Any], baseline: dict[str, Any]) -> bool:
    f, b, s = candidate.get("finite_contract", {}), baseline["finite_contract"], candidate.get("scope", {})
    return candidate.get("claim_bearing") is False and f.get("dimension") == b["dimension"] and f.get("weight") == b["weight"] and f.get("shell_count") == b["shell_count"] and f.get("tail_formula") == b["tail_formula"] and f.get("tail_radius_min") == b["tail_radius_min"] and s.get("geometric_shell_tail_closed") is True and all(s.get(k) is False for k in ("boundary_commutator_decay_closed", "history_tail_closed", "weighted_operator_form_closed", "exhaustion_cauchy_closed", "common_core_closed", "common_alpha_closed", "physical_empty_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    baseline = json.loads(MANIFEST.read_text(encoding="utf-8")); primary = json.loads(PRIMARY.read_text(encoding="utf-8")); independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    if not accepts(baseline, baseline): raise AssertionError("baseline rejected")
    if primary.get("verdict") != "EXPONENTIAL_SHELL_TAIL_AUDITED" or independent.get("verdict") != "INDEPENDENT_EXPONENTIAL_SHELL_TAIL_CONTROL": raise AssertionError("positive controls missing")
    rows: list[dict[str, Any]] = []
    def reject(name: str, mutation: dict[str, Any], candidate: dict[str, Any]) -> None:
        accepted = accepts(candidate, baseline)
        if accepted: raise AssertionError(f"mutation accepted: {name}")
        rows.append({"name": name, "status": "REJECTED", "mutation": mutation, "accepted": accepted})
    m = copy.deepcopy(baseline); m["finite_contract"]["shell_count"] = "N_3(n)=4*n^2+1"; reject("wrong shell count", {"shell_count": "4*n^2+1"}, m)
    m = copy.deepcopy(baseline); m["finite_contract"]["tail_formula"] = "2*(4*R^2+8*R+14)*2^(1-R)"; reject("wrong layer factor", {"tail_formula": "factor 2"}, m)
    m = copy.deepcopy(baseline); m["finite_contract"]["weight"] = "2^(-euclidean_norm(lower_endpoint))"; reject("wrong norm", {"weight": "euclidean"}, m)
    m = copy.deepcopy(baseline); m["finite_contract"]["tail_radius_min"] = 0; reject("zero-radius formula use", {"tail_radius_min": 0}, m)
    m = copy.deepcopy(baseline); m["scope"]["boundary_commutator_decay_closed"] = True; reject("commutator promotion", {"boundary_commutator_decay_closed": True}, m)
    m = copy.deepcopy(baseline); m["scope"]["history_tail_closed"] = True; reject("history-tail promotion", {"history_tail_closed": True}, m)
    m = copy.deepcopy(baseline); m["scope"]["weighted_operator_form_closed"] = True; reject("operator promotion", {"weighted_operator_form_closed": True}, m)
    m = copy.deepcopy(baseline); m["claim_bearing"] = True; reject("physical/QFT claim promotion", {"claim_bearing": True}, m)
    payload: dict[str, Any] = {"schema": "tect/pre-a-r444-hostile/1.0", "manifest": MANIFEST.relative_to(ROOT).as_posix(), "result_id": "R-444", "exploration_id": "EXP-001289", "claim_id": baseline["claim_ids"][0], "run_kind": "hostile", "verdict": "HOSTILE_MUTATIONS_REJECTED", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "mutations_rejected": len(rows), "scope": {"hostile_mutations_rejected": True, "claim_bearing": False, "operator_or_physical_promotion_rejected": True}, "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)}, "evidence_level": "T0 / EXECUTED ADVERSARIAL SCALAR-TAIL FIREWALL", "non_claims": baseline["non_claims"], "boundary": baseline["boundary"]}
    destination = output if output.is_absolute() else ROOT / output; atomic_json(destination, payload); print(f"R-444 HOSTILE {payload['verdict']} {len(rows)}/{len(rows)}", flush=True); return payload


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run(args.output)
    if args.self_test: assert payload["verdict"] == "HOSTILE_MUTATIONS_REJECTED" and payload["assertion_count"] == 8; print("R-444 HOSTILE SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__": raise SystemExit(main())
