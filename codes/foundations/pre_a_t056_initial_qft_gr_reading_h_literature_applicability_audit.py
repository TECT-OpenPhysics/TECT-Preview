#!/usr/bin/env python3
"""Primary verifier for the R-170 v1.0 literature-applicability audit.

The derivation reads the four claim-local records, their live status cards,
the pinned source bytes, and the bounded selected-index searches. Labelled
test oracles are consulted only after those values have been derived.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any


sys.dont_write_bytecode = True
__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-t056-initial-qft-gr-reading-h-literature-applicability-audit"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_sha256(path: Path) -> str:
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
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def strip_code(value: str) -> str:
    value = value.strip()
    return value[1:-1] if len(value) >= 2 and value[0] == value[-1] == "`" else value


def canonical_disposition(value: str) -> str:
    for candidate in ("APPLIES-CONDITIONALLY", "DOES-NOT-APPLY", "NOT-YET-ASSESSED", "APPLIES"):
        if value.startswith(candidate):
            return candidate
    raise AssertionError(f"unsupported disposition {value!r}")


def parse_metadata(text: str) -> dict[str, Any]:
    patterns = {
        "claim": r"^\*\*Claim:\*\*\s+`([^`]+)`\s*$",
        "reviewed": r"^\*\*Reviewed:\*\*\s+([^\s]+)\s*$",
        "disposition": r"^\*\*Overall disposition:\*\*\s+`([^`]+)`",
        "load_bearing": r"^\*\*Load-bearing use:\*\*\s+(Yes|No)",
    }
    found: dict[str, Any] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            raise AssertionError(f"missing metadata {key}")
        found[key] = match.group(1)
    found["disposition"] = canonical_disposition(found["disposition"])
    found["load_bearing"] = found["load_bearing"] == "Yes"
    return found


def parse_crosswalk(text: str) -> list[dict[str, Any]]:
    match = re.search(
        r"^## 3 Assumption-to-model crosswalk\s*$([\s\S]*?)(?=^## 4 )",
        text,
        re.MULTILINE,
    )
    if not match:
        raise AssertionError("crosswalk section missing")
    rows: list[dict[str, Any]] = []
    for line in match.group(1).splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] == "Source hypothesis" or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append(
            {
                "hypothesis": cells[0],
                "object": cells[1],
                "status": strip_code(cells[2]),
                "load_bearing": cells[3].lower() == "yes",
                "reason": cells[4],
            }
        )
    if not rows:
        raise AssertionError("no crosswalk rows")
    return rows


def parse_search(text: str, claim: str) -> dict[str, Any]:
    command = re.search(
        r'legacy_search\.py query --text "([^"]+)" --claim ([A-Z0-9-]+) --limit (\d+) --json',
        text,
    )
    if not command or command.group(2) != claim:
        raise AssertionError(f"missing exact bounded search for {claim}")
    zero = re.search(r"returned zero rows and zero unique source IDs", text)
    numeric = re.search(r"returned (\d+) rows spanning (\d+) unique source IDs", text)
    if zero:
        rows, unique = 0, 0
    elif numeric:
        rows, unique = int(numeric.group(1)), int(numeric.group(2))
    else:
        raise AssertionError(f"missing search outcome for {claim}")
    return {
        "query": command.group(1),
        "claim_filter": command.group(2),
        "limit": int(command.group(3)),
        "returned_rows": rows,
        "unique_source_ids": unique,
        "limit_saturated": "limit was saturated" in text or "limit was saturated" in text.lower(),
    }


def parse_adversarial_axes(text: str) -> list[str]:
    match = re.search(r"^## 6 Adversarial checks\s*$([\s\S]*?)(?=^## 7 )", text, re.MULTILINE)
    if not match:
        raise AssertionError("adversarial section missing")
    return re.findall(r"^- \*\*([^*]+?)\s+-\s+", match.group(1), re.MULTILINE)


def derive_records(manifest: dict[str, Any]) -> dict[str, Any]:
    dispositions: dict[str, str] = {}
    load_bearing: dict[str, bool] = {}
    row_counts: dict[str, int] = {}
    status_counts: dict[str, dict[str, int]] = {}
    blockers: dict[str, list[str]] = {}
    searches: dict[str, list[int]] = {}
    section_coverage: dict[str, bool] = {}
    adversarial_counts: dict[str, int] = {}
    stale_prose_firewalls: dict[str, bool] = {}
    record_hashes: dict[str, str] = {}

    allowed = set(manifest["record_contract"]["crosswalk_statuses"])
    section_prefixes = manifest["record_contract"]["required_section_prefixes"]
    for claim, contract in manifest["audit_records"].items():
        path = REPO / contract["path"]
        text = path.read_text(encoding="ascii")
        metadata = parse_metadata(text)
        if metadata["claim"] != claim or metadata["reviewed"] != manifest["issued"]:
            raise AssertionError(f"record metadata mismatch {claim}: {metadata}")
        rows = parse_crosswalk(text)
        if any(row["status"] not in allowed for row in rows):
            raise AssertionError(f"unsupported crosswalk status in {claim}")
        dispositions[claim] = metadata["disposition"]
        load_bearing[claim] = metadata["load_bearing"]
        row_counts[claim] = len(rows)
        status_counts[claim] = dict(sorted(Counter(row["status"] for row in rows).items()))
        blockers[claim] = [
            row["status"] for row in rows if row["load_bearing"] and row["status"] in {"FAILED", "UNASSESSED"}
        ]
        search = parse_search(text, claim)
        searches[claim] = [search["returned_rows"], search["unique_source_ids"]]
        expected_search = manifest["bounded_searches"][claim]
        if search != expected_search:
            raise AssertionError(f"search contract mismatch {claim}: {search!r} != {expected_search!r}")
        section_coverage[claim] = all(
            any(line.startswith(prefix) for line in text.splitlines()) for prefix in section_prefixes
        )
        axes = parse_adversarial_axes(text)
        adversarial_counts[claim] = len(axes)
        normalized_axes = " ".join(axes).lower()
        for required in ("convention", "domain", "limit"):
            if required not in normalized_axes:
                raise AssertionError(f"missing adversarial axis {required} in {claim}")
        stale_prose_firewalls[claim] = "status.json` is the live claim authority" in text
        if re.search(r"[A-Za-z]:[/\\]Dev[/\\]Contents", text):
            raise AssertionError(f"machine-specific Contents root in {claim}")
        if claim in {"C4-GRAVITY-1LOOP", "C5-NEWTON-G"}:
            required_boundary = (
                "configured Contents source root" in text
                and "explicitly non-exhaustive" in text
                and "no world-first or no-source claim" in text
            )
            if not required_boundary:
                raise AssertionError(f"discovery boundary incomplete in {claim}")
        record_hashes[claim] = sha256(path)

    return {
        "record_dispositions": dispositions,
        "record_load_bearing": load_bearing,
        "crosswalk_row_counts": row_counts,
        "crosswalk_status_counts": status_counts,
        "load_bearing_blockers": blockers,
        "bounded_search_outcomes": searches,
        "section_coverage": section_coverage,
        "adversarial_axis_counts": adversarial_counts,
        "stale_prose_firewalls": stale_prose_firewalls,
        "record_hashes": record_hashes,
    }


def configured_contents_root() -> Path:
    configured = os.environ.get("TECT_LEGACY_SOURCE_ROOT")
    return Path(configured).resolve() if configured else (REPO.parent / "Contents").resolve()


def verify_source_hashes(manifest: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    internal: dict[str, str] = {}
    for name, source in manifest["source_authorities"].items():
        actual = sha256(REPO / source["path"])
        if actual != source["sha256"]:
            raise AssertionError(f"source hash drift {name}: {actual} != {source['sha256']}")
        internal[name] = actual

    external: dict[str, str] = {}
    root = configured_contents_root()
    for candidates in manifest["external_discovery_candidates"].values():
        for source in candidates:
            relative = source["path"]
            if not relative.startswith("Contents/"):
                raise AssertionError(f"invalid configured-root locator {relative}")
            path = root / relative.removeprefix("Contents/")
            actual = sha256(path)
            if actual != source["sha256"]:
                raise AssertionError(f"candidate hash drift {relative}: {actual} != {source['sha256']}")
            external[relative] = actual
    return internal, external


def rerun_bounded_searches(manifest: dict[str, Any]) -> dict[str, list[int]]:
    observed: dict[str, list[int]] = {}
    searcher = REPO / "verification/scripts/legacy_search.py"
    for claim, contract in manifest["bounded_searches"].items():
        command = [
            sys.executable,
            "-B",
            "-X",
            "utf8",
            str(searcher),
            "query",
            "--text",
            contract["query"],
            "--claim",
            contract["claim_filter"],
            "--limit",
            str(contract["limit"]),
            "--json",
        ]
        completed = subprocess.run(
            command,
            cwd=REPO,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(f"legacy search failed for {claim}: {completed.stderr}")
        payload = json.loads(completed.stdout)
        rows = payload["results"]
        observed[claim] = [len(rows), len({row["source_id"] for row in rows})]
    return observed


def gate_section(markdown: str, gate: str) -> str:
    pattern = re.compile(rf"^### \*\*{re.escape(gate)}\*\*\s*$([\s\S]*?)(?=^### |\Z)", re.MULTILINE)
    matches = pattern.findall(markdown)
    if len(matches) != 1:
        raise AssertionError(f"expected one gate section {gate}, found {len(matches)}")
    return matches[0]


def parse_json_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def lifecycle_check(manifest: dict[str, Any], staged: bool) -> dict[str, Any]:
    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    section = gate_section(gates, manifest["closed_gate_ids"][0])
    results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    explorations = parse_json_lines(REPO / "explorations/log.jsonl")
    events = parse_json_lines(REPO / "changelog/log.jsonl")
    tasks = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]
    task = [item for item in tasks if item.get("id") == manifest["task_id"]]
    if len(task) != 1:
        raise AssertionError("T-056 identity is not unique")
    outputs = [REPO / manifest["artifacts"][key] for key in ("primary_result", "independent_result", "integrated_result")]
    if staged:
        state = {
            "gate_open": "**Status:** OPEN" in section,
            "exploration_absent": not any(row.get("id") == manifest["exploration_id"] for row in explorations),
            "event_absent": not any(row.get("id") == manifest["formal_integration"]["event_id"] for row in events),
            "result_absent": manifest["result_id"] not in results,
            "task_in_progress": task[0].get("status") == "in_progress",
            "runs_absent": not any(path.exists() for path in outputs),
        }
    else:
        state = {
            "gate_scoped_closed": manifest["closed_gate_status"][manifest["closed_gate_ids"][0]] in section,
            "exploration_present": sum(row.get("id") == manifest["exploration_id"] for row in explorations) == 1,
            "event_present": sum(row.get("id") == manifest["formal_integration"]["event_id"] for row in events) == 1,
            "result_present": manifest["result_id"] in results and manifest["version"] in results,
            "task_done": task[0].get("status") == "done",
        }
    if not all(state.values()):
        raise AssertionError(f"lifecycle mismatch: {state}")
    return state


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="ascii")
    derived = derive_records(manifest)

    audit.check(
        "record disposition matrix",
        derived["record_dispositions"] == manifest["test_oracles"]["record_dispositions"],
        derived["record_dispositions"],
        manifest["test_oracles"]["record_dispositions"],
        "records",
    )
    audit.check(
        "record load-bearing matrix",
        derived["record_load_bearing"] == manifest["test_oracles"]["record_load_bearing"],
        derived["record_load_bearing"],
        manifest["test_oracles"]["record_load_bearing"],
        "records",
    )
    audit.check(
        "crosswalk row counts",
        derived["crosswalk_row_counts"] == manifest["test_oracles"]["crosswalk_row_counts"],
        derived["crosswalk_row_counts"],
        manifest["test_oracles"]["crosswalk_row_counts"],
        "records",
    )
    policy_ok = (
        derived["load_bearing_blockers"]["B1-RH-ENUM"] == []
        and all(not derived["record_load_bearing"][claim] for claim in manifest["claim_ids"][1:])
        and all(derived["section_coverage"].values())
        and all(count >= 3 for count in derived["adversarial_axis_counts"].values())
        and all(derived["stale_prose_firewalls"].values())
    )
    audit.check("applicability policy rules", policy_ok, derived, "no load-bearing failed/unassessed import", "policy")

    expected_hashes = {claim: record["sha256"] for claim, record in manifest["audit_records"].items()}
    audit.check("record hashes", derived["record_hashes"] == expected_hashes, derived["record_hashes"], expected_hashes, "provenance")
    internal_hashes, external_hashes = verify_source_hashes(manifest)
    audit.check("pinned internal source hashes", len(internal_hashes) == len(manifest["source_authorities"]), len(internal_hashes), len(manifest["source_authorities"]), "provenance")
    expected_external = sum(len(rows) for rows in manifest["external_discovery_candidates"].values())
    audit.check("discovery candidate hashes", len(external_hashes) == expected_external, len(external_hashes), expected_external, "provenance")

    rerun = rerun_bounded_searches(manifest)
    audit.check(
        "bounded search recomputation",
        rerun == manifest["test_oracles"]["bounded_search_outcomes"] == derived["bounded_search_outcomes"],
        rerun,
        manifest["test_oracles"]["bounded_search_outcomes"],
        "search",
    )

    live_states: dict[str, dict[str, Any]] = {}
    live_ok = True
    for claim, contract in manifest["live_claim_contract"].items():
        card = json.loads((REPO / contract["status_path"]).read_text(encoding="utf-8"))
        state = {"tier": card.get("tier"), "lifecycle": card.get("lifecycle")}
        live_states[claim] = state
        live_ok = live_ok and state == {"tier": contract["tier"], "lifecycle": contract["lifecycle"]}
        if "package_status" in contract:
            live_ok = live_ok and card.get("reproduction", {}).get("status") == contract["package_status"]
        if "named_hypothesis" in contract:
            live_ok = live_ok and contract["named_hypothesis"] in card.get("hypotheses", [])
    audit.check("live status authority", live_ok, live_states, "exact live tiers/lifecycles and package states", "claims")

    closure = manifest["closed_gate_status"].get("LITERATURE-FIRST-APPLICABILITY-AUDIT")
    scope_tokens = (
        "CLOSED@INITIAL-FOUR-RECORDS",
        "status.json` is the live authority",
        "does not imply",
        "discovery candidates",
        "16 pi`, `32 pi`, and `64 pi",
        "present BCC-premised inheritance route `DOES-NOT-APPLY`",
        "policy remains binding",
        "External review is invited",
        "No R-170 v1.0 PDF is issued",
    )
    flat = " ".join(certificate.split())
    audit.check("certificate scope and adversarial contract", closure == scope_tokens[0] and all(token in flat for token in scope_tokens), [token for token in scope_tokens if token in flat], list(scope_tokens), "scope")
    boundary = manifest["no_overclaim"]
    boundary_ok = all(
        token in boundary
        for token in (
            "claim-nonbearing",
            "policy remains binding",
            "No claim tier or lifecycle changes",
            "no new negative",
            "no physical-empty sign",
            "no physical Sector A or Pre-A closure",
            "No R-170 v1.0 PDF",
        )
    )
    audit.check("manifest no-overclaim", boundary_ok, boundary_ok, True, "scope")

    lifecycle = lifecycle_check(manifest, staged)
    audit.check("staged or formal lifecycle", all(lifecycle.values()), lifecycle, "all lifecycle assertions true", "lifecycle")

    return {
        "schema": "tect/pre-a-t056-initial-qft-gr-reading-h-literature-applicability-audit-primary/1.0",
        "version": __version__,
        "mode": "staged" if staged else "formal",
        "assertions": len(audit.rows),
        "checks": audit.rows,
        "derived": derived,
        "source_hash": normalized_sha256(SCRIPT),
        "manifest_hash": normalized_sha256(MANIFEST),
        "certificate_hash": normalized_sha256(CERTIFICATE),
        "verdict": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"PRIMARY PASS {payload['assertions']}/{payload['assertions']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
