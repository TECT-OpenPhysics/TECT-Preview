"""Raw provenance must survive Git, independent of the writer/reader OS.

These small real-Git fixtures exercise the repository's actual attributes.
They do not normalize bytes or alter expected hashes to make a test pass.
"""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess

import pytest


REPO = Path(__file__).resolve().parents[2]
GIT = shutil.which("git")
pytestmark = pytest.mark.skipif(GIT is None, reason="Git is required")


def git(root, *args):
    env = os.environ.copy()
    # A caller's alternate index/worktree must not leak into these fixtures.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(key, None)
    return subprocess.run(
        [GIT, "-c", "core.hooksPath=", "-c", "commit.gpgsign=false",
         "-c", "user.name=Checkout Test", "-c", "user.email=test@example.invalid",
         *args], cwd=root, env=env, capture_output=True, check=True,
    ).stdout


def attributes(root):
    for relative in (".gitattributes", "output/.gitattributes"):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((REPO / relative).read_bytes())


def fixtures(root):
    payloads = {
        "strategy/authority.json": b'{\r\n  "claim_bearing": false\r\n}\r\n',
        "strategy/mixed.json": b'{\r\n  "claim_bearing": false\n}\r\n',
        "claims/C6/runs/result.json": b'{"value": 1}\n',
        "codes/source.py": b'print("source")\n',
        "changelog/log.jsonl": b'{"id": "fixture"}\n',
        "archive/legacy/source.txt": b'old\r\nsource\r\n',
        "output/blob.pdf": b'%PDF-fixture\x00\r\n\n\xff',
        "CATALOG.md": b'# Frozen catalog\r\n',
    }
    for relative, data in payloads.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return payloads


def assert_checkout(tmp_path, source, payloads, reader):
    target = tmp_path / ("reader-" + reader)
    git(tmp_path, "clone", "--no-hardlinks", "--no-checkout", str(source), str(target))
    git(target, "config", "core.autocrlf", reader)
    git(target, "checkout", "--detach", "HEAD")
    for relative, expected in payloads.items():
        actual = (target / relative).read_bytes()
        assert actual == expected, (reader, relative)
        assert hashlib.sha256(actual).digest() == hashlib.sha256(expected).digest()
    assert git(target, "status", "--porcelain") == b""


@pytest.mark.parametrize("writer", ["true", "false", "input"])
@pytest.mark.parametrize("reader", ["true", "false", "input"])
def test_raw_hashes_survive_staging_and_checkout(tmp_path, writer, reader):
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init")
    git(source, "config", "core.autocrlf", writer)
    attributes(source)
    payloads = fixtures(source)
    git(source, "add", "--all")
    for relative, expected in payloads.items():
        blob = git(source, "show", ":" + relative)
        # Only the frozen compatibility catalog retains a normalized blob.
        if relative == "CATALOG.md":
            assert blob == expected.replace(b"\r\n", b"\n")
        else:
            assert blob == expected
    git(source, "commit", "-m", "Exact-byte fixtures")
    assert_checkout(tmp_path, source, payloads, reader)


def test_migration_preserves_originals_without_repinning(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init")
    git(source, "config", "core.autocrlf", "true")
    payloads = fixtures(source)
    git(source, "add", "--all")
    git(source, "commit", "-m", "Old implicit conversion")
    # Reproduce the old defect: raw source hashes differ from stored blobs.
    for relative in ("strategy/authority.json", "strategy/mixed.json"):
        assert git(source, "show", "HEAD:" + relative) != payloads[relative]
    catalog_blob = git(source, "show", "HEAD:CATALOG.md")
    attributes(source)
    git(source, "add", ".gitattributes", "output/.gitattributes")
    git(source, "add", "--renormalize", ".")
    assert git(source, "show", ":CATALOG.md") == catalog_blob
    # No content edits: the historical migration is EOL-only.
    git(source, "diff", "--cached", "--ignore-space-at-eol", "--exit-code",
        "--", *payloads)
    git(source, "commit", "-m", "Preserve original bytes")
    for reader in ("true", "false", "input"):
        assert_checkout(tmp_path, source, payloads, reader)
