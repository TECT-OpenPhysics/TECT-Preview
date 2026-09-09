#!/usr/bin/env python3
"""Replay the current Q3LOCK manuscript and its attached diagnostics.

This is a new, non-overwriting checkpoint for the FSS primary-source applicability confirmation.  The
older paper replays remain historical readers and are deliberately not
weakened to accept a manuscript change.  This command replays the seven
current manuscript auditors, the seven canonical finite auditors, the
external-review matrix, the EXP-000782 independent package, and the finite
form audit in memory.  It preserves every historical result byte and never
creates a PDF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import runpy
import sys
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs"
PAPER = ROOT / "publish/papers/q3lock-phase-coexistence"
PACKAGE_MANIFEST = PAPER / "verification/package-manifest.json"
FRESH_SCRIPT = ROOT / "verification/scripts/q3lock_fresh_audit_checkpoint.py"
FRESH_LABEL = "2026-09-08-q3lock-manuscript-fresh-audit-source-review-v1"
FRESH_RESULT = RUNS / FRESH_LABEL / "result.json"
FRESH_SOURCE_MAP = RUNS / FRESH_LABEL / "source-map.json"
DEFAULT_OUTPUT = RUNS / "2026-09-08-q3lock-paper-integrated-replay-source-review-v1/result.json"
PRIOR_CURRENT_OUTPUT = RUNS / "2026-09-08-q3lock-paper-integrated-replay-final-content-review-v020/result.json"
PREVIOUS_CURRENT_OUTPUT = RUNS / "2026-09-08-q3lock-paper-integrated-replay-final-content-review-v019/result.json"
OLDER_CURRENT_OUTPUT = RUNS / "2026-09-08-q3lock-paper-integrated-replay-final-content-review-v018/result.json"
LEGACY_CURRENT_OUTPUT = RUNS / "2026-09-08-q3lock-paper-integrated-replay-final-content-review-v017/result.json"
ANCIENT_CURRENT_OUTPUT = RUNS / "2026-09-08-q3lock-paper-integrated-replay-final-content-review-v016/result.json"
INDEPENDENT_SCRIPT = ROOT / "verification/scripts/q3lock_independent_replay.py"
INDEPENDENT_RESULT = RUNS / "2026-09-08-q3lock-independent-replay-source-review-v1/result.json"
PRIOR_INDEPENDENT_RESULT = RUNS / "2026-09-07-q3lock-independent-replay-r16-v016/result.json"
OLD_INDEPENDENT_RESULT = RUNS / "2026-09-07-q3lock-independent-replay/result.json"
MATRIX_SCRIPT = ROOT / "verification/scripts/q3lock_independent_review_matrix_audit.py"
MATRIX_RESULT = RUNS / "2026-09-07-q3lock-independent-review-matrix-audit/result.json"
FINITE_SCRIPT = ROOT / "verification/scripts/q3lock_finite_form_closure_audit.py"
FINITE_RESULT = RUNS / "2026-09-08-q3lock-finite-form-closure-audit-source-review-v1/result.json"
PRIOR_FINITE_RESULT = RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r10-scalar-boundary/result.json"
OLD_FINITE_RESULT = RUNS / "2026-09-07-q3lock-finite-form-closure-audit/result.json"
ALGEBRA_SCRIPT = ROOT / "verification/scripts/q3lock_nonimporting_algebra.py"
ALGEBRA_RESULT = RUNS / "2026-09-08-q3lock-nonimporting-algebra-source-review-v1/result.json"
CURRENT_PRIOR_ALGEBRA_RESULT = RUNS / "2026-09-08-q3lock-nonimporting-algebra-current-v016-r10/result.json"
PRIOR_ALGEBRA_RESULT = RUNS / "2026-09-08-q3lock-nonimporting-algebra-current-v016-r4/result.json"
LEGACY_ALGEBRA_RESULT = RUNS / "2026-09-08-q3lock-nonimporting-algebra-current-v016-r3/result.json"
OLDER_ALGEBRA_RESULT = RUNS / "2026-09-08-q3lock-nonimporting-algebra-current-v016-r2/result.json"
OLDEST_ALGEBRA_RESULT = RUNS / "2026-09-08-q3lock-nonimporting-algebra-current-v016/result.json"
ANCESTOR_ALGEBRA_RESULT = RUNS / "2026-09-07-q3lock-nonimporting-algebra/result.json"
LEGACY_REPLAY = RUNS / "2026-09-07-q3lock-paper-readonly-replay-r10/result.json"
LEGACY_FRESH = RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r12-independent-replay-handoff"

MANUSCRIPT_AUDITS = (
    ("source", "verification/scripts/q3lock_manuscript_source_audit.py"),
    ("loop", "verification/scripts/q3lock_manuscript_loop_audit.py"),
    ("dlr", "verification/scripts/q3lock_manuscript_dlr_audit.py"),
    ("infrared", "verification/scripts/q3lock_manuscript_infrared_audit.py"),
    ("collective", "verification/scripts/q3lock_manuscript_collective_audit.py"),
    ("composition", "verification/scripts/q3lock_manuscript_composition_audit.py"),
    ("content", "verification/scripts/q3lock_manuscript_content_audit.py"),
)
CANONICAL = tuple(
    "verification/scripts/q3lock_" + name + "_audit.py"
    for name in (
        "absolute_partition",
        "thermodynamic_pressure",
        "dlr_tangent_content",
        "fkg_content",
        "reflection_infrared_content",
        "collective_falk_bruch_content",
        "strict_cusp_tangent_content",
    )
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def payload_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def atomic_no_replace(path: Path, payload: dict[str, Any]) -> None:
    if os.path.lexists(path):
        raise FileExistsError(f"refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def safe_repo_path(relative: str) -> Path:
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        raise ValueError("invalid source path")
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
        raise ValueError("missing or escaping source path: " + relative)
    return path


def validate_declared_source_hashes(node: Any) -> None:
    """Accept either exact-byte or LF-normalized hashes used by builders."""
    if isinstance(node, dict):
        declared = node.get("source_hashes")
        if isinstance(declared, dict):
            for relative, expected in declared.items():
                path = safe_repo_path(relative)
                if expected not in {sha256(path), normalized_sha256(path)}:
                    raise ValueError("current source hash mismatch: " + relative)
        for key, value in node.items():
            if key != "source_hashes":
                validate_declared_source_hashes(value)
    elif isinstance(node, list):
        for item in node:
            validate_declared_source_hashes(item)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_saved_payload(path: Path, payload: dict[str, Any], label: str) -> dict[str, Any]:
    before = path.read_bytes()
    saved = json.loads(before.decode("utf-8"))
    if saved != payload:
        raise ValueError(f"{label} saved payload differs")
    if path.read_bytes() != before:
        raise ValueError(f"{label} changed during read-only check")
    return saved


def run_builder(relative: str, run_name: str) -> dict[str, Any]:
    module = runpy.run_path(str(ROOT / relative), run_name=run_name)
    builder = module.get("build_payload")
    if not callable(builder):
        raise TypeError("builder missing: " + relative)
    payload = builder()
    if not isinstance(payload, dict):
        raise TypeError("builder did not return a mapping: " + relative)
    validate_declared_source_hashes(payload)
    return payload


def historical_paths(canonical_modules: list[tuple[str, dict[str, Any]]]) -> tuple[Path, ...]:
    paths: list[Path] = [
        RUNS / "2026-09-08-q3lock-independent-replay-portability-v1/result.json",
        RUNS / "2026-09-08-q3lock-paper-integrated-replay-portability-v1/result.json",
        RUNS / "2026-09-08-q3lock-manuscript-fresh-audit-portability-v1/result.json",
        RUNS / "2026-09-08-q3lock-manuscript-fresh-audit-portability-v1/source-map.json",
        RUNS / "2026-09-08-q3lock-review-locator-audit-portability-v1/result.json",
        RUNS / "2026-09-08-q3lock-completion-gate-audit-portability-v1/result.json",
        RUNS / "2026-09-08-q3lock-finite-form-closure-audit-collective-jensen-v038/result.json",
        RUNS / "2026-09-08-q3lock-nonimporting-algebra-collective-jensen-v039/result.json",
        RUNS / "2026-09-08-q3lock-independent-replay-collective-jensen-v057-readme-sync/result.json",
        RUNS / "2026-09-08-q3lock-paper-integrated-replay-collective-jensen-v110-final/result.json",
        RUNS / "2026-09-08-q3lock-manuscript-fresh-audit-collective-jensen-v115-final/result.json",
        RUNS / "2026-09-08-q3lock-manuscript-fresh-audit-collective-jensen-v115-final/source-map.json",
        LEGACY_REPLAY,
        PRIOR_CURRENT_OUTPUT,
        PREVIOUS_CURRENT_OUTPUT,
        OLDER_CURRENT_OUTPUT,
        LEGACY_CURRENT_OUTPUT,
        ANCIENT_CURRENT_OUTPUT,
        OLD_INDEPENDENT_RESULT,
        PRIOR_INDEPENDENT_RESULT,
        OLD_FINITE_RESULT,
        PRIOR_FINITE_RESULT,
        ALGEBRA_RESULT,
        CURRENT_PRIOR_ALGEBRA_RESULT,
        PRIOR_ALGEBRA_RESULT,
        LEGACY_ALGEBRA_RESULT,
        OLDER_ALGEBRA_RESULT,
        OLDEST_ALGEBRA_RESULT,
        ANCESTOR_ALGEBRA_RESULT,
        RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r7-fss-classical-phase-boundary/result.json",
        RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r8-fkg-cone-topology/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-source-audit/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r22-fss-classical-phase-boundary/result.json",
        RUNS / "2026-09-07-q3lock-paper-integrated-replay-r53-fss-source-confirmation/result.json",
        RUNS / "2026-09-07-q3lock-paper-integrated-replay-r54-review-matrix-v015/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r22-fss-classical-phase-boundary/source-map.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r21-fss-classical-phase-boundary/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r21-fss-classical-phase-boundary/source-map.json",
        RUNS / "2026-09-07-q3lock-independent-replay-r6-upper-truncation-resolvent-repair/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r20-fss-classical-phase-boundary/source-map.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r19-upper-truncation-resolvent-repair/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r19-upper-truncation-resolvent-repair/source-map.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r18-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r18-package-pointer-sync/source-map.json",
        RUNS / "2026-09-07-q3lock-independent-replay-r5-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r5-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-paper-integrated-replay-r15-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r17-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r17-package-pointer-sync/source-map.json",
        RUNS / "2026-09-07-q3lock-independent-replay-r5-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r5-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-paper-integrated-replay-r14-package-pointer-sync/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r16-simon-hypothesis-audit/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r16-simon-hypothesis-audit/source-map.json",
        RUNS / "2026-09-07-q3lock-independent-replay-r4-simon-hypothesis-audit/result.json",
        RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r4-simon-hypothesis-audit/result.json",
        RUNS / "2026-09-07-q3lock-paper-integrated-replay-r13-simon-hypothesis-audit/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r15-residual-label-fix/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r15-residual-label-fix/source-map.json",
        RUNS / "2026-09-07-q3lock-independent-replay-r3-residual-label-fix/result.json",
        RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r3-residual-label-fix/result.json",
        RUNS / "2026-09-07-q3lock-paper-integrated-replay-r12-residual-label-fix/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r13-form-closure/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r13-form-closure/source-map.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r14-integrated-form-closure/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r14-integrated-form-closure/source-map.json",
        RUNS / "2026-09-07-q3lock-paper-integrated-replay-r11-form-closure/result.json",
        RUNS / "2026-09-07-q3lock-independent-replay-r2-form-closure/result.json",
        RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r2-form-closure/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r12-independent-replay-handoff/result.json",
        RUNS / "2026-09-07-q3lock-manuscript-fresh-audit-r12-independent-replay-handoff/source-map.json",
    ]
    paths.extend(
        RUNS / f"2026-09-06-q3lock-manuscript-{part}-audit/result.json"
        for part in ("content", "loop", "dlr", "infrared", "collective", "composition")
    )
    paths.append(MATRIX_RESULT)
    paths.append(RUNS / "2026-09-07-q3lock-independent-replay-r14-fss-source-confirmation/result.json")
    paths.append(RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r9-fss-source-confirmation/result.json")
    paths.append(RUNS / "2026-09-07-q3lock-independent-replay-r15-scalar-boundary/result.json")
    paths.append(RUNS / "2026-09-07-q3lock-finite-form-closure-audit-r10-scalar-boundary/result.json")
    paths.append(RUNS / "2026-09-07-q3lock-paper-integrated-replay-r54-review-matrix-v015/result.json")
    paths.append(RUNS / "2026-09-07-q3lock-paper-integrated-replay-r55-review-matrix-v016/result.json")
    paths.append(RUNS / "2026-09-07-q3lock-paper-integrated-replay-r56-review-matrix-v016/result.json")
    paths.append(INDEPENDENT_RESULT)
    paths.append(FINITE_RESULT)
    for _, module in canonical_modules:
        output = module.get("OUT")
        if isinstance(output, Path):
            paths.append(output)
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path not in seen and path.is_file():
            unique.append(path)
            seen.add(path)
    return tuple(unique)


def build_payload() -> dict[str, Any]:
    if not __debug__:
        raise ValueError("assertions must be enabled; do not use python -O")

    manifest = read_json(PACKAGE_MANIFEST)
    expected_scope = {
        "result_id": "R-497",
        "tier": "T0",
        "claim_bearing": False,
        "publication_status": "RESEARCH_ONLY",
    }
    if manifest.get("claim_status") != expected_scope:
        raise ValueError("paper claim scope changed")
    if manifest.get("status") != "UNFROZEN_CONTENT_REVIEW" or manifest.get("pdf_status") != "DEFERRED":
        raise ValueError("paper freeze or PDF scope changed")
    if not (PAPER / "manuscript.tex").is_file():
        raise FileNotFoundError("manuscript.tex")
    pdfs = tuple(PAPER.glob("*.pdf"))
    if pdfs:
        raise ValueError("paper PDF exists before final content freeze")

    canonical_modules = [
        (relative, runpy.run_path(str(ROOT / relative), run_name="q3lock_integrated_canonical"))
        for relative in CANONICAL
    ]
    protected_before = {
        path: path.read_bytes()
        for path in historical_paths(canonical_modules)
        if path.is_file()
    }

    fresh_module = runpy.run_path(str(FRESH_SCRIPT), run_name="q3lock_integrated_fresh")
    fresh = fresh_module["validate_checkpoint"](FRESH_LABEL)
    if fresh.get("status") != "PASS" or fresh.get("claim_bearing") is not False:
        raise ValueError("fresh manuscript checkpoint scope/status changed")
    if fresh.get("checkpoint") != FRESH_RESULT.relative_to(ROOT).as_posix():
        raise ValueError("fresh checkpoint path mismatch")
    if not FRESH_RESULT.is_file() or not FRESH_SOURCE_MAP.is_file():
        raise FileNotFoundError("final content-review checkpoint")

    manuscript_replay: list[dict[str, Any]] = []
    expected_rows = {row["label"]: row for row in fresh["audits"]}
    for label, relative in MANUSCRIPT_AUDITS:
        payload = run_builder(relative, "q3lock_integrated_" + label)
        if payload.get("status") != "PASS" or payload.get("claim_bearing") is not False:
            raise ValueError("manuscript audit scope/status failed: " + relative)
        row = expected_rows.get(label)
        if row is None or row.get("schema") != payload.get("schema"):
            raise ValueError("fresh checkpoint is missing manuscript audit: " + label)
        if row.get("assertions_passed") != payload.get("assertions_passed"):
            raise ValueError("manuscript assertion count changed: " + label)
        digest = payload_digest(payload)
        if row.get("payload_sha256") != digest:
            raise ValueError("manuscript payload differs from final content-review: " + label)
        manuscript_replay.append(
            {
                "label": label,
                "script": relative,
                "schema": payload.get("schema"),
                "assertions_passed": payload.get("assertions_passed"),
                "payload_sha256": digest,
            }
        )

    canonical_replay: list[dict[str, Any]] = []
    for relative, module in canonical_modules:
        output = module.get("OUT")
        if not isinstance(output, Path) or not output.is_file():
            raise FileNotFoundError("canonical output: " + relative)
        saved = read_json(output)
        payload = module["build_payload"]()
        validate_declared_source_hashes(payload)
        if saved != payload:
            raise ValueError("canonical result differs from its saved checkpoint: " + relative)
        canonical_replay.append(
            {
                "script": relative,
                "output": output.relative_to(ROOT).as_posix(),
                "status": "PASS",
                "assertions_passed": payload.get("assertions_passed"),
                "payload_sha256": payload_digest(payload),
            }
        )

    matrix = run_builder("verification/scripts/q3lock_independent_review_matrix_audit.py", "q3lock_integrated_matrix")
    if matrix != read_json(MATRIX_RESULT):
        raise ValueError("review matrix result differs from saved checkpoint")
    independent = run_builder("verification/scripts/q3lock_independent_replay.py", "q3lock_integrated_independent")
    independent_saved = read_json(INDEPENDENT_RESULT)["replay"]
    if independent != independent_saved:
        raise ValueError("current independent replay differs from saved checkpoint")
    finite = run_builder("verification/scripts/q3lock_finite_form_closure_audit.py", "q3lock_integrated_finite_form")
    if finite != read_json(FINITE_RESULT):
        raise ValueError("current finite form result differs from saved checkpoint")
    algebra = run_builder("verification/scripts/q3lock_nonimporting_algebra.py", "q3lock_integrated_algebra")
    if algebra != read_json(ALGEBRA_RESULT)["replay"]:
        raise ValueError("current non-importing algebra result differs from saved checkpoint")

    for path, original in protected_before.items():
        if path.read_bytes() != original:
            raise ValueError("historical output changed during integrated replay: " + str(path))

    source_files = (
        Path(__file__).resolve(),
        ROOT / "verification/tests/test_q3lock_manuscript_math_delimiters.py",
        ROOT / "strategy/q3lock-remaining-blocks-and-source-review-260908.md",
        ROOT / "verification/tests/test_q3lock_independent_replay_portability.py",
        ROOT / "strategy/q3lock-replay-portability-and-bounded-review-260908.md",
        PACKAGE_MANIFEST,
        PAPER / "manuscript.tex",
        FRESH_RESULT,
        FRESH_SOURCE_MAP,
        INDEPENDENT_RESULT,
        FINITE_RESULT,
        MATRIX_RESULT,
        ALGEBRA_RESULT,
        PAPER / "verification/nonimporting-algebra-audit.md",
        *(ROOT / relative for _, relative in MANUSCRIPT_AUDITS),
        *(ROOT / relative for relative in CANONICAL),
    )
    source_rows = []
    seen: set[str] = set()
    for path in source_files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in seen:
            continue
        if not path.is_file():
            raise FileNotFoundError(relative)
        source_rows.append({"path": relative, "sha256": sha256(path)})
        seen.add(relative)

    return {
        "schema": "tect/q3lock-manuscript-integrated-replay/1.0",
        "script_version": __version__,
        "status": "PASS",
        "claim_bearing": False,
        "result_id": "R-497",
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "paper_version": manifest.get("version"),
        "pdf_status": manifest.get("pdf_status"),
        "fresh_manuscript_checkpoint": {
            "path": FRESH_RESULT.relative_to(ROOT).as_posix(),
            "source_map": FRESH_SOURCE_MAP.relative_to(ROOT).as_posix(),
            "audit_count": fresh.get("audit_count"),
            "total_assertions": fresh.get("total_assertions"),
            "payload_sha256": payload_digest(fresh),
        },
        "manuscript_replay": manuscript_replay,
        "canonical_replay": canonical_replay,
        "review_matrix": {
            "path": MATRIX_RESULT.relative_to(ROOT).as_posix(),
            "assertions_passed": matrix["assertions"]["passed"],
            "payload_sha256": payload_digest(matrix),
        },
        "independent_replay": {
            "path": INDEPENDENT_RESULT.relative_to(ROOT).as_posix(),
            "child_assertions": independent["fresh_independent"],
            "package_assertions": independent["assertions"]["passed"],
            "payload_sha256": payload_digest(independent),
        },
        "finite_form_replay": {
            "path": FINITE_RESULT.relative_to(ROOT).as_posix(),
            "assertions_passed": finite["assertions_passed"],
            "payload_sha256": payload_digest(finite),
        },
        "nonimporting_algebra_replay": {
            "path": ALGEBRA_RESULT.relative_to(ROOT).as_posix(),
            "assertions_passed": algebra["assertions_passed"],
            "coefficient_identities": len(algebra["identities"]),
            "payload_sha256": payload_digest(algebra),
            "scope": algebra["scope"],
        },
        "historical_records_preserved": len(protected_before),
        "historical_record_sha256": [
            {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in sorted(protected_before)
        ],
        "source_files": source_rows,
        "scope": (
            "Current internal manuscript, finite-diagnostic, and provenance replay only. "
            "This does not certify form closure, Simon theorem applicability, an "
            "infinite-volume phase, a cusp, external review, novelty, theorem promotion, "
            "content freeze, or a paper PDF."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="read-only check (default)")
    mode.add_argument("--write-new", action="store_true", help="create an absent integrated result")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        payload = build_payload()
        if args.write_new:
            atomic_no_replace(args.output, payload)
        else:
            check_saved_payload(args.output, payload, "integrated replay")
        print(
            "Q3LOCK INTEGRATED REPLAY: PASS; manuscript groups",
            len(payload["manuscript_replay"]),
            "; canonical groups",
            len(payload["canonical_replay"]),
            "; independent child",
            payload["independent_replay"]["child_assertions"]["assertions_passed"],
            "/",
            payload["independent_replay"]["child_assertions"]["assertions_total"],
            "; historical records",
            payload["historical_records_preserved"],
        )
        print(args.output)
        return 0
    except (AssertionError, FileNotFoundError, OSError, TypeError, ValueError, KeyError) as error:
        print("Q3LOCK INTEGRATED REPLAY: FAIL:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
