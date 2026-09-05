#!/usr/bin/env python3
"""Independent replay of the R503 finite-sector mixture Cauchy bound."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-mixture-cauchy-lean-manifest.json"
PAH001 = ROOT / "strategy/pa-hyp/PAH-001-v1.json"
OMC012 = ROOT / "strategy/pa-hyp/PAH-OMC-012-full-Q-graded-domain-v1.json"
OMC014 = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-v1.json"
OMC014_MANIFEST = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-cylinder-limit-manifest.json"
WEIGHT_INTAKE = ROOT / "strategy/pa-hyp/PAH-OMC-014-full-q-gibbs-limit-next-evidence-contract-v1.json"
R501 = ROOT / "strategy/pa-hyp/PAH-OMC-014-identifiability-lean-manifest.json"
LEAN = ROOT / "verification/lean/Tect/R503.lean"
REGISTRY = ROOT / "verification/lean/registry.json"
RUN_DIR = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-09-05-pah-omc014-mixture-cauchy-lean"
TOOLCHAIN = "leanprover/lean4:v4.32.1"
LEAN_PIN = "0bf2dd8506c100d727bdc79e25b2d2fd06638093206c8657fb2cc3bb9ebb5ffc"
PINS = {
    PAH001: "03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37",
    OMC012: "180228b83e44f46406b302c97ff6caab023240eeaa19997618012074930f3e72",
    OMC014: "1389bf64b2f26f267aa35bdfbee59cced2d16d8a5dcefd8e34a3deabb41d31b0",
    OMC014_MANIFEST: "072a55e76c47e2917a94e010682a82819eaf6e062a59d0a7733b654fb6c0e812",
    WEIGHT_INTAKE: "0ef41a6dd183458cea7ac45b84119dd820c7f5decdc8ef9ee393caca4031c502",
    R501: "1ef79e5a354e2a7abf32cbe92a98501a206cb5feacfef4a246d49453ab45d497",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
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


def compile_lean() -> dict[str, Any]:
    encoded = TOOLCHAIN.replace("/", "--").replace(":", "---")
    base = Path.home() / ".elan" / "toolchains" / encoded / "bin"
    lake = next((base / name for name in ("lake.exe", "lake") if (base / name).is_file()), None)
    if lake is None:
        found = shutil.which("lake")
        lake = Path(found) if found else None
    if lake is None:
        return {"status": "FAIL", "returncode": None, "output": "pinned lake missing"}
    result = subprocess.run(
        [str(lake), "env", "lean", "Tect/R503.lean"],
        cwd=LEAN.parent.parent,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        timeout=180,
    )
    output = (result.stdout + "\n" + result.stderr).strip()
    return {
        "status": "PASS" if result.returncode == 0 and "error:" not in output.lower() else "FAIL",
        "returncode": result.returncode,
        "command": "lake env lean Tect/R503.lean",
        "output": output[-2000:],
    }


def run(output: Path = RUN_DIR / "independent.json") -> dict[str, Any]:
    manifest, pah, omc012, omc014, omc014_manifest, intake, r501, registry = (
        read(path) for path in (MANIFEST, PAH001, OMC012, OMC014, OMC014_MANIFEST, WEIGHT_INTAKE, R501, REGISTRY)
    )
    source_bytes = LEAN.read_bytes()
    source = source_bytes.decode("utf-8")
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any) -> None:
        rows.append({"name": name, "pass": bool(ok), "actual": actual, "expected": expected})

    actual_pins = {str(path): sha(path) for path in PINS}
    expected_pins = {str(path): expected for path, expected in PINS.items()}
    check("all parent hashes", actual_pins == expected_pins, actual_pins, expected_pins)
    status = manifest.get("status", {})
    provenance = manifest.get("provenance", {})
    check(
        "manifest remains conditional HOLD",
        status.get("verdict") == "HOLD_FOR_EVIDENCE"
        and status.get("claim_bearing") is False
        and status.get("active_gate_change") is False
        and provenance.get("source_law_present") is False,
        {"status": status, "provenance": provenance},
        "HOLD/no law/no gate change",
    )
    check(
        "parent limit remains undefined",
        omc014.get("status", {}).get("omega_status") == "NOT_DEFINED"
        and str(omc012.get("status", {}).get("global_normalized_gibbs_measure", "")).startswith("NOT_DEFINED"),
        {
            "omega": omc014.get("status", {}).get("omega_status"),
            "global": omc012.get("status", {}).get("global_normalized_gibbs_measure"),
        },
        "undefined",
    )
    check(
        "weight intake is still uninstantiated",
        intake.get("status", {}).get("verdict") == "HOLD_FOR_EVIDENCE"
        and intake.get("status", {}).get("source_law") == "ABSENT_IN_PARENT",
        intake.get("status"),
        "HOLD/ABSENT_IN_PARENT",
    )
    check(
        "fixed finite index semantics",
        "one finite sector index type" in manifest.get("fixed_scope", {}).get("finite_index", "")
        and "Growing-Q tails" in manifest.get("fixed_scope", {}).get("finite_index", ""),
        manifest.get("fixed_scope", {}).get("finite_index"),
        "finite block with explicit tail separation",
    )

    ew, ea, C = Fraction(1, 10), Fraction(1, 20), Fraction(2)
    weights_1 = (Fraction(1), Fraction(0), Fraction(0))
    weights_2 = (Fraction(9, 10), Fraction(1, 10), Fraction(0))
    components_1 = (Fraction(1), Fraction(0), Fraction(2))
    components_2 = (Fraction(19, 20), Fraction(1, 20), Fraction(2))
    weight_drift = tuple(abs(x - y) for x, y in zip(weights_1, weights_2))
    component_drift = tuple(abs(x - y) for x, y in zip(components_1, components_2))
    component_abs = tuple(abs(x) for x in components_2)
    value_1 = sum(w * a for w, a in zip(weights_1, components_1))
    value_2 = sum(w * a for w, a in zip(weights_2, components_2))
    actual = abs(value_1 - value_2)
    bound = Fraction(len(weights_1)) * (C * ew + ea)
    check(
        "independent pointwise hypotheses",
        max(weight_drift) <= ew and max(component_drift) <= ea and max(component_abs) <= C and max(abs(w) for w in weights_1) <= 1,
        {
            "e_w": str(ew),
            "e_a": str(ea),
            "C": str(C),
            "weight_drift": [str(x) for x in weight_drift],
            "component_drift": [str(x) for x in component_drift],
        },
        "all finite hypotheses",
    )
    check(
        "independent exact mixture arithmetic",
        actual <= bound and value_1 == Fraction(1) and value_2 == Fraction(43, 50),
        {"value_1": str(value_1), "value_2": str(value_2), "actual": str(actual), "bound": str(bound)},
        "actual <= card*(C*e_w+e_a)",
    )
    declarations = ["finite_mixture_difference_bound"]
    declared = re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", source)
    registry_item = next((item for item in registry.get("entrypoints", []) if item.get("path") == "verification/lean/Tect/R503.lean"), None)
    check(
        "Lean declaration/hash/registry",
        all(name in declared for name in declarations) and sha(LEAN) == LEAN_PIN and registry_item is not None and registry_item.get("sha256") == LEAN_PIN,
        {"declared": declared, "registry": registry_item, "sha256": sha(LEAN)},
        declarations,
    )
    check(
        "Lean source policy",
        b"\r" not in source_bytes and source_bytes.endswith(b"\n") and not any(token in source for token in ("sorry", "admit", "axiom", "unsafe")),
        {"lf": b"\r" not in source_bytes, "final": source_bytes.endswith(b"\n")},
        "LF/no escape",
    )
    lean = compile_lean()
    check("Lean compilation", lean["status"] == "PASS", lean, "PASS")
    check(
        "non-claim firewall",
        status.get("physical_promotion") is False
        and any("projective consistency" in item.lower() for item in manifest.get("non_claims", []))
        and any("physical" in item.lower() for item in manifest.get("non_claims", [])),
        {"physical_promotion": status.get("physical_promotion"), "non_claims": manifest.get("non_claims", [])},
        "no physical or global-limit promotion",
    )

    failed = [row for row in rows if not row["pass"]]
    payload = {
        "schema": "tect/pah-omc014-mixture-cauchy-lean-independent/1.0",
        "run_kind": "independent",
        "audit_id": "PAH-OMC-014-MIXTURE-CAUCHY-LEAN-INDEPENDENT-001",
        "task_id": "T-054",
        "verification": "PASS" if not failed else "FAIL",
        "verdict": "HOLD_FOR_EVIDENCE",
        "classification": "AUXILIARY_SUPPORT_FINITE_MIXTURE_BOUND",
        "assertion_count": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "assertions": rows,
        "source_hashes": {"manifest": sha(MANIFEST), "lean": sha(LEAN), **{path.name: expected for path, expected in PINS.items()}},
        "scope": {"finite_index_card": len(weights_1), "weight_error": str(ew), "component_error": str(ea), "component_bound": str(C), "tail": "not supplied"},
        "derived": {"actual_mixture_drift": str(actual), "certified_upper_bound": str(bound), "formula": "card(ι)*(C*e_w+e_a)"},
        "claim_bearing": False,
        "active_gate_change": False,
        "source_law_present": False,
        "omega_status": "NOT_DEFINED",
        "projective_consistency": "NOT_TESTABLE",
        "weak_cylinder_limit": "NOT_TESTABLE",
        "non_claims": manifest.get("non_claims", []),
        "next_question": manifest.get("next_question"),
        "reproduction": manifest.get("reproduction", {}),
        "lean": lean,
    }
    atomic_json(output, payload)
    print(f"{payload['audit_id']} {payload['verification']} {payload['passed']}/{payload['assertion_count']}; verdict={payload['verdict']}")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=RUN_DIR / "independent.json")
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)["verification"] == "PASS" else 1)
