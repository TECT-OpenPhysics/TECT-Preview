"""Restore exact historical ignored-path evidence from tracked hash-pinned copies.

Never overwrite a different existing target or modify an exploration record.
Default invocation checks only. --restore creates missing ignored files.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile


def confined(root, relative, prefix):
    root = Path(root).resolve()
    if not relative.startswith(prefix + "/"):
        raise ValueError("Unexpected evidence path prefix")
    path = (root / relative).resolve()
    if not path.is_relative_to(root / prefix):
        raise ValueError("Evidence path escapes its allowed directory")
    return path


def hydrate(workspace, authority=None, restore=False):
    workspace = Path(workspace).resolve()
    authority = Path(authority or workspace).resolve()
    manifest = authority / "verification/portable-evidence.json"
    if not manifest.exists():
        return {"restored": 0, "checked": 0}
    entries = json.loads(manifest.read_text(encoding="utf-8"))["files"]
    prepared = []
    for entry in entries:
        source = confined(authority, entry["source"], "archive/portable-evidence")
        target = confined(workspace, entry["target"], "tmp")
        payload = source.read_bytes()
        if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
            raise ValueError("Archived evidence hash mismatch: " + entry["source"])
        if target.exists():
            if not target.is_file() or target.read_bytes() != payload:
                raise ValueError("Existing evidence differs; preserved: " + entry["target"])
        elif not restore:
            raise ValueError("Missing " + entry["target"] + "; run doctor.py --fix")
        prepared.append((target, payload))
    restored = 0
    for target, payload in prepared:
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation: a competing writer wins without being overwritten.
        # Copy from a fsynced temporary file using a hard link for atomic no-replace.
        fd, temporary = tempfile.mkstemp(prefix=".portable-", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, target)
                restored += 1
            except FileExistsError:
                if target.read_bytes() != payload:
                    raise ValueError("Concurrent evidence conflict; preserved: " + str(target))
        finally:
            os.unlink(temporary)
    return {"restored": restored, "checked": len(entries)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--authority")
    parser.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    try:
        result = hydrate(args.workspace, args.authority, args.restore)
        print("PORTABLE-EVIDENCE: PASS " + json.dumps(result))
        return 0
    except (OSError, ValueError, KeyError) as error:
        print("PORTABLE-EVIDENCE: FAIL " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
