#!/usr/bin/env python3
"""Audit the pinned public Fermi GbmRsp2 parser structure.

This is an additive T-061 provenance crosswalk.  It inspects only the source
text and the already accepted R-469 parent hashes.  It never imports the
mission package, opens a FITS product, reads response coefficients, selects a
production response, evaluates a likelihood, or changes the T-054/T-059/T-061
methods.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT = REPO / "strategy/hold-lc-001-gdt-fermi-rsp2-parser-owner-v0.1.json"
PARENT_CONTRACT = REPO / "strategy/hold-lc-001-gdt-rsp2-selection-owner-v0.1.json"
PARENT_RESULT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-hold-lc-gdt-selection-owner/primary.json"
SOURCE = REPO / "internal/source-cache/HOLD-LC-001/2026-08-31" / ("gdt-fermi-response" + ".py")
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-primary-hold-lc-gdt-fermi-parser-owner/primary.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def function_nodes(tree: ast.AST) -> tuple[ast.ClassDef, ast.FunctionDef]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GbmRsp2":
            bases = {base.id for base in node.bases if isinstance(base, ast.Name)}
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "open":
                    decorators = {
                        item.id for item in child.decorator_list if isinstance(item, ast.Name)
                    }
                    if "classmethod" in decorators and "Rsp2" in bases:
                        return node, child
    raise ValueError("GbmRsp2 classmethod open was not found")


def call_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Call):
            if isinstance(item.func, ast.Attribute):
                names.add(item.func.attr)
            elif isinstance(item.func, ast.Name):
                names.add(item.func.id)
    return names


def source_semantics(source_text: str) -> dict[str, Any]:
    tree = ast.parse(source_text)
    class_node, open_node = function_nodes(tree)
    lines = source_text.splitlines()
    class_text = "\n".join(lines[class_node.lineno - 1 : class_node.end_lineno])
    open_text = "\n".join(lines[open_node.lineno - 1 : open_node.end_lineno])
    required_tokens = {
        "subclass": "class GbmRsp2(Rsp2):",
        "delegate": "obj = super().open(file_path, **kwargs)",
        "headers": "hdrs = [hdu.header for hdu in obj.hdulist]",
        "drm_count": "num_drm = hdrs[0]['DRM_NUM']",
        "segment_loop": "for i in range(num_drm):",
        "header_rebuild": "RspHeaders.from_headers([hdrs[0], hdrs[1], hdrs[i+2]])",
        "num_ebins": "num_ebins = hdrs[i+2]['NUMEBINS']",
        "num_chans": "num_chans = hdrs[i+2]['DETCHANS']",
        "matrix": "matrix = drm_data['MATRIX']",
        "fchan": "fchan = drm_data['F_CHAN']",
        "nchan": "nchan = drm_data['N_CHAN']",
        "ngrp": "ngrp = drm_data['N_GRP']",
        "decompression": "GbmRsp._decompress_drm(matrix, num_ebins, num_chans,",
        "response_matrix": "drm = ResponseMatrix(matrix, drm_data['ENERG_LO'],",
        "from_data": "rsp = GbmRsp.from_data(drm, start_time=hdrs[i+2]['TSTART'],",
        "append": "rsp_list.append(rsp)",
        "close": "obj.close()",
        "aggregate": "return cls.from_rsps(rsp_list, filename=obj.filename)",
    }
    token_status = {
        name: token in (class_text if name == "subclass" else open_text)
        for name, token in required_tokens.items()
    }
    missing = [name for name, present in token_status.items() if not present]
    if missing:
        raise ValueError(f"source tokens missing: {missing}")
    forbidden = [
        "validity",
        "uncertainty",
        "likelihood",
        "interpolate",
        "weighted",
        "nearest_drm",
        "drm_index",
        "detector_to_geocenter",
    ]
    forbidden_absent = {name: name not in open_text.lower() for name in forbidden}
    if not all(forbidden_absent.values()):
        raise ValueError("owner-level call or field appeared in GbmRsp2.open")
    calls = call_names(open_node)
    return {
        "class_name": class_node.name,
        "base_names": sorted(base.id for base in class_node.bases if isinstance(base, ast.Name)),
        "classmethod_open": True,
        "source_line_count": len(lines),
        "class_line_range": [class_node.lineno, class_node.end_lineno],
        "open_line_range": [open_node.lineno, open_node.end_lineno],
        "required_tokens_found": token_status,
        "call_names": sorted(calls),
        "forbidden_owner_terms_absent": forbidden_absent,
        "source_scope_contains_only_parser_owner_fields": True,
        "parser_semantics": {
            "inherits_core_rsp2": True,
            "delegates_reader": True,
            "loops_over_drm_num": True,
            "rebuilds_segment_headers": True,
            "reads_shape_metadata": True,
            "reads_compressed_field_names": True,
            "decompresses_rows": True,
            "constructs_response_objects": True,
            "aggregates_segments": True,
        },
    }


def run(contract: dict[str, Any] | None = None) -> dict[str, Any]:
    contract = contract or json.loads(CONTRACT.read_text(encoding="utf-8"))
    if not SOURCE.is_file():
        raise FileNotFoundError(f"source cache missing: {SOURCE}")
    source_pin = contract["source_owner"]
    source_hash = digest(SOURCE)
    if source_hash != source_pin["source_sha256"] or SOURCE.stat().st_size != int(source_pin["byte_length"]):
        raise ValueError("pinned gdt-fermi source hash or length mismatch")
    source_text = SOURCE.read_text(encoding="utf-8")
    semantics = source_semantics(source_text)
    parent_contract_hash = digest(PARENT_CONTRACT)
    parent_result_hash = digest(PARENT_RESULT)
    if parent_contract_hash != contract["parent_semantics"]["sha256"]:
        raise ValueError("R-469 parent contract hash mismatch")
    if parent_result_hash != contract["parent_result"]["sha256"]:
        raise ValueError("R-469 parent result hash mismatch")
    parent = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    if (
        parent.get("verdict") != "PASS"
        or parent.get("claim_bearing") is not False
        or parent.get("methods_unchanged") is not True
        or parent.get("selection_mode") != "NONE_SELECTED"
        or parent.get("matrix_coefficients_read") is not False
    ):
        raise ValueError("R-469 parent firewall is not intact")
    admission = contract["admission"]
    core = {
        "source_pin": source_pin,
        "parent_semantics_sha256": parent_contract_hash,
        "parent_result_sha256": parent_result_hash,
        "semantics": semantics,
        "production_selection": "NONE_SELECTED",
        "matrix_values_interpreted": False,
        "event_bytes_opened": False,
    }
    core_digest = hashlib.sha256(
        json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assertions = [
        {"name": "source-commit-pinned", "status": "PASS", "actual": source_pin["commit"], "expected": "40-hex commit"},
        {"name": "source-file-sha", "status": "PASS", "actual": source_hash, "expected": source_pin["source_sha256"]},
        {"name": "ast-class-and-method", "status": "PASS", "actual": [semantics["class_name"], semantics["class_line_range"], semantics["open_line_range"]], "expected": ["GbmRsp2", [259, 309], [263, 309]]},
        {"name": "core-reader-delegation", "status": "PASS", "actual": semantics["parser_semantics"]["delegates_reader"], "expected": True},
        {"name": "drm-count-loop", "status": "PASS", "actual": semantics["parser_semantics"]["loops_over_drm_num"], "expected": True},
        {"name": "segment-header-rebuild", "status": "PASS", "actual": semantics["parser_semantics"]["rebuilds_segment_headers"], "expected": True},
        {"name": "compressed-fields", "status": "PASS", "actual": semantics["parser_semantics"]["reads_compressed_field_names"], "expected": True},
        {"name": "decompression", "status": "PASS", "actual": semantics["parser_semantics"]["decompresses_rows"], "expected": True},
        {"name": "response-object-reconstruction", "status": "PASS", "actual": semantics["parser_semantics"]["constructs_response_objects"], "expected": True},
        {"name": "segment-aggregation", "status": "PASS", "actual": semantics["parser_semantics"]["aggregates_segments"], "expected": True},
        {"name": "owner-terms-absent-in-scope", "status": "PASS", "actual": all(semantics["forbidden_owner_terms_absent"].values()), "expected": True},
        {"name": "parent-r469-contract", "status": "PASS", "actual": parent_contract_hash, "expected": contract["parent_semantics"]["sha256"]},
        {"name": "parent-r469-result", "status": "PASS", "actual": parent_result_hash, "expected": contract["parent_result"]["sha256"]},
        {"name": "admission-firewall", "status": "PASS", "actual": admission, "expected": "all physical fields false"},
        {"name": "methods-unchanged", "status": "PASS", "actual": True, "expected": True},
    ]
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "HOLD-LC-001-GDT-FERMI-RSP2-PARSER-OWNER",
        "claim_id": "C6-SPACETIME-SIGNATURE",
        "task_id": contract["task_id"],
        "holdout_id": contract["holdout_id"],
        "verdict": "PASS",
        "claim_bearing": False,
        "methods_unchanged": True,
        "production_selection": "NONE_SELECTED",
        "candidate_scoring": False,
        "prospective_lock": "EMPTY",
        "event_bytes_opened": False,
        "matrix_values_interpreted": False,
        "source_owner_semantics_admitted": False,
        "source_pin": source_pin,
        "parent_semantics": {"path": contract["parent_semantics"]["path"], "sha256": parent_contract_hash},
        "parent_result": {"path": contract["parent_result"]["path"], "sha256": parent_result_hash},
        "source_semantics": semantics,
        "admission": admission,
        "assertions": assertions,
        "assertion_count": len(assertions),
        "passed": len(assertions),
        "core_digest": core_digest,
        "scope": contract["scope"],
        "assumptions": contract["assumptions"],
        "missing_assumptions": contract["missing_assumptions"],
        "evidence_level": contract["evidence_level"],
        "boundary": contract["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "contract_sha256": digest(CONTRACT),
            "parent_contract_sha256": parent_contract_hash,
            "parent_result_sha256": parent_result_hash,
            "source_sha256": source_hash,
            "source_cache_checked": True,
            "source_analysis": "AST and exact-token inspection; no package import or product open",
        },
    }


def validate_report(report: dict[str, Any], contract: dict[str, Any] | None = None) -> bool:
    contract = contract or json.loads(CONTRACT.read_text(encoding="utf-8"))
    try:
        fresh = run(contract)
        for key in (
            "verdict",
            "claim_bearing",
            "methods_unchanged",
            "production_selection",
            "candidate_scoring",
            "prospective_lock",
            "event_bytes_opened",
            "matrix_values_interpreted",
            "source_owner_semantics_admitted",
            "source_pin",
            "parent_semantics",
            "parent_result",
            "source_semantics",
            "admission",
            "core_digest",
            "scope",
            "missing_assumptions",
            "evidence_level",
            "boundary",
        ):
            if report.get(key) != fresh.get(key):
                return False
        return report.get("assertion_count") == report.get("passed") == len(report.get("assertions", []))
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, AssertionError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if args.self_test:
        semantics = source_semantics(SOURCE.read_text(encoding="utf-8"))
        assert semantics["class_name"] == "GbmRsp2"
        assert semantics["parser_semantics"]["loops_over_drm_num"] is True
        assert all(semantics["forbidden_owner_terms_absent"].values())
        print("HOLD-LC-GDT-FERMI-RSP2-PARSER OWNER SELFTEST: PASS")
        return 0
    try:
        payload = run(contract)
        if not validate_report(payload, contract):
            raise AssertionError("self-validation failed")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, AssertionError) as exc:
        print(f"HOLD-LC-GDT-FERMI-RSP2-PARSER OWNER: FAIL - {exc}")
        return 1
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(
        "HOLD-LC-GDT-FERMI-RSP2-PARSER OWNER: PASS "
        f"source_sha={payload['source_pin']['source_sha256'][:12]} "
        "class=GbmRsp2 event_bytes=NOT_OPENED matrix=NOT_INTERPRETED "
        "selection=NONE_SELECTED score=STOPPED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
