#!/usr/bin/env python3
"""Replay the Q3LOCK draft diagnostics without rewriting historical results.

Default: compare a fresh in-memory replay with the saved tooling checkpoint.
--write-new publishes a separate result atomically and refuses any existing
destination. No proof, source PDF, release, claim promotion or external review
is supplied by this command. Assertion-enabled Python is required.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import runpy
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PAPER = "publish/papers/q3lock-phase-coexistence/"
RUNS = "claims/C6-SPACETIME-SIGNATURE/runs/"
SOURCE = "verification/scripts/q3lock_manuscript_source_audit.py"
HISTORICAL = RUNS + "2026-09-07-q3lock-manuscript-source-audit/result.json"
QPS = RUNS + "2026-09-07-q3lock-literature-qps-addendum/result.json"
DFFR = RUNS + "2026-09-07-q3lock-dffr-source-audit/result.json"
R1 = RUNS + "2026-09-07-q3lock-paper-readonly-replay/result.json"
R1_SOURCES = str(Path(R1).parent / "source-map.json").replace("\\", "/")
CANONICAL = tuple("verification/scripts/q3lock_" + name + "_audit.py" for name in (
    "absolute_partition", "thermodynamic_pressure", "dlr_tangent_content",
    "fkg_content", "reflection_infrared_content",
    "collective_falk_bruch_content", "strict_cusp_tangent_content"))
DOCUMENTS = frozenset(PAPER + name for name in (
    "README.md", "external-review-handoff.md", "literature-qps-addendum.md",
    "verification/README.md", "verification/package-manifest.json",
    "verification/replay-safety-audit.md"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def default_output():
    """Resolve the current checkpoint from the package, confined to public runs."""
    manifest = json.loads((ROOT / (PAPER + "verification/package-manifest.json"))
                          .read_text(encoding="utf-8"))
    relative = manifest["tooling_checkpoint"]
    if (not isinstance(relative, str) or "\\" in relative or ":" in relative
            or Path(relative).is_absolute() or ".." in Path(relative).parts):
        raise ValueError("Invalid tooling checkpoint path.")
    target = (ROOT / relative).resolve()
    if not target.is_relative_to((ROOT / RUNS).resolve()) or target.suffix != ".json":
        raise ValueError("Tooling checkpoint must be a JSON file under public claim runs.")
    return target


def preserved_r1_sources():
    """Validate raw R1 source copies against the unmodified R1 result hashes."""
    record = json.loads((ROOT / R1).read_text(encoding="utf-8"))
    mapping = json.loads((ROOT / R1_SOURCES).read_text(encoding="utf-8"))
    if mapping["checkpoint"] != R1:
        raise ValueError("R1 source map points to a different checkpoint.")
    archive_root = (ROOT / R1).parent.resolve()
    seen, hashes = set(), {R1_SOURCES: digest(ROOT / R1_SOURCES)}
    for row in mapping["files"]:
        source, archive = row["source"], row["archive"]
        archived = (ROOT / archive).resolve()
        if source in seen or not archived.is_relative_to(archive_root):
            raise ValueError("Duplicate or escaping R1 source archive.")
        expected = record["source_hashes"][source]
        if row["sha256"] != expected or digest(archived) != expected:
            raise ValueError("R1 source archive differs from original bytes: " + source)
        seen.add(source)
        hashes[archived.relative_to(ROOT).as_posix()] = expected
    if not seen:
        raise ValueError("Empty R1 source preservation map.")
    return hashes


def payload_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True).encode("utf-8")).hexdigest()


def differences(old, new, path=""):
    if isinstance(old, dict) and isinstance(new, dict):
        rows = []
        for key in sorted(old.keys() | new.keys()):
            location = path + "/" + key
            if key not in old or key not in new:
                rows.append({"path": location, "old": old.get(key),
                             "new": new.get(key), "key_set_changed": True})
            else:
                rows.extend(differences(old[key], new[key], location))
        return rows
    return [] if old == new else [{"path": path, "old": old, "new": new}]


def require_document_only(old, new, allowed_hashes):
    rows = differences(old, new)
    for row in rows:
        _, separator, source = row["path"].rpartition("/source_hashes/")
        if (not separator or source not in allowed_hashes
                or row["new"] != allowed_hashes[source]):
            raise ValueError("Non-document or unexplained replay difference: " + row["path"])
    return rows


def require_draft_scope(manifest):
    expected = {"result_id": "R-497", "tier": "T0", "claim_bearing": False,
                "publication_status": "RESEARCH_ONLY"}
    if (manifest["claim_status"] != expected
            or manifest["status"] != "UNFROZEN_CONTENT_REVIEW"
            or manifest["pdf_status"] != "DEFERRED"):
        raise ValueError("Draft scope changed; this tooling checkpoint cannot accept it.")


def guard_self_tests():
    # Tooling fixtures only; these strings are not scientific/source hashes.
    rows = []
    old = {"assertions": [{"pass": True}], "source_hashes": {"document": "old", "code": "same"}}
    new = {"assertions": [{"pass": True}], "source_hashes": {"document": "new", "code": "same"}}
    accepted = require_document_only(old, new, {"document": "new"})
    assert len(accepted) == 1
    rows.append({"name": "explicit-document-hash-change", "pass": True})
    added = require_document_only({"source_hashes": {}},
                                  {"source_hashes": {"document": "new"}},
                                  {"document": "new"})
    assert len(added) == 1 and added[0]["key_set_changed"]
    rows.append({"name": "explicit-new-document-hash", "pass": True})
    for name, mutant, allowed in (
        ("changed-assertion", {**new, "assertions": [{"pass": False}]}, {"document": "new"}),
        ("unlisted-source", {**new, "source_hashes": {"document": "new", "code": "other"}},
         {"document": "new"}),
        ("wrong-document-hash", new, {"document": "different"}),
        ("added-null-key", {**new, "unexpected": None}, {"document": "new"}),
    ):
        try:
            require_document_only(old, mutant, allowed)
        except ValueError:
            rows.append({"name": name, "pass": True})
        else:
            raise AssertionError("Hostile tooling fixture accepted: " + name)
    return rows


def build_payload():
    if not __debug__:
        raise ValueError("Use assertion-enabled Python, without -O or PYTHONOPTIMIZE.")
    manifest = json.loads((ROOT / (PAPER + "verification/package-manifest.json")).read_text())
    require_draft_scope(manifest)
    archived_hashes = preserved_r1_sources()
    dffr = json.loads((ROOT / DFFR).read_text())
    qps = json.loads((ROOT / QPS).read_text())
    if digest(ROOT / QPS) != dffr["historical_snapshot_sha256"]:
        raise ValueError("Historical QPS snapshot changed.")
    if digest(ROOT / HISTORICAL) != qps["historical_run_sha256"]:
        raise ValueError("Historical manuscript source snapshot changed.")
    # Check the preserved code, notes and results before executing old builders.
    for source, expected in dffr["source_hashes"].items():
        if source not in DOCUMENTS and digest(ROOT / source) != expected:
            raise ValueError("Protected source changed: " + source)
    frozen = ROOT / "strategy/q3lock-exp782-independent-result-manifest-260905.json"
    for row in json.loads(frozen.read_text())["source_files"]:
        if digest(ROOT / row["path"]) != row["sha256"]:
            raise ValueError("Frozen authority changed: " + row["path"])

    historical_paths = {ROOT / path for path in (HISTORICAL, QPS, DFFR, R1)}
    historical_paths.update(ROOT / (RUNS + "2026-09-06-q3lock-manuscript-" +
                                   part + "-audit/result.json")
                            for part in ("content", "loop", "dlr", "infrared",
                                         "collective", "composition"))
    modules = [(path, runpy.run_path(str(ROOT / path), run_name="q3lock_readonly"))
               for path in CANONICAL]
    historical_paths.update(module["OUT"] for _, module in modules)
    before = {path: path.read_bytes() for path in historical_paths}
    current = runpy.run_path(str(ROOT / SOURCE), run_name="q3lock_source_readonly")["build_payload"]()
    allowed_hashes = {path: digest(ROOT / path) for path in DOCUMENTS}
    changes = require_document_only(json.loads(before[ROOT / HISTORICAL]), current, allowed_hashes)
    canonical_replay = []
    for script, module in modules:
        replay = module["build_payload"]()
        if replay != json.loads(before[module["OUT"]]):
            raise ValueError("Canonical result differs from its saved checkpoint: " + script)
        canonical_replay.append({"script": script, "status": "PASS",
                                 "assertions_passed": replay["assertions_passed"],
                                 "payload_sha256": payload_digest(replay)})
    for path, original in before.items():
        if path.read_bytes() != original:
            raise ValueError("Historical output bytes changed: " + str(path))

    hashes, groups = {}, {}

    def collect(node):
        if not isinstance(node, dict):
            return
        if "schema" in node and "assertions_passed" in node:
            group = {key: node[key] for key in ("schema", "status", "assertions_passed")}
            if node["schema"] in groups and groups[node["schema"]] != group:
                raise ValueError("Inconsistent duplicate diagnostic group.")
            groups[node["schema"]] = group
        for source, value in node.get("source_hashes", {}).items():
            if digest(ROOT / source) != value or source in hashes and hashes[source] != value:
                raise ValueError("Inconsistent source hash: " + source)
            hashes[source] = value
        for key, value in node.items():
            if key != "source_hashes":
                collect(value)

    collect(current)
    extra = (Path(__file__).resolve(), frozen,
             ROOT / "verification/tests/test_q3lock_paper_replay.py",
             ROOT / (PAPER + "verification/replay-safety-audit.md"))
    for path in (*extra, *historical_paths, *(ROOT / source for source in CANONICAL)):
        hashes[path.relative_to(ROOT).as_posix()] = digest(path)
    if preserved_r1_sources() != archived_hashes:
        raise ValueError("R1 source archive changed during replay.")
    hashes.update(archived_hashes)
    guards = guard_self_tests()
    return {
        "schema": "tect/q3lock-paper-readonly-replay/1.0",
        "status": "PASS", "claim_bearing": False,
        "manuscript_version": manifest["version"], "pdf_status": manifest["pdf_status"],
        "canonical_replay": canonical_replay,
        "manuscript_replay": list(groups.values()),
        "manuscript_payload_sha256": payload_digest(current),
        "documentation_changes_from_source_checkpoint": changes,
        "historical_records_preserved": len(before),
        "guard_assertions": guards, "guard_assertions_passed": len(guards),
        "source_hashes": dict(sorted(hashes.items())),
        "scope": "Existing finite diagnostics and provenance only; no new phase proof, independent analytic acceptance, literature opinion or final freeze."
    }


def write_new(path, payload):
    """Publish complete JSON with an atomic, no-replace hard link on one volume."""
    if os.path.lexists(path):
        raise FileExistsError("Refusing to overwrite existing result: " + str(path))
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        # Unlike replace(), link() fails if a concurrent publisher won the name.
        os.link(temporary, path)
    finally:
        os.unlink(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only check (default)")
    mode.add_argument("--write-new", action="store_true", help="create a separate, absent output")
    mode.add_argument("--self-test", action="store_true", help="run pure tooling guard fixtures only")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        if not __debug__:
            raise ValueError("Use assertion-enabled Python, without -O or PYTHONOPTIMIZE.")
        if args.self_test:
            print("GUARD SELF-TEST: PASS", len(guard_self_tests()))
            return 0
        output = args.output if args.output is not None else default_output()
        if args.write_new and os.path.lexists(output):
            raise FileExistsError("Refusing to overwrite existing result: " + str(output))
        saved = None if args.write_new else output.read_bytes()
        payload = build_payload()
        if args.write_new:
            write_new(output, payload)
        elif json.loads(saved) != payload:
            raise ValueError("Saved replay differs; investigate and register a separate checkpoint.")
        elif output.read_bytes() != saved:
            raise ValueError("Saved replay changed during the read-only check.")
        print("Q3LOCK PAPER REPLAY: PASS; canonical groups",
              len(payload["canonical_replay"]), "; manuscript groups",
              len(payload["manuscript_replay"]), "; historical records preserved",
              payload["historical_records_preserved"])
        return 0
    except ImportError as error:
        print("Q3LOCK PAPER REPLAY: FAIL: missing research dependency:", error,
              "- use the documented repository Python environment.", file=sys.stderr)
        return 1
    except (OSError, ValueError, AssertionError, KeyError, TypeError) as error:
        print("Q3LOCK PAPER REPLAY: FAIL:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
