"""Verify file bytes, not the mathematical theorem. Python standard library only."""
from pathlib import Path
import hashlib, json, sys
root = Path(__file__).resolve().parent
m = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
for name, expected in m["files"].items():
    p = (root / name).resolve()
    if not p.is_relative_to(root) or not p.is_file():
        raise SystemExit("FAIL missing/unsafe member: " + name)
    if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
        raise SystemExit("FAIL changed member: " + name)
print("PASS", len(m["files"]), "file hashes; mathematics and literature review remain OPEN")
