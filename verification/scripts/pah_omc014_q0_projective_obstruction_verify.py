#!/usr/bin/env python3
"""Integrated verifier for the PAH-OMC-014 Q=0 projective obstruction."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC004 = ROOT / "strategy/pa-hyp/PAH-OMC-004-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
PRIMARY = ROOT / "codes/foundations/pah_omc014_q0_projective_obstruction.py"
INDEPENDENT = ROOT / "codes/foundations/pah_omc014_q0_projective_obstruction_independent.py"
HOSTILE = ROOT / "codes/foundations/pah_omc014_q0_projective_obstruction_hostile.py"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-q0-projective-obstruction"
DEFAULT_OUTPUT = RUN_DIR / "integrated.json"
EXPECTED_HASHES = {
    "PAH-001": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "PAH-OMC-004": "38163b7f0320cc7041cda4230bc0f6f07cfdc589cd3f12fdbab9f86c25a3a10c",
    "PAH-OMC-012": "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
}
EXPECTED_MAP_SHA = "b66044e590399d959ab2947edf22f3aa2aeea4405473b88c4327da24058ebb93"
EXPECTED_MAP_TERMS = 2784
NEGATIVE_TAG = "AUDIT-2026-09-05-PAH-OMC-014-Q0-COMPONENT-PUSHFORWARD"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            json.dump(payload, stream, ensure_ascii=True, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def child(script: Path, output: Path, *extra: str) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output), *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    payload = read(output) if output.is_file() else {}
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-2000:],
        "stderr": proc.stderr[-2000:],
        "payload": payload,
    }


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, passed: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "passed": bool(passed), "actual": actual, "expected": expected})

    with tempfile.TemporaryDirectory(prefix="pah_omc014_q0_integrated_") as directory:
        temporary = Path(directory)
        primary_path = temporary / "primary.json"
        independent_path = temporary / "independent.json"
        hostile_path = temporary / "hostile.json"
        primary = child(PRIMARY, primary_path)
        independent = child(INDEPENDENT, independent_path)
        hostile = child(HOSTILE, hostile_path, "--primary-run", str(primary_path), "--independent-run", str(independent_path))

        p_payload = primary["payload"]
        i_payload = independent["payload"]
        h_payload = hostile["payload"]
        check("primary subprocess", primary["returncode"] == 0 and p_payload.get("verification") == "PASS", {"returncode": primary["returncode"], "verification": p_payload.get("verification")}, "0/PASS")
        check("independent subprocess", independent["returncode"] == 0 and i_payload.get("verification") == "PASS", {"returncode": independent["returncode"], "verification": i_payload.get("verification")}, "0/PASS")
        check("hostile subprocess", hostile["returncode"] == 0 and h_payload.get("verification") == "PASS" and h_payload.get("verdict") == "HOSTILE_MUTATIONS_REJECTED", {"returncode": hostile["returncode"], "verification": h_payload.get("verification"), "verdict": h_payload.get("verdict")}, "0/PASS/HOSTILE_MUTATIONS_REJECTED")
        check("source hashes", p_payload.get("source_hashes") == i_payload.get("source_hashes") == h_payload.get("source_hashes") == EXPECTED_HASHES, {"primary": p_payload.get("source_hashes"), "independent": i_payload.get("source_hashes"), "hostile": h_payload.get("source_hashes")}, EXPECTED_HASHES)
        p_map = p_payload.get("derived", {}).get("cross_difference_coefficients")
        i_map = i_payload.get("derived", {}).get("cross_difference_coefficients")
        check("independent map equality", p_map == i_map, {"primary_terms": len(p_map or []), "independent_terms": len(i_map or [])}, "identical exact maps")
        check("map oracle", p_payload.get("derived", {}).get("cross_difference_sha256") == EXPECTED_MAP_SHA and i_payload.get("derived", {}).get("cross_difference_sha256") == EXPECTED_MAP_SHA and len(p_map or []) == EXPECTED_MAP_TERMS, {"primary": [p_payload.get("derived", {}).get("cross_difference_sha256"), len(p_map or [])], "independent": [i_payload.get("derived", {}).get("cross_difference_sha256"), len(i_map or [])]}, {"sha256": EXPECTED_MAP_SHA, "terms": EXPECTED_MAP_TERMS})
        check("negative scope is componentwise", p_payload.get("verdict") == "NEGATIVE_RESULT" and ("not a full-Q global-mixture no-go" in p_payload.get("boundary", "") or "does not refute a global full-Q mixture" in p_payload.get("boundary", "")) and p_payload.get("negative_tag") == NEGATIVE_TAG, {"verdict": p_payload.get("verdict"), "boundary": p_payload.get("boundary"), "tag": p_payload.get("negative_tag")}, "scoped NEGATIVE_RESULT")
        check("exact proof criterion is present", "Lindemann" in p_payload.get("exact_nonzero_criterion", "") and "integer coefficient map" in p_payload.get("exact_nonzero_criterion", ""), p_payload.get("exact_nonzero_criterion"), "exact nonzero criterion")
        check("no parent mutation", sha(PAH001) == EXPECTED_HASHES["PAH-001"] and sha(OMC004) == EXPECTED_HASHES["PAH-OMC-004"] and sha(OMC012) == EXPECTED_HASHES["PAH-OMC-012"], {"PAH-001": sha(PAH001), "PAH-OMC-004": sha(OMC004), "PAH-OMC-012": sha(OMC012)}, EXPECTED_HASHES)
        check("physical and continuum firewall", all(any(term in item for item in p_payload.get("non_claims", [])) for term in ("physical Pre-A", "continuum", "QFT", "TOE")), p_payload.get("non_claims"), "non-claims retained")
        check("Lean status is honest", h_payload.get("lean", {}).get("status") == "NOT_APPLICABLE" and "outside" in h_payload.get("lean", {}).get("reason", ""), h_payload.get("lean"), "NOT_APPLICABLE with reason")

        failed = [row for row in rows if not row["passed"]]
        payload: dict[str, Any] = {
            "schema": "tect/pah-omc014-q0-projective-obstruction-integrated/1.0",
            "run_kind": "integrated",
            "audit_id": "PAH-OMC-014-Q0-PROJECTIVE-OBSTRUCTION-INTEGRATED-001",
            "task_id": "T-054",
            "claim_id": "C6-SPACETIME-SIGNATURE",
            "negative_tag": NEGATIVE_TAG,
            "verification": "PASS" if not failed else "FAIL",
            "verdict": "NEGATIVE_RESULT" if not failed else "HOLD_FOR_EVIDENCE",
            "classification": "ROUTE_LOCAL_Q0_COMPONENT_PUSHFORWARD_NO_GO",
            "assertion_count": len(rows),
            "passed": len(rows) - len(failed),
            "failed": len(failed),
            "assertions": rows,
            "source_hashes": {"PAH-001": sha(PAH001), "PAH-OMC-004": sha(OMC004), "PAH-OMC-012": sha(OMC012), "primary": sha(PRIMARY), "independent": sha(INDEPENDENT), "hostile": sha(HOSTILE)},
            "runs": {"primary": p_payload, "independent": i_payload, "hostile": h_payload},
            "scope": "G_3 -> G_2, K=2, M_s=M_psi=1, epsilon=1/2, beta=1, nu=1, R_max=1, Q=0; aperture indicator at (0,0)",
            "exact_witness": {"cross_difference_terms": EXPECTED_MAP_TERMS, "cross_difference_sha256": EXPECTED_MAP_SHA, "criterion": "nonempty integer coefficient map over distinct rational exponents; Lindemann--Weierstrass gives exact nonvanishing"},
            "boundary": "Rejects only the deterministic-grade component push-forward equality at Q_f=0. A global cross-Q mixture with sector cancellation remains outside this test.",
            "claim_bearing": False,
            "active_gate_change": False,
            "lean": {"status": "NOT_APPLICABLE", "reason": "The exact exponential-polynomial theorem is not formalized in the current Lean bridge; finite algebraic inputs are replayed by two independent Python lanes."},
            "non_claims": ["No source-owned cross-Q weights, global normalized Gibbs state, weak cylinder limit or stationarity are supplied.", "No infinite-volume, continuum, physical Pre-A, spacetime, QFT, gravity, Yang--Mills, mass-gap or TOE conclusion follows."],
            "next_question": "Can a separately source-owned normalized cross-Q kernel and weight recursion establish full-mixture projectivity despite the Q_f=0 component mismatch, without fitted weights or parent-model changes?",
        }
        atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return 0 if run(args.output)["verification"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
