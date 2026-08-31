#!/usr/bin/env python3
"""Independent standard-library reconstruction of the R-470 parser audit.

The implementation is intentionally separate from the primary lane.  It uses
AST nodes and a different token table, reads only the pinned source text and
R-469 metadata hashes, and never opens an event product or response matrix.
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-31-independent-hold-lc-gdt-fermi-parser-owner/independent.json"


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


def locate_open(tree: ast.AST) -> tuple[ast.ClassDef, ast.FunctionDef]:
    for item in ast.walk(tree):
        if not isinstance(item, ast.ClassDef) or item.name != "GbmRsp2":
            continue
        parent_names = [base.id for base in item.bases if isinstance(base, ast.Name)]
        if "Rsp2" not in parent_names:
            continue
        for child in item.body:
            if not isinstance(child, ast.FunctionDef) or child.name != "open":
                continue
            if any(isinstance(dec, ast.Name) and dec.id == "classmethod" for dec in child.decorator_list):
                return item, child
    raise ValueError("independent AST locator could not find GbmRsp2.open")


def audit_source(text: str) -> dict[str, Any]:
    tree = ast.parse(text)
    class_node, open_node = locate_open(tree)
    rows = text.splitlines()
    body = "\n".join(rows[open_node.lineno - 1 : open_node.end_lineno])
    token_pairs = [
        ("subclass", "class GbmRsp2(Rsp2):"),
        ("delegate", "obj = super().open(file_path, **kwargs)"),
        ("headers", "hdrs = [hdu.header for hdu in obj.hdulist]"),
        ("drm_count", "num_drm = hdrs[0]['DRM_NUM']"),
        ("segment_loop", "for i in range(num_drm):"),
        ("header_rebuild", "RspHeaders.from_headers([hdrs[0], hdrs[1], hdrs[i+2]])"),
        ("num_ebins", "num_ebins = hdrs[i+2]['NUMEBINS']"),
        ("num_chans", "num_chans = hdrs[i+2]['DETCHANS']"),
        ("matrix", "matrix = drm_data['MATRIX']"),
        ("fchan", "fchan = drm_data['F_CHAN']"),
        ("nchan", "nchan = drm_data['N_CHAN']"),
        ("ngrp", "ngrp = drm_data['N_GRP']"),
        ("decompression", "GbmRsp._decompress_drm(matrix, num_ebins, num_chans,"),
        ("response_matrix", "drm = ResponseMatrix(matrix, drm_data['ENERG_LO'],"),
        ("from_data", "rsp = GbmRsp.from_data(drm, start_time=hdrs[i+2]['TSTART'],"),
        ("append", "rsp_list.append(rsp)"),
        ("close", "obj.close()"),
        ("aggregate", "return cls.from_rsps(rsp_list, filename=obj.filename)"),
    ]
    token_status = {
        name: token in (text.splitlines()[class_node.lineno - 1 : class_node.end_lineno] if name == "subclass" else body)
        for name, token in token_pairs
    }
    if not all(token_status.values()):
        raise ValueError(f"independent source-token mismatch: {token_status}")
    forbidden = ("validity", "uncertainty", "likelihood", "interpolate", "weighted", "nearest_drm", "drm_index", "detector_to_geocenter")
    absent = {term: term not in body.lower() for term in forbidden}
    if not all(absent.values()):
        raise ValueError("independent owner-gap boundary changed")
    calls = set()
    for item in ast.walk(open_node):
        if isinstance(item, ast.Call):
            calls.add(item.func.attr if isinstance(item.func, ast.Attribute) else getattr(item.func, "id", "<call>"))
    return {
        "class_name": class_node.name,
        "base_names": sorted(base.id for base in class_node.bases if isinstance(base, ast.Name)),
        "classmethod_open": True,
        "source_line_count": len(rows),
        "class_line_range": [class_node.lineno, class_node.end_lineno],
        "open_line_range": [open_node.lineno, open_node.end_lineno],
        "required_tokens_found": token_status,
        "call_names": sorted(calls),
        "forbidden_owner_terms_absent": absent,
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


def run() -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    source_pin = contract["source_owner"]
    if digest(SOURCE) != source_pin["source_sha256"] or SOURCE.stat().st_size != int(source_pin["byte_length"]):
        raise ValueError("independent source pin mismatch")
    semantics = audit_source(SOURCE.read_text(encoding="utf-8"))
    parent_contract_hash = digest(PARENT_CONTRACT)
    parent_result_hash = digest(PARENT_RESULT)
    if parent_contract_hash != contract["parent_semantics"]["sha256"] or parent_result_hash != contract["parent_result"]["sha256"]:
        raise ValueError("independent R-469 parent hash mismatch")
    parent = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    if any(
        (
            parent.get("verdict") != "PASS",
            parent.get("claim_bearing") is not False,
            parent.get("methods_unchanged") is not True,
            parent.get("selection_mode") != "NONE_SELECTED",
            parent.get("matrix_coefficients_read") is not False,
        )
    ):
        raise ValueError("independent parent firewall mismatch")
    core = {
        "source_pin": source_pin,
        "parent_semantics_sha256": parent_contract_hash,
        "parent_result_sha256": parent_result_hash,
        "semantics": semantics,
        "production_selection": "NONE_SELECTED",
        "matrix_values_interpreted": False,
        "event_bytes_opened": False,
    }
    core_digest = hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    assertions = [
        {"name": "source_sha", "pass": True, "actual": digest(SOURCE), "expected": source_pin["source_sha256"]},
        {"name": "parent_contract_sha", "pass": True, "actual": parent_contract_hash, "expected": contract["parent_semantics"]["sha256"]},
        {"name": "parent_result_sha", "pass": True, "actual": parent_result_hash, "expected": contract["parent_result"]["sha256"]},
        {"name": "class", "pass": semantics["class_name"] == "GbmRsp2" and semantics["base_names"] == ["Rsp2"], "actual": semantics["class_name"], "expected": "GbmRsp2/Rsp2"},
        {"name": "delegation", "pass": semantics["parser_semantics"]["delegates_reader"], "actual": True, "expected": True},
        {"name": "segment_loop", "pass": semantics["parser_semantics"]["loops_over_drm_num"], "actual": True, "expected": True},
        {"name": "field_access", "pass": semantics["parser_semantics"]["reads_compressed_field_names"], "actual": True, "expected": True},
        {"name": "reconstruction", "pass": semantics["parser_semantics"]["constructs_response_objects"], "actual": True, "expected": True},
        {"name": "owner_gap", "pass": all(semantics["forbidden_owner_terms_absent"].values()), "actual": True, "expected": True},
        {"name": "firewall", "pass": True, "actual": ["NONE_SELECTED", False, False], "expected": ["NONE_SELECTED", False, False]},
    ]
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "HOLD-LC-001-GDT-FERMI-RSP2-PARSER-OWNER-INDEPENDENT",
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
        "parent_semantics_sha256": parent_contract_hash,
        "parent_result_sha256": parent_result_hash,
        "source_semantics": semantics,
        "admission": contract["admission"],
        "assertions": assertions,
        "assertion_count": len(assertions),
        "passed": sum(1 for item in assertions if item["pass"]),
        "core_digest": core_digest,
        "boundary": contract["non_claims"],
        "recorded_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "provenance": {
            "contract_sha256": digest(CONTRACT),
            "source_sha256": digest(SOURCE),
            "parent_contract_sha256": parent_contract_hash,
            "parent_result_sha256": parent_result_hash,
            "source_cache_checked": True,
            "source_analysis": "independent AST and token inspection; no package import or product open",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        payload = run()
        if args.self_test:
            assert payload["verdict"] == "PASS"
            assert payload["core_digest"]
            print("HOLD-LC-GDT-FERMI-RSP2-PARSER OWNER INDEPENDENT SELFTEST: PASS")
            return 0
        store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, AssertionError) as exc:
        print(f"HOLD-LC-GDT-FERMI-RSP2-PARSER OWNER INDEPENDENT: FAIL - {exc}")
        return 1
    print(
        "HOLD-LC-GDT-FERMI-RSP2-PARSER OWNER INDEPENDENT: PASS "
        f"source_sha={payload['source_pin']['source_sha256'][:12]} "
        "class=GbmRsp2 event_bytes=NOT_OPENED matrix=NOT_INTERPRETED "
        "selection=NONE_SELECTED score=STOPPED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
