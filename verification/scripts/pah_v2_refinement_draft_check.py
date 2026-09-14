#!/usr/bin/env python3
"""Check the PAH-v2 comparison DRAFT's integrity, not a comparison theorem.

The source hashes are INPUTS from issued v2/R-570 authority. Derived counts
come from checks. Hostile mutations test documentary authority boundaries
only. No model is enumerated, no Gibbs/rate/defect value is computed, and no
mathematical or independent-person review is claimed. --require-ready exits
2 for this uninstantiated draft, even when documentary checks pass.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "strategy/pa-hyp/PAH-v2-refinement-contract-draft.json"
NOTE = ROOT / "strategy/pa-hyp/PAH-v2-refinement-decision.md"
OUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-refinement/draft.json"
# INPUTS: immutable authority checksums, not computed numerical conclusions.
SOURCE_ANCHORS = {
    "strategy/pa-hyp/PAH-001-v1.json": "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    "strategy/pa-hyp/PAH-001-v2-r2.json": "2e1f5f21796a224f80141572dd9dd6451dd2cbba86233998ea992aa2bff6e36a",
    "strategy/pa-hyp/PAH-v2-finite-result-v1.json": "9595fbb674443962c2790e4c0737eece6cb086ed9ba9d47783e7777907c678e7",
    "codes/foundations/pah_v2_root_enumerator.py": "37044e1e7bc274985823d095a21cd6759dbe9e4c5be303b69464d02846291cc2",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer(data, path):
    value = data
    for part in path.strip("/").split("/"):
        value = value[part]
    return value


def validate(data, parent):
    """Schema/content consistency for this draft; no existence inference."""
    checks = []

    def require(name, condition):
        assert condition, name
        checks.append(name)

    require("unapproved uninstantiated status", data["status"] == "DRAFT_NOT_APPROVED_NOT_INSTANTIATED")
    require("no approved source pin", all(data[k] is None for k in ("approved_contract", "approval_record", "operative_hash_pin")))
    require("source anchors immutable", data["source_pins"] == SOURCE_ANCHORS)
    required = ("authority", "immutable_model", "tower_contract", "ordered_limits", "comparison_interface", "root_correspondence", "common_cylinder", "preregistered_tests", "readiness", "verification_scope", "non_claims")
    require("all requested roles present", all(data.get(k) for k in required))
    require("inherited limit order", data["ordered_limits"]["order"] == [row["id"] for row in parent["ordered_limits"]["order"]])
    require("sup norm not silently replaced", data["immutable_model"]["common_norm"] == "The inherited supremum norm, not a substituted Gibbs-L2 norm. Gibbs-L2 is separately reported only as a weaker diagnostic.")
    require("fine to coarse state direction", data["comparison_interface"]["state_map_direction"] == "fine_to_coarse")
    require("coarse to fine observable direction", data["comparison_interface"]["observable_map_direction"] == "coarse_to_fine_pullback")
    require("no Gibbs projectivity assumption", data["comparison_interface"]["ensemble_identification"] == "NOT_ASSUMED")
    require("unconstructed common limiting core", data["common_cylinder"]["limiting_core_status"] == "NOT_CONSTRUCTED")
    require("no defect computation admitted", data["preregistered_tests"]["evaluation_status"] == "NOT_RUN_NO_INSTANTIATED_CONTRACT")
    require("ready cannot mean a template PASS", data["readiness"]["status"] == "HOLD_FOR_DEFINITIONS_AND_OWNER_APPROVAL")
    missing = data["readiness"]["missing"]
    require("all missing fields reported", {row["id"] for row in missing} == {"TOWER", "MAP", "ROOT", "APPROVAL"} and len(missing) == len({row["id"] for row in missing}))
    for row in missing:
        require("unfilled input " + row["id"], pointer(data, row["path"]) is None and bool(row["required"]))
    require("Lean not inherited", data["verification_scope"]["Lean"].startswith("NOT_RUN_NO_APPROVED_INSTANTIATION"))
    require("independent review not fabricated", data["verification_scope"]["independent_mathematical_review"] == "NOT_RUN_NO_APPROVED_INSTANTIATION")
    require("separate exact weak and state criteria", all(data["preregistered_tests"].get(k) for k in ("exact_defect", "expanded_defect", "sup_defect", "gibbs_diagnostic", "state_defect", "eventual_exact_target", "controlled_target", "falsifiers")))
    require("no root multiplicity division", "No division by preimage size" in data["root_correspondence"]["multiplicity"])
    require("complete core not constants alone", "not only constants" in data["common_cylinder"]["support_rule"])
    require("no physical promotion", any("No dynamics convergence" in line for line in data["non_claims"]))
    return checks


def hostile(data, parent):
    mutations = [
        ("claimed approval", lambda d: d.__setitem__("approval_record", "synthetic approval")),
        ("operative pin on an unapproved draft", lambda d: d.__setitem__("operative_hash_pin", "0" * 64)),
        ("reversed state map", lambda d: d["comparison_interface"].__setitem__("state_map_direction", "coarse_to_fine")),
        ("reversed observable map", lambda d: d["comparison_interface"].__setitem__("observable_map_direction", "fine_to_coarse")),
        ("changed limit order", lambda d: d["ordered_limits"]["order"].reverse()),
        ("Gibbs pushforward equated", lambda d: d["comparison_interface"].__setitem__("ensemble_identification", "ASSUMED")),
        ("Gibbs-L2 substituted", lambda d: d["immutable_model"].__setitem__("common_norm", "Gibbs-L2")),
        ("template declared ready", lambda d: d["readiness"].__setitem__("status", "READY")),
        ("uninstantiated core declared complete", lambda d: d["common_cylinder"].__setitem__("limiting_core_status", "COMPLETE")),
        ("missing map concealed", lambda d: d["readiness"]["missing"].pop(1)),
        ("fake map implementation", lambda d: d["comparison_interface"].__setitem__("implementation", "copy legacy map")),
        ("channel division", lambda d: d["root_correspondence"].__setitem__("multiplicity", "Divide by preimage size")),
        ("inherited Lean PASS", lambda d: d["verification_scope"].__setitem__("Lean", "PASS via R-570")),
        ("claimed independent-person review", lambda d: d["verification_scope"].__setitem__("independent_mathematical_review", "PASS")),
    ]
    rejected = []
    for name, mutate in mutations:
        altered = deepcopy(data)
        mutate(altered)
        try:
            validate(altered, parent)
        except (AssertionError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError("hostile mutation accepted: " + name)
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    for name, expected in SOURCE_ANCHORS.items():
        assert sha(ROOT / name) == expected, name
    data = json.loads(DRAFT.read_text(encoding="utf-8"))
    parent = json.loads((ROOT / "strategy/pa-hyp/PAH-001-v1.json").read_text(encoding="utf-8"))
    checks = validate(data, parent)
    rejected = hostile(data, parent)
    for path in (DRAFT, NOTE, Path(__file__)):
        raw = path.read_bytes()
        assert b"\r" not in raw and raw.endswith(b"\n"), path
        raw.decode("ascii")  # New tracked documentary artifacts are English-only.
    result = {
        "schema": "tect/pah-v2-refinement-draft-check/1.0",
        "integrity_status": "PASS",
        "contract_status": data["readiness"]["status"],
        "source_pins": SOURCE_ANCHORS,
        "draft_sha256_integrity_only": sha(DRAFT),
        "note_sha256": sha(NOTE),
        "script_sha256": sha(Path(__file__)),
        "checks": checks,
        "hostile_documentary_mutations_rejected": rejected,
        "missing_inputs": data["readiness"]["missing"],
        "math_runs": "NOT_RUN_NO_APPROVED_INSTANTIATION",
        "non_claims": "Metadata checks do not prove existence of maps, symmetry, dynamics, convergence or physical identity; no external-person review.",
    }
    if args.require_ready:
        print("PAH-V2-REFINEMENT: HOLD (TOWER, MAP, ROOT and APPROVAL absent; no operative contract)")
        return 2
    if args.check:
        assert json.loads(OUT.read_text(encoding="utf-8")) == result, "stored draft run differs"
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with OUT.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print(f"PAH-V2-REFINEMENT-DRAFT: PASS ({len(checks)} documentary checks; {len(rejected)} hostile mutations rejected)")
    print("Contract readiness: " + result["contract_status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
