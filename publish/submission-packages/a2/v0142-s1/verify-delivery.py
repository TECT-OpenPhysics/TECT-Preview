#!/usr/bin/env python3
"""Verify and distribute an immutable A2/R-157/R-158 paper checkpoint.

Archive identities and commit below are declared provenance INPUTS, not derived
scientific numbers. --stage reads the two existing transport archives, validates
every member, and extracts into an absent scratch directory. --seal requires a
fresh extracted-source replay and authored all-page visual receipt. --check is
read-only. Large source transport stays outside Git; its identity and regeneration
contract are public. No source proof, old receipt, branch or review form is edited.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "publish/submission-packages/a2/v0142-s1"
PAPER = "publish/papers/a2-r157-r158-ensemble-minimizers"
SOURCE_COMMIT = "903426f3229ff1a5bda3dbe961d37bc13c0a5dd0"
INPUTS = {
    "a2-r157-r158-submission-v0.1.42.zip":
        "4ab649efdcae847fa3023bdaab4ae8066bb6022597ec399bba6b30a0fc297141",
    "a2-r157-r158-reproduction-source-v0.1.42.zip":
        "f7a4e7c672a0a2a849c6b26cbe921a332c76ba181adeffda386acb273709e501",
}
SMALL, SOURCE = INPUTS
MANIFEST = "TRANSPORT-MANIFEST.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def safe(name):
    p = PurePosixPath(name)
    require(bool(name) and p.parts and p.as_posix() == name and not p.is_absolute()
            and ":" not in name and "\\" not in name
            and not {"..", ".git", "internal", "__pycache__"}.intersection(p.parts),
            "Unsafe member: " + name)
    return p


def verify_zip(path, expected=None):
    if expected:
        require(digest(path.read_bytes()) == expected, "Archive identity changed")
    with zipfile.ZipFile(path) as z:
        entries = [i for i in z.infolist() if not i.is_dir()]
        names = [i.filename for i in entries]
        require(len(names) == len(set(names)), "Duplicate archive member")
        for item in entries:
            safe(item.filename)
            require((item.external_attr >> 16) & 0o170000 != 0o120000, "Symlink member")
        m = json.loads(z.read(MANIFEST))
        require(m["source_commit"] == SOURCE_COMMIT, "Wrong source checkpoint")
        require(m["external_review"] == "NOT PERFORMED" and m["submitted"] is False,
                "False review/submission disposition")
        require(set(names) == set(m["files"]) | {MANIFEST}, "Incomplete inventory")
        for name, row in m["files"].items():
            data = z.read(name)
            require(digest(data) == row["sha256"] and len(data) == row["bytes"],
                    "Changed member: " + name)
        require(z.testzip() is None, "ZIP CRC failure")
    return m


def extract_checked(path, target):
    require(not target.exists(), "Extraction target must be absent")
    target.mkdir(parents=True)
    with zipfile.ZipFile(path) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            out = target.joinpath(*safe(item.filename).parts)
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("xb") as stream:
                stream.write(z.read(item))


def stage(inputs, work):
    require(not work.exists(), "Scratch directory must be absent")
    manifests = {name: verify_zip(inputs / name, h) for name, h in INPUTS.items()}
    with zipfile.ZipFile(inputs / SMALL) as small, zipfile.ZipFile(inputs / SOURCE) as source:
        require(source.comment.decode("ascii").strip() == SOURCE_COMMIT,
                "Git archive comment does not identify the pinned commit")
        shared = []
        for name in manifests[SMALL]["files"]:
            if name.startswith("paper/"):
                source_name = "source/" + PAPER + "/" + name[len("paper/"):]
                require(small.read(name) == source.read(source_name), "Paper/source mismatch")
                shared.append(name)
        replay = json.loads(small.read("checks/final-clean-replay.json"))
        require(replay["resolved_commit"] == SOURCE_COMMIT
                and replay["verdict"] == "PAPER-CLEAN-SNAPSHOT-REPLAY-PASS",
                "Wrong historical clean replay")
    work.mkdir(parents=True)
    extract_checked(inputs / SMALL, work / "package")
    extract_checked(inputs / SOURCE, work / "replay")
    write_json(work / "stage.json", {
        "source_commit": SOURCE_COMMIT, "input_archives": INPUTS,
        "file_counts": {n: len(m["files"]) for n, m in manifests.items()},
        "identical_paper_source_files": len(shared), "verdict": "PASS",
        "external_review": "NOT PERFORMED", "submitted": False})
    print("STAGE PASS: both archives and paper/source identities verified", flush=True)


def seal(inputs, work, companion):
    require(not DEST.exists() and not DEST.with_suffix(".zip").exists(), "Sealed edition exists")
    require(not companion.exists(), "Companion destination must be absent")
    stage_receipt = read_json(work / "stage.json")
    require(stage_receipt["input_archives"] == INPUTS, "Stage source differs")
    replay = read_json(work / "replay-result-current.json")
    require(replay["verdict"] == "PASS" and replay["passed"] == replay["total"]
            and replay["total"] > 0 and not replay["fatal_error"], "Fresh replay failed")
    require(len(replay["results"]) == replay["total"]
            and all(r["passed"] and r["returncode"] == 0 for r in replay["results"]),
            "Replay rows disagree with summary")
    require(replay["input_manifest_sha256"] == digest((work / "package/paper/verification/runs/reproduction-manifest.json").read_bytes()),
            "Replay did not start from the original paper inventory")
    qa = read_json(work / "current-package-qa.json")
    require(qa["verdict"] == "PASS" and qa["external_review"] == "NOT PERFORMED"
            and qa["actual_submission"] == "NOT PERFORMED"
            and qa["manuscript_sha256"] == digest((work / "package/paper/manuscript.tex").read_bytes()),
            "Current package identity/scope audit failed")
    visual = read_json(work / "visual-review.json")
    for name, row in visual["documents"].items():
        require(digest((work / "package/paper" / name).read_bytes()) == row["sha256"],
                "Visual identity changed")
        require(row["verdict"] == "PASS" and row["pages"] > 0
                and row["inspected_pages"] == list(range(1, row["pages"] + 1)),
                "Incomplete visual inspection")
    require(set(visual["documents"]) == {"manuscript.pdf", "submission-notes.pdf"},
            "Missing final document")
    for name, h in INPUTS.items():
        verify_zip(inputs / name, h)
    DEST.mkdir(parents=True)
    with zipfile.ZipFile(inputs / SMALL) as z:
        for item in z.infolist():
            if item.is_dir():
                continue
            name = item.filename
            if name == MANIFEST:
                name = "checks/original-transport-manifest.json"
            out = DEST.joinpath(*safe(name).parts)
            out.parent.mkdir(parents=True, exist_ok=True)
            with out.open("xb") as stream:
                stream.write(z.read(item))
    for name in ("stage.json", "replay-result-current.json", "visual-review.json",
                 "manuscript-qa.json", "notes-qa.json",
                 "replay-environment-failure.json", "replay-result.json", "current-package-qa.json"):
        shutil.copyfile(work / name, DEST / "checks" / name)
    shutil.copyfile(work / "DELIVERY-README.md", DEST / "DELIVERY-README.md")
    shutil.copyfile(Path(__file__), DEST / "verify-delivery.py")
    companion.mkdir(parents=True)
    shutil.copyfile(inputs / SOURCE, companion / SOURCE)
    require(digest((companion / SOURCE).read_bytes()) == INPUTS[SOURCE], "Companion copy differs")
    files = {p.relative_to(DEST).as_posix(): {"bytes": p.stat().st_size,
             "sha256": digest(p.read_bytes())} for p in sorted(DEST.rglob("*")) if p.is_file()}
    write_json(DEST / MANIFEST, {"source_commit": SOURCE_COMMIT,
        "paper_version": "0.1.42", "distribution_version": "s1",
        "external_review": "NOT PERFORMED", "submitted": False,
        "files": files, "source_companion": {"file": SOURCE, "sha256": INPUTS[SOURCE],
            "bytes": (companion / SOURCE).stat().st_size,
            "scope": "Complete pinned repository, not additional paper claims; runtimes excluded"}})
    with zipfile.ZipFile(DEST.with_suffix(".zip"), "x", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DEST.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(DEST).as_posix())
    result = verify_zip(DEST.with_suffix(".zip"))
    print("SEAL PASS:", len(result["files"]), "inventoried files")


def self_test():
    cases = ("", ".", "../x", "/x", "C:/x", "a\\b", "a//b", ".git/config", "internal/x")
    for name in cases:
        try:
            safe(name)
        except ValueError:
            pass
        else:
            raise AssertionError("Unsafe fixture accepted")
    require(str(safe("paper/manuscript.pdf")) == "paper/manuscript.pdf", "Safe fixture rejected")
    data = b"fixture"
    base = {"source_commit": SOURCE_COMMIT, "external_review": "NOT PERFORMED",
            "submitted": False, "files": {"paper/test.txt": {"sha256": digest(data), "bytes": len(data)}}}
    fixtures = [({}, data, False, True),
                ({"external_review": "APPROVED"}, data, False, False),
                ({"submitted": True}, data, False, False),
                ({"source_commit": "wrong"}, data, False, False),
                ({}, b"changed", False, False), ({}, data, True, False),
                ({"files": {}}, data, False, False)]
    for patch, content, missing, allowed in fixtures:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as z:
            if not missing:
                z.writestr("paper/test.txt", content)
            z.writestr(MANIFEST, json.dumps({**base, **patch}))
        stream.seek(0)
        try:
            verify_zip(stream)
        except (ValueError, KeyError):
            require(not allowed, "Valid archive fixture rejected")
        else:
            require(allowed, "Hostile archive fixture accepted")
    print("SELF TEST PASS:", len(cases), "unsafe paths and", len(fixtures), "archive fixtures")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", action="store_true")
    p.add_argument("--seal", action="store_true")
    p.add_argument("--check", type=Path)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--inputs", type=Path)
    p.add_argument("--work", type=Path)
    p.add_argument("--companion", type=Path)
    a = p.parse_args()
    if not __debug__:
        raise SystemExit("Assertions must be enabled")
    if a.self_test:
        self_test()
    if a.check:
        m = verify_zip(a.check)
        print("ARCHIVE PASS:", len(m["files"]), "files; external review NOT PERFORMED")
    if a.stage:
        require(a.inputs is not None and a.work is not None, "Stage paths required")
        stage(a.inputs.resolve(), a.work.resolve())
    if a.seal:
        require(a.inputs is not None and a.work is not None and a.companion is not None,
                "Seal paths required")
        seal(a.inputs.resolve(), a.work.resolve(), a.companion.resolve())


if __name__ == "__main__":
    main()
