#!/usr/bin/env python3
"""Hostile mutation audit for the R-473 detector-frame TTE feature index.

Each mutation is applied to a temporary copy or to an in-memory manifest and
must be rejected before it can enter the finite feature index.  This audit is
deliberately a firewall test: it does not add a statistical model, a dynamics
owner, a candidate score, or a physical interpretation.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import struct
import tempfile
from pathlib import Path
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/hold-lc-001-tte-event-feature-index-v0.1.json"
BYTE_FREEZE = REPO / "strategy/hold-lc-001-event-byte-freeze-v0.1.json"
DEFAULT_CACHE_ROOT = REPO / "internal/source-cache/HOLD-LC-001/2026-08-30"
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-08-31-hostile-hold-lc-tte-event-feature-index/hostile.json"
)


def load_primary() -> Any:
    path = REPO / "verification/scripts/hold_lc_001_tte_event_feature_index.py"
    spec = importlib.util.spec_from_file_location("r473_primary", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load R-473 primary module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
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


def validate_manifest_firewall(manifest: dict[str, Any]) -> None:
    """Reject any mutation that would widen R-473 beyond its declared slot."""
    if manifest.get("result_id") != "R-473" or manifest.get("exploration_id") != "EXP-001348":
        raise ValueError("identity changed")
    if manifest.get("claim_bearing") is not False or manifest.get("tier") != "T0":
        raise ValueError("claim/tier firewall changed")
    methods = manifest.get("methods_preserved", {})
    if not methods or any(value is not True for value in methods.values()):
        raise ValueError("method-preservation firewall changed")
    admission = manifest.get("admission", {})
    if admission.get("candidate_scoring_allowed") is not False:
        raise ValueError("candidate scoring enabled")
    if admission.get("prospective_lock") != "EMPTY":
        raise ValueError("prospective lock changed")
    if any(admission.get(key) is not False for key in (
        "response_matrix_values_read",
        "geocenter_conversion_admitted",
        "time_standard_conversion_admitted",
        "calibration_validity_admitted",
        "timing_likelihood_admitted",
        "component_covariance_admitted",
        "intrinsic_emission_nuisance_admitted",
        "source_owner_admitted",
    )):
        raise ValueError("statistical or owner admission widened")
    scope = manifest.get("scope_firewall", {})
    if any(scope.get(key) is not False for key in (
        "statistical_model_closed",
        "physical_owner_closed",
        "complete_f_reg_f_lim_f_eff_f_obs",
        "candidate_selection",
        "prospective_prediction",
        "physical_sector_closed",
        "pre_a_closed",
        "sector_a_closed",
        "c6_closed",
        "qft_identity_closed",
        "yang_mills_identity_closed",
        "continuum_closed",
        "mass_gap_closed",
    )):
        raise ValueError("physical scope widened")


def validate_parent_hash(manifest: dict[str, Any]) -> None:
    expected = str(manifest.get("inputs", {}).get("byte_freeze", {}).get("sha256", ""))
    actual = sha256(BYTE_FREEZE.read_bytes())
    if expected != actual:
        raise ValueError("byte-freeze parent hash mismatch")
    validate_manifest_firewall(manifest)


def copy_with_mutation(source: Path, destination: Path, mutation: Callable[[bytearray, dict[str, Any]], None], report: dict[str, Any]) -> Path:
    data = bytearray(source.read_bytes())
    mutation(data, report)
    destination.write_bytes(bytes(data))
    return destination


def expect_reject(name: str, operation: Callable[[], Any]) -> dict[str, Any]:
    try:
        operation()
    except Exception as error:  # noqa: BLE001 - every parser rejection is evidence
        return {"name": name, "rejected": True, "reason": f"{type(error).__name__}: {error}"}
    return {"name": name, "rejected": False, "reason": "mutation was accepted"}


def run(manifest_path: Path = MANIFEST, cache_root: Path = DEFAULT_CACHE_ROOT) -> dict[str, Any]:
    primary = load_primary()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest_firewall(manifest)
    byte_manifest = json.loads(BYTE_FREEZE.read_text(encoding="utf-8"))
    item = next(product for product in byte_manifest["products"] if product["id"] == "FERMI-GBM-N0-TTE")
    source = cache_root / Path(*Path(str(item["local_cache_key"]).replace("/", os.sep)).parts[2:])
    original = primary.extract_tte(source, expected_hash=str(item["sha256"]), expected_length=int(item["byte_length"]))
    events = original["events_hdu"]
    data_start = int(events["data_offset"])
    row_width = int(events["row_width"])
    original_data = source.read_bytes()
    original_hash = sha256(original_data)
    original_raw_time = struct.unpack(">d", original_data[data_start : data_start + 8])[0]
    trigger = float(original["time_header"]["trigtime"])
    tstop = float(original["time_header"]["tstop"])

    mutations: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="r473-hostile-") as temporary:
        root = Path(temporary)

        def file_case(name: str, mutation: Callable[[bytearray, dict[str, Any]], None], operation: Callable[[Path], Any]) -> None:
            target = root / f"{name}.fit"
            copy_with_mutation(source, target, mutation, original)
            mutations.append(expect_reject(name, lambda: operation(target)))

        def swap_first_two(data: bytearray, report: dict[str, Any]) -> None:
            first_row = bytes(data[data_start : data_start + row_width])
            second_row = bytes(data[data_start + row_width : data_start + 2 * row_width])
            data[data_start : data_start + row_width] = second_row
            data[data_start + row_width : data_start + 2 * row_width] = first_row

        file_case("row-order-decrease", swap_first_two, lambda path: primary.extract_tte(path))
        file_case(
            "timestamp-outside-header",
            lambda data, report: data.__setitem__(slice(data_start, data_start + 8), struct.pack(">d", (tstop - trigger) + 1000.0)),
            lambda path: primary.extract_tte(path),
        )
        file_case(
            "timestamp-nan",
            lambda data, report: data.__setitem__(slice(data_start, data_start + 8), struct.pack(">d", math.nan)),
            lambda path: primary.extract_tte(path),
        )
        file_case(
            "pha-out-of-range",
            lambda data, report: data.__setitem__(slice(data_start + 8, data_start + 10), struct.pack(">h", 32767)),
            lambda path: primary.extract_tte(path),
        )
        mutations.append(
            expect_reject(
                "truncated-fits",
                lambda: primary.extract_tte(root / "truncated.fit")
                if (root / "truncated.fit").write_bytes(original_data[:-1]) is not None
                else None,
            )
        )
        file_case(
            "hash-byte-flip",
            lambda data, report: data.__setitem__(0, data[0] ^ 1),
            lambda path: primary.extract_tte(path, expected_hash=original_hash, expected_length=len(original_data)),
        )
        def mutate_time_tform(data: bytearray, report: dict[str, Any]) -> None:
            header_offset = int(report["events_hdu"]["header_offset"])
            location = data.find(b"TFORM1", header_offset)
            card = bytes(data[location : location + 80]) if location >= 0 else b""
            value_offset = card.find(b"1D")
            if location < 0 or value_offset < 0:
                raise ValueError("EVENTS TFORM1 card not found")
            data[location + value_offset + 1] = ord("J")

        file_case("time-tform-schema", mutate_time_tform, lambda path: primary.extract_tte(path))

        altered_hash = copy.deepcopy(manifest)
        altered_hash["inputs"]["byte_freeze"]["sha256"] = "0" * 64
        mutations.append(expect_reject("manifest-byte-freeze-hash", lambda: validate_parent_hash(altered_hash)))

        altered_score = copy.deepcopy(manifest)
        altered_score["admission"]["candidate_scoring_allowed"] = True
        mutations.append(expect_reject("candidate-score-promotion", lambda: validate_manifest_firewall(altered_score)))

        altered_lock = copy.deepcopy(manifest)
        altered_lock["admission"]["prospective_lock"] = "FROZEN"
        mutations.append(expect_reject("prospective-lock-promotion", lambda: validate_manifest_firewall(altered_lock)))

        altered_method = copy.deepcopy(manifest)
        altered_method["methods_preserved"]["t054_forward_method_unchanged"] = False
        mutations.append(expect_reject("method-change-promotion", lambda: validate_manifest_firewall(altered_method)))

        altered_physical = copy.deepcopy(manifest)
        altered_physical["scope_firewall"]["physical_sector_closed"] = True
        mutations.append(expect_reject("physical-sector-promotion", lambda: validate_manifest_firewall(altered_physical)))

    if len(mutations) < 10 or not all(item["rejected"] for item in mutations):
        raise AssertionError("hostile mutation firewall did not reject every mutation")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "hostile",
        "audit_id": "HOLD-LC-001-TTE-EVENT-FEATURE-INDEX",
        "result_id": "R-473",
        "exploration_id": "EXP-001348",
        "claim_id": manifest["claim_ids"][0],
        "task_id": "T-061",
        "holdout_id": "HOLD-LC-001",
        "verdict": "PASS",
        "tier": "T0",
        "claim_bearing": False,
        "methods_unchanged": True,
        "assertion_count": len(mutations),
        "passed": sum(1 for item in mutations if item["rejected"]),
        "all_mutations_rejected": all(item["rejected"] for item in mutations),
        "mutations": mutations,
        "scope": manifest["scope_firewall"],
        "admission": manifest["admission"],
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "falsifiers": manifest["falsifiers"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "provenance": {
            "manifest_sha256": sha256(manifest_path.read_bytes()),
            "byte_freeze_sha256": sha256(BYTE_FREEZE.read_bytes()),
            "hostile_script_sha256": sha256(Path(__file__).resolve().read_bytes()),
            "source_product": item["id"],
            "source_sha256": original_hash,
            "source_byte_length": len(original_data),
            "source_event_data_offset": data_start,
            "source_first_raw_time": original_raw_time,
        },
    }


def self_test() -> int:
    assert sha256(b"[0,1,2]") == hashlib.sha256(b"[0,1,2]").hexdigest()
    base = {"result_id": "R-473", "exploration_id": "EXP-001348", "claim_bearing": False, "tier": "T0", "methods_preserved": {"x": True}, "admission": {"candidate_scoring_allowed": False, "prospective_lock": "EMPTY", **{key: False for key in ("response_matrix_values_read", "geocenter_conversion_admitted", "time_standard_conversion_admitted", "calibration_validity_admitted", "timing_likelihood_admitted", "component_covariance_admitted", "intrinsic_emission_nuisance_admitted", "source_owner_admitted")}}, "scope_firewall": {key: False for key in ("statistical_model_closed", "physical_owner_closed", "complete_f_reg_f_lim_f_eff_f_obs", "candidate_selection", "prospective_prediction", "physical_sector_closed", "pre_a_closed", "sector_a_closed", "c6_closed", "qft_identity_closed", "yang_mills_identity_closed", "continuum_closed", "mass_gap_closed")}}
    validate_manifest_firewall(base)
    base["admission"]["candidate_scoring_allowed"] = True
    try:
        validate_manifest_firewall(base)
    except ValueError:
        pass
    else:
        raise AssertionError("firewall self-test accepted a score promotion")
    print("HOLD-LC-TTE-FEATURE HOSTILE SELFTEST: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--cache-root", type=Path, default=DEFAULT_CACHE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        payload = run(args.manifest.resolve(), args.cache_root.resolve())
        atomic_json(args.output.resolve(), payload)
    except (AssertionError, OSError, KeyError, TypeError, ValueError, json.JSONDecodeError, RuntimeError) as error:
        print(f"HOLD-LC-TTE-FEATURE HOSTILE: FAIL - {error}")
        return 1
    print(
        "HOLD-LC-TTE-FEATURE HOSTILE: PASS "
        f"mutations={payload['assertion_count']} rejected={payload['passed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
