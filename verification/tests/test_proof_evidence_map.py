"""Coverage and staleness tests for the generated global proof evidence map."""

import importlib.util
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "verification" / "scripts" / "build_proof_evidence_map.py"
MAP_JSON = REPO / "verification" / "proof-evidence-map.json"
MAP_MARKDOWN = REPO / "theory" / "proof-evidence-map.md"
MAP_IO = REPO / "verification" / "scripts" / "proof_evidence_map_io.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_machine_map():
    module = load_module(MAP_IO, "proof_evidence_map_io_test")
    return module.load_map(REPO)


def test_proof_evidence_map_in_sync():
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--check"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_machine_map_has_complete_unique_coverage():
    data = load_machine_map()
    coverage = data["coverage"]
    assert coverage["status_cards"] == len(data["claims"])
    assert coverage["reusable_results"] == len(data["reusable_results"])
    assert coverage["negative_records"] == len(data["negative_records"])
    assert coverage["proof_explorations"] == len(data["proof_explorations"])
    assert coverage["process_grade_lessons"] == len(data["process_grade_lessons"])
    assert coverage["accepted_events"] == len(data["accepted_events"])
    assert coverage["tasks"] == len(data["all_tasks"])
    assert all(not claim["id"].startswith("_") for claim in data["claims"])
    assert coverage["unordered_root_notes"] == sum(
        len(claim["evidence_inventory"]["unordered_root_notes"])
        for claim in data["claims"]
    )

    for records, key in (
        (data["claims"], "id"),
        (data["reusable_results"], "id"),
        (data["negative_records"], "tag"),
        (data["proof_explorations"], "id"),
        (data["accepted_events"], "id"),
        (data["all_tasks"], "id"),
    ):
        identifiers = [record[key] for record in records]
        assert len(identifiers) == len(set(identifiers))

    for record in data["negative_records"]:
        assert record["detail"]["failure_mode"]
        assert record["detail"]["evidence"]
        assert record["detail"]["consequence"]
    assert sum(coverage["exploration_verdicts"].values()) == len(
        data["proof_explorations"]
    )
    for record in data["proof_explorations"]:
        assert record["question"]
        assert record["method"]
        assert record["finding"]
        assert record["decision_reason"]
        assert record["boundary"]
        assert record["next_action"]
        for reference in record["evidence_refs"]:
            assert (REPO / reference.split("#", 1)[0]).is_file()


def test_machine_map_index_and_shards_are_small_and_lossless():
    index = json.loads(MAP_JSON.read_text(encoding="utf-8"))
    assert index["schema"] == "tect/proof-evidence-map-index/1.0"
    assert index["shard_count"] == len(index["shards"])
    assert MAP_JSON.stat().st_size < 1_000_000
    shard_sizes = []
    for entry in index["shards"]:
        path = REPO / entry["path"]
        assert path.is_file()
        assert path.stat().st_size == entry["bytes"]
        shard_sizes.append(path.stat().st_size)
    assert shard_sizes
    assert max(shard_sizes) < 5_000_000
    data = load_machine_map()
    assert index["coverage"]["proof_explorations"] == len(data["proof_explorations"])


def test_graph_edges_and_authority_paths_resolve():
    data = load_machine_map()
    node_ids = {node["id"] for node in data["graph"]["nodes"]}
    for node in data["graph"]["nodes"]:
        authority = node["authority"].split("#", 1)[0]
        assert (REPO / authority).exists()
    for edge in data["graph"]["edges"]:
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids

    node_by_id = {node["id"]: node for node in data["graph"]["nodes"]}
    for task in data["live_tasks"]:
        gate = task.get("gate")
        if gate:
            assert node_by_id[f"gate:{gate}"]["kind"] != "historical_gate_reference"
    for reference in data["coverage_diagnostics"]["historical_task_gate_references"]:
        node = node_by_id[f"gate:{reference['gate']}"]
        assert node["kind"] == "historical_gate_reference"
        assert node["authority"] == "todo/todo.json"

    for claim in data["claims"]:
        for key in ("claim", "status", "lineage"):
            assert (REPO / claim["paths"][key]).exists()
        for key in (
            "proof_notes",
            "proof_pdfs",
            "unordered_root_notes",
            "unordered_root_pdfs",
            "run_json",
            "manifests",
            "bundle_manifests",
            "bundle_embedded_manifests",
        ):
            paths = claim["evidence_inventory"][key]
            assert all((REPO / path).exists() for path in paths)
        inventory = claim["evidence_inventory"]
        manifest_classes = [
            set(inventory[key])
            for key in ("manifests", "bundle_manifests", "bundle_embedded_manifests")
        ]
        assert not (manifest_classes[0] & manifest_classes[1])
        assert not (manifest_classes[0] & manifest_classes[2])
        assert not (manifest_classes[1] & manifest_classes[2])


def test_markdown_local_link_targets_resolve():
    text = MAP_MARKDOWN.read_text(encoding="utf-8")
    destinations = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
    assert destinations
    missing = []
    for destination in destinations:
        target, _, fragment = unquote(destination).partition("#")
        if not target or "://" in target:
            continue
        if not destination.startswith(("../", "sectors/", "#")):
            continue
        target_path = (MAP_MARKDOWN.parent / target).resolve()
        if not target_path.exists():
            missing.append(destination)
        elif fragment:
            assert fragment.lower() in target_path.read_text(
                encoding="utf-8", errors="replace"
            ).lower()
    assert not missing


def test_associations_use_canonical_structured_sources_only():
    data = load_machine_map()
    known = {claim["id"] for claim in data["claims"]}
    for event in data["accepted_events"]:
        assert set(event["claim_refs"]) <= set(event["claim_ids"])
        assert set(event["claim_refs"]) <= known

    results = {record["id"]: record for record in data["reusable_results"]}
    negatives = {record["tag"]: record for record in data["negative_records"]}
    unbound_results = {
        identifier for identifier, record in results.items() if not record["claim_refs"]
    }
    assert unbound_results == set(
        data["coverage_diagnostics"]["claim_unbound_result_ids"]
    )
    unbound_negatives = {
        tag for tag, record in negatives.items() if not record["claim_refs"]
    }
    assert unbound_negatives == set(
        data["coverage_diagnostics"]["claim_unbound_negative_tags"]
    )
    assert "AUDIT-2026-07-24-PROOF-MAP-SEMANTIC-ASSOCIATION" in unbound_negatives
    assert results["R-038"]["claim_refs"] == ["B5-BEYOND-LAYER-BOUND"]
    assert (
        "NG-2026-07-23-A13-ABSOLUTE-SCORE-AND-FULL-REMAINDER"
        in results["R-068"]["co_recorded_negative_tags"]
    )
    assert set(results["R-068"]["co_recorded_negative_tags"]) <= set(negatives)
    assert negatives["AUDIT-2026-07-17-A3-GALERKIN-BALL-UNDERBOUND"][
        "claim_refs"
    ] == ["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]
    a13_id = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
    assert negatives[
        "NG-2026-07-31-A13-ELLIPTIC-GAUSSIAN-D4-FLOOR-UNIFORMITY"
    ]["claim_refs"] == [a13_id]
    assert negatives[
        "NG-2026-07-31-A13-POINTWISE-ELLIPTICITY-SPATIAL-FRACTIONAL-TRANSFER"
    ]["claim_refs"] == [a13_id]

    for record in list(results.values()) + list(negatives.values()):
        fields = json.dumps(record.get("detail", {}), ensure_ascii=False)
        assert "<a id=" not in fields
        assert "## Process-grade" not in fields

    exploration_claim_edges = {
        (edge["from"].split(":", 1)[1], edge["to"].split(":", 1)[1])
        for edge in data["graph"]["edges"]
        if edge["from"].startswith("exploration:")
        and edge["relation"] == "assesses"
    }
    assert exploration_claim_edges == {
        (record["id"], claim)
        for record in data["proof_explorations"]
        for claim in record["claim_ids"]
    }
    assert all(
        edge["basis"].startswith("structured_")
        for edge in data["graph"]["edges"]
        if edge["from"].startswith("exploration:")
    )


def test_current_child_gate_and_honest_a13_boundary_are_visible():
    data = load_machine_map()
    a13 = next(
        claim
        for claim in data["claims"]
        if claim["id"] == "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
    )
    assert set(a13["evidence_links"]["route_gate_ids"]) == {
        "A13-CLASSII-CONTROLLED-SHELL-ENERGY-ONE-USE",
        "A13-CLASSII-FULL-PROGRESSIVE-REVISIT-EXTENSION",
    }
    gate_ids = {gate["id"] for gate in data["open_gate_index"]}
    assert set(a13["evidence_links"]["route_gate_ids"]) <= gate_ids
    text = MAP_MARKDOWN.read_text(encoding="utf-8")
    assert "controlled-shell one-use, Nelson theorem, and interacting measure remain open" in text
    assert "## Negative, retracted, and audit history" in text


def test_stale_targets_detect_each_output_independently(tmp_path):
    module = load_module(BUILDER, "proof_evidence_map_builder")
    markdown = tmp_path / "map.md"
    machine = tmp_path / "map.json"
    markdown.write_text("current", encoding="utf-8")
    outputs = {markdown: "current", machine: "{}\n"}
    assert module.stale_targets(outputs) == [machine]
    machine.write_text("stale", encoding="utf-8")
    assert module.stale_targets(outputs) == [machine]
    machine.write_text("{}\n", encoding="utf-8")
    assert module.stale_targets(outputs) == []


def test_footer_enforcement_cannot_be_bypassed_by_omitting_version_metadata(tmp_path):
    module = load_module(BUILDER, "proof_evidence_map_footer_builder")
    module.REPO = tmp_path
    legacy = tmp_path / "legacy-note-260723-v1.0.tex.txt"
    current = tmp_path / "current-note-260724-v1.0.tex.txt"
    undated = tmp_path / "undated-note.tex.txt"
    for path in (legacy, current, undated):
        path.write_text("incomplete proof note\n", encoding="utf-8")
    assert set(module.auditable_note_paths(tmp_path)) == {legacy, current, undated}

    legacy_audit = module.audit_note_footer(legacy)
    current_audit = module.audit_note_footer(current)
    undated_audit = module.audit_note_footer(undated)
    assert legacy_audit["first_issued"] == "2026-07-23"
    assert not legacy_audit["enforcement_applies"]
    assert current_audit["first_issued"] == "2026-07-24"
    assert current_audit["enforcement_applies"]
    assert not undated_audit["first_issued"]
    assert undated_audit["enforcement_applies"]


def test_source_hash_normalizes_cross_platform_newlines(tmp_path):
    module = load_module(BUILDER, "proof_evidence_map_hash_builder")
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    lf.write_bytes(b"alpha\nbeta\n")
    crlf.write_bytes(b"alpha\r\nbeta\r\n")
    assert module.sha256(lf) == module.sha256(crlf)


def test_manifest_classification_is_case_stable_and_disjoint(tmp_path):
    module = load_module(BUILDER, "proof_evidence_map_manifest_builder")
    claim_manifest = tmp_path / "proof_MANIFEST.JSON"
    bundle_manifest = tmp_path / "Bundle" / "package" / "MANIFEST.JSON"
    embedded_manifest = tmp_path / "Bundle" / "package" / "copy_manifest.JSON"
    for path in (claim_manifest, bundle_manifest, embedded_manifest):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    classified = module.manifest_paths(tmp_path)
    assert classified == {
        "claim_level": [claim_manifest],
        "bundle_top": [bundle_manifest],
        "bundle_embedded": [embedded_manifest],
    }


def test_shared_gate_wiring_keeps_catalog_last():
    gates = load_module(REPO / "verification" / "scripts" / "gates.py", "tect_gates")
    assert (
        "exploration-integrity",
        ["exploration.py", "verify"],
    ) in gates.SYNC_GATES
    assert (
        "proof-evidence-map",
        ["build_proof_evidence_map.py", "--check"],
    ) in gates.SYNC_GATES
    scripts = [entry[0] for entry in gates.REGEN_ORDER]
    assert "build_proof_evidence_map.py" in scripts
    assert scripts[-1] == "build_catalog.py"
    assert scripts.index("build_proof_evidence_map.py") < scripts.index("build_catalog.py")
    labels = [label for label, _ in gates.SYNC_GATES]
    assert labels.index("exploration-integrity") < labels.index("proof-evidence-map")


def test_exploration_projection_and_historical_boundary_are_visible():
    data = load_machine_map()
    records = data["proof_explorations"]
    assert records
    canonical_records = [
        json.loads(line)
        for line in (REPO / "explorations" / "log.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert records == canonical_records
    canonical_bytes = (REPO / "explorations" / "log.jsonl").read_bytes()
    expected_hash = hashlib.sha256(
        canonical_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()
    assert data["source_hashes"]["explorations/log.jsonl"] == expected_hash
    assert data["coverage_diagnostics"]["exploration_prospective_coverage_from"] == (
        "2026-07-24"
    )
    assert data["coverage_diagnostics"]["historical_backfill_explorations"] == sum(
        record["provenance"] == "historical-backfill" for record in records
    )
    text = MAP_MARKDOWN.read_text(encoding="utf-8")
    for record in records:
        assert text.count(f'<a id="{record["id"].lower()}"></a>') == 1
    a13 = next(
        claim
        for claim in data["claims"]
        if claim["id"] == "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
    )
    assert a13["evidence_links"]["exploration_ids"] == [
        record["id"]
        for record in records
        if a13["id"] in record["claim_ids"]
    ]

    outgoing = {
        record["id"]: {
            (edge["relation"], edge["to"], edge["basis"])
            for edge in data["graph"]["edges"]
            if edge["from"] == f"exploration:{record['id']}"
        }
        for record in records
    }
    for record in records:
        expected = {
            ("assesses", f"claim:{claim}", "structured_claim_id")
            for claim in record["claim_ids"]
        }
        expected |= {
            ("assesses_gate", f"gate:{gate}", "structured_gate_id")
            for gate in record["gate_ids"]
        }
        if record["task_id"]:
            expected.add(
                ("records_task", f"task:{record['task_id']}", "structured_task_id")
            )
        expected |= {
            ("references_result", f"result:{value}", "structured_formal_ref")
            for value in record["formal_refs"]["results"]
        }
        expected |= {
            ("references_negative", f"negative:{value}", "structured_formal_ref")
            for value in record["formal_refs"]["negatives"]
        }
        expected |= {
            ("references_event", f"event:{value}", "structured_formal_ref")
            for value in record["formal_refs"]["events"]
        }
        expected |= {
            (
                relation["relation"],
                f"exploration:{relation['id']}",
                "structured_related_ref",
            )
            for relation in record["related"]
        }
        assert outgoing[record["id"]] == expected

    expected_current_gates = {
        gate
        for claim in data["claims"]
        for gate in claim["open_gates"]
    } | {
        task["gate"] for task in data["live_tasks"] if task.get("gate")
    }
    assert {gate["id"] for gate in data["open_gate_index"]} == expected_current_gates


def test_map_loader_refuses_exploration_integrity_errors(monkeypatch):
    module = load_module(BUILDER, "proof_evidence_map_exploration_loader")
    monkeypatch.setattr(
        module,
        "verify_explorations",
        lambda: ([], ["fixture integrity failure"]),
    )
    try:
        module.load_explorations()
    except ValueError as error:
        assert "fixture integrity failure" in str(error)
    else:
        raise AssertionError("exploration integrity error was silently bypassed")
