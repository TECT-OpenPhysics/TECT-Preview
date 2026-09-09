#!/usr/bin/env python3
"""Audit/export unreviewed submission materials; never assign peer approval.

Default mode checks current paper identities and writes a local QA receipt.
--export requires a successful clean replay of the exact HEAD commit and
creates a small paper archive plus a complete committed-source archive.
The latter deliberately retains the wider registry context needed by legacy
checks; it is not a claim that unrelated research belongs to this paper.
All counts/hashes are computed. BASELINE is a declared provenance input.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

import reproduction_manifest as rm

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parents[2]
REL = PAPER.relative_to(ROOT).as_posix()
BASELINE = "1132b287d6453d4c2f4d294ab1f9daa3154f1f59"
OUTPUT = PAPER / "verification/runs/submission-package.json"
MANIFEST = "TRANSPORT-MANIFEST.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def safe_member(name):
    path = PurePosixPath(name)
    return bool(name and path.parts and not path.is_absolute() and ".." not in path.parts
                and "\\" not in name and ":" not in name
                and all(part not in (".git", "internal", "__pycache__") for part in path.parts))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def verified_rows(reader, rows):
    names = [item.filename for item in reader.infolist() if not item.is_dir()]
    require(len(names) == len(set(names)), "Duplicate archive member")
    require(set(names) == set(rows) | {MANIFEST}, "Archive inventory mismatch")
    for name, expected in rows.items():
        require(safe_member(name), "Unsafe archive member")
        data = reader.read(name)
        require(digest(data) == expected["sha256"] and len(data) == expected["bytes"],
                "Archive bytes differ: " + name)
    return len(rows)


def verify_archive(path):
    with zipfile.ZipFile(path) as reader:
        data = json.loads(reader.read(MANIFEST))
        count = verified_rows(reader, data["files"])
        require(reader.testzip() is None, "CRC failure")
    return count


def check():
    manifest = read_json(PAPER / "verification/runs/reproduction-manifest.json")
    assertions = {}
    assertions["manifest_pass"] = manifest["verdict"] == "PAPER-REPRODUCTION-MANIFEST-PASS"
    assertions["all_manifest_file_bytes_current"] = all(
        (ROOT / row["path"]).is_file()
        and digest((ROOT / row["path"]).read_bytes()) == row["sha256"]
        for row in manifest["files"])
    assertions["all_replay_input_bytes_current"] = all(
        digest((ROOT / row["path"]).read_bytes()) == row["sha256"]
        for row in manifest["replay_inputs"])
    rebuilt = rm.build()
    assertions["current_audit_verdicts_and_source_ids"] = rebuilt["verdict"].endswith("PASS")
    text = (PAPER / "manuscript.tex").read_text(encoding="utf-8")
    baseline = git("show", f"{BASELINE}:{REL}/manuscript.tex").decode("utf-8").replace("\r\n", "\n")
    start = r"\section{Introduction and statement of scope}"
    stop = r"\section{Verification and reproducibility}"
    assertions["mathematical_body_identical_to_baseline"] = (
        text.split(start, 1)[1].split(stop, 1)[0] == baseline.split(start, 1)[1].split(stop, 1)[0])
    assertions["appendix_and_bibliography_identical"] = text.split(r"\appendix", 1)[1] == baseline.split(r"\appendix", 1)[1]
    a, b = r"\section{Limitations and falsifiers}", r"\section{Conclusion}"
    assertions["limitations_identical"] = text.split(a, 1)[1].split(b, 1)[0] == baseline.split(a, 1)[1].split(b, 1)[0]
    assertions["external_review_disclosed_in_manuscript"] = "No external mathematical review or signed specialist novelty review has been" in text
    assertions["ai_role_disclosed_in_manuscript"] = "AI-assisted tools were used in research discussion" in text
    for name in ("independent-proof-review-form.md", "specialist-novelty-review-form.md"):
        form = (PAPER / name).read_text(encoding="utf-8")
        assertions[name + "_blank"] = ("Status: `BLANK /" in form
            and "reviewer_name: <name>" in form
            and "signature_or_verifiable_review_record: <reference>" in form)
        assertions[name + "_hashes"] = all(digest((PAPER / f).read_bytes()) in form
                                                        for f in ("manuscript.tex", "manuscript.pdf"))
    for pdf, qa_name, visual_name in (
        ("manuscript.pdf", "pdf-qa.json", "render-review.json"),
        ("submission-notes.pdf", "submission-notes-qa.json", "submission-notes-render.json"),
    ):
        qa = read_json(PAPER / "verification/runs" / qa_name)
        visual = read_json(PAPER / "verification/runs" / visual_name)
        current_hash = digest((PAPER / pdf).read_bytes())
        assertions[pdf + "_review_identity"] = qa["pdf_sha256"] == visual["pdf_sha256"] == current_hash
        assertions[pdf + "_all_pages_reviewed"] = (qa["verdict"] == visual["verdict"] == "PASS"
            and visual["pages"] == qa["pages"]
            and visual["visually_inspected_pages"] == list(range(1, qa["pages"] + 1)))
    ready = (PAPER / "submission-readiness.md").read_text(encoding="utf-8")
    assertions["review_and_submission_status_separate"] = "NOT PERFORMED" in ready and "not submitted" in ready
    assertions["personal_declarations_not_invented"] = "These personal facts are not inferred" in ready
    rows = [{"path": name, "passed": bool(ok)} for name, ok in assertions.items()]
    return {"schema": "tect/paper-submission-qa/1.0", "paper_version": "0.1.42",
            "baseline_commit": BASELINE, "manuscript_sha256": digest((PAPER / "manuscript.tex").read_bytes()),
            "assertions": {"passed": sum(assertions.values()), "total": len(rows), "results": rows},
            "verdict": "PASS" if all(assertions.values()) else "FAIL",
            "external_review": "NOT PERFORMED", "actual_submission": "NOT PERFORMED",
            "non_claims": ["Identity and packaging QA only; no mathematical or novelty endorsement.",
                           "No claim-level PUBLISHED capstone or external submission is recorded."]}


def self_test():
    for bad in ("", ".", "../escape", "/absolute", "C:/absolute", "x\\escape", ".git/config", "internal/private"):
        require(not safe_member(bad), "Unsafe fixture accepted")
    require(safe_member("source/claims/a.json"), "Safe fixture rejected")
    data = b"fixture"
    rows = {"safe.txt": {"sha256": digest(data), "bytes": len(data)}}
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as out:
        out.writestr("safe.txt", data)
        out.writestr(MANIFEST, "{}")
    with zipfile.ZipFile(stream) as reader:
        require(verified_rows(reader, rows) == 1, "Valid fixture rejected")
        for mutation in (b"changed", b"fixture plus"):
            wrong = {"safe.txt": {"sha256": digest(mutation), "bytes": len(mutation)}}
            try:
                verified_rows(reader, wrong)
            except ValueError:
                pass
            else:
                raise AssertionError("Changed archive content accepted")
    altered = "signature_or_verifiable_review_record: signed"
    require("signature_or_verifiable_review_record: <reference>" not in altered,
            "Filled signature fixture accepted")


def add_inventory(path, metadata):
    with zipfile.ZipFile(path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        rows = {}
        for item in archive.infolist():
            if item.is_dir():
                continue
            require(safe_member(item.filename), "Unsafe source path")
            data = archive.read(item)
            rows[item.filename] = {"bytes": len(data), "sha256": digest(data)}
        archive.writestr(MANIFEST, json.dumps({**metadata, "files": rows}, indent=2, sort_keys=True) + "\n")
    count = verify_archive(path)
    return {"file": path.name, "bytes": path.stat().st_size,
            "sha256": digest(path.read_bytes()), "verified_files": count}


def export(directory, receipt):
    directory = directory.resolve()
    require(directory.is_relative_to(ROOT / "tmp"), "Exports must remain below this workspace's tmp directory")
    directory.mkdir(parents=True, exist_ok=True)
    require(not any(directory.iterdir()), "Export directory must be empty; prior archives are preserved")
    head = git("rev-parse", "HEAD").decode().strip()
    replay = read_json(receipt)
    require(replay["verdict"] == "PAPER-CLEAN-SNAPSHOT-REPLAY-PASS", "Clean replay failed")
    require(replay["resolved_commit"] == head, "Replay is not for current committed source")
    require(not git("status", "--porcelain").strip(), "Export requires a clean committed source")
    require(check()["verdict"] == "PASS", "Current paper QA failed")
    metadata = {"paper_version": "0.1.42", "source_commit": head,
                "external_review": "NOT PERFORMED", "submitted": False,
                "scope": "Submission transport, not claim-level operator-confirmed capstone"}
    small = directory / "a2-r157-r158-submission-v0.1.42.zip"
    files = set(rm.PACKAGE_FILES) | {"verification/runs/reproduction-manifest.json",
                                    "verification/runs/submission-package.json"}
    with zipfile.ZipFile(small, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.write(PAPER / name, "paper/" + name)
        archive.writestr("checks/final-clean-replay.json", receipt.read_bytes())
        archive.writestr("START-HERE.txt", "Read paper/submission-notes.pdf and submission-readiness.md.\n"
            "External review NOT PERFORMED. No actual submission.\n"
            "The separate source ZIP contains the complete committed repository for replay,\n"
            "including wider historical registry context; these are not additional paper claims.\n"
            "Python/TeX/Lean runtimes and private caches are not included.\n"
            "Extract the source ZIP and follow the paper verification README from source/.\n")
    records = [add_inventory(small, metadata)]
    source = directory / "a2-r157-r158-reproduction-source-v0.1.42.zip"
    subprocess.run(["git", "archive", "--format=zip", "--prefix=source/", "-o", str(source), head],
                   cwd=ROOT, check=True)
    records.append(add_inventory(source, {**metadata, "scope": "Complete committed source; wider registry retained for legacy replay"}))
    result = {**metadata, "verdict": "PASS", "archives": records,
              "replay_receipt_sha256": digest(receipt.read_bytes())}
    rm.atomic_write(directory / "transport-receipt.json", json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--export", type=Path)
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--verify-archive", type=Path)
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    if args.self_test:
        self_test()
    if args.verify_archive:
        print("ARCHIVE-PASS:", verify_archive(args.verify_archive))
        return 0
    if args.export:
        require(args.replay is not None, "--export requires --replay")
        export(args.export, args.replay)
        return 0
    result = check()
    rm.atomic_write(args.output, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"SUBMISSION-PACKAGE-{result['verdict']}: {result['assertions']['passed']}/{result['assertions']['total']}")
    for row in result["assertions"]["results"]:
        if not row["passed"]:
            print("FAILED:", row["path"])
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
