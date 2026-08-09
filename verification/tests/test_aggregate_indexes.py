import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "verification" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_proof_evidence_map import (  # noqa: E402
    parse_gate_definitions,
    parse_negatives,
    parse_results,
)
from lint_claims import load_registry  # noqa: E402


def canonical(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def json_file(relative: str):
    return json.loads((REPO / relative).read_text(encoding="utf-8"))


def test_frozen_compatibility_volumes():
    expected = {
        "CHANGELOG.md": "500be22d8db17f9bf25b6f312ca3b300d5eab0e04f03c72dfe269d85e1b55970",
        "CATALOG.md": "121625b81a42e3650eb46327bee84f0dfd9ed821f7d71ecc85077c606ea97d47",
        "verification/catalog.json": "5e09e38b81b8ea34b3349c423a626cc9ae6d8e062134a2e14c8c6d41104c91bc",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256(canonical(REPO / relative)).hexdigest() == digest


def test_changelog_locator_and_body_coverage():
    records = [json.loads(line) for line in
               (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()
               if line.strip()]
    index = json_file("changelog/index.json")
    assert index["schema"] == "tect/changelog-index/2.0"
    assert index["total"] == len(records)

    locator_rows = []
    for descriptor in index["locators"]:
        path = REPO / descriptor["path"]
        data = path.read_bytes()
        assert len(data) == descriptor["bytes"]
        assert hashlib.sha256(data).hexdigest() == descriptor["sha256"]
        payload = json.loads(data.decode("utf-8"))
        assert payload["count"] == len(payload["entries"]) == descriptor["count"]
        locator_rows.extend(payload["entries"])
    assert [row["id"] for row in locator_rows] == [row["id"] for row in records]
    assert len({row["id"] for row in locator_rows}) == len(records)

    page_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((REPO / "changelog/pages").glob("*.md"))
    )
    cutover = index["cutover"]["records"]
    for ordinal, record in enumerate(records, start=1):
        anchor = f'<a id="{record["id"]}"></a>'
        assert page_text.count(anchor) == (0 if ordinal <= cutover else 1)

    correction = next(
        row for row in records
        if row["id"].startswith("20260810-correction-aggregate-index-cutover")
    )
    assert correction["id"].startswith("20260810-correction-aggregate-index-cutover")
    assert "\\n" not in correction["raw"]
    assert "Corrects:" in correction["raw"]
    assert "20260810-aggregate-index-cutover-bounded-changelog-and-c" in correction["raw"]


def test_catalog_manifest_shards_and_live_claims():
    manifest = json_file("verification/catalog/index.json")
    summary = json_file("verification/catalog-summary.json")
    assert manifest["schema"] == "tect/catalog-manifest/2.0"
    rows = []
    for descriptor in manifest["shards"]:
        path = REPO / descriptor["path"]
        data = path.read_bytes()
        assert len(data) == descriptor["bytes"]
        assert hashlib.sha256(data).hexdigest() == descriptor["sha256"]
        payload = json.loads(data.decode("utf-8"))
        assert payload["kind"] == descriptor["kind"]
        assert payload["count"] == len(payload["entries"]) == descriptor["count"]
        rows.extend(payload["entries"])
    assert len(rows) == manifest["total"] == summary["total"]
    paths = [row["path"] for row in rows]
    assert len(paths) == len(set(paths))
    assert summary["claim_count"] == len(summary["claim_status_paths"]) == 49
    assert all(re.fullmatch(r"claims/(?!_)[^/]+/status\.json", path)
               for path in summary["claim_status_paths"])


def test_generated_aggregate_size_budgets():
    assert (REPO / "changelog/INDEX.md").stat().st_size <= 128 * 1024
    assert (REPO / "changelog/index.json").stat().st_size <= 128 * 1024
    assert all(path.stat().st_size <= 128 * 1024
               for path in (REPO / "changelog/locators").glob("*.json"))
    assert all(path.stat().st_size <= 256 * 1024
               for path in (REPO / "changelog/pages").glob("*.md"))
    assert (REPO / "catalog/INDEX.md").stat().st_size <= 128 * 1024
    assert (REPO / "verification/catalog-summary.json").stat().st_size <= 128 * 1024
    assert (REPO / "verification/catalog/index.json").stat().st_size <= 128 * 1024
    assert all(path.stat().st_size <= 512 * 1024
               for path in (REPO / "verification/catalog/kinds").glob("*.json"))
    for relative in (
        "management/INDEX.md", "results/INDEX.md", "results/index.json",
        "negative-results/INDEX.md", "negative-results/index.json",
        "claims/GATES-INDEX.md", "claims/gates-index.json",
        "theory/proof-evidence/INDEX.md",
    ):
        assert (REPO / relative).stat().st_size <= 128 * 1024


def test_management_locator_coverage():
    expected = {
        "results/index.json": ("tect/results-index/1.0", "RESULTS-LEDGER.md"),
        "negative-results/index.json": (
            "tect/negative-index/1.0", "negative-results/registry.md"
        ),
        "claims/gates-index.json": ("tect/gate-index/1.0", "claims/GATES.md"),
    }
    for relative, (schema, authority) in expected.items():
        payload = json_file(relative)
        entries = payload["entries"]
        assert payload["schema"] == schema
        assert payload["count"] == len(entries)
        assert len({row["id"] for row in entries}) == len(entries)
        assert (REPO / authority).exists()

    assert json_file("results/index.json")["count"] == len(parse_results())
    assert json_file("negative-results/index.json")["count"] == len(parse_negatives())
    assert json_file("claims/gates-index.json")["count"] == len(parse_gate_definitions())


def test_gate_registry_accepts_only_heading_definitions():
    registry = load_registry()
    assert registry == set(parse_gate_definitions())
    assert not {"OPEN", "T4", "CLOSED-CONDITIONAL"} & registry


def test_website_uses_compact_current_surfaces():
    source = (REPO / "publish/website/app.js").read_text(encoding="utf-8")
    assert 'fetchJSON("verification/catalog-summary.json")' in source
    assert 'fetchJSON("verification/catalog/index.json")' in source
    assert 'mdPage("Changelog", "changelog/INDEX.md")' in source
    assert 'mdPage("Current research management", "management/INDEX.md")' in source
    assert 'mdPage("Gate & hypothesis index", "claims/GATES-INDEX.md")' in source
    assert 'mdPage("Reusable results index", "results/INDEX.md")' in source
    assert 'mdPage("Proof-evidence entry", "theory/proof-evidence/INDEX.md")' in source
    legacy_catalog_fetch = 'fetchJSON("verification/catalog' + '.json")'
    assert legacy_catalog_fetch not in source
    assert "Top priority: STEP-5B" not in source
    assert "esc(c.statement)" in source
    assert "esc(c.falsifier)" in source
    assert "rewriteRepoLinks" in source
    assert "SLUG_RE" in source
