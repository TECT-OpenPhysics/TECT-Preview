"""Read-only fixed-checkpoint preservation audit; no scientific promotion."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = HERE.relative_to(ROOT).as_posix()
MAIN = "cfca9f789759bc613fdf807058f6f361b485cd82"  # Fixed input.
PROOF = "e8a284f65b92563bf12cd42fa3ad5d542f4a2c70"  # Fixed input.
BASE = "0775b22a9e567c1ac426cc8ce29bea7b6bc55a78"  # Fixed input.
BOUNDARY = "Checkpoint replay only: original proof prose uses source-qualified EXP IDs; consult the crosswalk. No new scientific review or promotion. Original boundary: "
REASON = "Lossless fixed-checkpoint integration, not a new route decision. Original decision: "


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def blob(ref, path):
    return git("show", ref + ":" + path)


def rows(data):
    return [json.loads(line) for line in data.splitlines()]


def remap_locator(value, mapping):
    prefix = "explorations/log.jsonl#"
    if value.startswith(prefix):
        return prefix + mapping.get(value[len(prefix):], value[len(prefix):])
    return value


def validate_replay(original, replayed, crosswalk):
    require(len(original) == len(replayed) == len(crosswalk["records"]), "Replay count differs")
    mapping = {row["source_id"]: row["canonical_id"] for row in crosswalk["records"]}
    require(len(mapping) == len(original), "Duplicate source identity")
    require(len(set(mapping.values())) == len(original), "Duplicate replay identity")
    first = crosswalk["canonical_prefix_records"] + 1
    changed = {"id", "title", "recorded_at", "recorded_by", "reviewed_on", "provenance",
               "boundary", "decision_reason", "related", "evidence_refs", "replay_provenance"}
    for offset, (old, new, row) in enumerate(zip(original, replayed, crosswalk["records"])):
        require(row["source_id"] == old["id"], "Source ordering differs")
        require(new["id"] == row["canonical_id"] == f"EXP-{first + offset:06d}", "Wrong replay ID")
        require(set(new) == set(old) | {"replay_provenance"}, "Unexpected payload keys")
        for key in set(old) - changed:
            require(new[key] == old[key], "Scientific field changed: " + key)
        require(new["title"] == "Checkpoint replay: " + old["title"], "Missing replay label")
        require(new["boundary"] == BOUNDARY + old["boundary"], "Replay boundary changed")
        require(new["decision_reason"] == REASON + old["decision_reason"], "Original decision changed")
        require(new["provenance"] == "historical-backfill", "False fresh-review attribution")
        require(new["recorded_at"] == crosswalk["replayed_at"], "Wrong import timestamp")
        require(new["reviewed_on"] == crosswalk["replayed_at"][:10], "Wrong import date")
        require(new["recorded_by"] == "Codex integration controller", "Wrong import author")
        meta = new["replay_provenance"]
        require(meta == row["replay_provenance"], "Qualified provenance differs")
        require(meta["source_commit"] == PROOF and meta["source_id"] == old["id"], "Wrong qualified source")
        for key in ("recorded_at", "recorded_by", "reviewed_on", "provenance"):
            require(meta["original_" + key] == old[key], "Original metadata changed")
        expected_related = [{"id": mapping.get(edge["id"], edge["id"]), "relation": edge["relation"]}
                            for edge in old["related"]]
        require(new["related"] == expected_related, "Wrong related-edge translation")
        expected_refs = [remap_locator(value, mapping) for value in old["evidence_refs"]]
        expected_refs.append(REL + "/crosswalk.json#" + old["id"])
        require(new["evidence_refs"] == expected_refs, "Wrong evidence-locator translation")


def check(require_ancestry=False):
    crosswalk = json.loads((HERE / "crosswalk.json").read_text(encoding="utf-8"))
    require((crosswalk["canonical_base"], crosswalk["source_commit"], crosswalk["common_base"])
            == (MAIN, PROOF, BASE), "Wrong source snapshots")
    path = "explorations/log.jsonl"
    shared, canonical, source = (blob(ref, path) for ref in (BASE, MAIN, PROOF))
    require(canonical.startswith(shared) and source.startswith(shared), "Common prefix differs")
    suffix = (HERE / "source-explorations.jsonl").read_bytes()
    require(source[len(shared):] == suffix, "Archived original records changed")
    require(sha(source) == crosswalk["source_log_sha256"], "Wrong full source log hash")
    temporal = (HERE / "source-temporal-corrections.jsonl").read_bytes()
    require(temporal == blob(PROOF, "explorations/temporal-corrections.jsonl"), "Source time sidecar changed")
    require((ROOT / "explorations/temporal-corrections.jsonl").read_bytes()
            == blob(MAIN, "explorations/temporal-corrections.jsonl"), "Canonical time sidecar changed")
    current = (ROOT / path).read_bytes()
    require(current.startswith(canonical), "Canonical published prefix changed")
    original = rows(suffix)
    new = rows(current[len(canonical):])[:len(original)]
    require(len(rows(canonical)) == crosswalk["canonical_prefix_records"], "Wrong prefix length")
    validate_replay(original, new, crosswalk)
    for raw, row in zip(suffix.splitlines(keepends=True), crosswalk["records"]):
        require(sha(raw) == row["source_line_sha256"], "Original line hash differs")
        require(row["replay_provenance"]["source_line_sha256"] == sha(raw), "Provenance line hash differs")
    corrected = set()
    for correction in rows(temporal):
        for item in correction["corrections"]:
            first, last = (int(item[key].split("-")[1]) for key in ("first_id", "last_id"))
            corrected.update(f"EXP-{number:06d}" for number in range(first, last + 1))
    for old, row in zip(original, crosswalk["records"]):
        expected = "UNKNOWN" if old["id"] in corrected else "RETAINED_SOURCE_TEXT"
        require(row["replay_provenance"]["original_timestamp_semantics"] == expected,
                "Source timestamp correction misapplied")
    trees = {}
    for ref in {value["source_commit"] for value in crosswalk["protected_files"].values()}:
        require(ref in {MAIN, PROOF}, "Unapproved inventory source")
        trees[ref] = {}
        for item in git("ls-tree", "-r", "-z", ref).split(b"\0"):
            if item:
                header, path = item.split(b"\t", 1)
                mode, kind, oid = header.decode().split()
                if kind == "blob":
                    trees[ref][path.decode()] = oid
    for path, expected in crosswalk["protected_files"].items():
        resolved = (ROOT / path).resolve()
        require(resolved.is_relative_to(ROOT), "Inventory path escapes repository")
        data = resolved.read_bytes()
        oid = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(sha(data) == expected["sha256"], "Protected bytes changed: " + path)
        require(oid == expected["git_blob"] == trees[expected["source_commit"]].get(path),
                "Protected bytes do not match fixed Git source: " + path)
    path = "changelog/log.jsonl"
    old_events, source_events, events = rows(blob(MAIN, path)), rows(blob(PROOF, path)), rows((ROOT / path).read_bytes())
    ids = {event["id"] for event in old_events}
    additions = [event for event in source_events if event["id"] not in ids]
    union = old_events + additions
    require(events[:len(union)] == union, "Changelog payload union changed")
    require(len(events) > len(union) and events[len(union)]["id"] == crosswalk["integration_event"], "Missing integration disclosure")
    if require_ancestry:
        for ref in (MAIN, PROOF):
            git("merge-base", "--is-ancestor", ref, "HEAD")
    return {"status": "PASS", "source_commit": PROOF, "canonical_base": MAIN,
            "original_records_preserved": len(original), "replay_records": len(new),
            "protected_files": len(crosswalk["protected_files"]),
            "unchanged_source_exploration_bytes": len(suffix),
            "both_source_ancestors_verified": require_ancestry,
            "scientific_claim": False}


def self_test():
    crosswalk = json.loads((HERE / "crosswalk.json").read_text(encoding="utf-8"))
    original = rows((HERE / "source-explorations.jsonl").read_bytes())
    new = rows((ROOT / "explorations/log.jsonl").read_bytes())[crosswalk["canonical_prefix_records"]:][:len(original)]
    validate_replay(original, new, crosswalk)
    fixtures = []
    changed = copy.deepcopy(new); changed[0]["finding"] += " changed"; fixtures.append(changed)
    fixtures.append(copy.deepcopy(new[:-1]))
    changed = copy.deepcopy(new); changed[0]["id"] = "EXP-000001"; fixtures.append(changed)
    changed = copy.deepcopy(new); changed[0]["provenance"] = "contemporaneous"; fixtures.append(changed)
    changed = copy.deepcopy(new); changed[0]["evidence_refs"] = []; fixtures.append(changed)
    changed = copy.deepcopy(new)
    target = next(row for row in changed if row["related"])
    target["related"][0]["id"] = "EXP-000000"; fixtures.append(changed)
    for changed in fixtures:
        try:
            validate_replay(original, changed, crosswalk)
        except ValueError:
            continue
        raise ValueError("Hostile replay fixture accepted")
    print("REPLAY SELF-TEST PASS:", len(fixtures), "hostile transformations rejected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--require-ancestry", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    if args.check:
        print(json.dumps(check(args.require_ancestry), indent=2))
