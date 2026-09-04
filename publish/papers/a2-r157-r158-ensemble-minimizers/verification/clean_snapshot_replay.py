#!/usr/bin/env python3
"""Replay the A2/R-157/R-158 verification surface from a clean Git snapshot.

The runner archives a committed Git tree, extracts it into a fresh temporary
directory, and executes every mathematical/audit command listed by the paper
manifest.  The runner itself is excluded from the nested command list.  A
pre-resolved Lean ``.lake`` dependency cache may be linked explicitly; this is
recorded as an environment input and never treated as tracked source.

This is a source-clean reproducibility audit, not a proof or external review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PAPER_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]
MANIFEST_PATH = PAPER_ROOT / "verification" / "runs" / "reproduction-manifest.json"
DEFAULT_OUTPUT = PAPER_ROOT / "verification" / "runs" / "clean-snapshot-replay.json"
SELF_RELATIVE = (
    "publish/papers/a2-r157-r158-ensemble-minimizers/verification/"
    "clean_snapshot_replay.py"
)
R472_RELATIVE = "verification/scripts/a2_r472_lean_crosscheck_verify.py"

# Output tokens are test oracles for command contracts, not derived numbers.
EXPECTED_TOKENS = {
    "codes/foundations/a2_full_production_verify.py": (
        "ASSERTS: 61/61",
        "A2-FULL-PRODUCTION-VERIFY-PASS",
    ),
    "codes/foundations/a2_pinned_functional_unique_zero_global_minimizer.py": (
        "26/26 PASS",
    ),
    "codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_independent.py": (
        "24/24 PASS",
    ),
    "codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_verify.py": (
        "144/144 PASS",
        "legacy A2 61/61 PASS",
    ),
    "codes/foundations/a2_charge_ensemble_first_order_shell_transition.py": (
        "35/35 PASS",
    ),
    "codes/foundations/a2_charge_ensemble_first_order_shell_transition_independent.py": (
        "24/24 PASS",
    ),
    "codes/foundations/a2_charge_ensemble_first_order_shell_transition_verify.py": (
        "155/155 PASS",
        "R-157/A2 regression PASS",
    ),
    R472_RELATIVE: (
        "R-472 INTEGRATED PASS 22/22",
        "Lean=PASS",
    ),
    "publish/papers/a2-r157-r158-ensemble-minimizers/verification/exact_coercivity_audit.py": (
        "PAPER-EXACT-COERCIVITY-AUDIT-PASS: 13/13",
    ),
    "publish/papers/a2-r157-r158-ensemble-minimizers/verification/classii_sign_audit.py": (
        "PAPER-CLASSII-SIGN-AUDIT-PASS: 8/8",
    ),
    "publish/papers/a2-r157-r158-ensemble-minimizers/verification/ensemble_identity_audit.py": (
        "PAPER-ENSEMBLE-IDENTITY-AUDIT-PASS: 24/24",
    ),
    "publish/papers/a2-r157-r158-ensemble-minimizers/verification/analytic_dependency_audit.py": (
        "PAPER-ANALYTIC-DEPENDENCY-AUDIT-PASS: 50/50",
    ),
    "publish/papers/a2-r157-r158-ensemble-minimizers/verification/review_packet_audit.py": (
        "PAPER-REVIEW-PACKET-AUDIT-PASS: 22/22",
    ),
    "publish/papers/a2-r157-r158-ensemble-minimizers/verification/reproduction_manifest.py": (
        "PAPER-REPRODUCTION-MANIFEST-PASS",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def command_script(command: str) -> str:
    parts = command.split()
    if len(parts) < 4 or parts[:3] != ["python", "-X", "utf8"]:
        raise ValueError(f"unsupported replay command: {command}")
    return parts[3]


def nested_commands(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    commands = [
        item
        for item in manifest["expected_commands"]
        if command_script(item["command"]) != SELF_RELATIVE
    ]
    paths = [command_script(item["command"]) for item in commands]
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate nested replay script")
    if set(paths) != set(EXPECTED_TOKENS):
        raise ValueError(
            "clean replay oracle mismatch: "
            f"missing={sorted(set(EXPECTED_TOKENS) - set(paths))}, "
            f"extra={sorted(set(paths) - set(EXPECTED_TOKENS))}"
        )
    return commands


def git(*args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(process.stdout + process.stderr)
    return process.stdout.strip()


def link_lean_cache(target: Path, link: Path) -> str:
    if not target.is_dir():
        raise FileNotFoundError(f"Lean cache is missing: {target}")
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        process = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(process.stdout + process.stderr)
        return "junction"
    os.symlink(target, link, target_is_directory=True)
    return "directory-symlink"


def remove_cache_link(link: Path) -> None:
    if not os.path.lexists(link):
        return
    if os.name == "nt":
        os.rmdir(link)
    else:
        link.unlink()


def interpreter_record(python: Path) -> dict[str, Any]:
    probe = subprocess.run(
        [
            str(python),
            "-X",
            "utf8",
            "-c",
            (
                "import json, platform, sympy, sys; "
                "print(json.dumps({'executable': sys.executable, "
                "'python': platform.python_version(), 'sympy': sympy.__version__}, "
                "sort_keys=True))"
            ),
        ],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if probe.returncode != 0:
        raise RuntimeError(
            "The replay interpreter does not satisfy requirements.txt: "
            + probe.stdout
            + probe.stderr
        )
    return json.loads(probe.stdout)


def self_test() -> None:
    assert command_script("python -X utf8 a.py") == "a.py"
    try:
        command_script("python a.py")
    except ValueError:
        pass
    else:
        raise AssertionError("malformed command was accepted")
    fake = {
        "expected_commands": [
            {"command": f"python -X utf8 {path}"} for path in EXPECTED_TOKENS
        ]
        + [{"command": f"python -X utf8 {SELF_RELATIVE}"}]
    }
    assert len(nested_commands(fake)) == 14


def replay(
    *,
    treeish: str,
    python: Path,
    lean_cache: Path,
    output: Path,
    keep_workdir: bool,
) -> int:
    commands: list[dict[str, Any]] = []
    interpreter: dict[str, Any] = {}
    resolved_commit = ""
    resolved_tree = ""
    resolved_object_type = ""
    worktree_clean = False
    tracked_files = 0
    snapshot_manifest_sha256 = ""
    temp_parent = REPO_ROOT / "tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="a2-clean-snapshot-", dir=temp_parent))
    archive = work / "source.tar"
    snapshot = work / "snapshot"
    snapshot.mkdir()
    cache_link = snapshot / "verification" / "lean" / ".lake"
    cache_link_type = "not-linked"
    rows: list[dict[str, Any]] = []
    fatal_error = ""
    try:
        interpreter = interpreter_record(python)
        resolved_object = git("rev-parse", treeish)
        resolved_object_type = git("cat-file", "-t", resolved_object)
        if resolved_object_type == "commit":
            resolved_commit = resolved_object
            resolved_tree = git("rev-parse", f"{treeish}^{{tree}}")
        elif resolved_object_type == "tree":
            resolved_tree = resolved_object
        else:
            raise ValueError(
                f"treeish must resolve to a commit or tree, got {resolved_object_type}"
            )
        worktree_clean = git("status", "--porcelain") == ""
        archive_process = subprocess.run(
            ["git", "archive", "--format=tar", "-o", str(archive), treeish],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        if archive_process.returncode != 0:
            raise RuntimeError(archive_process.stdout + archive_process.stderr)
        with tarfile.open(archive, "r") as bundle:
            bundle.extractall(snapshot, filter="data")
        snapshot_manifest_path = (
            snapshot
            / "publish"
            / "papers"
            / "a2-r157-r158-ensemble-minimizers"
            / "verification"
            / "runs"
            / "reproduction-manifest.json"
        )
        snapshot_manifest_sha256 = sha256(snapshot_manifest_path)
        commands = nested_commands(
            json.loads(snapshot_manifest_path.read_text(encoding="utf-8"))
        )
        snapshot_files = sum(1 for path in snapshot.rglob("*") if path.is_file())
        tracked_files = len(
            git("ls-tree", "-r", "--name-only", treeish).splitlines()
        )
        if snapshot_files != tracked_files:
            raise RuntimeError(
                f"snapshot file count mismatch: {snapshot_files} != {tracked_files}"
            )

        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        environment["TECT_PYTHON"] = str(python)
        for item in commands:
            command = item["command"]
            parts = command.split()
            script = command_script(command)
            if script == R472_RELATIVE and cache_link_type == "not-linked":
                cache_link_type = link_lean_cache(lean_cache, cache_link)
            process = subprocess.run(
                [str(python), *parts[1:]],
                cwd=snapshot,
                env=environment,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
                timeout=600,
            )
            combined = (process.stdout + "\n" + process.stderr).strip()
            tokens = EXPECTED_TOKENS[script]
            passed = process.returncode == 0 and all(
                token in combined for token in tokens
            )
            rows.append(
                {
                    "command": command,
                    "script": script,
                    "returncode": process.returncode,
                    "expected_tokens": list(tokens),
                    "all_expected_tokens_present": all(
                        token in combined for token in tokens
                    ),
                    "stdout_sha256": text_sha256(process.stdout),
                    "stderr_sha256": text_sha256(process.stderr),
                    "output_tail": combined[-4000:],
                    "status": "PASS" if passed else "FAIL",
                }
            )
    except Exception as error:  # the JSON artifact must retain setup failures
        fatal_error = f"{type(error).__name__}: {error}"
    finally:
        try:
            remove_cache_link(cache_link)
        except Exception as error:
            fatal_error = fatal_error or f"cache cleanup failed: {error}"

    passed = sum(row["status"] == "PASS" for row in rows)
    total = len(commands) if commands else len(EXPECTED_TOKENS)
    verdict = (
        "PAPER-CLEAN-SNAPSHOT-REPLAY-PASS"
        if not fatal_error and passed == total
        else "PAPER-CLEAN-SNAPSHOT-REPLAY-FAIL"
    )
    result = {
        "schema": "tect/paper-clean-snapshot-replay/1.0",
        "paper_id": "a2-r157-r158-ensemble-minimizers",
        "generated_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "treeish": treeish,
        "resolved_commit": resolved_commit,
        "resolved_tree": resolved_tree,
        "resolved_object_type": resolved_object_type,
        "source_worktree_clean_before_replay": worktree_clean,
        "archive_sha256": sha256(archive) if archive.is_file() else "",
        "tracked_file_count": tracked_files,
        "snapshot_manifest_sha256": snapshot_manifest_sha256,
        "interpreter": interpreter,
        "requirements_sha256": sha256(REPO_ROOT / "requirements.txt"),
        "platform": platform.platform(),
        "lean_environment": {
            "non_bearing": True,
            "cache_path": str(lean_cache.resolve()),
            "cache_link_type": cache_link_type,
            "registry_sha256": sha256(REPO_ROOT / "verification/lean/registry.json"),
            "lake_manifest_sha256": sha256(
                REPO_ROOT / "verification/lean/lake-manifest.json"
            ),
        },
        "assertions": {"passed": passed, "total": total, "results": rows},
        "fatal_error": fatal_error,
        "verdict": verdict,
        "non_claims": [
            "This is a clean tracked-source replay, not a fresh operating-system or network bootstrap.",
            "The external Python environment and pre-resolved Lean dependency cache are recorded inputs.",
            "The non-bearing R-472 Lean sidecar does not promote the A2/R-157/R-158 theorem claims.",
            "Passing executable checks does not replace analytic or specialist external review.",
        ],
    }
    atomic_write(output, result)
    print(f"{verdict}: {passed}/{total}")
    print(f"artifact: {output}")
    if keep_workdir:
        print(f"workdir: {work}")
    else:
        shutil.rmtree(work)
    return 0 if verdict.endswith("PASS") else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--treeish", default="HEAD")
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument(
        "--lean-cache",
        type=Path,
        default=REPO_ROOT / "verification" / "lean" / ".lake",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--keep-workdir", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    return replay(
        treeish=args.treeish,
        python=args.python.resolve(),
        lean_cache=args.lean_cache.resolve(),
        output=args.output.resolve(),
        keep_workdir=args.keep_workdir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
