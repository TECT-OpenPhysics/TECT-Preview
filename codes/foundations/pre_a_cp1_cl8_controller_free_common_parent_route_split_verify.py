#!/usr/bin/env python3
"""Integrated publication verifier for the CL8 controller-free parent route."""

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
SLUG = "pre-a-cp1-cl8-controller-free-common-parent-route-split"
CANDIDATE_ID = "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-DKD-HISTORY-CONJUGACY-BOND-TWIST-AND-ROUTE-NOGOS"
NEGATIVES = (
    "NG-2026-08-04-PRE-A-CP1-CL8-BOND-FLOW-GLOBAL-ALL-TIME-SIDEWAYS",
    "NG-2026-08-04-PRE-A-CP1-CL8-DKD2-DIRECT-TWO-LEG-LOCALIZATION",
    "NG-2026-08-04-PRE-A-CP1-CL8-MIDPOINT-QUAD-GLOBAL-UNIQUENESS",
)
EXPLORATION_ID = "EXP-000758"
CORRECTION_EXPLORATION_ID = "EXP-000759"
PARENT_IDS = (
    "PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
    "PA-CP1-ST8-Q3LOCK-v0",
)
EXPECTED_VERDICT = (
    "CLOSE ONLY THE CLASSICAL INSERTED-1D BALANCED-EVEN-M FIXED-REGULATOR "
    "CONTROLLER-FREE D-K-D HISTORY INTERTWINER; RETAIN QUANTUM MIXED-CUT, "
    "STATE/ENERGY-SELECTION, 1D-TO-3D, REGULATOR, CONTINUUM/HADAMARD, C6, "
    "CP1, AND PRE-A GATES"
)
SCHEMA = f"tect/{SLUG}-integrated/0.1"
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


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def child_summary(stdout: str) -> dict[str, int]:
    match = re.fullmatch(r"PASS ([0-9]+)/([0-9]+) -> .+", stdout.strip())
    if match is None:
        raise AssertionError(f"unexpected child stdout: {stdout!r}")
    return {"passed": int(match.group(1)), "total": int(match.group(2))}


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
    with tempfile.TemporaryDirectory(prefix="tect-prea-history-") as directory:
        root = Path(directory)
        primary_path = root / "primary.json"
        independent_path = root / "independent.json"
        primary, primary_stdout = run_child(PRIMARY, primary_path)
        independent, independent_stdout = run_child(INDEPENDENT, independent_path)
    primary_command = child_summary(primary_stdout)
    independent_command = child_summary(independent_stdout)

    audit.check("candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration identity", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("correction exploration identity", manifest["correction_exploration_id"] == CORRECTION_EXPLORATION_ID, manifest["correction_exploration_id"], CORRECTION_EXPLORATION_ID, "identity")
    audit.check("negative identity", tuple(manifest["negative_ids"]) == NEGATIVES, manifest["negative_ids"], list(NEGATIVES), "identity")
    audit.check("canonical parent ids", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], list(PARENT_IDS), "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    audit.check("scoped verdict", manifest["verdict"] == EXPECTED_VERDICT, manifest["verdict"], EXPECTED_VERDICT, "scope")
    for child_name, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{child_name} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "child")
        audit.check(f"{child_name} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "child")
        audit.check(f"{child_name} negatives", tuple(child["negative_ids"]) == NEGATIVES, child["negative_ids"], list(NEGATIVES), "child")
        audit.check(f"{child_name} parent ids", tuple(child["parent_ids"]) == PARENT_IDS, child["parent_ids"], list(PARENT_IDS), "child")
        audit.check(f"{child_name} claim nonbearing", child["claim_bearing"] is False, child["claim_bearing"], False, "child")
        audit.check(f"{child_name} verdict", child["verdict"] == EXPECTED_VERDICT, child["verdict"], EXPECTED_VERDICT, "child")
        audit.check(f"{child_name} manifest hash", child["manifest_sha256"] == sha256(MANIFEST), child["manifest_sha256"], sha256(MANIFEST), "freshness")
        audit.check(f"{child_name} certificate hash", child["certificate_sha256"] == sha256(CERTIFICATE), child["certificate_sha256"], sha256(CERTIFICATE), "freshness")
        audit.check(f"{child_name} assertions all pass", child["assertion_summary"]["passed"] == child["assertion_summary"]["total"], child["assertion_summary"], "all pass", "child")
        audit.check(f"{child_name} scope exact", child["scope"] == manifest["scope"], "equal", "manifest scope", "scope")
        audit.check(f"{child_name} next gate", child["next_gate"] == manifest["gate_resolution"]["next_gate"], child["next_gate"], manifest["gate_resolution"]["next_gate"], "scope")
    audit.check("primary command pass", primary_command == primary["assertion_summary"], primary_command, primary["assertion_summary"], "child")
    audit.check("independent command pass", independent_command == independent["assertion_summary"], independent_command, independent["assertion_summary"], "child")
    audit.check("no temporary child path retained", "tect-prea-history-" not in json.dumps(audit.rows), "absent", "absent", "determinism")

    shared_keys = (
        "kappa",
        "beta",
        "all_cut_count",
        "periodic_flux",
        "all_cut_fluxes",
        "checker_times",
        "checker_plus_times",
        "q3_potential",
        "q3_gradient",
        "q3_hessian_v",
        "nonlinear_next_site0",
        "checker_canonical_p0",
        "energy_defect_nonzero",
    )
    for profile in ("f0", "f1"):
        primary_fp = primary["invariants"]["history_fixture_fingerprints"][profile]
        independent_fp = independent["invariants"]["history_fixture_fingerprints"][profile]
        for key in shared_keys:
            audit.check(f"{profile} shared {key}", primary_fp[key] == independent_fp[key], primary_fp[key], independent_fp[key], "cross_agreement")
    for child_name, child in (("primary", primary), ("independent", independent)):
        assertion_names = {row["name"] for row in child["assertions"]}
        for profile in ("f0", "f1"):
            required_names = (
                f"{profile} typed C pullback" if child_name == "primary" else f"{profile} typed C pullback coefficient",
                f"{profile} minus-to-plus simultaneous quad flip",
                f"{profile} plus-to-next-minus simultaneous periodic quad flip",
                f"{profile} translated-cut energy defect identity",
                f"{profile} nonlinear 1x5 rectangle exact",
                f"{profile} every monotone-cut oriented flux",
            )
            for required_name in required_names:
                audit.check(f"{child_name} assertion present {required_name}", required_name in assertion_names, required_name, "present", "coverage")
        q3_requirement = "Q3 gradient is derivative of potential" if child_name == "primary" else "f0 Q3 gradient from potential"
        audit.check(f"{child_name} Q3 derivative anchor", q3_requirement in assertion_names, q3_requirement, "present", "coverage")
    audit.check("F0 cut count oracle", primary["invariants"]["history_fixture_fingerprints"]["f0"]["all_cut_count"] == 6, primary["invariants"]["history_fixture_fingerprints"]["f0"]["all_cut_count"], 6, "oracles")
    audit.check("F1 cut count oracle", primary["invariants"]["history_fixture_fingerprints"]["f1"]["all_cut_count"] == 20, primary["invariants"]["history_fixture_fingerprints"]["f1"]["all_cut_count"], 20, "oracles")
    audit.check("F0 current oracle", primary["invariants"]["history_fixture_fingerprints"]["f0"]["periodic_flux"] == "1/15", primary["invariants"]["history_fixture_fingerprints"]["f0"]["periodic_flux"], "1/15", "oracles")
    audit.check("F1 current oracle", primary["invariants"]["history_fixture_fingerprints"]["f1"]["periodic_flux"] == "1/792", primary["invariants"]["history_fixture_fingerprints"]["f1"]["periodic_flux"], "1/792", "oracles")
    audit.check("harmonic caustic oracle", primary["invariants"]["harmonic_caustic"] == "0" and independent["invariants"]["harmonic_caustic"] == "0", [primary["invariants"]["harmonic_caustic"], independent["invariants"]["harmonic_caustic"]], ["0", "0"], "oracles")
    for profile in ("f0", "f1"):
        audit.check(f"{profile} every cut flux oracle", all(value == primary["invariants"]["history_fixture_fingerprints"][profile]["periodic_flux"] for value in primary["invariants"]["history_fixture_fingerprints"][profile]["all_cut_fluxes"]), "all equal", "periodic flux", "oracles")
        audit.check(f"{profile} D-K-D energy defect nonzero", primary["invariants"]["history_fixture_fingerprints"][profile]["energy_defect_nonzero"] is True, True, True, "oracles")
    audit.check("Poisson noncommutation oracle", primary["invariants"]["poisson_witness"] == "-1/2", primary["invariants"]["poisson_witness"], "-1/2", "oracles")
    audit.check("midpoint root oracle", independent["invariants"]["midpoint_hostile_y_squared"] == "32", independent["invariants"]["midpoint_hostile_y_squared"], "32", "oracles")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    if PRIMARY_STORED.is_file():
        audit.check("stored primary fresh", PRIMARY_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(primary), sha256(PRIMARY_STORED), hashlib.sha256(canonical_bytes(primary)).hexdigest(), "stored")
    if INDEPENDENT_STORED.is_file():
        audit.check("stored independent fresh", INDEPENDENT_STORED.read_bytes().replace(b"\r\n", b"\n") == canonical_bytes(independent), sha256(INDEPENDENT_STORED), hashlib.sha256(canonical_bytes(independent)).hexdigest(), "stored")

    required_anchors = (
        "section-3-exact-history-conjugacy",
        "section-5-staggered-ab-quad",
        "section-7-open-rectangle-all-cuts",
        "section-8-balanced-periodic-seam",
        "section-9-discrete-symplectic-current",
        "section-10-commuting-dynamics-diagram",
        "section-17-adversarial-review",
        "section-18-gate-and-pre-a-status",
    )
    for anchor in required_anchors:
        audit.check(f"certificate anchor {anchor}", f'id="{anchor}"' in certificate, anchor, "present", "certificate")
    audit.check("history wedge sign", "Omega_hist=(mu/delta) sum dx_plus wedge dx_minus" in certificate, "present", "correct sign", "certificate")
    audit.check("typed symplectic pullback", "C_delta^* Omega_hist=Omega_phase" in certificate and "(C_delta^(-1))^* Omega_phase=Omega_hist" in certificate, "present", "typed both directions", "certificate")
    audit.check("two-parity first diagram", "J_m^+ after B_m^-=F_delta after J_m^-" in certificate, "present", "first parity", "certificate")
    audit.check("two-parity complementary diagram", "J_(m+2)^- after B_m^+=F_delta after J_m^+" in certificate, "present", "complementary parity", "certificate")
    audit.check("time-indexed arbitrary-cut decoder", "J_C^[n]" in certificate and "J_D^[n+1]" in certificate, "present", "time indexed", "certificate")
    audit.check("cut energy ledger", "E_C^[n]=H_a after J_C^[n]" in certificate and "E_D^[n+1] after B_(C->D)-E_C^[n]" in certificate and "H_a after F_delta-H_a" in certificate, "present", "time-indexed exact defect", "certificate")
    audit.check("quantum firewall", "not thereby proved to be tensor-factor" in certificate, "present", "mixed-cut quantum open", "certificate")
    audit.check("Pre-A firewall", "`C0`, `N1`--`N5`, `CP1`\nand Pre-A remain open" in certificate, "present", "open", "certificate")
    package_files = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)
    non_ascii = {str(path.relative_to(REPO)): sorted({char for char in path.read_text(encoding="utf-8") if ord(char) > 127}) for path in package_files}
    audit.check("package ASCII clean", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "hygiene")
    audit.check("ambiguous global scope key absent", "exact_global_boundary_Cauchy_diagram" not in manifest["scope"], sorted(manifest["scope"]), "absent", "scope")
    audit.check("scoped diagram key true", manifest["scope"]["exact_classical_inserted_1D_balanced_even_M_fixed_regulator_DKD_boundary_Cauchy_diagram"] is True, True, True, "scope")
    audit.check("corrected CP1 boundary", "only the classical inserted-1D, balanced-even-M, fixed-regulator D-K-D diagram is established" in manifest["Pre_A_chain_role"]["CP1"], manifest["Pre_A_chain_role"]["CP1"], "scoped diagram only", "scope")

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative in NEGATIVES:
        audit.check(f"negative registered {negative}", f"### {negative} " in negative_text, negative, "detailed entry", "records")
    index_text = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index registered", MANIFEST.name in index_text and CERTIFICATE.name in index_text, [MANIFEST.name, CERTIFICATE.name], "both", "records")
    exploration = exploration_record(EXPLORATION_ID)
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration negatives", tuple(exploration["formal_refs"]["negatives"]) == NEGATIVES, exploration["formal_refs"]["negatives"], list(NEGATIVES), "records")
    audit.check("exploration next gate", manifest["gate_resolution"]["next_gate"] in exploration["next_action"], exploration["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    correction = exploration_record(CORRECTION_EXPLORATION_ID)
    audit.check("correction exploration verdict", correction["verdict"] == "advanced", correction["verdict"], "advanced", "records")
    correction_related = correction.get("related", [])
    audit.check("correction relates to original", any(item.get("id") == EXPLORATION_ID and item.get("relation") == "corrects" for item in correction_related), correction_related, f"corrects {EXPLORATION_ID}", "records")
    audit.check("correction continues prior route", any(item.get("id") == "EXP-000750" and item.get("relation") == "continues" for item in correction_related), correction_related, "continues EXP-000750", "records")
    audit.check("correction keeps negatives", tuple(correction["formal_refs"]["negatives"]) == NEGATIVES, correction["formal_refs"]["negatives"], list(NEGATIVES), "records")
    audit.check("correction keeps result refs empty", correction["formal_refs"].get("results", []) == [], correction["formal_refs"].get("results", []), [], "records")
    audit.check("correction next gate", manifest["gate_resolution"]["next_gate"] in correction["next_action"], correction["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    todo_text = (REPO / "todo/todo.json").read_text(encoding="utf-8")
    audit.check("TODO route recorded", CORRECTION_EXPLORATION_ID in todo_text and manifest["gate_resolution"]["next_gate"] in todo_text, CORRECTION_EXPLORATION_ID, "TODO plus next gate", "records")
    changelog_text = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    audit.check("changelog route recorded", CORRECTION_EXPLORATION_ID in changelog_text and MANIFEST.name in changelog_text, CORRECTION_EXPLORATION_ID, "changelog plus manifest", "records")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    audit.check("C6 advancement false", manifest["scope"]["C6_advanced"] is False, manifest["scope"]["C6_advanced"], False, "claim_firewall")
    audit.check("Pre-A false", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "claim_firewall")

    catalog_text = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    map_text = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    audit.check("catalog manifest", MANIFEST.name in catalog_text, MANIFEST.name, "catalogued", "generated")
    audit.check("catalog certificate", CERTIFICATE.name in catalog_text, CERTIFICATE.name, "catalogued", "generated")
    audit.check("proof map exploration", EXPLORATION_ID in map_text, EXPLORATION_ID, "mapped", "generated")
    for negative in NEGATIVES:
        audit.check(f"proof map negative {negative}", negative in map_text, negative, "mapped", "generated")

    payload = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(PARENT_IDS),
        "claim_bearing": manifest["claim_bearing"],
        "verdict": manifest["verdict"],
        "negative_ids": list(NEGATIVES),
        "exploration_id": EXPLORATION_ID,
        "correction_exploration_id": CORRECTION_EXPLORATION_ID,
        "status": manifest["status"],
        "script_version": __version__,
        "script_sha256": sha256(SCRIPT),
        "manifest_sha256": sha256(MANIFEST),
        "certificate_sha256": sha256(CERTIFICATE),
        "primary_sha256": hashlib.sha256(canonical_bytes(primary)).hexdigest(),
        "independent_sha256": hashlib.sha256(canonical_bytes(independent)).hexdigest(),
        "child_assertions": {
            "primary": primary["assertion_summary"],
            "independent": independent["assertion_summary"],
        },
        "shared_invariants": {
            profile: {key: primary["invariants"]["history_fixture_fingerprints"][profile][key] for key in shared_keys}
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
