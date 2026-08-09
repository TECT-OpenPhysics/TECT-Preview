#!/usr/bin/env python3
"""Integrated verifier for the CL8 Q3 vector P(Phi)2 comparator route split."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.1"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-VECTOR-PHI2-CONSTRUCTIVE-COMPARATOR-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-PHI2-NORMALIZABILITY-L1-DENSITY-AND-CONFIGURATION-CHARACTERISTIC-LIMIT-WITH-RP-AND-SELECTION-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-FULL-EUCLIDEAN-SHARP-CUTOFF-REFLECTION-POSITIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-TIME-ZERO-CONFIGURATION-ONLY-FULL-WEYL-STATE",
    "NG-2026-08-04-PRE-A-CP1-CL8-CONSTRUCTIVE-NORMALIZABILITY-ONLY-PHYSICAL-STATE-SELECTION",
)
EXPLORATION_ID = "EXP-000766"
CORRECTION_ID = "EXP-000767"
PARENT_IDS = (
    "PA-CP1-CL8-MATRIX-COUNTERTERM-STATE-COMPACTNESS-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-ORDERED-Q3-GAUSSIAN-TANGENT-REGULATOR-ROUTE-SPLIT-v0",
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


def canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


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
    match = re.search(r"([0-9]+)/([0-9]+) PASS$", stdout)
    if match is None:
        raise AssertionError(f"unexpected child output: {stdout!r}")
    return {"passed": int(match.group(1)), "total": int(match.group(2))}


def assertion_names(payload: dict[str, Any]) -> set[str]:
    return {row["name"] for row in payload["assertions"]}


def exploration_record(exploration_id: str) -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == exploration_id:
            return record
    raise AssertionError(f"missing {exploration_id}")


def imported_modules(path: Path) -> tuple[set[str], set[str], set[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    direct = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    from_modules = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    dynamic = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval", "compile"}}
    return direct, from_modules, dynamic


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate.split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("correction exploration id", manifest["correction_exploration_id"] == CORRECTION_ID, manifest["correction_exploration_id"], CORRECTION_ID, "identity")
    audit.check("package version", manifest["package_version"] == "0.1.1", manifest["package_version"], "0.1.1", "identity")
    audit.check("parent ids", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], list(PARENT_IDS), "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    support_contract = manifest["theorem_hypothesis_instantiation"]["maximal_formal_support"]
    audit.check("maximal support contract", support_contract == {
        "support_count": 64,
        "A_minus_count": 61,
        "degree_counts": {"0": 1, "1": 8, "2": 20, "3": 32},
        "support_64_attainment_conditions": ["lambda!=0", "eta_int!=0", "m_int+3 eta_int!=0"],
        "A_minus_61_attainment_condition": "lambda!=0",
        "actual_support_relation": "subset",
    }, support_contract, "exact typed support contract", "contracts")
    terminal_contract = manifest["density_convergence_corollary"]["finite_to_terminal_martingale"]
    audit.check("terminal martingale contract", terminal_contract == {
        "finite_identity": "for every M>=N, E[R_M|G_N]=R_N",
        "limit_input": "Proposition A.1 and estimate (A.3) give R_M->R in L1",
        "terminal_identity": "E[R|G_N]=R_N",
        "centered_degrees": [1, 2, 3, 4],
    }, terminal_contract, "exact terminal contract", "contracts")
    projected_contract = manifest["reflection_positivity_no_go"]["projected_law_scope"]
    audit.check("projected RP contract", projected_contract == {
        "cutoff": 1,
        "law": "nu_1=(P_1)_#(rho_1 mu)",
        "Gaussian_b1_positive": True,
        "interacting_b1_positive": True,
        "lifted_rho1_mu_decided": False,
        "higher_projected_N_decided": False,
        "limiting_local_measure_decided": False,
    }, projected_contract, "exact projected-law contract", "contracts")
    volume_contract = manifest["selection_no_go"]["volume_convention"]
    audit.check("selection volume contract", volume_contract == {
        "ratio": "c exp(-V|x|^2/2)",
        "V": "integral_T2 1 dz",
        "normalized_Haar_V": 1,
    }, volume_contract, "exact volume contract", "contracts")

    with tempfile.TemporaryDirectory(prefix="tect-phi2-integrated-") as temporary:
        temporary_path = Path(temporary)
        primary, primary_stdout = run_child(PRIMARY, temporary_path / "primary.json")
        independent, independent_stdout = run_child(INDEPENDENT, temporary_path / "independent.json")
    summaries = {"primary": child_summary(primary_stdout), "independent": child_summary(independent_stdout)}
    audit.check("primary child all pass", summaries["primary"]["passed"] == summaries["primary"]["total"], summaries["primary"], "all pass", "children")
    audit.check("independent child all pass", summaries["independent"]["passed"] == summaries["independent"]["total"], summaries["independent"], "all pass", "children")
    for name, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{name} candidate", child["candidate_id"] == CANDIDATE_ID, child["candidate_id"], CANDIDATE_ID, "children")
        audit.check(f"{name} result", child["result_id"] == RESULT_ID, child["result_id"], RESULT_ID, "children")
        audit.check(f"{name} negatives", tuple(child["negative_ids"]) == NEGATIVE_IDS, child["negative_ids"], list(NEGATIVE_IDS), "children")
        audit.check(f"{name} scope", child["scope"] == manifest["scope"], child["scope"], manifest["scope"], "children")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))
    audit.check("stored primary fresh", canonical_bytes(primary_stored) == canonical_bytes(primary), sha256(PRIMARY_STORED), "fresh child payload", "stored")
    audit.check("stored independent fresh", canonical_bytes(independent_stored) == canonical_bytes(independent), sha256(INDEPENDENT_STORED), "fresh child payload", "stored")
    audit.check("primary script hash", primary["source_sha256"]["script"] == sha256(PRIMARY), primary["source_sha256"]["script"], sha256(PRIMARY), "stored")
    audit.check("independent script hash", independent["source_sha256"]["script"] == sha256(INDEPENDENT), independent["source_sha256"]["script"], sha256(INDEPENDENT), "stored")
    audit.check("primary manifest hash", primary["source_sha256"]["manifest"] == sha256(MANIFEST), primary["source_sha256"]["manifest"], sha256(MANIFEST), "stored")
    audit.check("independent manifest hash", independent["source_sha256"]["manifest"] == sha256(MANIFEST), independent["source_sha256"]["manifest"], sha256(MANIFEST), "stored")
    audit.check("primary certificate hash", primary["source_sha256"]["certificate"] == sha256(CERTIFICATE), primary["source_sha256"]["certificate"], sha256(CERTIFICATE), "stored")
    audit.check("independent certificate hash", independent["source_sha256"]["certificate"] == sha256(CERTIFICATE), independent["source_sha256"]["certificate"], sha256(CERTIFICATE), "stored")

    primary_names = assertion_names(primary)
    independent_names = assertion_names(independent)
    primary_required = (
        "maximal formal support count",
        "support 64 attainment conditions",
        "A-minus 61 lambda condition",
        "diagonal quadratic cancellation leaves 56",
        "descendant degree counts",
        "quartic dominates auxiliary",
        "Q3 quartic coercivity identity",
        "Wick martingale degree 4",
        "Wick Hermite centering degree 1",
        "Wick Hermite centering degree 2",
        "Wick Hermite centering degree 3",
        "Wick Hermite centering degree 4",
        "finite-to-terminal L1 passage",
        "temporal tail finite fixture",
        "whole quadratic Wick scalar",
        "RP negative form identity",
        "RP orientation sentinel",
        "projected interacting b1 positive",
        "lifted rho1 RP undecided",
        "chirped P variance",
        "normalized Haar volume",
        "regulators not identical",
        "scope false Pre_A_complete",
    )
    independent_required = (
        "maximal formal support count",
        "support 64 conditions",
        "A-minus 61 condition",
        "cancelled diagonal support count",
        "envelope counts",
        "q mutation sentinel",
        "Hermite conditional degree 4",
        "Hermite centering degree 1",
        "Hermite centering degree 2",
        "Hermite centering degree 3",
        "Hermite centering degree 4",
        "terminal martingale L1 input",
        "temporal tail bound",
        "translation sign sentinel",
        "reflection exact pair",
        "ordinary orientation positive",
        "projected law interacting b1",
        "full lifted law undecided",
        "chirped momentum variance",
        "chirp mutation sentinel",
        "normalized Haar volume",
        "regulator mismatch",
        "scope Pre_A_complete",
    )
    for name in primary_required:
        audit.check(f"primary coverage {name}", name in primary_names, name, "present", "coverage")
    for name in independent_required:
        audit.check(f"independent coverage {name}", name in independent_names, name, "present", "coverage")

    direct, from_modules, dynamic = imported_modules(INDEPENDENT)
    audit.check("independent AST import firewall", PRIMARY.stem not in direct and PRIMARY.stem not in from_modules, sorted(direct | from_modules), f"not {PRIMARY.stem}", "independence")
    audit.check("independent AST dynamic firewall", not dynamic and "runpy" not in direct, {"dynamic": sorted(dynamic), "imports": sorted(direct)}, "none", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    for key in ("maximal_support_count", "cancelled_support_count", "maximum_auxiliary_power", "Wick_threshold"):
        audit.check(f"cross oracle {key}", primary["derived"][key] == independent["derived"][key], primary["derived"][key], independent["derived"][key], "cross")
    audit.check("cross descendant counts", primary["derived"]["descendant_degree_counts"] == independent["derived"]["descendant_degree_counts"], primary["derived"]["descendant_degree_counts"], independent["derived"]["descendant_degree_counts"], "cross")
    audit.check("cross Wick centered means", primary["derived"]["Hermite_centered_means"] == independent["derived"]["Hermite_centered_means"] == {"1": "0", "2": "0", "3": "0", "4": "0"}, primary["derived"]["Hermite_centered_means"], independent["derived"]["Hermite_centered_means"], "cross")
    audit.check("cross projected-law scope", primary["derived"]["projected_law_scope"] == independent["derived"]["projected_law_scope"] == projected_contract, primary["derived"]["projected_law_scope"], independent["derived"]["projected_law_scope"], "cross")
    audit.check("cross normalized Haar volume", primary["derived"]["normalized_Haar_V"] == independent["derived"]["normalized_Haar_V"] == 1, primary["derived"]["normalized_Haar_V"], independent["derived"]["normalized_Haar_V"], "cross")
    audit.check("cross temporal start diversity", primary["derived"]["temporal_tail"]["start"] != independent["derived"]["temporal_tail"]["start"], primary["derived"]["temporal_tail"]["start"], independent["derived"]["temporal_tail"]["start"], "cross")
    wick_scalar_fixture = -4 * 3 * 7 - 12 * 3 * 4
    primary_wick_formula = primary["derived"]["Wick_scalar"].replace(" ", "")
    audit.check("primary Wick scalar formula", "-12*C*eta_int" in primary_wick_formula and "-4*C*m_int" in primary_wick_formula, primary["derived"]["Wick_scalar"], "symbolic formula", "cross")
    audit.check("independent Wick scalar fixture", int(independent["derived"]["Wick_scalar"]) == wick_scalar_fixture, independent["derived"]["Wick_scalar"], wick_scalar_fixture, "cross")
    primary_reflection_numeric = float(-7 + 4 * math.sqrt(3.0))
    independent_reflection_numeric = float(independent["derived"]["reflection_form"]["numeric"])
    audit.check("cross reflection numeric", abs(primary_reflection_numeric - independent_reflection_numeric) < 1e-14, primary_reflection_numeric, independent_reflection_numeric, "cross")
    audit.check("cross momentum base", primary["derived"]["momentum_variances"]["base"] == independent["derived"]["momentum_variances"]["base"], primary["derived"]["momentum_variances"]["base"], independent["derived"]["momentum_variances"]["base"], "cross")
    audit.check("cross momentum chirped", primary["derived"]["momentum_variances"]["chirped"] == independent["derived"]["momentum_variances"]["chirped"], primary["derived"]["momentum_variances"]["chirped"], independent["derived"]["momentum_variances"]["chirped"], "cross")
    primary_spectral = float(4 * math.pi**2 / 9)
    audit.check("cross spectral symbol", abs(primary_spectral - float(independent["derived"]["regulator_symbols"]["spectral"])) < 1e-14, primary_spectral, independent["derived"]["regulator_symbols"]["spectral"], "cross")
    audit.check("cross centered symbol", abs(float(independent["derived"]["regulator_symbols"]["centered"]) - 3.0) < 1e-14 and primary["derived"]["regulator_symbols"]["centered"] == "3", primary["derived"]["regulator_symbols"]["centered"], independent["derived"]["regulator_symbols"]["centered"], "cross")

    certificate_phrases = (
        "The exact eight-component Q3 polynomial passes an established multivariate",
        "R_N=\\mathbb E_\\mu[R\\mid G_N]",
        "\\mathbb E_\\mu[R_M\\mid G_N]=R_N",
        "uniform high-moment estimate (A.3)",
        "m_int=-3 eta_int",
        "common Gaussian distribution space",
        "commuting time-zero configuration subgroup",
        "do not identify a full Weyl state",
        "induced projected interacting law",
        "not the lifted law `rho_1 mu`",
        "normalized Haar measure",
        "K_int=K_target-m0^2 I",
        "It does not itself construct a vacuum",
        "cannot prove a thermodynamic phase transition",
        "below-empty-space comparison",
    )
    for phrase in certificate_phrases:
        audit.check(f"certificate phrase {phrase[:35]}", phrase in certificate_flat, phrase, "present", "certificate")
    package_files = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)
    non_ascii = {
        str(path.relative_to(REPO)): sorted({character for character in path.read_text(encoding="utf-8") if ord(character) > 127})
        for path in package_files
    }
    audit.check("package ASCII clean", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "hygiene")

    negative_text = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"negative registered {negative_id}", f"### {negative_id} " in negative_text, negative_id, "detailed entry", "records")
    index_text = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index registered", MANIFEST.name in index_text and CERTIFICATE.name in index_text, [MANIFEST.name, CERTIFICATE.name], "both", "records")
    exploration = exploration_record(EXPLORATION_ID)
    audit.check("exploration verdict", exploration["verdict"] == "advanced", exploration["verdict"], "advanced", "records")
    audit.check("exploration claim nonbearing", exploration["formal_refs"].get("results", []) == [], exploration["formal_refs"], "empty results", "records")
    audit.check("exploration negatives", tuple(exploration["formal_refs"].get("negatives", [])) == NEGATIVE_IDS, exploration["formal_refs"], list(NEGATIVE_IDS), "records")
    audit.check("exploration continues prior route", any(item.get("id") == "EXP-000765" and item.get("relation") == "continues" for item in exploration.get("related", [])), exploration.get("related", []), "continues EXP-000765", "records")
    audit.check("exploration next gate", manifest["gate_resolution"]["next_gate"] in exploration["next_action"], exploration["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    correction = exploration_record(CORRECTION_ID)
    audit.check("correction verdict", correction["verdict"] == "advanced", correction["verdict"], "advanced", "records")
    audit.check("correction claim", correction["claim_ids"] == ["C6-SPACETIME-SIGNATURE"], correction["claim_ids"], ["C6-SPACETIME-SIGNATURE"], "records")
    audit.check("correction task", correction["task_id"] == "T-054" and correction["gate_ids"] == [], {"task": correction["task_id"], "gates": correction["gate_ids"]}, "T-054 with no gate closure", "records")
    audit.check("correction results empty", correction["formal_refs"].get("results", []) == [], correction["formal_refs"], "empty results", "records")
    audit.check("correction negatives unchanged", tuple(correction["formal_refs"].get("negatives", [])) == NEGATIVE_IDS, correction["formal_refs"], list(NEGATIVE_IDS), "records")
    audit.check("correction events empty", correction["formal_refs"].get("events", []) == [], correction["formal_refs"], "empty events", "records")
    audit.check("correction relation", any(item.get("id") == EXPLORATION_ID and item.get("relation") == "corrects" for item in correction.get("related", [])), correction.get("related", []), "corrects EXP-000766", "records")
    for phrase in ("m_int+3*eta_int", "E[R_M|G_N]=R_N", "estimate (A.3)", "induced N=1 law", "rho_1 mu", "V=1 for normalized Haar"):
        audit.check(f"correction finding {phrase[:25]}", phrase in correction["finding"], phrase, "present", "records")
    audit.check("correction boundary C6", all(phrase in correction["boundary"] for phrase in ("negative IDs", "C6", "CP1", "Pre-A")), correction["boundary"], "unchanged formal boundaries", "records")
    audit.check("correction next gate", manifest["gate_resolution"]["next_gate"] in correction["next_action"], correction["next_action"], manifest["gate_resolution"]["next_gate"], "records")
    todo_text = (REPO / "todo/todo.json").read_text(encoding="utf-8")
    audit.check("TODO route recorded", EXPLORATION_ID in todo_text and CORRECTION_ID in todo_text and manifest["gate_resolution"]["next_gate"] in todo_text, [EXPLORATION_ID, CORRECTION_ID], "TODO and gate", "records")
    changelog_text = (REPO / "changelog/log.jsonl").read_text(encoding="utf-8")
    audit.check("changelog route recorded", EXPLORATION_ID in changelog_text and CORRECTION_ID in changelog_text and MANIFEST.name in changelog_text, [EXPLORATION_ID, CORRECTION_ID], "changelog and manifest", "records")
    lineage_text = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    for kind in ("primary", "independent", "integrated"):
        audit.check(f"C6 lineage {kind}", f"runs/2026-08-04-{kind}-{SLUG}/" in lineage_text, kind, "run", "records")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    audit.check("C6 advancement false", manifest["scope"]["C6_advanced"] is False, manifest["scope"]["C6_advanced"], False, "claim_firewall")
    audit.check("Pre-A false", manifest["scope"]["Pre_A_complete"] is False, manifest["scope"]["Pre_A_complete"], False, "claim_firewall")
    audit.check("canonical CL8 false", manifest["scope"]["canonical_CL8_regulator_identified"] is False, manifest["scope"]["canonical_CL8_regulator_identified"], False, "claim_firewall")
    audit.check("full Weyl false", manifest["scope"]["full_phase_space_Weyl_CCR"] is False, manifest["scope"]["full_phase_space_Weyl_CCR"], False, "claim_firewall")
    audit.check("below empty space false", manifest["scope"]["below_empty_space_comparison"] is False, manifest["scope"]["below_empty_space_comparison"], False, "claim_firewall")

    catalog = (REPO / "CATALOG.md").read_text(encoding="utf-8")
    proof_map = (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8")
    audit.check("catalog manifest", MANIFEST.name in catalog, MANIFEST.name, "catalogued", "generated")
    audit.check("catalog certificate", CERTIFICATE.name in catalog, CERTIFICATE.name, "catalogued", "generated")
    audit.check("proof map exploration", EXPLORATION_ID in proof_map, EXPLORATION_ID, "mapped", "generated")
    audit.check("proof map correction", CORRECTION_ID in proof_map, CORRECTION_ID, "mapped", "generated")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"proof map negative {negative_id}", negative_id in proof_map, negative_id, "mapped", "generated")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(PARENT_IDS),
        "negative_ids": list(NEGATIVE_IDS),
        "exploration_id": EXPLORATION_ID,
        "correction_exploration_id": CORRECTION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE), "primary": sha256(PRIMARY), "independent": sha256(INDEPENDENT)},
        "child_summaries": summaries,
        "cross_oracles": {
            "maximal_support_count": primary["derived"]["maximal_support_count"],
            "cancelled_support_count": primary["derived"]["cancelled_support_count"],
            "descendant_degree_counts": primary["derived"]["descendant_degree_counts"],
            "Hermite_centered_means": primary["derived"]["Hermite_centered_means"],
            "maximum_auxiliary_power": primary["derived"]["maximum_auxiliary_power"],
            "Wick_threshold": primary["derived"]["Wick_threshold"],
            "reflection_numeric": independent_reflection_numeric,
            "projected_law_scope": projected_contract,
            "normalized_Haar_V": volume_contract["normalized_Haar_V"],
            "momentum_variances": independent["derived"]["momentum_variances"],
            "regulator_symbols": independent["derived"]["regulator_symbols"],
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
