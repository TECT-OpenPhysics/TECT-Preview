#!/usr/bin/env python3
"""Verify the sealed Q3LOCK ZIP by actual extraction, replay and hostile tests.

Packaging only: no mathematical or scientific numbers are computed here.
Use --work ABSENT_DIRECTORY and optionally --write-new OUTPUT_JSON. Snapshot
and hostile fixtures are retained, never deleted; output overwrites refused.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "verification/scripts/build_q3lock_submission.py"
CURRENT_LABEL = "2026-09-09-q3lock-submission-locator-audit"


def current_replay():
    """New checkpoint for added evidence locators; no old comparator is changed."""
    old = runpy.run_path(str(ROOT / "verification/scripts/q3lock_manuscript_integrated_replay.py"),
                        run_name="q3_current_interfaces")
    fresh = runpy.run_path(str(ROOT / "verification/scripts/q3lock_fresh_audit_checkpoint.py"),
                          run_name="q3_current_fresh")
    checkpoint = fresh["validate_checkpoint"](CURRENT_LABEL)
    historical = fresh["validate_checkpoint"](old["FRESH_LABEL"])
    # Preserve every historical source byte. Only the two appended-locator
    # Markdown files enlarge the current recursive source inventory.
    old_sources = {x["source"]: x["sha256"] for x in old["read_json"](old["FRESH_SOURCE_MAP"])["files"]}
    _, _, new_map = fresh["checkpoint_paths"](CURRENT_LABEL)
    new_sources = {x["source"]: x["sha256"] for x in old["read_json"](new_map)["files"]}
    assert all(new_sources.get(k) == v for k, v in old_sources.items())
    additions = sorted(set(new_sources) - set(old_sources))
    expected_additions = sorted("publish/papers/q3lock-phase-coexistence/submission-v0138-s1/" + name
                                for name in ("README.md", "internal-review.md"))
    assert additions == expected_additions, additions
    expected = {x["label"]: x for x in checkpoint["audits"]}
    groups = []
    for label, path in old["MANUSCRIPT_AUDITS"]:
        payload = old["run_builder"](path, "current_" + label)
        assert old["payload_digest"](payload) == expected[label]["payload_sha256"], label
        groups.append({"label": label, "assertions_passed": payload["assertions_passed"]})
    canonical = []
    modules = [(path, runpy.run_path(str(ROOT / path), run_name="q3_canonical_current"))
               for path in old["CANONICAL"]]
    protected = {p: p.read_bytes() for p in old["historical_paths"](modules) if p.is_file()}
    for path, module in modules:
        actual = module["build_payload"]()
        old["validate_declared_source_hashes"](actual)
        assert actual == old["read_json"](module["OUT"]), path
        canonical.append({"script": path, "assertions_passed": actual.get("assertions_passed")})
    extra = {}
    for label, path, result, envelope in (
        ("matrix", "verification/scripts/q3lock_independent_review_matrix_audit.py", old["MATRIX_RESULT"], None),
        ("independent", "verification/scripts/q3lock_independent_replay.py", old["INDEPENDENT_RESULT"], "replay"),
        ("finite_form", "verification/scripts/q3lock_finite_form_closure_audit.py", old["FINITE_RESULT"], None),
        ("algebra", "verification/scripts/q3lock_nonimporting_algebra.py", old["ALGEBRA_RESULT"], "replay"),
    ):
        payload = old["run_builder"](path, "current_" + label)
        saved = old["read_json"](result)
        assert payload == (saved[envelope] if envelope else saved), label
        extra[label] = "EXACT_SAVED_PAYLOAD_MATCH"
    assert all(p.read_bytes() == b for p, b in protected.items())
    return {"status": "PASS", "checkpoint": checkpoint["checkpoint"],
            "manuscript_groups": groups, "canonical_groups": canonical, "additional_replays": extra,
            "historical_records_preserved": len(protected), "historical_sources_unchanged": True,
            "source_inventory_additions": additions,
            "historical_default_boundary": "The old source-review-v1 default is a snapshot check. Its complete payload differs only through the recursive inventory's two new Markdown locator files; use this new dated current replay or the unchanged archived replay."}


def main():
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--write-new", type=Path)
    args = parser.parse_args()
    work = args.work.resolve()
    if work.exists():
        raise ValueError("Use an absent scratch directory; snapshots are retained")
    if args.write_new and args.write_new.exists():
        raise ValueError("Existing result output refused")
    m = runpy.run_path(str(BUILDER), run_name="submission_package_audit")
    m["self_test"]()
    m["check"]()
    current = current_replay()
    dest = m["DEST"]
    archive = dest.with_suffix(".zip")
    manifest = json.loads((dest / "MANIFEST.json").read_text(encoding="utf-8"))
    work.mkdir(parents=True)
    snapshot = work / "delivered"
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            m["safe_member"](name)
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(z.read(name))
    integrity = subprocess.run([sys.executable, "verify-package.py"], cwd=snapshot,
                               text=True, capture_output=True)
    assert integrity.returncode == 0, integrity.stdout + integrity.stderr
    checks = m["replay"](snapshot / "research-snapshot")
    for name, expected in manifest["files"].items():
        assert m["file_hash"](snapshot / name) == expected, name
    scientific = m["same_science"](
        (snapshot / "research-snapshot/publish/papers/q3lock-phase-coexistence/manuscript.tex").read_text(encoding="utf-8"),
        (snapshot / "manuscript.tex").read_text(encoding="utf-8"))

    # Synthetic hostile fixtures only. They do not modify the delivered copy.
    cases = {
        "false_external_signature": {"scope": dict(m["SCOPE"], mathematics_review="PASS"), "files": {}},
        "missing_member": {"scope": m["SCOPE"], "files": {"missing.txt": "fixture"}},
        "path_escape": {"scope": m["SCOPE"], "files": {"../escape": "fixture"}},
        "changed_bytes": {"scope": m["SCOPE"], "files": {"changed.txt": hashlib.sha256(b"expected").hexdigest()}},
    }
    verdicts = {}
    for name, fixture in cases.items():
        folder = work / "hostile" / name
        folder.mkdir(parents=True)
        m["write_text"](folder / "verify-package.py", m["VERIFY"])
        m["write_json"](folder / "MANIFEST.json", fixture)
        if name == "changed_bytes":
            (folder / "changed.txt").write_bytes(b"changed")
        run = subprocess.run([sys.executable, "verify-package.py"], cwd=folder,
                             text=True, capture_output=True)
        assert run.returncode != 0, "Hostile verifier input accepted: " + name
        verdicts[name] = {"rejected": True, "message": (run.stdout+run.stderr).strip()}

    # Reject optimized Python before any attempted extraction.
    optimized = subprocess.run([sys.executable, "-O", str(BUILDER), "--self-test"],
                               capture_output=True, text=True)
    assert optimized.returncode != 0
    payload = {
        "schema": "tect/q3lock-submission-package-audit/1.0", "status": "PASS",
        "claim_bearing": False, "result_id": "R-497", "scope": m["SCOPE"],
        "archive_sha256": m["file_hash"](archive),
        "archive_members": len(manifest["files"])+1,
        "verified_file_hashes": len(manifest["files"]),
        "extracted_integrity": integrity.stdout.strip(),
        "extracted_integrated_replay": checks,
        "current_repository_replay": current,
        "scientific_body_comparison": scientific,
        "hostile_verifier_checks": verdicts,
        "optimized_python_rejected": True,
        "python": sys.version,
        "source_hashes": {p.relative_to(ROOT).as_posix(): m["file_hash"](p)
                          for p in (BUILDER, Path(__file__).resolve(), dest / "MANIFEST.json",
                                    dest / "build-report.json", dest / "render-review.json")},
        "boundary": "Package integrity, finite/provenance replay and layout receipts only; no analytic, novelty, external-review, journal or sector acceptance. No transmission.",
    }
    if args.write_new:
        args.write_new.parent.mkdir(parents=True, exist_ok=True)
        with args.write_new.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print("Q3LOCK SUBMISSION AUDIT PASS", payload["verified_file_hashes"],
          "hashes;", len(verdicts), "hostile verifier cases rejected; extracted replay PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
