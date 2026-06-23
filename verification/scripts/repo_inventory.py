#!/usr/bin/env python3
"""repo_inventory.py -- shared tracked-artefact enumeration + incremental cache.

ROOT-CAUSE FIX (governance/adr/0001-catalog-incremental-tracked-enumeration.md):
build_catalog.py and release_check.py previously enumerated the PHYSICAL tree
(`Path.rglob("*")`) with a hand-maintained SKIP_DIRS set that did NOT honor
.gitignore. When Google Drive for Desktop left hundreds of MB of sync-temp
files on disk (.tmp.driveupload/*), and after 8047 such files were committed
by mistake before an ignore rule existed, the scanners read ~450 MB of junk on
every run -> the 45 s sandbox timeout. This module enumerates the REAL artefact
set via git, honoring .gitignore including files committed-by-mistake
(`git check-ignore --no-index`), and caches per-file computations keyed on
(size, mtime_ns) so unchanged files are never re-read. Stdlib-only.

Public API:
  real_files(repo)            -> sorted list[Path] of non-ignored working-tree files
  StatCache(cache_path)       -> incremental (size, mtime_ns)-keyed compute cache
"""
__version__ = "1.0.0"
__first_issued__ = "2026-06-23"
__version_issued__ = "2026-06-23"

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

# Fallback denylist (only used when git is unavailable). Mirrors the .gitignore
# Drive/transient sections so the fallback still excludes the junk class.
_DENY_PARTS = {
    ".git", "internal", "__pycache__", ".pytest_cache", "build", ".cache",
    ".tmp.driveupload", ".tmp.drivedownload", ".driveupload", ".drivedownload",
}


def _git(repo, args, inp=None, timeout=60):
    return subprocess.run(
        ["git"] + args, capture_output=True, text=True,
        cwd=str(repo), input=inp, timeout=timeout,
    )


def real_files(repo: Path, skip_names=frozenset()) -> list:
    """All non-ignored files in the working tree (tracked + new untracked),
    with gitignored junk excluded -- including files committed by mistake
    before an ignore rule existed (caught by `check-ignore --no-index`).

    Falls back to an rglob + denylist walk if git is unavailable.
    """
    repo = Path(repo)
    try:
        tracked = [l for l in _git(repo, ["ls-files", "-z"]).stdout.split("\0") if l]
        others = [l for l in _git(
            repo, ["ls-files", "-z", "--others", "--exclude-standard"]).stdout.split("\0") if l]
        cand = tracked + others
        if cand:
            ig = _git(repo, ["check-ignore", "--no-index", "--stdin", "-z"],
                      inp="\0".join(cand) + "\0")
            ignored = {l for l in ig.stdout.split("\0") if l}
            cand = [p for p in cand if p not in ignored]
        out = []
        for p in cand:
            if os.path.basename(p) in skip_names:
                continue
            f = repo / p
            if f.is_file():
                out.append(f)
        if out:
            return sorted(out)
    except Exception:
        pass
    return _rglob_fallback(repo, skip_names)


def _rglob_fallback(repo: Path, skip_names) -> list:
    out = []
    for f in repo.rglob("*"):
        if not f.is_file():
            continue
        if any(part in _DENY_PARTS for part in f.parts):
            continue
        if f.name in skip_names:
            continue
        out.append(f)
    return sorted(out)


class StatCache:
    """Incremental compute cache keyed on (size, mtime_ns).

    get_or_compute(repo, f, compute_fn) returns compute_fn(f, data_bytes) but
    invokes it (and reads the file) ONLY when the file's (size, mtime_ns) differs
    from the cached signature. On a hit the file is not read at all. The cache
    file is gitignored (verification/.cache/); delete it to force a cold rebuild.

    Trust model: identical (size, mtime_ns) is treated as unchanged content --
    the same heuristic git's index uses. A content change that preserves both
    size and nanosecond mtime is not observable; normal edits always change one.
    """

    def __init__(self, cache_path: Path):
        self.path = Path(cache_path)
        self.data = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}
        self._seen = set()
        self.dirty = False
        self.hits = 0
        self.misses = 0

    def get_or_compute(self, repo: Path, f: Path, compute_fn):
        rel = str(f.relative_to(repo)).replace("\\", "/")
        self._seen.add(rel)
        st = f.stat()
        sig = [st.st_size, st.st_mtime_ns]
        ent = self.data.get(rel)
        if ent is not None and ent.get("sig") == sig:
            self.hits += 1
            return ent["val"]
        self.misses += 1
        data = f.read_bytes()
        val = compute_fn(f, data)
        self.data[rel] = {"sig": sig, "val": val}
        self.dirty = True
        return val

    def prune(self):
        """Drop cache entries for files no longer enumerated (deleted/moved)."""
        stale = [k for k in self.data if k not in self._seen]
        for k in stale:
            del self.data[k]
        if stale:
            self.dirty = True

    def save(self):
        if not self.dirty:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh)
        os.replace(tmp, self.path)


# convenience for callers that only want a content hash
def sha256_12(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]
