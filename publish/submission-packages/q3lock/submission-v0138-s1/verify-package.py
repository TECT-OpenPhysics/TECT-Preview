"""Integrity and declared scope only, not mathematical acceptance."""
from pathlib import Path, PurePosixPath
import hashlib, json
root = Path(__file__).resolve().parent
m = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
scope = m["scope"]
if scope != {'result_id': 'R-497', 'tier': 'T0', 'claim_bearing': False, 'mathematics_review': 'NOT_PERFORMED', 'literature_review': 'NOT_PERFORMED', 'external_review_required_for_packaging': False, 'actual_submission': 'NOT_AUTHORIZED_NOT_PERFORMED'}:
    raise SystemExit("FAIL: declared scientific/review scope changed")
for name, expected in m["files"].items():
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or "\\" in name or ":" in name:
        raise SystemExit("FAIL unsafe member: " + name)
    target = (root / name).resolve()
    if not target.is_relative_to(root) or not target.is_file():
        raise SystemExit("FAIL missing/unsafe member: " + name)
    if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise SystemExit("FAIL changed member: " + name)
print("PASS", len(m["files"]), "file hashes; external review NOT PERFORMED")
