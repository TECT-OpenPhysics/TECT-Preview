#!/usr/bin/env python3
"""Independent standard-library audit of the R-170 v1.0 rollout records.

This lane does not import the primary or integrated verifier. It uses a
line-oriented Markdown parser, independently reruns the selected-index
queries, and verifies both repository and configured Contents hashes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"


def byte_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            block = stream.read(65536)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def normalized_hash(path: Path) -> str:
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

    def require(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def unquote(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1]
    return value


def metadata_value(lines: list[str], label: str) -> str:
    prefix = f"**{label}:**"
    matches = [line[len(prefix):].strip() for line in lines if line.startswith(prefix)]
    if len(matches) != 1:
        raise AssertionError(f"expected one {label}, found {len(matches)}")
    return unquote(matches[0])


def disposition_root(value: str) -> str:
    value = value.lstrip("`")
    ordered = ("APPLIES-CONDITIONALLY", "DOES-NOT-APPLY", "NOT-YET-ASSESSED", "APPLIES")
    matches = [item for item in ordered if value.startswith(item)]
    if len(matches) != 1:
        raise AssertionError(f"invalid disposition {value}")
    return matches[0]


def section_lines(lines: list[str], number: int) -> list[str]:
    prefix = f"## {number} "
    starts = [index for index, line in enumerate(lines) if line.startswith(prefix)]
    if len(starts) != 1:
        raise AssertionError(f"section {number} count {len(starts)}")
    start = starts[0] + 1
    end = next((index for index in range(start, len(lines)) if lines[index].startswith("## ")), len(lines))
    return lines[start:end]


def crosswalk_rows(lines: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in section_lines(lines, 3):
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line[1:-1].split("|")]
        if len(cells) != 5 or cells[0] == "Source hypothesis" or cells[0].replace("-", "").replace(":", "") == "":
            continue
        rows.append(
            {
                "hypothesis": cells[0],
                "object": cells[1],
                "status": unquote(cells[2]),
                "load_bearing": cells[3].lower() == "yes",
                "reason": cells[4],
            }
        )
    if not rows:
        raise AssertionError("empty crosswalk")
    return rows


def search_fact(text: str, claim: str, contract: dict[str, Any]) -> list[int]:
    exact_command = (
        f'legacy_search.py query --text "{contract["query"]}" '
        f'--claim {claim} --limit {contract["limit"]} --json'
    )
    if exact_command not in text:
        raise AssertionError(f"missing search command {claim}")
    if "returned zero rows and zero unique source IDs" in text:
        return [0, 0]
    marker = "returned "
    position = text.find(marker)
    while position >= 0:
        tail = text[position + len(marker):]
        words = tail.split()
        if len(words) >= 5 and words[0].isdigit() and words[1] == "rows" and words[2] == "spanning" and words[3].isdigit():
            return [int(words[0]), int(words[3])]
        position = text.find(marker, position + 1)
    raise AssertionError(f"missing search result {claim}")


def adversarial_labels(lines: list[str]) -> list[str]:
    labels: list[str] = []
    for line in section_lines(lines, 6):
        if line.startswith("- **") and "**" in line[4:]:
            labels.append(line[4:].split("**", 1)[0])
    return labels


def derive_independent(manifest: dict[str, Any]) -> dict[str, Any]:
    dispositions: dict[str, str] = {}
    load_bearing: dict[str, bool] = {}
    row_counts: dict[str, int] = {}
    status_counts: dict[str, dict[str, int]] = {}
    blockers: dict[str, list[str]] = {}
    searches: dict[str, list[int]] = {}
    section_coverage: dict[str, bool] = {}
    adversarial_counts: dict[str, int] = {}
    stale_firewalls: dict[str, bool] = {}
    hashes: dict[str, str] = {}
    allowed = set(manifest["record_contract"]["crosswalk_statuses"])

    for claim in manifest["claim_ids"]:
        contract = manifest["audit_records"][claim]
        path = REPO / contract["path"]
        text = path.read_text(encoding="ascii")
        lines = text.splitlines()
        if metadata_value(lines, "Claim") != claim or metadata_value(lines, "Reviewed") != manifest["issued"]:
            raise AssertionError(f"metadata mismatch {claim}")
        dispositions[claim] = disposition_root(metadata_value(lines, "Overall disposition"))
        load_bearing[claim] = metadata_value(lines, "Load-bearing use").startswith("Yes")
        rows = crosswalk_rows(lines)
        if any(row["status"] not in allowed for row in rows):
            raise AssertionError(f"bad status {claim}")
        row_counts[claim] = len(rows)
        status_counts[claim] = dict(sorted(Counter(row["status"] for row in rows).items()))
        blockers[claim] = [
            row["status"] for row in rows if row["load_bearing"] and row["status"] in ("FAILED", "UNASSESSED")
        ]
        searches[claim] = search_fact(text, claim, manifest["bounded_searches"][claim])
        section_coverage[claim] = all(
            sum(line.startswith(prefix) for line in lines) == 1
            for prefix in manifest["record_contract"]["required_section_prefixes"]
        )
        labels = adversarial_labels(lines)
        adversarial_counts[claim] = len(labels)
        joined = " ".join(labels).lower()
        if not all(word in joined for word in ("convention", "domain", "limit")):
            raise AssertionError(f"missing adversarial axis {claim}")
        stale_firewalls[claim] = "status.json` is the live claim authority" in text
        if ":/Dev/Contents" in text or ":\\Dev\\Contents" in text:
            raise AssertionError(f"absolute Contents root {claim}")
        hashes[claim] = byte_hash(path)

    return {
        "record_dispositions": dispositions,
        "record_load_bearing": load_bearing,
        "crosswalk_row_counts": row_counts,
        "crosswalk_status_counts": status_counts,
        "load_bearing_blockers": blockers,
        "bounded_search_outcomes": searches,
        "section_coverage": section_coverage,
        "adversarial_axis_counts": adversarial_counts,
        "stale_prose_firewalls": stale_firewalls,
        "record_hashes": hashes,
    }


def resolve_contents() -> Path:
    setting = os.environ.get("TECT_LEGACY_SOURCE_ROOT")
    if setting:
        return Path(setting).resolve()
    return (REPO.parent / "Contents").resolve()


def source_checks(manifest: dict[str, Any]) -> dict[str, int]:
    internal = 0
    for source in manifest["source_authorities"].values():
        if byte_hash(REPO / source["path"]) != source["sha256"]:
            raise AssertionError(f"internal source drift {source['path']}")
        internal += 1
    external = 0
    root = resolve_contents()
    for sources in manifest["external_discovery_candidates"].values():
        for source in sources:
            prefix = "Contents/"
            if not source["path"].startswith(prefix):
                raise AssertionError(f"invalid Contents locator {source['path']}")
            if byte_hash(root / source["path"][len(prefix):]) != source["sha256"]:
                raise AssertionError(f"external source drift {source['path']}")
            external += 1
    return {"internal": internal, "external": external}


def run_searches(manifest: dict[str, Any]) -> dict[str, list[int]]:
    output: dict[str, list[int]] = {}
    program = REPO / "verification/scripts/legacy_search.py"
    for claim, contract in manifest["bounded_searches"].items():
        command = [
            sys.executable,
            "-B",
            "-X",
            "utf8",
            str(program),
            "query",
            "--text",
            contract["query"],
            "--claim",
            claim,
            "--limit",
            str(contract["limit"]),
            "--json",
        ]
        completed = subprocess.run(command, cwd=REPO, capture_output=True, text=True, encoding="utf-8")
        if completed.returncode:
            raise AssertionError(f"query failed {claim}: {completed.stderr}")
        rows = json.loads(completed.stdout)["results"]
        unique: set[str] = set()
        for row in rows:
            unique.add(row["source_id"])
        output[claim] = [len(rows), len(unique)]
    return output


def one_gate_section(text: str, gate: str) -> str:
    heading = f"### **{gate}**"
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if line == heading]
    if len(starts) != 1:
        raise AssertionError(f"gate heading count {gate}: {len(starts)}")
    start = starts[0] + 1
    end = next((index for index in range(start, len(lines)) if lines[index].startswith("### ")), len(lines))
    return "\n".join(lines[start:end])


def json_lines(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            result.append(json.loads(line))
    return result


def lifecycle(manifest: dict[str, Any], staged: bool) -> dict[str, bool]:
    gate = manifest["closed_gate_ids"][0]
    section = one_gate_section((REPO / "claims/GATES.md").read_text(encoding="utf-8"), gate)
    results = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
    explorations = json_lines(REPO / "explorations/log.jsonl")
    events = json_lines(REPO / "changelog/log.jsonl")
    tasks = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))["tasks"]
    task_rows = [row for row in tasks if row.get("id") == manifest["task_id"]]
    if len(task_rows) != 1:
        raise AssertionError("T-056 not unique")
    paths = [REPO / manifest["artifacts"][name] for name in ("primary_result", "independent_result", "integrated_result")]
    if staged:
        result = {
            "gate_open": "**Status:** OPEN" in section,
            "exp_absent": sum(row.get("id") == manifest["exploration_id"] for row in explorations) == 0,
            "event_absent": sum(row.get("id") == manifest["formal_integration"]["event_id"] for row in events) == 0,
            "result_absent": manifest["result_id"] not in results,
            "task_active": task_rows[0].get("status") == "in_progress",
            "runs_absent": not any(path.exists() for path in paths),
        }
    else:
        result = {
            "gate_scoped": manifest["closed_gate_status"][gate] in section,
            "exp_unique": sum(row.get("id") == manifest["exploration_id"] for row in explorations) == 1,
            "event_unique": sum(row.get("id") == manifest["formal_integration"]["event_id"] for row in events) == 1,
            "result_present": manifest["result_id"] in results and manifest["version"] in results,
            "task_done": task_rows[0].get("status") == "done",
        }
    if not all(result.values()):
        raise AssertionError(f"lifecycle mismatch {result}")
    return result


def run(staged: bool) -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    derived = derive_independent(manifest)
    oracle = manifest["test_oracles"]

    audit.require("independent disposition matrix", derived["record_dispositions"] == oracle["record_dispositions"], derived["record_dispositions"], oracle["record_dispositions"], "records")
    audit.require("independent load-bearing matrix", derived["record_load_bearing"] == oracle["record_load_bearing"], derived["record_load_bearing"], oracle["record_load_bearing"], "records")
    audit.require("independent row counts", derived["crosswalk_row_counts"] == oracle["crosswalk_row_counts"], derived["crosswalk_row_counts"], oracle["crosswalk_row_counts"], "records")
    policy = (
        derived["load_bearing_blockers"]["B1-RH-ENUM"] == []
        and all(not derived["record_load_bearing"][claim] for claim in manifest["claim_ids"][1:])
        and all(derived["section_coverage"].values())
        and all(value >= 3 for value in derived["adversarial_axis_counts"].values())
        and all(derived["stale_prose_firewalls"].values())
    )
    audit.require("independent policy decision", policy, policy, True, "policy")

    expected_hashes = {claim: manifest["audit_records"][claim]["sha256"] for claim in manifest["claim_ids"]}
    audit.require("independent record hashes", derived["record_hashes"] == expected_hashes, derived["record_hashes"], expected_hashes, "provenance")
    checked = source_checks(manifest)
    expected_external = sum(len(rows) for rows in manifest["external_discovery_candidates"].values())
    expected_checked = {"internal": len(manifest["source_authorities"]), "external": expected_external}
    audit.require("independent source pins", checked == expected_checked, checked, expected_checked, "provenance")

    observed = run_searches(manifest)
    audit.require("independent search results", observed == oracle["bounded_search_outcomes"] == derived["bounded_search_outcomes"], observed, oracle["bounded_search_outcomes"], "search")

    certificate = " ".join(CERTIFICATE.read_text(encoding="ascii").split())
    tokens = (
        "CLOSED@INITIAL-FOUR-RECORDS",
        "does not imply",
        "NOT-YET-ASSESSED",
        "16 pi`, `32 pi`, and `64 pi",
        "not a universal no-go",
        "policy remains binding",
        "External review is invited",
        "No R-170 v1.0 PDF is issued",
    )
    audit.require("independent certificate boundary", all(token in certificate for token in tokens), [token for token in tokens if token in certificate], list(tokens), "scope")
    boundary = manifest["no_overclaim"]
    audit.require("independent no-overclaim", manifest["claim_bearing"] is False and manifest["new_negative_ids"] == [] and "no physical Sector A or Pre-A closure" in boundary, boundary, "T0/no new negative/no physical closure", "scope")

    lifecycle_state = lifecycle(manifest, staged)
    audit.require("independent lifecycle", all(lifecycle_state.values()), lifecycle_state, "all true", "lifecycle")

    return {
        "schema": "tect/pre-a-t056-initial-qft-gr-reading-h-literature-applicability-audit-independent/1.0",
        "version": __version__,
        "mode": "staged" if staged else "formal",
        "assertions": len(audit.rows),
        "checks": audit.rows,
        "derived": derived,
        "source_hash": normalized_hash(SCRIPT),
        "manifest_hash": normalized_hash(MANIFEST),
        "certificate_hash": normalized_hash(CERTIFICATE),
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
    print(f"INDEPENDENT PASS {payload['assertions']}/{payload['assertions']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
