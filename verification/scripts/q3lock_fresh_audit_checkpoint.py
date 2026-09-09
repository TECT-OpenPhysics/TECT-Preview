"""Create or validate a non-overwriting Q3LOCK manuscript audit checkpoint.

The seven registered manuscript auditors write protected historical results when
run as stand-alone commands.  This wrapper imports their ``build_payload``
functions in memory, verifies that the protected bytes stay unchanged, and
writes one new immutable aggregate checkpoint.  It is provenance evidence only
and does not promote R-497, certify an analytic limit, or build a PDF.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import runpy
import tempfile


ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
DEFAULT_LABEL = "2026-09-08-q3lock-manuscript-fresh-audit-source-review-v1"


def checkpoint_paths(label=DEFAULT_LABEL):
    if (not isinstance(label, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", label)):
        raise ValueError("Checkpoint label must be one safe public-run directory name.")
    out_dir = RUNS / label
    return out_dir, out_dir / "result.json", out_dir / "source-map.json"


OUT_DIR, OUT, SOURCE_MAP = checkpoint_paths()

AUDIT_SPECS = (
    ("source", "verification/scripts/q3lock_manuscript_source_audit.py"),
    ("loop", "verification/scripts/q3lock_manuscript_loop_audit.py"),
    ("dlr", "verification/scripts/q3lock_manuscript_dlr_audit.py"),
    ("infrared", "verification/scripts/q3lock_manuscript_infrared_audit.py"),
    ("collective", "verification/scripts/q3lock_manuscript_collective_audit.py"),
    ("composition", "verification/scripts/q3lock_manuscript_composition_audit.py"),
    ("content", "verification/scripts/q3lock_manuscript_content_audit.py"),
)

PROTECTED = tuple(
    RUNS / f"2026-09-06-q3lock-manuscript-{part}-audit/result.json"
    for part in ("content", "loop", "dlr", "infrared", "collective", "composition")
) + (RUNS / "2026-09-07-q3lock-manuscript-source-audit/result.json",)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _collect_hashes(node, hashes):
    if not isinstance(node, dict):
        if isinstance(node, list):
            for item in node:
                _collect_hashes(item, hashes)
        return
    for source, value in node.get("source_hashes", {}).items():
        path = (ROOT / source).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
            raise ValueError("Audit source hash escapes or is missing: " + source)
        observed = digest(path)
        if observed != value or (source in hashes and hashes[source] != value):
            raise ValueError("Inconsistent audit source hash: " + source)
        hashes[source] = value
    for key, value in node.items():
        if key != "source_hashes":
            _collect_hashes(value, hashes)


def build_payload(label=None):
    _, out, source_map_path = checkpoint_paths(label or DEFAULT_LABEL)
    if out.exists() or source_map_path.exists():
        raise FileExistsError("Fresh audit checkpoint already exists; refusing overwrite.")
    before = {path: path.read_bytes() for path in PROTECTED}
    results = []
    hashes = {"verification/scripts/q3lock_fresh_audit_checkpoint.py": digest(Path(__file__))}
    for label, relative in AUDIT_SPECS:
        script = ROOT / relative
        module = runpy.run_path(str(script), run_name="q3lock_fresh_" + label)
        payload = module["build_payload"]()
        if payload.get("status") != "PASS" or payload.get("claim_bearing") is not False:
            raise AssertionError("Audit scope/status failed: " + relative)
        results.append({
            "label": label,
            "script": relative,
            "schema": payload.get("schema"),
            "assertions_passed": payload.get("assertions_passed"),
            "payload_sha256": payload_digest(payload),
        })
        _collect_hashes(payload, hashes)
    after = {path: path.read_bytes() for path in PROTECTED}
    if before != after:
        raise AssertionError("A protected historical audit output changed in memory replay.")
    protected_hashes = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(value).hexdigest()
        for path, value in before.items()
    }
    source_map = {
        "schema": "tect/q3lock-fresh-audit-source-map/1.0",
        "checkpoint": out.relative_to(ROOT).as_posix(),
        "files": [
            {"source": source, "sha256": value}
            for source, value in sorted(hashes.items())
        ],
    }
    _atomic_json(source_map_path, source_map)
    hashes[source_map_path.relative_to(ROOT).as_posix()] = digest(source_map_path)
    return {
        "schema": "tect/q3lock-manuscript-fresh-audit-checkpoint/1.0",
        "status": "PASS",
        "claim_bearing": False,
        "checkpoint": out.relative_to(ROOT).as_posix(),
        "recorded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "audit_count": len(results),
        "audits": results,
        "total_assertions": sum(row["assertions_passed"] for row in results),
        "protected_record_count": len(PROTECTED),
        "protected_records_preserved": True,
        "protected_record_hashes": protected_hashes,
        "source_map": source_map_path.relative_to(ROOT).as_posix(),
        "source_map_sha256": hashes[source_map_path.relative_to(ROOT).as_posix()],
        "source_hashes": dict(sorted(hashes.items())),
        "scope": "Current internal manuscript replay only; no analytic closure, external review, theorem promotion, novelty certificate, or PDF.",
    }


def validate_checkpoint(label=None):
    _, out, source_map_path = checkpoint_paths(label or DEFAULT_LABEL)
    if not out.is_file() or not source_map_path.is_file():
        raise FileNotFoundError("Fresh audit checkpoint is missing.")
    result = json.loads(out.read_text(encoding="utf-8"))
    source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
    if result.get("status") != "PASS" or result.get("claim_bearing") is not False:
        raise ValueError("Fresh audit checkpoint scope/status changed.")
    if result.get("source_map_sha256") != digest(source_map_path):
        raise ValueError("Fresh audit source map hash changed.")
    if source_map.get("checkpoint") != out.relative_to(ROOT).as_posix():
        raise ValueError("Fresh audit source map points to a different checkpoint.")
    for source, expected in result.get("source_hashes", {}).items():
        path = (ROOT / source).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
            raise ValueError("Fresh audit source is missing or escapes: " + source)
        if digest(path) != expected:
            raise ValueError("Fresh audit source changed: " + source)
    for relative, expected in result.get("protected_record_hashes", {}).items():
        path = ROOT / relative
        if digest(path) != expected:
            raise ValueError("Protected audit record changed: " + relative)
    if result.get("audit_count") != len(result.get("audits", [])):
        raise ValueError("Fresh audit count is inconsistent.")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="run the seven in-memory auditors and write a new checkpoint")
    parser.add_argument("--label", default=DEFAULT_LABEL,
                        help="absent public-run directory name for this checkpoint")
    args = parser.parse_args()
    _, out, _ = checkpoint_paths(args.label)
    if args.write:
        payload = build_payload(args.label)
        _atomic_json(out, payload)
        print("Q3LOCK fresh manuscript audit checkpoint: PASS",
              payload["audit_count"], "audits;", payload["total_assertions"], "assertions")
    else:
        payload = validate_checkpoint(args.label)
        print("Q3LOCK fresh manuscript audit checkpoint: VALID",
              payload["audit_count"], "audits;", payload["total_assertions"], "assertions")
    print(out.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
