#!/usr/bin/env python3
"""Build the global TECT proof evidence map.

The generated Markdown is the human one-glance route map.  The generated JSON
is the complete machine-readable projection.  Neither is an authority for a
claim tier: status cards, proof notes, ledgers, and registries remain the
canonical sources.

Usage:
    python verification/scripts/build_proof_evidence_map.py
    python verification/scripts/build_proof_evidence_map.py --check
    python verification/scripts/build_proof_evidence_map.py --self-test
"""

__version__ = "1.2.0"

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from evidence_paths import (
    auditable_note_paths,
    lineage_note_paths,
    manifest_paths,
    unordered_root_note_paths,
)
from exploration import LOG as EXPLORATIONS, verify as verify_explorations


REPO = Path(__file__).resolve().parents[2]
OUT_MD = REPO / "theory" / "proof-evidence-map.md"
OUT_JSON = REPO / "verification" / "proof-evidence-map.json"
RESULTS = REPO / "RESULTS-LEDGER.md"
NEGATIVES = REPO / "negative-results" / "registry.md"
CHANGELOG = REPO / "changelog" / "log.jsonl"
TODO = REPO / "todo" / "todo.json"
GATES = REPO / "claims" / "GATES.md"

SECTOR_ORDER = tuple("ABCDEF")
TIER_ORDER = ("T7", "T6", "T5", "T4", "T3", "T2", "T1", "T0")
LIVE_TASK_STATUSES = {"in_progress", "next", "blocked", "backlog"}
TASK_STATUS_ORDER = {"in_progress": 0, "next": 1, "blocked": 2, "backlog": 3}
RECENT_EVENT_DISPLAY_LIMIT = 20  # tooling display threshold, not theory data
TABLE_TEXT_LIMIT = 210  # tooling display threshold, not theory data
FOOTER_ENFORCEMENT_DATE = "2026-07-24"
FOOTER_LABELS = (
    "Result ID",
    "Precise statement",
    "Scope",
    "Dependencies",
    "Evidence grade",
    "Reproduction command",
    "Expected output",
    "Falsification gate",
    "Tier before / after",
    "No-overclaim statement",
    "Next required action",
)

CLAIM_ID_RE = re.compile(r"\b([A-F]\d+[A-Z]?-[A-Z0-9][A-Z0-9-]{2,})\b")
FAMILY_RE = re.compile(r"\b([A-F]\d+[A-Z]?)\b")
RESULT_ROW_RE = re.compile(
    r"^\| \[(R-\d+)\]\(#([^)]+)\) \| (.*?) \| (.*?) \|$"
)
NEGATIVE_TAG = r"(?:R|F|NG|AUDIT)-[A-Za-z0-9-]+"
NEGATIVE_ROW_RE = re.compile(
    rf"^\| \[({NEGATIVE_TAG})\]\(#([^)]+)\) \| (.*?) \| (.*?) \|$"
)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    os.close(fd)
    try:
        Path(tmp).write_text(text, encoding="utf-8", newline="\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def sha256(path: Path) -> str:
    canonical = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(canonical).hexdigest()


def collapse(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def clip(text: object, limit: int = TABLE_TEXT_LIMIT) -> str:
    value = collapse(text)
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def pipe(text: object) -> str:
    return clip(text).replace("|", "\\|")


def pipe_full(text: object) -> str:
    return collapse(text).replace("|", "\\|")


def normalize_status(value: object) -> str:
    return collapse(value).lower()


def audit_note_footer(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = [
        label
        for label in FOOTER_LABELS
        if not re.search(rf"^\s*{re.escape(label)}:\s*", text, re.MULTILINE)
    ]
    version = re.search(r"%\s*Version:.*?first issued\s*(\d{4}-\d{2}-\d{2})", text)
    filename_date = re.search(r"(?<!\d)(\d{6})(?!\d)", path.name)
    if version:
        first_issued = version.group(1)
        date_basis = "version_metadata"
    elif filename_date:
        compact_date = filename_date.group(1)
        candidate_date = (
            f"20{compact_date[:2]}-{compact_date[2:4]}-{compact_date[4:]}"
        )
        try:
            date.fromisoformat(candidate_date)
        except ValueError:
            first_issued = ""
            date_basis = "unknown"
        else:
            first_issued = candidate_date
            date_basis = "filename"
    else:
        first_issued = ""
        date_basis = "unknown"
    return {
        "path": path.relative_to(REPO).as_posix(),
        "first_issued": first_issued,
        "date_basis": date_basis,
        "missing_labels": missing,
        "enforcement_applies": not first_issued or first_issued >= FOOTER_ENFORCEMENT_DATE,
    }


def markdown_anchor(identifier: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", identifier.lower()).strip("-")


def parse_labeled_fields(section: str) -> dict[str, str]:
    fields: dict[str, list[str]] = {}
    current = ""
    for line in section.splitlines():
        match = re.match(
            r"^(?:[-*+]\s+)?\*\*([^*]+?)\*\*\s*(.*)$",
            line.strip(),
        )
        if match:
            label = match.group(1).strip().rstrip(".:").lower()
            label = re.sub(r"[^a-z0-9]+", "_", label).strip("_")
            current = label
            fields.setdefault(current, [])
            if match.group(2).strip():
                fields[current].append(match.group(2).strip())
        elif current and line.strip() and line.strip() != "---":
            fields[current].append(line.strip())
    return {key: collapse(" ".join(value)) for key, value in fields.items()}


def first_labeled_paragraph(section: str, label: str) -> str:
    marker = re.compile(rf"^\*\*{re.escape(label)}:\*\*\s*(.*)$", re.IGNORECASE)
    collected: list[str] = []
    active = False
    for line in section.splitlines():
        if not active:
            match = marker.match(line.strip())
            if not match:
                continue
            active = True
            if match.group(1).strip():
                collected.append(match.group(1).strip())
            continue
        if not line.strip() or line.lstrip().startswith("**") or line.startswith("#"):
            break
        collected.append(line.strip())
    return collapse(" ".join(collected))


def parse_sections(text: str, identifier_pattern: str) -> dict[str, dict[str, object]]:
    heading = re.compile(
        rf"^###\s+({identifier_pattern})\b\s*(?:(?:--|—|–)\s*)?(.*)$",
        re.MULTILINE,
    )
    matches = list(heading.finditer(text))
    boundary = re.compile(r"^(?:<a\s+id=[^>]+></a>\s*$|#{1,3}\s+)", re.MULTILINE | re.IGNORECASE)
    sections: dict[str, dict[str, object]] = {}
    for match in matches:
        next_boundary = boundary.search(text, match.end())
        end = next_boundary.start() if next_boundary else len(text)
        identifier = match.group(1)
        if identifier in sections:
            raise ValueError(f"duplicate detail section: {identifier}")
        body = text[match.end() : end]
        sections[identifier] = {
            "title": collapse(match.group(2).lstrip("-—– ")),
            "fields": parse_labeled_fields(body),
        }
    return sections


def parse_results() -> list[dict[str, object]]:
    text = RESULTS.read_text(encoding="utf-8")
    rows: dict[str, dict[str, object]] = {}
    for line in text.splitlines():
        match = RESULT_ROW_RE.match(line)
        if not match:
            continue
        identifier, anchor, title, summary = match.groups()
        if identifier in rows:
            raise ValueError(f"duplicate result index row: {identifier}")
        rows[identifier] = {
            "id": identifier,
            "anchor": anchor,
            "title": collapse(title),
            "summary": collapse(summary),
        }
    sections = parse_sections(text, r"R-\d+")
    if set(rows) != set(sections):
        missing_detail = sorted(set(rows) - set(sections))
        missing_index = sorted(set(sections) - set(rows))
        raise ValueError(
            f"result registry coverage mismatch: missing_detail={missing_detail}; "
            f"missing_index={missing_index}"
        )
    output = []
    for identifier, row in rows.items():
        section = sections[identifier]
        row["detail_title"] = section["title"]
        row["detail"] = section["fields"]
        fields = section["fields"]
        row["normalized_detail"] = {
            "statement": fields.get("statement") or fields.get("statement_one_line", ""),
            "proof_anchor": fields.get("proven_in") or fields.get("where_proved", ""),
            "reuse": fields.get("reuse_scope") or fields.get("reuse", ""),
            "boundary": (
                fields.get("boundary")
                or fields.get("tier")
                or fields.get("tier_publication_target", "")
            ),
            "publication_target": fields.get("publication_target", ""),
        }
        output.append(row)
    return sorted(output, key=lambda item: int(str(item["id"]).split("-")[1]), reverse=True)


def parse_negatives() -> list[dict[str, object]]:
    text = NEGATIVES.read_text(encoding="utf-8")
    rows: dict[str, dict[str, object]] = {}
    for line in text.splitlines():
        match = NEGATIVE_ROW_RE.match(line)
        if not match:
            continue
        identifier, anchor, branch, summary = match.groups()
        if identifier in rows:
            raise ValueError(f"duplicate negative index row: {identifier}")
        rows[identifier] = {
            "tag": identifier,
            "anchor": anchor,
            "branch": collapse(branch),
            "summary": collapse(summary),
        }
    sections = parse_sections(text, NEGATIVE_TAG)
    if set(rows) != set(sections):
        missing_detail = sorted(set(rows) - set(sections))
        missing_index = sorted(set(sections) - set(rows))
        raise ValueError(
            f"negative registry coverage mismatch: missing_detail={missing_detail}; "
            f"missing_index={missing_index}"
        )
    output = []
    for identifier, row in rows.items():
        section = sections[identifier]
        fields = section["fields"]
        missing = [
            label
            for label in ("failure_mode", "evidence", "consequence")
            if not fields.get(label)
        ]
        if missing:
            raise ValueError(f"negative detail {identifier} lacks fields: {missing}")
        row["detail_title"] = section["title"]
        row["detail"] = fields
        row["kind"] = (
            "retraction"
            if identifier.startswith("R-")
            else "fired_falsifier"
            if identifier.startswith("F-")
            else "no_go"
            if identifier.startswith("NG-")
            else "audit"
        )
        output.append(row)

    def date_key(item: dict[str, object]) -> tuple[str, str]:
        match = re.search(r"(20\d{2}-\d{2}-\d{2})", str(item["tag"]))
        return (match.group(1) if match else "0000-00-00", str(item["tag"]))

    return sorted(output, key=date_key, reverse=True)


def parse_process_grade_lessons() -> list[str]:
    text = NEGATIVES.read_text(encoding="utf-8")
    match = re.search(
        r"^## Process-grade negative results[^\n]*\n(.*?)(?=^##\s)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        return []
    lessons: list[str] = []
    current: list[str] = []
    for line in match.group(1).splitlines():
        if line.startswith("- "):
            if current:
                lessons.append(collapse(" ".join(current)))
            current = [line[2:].strip()]
        elif current and line.strip():
            current.append(line.strip())
    if current:
        lessons.append(collapse(" ".join(current)))
    return lessons


def parse_gate_definitions() -> dict[str, dict[str, str]]:
    text = GATES.read_text(encoding="utf-8")
    heading = re.compile(
        r"^#{2,4}\s+\*\*([A-Z0-9][A-Z0-9-]+)\*\*\s*$", re.MULTILINE
    )
    matches = list(heading.finditer(text))
    definitions: dict[str, dict[str, str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        identifier = match.group(1)
        if identifier in definitions:
            raise ValueError(f"duplicate gate/hypothesis definition: {identifier}")
        section = text[match.end() : end]
        fields = parse_labeled_fields(section)
        fields["statement_summary"] = first_labeled_paragraph(section, "Statement")
        fields["status_summary"] = first_labeled_paragraph(section, "Status")
        definitions[identifier] = fields
    return definitions


def load_cards() -> list[dict[str, object]]:
    cards = []
    for status_path in sorted(
        (REPO / "claims").glob("*/status.json"), key=lambda path: path.parent.name
    ):
        if status_path.parent.name.startswith("_"):
            continue
        card = json.loads(status_path.read_text(encoding="utf-8"))
        identifier = str(card.get("id", ""))
        if identifier != status_path.parent.name:
            raise ValueError(
                f"status id/path mismatch: {status_path.parent.name} != {identifier}"
            )
        reproduction = card.get("reproduction")
        if not isinstance(reproduction, dict):
            reproduction = {}
        grades = card.get("evidence_grade", [])
        if isinstance(grades, str):
            grades = [grades]
        claim_dir = status_path.parent
        note_files = lineage_note_paths(claim_dir)
        unordered_notes = unordered_root_note_paths(claim_dir)
        note_paths = [path.relative_to(REPO).as_posix() for path in note_files]
        footer_audits = [audit_note_footer(path) for path in auditable_note_paths(claim_dir)]
        incomplete_footers = [audit for audit in footer_audits if audit["missing_labels"]]
        enforced_footer_failures = [
            audit for audit in incomplete_footers if audit["enforcement_applies"]
        ]
        if enforced_footer_failures:
            raise ValueError(
                f"claim {identifier} has post-{FOOTER_ENFORCEMENT_DATE} incomplete "
                f"result footers: {enforced_footer_failures}"
            )
        sibling_pdfs = [
            path.with_name(path.name.removesuffix(".tex.txt") + ".pdf")
            for path in note_files
        ]
        pdf_paths = [
            path.relative_to(REPO).as_posix() for path in sibling_pdfs if path.exists()
        ]
        missing_pdf_paths = [
            path.relative_to(REPO).as_posix() for path in sibling_pdfs if not path.exists()
        ]
        unordered_note_paths = [
            path.relative_to(REPO).as_posix() for path in unordered_notes
        ]
        unordered_pdf_paths = [
            path.with_name(path.name.removesuffix(".tex.txt") + ".pdf")
            .relative_to(REPO)
            .as_posix()
            for path in unordered_notes
            if path.with_name(path.name.removesuffix(".tex.txt") + ".pdf").exists()
        ]
        run_paths = sorted(
            path.relative_to(REPO).as_posix()
            for path in (claim_dir / "runs").rglob("*.json")
        ) if (claim_dir / "runs").exists() else []
        manifests = manifest_paths(claim_dir)
        claim_manifest_paths = [
            path.relative_to(REPO).as_posix() for path in manifests["claim_level"]
        ]
        bundle_manifest_paths = [
            path.relative_to(REPO).as_posix() for path in manifests["bundle_top"]
        ]
        bundle_embedded_manifest_paths = [
            path.relative_to(REPO).as_posix() for path in manifests["bundle_embedded"]
        ]
        index_path = claim_dir / "INDEX.md"
        cards.append(
            {
                "id": identifier,
                "title": card.get("title", ""),
                "sector": card.get("sector", "?"),
                "tier": card.get("tier", "?"),
                "lifecycle": card.get("lifecycle", "?"),
                "evidence_grade": list(grades),
                "dependencies": list(card.get("dependencies", [])),
                "soft_dependencies": list(card.get("soft_dependencies", [])),
                "hypotheses": list(card.get("hypotheses", [])),
                "open_gates": list(card.get("open_gates", [])),
                "statement": card.get("statement", ""),
                "scope": card.get("scope", ""),
                "falsifier": card.get("falsifier", ""),
                "next_action": card.get("next_action", ""),
                "notes": card.get("notes", ""),
                "last_review": card.get("last_review", ""),
                "reproduction": {
                    "command": reproduction.get("command", ""),
                    "expected": reproduction.get("expected", ""),
                    "status": reproduction.get("status", ""),
                },
                "paths": {
                    "claim": f"claims/{identifier}/claim.md",
                    "status": f"claims/{identifier}/status.json",
                    "lineage": f"claims/{identifier}/LINEAGE.md",
                    "index": index_path.relative_to(REPO).as_posix() if index_path.exists() else "",
                },
                "evidence_inventory": {
                    "proof_notes": note_paths,
                    "incomplete_historical_footers": incomplete_footers,
                    "proof_pdfs": pdf_paths,
                    "missing_sibling_pdfs": missing_pdf_paths,
                    "unordered_root_notes": unordered_note_paths,
                    "unordered_root_pdfs": unordered_pdf_paths,
                    "run_json": run_paths,
                    "manifests": claim_manifest_paths,
                    "bundle_manifests": bundle_manifest_paths,
                    "bundle_embedded_manifests": bundle_embedded_manifest_paths,
                },
            }
        )
    identifiers = [str(card["id"]) for card in cards]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate claim identifiers")
    for card in cards:
        for key in ("claim", "status", "lineage"):
            path = REPO / str(card["paths"][key])
            if not path.exists():
                raise ValueError(f"claim {card['id']} lacks required {key} path: {path}")
    return cards


def load_events() -> list[dict[str, object]]:
    events = []
    for sequence, line in enumerate(CHANGELOG.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        event = json.loads(line)
        events.append(
            {
                "sequence": sequence,
                "id": event.get("id", ""),
                "date": event.get("date", ""),
                "header": event.get("header", ""),
                "claim_ids": list(event.get("claim_ids", [])),
                "keywords": list(event.get("keywords", [])),
                "negative_results": list(event.get("neg_results", [])),
                "notes": list(event.get("notes", [])),
                "scripts": list(event.get("scripts", [])),
                "raw": event.get("raw", ""),
            }
        )
    identifiers = [str(event["id"]) for event in events]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate changelog event identifiers")
    return events


def load_tasks() -> list[dict[str, object]]:
    source = json.loads(TODO.read_text(encoding="utf-8"))
    tasks = []
    for task in source.get("tasks", []):
        value = dict(task)
        value["status_normalized"] = normalize_status(task.get("status", ""))
        value.setdefault("blocked_by", [])
        tasks.append(value)
    identifiers = [str(task.get("id", "")) for task in tasks]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("duplicate task identifiers")
    return tasks


def load_explorations() -> list[dict[str, object]]:
    records, errors = verify_explorations()
    if errors:
        raise ValueError("invalid exploration ledger: " + "; ".join(errors))
    return records


def claim_reference_context(
    cards: list[dict[str, object]],
) -> tuple[set[str], dict[str, list[str]]]:
    known = {str(card["id"]) for card in cards}
    families: dict[str, list[str]] = defaultdict(list)
    for identifier in known:
        families[identifier.split("-", 1)[0]].append(identifier)
    return known, families


def attach_event_references(
    events: list[dict[str, object]],
    cards: list[dict[str, object]],
    results: list[dict[str, object]],
) -> None:
    known_claims, _ = claim_reference_context(cards)
    known_results = {str(result["id"]) for result in results}
    result_pattern = re.compile(r"\bR-\d{3}\b")
    for event in events:
        explicit = [str(value) for value in event.get("claim_ids", [])]
        refs = sorted({value for value in explicit if value in known_claims})
        event["claim_refs"] = refs
        event["claim_ref_basis"] = {value: "explicit_claim_ids" for value in refs}
        event["unresolved_claim_ids"] = sorted(
            {value for value in explicit if value not in known_claims}
        )
        searchable = " ".join(
            [
                collapse(event.get("header", "")),
                collapse(event.get("raw", "")),
                " ".join(str(value) for value in event.get("notes", [])),
                " ".join(str(value) for value in event.get("scripts", [])),
            ]
        )
        event["result_ids"] = sorted(
            {value for value in result_pattern.findall(searchable) if value in known_results}
        )
        event["linked_result_ids"] = list(event["result_ids"])
        event["result_link_basis"] = {
            value: "explicit_result_id" for value in event["result_ids"]
        }


def attach_result_claim_references(
    results: list[dict[str, object]], cards: list[dict[str, object]]
) -> None:
    known, families = claim_reference_context(cards)
    leading_family = re.compile(r"^\s*`?([A-F]\d+[A-Z]?)(?=\s|/|`|-)")
    for record in results:
        proof_anchor = collapse(record.get("normalized_detail", {}).get("proof_anchor", ""))
        refs = {
            identifier
            for identifier in CLAIM_ID_RE.findall(proof_anchor)
            if identifier in known
        }
        basis = {identifier: "proof_anchor_exact" for identifier in refs}
        family_refs: set[str] = set()
        match = leading_family.match(proof_anchor)
        if match:
            family = match.group(1)
            family_refs.add(family)
            candidates = families.get(family, [])
            if len(candidates) == 1:
                refs.add(candidates[0])
                basis.setdefault(candidates[0], f"proof_anchor_unique_family:{family}")
        record["claim_refs"] = sorted(refs)
        record["claim_ref_basis"] = {
            identifier: basis[identifier] for identifier in sorted(basis)
        }
        record["family_refs"] = sorted(family_refs)


def attach_negative_claim_references(
    negatives: list[dict[str, object]],
    cards: list[dict[str, object]],
    events: list[dict[str, object]],
) -> None:
    known, families = claim_reference_context(cards)
    tag_family = re.compile(r"(?:^|-)([A-F]\d+[A-Z]?)(?=-|$)")
    primary_tag_family = re.compile(
        r"^(?:R|F|NG|AUDIT)-\d{4}-\d{2}-\d{2}-"
        r"([A-F]\d+[A-Z]?)(?=-|$)"
    )
    leading_family = re.compile(r"^\s*`?([A-F]\d+[A-Z]?)(?=\s|/|`|-)")
    parenthetical = re.compile(r"\(([^()]*)\)")
    slash_families = re.compile(
        r"^\s*([A-F]\d+[A-Z]?)(?:\s*/\s*([A-F]\d+[A-Z]?))+\s*$"
    )
    for record in negatives:
        detail = record.get("detail", {})
        structured_text = " ".join(
            [
                collapse(record.get("branch", "")),
                collapse(record.get("detail_title", "")),
                collapse(detail.get("failure_mode", "")),
                collapse(detail.get("evidence", "")),
                collapse(detail.get("consequence", "")),
            ]
        )
        refs = {
            identifier
            for identifier in CLAIM_ID_RE.findall(structured_text)
            if identifier in known
        }
        basis = {identifier: "structured_exact" for identifier in refs}
        tag = str(record["tag"])
        primary = primary_tag_family.match(tag)
        structural_families = (
            {primary.group(1)} if primary else set(tag_family.findall(tag))
        )
        for value in (record.get("branch", ""), record.get("detail_title", "")):
            match = leading_family.match(collapse(value))
            if match:
                structural_families.add(match.group(1))
            for group in parenthetical.findall(str(value)):
                if slash_families.fullmatch(group):
                    structural_families.update(FAMILY_RE.findall(group))
        for family in structural_families:
            candidates = families.get(family, [])
            if len(candidates) == 1:
                refs.add(candidates[0])
                basis.setdefault(candidates[0], f"structured_unique_family:{family}")

        for event in events:
            if record["tag"] not in event.get("negative_results", []):
                continue
            event_refs = list(event.get("claim_refs", []))
            if structural_families:
                event_refs = [
                    identifier
                    for identifier in event_refs
                    if identifier.split("-", 1)[0] in structural_families
                ]
            for identifier in event_refs:
                refs.add(identifier)
                basis.setdefault(
                    identifier, f"explicit_negative_event:{event['id']}"
                )
        record["claim_refs"] = sorted(refs)
        record["claim_ref_basis"] = {
            identifier: basis[identifier] for identifier in sorted(basis)
        }
        record["family_refs"] = sorted(structural_families)


def attach_result_event_links(
    results: list[dict[str, object]], events: list[dict[str, object]], known_negative_tags: set[str]
) -> None:
    for result in results:
        proof_anchor = collapse(result.get("normalized_detail", {}).get("proof_anchor", ""))
        related = []
        for event in events:
            basis = ""
            if result["id"] in event.get("result_ids", []):
                basis = "explicit_result_id"
            else:
                for note in event.get("notes", []):
                    name = Path(str(note)).name
                    if name.endswith(".tex.txt"):
                        stem = name.removesuffix(".tex.txt")
                    else:
                        stem = Path(name).stem
                    if len(stem) >= 12 and stem in proof_anchor:
                        basis = f"proof_anchor_note:{stem}"
                        break
            if not basis:
                continue
            related.append(event)
            linked = set(event.get("linked_result_ids", []))
            linked.add(str(result["id"]))
            event["linked_result_ids"] = sorted(linked)
            event.setdefault("result_link_basis", {})[str(result["id"])] = basis
        result["accepted_event_ids"] = [str(event["id"]) for event in related]
        result["co_recorded_negative_tags"] = sorted(
            {
                str(tag)
                for event in related
                for tag in event.get("negative_results", [])
                if tag in known_negative_tags
            }
        )


def source_hashes(status_paths: list[Path]) -> dict[str, str]:
    sources = [RESULTS, NEGATIVES, EXPLORATIONS, CHANGELOG, TODO, GATES] + status_paths
    return {
        path.relative_to(REPO).as_posix(): sha256(path)
        for path in sorted(sources, key=lambda item: item.relative_to(REPO).as_posix())
    }


def tier_profile(cards: list[dict[str, object]]) -> str:
    counts = Counter(str(card["tier"]) for card in cards)
    values = [f"{tier}x{counts[tier]}" for tier in TIER_ORDER if counts[tier]]
    values.extend(
        f"{tier}x{count}"
        for tier, count in sorted(counts.items())
        if tier not in TIER_ORDER
    )
    return " ".join(values) or "-"


def reference_index(
    records: list[dict[str, object]], key: str
) -> dict[str, list[str]]:
    index: dict[str, list[str]] = defaultdict(list)
    for record in records:
        for claim in record.get("claim_refs", []):
            index[str(claim)].append(str(record[key]))
    return {claim: values for claim, values in index.items()}


def build_graph(
    cards: list[dict[str, object]],
    results: list[dict[str, object]],
    negatives: list[dict[str, object]],
    explorations: list[dict[str, object]],
    events: list[dict[str, object]],
    tasks: list[dict[str, object]],
    gate_definitions: dict[str, dict[str, str]],
) -> dict[str, object]:
    nodes: dict[str, dict[str, str]] = {}
    edges: list[dict[str, str]] = []

    def add_node(identifier: str, kind: str, label: str, authority: str) -> None:
        value = {"id": identifier, "kind": kind, "label": label, "authority": authority}
        if identifier in nodes and nodes[identifier] != value:
            raise ValueError(f"graph node collision: {identifier}")
        nodes[identifier] = value

    def add_edge(source: str, relation: str, target: str, basis: str = "canonical") -> None:
        edges.append({"from": source, "relation": relation, "to": target, "basis": basis})

    referenced_gates = {
        str(value)
        for card in cards
        for value in list(card.get("open_gates", [])) + list(card.get("hypotheses", []))
    } | {
        str(value)
        for record in explorations
        for value in record.get("gate_ids", [])
    }
    for card in cards:
        identifier = str(card["id"])
        node = f"claim:{identifier}"
        add_node(node, "claim", collapse(card["title"]), str(card["paths"]["status"]))
    for gate in referenced_gates:
        kind = "hypothesis" if any(gate in card.get("hypotheses", []) for card in cards) else "gate"
        add_node(f"gate:{gate}", kind, gate, f"claims/GATES.md#{markdown_anchor(gate)}")
    for result in results:
        identifier = str(result["id"])
        add_node(
            f"result:{identifier}",
            "accepted_result",
            collapse(result["title"]),
            f"RESULTS-LEDGER.md#{result['anchor']}",
        )
    for record in negatives:
        identifier = str(record["tag"])
        add_node(
            f"negative:{identifier}",
            str(record["kind"]),
            collapse(record["branch"] or record["detail_title"]),
            f"negative-results/registry.md#{record['anchor']}",
        )
    for record in explorations:
        identifier = str(record["id"])
        add_node(
            f"exploration:{identifier}",
            "proof_exploration",
            collapse(record["title"]),
            "explorations/log.jsonl",
        )
    for event in events:
        identifier = str(event["id"])
        add_node(f"event:{identifier}", "accepted_event", collapse(event["header"]), "CHANGELOG.md")
    for task in tasks:
        identifier = str(task.get("id", ""))
        add_node(f"task:{identifier}", "task", collapse(task.get("title", "")), "todo/todo.json")

    known_claims = {str(card["id"]) for card in cards}
    known_tasks = {str(task.get("id", "")) for task in tasks}
    known_results = {str(result["id"]) for result in results}
    known_negatives = {str(record["tag"]) for record in negatives}
    for card in cards:
        claim_node = f"claim:{card['id']}"
        for dependency in card.get("dependencies", []):
            add_edge(claim_node, "depends_on", f"claim:{dependency}")
        for dependency in card.get("soft_dependencies", []):
            add_edge(claim_node, "soft_depends_on", f"claim:{dependency}")
        for hypothesis in card.get("hypotheses", []):
            add_edge(claim_node, "assumes", f"gate:{hypothesis}")
        for gate in card.get("open_gates", []):
            add_edge(claim_node, "blocked_by_gate", f"gate:{gate}")
    for result in results:
        for claim in result.get("claim_refs", []):
            basis = str(result.get("claim_ref_basis", {}).get(claim, "canonical"))
            add_edge(f"result:{result['id']}", "bears_on", f"claim:{claim}", basis)
    for record in negatives:
        for claim in record.get("claim_refs", []):
            basis = str(record.get("claim_ref_basis", {}).get(claim, "canonical"))
            add_edge(f"negative:{record['tag']}", "bears_on", f"claim:{claim}", basis)
    for record in explorations:
        node = f"exploration:{record['id']}"
        for claim in record.get("claim_ids", []):
            add_edge(node, "assesses", f"claim:{claim}", "structured_claim_id")
        task_id = record.get("task_id")
        if task_id:
            add_edge(node, "records_task", f"task:{task_id}", "structured_task_id")
        for gate in record.get("gate_ids", []):
            add_edge(node, "assesses_gate", f"gate:{gate}", "structured_gate_id")
        formal = record.get("formal_refs", {})
        for result in formal.get("results", []):
            add_edge(node, "references_result", f"result:{result}", "structured_formal_ref")
        for negative in formal.get("negatives", []):
            add_edge(node, "references_negative", f"negative:{negative}", "structured_formal_ref")
        for event in formal.get("events", []):
            add_edge(node, "references_event", f"event:{event}", "structured_formal_ref")
        for relation in record.get("related", []):
            add_edge(
                node,
                str(relation["relation"]),
                f"exploration:{relation['id']}",
                "structured_related_ref",
            )
    for event in events:
        for claim in event.get("claim_refs", []):
            if claim in known_claims:
                basis = str(event.get("claim_ref_basis", {}).get(claim, "canonical"))
                add_edge(f"event:{event['id']}", "records", f"claim:{claim}", basis)
        for result in event.get("linked_result_ids", []):
            if result in known_results:
                add_edge(
                    f"event:{event['id']}",
                    "records_result",
                    f"result:{result}",
                    str(event.get("result_link_basis", {}).get(result, "canonical")),
                )
        for negative in event.get("negative_results", []):
            if negative in known_negatives:
                add_edge(
                    f"event:{event['id']}",
                    "records_negative",
                    f"negative:{negative}",
                    "explicit_negative_tag",
                )
    for task in tasks:
        task_node = f"task:{task.get('id', '')}"
        claim = collapse(task.get("claim", ""))
        gate = collapse(task.get("gate", ""))
        if claim:
            add_edge(task_node, "advances", f"claim:{claim}")
        if gate:
            gate_node = f"gate:{gate}"
            if gate_node not in nodes:
                if gate in gate_definitions:
                    add_node(
                        gate_node,
                        "gate",
                        gate,
                        f"claims/GATES.md#{markdown_anchor(gate)}",
                    )
                else:
                    add_node(
                        gate_node,
                        "historical_gate_reference",
                        gate,
                        "todo/todo.json",
                    )
            add_edge(task_node, "targets", gate_node)
        for blocker in task.get("blocked_by", []):
            blocker = str(blocker)
            if blocker in known_tasks:
                add_edge(task_node, "blocked_by", f"task:{blocker}")

    unique_edges = {
        (edge["from"], edge["relation"], edge["to"], edge["basis"])
        for edge in edges
    }
    if len(unique_edges) != len(edges):
        raise ValueError("duplicate graph edges")
    for edge in edges:
        if edge["from"] not in nodes or edge["to"] not in nodes:
            raise ValueError(f"unresolved graph edge: {edge}")
    edges.sort(key=lambda edge: (edge["from"], edge["relation"], edge["to"], edge["basis"]))
    return {
        "namespace_contract": "claim:, result:, negative:, exploration:, event:, gate:, task:",
        "nodes": [nodes[key] for key in sorted(nodes)],
        "edges": edges,
    }


def build_data() -> dict[str, object]:
    cards = load_cards()
    results = parse_results()
    negatives = parse_negatives()
    explorations = load_explorations()
    process_grade_lessons = parse_process_grade_lessons()
    events = load_events()
    tasks = load_tasks()
    gate_definitions = parse_gate_definitions()
    attach_event_references(events, cards, results)
    attach_result_claim_references(results, cards)
    attach_negative_claim_references(negatives, cards, events)
    attach_result_event_links(
        results, events, {str(record["tag"]) for record in negatives}
    )

    known_claims = {str(card["id"]) for card in cards}
    known_tasks = {str(task.get("id", "")) for task in tasks}
    allowed_statuses = LIVE_TASK_STATUSES | {"done"}
    for task in tasks:
        status = str(task["status_normalized"])
        if status not in allowed_statuses:
            raise ValueError(f"task {task.get('id')} has invalid status {task.get('status')}")
        claim = collapse(task.get("claim", ""))
        if claim and claim not in known_claims:
            raise ValueError(f"task {task.get('id')} cites unknown claim {claim}")
        gate = collapse(task.get("gate", ""))
        if status in LIVE_TASK_STATUSES and gate and gate not in gate_definitions:
            raise ValueError(f"live task {task.get('id')} cites undefined gate {gate}")
        for blocker in task.get("blocked_by", []):
            blocker = str(blocker)
            if re.fullmatch(r"T-\d+", blocker) and blocker not in known_tasks:
                raise ValueError(f"task {task.get('id')} cites unknown blocker {blocker}")

    for card in cards:
        for dependency in list(card.get("dependencies", [])) + list(card.get("soft_dependencies", [])):
            if dependency not in known_claims:
                raise ValueError(f"claim {card['id']} cites unknown dependency {dependency}")
        reproduction = card.get("reproduction", {})
        if reproduction.get("status") == "AVAILABLE" and (
            not reproduction.get("command") or not reproduction.get("expected")
        ):
            raise ValueError(f"claim {card['id']} has incomplete AVAILABLE reproduction")

    open_gates = sorted(
        {str(gate) for card in cards for gate in card.get("open_gates", [])}
    )
    missing_gate_definitions = sorted(set(open_gates) - set(gate_definitions))
    if missing_gate_definitions:
        raise ValueError(f"open gates lack definitions: {missing_gate_definitions}")
    named_hypotheses = {
        str(hypothesis) for card in cards for hypothesis in card.get("hypotheses", [])
    }
    missing_hypotheses = sorted(named_hypotheses - set(gate_definitions))
    if missing_hypotheses:
        raise ValueError(f"named hypotheses lack definitions: {missing_hypotheses}")

    result_index = reference_index(results, "id")
    negative_index = reference_index(negatives, "tag")
    exploration_index: dict[str, list[str]] = defaultdict(list)
    for record in explorations:
        for claim in record.get("claim_ids", []):
            exploration_index[str(claim)].append(str(record["id"]))
    event_index = reference_index(events, "id")
    event_by_id = {str(event["id"]): event for event in events}
    for card in cards:
        identifier = str(card["id"])
        accepted = event_index.get(identifier, [])
        card["evidence_links"] = {
            "result_ids": result_index.get(identifier, []),
            "negative_tags": negative_index.get(identifier, []),
            "exploration_ids": exploration_index.get(identifier, []),
            "latest_exploration_id": (
                exploration_index.get(identifier, [""])[-1]
                if exploration_index.get(identifier)
                else ""
            ),
            "accepted_event_ids": accepted,
            "latest_event_id": accepted[-1] if accepted else "",
        }

    live_tasks = [
        task for task in tasks if str(task["status_normalized"]) in LIVE_TASK_STATUSES
    ]
    live_tasks.sort(
        key=lambda task: (
            TASK_STATUS_ORDER.get(str(task["status_normalized"]), 99),
            str(task.get("id", "")),
        )
    )

    for card in cards:
        identifier = str(card["id"])
        live_task_gates = sorted(
            {
                collapse(task.get("gate", ""))
                for task in live_tasks
                if task.get("claim") == identifier and collapse(task.get("gate", ""))
            }
        )
        card["evidence_links"]["live_task_gate_ids"] = live_task_gates
        card["evidence_links"]["route_gate_ids"] = sorted(
            set(str(value) for value in card.get("open_gates", []))
            | set(live_task_gates)
        )

    current_route_gates = sorted(
        set(open_gates)
        | {
            collapse(task.get("gate", ""))
            for task in live_tasks
            if collapse(task.get("gate", ""))
        }
    )

    gate_index = []
    for gate in current_route_gates:
        card_owners = sorted(
            str(card["id"]) for card in cards if gate in card.get("open_gates", [])
        )
        task_owners = sorted(
            {
                collapse(task.get("claim", ""))
                for task in live_tasks
                if task.get("gate") == gate and collapse(task.get("claim", ""))
            }
        )
        owners = sorted(set(card_owners) | set(task_owners))
        task_ids = sorted(
            str(task.get("id", "")) for task in live_tasks if task.get("gate") == gate
        )
        gate_index.append(
            {
                "id": gate,
                "owners": owners,
                "claim_card_owners": card_owners,
                "live_task_owners": task_owners,
                "live_tasks": task_ids,
                "definition": gate_definitions.get(gate, {}),
                "path": f"claims/GATES.md#{markdown_anchor(gate)}",
            }
        )

    sector_rows = []
    for sector in SECTOR_ORDER:
        sector_cards = [card for card in cards if card.get("sector") == sector]
        sector_open = sorted(
            {
                str(gate)
                for card in sector_cards
                for gate in card["evidence_links"].get("route_gate_ids", [])
            }
        )
        claim_ids = {str(card["id"]) for card in sector_cards}
        sector_live = [task for task in live_tasks if task.get("claim") in claim_ids]
        sector_rows.append(
            {
                "sector": sector,
                "status_cards": len(sector_cards),
                "active": sum(card.get("lifecycle") == "ACTIVE" for card in sector_cards),
                "refuted": sum(card.get("lifecycle") == "REFUTED" for card in sector_cards),
                "tier_profile": tier_profile(sector_cards),
                "open_gates": sector_open,
                "live_tasks": [str(task.get("id", "")) for task in sector_live],
            }
        )

    for event in events:
        event.pop("sequence", None)

    graph = build_graph(
        cards, results, negatives, explorations, events, tasks, gate_definitions
    )

    status_paths = [REPO / str(card["paths"]["status"]) for card in cards]
    coverage = {
        "status_cards": len(cards),
        "active_claims": sum(card.get("lifecycle") == "ACTIVE" for card in cards),
        "refuted_claims": sum(card.get("lifecycle") == "REFUTED" for card in cards),
        "reusable_results": len(results),
        "negative_records": len(negatives),
        "proof_explorations": len(explorations),
        "exploration_verdicts": {
            verdict: sum(record["verdict"] == verdict for record in explorations)
            for verdict in ("advanced", "failed", "inconclusive", "parked")
        },
        "process_grade_lessons": len(process_grade_lessons),
        "accepted_events": len(events),
        "tasks": len(tasks),
        "live_tasks": len(live_tasks),
        "completed_tasks": sum(str(task["status_normalized"]) == "done" for task in tasks),
        "open_gates": len(open_gates),
        "current_route_gates": len(current_route_gates),
        "sectors": len([row for row in sector_rows if row["status_cards"]]),
        "proof_notes": sum(
            len(card["evidence_inventory"]["proof_notes"]) for card in cards
        ),
        "proof_pdfs": sum(
            len(card["evidence_inventory"]["proof_pdfs"]) for card in cards
        ),
        "unordered_root_notes": sum(
            len(card["evidence_inventory"]["unordered_root_notes"])
            for card in cards
        ),
        "unordered_root_pdfs": sum(
            len(card["evidence_inventory"]["unordered_root_pdfs"])
            for card in cards
        ),
        "proof_notes_without_sibling_pdf": sum(
            len(card["evidence_inventory"]["missing_sibling_pdfs"]) for card in cards
        ),
        "proof_notes_with_incomplete_historical_footer": sum(
            len(card["evidence_inventory"]["incomplete_historical_footers"])
            for card in cards
        ),
        "run_json": sum(
            len(card["evidence_inventory"]["run_json"]) for card in cards
        ),
        "claim_manifests": sum(
            len(card["evidence_inventory"]["manifests"]) for card in cards
        ),
        "bundle_manifests": sum(
            len(card["evidence_inventory"]["bundle_manifests"]) for card in cards
        ),
        "bundle_embedded_manifests": sum(
            len(card["evidence_inventory"]["bundle_embedded_manifests"])
            for card in cards
        ),
    }
    gate_status_conflicts = []
    for gate in gate_index:
        status = collapse(gate["definition"].get("status_summary", ""))
        if status.upper().startswith("CLOSED"):
            gate_status_conflicts.append(
                {"gate": gate["id"], "owners": gate["owners"], "registered_status": status}
            )
    diagnostics = {
        "claims_without_generated_index": [
            str(card["id"]) for card in cards if not card["paths"].get("index")
        ],
        "historical_notes_without_sibling_pdf": [
            path
            for card in cards
            for path in card["evidence_inventory"]["missing_sibling_pdfs"]
        ],
        "grandfathered_incomplete_note_footers": [
            audit
            for card in cards
            for audit in card["evidence_inventory"]["incomplete_historical_footers"]
        ],
        "open_gate_status_conflicts": gate_status_conflicts,
        "claim_unbound_result_ids": [
            str(result["id"]) for result in results if not result.get("claim_refs")
        ],
        "claim_unbound_negative_tags": [
            str(record["tag"]) for record in negatives if not record.get("claim_refs")
        ],
        "historical_task_gate_references": [
            {"task": str(task.get("id", "")), "gate": collapse(task.get("gate", ""))}
            for task in tasks
            if collapse(task.get("gate", ""))
            and collapse(task.get("gate", "")) not in gate_definitions
        ],
        "historical_event_noncard_claim_ids": [
            {"event": str(event["id"]), "claim_ids": event["unresolved_claim_ids"]}
            for event in events
            if event.get("unresolved_claim_ids")
        ],
        "event_unregistered_negative_tags": [
            {"event": str(event["id"]), "tags": unknown}
            for event in events
            for unknown in [
                sorted(
                    set(str(value) for value in event.get("negative_results", []))
                    - {str(record["tag"]) for record in negatives}
                )
            ]
            if unknown
        ],
        "footer_enforcement_date": FOOTER_ENFORCEMENT_DATE,
        "exploration_prospective_coverage_from": "2026-07-24",
        "historical_backfill_explorations": sum(
            record.get("provenance") == "historical-backfill"
            for record in explorations
        ),
    }
    return {
        "schema": "tect/proof-evidence-map/1.2",
        "generator": {
            "path": "verification/scripts/build_proof_evidence_map.py",
            "version": __version__,
        },
        "authority_boundary": (
            "This projection is complete by reference but is not a tier or proof "
            "authority. Claim status cards, proof notes/runs, RESULTS-LEDGER.md, "
            "negative-results/registry.md, explorations/log.jsonl, "
            "changelog/log.jsonl, todo/todo.json, and claims/GATES.md remain canonical."
        ),
        "source_hashes": source_hashes(status_paths),
        "coverage": coverage,
        "coverage_diagnostics": diagnostics,
        "sectors": sector_rows,
        "live_tasks": live_tasks,
        "open_gate_index": gate_index,
        "claims": cards,
        "reusable_results": results,
        "negative_records": negatives,
        "proof_explorations": explorations,
        "inconclusive_or_parked_exploration_ids": [
            str(record["id"])
            for record in explorations
            if record["verdict"] in {"inconclusive", "parked"}
        ],
        "process_grade_lessons": process_grade_lessons,
        "accepted_events": events,
        "all_tasks": tasks,
        "graph": graph,
    }


def claim_link(identifier: str, label: str | None = None) -> str:
    return f"[{label or identifier}](../claims/{identifier}/claim.md)"


def gate_link(identifier: str) -> str:
    return f"[{identifier}](../claims/GATES.md#{markdown_anchor(identifier)})"


def compact_links(identifiers: list[str], kind: str, maximum: int = 2) -> str:
    if not identifiers:
        return "-"
    shown = identifiers[:maximum]
    if kind == "result":
        links = [f"[{value}](../RESULTS-LEDGER.md#{value.lower()})" for value in shown]
    elif kind == "exploration":
        links = [f"[{value}](#{value.lower()})" for value in shown]
    else:
        links = [
            f"[{value}](../negative-results/registry.md#{markdown_anchor(value)})"
            for value in shown
        ]
    if len(identifiers) > maximum:
        links.append(f"+{len(identifiers) - maximum}")
    return ", ".join(links)


def exploration_evidence_link(reference: str) -> str:
    path, _, locator = reference.partition("#")
    label = path.replace("|", "\\|")
    suffix = f" ({locator})" if locator else ""
    return f"[`{label}`](../{path}){suffix}"


def mermaid_id(identifier: str) -> str:
    return "N_" + re.sub(r"[^A-Za-z0-9_]", "_", identifier)


def mermaid_label(value: object, limit: int = 70) -> str:
    return clip(value, limit).replace('"', "'").replace("&", "and")


def render_mermaid(live_tasks: list[dict[str, object]]) -> list[str]:
    lines = ["```mermaid", "flowchart LR"]
    task_ids = {str(task.get("id", "")) for task in live_tasks}
    gates_seen: set[str] = set()
    claims_seen: set[str] = set()
    for task in live_tasks:
        identifier = str(task.get("id", ""))
        status = str(task.get("status_normalized", ""))
        node = mermaid_id(identifier)
        label = mermaid_label(task.get("title", ""), 58)
        lines.append(f'  {node}["{identifier}<br/>{status}<br/>{label}"]')
        gate = collapse(task.get("gate", ""))
        if gate:
            gate_node = mermaid_id(gate)
            if gate not in gates_seen:
                lines.append(f'  {gate_node}{{"{mermaid_label(gate, 72)}"}}')
                gates_seen.add(gate)
            lines.append(f"  {node} -->|targets| {gate_node}")
        claim = collapse(task.get("claim", ""))
        if gate and claim:
            claim_node = mermaid_id(claim)
            if claim not in claims_seen:
                lines.append(f'  {claim_node}["{mermaid_label(claim, 72)}"]')
                claims_seen.add(claim)
            lines.append(f"  {mermaid_id(gate)} -->|advances| {claim_node}")
        for blocker in task.get("blocked_by", []):
            if str(blocker) in task_ids:
                lines.append(
                    f'  {node} -. "blocked by" .-> {mermaid_id(str(blocker))}'
                )
    lines += [
        "  classDef active fill:#d7f5df,stroke:#257942,color:#102418",
        "  classDef waiting fill:#fff2cc,stroke:#a87900,color:#2a2100",
    ]
    active_nodes = [
        mermaid_id(str(task.get("id", "")))
        for task in live_tasks
        if task.get("status_normalized") in {"in_progress", "next"}
    ]
    waiting_nodes = [
        mermaid_id(str(task.get("id", "")))
        for task in live_tasks
        if task.get("status_normalized") in {"blocked", "backlog"}
    ]
    if active_nodes:
        lines.append(f"  class {','.join(active_nodes)} active")
    if waiting_nodes:
        lines.append(f"  class {','.join(waiting_nodes)} waiting")
    lines.append("```")
    return lines


def render_markdown(data: dict[str, object]) -> str:
    coverage = data["coverage"]
    cards = data["claims"]
    results = data["reusable_results"]
    negatives = data["negative_records"]
    explorations = data["proof_explorations"]
    exploration_by_id = {
        str(record["id"]): record for record in explorations
    }
    process_grade_lessons = data["process_grade_lessons"]
    live_tasks = data["live_tasks"]
    events = data["accepted_events"]
    event_by_id = {str(event["id"]): event for event in events}

    lines = [
        "# TECT proof evidence map",
        "",
        "> GENERATED by `verification/scripts/build_proof_evidence_map.py` - do not hand-edit. ",
        "> This is a complete-by-reference navigation and audit surface, not a new proof or tier authority.",
        "",
        "> **Bounded reader route:** start with [`proof-evidence/INDEX.md`](proof-evidence/INDEX.md)",
        "> and search this compatibility map only by the required ID.",
        "",
        "Use this page to see what succeeded, what failed and why, what remains open,",
        "and where each assertion can be reproduced. The linked claim card, proof note/run,",
        "result ledger, exploration record, negative-result entry, gate definition, task ledger, or changelog entry",
        "always remains authoritative.",
        "",
        "## One-glance record flow",
        "",
        "```mermaid",
        "flowchart LR",
        '  P["Proof note + reproducible run"] --> C["Claim current state"]',
        '  P --> E["Append-only route assessment"]',
        '  P --> S["Accepted reusable result / RESULTS-LEDGER"]',
        '  P --> F["Failed route / negative registry"]',
        '  E --> S',
        '  E --> F',
        '  E --> G',
        '  S --> G["Open gate"]',
        '  F --> G',
        '  G --> T["Live TODO frontier"]',
        '  C --> M["This generated evidence map"]',
        '  S --> M',
        '  F --> M',
        '  E --> M',
        '  T --> M',
        "```",
        "",
        "## Repository proof snapshot",
        "",
        "| Record class | Count | Meaning |",
        "|---|---:|---|",
        f"| Status cards | {coverage['status_cards']} | {coverage['active_claims']} active; {coverage['refuted_claims']} refuted |",
        f"| Reusable result records | {coverage['reusable_results']} | Curated theorems, reductions, partial advances, and no-go lemmas with proof anchors |",
        f"| Negative/audit records | {coverage['negative_records']} indexed + {coverage['process_grade_lessons']} legacy process lessons | No-go, falsifier, retraction, and process-audit trust assets with evidence and consequence |",
        f"| Proof explorations | {coverage['proof_explorations']} | Route decisions: "
        + ", ".join(
            f"{verdict} {count}"
            for verdict, count in coverage["exploration_verdicts"].items()
        )
        + "; non-tier-bearing |",
        f"| Accepted chronological events | {coverage['accepted_events']} | Complete history is preserved in the JSON map and `changelog/log.jsonl`; use `changelog/INDEX.md` for bounded reading |",
        f"| Tasks | {coverage['tasks']} | {coverage['live_tasks']} live; {coverage['completed_tasks']} completed |",
        f"| Current route gates | {coverage['current_route_gates']} | {coverage['open_gates']} claim-card gates plus live-task child targets, deduplicated |",
        f"| Proof evidence inventory | {coverage['proof_notes']} lineage notes / {coverage['proof_pdfs']} sibling PDFs / {coverage['unordered_root_notes']} legacy unordered root notes / {coverage['unordered_root_pdfs']} paired root PDFs / {coverage['run_json']} run JSON files / {coverage['claim_manifests']} claim-level manifests / {coverage['bundle_manifests']} bundle manifests / {coverage['bundle_embedded_manifests']} frozen embedded manifests | Complete paths and disjoint manifest classes are stored per claim in the machine map; {coverage['proof_notes_without_sibling_pdf']} historical/superseded lineage-note paths lack a sibling PDF and {coverage['proof_notes_with_incomplete_historical_footer']} grandfathered evidence notes have incomplete standard footers, all kept visible |",
        "",
        "## Coverage diagnostics",
        "",
        "These are visible migration or metadata debts, not silently dropped records.",
        "",
        "| Diagnostic | Count | Management rule |",
        "|---|---:|---|",
        f"| Claims without generated `INDEX.md` | {len(data['coverage_diagnostics']['claims_without_generated_index'])} | Evidence-map and sector-dossier links fall back to `claim.md`; `LINEAGE.md` remains available |",
        f"| Historical/superseded notes without sibling PDF | {len(data['coverage_diagnostics']['historical_notes_without_sibling_pdf'])} | Paths remain in machine inventory; current-note PDF enforcement is unchanged |",
        f"| Grandfathered notes with incomplete standard footer | {len(data['coverage_diagnostics']['grandfathered_incomplete_note_footers'])} | Kept visible; notes first issued on/after {data['coverage_diagnostics']['footer_enforcement_date']} fail the map gate if any mandatory footer label is absent |",
        f"| Claim cards listing a gate whose registered status begins `CLOSED` | {len(data['coverage_diagnostics']['open_gate_status_conflicts'])} | Exposed as reconciliation debt; the map does not silently flip claim cards |",
        f"| Claim-unbound reusable results / negative records | {len(data['coverage_diagnostics']['claim_unbound_result_ids'])} / {len(data['coverage_diagnostics']['claim_unbound_negative_tags'])} | Ambiguous family references stay unbound; no claim edge is invented |",
        f"| Completed-task references to retired gate identifiers | {len(data['coverage_diagnostics']['historical_task_gate_references'])} | Preserved as `historical_gate_reference` nodes anchored to `todo/todo.json`, never mislinked to the current gate registry |",
        f"| Changelog tokens that are not current claim-card IDs | {sum(len(item['claim_ids']) for item in data['coverage_diagnostics']['historical_event_noncard_claim_ids'])} | Preserved in event metadata but never promoted to claim edges; many are historical proof-unit IDs from the legacy extractor |",
        f"| Changelog negative tags absent from the indexed registry | {sum(len(item['tags']) for item in data['coverage_diagnostics']['event_unregistered_negative_tags'])} | Preserved as historical event text, rendered without a false registry anchor, and excluded from negative graph edges |",
        f"| Historical exploration backfill | {data['coverage_diagnostics']['historical_backfill_explorations']} | Directly recovered from cited tracked evidence; pre-{data['coverage_diagnostics']['exploration_prospective_coverage_from']} chat-only deliberation is explicitly not claimed complete |",
        "",
        "## Current proof-route roadmap",
        "",
    ]
    lines += render_mermaid(live_tasks)
    lines += [
        "",
        "| Task | State | Claim | Target gate | Core next action / reason |",
        "|---|---|---|---|---|",
    ]
    for task in live_tasks:
        claim = collapse(task.get("claim", ""))
        gate = collapse(task.get("gate", ""))
        note = task.get("note", "")
        blocked = task.get("blocked_by", [])
        if blocked:
            note = f"Blocked by {', '.join(str(value) for value in blocked)}. {note}"
        lines.append(
            f"| **{pipe(task.get('id', ''))}** {pipe(task.get('title', ''))} | "
            f"{pipe(task.get('status_normalized', ''))} | "
            f"{claim_link(claim) if claim else '-'} | "
            f"{gate_link(gate) if gate else '-'} | {pipe_full(note)} |"
        )

    lines += [
        "",
        "## Sector state map",
        "",
        "| Sector | Status cards | Lifecycle | Tier profile | Current route gates | Live tasks |",
        "|---|---:|---|---|---:|---|",
    ]
    for sector in data["sectors"]:
        lines.append(
            f"| [{sector['sector']}](sectors/{sector['sector']}.md) | "
            f"{sector['status_cards']} | {sector['active']} active / {sector['refuted']} refuted | "
            f"{pipe(sector['tier_profile'])} | {len(sector['open_gates'])} | "
            f"{', '.join(sector['live_tasks']) or '-'} |"
        )

    lines += [
        "",
        "## Current route-gate ownership",
        "",
        "This union keeps claim-card umbrella gates and live-task child gates visible together.",
        "Ownership source remains explicit; the map does not rewrite a claim card.",
        "",
        "| Gate | Claim owners | Source | Live tasks | Current registered status |",
        "|---|---|---|---|---|",
    ]
    for gate in data["open_gate_index"]:
        owners = ", ".join(claim_link(value, value) for value in gate["owners"])
        status = (
            gate["definition"].get("status_summary")
            or gate["definition"].get("status")
            or "See gate definition."
        )
        lines.append(
            f"| {gate_link(gate['id'])} | {owners or '-'} | "
            f"{'claim card' if gate['claim_card_owners'] else 'live task'}"
            f"{' + live task' if gate['claim_card_owners'] and gate['live_task_owners'] else ''} | "
            f"{', '.join(gate['live_tasks']) or '-'} | {pipe_full(status)} |"
        )

    lines += [
        "",
        "## Proof-exploration decision record",
        "",
        "This is the complete projection of `explorations/log.jsonl`. It records",
        "researcher-reusable route decisions, not private token-by-token reasoning.",
        "`advanced` is not proof; `failed` is not a formal global no-go unless an",
        "explicit negative-registry reference is present. Prospective mandatory",
        f"coverage begins {data['coverage_diagnostics']['exploration_prospective_coverage_from']}; "
        "older backfill is evidence-limited.",
        "",
        "### Recorded inconclusive or parked route assessments",
        "",
        "This table is a review aid, not a substitute for the live TODO order.",
        "",
        "| Exploration | Reviewed | Verdict | Claim / gate | Finding | Next or resume condition |",
        "|---|---|---|---|---|---|",
    ]
    for record in sorted(
        [
            exploration_by_id[identifier]
            for identifier in data["inconclusive_or_parked_exploration_ids"]
        ],
        key=lambda item: (str(item["reviewed_on"]), str(item["id"])),
    ):
        owners = ", ".join(claim_link(str(value)) for value in record["claim_ids"])
        gates = ", ".join(gate_link(str(value)) for value in record["gate_ids"])
        lines.append(
            f"| [{record['id']}](#{str(record['id']).lower()}) {pipe(record['title'])} | "
            f"{record['reviewed_on']} | {record['verdict']} | {owners}"
            f"{'<br/>' + gates if gates else ''} | {pipe_full(record['finding'])} | "
            f"{pipe_full(record['next_action'])} |"
        )

    lines += [
        "",
        "### Complete reviewed chronology",
        "",
    ]
    negative_anchors = {
        str(record["tag"]): str(record["anchor"]) for record in negatives
    }
    for record in sorted(
        explorations,
        key=lambda item: (str(item["reviewed_on"]), str(item["id"])),
    ):
        identifier = str(record["id"])
        claims_text = ", ".join(
            claim_link(str(value)) for value in record["claim_ids"]
        )
        gates_text = ", ".join(
            gate_link(str(value)) for value in record["gate_ids"]
        ) or "-"
        task_text = f"`{record['task_id']}`" if record.get("task_id") else "-"
        formal = record["formal_refs"]
        formal_links = [
            f"[{value}](../RESULTS-LEDGER.md#{str(value).lower()})"
            for value in formal["results"]
        ]
        formal_links.extend(
            f"[{value}](../negative-results/registry.md#{negative_anchors[value]})"
            for value in formal["negatives"]
        )
        formal_links.extend(f"`event:{value}`" for value in formal["events"])
        related = ", ".join(
            f"{item['relation']} [{item['id']}](#{str(item['id']).lower()})"
            for item in record["related"]
        ) or "-"
        lines += [
            f'<a id="{identifier.lower()}"></a>',
            f"#### {identifier} — {record['title']}",
            "",
            f"- **Review metadata:** reviewed {record['reviewed_on']}; recorded "
            f"{record['recorded_at']}; `{record['provenance']}`; verdict "
            f"**{record['verdict']}**.",
            f"- **Structured scope:** claim {claims_text}; gate {gates_text}; task {task_text}.",
            f"- **Question:** {record['question']}",
            "- **Finite checks:** " + " ".join(
                f"({number}) {method}" for number, method in enumerate(record["method"], start=1)
            ),
            f"- **Finding:** {record['finding']}",
            f"- **Decision reason:** {record['decision_reason']}",
            f"- **Boundary:** {record['boundary']}",
            f"- **Next / revisit condition:** {record['next_action']}",
            f"- **Related explorations:** {related}",
            f"- **Formal authorities:** {', '.join(formal_links) or '-'}",
            "- **Located evidence:** " + "; ".join(
                exploration_evidence_link(value) for value in record["evidence_refs"]
            ),
            "",
        ]

    lines += [
        "",
        "## Claim evidence matrix",
        "",
        "Each row links current state, accepted evidence, retired routes, open gates,",
        "and the latest accepted change. Counts and associations are derived from the",
        "canonical registries; a dash means no unambiguous registry link, not proof absence.",
        "",
    ]
    for sector in SECTOR_ORDER:
        sector_cards = [card for card in cards if card.get("sector") == sector]
        if not sector_cards:
            continue
        lines += [
            f"### Sector {sector}",
            "",
            "| Claim | State | Evidence grade | Proof trail | Accepted reusable results | Negative/audit history | Explorations | Current route gates | Latest accepted step | Reproduce |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for card in sector_cards:
            links = card["evidence_links"]
            latest_id = str(links.get("latest_event_id", ""))
            latest = event_by_id.get(latest_id, {})
            latest_text = clip(latest.get("header", "-"), 85)
            gates = links.get("route_gate_ids", [])
            gate_text = ", ".join(gate_link(str(value)) for value in gates) or "-"
            reproduction = card.get("reproduction", {})
            inventory = card["evidence_inventory"]
            trail = (
                f"[LINEAGE](../claims/{card['id']}/LINEAGE.md) "
                f"({len(inventory['proof_notes'])} notes; {len(inventory['run_json'])} runs)"
            )
            reproduce = (
                f"[{collapse(reproduction.get('status', 'AVAILABLE')) or 'AVAILABLE'}]"
                f"(../claims/{card['id']}/status.json)"
                if reproduction.get("command")
                else "-"
            )
            lines.append(
                f"| {claim_link(str(card['id']), pipe(card['id']))}<br/>{pipe(card['title'])} | "
                f"{pipe(card['tier'])} / {pipe(card['lifecycle'])} | "
                f"{pipe(', '.join(card['evidence_grade']) or '-')} | "
                f"{trail} | "
                f"{compact_links(links.get('result_ids', []), 'result')} | "
                f"{compact_links(links.get('negative_tags', []), 'negative')} | "
                f"{compact_links(links.get('exploration_ids', []), 'exploration')} | "
                f"{gate_text} | {pipe(latest_text)} | {reproduce} |"
            )
        lines.append("")

    lines += [
        "## Accepted reusable-result record",
        "",
        "`R-NNN` means accepted and reusable; it does not imply a positive theorem. Some",
        "entries are no-go lemmas, partial reductions, or conditional consolidations.",
        "",
        "| Result | Host claim(s) / same-event route history | Core verified content | Honest boundary |",
        "|---|---|---|---|",
    ]
    for result in results:
        normalized = result.get("normalized_detail", {})
        boundary = normalized.get("boundary", "") or "See the detailed result record."
        hosts = ", ".join(claim_link(value) for value in result.get("claim_refs", []))
        paired = compact_links(result.get("co_recorded_negative_tags", []), "negative", maximum=4)
        route_history = hosts or "-"
        if paired != "-":
            route_history += f"; same event: {paired}"
        lines.append(
            f"| [{result['id']}](../RESULTS-LEDGER.md#{result['anchor']}) "
            f"{pipe(result['title'])} | {route_history} | "
            f"{pipe_full(result['summary'])} | {pipe_full(boundary)} |"
        )

    lines += [
        "",
        "## Negative, retracted, and audit history",
        "",
        "| Tag | Kind | Route / claim | Why it failed | Consequence |",
        "|---|---|---|---|---|",
    ]
    for record in negatives:
        detail = record.get("detail", {})
        reason = detail.get("failure_mode") or record.get("summary", "")
        consequence = detail.get("consequence", "See the detailed registry entry.")
        lines.append(
            f"| [{record['tag']}](../negative-results/registry.md#{record['anchor']}) | "
            f"{pipe(record['kind'])} | "
            f"{pipe(record['branch'] or record.get('detail_title', ''))} | "
            f"{pipe_full(reason)} | {pipe_full(consequence)} |"
        )

    lines += [
        "",
        "### Legacy process-grade lessons",
        "",
        "These unnumbered governance lessons are projected verbatim-by-summary so they are",
        "not lost merely because they predate the indexed negative-record schema.",
        "",
    ]
    lines.extend(f"- {lesson}" for lesson in process_grade_lessons)

    lines += [
        "",
        "## Recent accepted chronology",
        "",
        f"The newest {min(RECENT_EVENT_DISPLAY_LIMIT, len(events))} entries are shown here. "
        "All accepted events, including their notes and scripts, are present in "
        "`verification/proof-evidence-map.json`; the append-only authority is `changelog/log.jsonl`.",
        "",
        "| Date | Accepted change | Claims | Negative-result links |",
        "|---|---|---|---|",
    ]
    for event in reversed(events[-RECENT_EVENT_DISPLAY_LIMIT:]):
        claim_values = [
            claim_link(identifier)
            for identifier in event.get("claim_refs", [])
            if identifier in {str(card["id"]) for card in cards}
        ]
        negative_by_tag = {str(record["tag"]): record for record in negatives}
        negative_values = []
        for tag in event.get("negative_results", []):
            if tag in negative_by_tag:
                negative_values.append(
                    f"[{tag}](../negative-results/registry.md#{negative_by_tag[tag]['anchor']})"
                )
            else:
                negative_values.append(f"`{tag}` (historical/unindexed)")
        lines.append(
            f"| {pipe(event.get('date', ''))} | {pipe(event.get('header', ''))} | "
            f"{', '.join(claim_values) or '-'} | {', '.join(negative_values) or '-'} |"
        )

    lines += [
        "",
        "## Coverage and maintenance contract",
        "",
        "| Canonical source | What this map projects |",
        "|---|---|",
        "| `claims/*/status.json` | Current statement, scope, tier, lifecycle, dependencies, evidence grade, falsifier, gate, next action, and reproduction command |",
        "| `RESULTS-LEDGER.md` | Every indexed reusable success and its detailed proof/boundary fields |",
        "| `negative-results/registry.md` | Every indexed failed/retracted/audit route and its failure/evidence/consequence fields |",
        "| `explorations/log.jsonl` | Every append-only proof-route question, finite check, verdict, boundary, next/revisit condition, and structured formal link |",
        "| `changelog/log.jsonl` | Every accepted chronological event, note, script, claim, and negative-result link |",
        "| `todo/todo.json` | Live route order, ownership, blockers, and completed-work coverage |",
        "| `claims/GATES.md` | Definitions and registered status of every claim-card or live-task current route gate |",
        "",
        "The generator fails on duplicate IDs, missing result/negative detail or index entries,",
        "unknown task claims, undefined live-task/current route gates, rewritten or",
        "unresolved exploration entries, post-policy footer omissions, malformed JSON,",
        "unresolved graph edges, or stale output.",
        "It writes both outputs atomically and is part of `regen_all.py`, `doctor.py`, and",
        "`release_check.py` through the shared gate list.",
        "",
        "```bash",
        "python verification/scripts/build_proof_evidence_map.py",
        "python verification/scripts/build_proof_evidence_map.py --check",
        "python verification/scripts/build_proof_evidence_map.py --self-test",
        "python verification/scripts/exploration.py verify",
        "```",
        "",
        "For token-efficient research, search this map by claim, result, exploration, failure tag, or gate",
        "instead of loading it in full; open only the linked canonical records needed for the task.",
        "",
    ]
    return "\n".join(lines)


def self_test() -> None:
    fixture = """### R-001 -- fixture result

**Statement.** Exact fixture.

**Boundary.** No promotion.
"""
    parsed = parse_sections(fixture, r"R-\d+")
    assert parsed["R-001"]["title"] == "fixture result"
    assert parsed["R-001"]["fields"]["statement"] == "Exact fixture."
    assert parsed["R-001"]["fields"]["boundary"] == "No promotion."
    assert markdown_anchor("A13-CLASSII-GATE") == "a13-classii-gate"
    assert normalize_status("BLOCKED") == "blocked"
    assert pipe("a|b") == "a\\|b"


def build_outputs() -> tuple[str, str, dict[str, object]]:
    data = build_data()
    markdown = render_markdown(data)
    machine = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    return markdown, machine, data


def stale_targets(outputs: dict[Path, str]) -> list[Path]:
    return [
        path
        for path, expected in outputs.items()
        if not path.exists() or path.read_text(encoding="utf-8") != expected
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    self_test()
    if args.self_test:
        print("PROOF-EVIDENCE-MAP SELF-TEST: PASS")
        return 0

    try:
        markdown, machine, data = build_outputs()
    except Exception as error:
        print(f"PROOF-EVIDENCE-MAP: FAIL: {error}")
        return 1

    outputs = {OUT_MD: markdown, OUT_JSON: machine}
    if args.check:
        stale = stale_targets(outputs)
        if stale:
            print(f"PROOF-EVIDENCE-MAP CHECK: FAIL ({len(stale)} stale)")
            for path in stale:
                print(f"  stale: {path.relative_to(REPO).as_posix()}")
            print("  fix: python verification/scripts/build_proof_evidence_map.py")
            return 1
        coverage = data["coverage"]
        print(
            "PROOF-EVIDENCE-MAP CHECK: PASS "
            f"({coverage['status_cards']} status cards; "
            f"{coverage['reusable_results']} results; "
            f"{coverage['negative_records']} negative records; "
            f"{coverage['proof_explorations']} explorations; "
            f"{coverage['accepted_events']} events; "
            f"{coverage['tasks']} tasks)"
        )
        return 0

    for path, text in outputs.items():
        atomic_write(path, text)
    coverage = data["coverage"]
    print(
        "PROOF-EVIDENCE-MAP: wrote theory/proof-evidence-map.md + "
        "verification/proof-evidence-map.json "
        f"({coverage['status_cards']} status cards; "
        f"{coverage['reusable_results']} results; "
        f"{coverage['negative_records']} negative records; "
        f"{coverage['proof_explorations']} explorations; "
        f"{coverage['accepted_events']} events; "
        f"{coverage['tasks']} tasks)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
