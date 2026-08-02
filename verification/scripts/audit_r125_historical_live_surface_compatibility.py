#!/usr/bin/env python3
"""Audit immutable R-125 evidence against the evolving live A13 surfaces.

The issued R-125 verifier intentionally remains byte-for-byte immutable because
later A13 manifests pin its manifest hash.  That historical verifier mixed
immutable package checks with exact tokens from mutable status, TODO, and
sector-map surfaces.  This companion reruns it into a temporary artifact,
requires every immutable check to pass, permits failures only in the declared
mutable rows, and then checks the current surfaces structurally.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-03"
__version_issued__ = "2026-08-03"

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-"
    "ROOT-SHELL-OPERATOR-BOUNDARY"
)
GATE = "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE"
SLUG = "classii-conditional-variance-forest-bridge-root-shell-operator-boundary"
SCHEMA = "tect/a13-r125-historical-live-surface-compatibility-audit/1.0"
HISTORICAL_MANIFEST_SHA256 = (
    "64d0d5ee851a49c5f85994f71616b4d51def2bca701abea6d006a578d8d44e2f"
)
HISTORICAL_VERIFIER_SHA256 = (
    "3657cc48658bc5e755a519aef2434a38b644dee051df5d7b2ad87c78f9ce7ae8"
)
HISTORICAL_INTEGRATED_ASSERTIONS = 164
HISTORICAL_AGGREGATE_ASSERTIONS = 254
EXPECTED_CURRENT_ASSERTIONS = 31

CLAIM_DIR = REPO / "claims" / CLAIM
MANIFEST = CLAIM_DIR / (
    "classii_conditional_variance_forest_bridge_root_shell_"
    "operator_boundary_manifest.json"
)
HISTORICAL_VERIFIER = REPO / (
    "codes/foundations/a13_classii_conditional_variance_forest_bridge_"
    "root_shell_operator_boundary_verify.py"
)
HISTORICAL_RESULT = CLAIM_DIR / (
    "runs/2026-07-30-integrated-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary/result.json"
)
STATUS = CLAIM_DIR / "status.json"
TODO_SOURCE = REPO / "todo/todo.json"
THEOREM_MAP = REPO / "governance/sector-a-theorem-map.json"
PROOF_MAP = REPO / "theory/proof-evidence-map.md"
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-08-03-audit-r125-historical-live-surface-compatibility/"
    "result.json"
)

# These are the only rows in the historical verifier whose truth may change
# solely because a live/generated surface advances.  Every other historical
# row remains fail-closed.
MUTABLE_HISTORICAL_ROWS = {
    ("surface", "claim"),
    ("surface", "status"),
    ("surface", "roadmap"),
    ("surface", "todo_source"),
    ("surface", "todo_generated"),
    ("surface", "sector_map"),
    ("surface", "claims_generated"),
    ("surface", "proof_map"),
    ("surface", "catalog"),
    ("surface", "catalog_json"),
    ("semantic", "status_no_overclaim"),
    ("semantic", "status_next_action"),
    ("semantic", "successor_alignment"),
}

R125_LEGACY_EVIDENCE = {
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "classii_conditional_variance_forest_bridge_root_shell_operator_boundary_"
    "manifest.json",
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/notes/"
    "classii-conditional-variance-forest-bridge-root-shell-operator-boundary-"
    "260730-v1.0.tex.txt",
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/notes/"
    "classii-conditional-variance-forest-bridge-root-shell-operator-boundary-"
    "260730-v1.0.pdf",
    "codes/foundations/"
    "a13_classii_conditional_variance_forest_bridge_root_shell_operator_"
    "boundary.py",
    "codes/foundations/"
    "a13_classii_conditional_variance_forest_bridge_root_shell_operator_"
    "boundary_independent.py",
    "codes/foundations/"
    "a13_classii_conditional_variance_forest_bridge_root_shell_operator_"
    "boundary_verify.py",
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/"
    "2026-07-30-primary-conditional-variance-forest-bridge-root-shell-"
    "operator-boundary/result.json",
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/"
    "2026-07-30-independent-conditional-variance-forest-bridge-root-shell-"
    "operator-boundary/result.json",
    "RESULTS-LEDGER.md#r-125",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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


def has_tokens(text: str, tokens: tuple[str, ...]) -> bool:
    return all(token in text for token in tokens)


def unexpected_historical_failures(
    rows: list[dict[str, Any]],
) -> list[tuple[str, str]]:
    return [
        (str(row.get("group")), str(row.get("name")))
        for row in rows
        if row.get("status") != "PASS"
        and (str(row.get("group")), str(row.get("name")))
        not in MUTABLE_HISTORICAL_ROWS
    ]


def taxonomy_prefixes(theorem_map: dict[str, Any]) -> set[str]:
    families = theorem_map.get("subproof_taxonomy", {}).get(CLAIM, [])
    return {
        str(prefix)
        for family in families
        for prefix in family.get("lineage_prefixes", [])
    }


def run_self_test() -> int:
    allowed = [{"group": "surface", "name": "status", "status": "FAIL"}]
    immutable = [{"group": "manifest", "name": "scope", "status": "FAIL"}]
    assert unexpected_historical_failures(allowed) == []
    assert unexpected_historical_failures(immutable) == [("manifest", "scope")]
    assert has_tokens("R-125 trace bracket future variance", ("R-125", "trace"))
    assert not has_tokens("R-125 trace", ("R-125", "future variance"))
    fixture = {
        "subproof_taxonomy": {
            CLAIM: [{"lineage_prefixes": [SLUG]}],
        }
    }
    assert SLUG in taxonomy_prefixes(fixture)
    fixture["subproof_taxonomy"][CLAIM][0]["lineage_prefixes"] = ["mutant"]
    assert SLUG not in taxonomy_prefixes(fixture)
    return 6


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
    ) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": actual,
                "expected": expected,
            }
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()

    self_test_assertions = run_self_test()
    if arguments.self_test:
        print(f"R-125 compatibility self-test PASS: {self_test_assertions}/"
              f"{self_test_assertions}")
        return 0

    audit = Audit()
    audit.check(
        "self_test",
        "mutants_rejected",
        self_test_assertions == 6,
        self_test_assertions,
        6,
    )

    required = (
        MANIFEST,
        HISTORICAL_VERIFIER,
        HISTORICAL_RESULT,
        STATUS,
        TODO_SOURCE,
        THEOREM_MAP,
        PROOF_MAP,
    )
    for path in required:
        audit.check(
            "existence",
            path.relative_to(REPO).as_posix(),
            path.is_file(),
            path.is_file(),
            True,
        )
    if not all(path.is_file() for path in required):
        payload = {
            "schema": SCHEMA,
            "version": __version__,
            "status": "FAIL",
            "assertions": audit.rows,
        }
        atomic_json(arguments.output, payload)
        print("R-125 historical/live compatibility FAIL: missing inputs")
        return 1

    manifest = load_json(MANIFEST)
    stored = load_json(HISTORICAL_RESULT)
    audit.check(
        "immutable",
        "manifest_sha256",
        sha256(MANIFEST) == HISTORICAL_MANIFEST_SHA256,
        sha256(MANIFEST),
        HISTORICAL_MANIFEST_SHA256,
    )
    audit.check(
        "immutable",
        "verifier_sha256",
        sha256(HISTORICAL_VERIFIER) == HISTORICAL_VERIFIER_SHA256,
        sha256(HISTORICAL_VERIFIER),
        HISTORICAL_VERIFIER_SHA256,
    )
    verifier_pin = manifest.get("files", {}).get("verifier", {})
    audit.check(
        "immutable",
        "manifest_verifier_pin",
        verifier_pin.get("sha256") == HISTORICAL_VERIFIER_SHA256
        and verifier_pin.get("version") == "1.0.0",
        verifier_pin,
        {"sha256": HISTORICAL_VERIFIER_SHA256, "version": "1.0.0"},
    )
    audit.check(
        "immutable",
        "stored_integrated_contract",
        stored.get("status") == "PASS"
        and stored.get("result_id") == RESULT_ID
        and stored.get("assertions_total") == HISTORICAL_INTEGRATED_ASSERTIONS
        and stored.get("assertions_passed") == HISTORICAL_INTEGRATED_ASSERTIONS
        and stored.get("aggregate_assertions") == HISTORICAL_AGGREGATE_ASSERTIONS,
        {
            key: stored.get(key)
            for key in (
                "status",
                "result_id",
                "assertions_total",
                "assertions_passed",
                "aggregate_assertions",
            )
        },
        "R-125 historical PASS 164/164; aggregate 254",
    )
    audit.check(
        "immutable",
        "stored_manifest_pin",
        stored.get("diagnostics", {}).get("manifest_sha256")
        == HISTORICAL_MANIFEST_SHA256,
        stored.get("diagnostics", {}).get("manifest_sha256"),
        HISTORICAL_MANIFEST_SHA256,
    )

    historical_payload: dict[str, Any] = {}
    historical_stdout = ""
    historical_stderr = ""
    historical_returncode: int | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="tect-r125-compat-") as directory:
            temporary_output = Path(directory) / "historical-live.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(HISTORICAL_VERIFIER),
                    "--output",
                    str(temporary_output),
                    "--timeout",
                    str(arguments.timeout),
                ],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=arguments.timeout + 30,
                check=False,
            )
            historical_returncode = completed.returncode
            historical_stdout = completed.stdout.strip()
            historical_stderr = completed.stderr.strip()
            if temporary_output.is_file():
                historical_payload = load_json(temporary_output)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        historical_stderr = f"{type(exc).__name__}: {exc}"

    historical_rows = historical_payload.get("assertions", [])
    unexpected = unexpected_historical_failures(historical_rows)
    all_failures = [
        (str(row.get("group")), str(row.get("name")))
        for row in historical_rows
        if row.get("status") != "PASS"
    ]
    child_stdout = historical_payload.get("diagnostics", {}).get(
        "child_stdout", {}
    )
    audit.check(
        "rerun",
        "historical_output_readable",
        bool(historical_payload),
        bool(historical_payload),
        True,
    )
    audit.check(
        "rerun",
        "historical_assertion_inventory",
        len(historical_rows) == HISTORICAL_INTEGRATED_ASSERTIONS,
        len(historical_rows),
        HISTORICAL_INTEGRATED_ASSERTIONS,
    )
    audit.check(
        "rerun",
        "immutable_rows_pass",
        not unexpected,
        unexpected,
        [],
    )
    audit.check(
        "rerun",
        "failures_confined_to_mutable_rows",
        set(all_failures) <= MUTABLE_HISTORICAL_ROWS,
        all_failures,
        "subset of declared mutable historical rows",
    )
    audit.check(
        "rerun",
        "child_primary_reexecuted",
        "primary PASS 51/51" in str(child_stdout.get("primary", "")),
        child_stdout.get("primary"),
        "R-125 primary PASS 51/51",
    )
    audit.check(
        "rerun",
        "child_independent_reexecuted",
        "independent PASS 39/39" in str(child_stdout.get("independent", "")),
        child_stdout.get("independent"),
        "R-125 independent PASS 39/39",
    )

    status = load_json(STATUS)
    audit.check(
        "live_status",
        "identity_tier_lifecycle",
        status.get("id") == CLAIM
        and status.get("tier") == "T4"
        and status.get("lifecycle") == "ACTIVE",
        (status.get("id"), status.get("tier"), status.get("lifecycle")),
        (CLAIM, "T4", "ACTIVE"),
    )
    expected_gates = {
        "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION",
        GATE,
    }
    audit.check(
        "live_status",
        "open_gates",
        set(status.get("open_gates", [])) == expected_gates,
        status.get("open_gates"),
        sorted(expected_gates),
    )
    legacy_evidence = set(status.get("legacy_evidence", []))
    audit.check(
        "live_status",
        "r125_immutable_evidence_retained",
        R125_LEGACY_EVIDENCE <= legacy_evidence,
        sorted(R125_LEGACY_EVIDENCE - legacy_evidence),
        [],
    )
    status_boundary = str(status.get("no_overclaim", ""))
    audit.check(
        "live_status",
        "no_overclaim_is_current_and_open",
        has_tokens(status_boundary, ("T-050", "A13", "Nelson", "Sector A"))
        and (
            "does not close" in status_boundary
            or "remain open" in status_boundary
        ),
        status_boundary,
        "current T-050/A13/Nelson/Sector-A open boundary",
    )
    next_action = str(status.get("next_action", ""))
    audit.check(
        "live_status",
        "next_action_preserves_r125_dependencies",
        has_tokens(
            next_action,
            (
                "R-125",
                "trace",
                "bracket",
                "future variance",
                "R-063",
                "forest",
                "source/sextic",
            ),
        ),
        next_action,
        "R-125 trace/bracket/future variance plus R-063 forest and source/sextic",
    )

    todo = load_json(TODO_SOURCE)
    task = next(
        (item for item in todo.get("tasks", []) if item.get("id") == "T-050"),
        {},
    )
    audit.check(
        "live_todo",
        "task_identity",
        task.get("status") == "in_progress"
        and task.get("claim") == CLAIM
        and task.get("gate") == GATE,
        {
            key: task.get(key)
            for key in ("id", "status", "claim", "gate")
        },
        {"id": "T-050", "status": "in_progress", "claim": CLAIM, "gate": GATE},
    )
    task_note = str(task.get("note", ""))
    audit.check(
        "live_todo",
        "route_dependencies",
        has_tokens(
            task_note,
            (
                "R-125",
                "forest",
                "balanced response",
                "source",
                "sextic",
            ),
        )
        and ("event-complete" in task_note or "complete event" in task_note)
        and ("complete-low" in task_note or "complete low" in task_note),
        task_note,
        "event-complete R-125 forest/complete-low/balanced/source/sextic route",
    )

    theorem_map = load_json(THEOREM_MAP)
    frontier = theorem_map.get("active_frontier", {})
    audit.check(
        "live_theorem_map",
        "frontier_identity",
        frontier.get("host_claim") == CLAIM
        and frontier.get("selected_subproof") == GATE
        and frontier.get("parent_gate") == GATE
        and frontier.get("umbrella_gate") == GATE,
        {
            key: frontier.get(key)
            for key in (
                "host_claim",
                "selected_subproof",
                "parent_gate",
                "umbrella_gate",
            )
        },
        "current A13/T-050 frontier",
    )
    prefixes = taxonomy_prefixes(theorem_map)
    audit.check(
        "live_theorem_map",
        "r125_taxonomy_retained",
        SLUG in prefixes,
        SLUG in prefixes,
        True,
    )
    success_condition = str(frontier.get("success_condition", ""))
    audit.check(
        "live_theorem_map",
        "success_condition_preserves_complete_incidence",
        has_tokens(
            success_condition,
            (
                "R-125",
                "R-063",
                "forest",
                "complete low",
                "balanced response",
                "source",
                "sextic",
                "T-050",
            ),
        ),
        success_condition,
        "R-125/R-063/forest/low/balanced/source/sextic/T-050 incidence",
    )

    proof_map_text = PROOF_MAP.read_text(encoding="utf-8")
    audit.check(
        "live_generated",
        "proof_map_retains_r125",
        "R-125" in proof_map_text and SLUG in proof_map_text,
        ("R-125" in proof_map_text, SLUG in proof_map_text),
        (True, True),
    )

    if EXPECTED_CURRENT_ASSERTIONS:
        audit.check(
            "contract",
            "current_assertion_count",
            len(audit.rows) + 1 == EXPECTED_CURRENT_ASSERTIONS,
            len(audit.rows) + 1,
            EXPECTED_CURRENT_ASSERTIONS,
        )

    passed = sum(row["status"] == "PASS" for row in audit.rows)
    count_ok = (
        not EXPECTED_CURRENT_ASSERTIONS
        or len(audit.rows) == EXPECTED_CURRENT_ASSERTIONS
    )
    overall = passed == len(audit.rows) and count_ok
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "claim_id": CLAIM,
        "historical_result_id": RESULT_ID,
        "status": "PASS" if overall else "FAIL",
        "assertions_total": len(audit.rows),
        "assertions_passed": passed,
        "assertions_failed": len(audit.rows) - passed + (0 if count_ok else 1),
        "assertions": audit.rows,
        "historical_rerun": {
            "returncode": historical_returncode,
            "reported_status": historical_payload.get("status"),
            "failed_rows": all_failures,
            "allowed_mutable_rows": sorted(MUTABLE_HISTORICAL_ROWS),
            "stdout": historical_stdout,
            "stderr": historical_stderr,
        },
        "source_hashes": {
            "companion": sha256(Path(__file__).resolve()),
            "historical_manifest": sha256(MANIFEST),
            "historical_verifier": sha256(HISTORICAL_VERIFIER),
            "historical_result": sha256(HISTORICAL_RESULT),
            "status": sha256(STATUS),
            "todo_source": sha256(TODO_SOURCE),
            "theorem_map": sha256(THEOREM_MAP),
        },
        "boundary": (
            "The historical R-125 theorem package remains immutable.  This audit "
            "separates its fresh mathematical rerun from evolving live-surface "
            "routing.  It changes no theorem, tier, gate, phase, or PDE verdict."
        ),
    }
    atomic_json(arguments.output, payload)
    for row in audit.rows:
        if row["status"] != "PASS":
            print(
                f"FAIL {row['group']}: {row['name']}: "
                f"{row['actual']} != {row['expected']}"
            )
    print(
        f"R-125 historical/live compatibility {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']}"
    )
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
