#!/usr/bin/env python3
"""Audit hash-frozen Fermi time-segmented response-history products.

This additive audit verifies exact response-history bytes and reads only FITS
scalar headers/table declarations.  It never reads EBOUNDS or response-matrix
values, constructs a timing likelihood, or admits a calibration uncertainty.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

from audit_hold_lc_owner_artifacts import (
    DEFAULT_CACHE_ROOT,
    REPO,
    atomic_json_write,
    parse_fits_headers,
    product_path,
    sha256_and_size,
    table_columns,
)


DEFAULT_MANIFEST = REPO / "strategy" / "hold-lc-001-response-history-byte-freeze-v0.1.json"
DEFAULT_OUTPUT = REPO / "strategy" / "hold-lc-001-response-history-audit-v0.1.json"
RESPONSE_HISTORY_ROLE = "time_segmented_response_history_owner_candidate"
EBOUNDS_COLUMNS = ("CHANNEL", "E_MIN", "E_MAX")
MATRIX_COLUMNS = ("ENERG_LO", "ENERG_HI", "N_GRP", "F_CHAN", "N_CHAN", "MATRIX")
COVERAGE_KEYS = ("DATE-OBS", "DATE-END", "TSTART", "TSTOP", "TIMESYS", "TIMEUNIT")


def hdu_metadata(index: int, header: dict[str, Any]) -> dict[str, Any]:
    selected_keys = (
        "XTENSION",
        "EXTNAME",
        "BITPIX",
        "NAXIS",
        "NAXIS1",
        "NAXIS2",
        "PCOUNT",
        "GCOUNT",
        "TFIELDS",
        "DATE-OBS",
        "DATE-END",
        "MJDREFI",
        "MJDREFF",
        "TSTART",
        "TSTOP",
        "TRIGTIME",
        "TIMESYS",
        "TIMEUNIT",
        "DETNAM",
        "DETCHANS",
        "CREATOR",
        "FILENAME",
        "DRM_NUM",
        "DRM_TYPE",
        "RSP_NUM",
        "INFILE01",
        "INFILE02",
        "INFILE03",
        "INFILE04",
    )
    return {
        "hdu_index": index,
        "header_byte_offset": header["_header_byte_offset"],
        "header_byte_length": header["_header_byte_length"],
        "data_byte_length": header["_data_byte_length"],
        "fields": {key: header[key] for key in selected_keys if key in header},
        "table_columns": table_columns(header),
    }


def coverage_from_hdu(item: dict[str, Any]) -> dict[str, Any]:
    return {key: item["fields"].get(key) for key in COVERAGE_KEYS}


def schema_audit(hdus: list[dict[str, Any]]) -> dict[str, Any]:
    ebounds = [item for item in hdus if item["fields"].get("EXTNAME") == "EBOUNDS"]
    matrices = [item for item in hdus if item["fields"].get("EXTNAME") == "SPECRESP MATRIX"]
    ebounds_names = {column["name"] for item in ebounds for column in item["table_columns"]}
    matrix_names = {column["name"] for item in matrices for column in item["table_columns"]}
    missing_ebounds = [column for column in EBOUNDS_COLUMNS if column not in ebounds_names]
    missing_matrix = [column for column in MATRIX_COLUMNS if column not in matrix_names]
    ordered = True
    segments = sorted(
        matrices,
        key=lambda item: int(item["fields"].get("RSP_NUM", 0)),
    )
    response_numbers = [item["fields"].get("RSP_NUM") for item in segments]
    if not segments or any(number is None for number in response_numbers):
        ordered = False
    else:
        ordered = response_numbers == list(range(1, len(response_numbers) + 1))
        ordered = ordered and all(
            float(current["fields"].get("TSTART", 0)) >= float(previous["fields"].get("TSTART", 0))
            and float(current["fields"].get("TSTOP", 0)) >= float(previous["fields"].get("TSTOP", 0))
            for previous, current in zip(segments, segments[1:])
        )
    coverage_present = all(
        all(item["fields"].get(key) is not None for key in COVERAGE_KEYS)
        for item in [*ebounds, *matrices]
    ) and bool(ebounds) and bool(matrices)
    time_standard = all(
        item["fields"].get("TIMESYS") == "TT" and item["fields"].get("TIMEUNIT") == "s"
        for item in [*ebounds, *matrices]
    ) and bool(ebounds) and bool(matrices)
    nonempty_matrix_rows = any(int(item["fields"].get("NAXIS2", 0)) > 0 for item in matrices)
    header_owner_fields = {
        key: next(
            (item["fields"].get(key) for item in hdus if item["fields"].get(key) is not None),
            None,
        )
        for key in ("CREATOR", "DRM_TYPE", "DRM_NUM", "TRIGTIME", "DETNAM")
    }
    schema_match = (
        len(ebounds) == 1
        and bool(matrices)
        and not missing_ebounds
        and not missing_matrix
        and coverage_present
        and time_standard
        and ordered
        and nonempty_matrix_rows
        and all(value is not None for value in header_owner_fields.values())
    )
    return {
        "ebounds_hdu_indices": [item["hdu_index"] for item in ebounds],
        "response_matrix_hdu_indices": [item["hdu_index"] for item in matrices],
        "response_segment_count": len(matrices),
        "response_numbers": response_numbers,
        "ebounds_declared_columns": sorted(ebounds_names),
        "response_matrix_declared_columns": sorted(matrix_names),
        "required_ebounds_columns": list(EBOUNDS_COLUMNS),
        "required_response_matrix_columns": list(MATRIX_COLUMNS),
        "missing_ebounds_columns": missing_ebounds,
        "missing_response_matrix_columns": missing_matrix,
        "coverage": {
            "first_segment": coverage_from_hdu(segments[0]) if segments else None,
            "last_segment": coverage_from_hdu(segments[-1]) if segments else None,
            "all_declared_hdus": coverage_present,
        },
        "time_standard_fields_present": time_standard,
        "response_segment_order_and_numbering": ordered,
        "nonempty_response_rows_declared": nonempty_matrix_rows,
        "header_owner_fields": header_owner_fields,
        "schema_match": schema_match,
    }


def audit_product(product: dict[str, Any], cache_root: Path) -> dict[str, Any]:
    path = product_path(cache_root, str(product["local_cache_key"]))
    if not path.is_file():
        raise FileNotFoundError(path)
    actual_hash, actual_size = sha256_and_size(path)
    expected_hash = str(product["sha256"])
    expected_size = int(product["byte_length"])
    record: dict[str, Any] = {
        "id": product["id"],
        "role": product["role"],
        "detector": product.get("detector"),
        "local_cache_key": product["local_cache_key"],
        "recorded_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "recorded_byte_length": expected_size,
        "actual_byte_length": actual_size,
        "sha256_match": actual_hash == expected_hash,
        "byte_length_match": actual_size == expected_size,
        "matrix_values_read": False,
        "header_audit_performed": False,
        "hdu_count": 0,
        "hdus": [],
        "schema": None,
    }
    if record["sha256_match"] and record["byte_length_match"]:
        headers = parse_fits_headers(path)
        metadata = [hdu_metadata(index, header) for index, header in enumerate(headers)]
        record["header_audit_performed"] = True
        record["hdu_count"] = len(metadata)
        record["hdus"] = metadata
        record["schema"] = schema_audit(metadata)
    return record


def audit(manifest_path: Path, cache_root: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_hash, manifest_size = sha256_and_size(manifest_path)
    try:
        manifest_display = str(manifest_path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        manifest_display = str(manifest_path)
    products = [audit_product(product, cache_root) for product in manifest.get("products", [])]
    all_hashes = all(item["sha256_match"] and item["byte_length_match"] for item in products)
    all_schema = all(item["schema"] and item["schema"]["schema_match"] for item in products)
    segments = sum(item["schema"]["response_segment_count"] for item in products if item["schema"])
    return {
        "schema": "tect/observation-response-history-audit/0.1",
        "id": "HOLD-LC-001-RESPONSE-HISTORY-AUDIT-v0.1",
        "version": "0.1.0",
        "task_id": "T-061",
        "holdout_id": "HOLD-LC-001",
        "claim_bearing": False,
        "status": "RESPONSE_HISTORY_SCHEMA_PRESENT_STATISTICAL_OWNER_UNADMITTED",
        "parent_response_history_manifest": manifest_display,
        "parent_response_history_manifest_sha256": manifest_hash,
        "parent_response_history_manifest_byte_length": manifest_size,
        "parser_dependency": {
            "path": "verification/scripts/audit_hold_lc_owner_artifacts.py",
            "sha256": "f8b312b34856df923390c531f07758f15ac5a29e25817226b910391ccd158f6d",
        },
        "scope": {
            "products": [item["id"] for item in products],
            "extraction": "Exact SHA-256/byte-length verification plus FITS scalar headers and table declarations; no EBOUNDS values, response-matrix values, event rows, timing fit or score.",
            "data_role": "CALIBRATION",
            "finite_scope": "Finite response-history owner-provenance/schema intake only; no continuum, physical identity or prospective validation claim.",
        },
        "products": products,
        "available_metadata": {
            "response_history_sha256_and_byte_length": all_hashes,
            "ebounds_and_matrix_schema": all_schema,
            "time_segment_count_declared": segments,
            "response_segment_order_and_numbering": all(
                item["schema"] and item["schema"]["response_segment_order_and_numbering"]
                for item in products
            ),
            "time_standard_and_segment_coverage": all(
                item["schema"] and item["schema"]["time_standard_fields_present"]
                and item["schema"]["coverage"]["all_declared_hdus"]
                for item in products
            ),
            "response_matrix_values_read": False,
            "calibration_validity_interpolation": False,
            "detector_to_geocenter_conversion": False,
            "source_owned_timing_likelihood": False,
            "component_or_shared_covariance": False,
            "intrinsic_emission_nuisance_law": False,
            "complete_f_reg_f_lim_f_eff_f_obs": False,
        },
        "interpretation": {
            "response_history": "Both exact rsp2 products declare one EBOUNDS table and eight numbered SPECRESP MATRIX segments with TT-second header coverage and trigger context. This establishes a time-segmented response-history owner candidate, not the matrix values or a complete calibration law.",
            "linkage_boundary": "The headers expose response-generation inputs and segment intervals, but this audit does not read the response values or prove validity/interpolation linkage to the spectral-history products.",
            "admission": "The new metadata narrows the physical-owner request. Candidate scoring and all four estimator-map stages remain stopped until conversion, uncertainty, likelihood and nuisance ownership are frozen.",
        },
        "checks": {
            "all_selected_product_hashes_match": all_hashes,
            "all_response_history_schemas_match": all_schema,
            "header_only_no_table_values_read": True,
            "candidate_scoring": "STOPPED",
            "prospective_lock": "EMPTY",
        },
        "assumptions": [
            "The response-history byte-freeze manifest remains authoritative for product identity, roles, hashes and locators.",
            "FITS scalar headers and table declarations are descriptive provenance; no matrix or EBOUNDS value is interpreted.",
            "The two rsp2 files are physical-owner candidates and not a complete timing or calibration implementation.",
            "The existing T-054 forward method, T-059 inverse method, owner order and promotion firewalls remain controlling.",
        ],
        "missing_assumptions": [
            "A source-owned rule linking response-history segments to selected event windows and spectral-history validity intervals.",
            "A detector-to-geocenter timing conversion and uncertainty for the GBM and GW instruments.",
            "Frozen detector, energy, background and temporal windows with selection semantics.",
            "A source-owned joint timing likelihood or component/shared covariance including calibration and intrinsic-emission nuisance terms.",
            "A complete candidate-neutral F_reg/F_lim/F_eff/F_obs map and immutable scorer.",
            "A prospective holdout not used for source selection, response selection or estimator design.",
        ],
        "evidence_level": "T0 exact public-product byte freeze and response-history header/schema intake; no matrix-value or model test",
        "next_action": "Request or locate the validity/interpolation and timing-uncertainty owner rules linked to the response-history segments. Keep matrix values and scoring locked; independently reproduce F_reg only after the complete physical-owner and proof-owner contracts are frozen.",
        "non_claims": [
            "This audit does not admit response-matrix values, a calibration-validity interpolation, detector-to-geocenter correction, timing likelihood, covariance, nuisance law, candidate, map, score or prediction.",
            "Time-segmented response headers do not identify microscopic dynamics, causal propagation or a physical Yang-Mills sector.",
            "No Pre-A, C6, A13, Sector-A, QFT, Yang-Mills, gravity, continuum, physical-vacuum, cosmic-origin, theory-of-everything or mass-gap claim follows.",
            "The established T-054 forward and T-059 inverse methods are unchanged; this is additive response-history owner intake only.",
        ],
    }


def synthetic_hdu(extname: str, columns: tuple[str, ...], rsp_num: int | None = None) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "EXTNAME": extname,
        "XTENSION": "BINTABLE",
        "NAXIS2": 1,
        "DATE-OBS": "2017-08-17T00:00:00",
        "DATE-END": "2017-08-17T00:00:01",
        "TSTART": float(rsp_num or 0),
        "TSTOP": float((rsp_num or 0) + 1),
        "TIMESYS": "TT",
        "TIMEUNIT": "s",
        "CREATOR": "synthetic",
        "DRM_TYPE": "CSPEC",
        "DRM_NUM": 1,
        "TRIGTIME": 0.5,
        "DETNAM": "N0",
    }
    if rsp_num is not None:
        fields["RSP_NUM"] = rsp_num
    return {"hdu_index": rsp_num or 0, "fields": fields, "table_columns": [{"name": name} for name in columns]}


def self_test() -> int:
    headers = [
        synthetic_hdu("EBOUNDS", EBOUNDS_COLUMNS),
        synthetic_hdu("SPECRESP MATRIX", MATRIX_COLUMNS, 1),
        synthetic_hdu("SPECRESP MATRIX", MATRIX_COLUMNS, 2),
    ]
    result = schema_audit(headers)
    assert result["schema_match"]
    assert result["response_segment_count"] == 2
    assert result["response_numbers"] == [1, 2]
    broken = synthetic_hdu("SPECRESP MATRIX", MATRIX_COLUMNS[:-1], 1)
    assert not schema_audit([headers[0], broken])["schema_match"]
    print("HOLD-LC-RSP2 SELFTEST: PASS (segment numbering, coverage and schema rules)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        report = audit(args.manifest, args.cache_root)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"HOLD-LC-RSP2: FAIL - {exc}")
        return 1
    if not report["checks"]["all_selected_product_hashes_match"]:
        mismatches = [item["id"] for item in report["products"] if not item["sha256_match"] or not item["byte_length_match"]]
        print(f"HOLD-LC-RSP2: FAIL - hash/length mismatch: {','.join(mismatches)}")
        return 1
    if not report["checks"]["all_response_history_schemas_match"]:
        failures = [item["id"] for item in report["products"] if not item["schema"] or not item["schema"]["schema_match"]]
        print(f"HOLD-LC-RSP2: FAIL - schema mismatch: {','.join(failures)}")
        return 1
    atomic_json_write(args.output, report)
    print(
        "HOLD-LC-RSP2: PASS "
        f"products={len(report['products'])} segments={report['available_metadata']['time_segment_count_declared']} "
        f"time_standard={report['available_metadata']['time_standard_and_segment_coverage']} "
        "matrix_values=NOT_READ likelihood=NOT_ADMITTED covariance=NOT_ADMITTED score=STOPPED"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())