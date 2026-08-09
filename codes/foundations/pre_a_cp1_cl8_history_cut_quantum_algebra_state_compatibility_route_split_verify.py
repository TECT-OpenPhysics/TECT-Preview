#!/usr/bin/env python3
"""Integrated verifier for the CL8 history-cut quantum route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.2.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split"
CANDIDATE_ID = "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-STATE-COMPATIBILITY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-HISTORY-CUT-BH-CCR-STATE-TRANSPORT-AND-RAW-LEG-NOGO"
NEGATIVES = ("NG-2026-08-04-PRE-A-CP1-CL8-HISTORY-CUT-RAW-LEG-TENSOR-FACTORIZATION",)
EXPLORATION_ID = "EXP-000760"
CORRECTION_EXPLORATION_ID = "EXP-000761"
PARENT_IDS = (
    "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-PASSIVE-TWO-ARM-CHARACTERISTIC-CONTROL-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0",
)
EXPECTED_VERDICT = (
    "CLOSE EXACT FINITE OPEN ALL-CUT B(H) UNITARIES AND CUT CCR, PLUS THE "
    "BALANCED-EVEN-M PERIODIC D-K-D AUTOMORPHISM AND NORMAL-STATE-TRANSPORT "
    "INTERTWINER; RETAIN FIXED WEYL-CSTAR INVARIANCE, STATIONARITY/SELECTION, "
    "INTER-REGULATOR, CONTINUUM/HADAMARD, 1D-TO-3D, C6, CP1, AND PRE-A GATES"
)
SCHEMA = f"tect/{SLUG}-integrated/0.2"
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-{SLUG}/result.json"


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], str]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"{script.name} failed:\n{completed.stdout}\n{completed.stderr}")
    return json.loads(output.read_text(encoding="utf-8")), completed.stdout.strip()


def child_summary(stdout: str) -> dict[str, int]:
    match = re.fullmatch(r"PASS ([0-9]+)/([0-9]+) -> .+", stdout)
    if match is None:
        raise AssertionError(f"unexpected child output: {stdout!r}")
    return {"passed": int(match.group(1)), "total": int(match.group(2))}


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def exploration_record(exploration_id: str) -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == exploration_id:
            return record
    raise AssertionError(f"missing {exploration_id}")


def run(output: Path) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="tect-prea-qhist-") as directory:
        root = Path(directory)
        primary, primary_stdout = run_child(PRIMARY, root / "primary.json")
        independent, independent_stdout = run_child(INDEPENDENT, root / "independent.json")
    primary_command = child_summary(primary_stdout)
    independent_command = child_summary(independent_stdout)

    audit.check("candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration identity", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("correction exploration identity", manifest["correction_exploration_id"] == CORRECTION_EXPLORATION_ID, manifest["correction_exploration_id"], CORRECTION_EXPLORATION_ID, "identity")
    audit.check("parent identities", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], list(PARENT_IDS), "identity")
    audit.check("negative identity", tuple(manifest["negative_ids"]) == NEGATIVES, manifest["negative_ids"], list(NEGATIVES), "identity")
    audit.check("scoped verdict", manifest["verdict"] == EXPECTED_VERDICT, manifest["verdict"], EXPECTED_VERDICT, "scope")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    for child_name, child, command in (
        ("primary", primary, primary_command),
        ("independent", independent, independent_command),
    ):
        audit.check(f"{child_name} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "child")
        audit.check(f"{child_name} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "child")
        audit.check(f"{child_name} parents", tuple(child["parent_ids"]) == PARENT_IDS, child["parent_ids"], list(PARENT_IDS), "child")
        audit.check(f"{child_name} negatives", tuple(child["negative_ids"]) == NEGATIVES, child["negative_ids"], list(NEGATIVES), "child")
        audit.check(f"{child_name} verdict", child["verdict"] == EXPECTED_VERDICT, child["verdict"], EXPECTED_VERDICT, "child")
        audit.check(f"{child_name} manifest hash", child["manifest_sha256"] == sha256(MANIFEST), child["manifest_sha256"], sha256(MANIFEST), "freshness")
        audit.check(f"{child_name} certificate hash", child["certificate_sha256"] == sha256(CERTIFICATE), child["certificate_sha256"], sha256(CERTIFICATE), "freshness")
        audit.check(f"{child_name} scope", child["scope"] == manifest["scope"], "equal", "manifest scope", "scope")
        audit.check(f"{child_name} next gate", child["next_gate"] == manifest["gate_resolution"]["next_gate"], child["next_gate"], manifest["gate_resolution"]["next_gate"], "scope")
        audit.check(f"{child_name} assertions", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "child")
        audit.check(f"{child_name} command summary", command == child["assertion_summary"], command, child["assertion_summary"], "child")

    shared_keys = (
        "M",
        "ell",
        "kappa",
        "beta",
        "cut_count",
        "one_species_darboux_determinant",
        "full_eight_species_darboux_determinant",
        "tensor_witness",
        "kernel_mixed_hessian_determinant",
        "kernel_normalization_power",
        "parity_order_count",
        "following_site0",
        "second_following_site0",
    )
    for profile in ("f0", "f1"):
        primary_fixture = primary["invariants"]["fixtures"][profile]
        independent_fixture = independent["invariants"]["fixtures"][profile]
        for key in shared_keys:
            audit.check(f"{profile} shared {key}", primary_fixture[key] == independent_fixture[key], primary_fixture[key], independent_fixture[key], "cross_agreement")

    for rectangle, expected_cuts, expected_legs, expected_sweeps in (("open-2x2", 6, 5, 2), ("open-2x3", 10, 6, 5)):
        primary_open = primary["invariants"]["open_rectangles"][rectangle]
        independent_open = independent["invariants"]["open_rectangles"][rectangle]
        audit.check(f"{rectangle} cross agreement", primary_open == independent_open, primary_open, independent_open, "cross_agreement")
        audit.check(f"{rectangle} cut oracle", primary_open["cuts"] == expected_cuts, primary_open["cuts"], expected_cuts, "oracle")
        audit.check(f"{rectangle} leg oracle", primary_open["legs"] == expected_legs, primary_open["legs"], expected_legs, "oracle")
        audit.check(f"{rectangle} sweep oracle", primary_open["sweeps"] == expected_sweeps, primary_open["sweeps"], expected_sweeps, "oracle")

    f0 = primary["invariants"]["fixtures"]["f0"]
    f1 = primary["invariants"]["fixtures"]["f1"]
    audit.check("F0 cut oracle", f0["cut_count"] == 6, f0["cut_count"], 6, "oracle")
    audit.check("F1 cut oracle", f1["cut_count"] == 20, f1["cut_count"], 20, "oracle")
    audit.check("F0 kappa oracle", f0["kappa"] == "3/64", f0["kappa"], "3/64", "oracle")
    audit.check("F1 kappa oracle", f1["kappa"] == "7/300", f1["kappa"], "7/300", "oracle")
    audit.check("F0 raw tensor oracle", f0["tensor_witness"] == "3/64", f0["tensor_witness"], "3/64", "oracle")
    audit.check("F1 raw tensor oracle", f1["tensor_witness"] == "-7/250", f1["tensor_witness"], "-7/250", "oracle")
    audit.check("negative-step history coefficient", f1["ell"] == "-5/6", f1["ell"], "-5/6", "oracle")
    audit.check("F0 parity order oracle", f0["parity_order_count"] == 2, f0["parity_order_count"], 2, "oracle")
    audit.check("F1 parity order oracle", f1["parity_order_count"] == 6, f1["parity_order_count"], 6, "oracle")

    for child_name, child in (("primary", primary), ("independent", independent)):
        names = {row["name"] for row in child["assertions"]}
        required_fragments = (
            "D-K-D midpoint",
            "raw cross-leg",
            "independent inverse" if child_name == "independent" else "circuit inverse",
            "every ready order" if child_name == "independent" else "all simultaneous-flip orders",
            "staged order mutant central Q difference",
            "staged order mutant retained P difference",
            "reference decoder P",
            "strong support commutation",
            "open-2x3 full sweep order independence",
            "typed physical Gamma and Lambda maps agree",
            "reversed Gamma physical",
            "co-moving",
        )
        for fragment in required_fragments:
            audit.check(f"{child_name} coverage {fragment}", any(fragment in name for name in names), fragment, "present", "coverage")
    independent_source = INDEPENDENT.read_text(encoding="utf-8").lower()
    audit.check("independent has no SymPy import", "import sympy" not in independent_source, "absent", "absent", "independence")
    audit.check("independent has no NumPy import", "import numpy" not in independent_source, "absent", "absent", "independence")
    audit.check("independent does not import primary", "from pre_a_cp1_cl8_history_cut_quantum" not in independent_source, "absent", "absent", "independence")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    audit.check("stored primary fresh", PRIMARY_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(primary), sha256(PRIMARY_STORED), hashlib.sha256(canonical_bytes(primary)).hexdigest(), "stored")
    audit.check("stored independent fresh", INDEPENDENT_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(independent), sha256(INDEPENDENT_STORED), hashlib.sha256(canonical_bytes(independent)).hexdigest(), "stored")

    required_anchors = (
        "section-3-history-fio",
        "section-4-cut-darboux",
        "section-5-reference-cut-anchor",
        "section-7-exact-flip-unitary",
        "section-8-all-cut-quantum-sweep",
        "section-9-periodic-dkd-diagram",
        "section-10-normal-state-transport",
        "section-12-raw-leg-tensor-no-go",
        "section-15-adversarial-review",
        "section-17-gate-and-pre-a-status",
    )
    for anchor in required_anchors:
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate, anchor, "present", "certificate")
    audit.check("unitary order explicit", "U_flip=U_q U_kappa R_s U_p" in certificate, "present", "correct order", "certificate")
    audit.check("outer momentum shifts explicit", "P_L_prime=P_L+kappa*P_s" in certificate and "P_R_prime=P_R+kappa*P_s" in certificate, "present", "both shifts", "certificate")
    audit.check("phase versus automorphism separated", "The phase belongs to the implementer, not the automorphism" in certificate, "present", "separated", "certificate")
    audit.check("state transport not stationarity", "This is transport, not stationarity" in certificate, "present", "separated", "certificate")
    audit.check("history anchor typed", "Lambda_C^[n]:H_C -> H_hist" in certificate, "present", "typed", "certificate")
    audit.check("phase anchor typed", "Gamma_C^[n]=M_half^* Lambda_C^[n]:H_C -> H_a" in certificate, "present", "typed", "certificate")
    audit.check("same-time Gamma direction", "=Gamma_D^[n]^* Gamma_C^[n]" in certificate, "present", "Gamma_D^* Gamma_C", "certificate")
    audit.check("physical Gamma direction", "=Gamma_D^[n+1]^* U_DKD Gamma_C^[n]" in certificate, "present", "Gamma_D^* U Gamma_C", "certificate")
    audit.check("co-moving state boundary", "genuinely Gibbs/ground for the co-moving operator" in certificate, "present", "co-moving only", "certificate")
    audit.check("explicit reference regularity", "position-phase unitary" in certificate and "strongly\ncontinuous" in certificate, "present", "explicit", "certificate")
    audit.check("open endpoint audit recorded", "open `2 by 2` and\n    `2 by 3`" in certificate, "present", "open fixtures", "certificate")
    audit.check("Weyl boundary retained", "One fixed concrete Weyl" in certificate and "C-star algebra is not claimed invariant" in certificate, "present", "open", "certificate")
    audit.check("Pre-A firewall", "It does not close C0 or\nN1--N5, advance C6, complete CP1, or complete Pre-A" in certificate, "present", "open", "certificate")
    package_files = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)
    non_ascii = {
        str(path.relative_to(REPO)): sorted({character for character in path.read_text(encoding="utf-8") if ord(character) > 127})
        for path in package_files
    }
    audit.check("package ASCII clean", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "hygiene")

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    audit.check("negative registered", f"### {NEGATIVES[0]} " in negative_text, NEGATIVES[0], "detailed entry", "records")
    index_text = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index registered", MANIFEST.name in index_text and CERTIFICATE.name in index_text, [MANIFEST.name, CERTIFICATE.name], "both", "records")
    exploration = exploration_record(EXPLORATION_ID)
    correction = exploration_record(CORRECTION_EXPLORATION_ID)
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration result refs remain empty", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "claim-nonbearing strategy result", "records")
    audit.check("exploration negative", tuple(exploration["formal_refs"].get("negatives", [])) == NEGATIVES, exploration["formal_refs"], list(NEGATIVES), "records")
    audit.check("exploration continues repaired route", any(item.get("id") == "EXP-000759" and item.get("relation") == "continues" for item in exploration.get("related", [])), exploration.get("related", []), "continues EXP-000759", "records")
    audit.check("exploration next gate", manifest["gate_resolution"]["next_gate"] in exploration["next_action"], exploration["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    audit.check("correction verdict", correction["verdict"] == "advanced", correction["verdict"], "advanced", "records")
    audit.check("correction relation", any(item.get("id") == EXPLORATION_ID and item.get("relation") == "corrects" for item in correction.get("related", [])), correction.get("related", []), f"corrects {EXPLORATION_ID}", "records")
    audit.check("correction result refs remain empty", correction["formal_refs"].get("results", []) == [], correction["formal_refs"], "claim-nonbearing strategy result", "records")
    audit.check("correction negative unchanged", tuple(correction["formal_refs"].get("negatives", [])) == NEGATIVES, correction["formal_refs"], list(NEGATIVES), "records")
    audit.check("correction next gate", manifest["gate_resolution"]["next_gate"] in correction["next_action"], correction["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    todo_text = (REPO / "todo/todo.json").read_text(encoding="utf-8")
    audit.check("TODO route recorded", CORRECTION_EXPLORATION_ID in todo_text and manifest["gate_resolution"]["next_gate"] in todo_text, CORRECTION_EXPLORATION_ID, "TODO plus next gate", "records")
    changelog_text = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    audit.check("changelog route recorded", CORRECTION_EXPLORATION_ID in changelog_text and MANIFEST.name in changelog_text, CORRECTION_EXPLORATION_ID, "changelog plus manifest", "records")
    lineage_text = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    audit.check("C6 lineage run record", f"runs/2026-08-04-primary-{SLUG}/" in lineage_text and f"runs/2026-08-04-independent-{SLUG}/" in lineage_text, SLUG, "primary and independent runs", "records")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    audit.check("C6 advancement false", manifest["scope"]["C6_advanced"] is False, manifest["scope"]["C6_advanced"], False, "claim_firewall")
    audit.check("Pre-A false", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "claim_firewall")

    catalog = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    audit.check("catalog manifest", MANIFEST.name in catalog, MANIFEST.name, "catalogued", "generated")
    audit.check("catalog certificate", CERTIFICATE.name in catalog, CERTIFICATE.name, "catalogued", "generated")
    audit.check("proof map exploration", EXPLORATION_ID in proof_map, EXPLORATION_ID, "mapped", "generated")
    audit.check("proof map correction exploration", CORRECTION_EXPLORATION_ID in proof_map, CORRECTION_EXPLORATION_ID, "mapped", "generated")
    audit.check("proof map negative", NEGATIVES[0] in proof_map, NEGATIVES[0], "mapped", "generated")

    payload = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(PARENT_IDS),
        "negative_ids": list(NEGATIVES),
        "exploration_id": EXPLORATION_ID,
        "correction_exploration_id": CORRECTION_EXPLORATION_ID,
        "claim_bearing": manifest["claim_bearing"],
        "verdict": manifest["verdict"],
        "status": manifest["status"],
        "script_version": __version__,
        "script_sha256": sha256(SCRIPT),
        "manifest_sha256": sha256(MANIFEST),
        "certificate_sha256": sha256(CERTIFICATE),
        "primary_sha256": hashlib.sha256(canonical_bytes(primary)).hexdigest(),
        "independent_sha256": hashlib.sha256(canonical_bytes(independent)).hexdigest(),
        "child_assertions": {"primary": primary["assertion_summary"], "independent": independent["assertion_summary"]},
        "shared_invariants": {
            profile: {key: primary["invariants"]["fixtures"][profile][key] for key in shared_keys}
            for profile in ("f0", "f1")
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "total_assertions": len(audit.rows) + primary["assertion_summary"]["total"] + independent["assertion_summary"]["total"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    summary = payload["assertion_summary"]
    print(f"PASS {summary['passed']}/{summary['total']} integrated; {payload['total_assertions']} total -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
