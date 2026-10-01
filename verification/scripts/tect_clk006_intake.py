"""Local CLK006 manifest intake; not a scientific or permission verifier.

INPUTS: hash-pinned intake policy and its protected CLK002/CLK005 authorities.
Run: python -X utf8 verification/scripts/tect_clk006_intake.py --packet PATH
Self-test: python -X utf8 verification/scripts/tect_clk006_intake.py --self-test
Attachments are read as bytes only. Never download, execute, unpack or publish.
Use a quiescent private intake directory; this is not a hostile-filesystem sandbox.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "strategy/clock/TECT-CLK-006-intake-policy-v1.json"
# INPUT: policy authority fingerprint, not a computed scientific constant.
POLICY_SHA256 = "10fe23ebe0a44368fa916e6ca53d466002e6cd275b26fec4f11330aef81a4104"
RUN_PATH = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs/2026-10-01-tect-clk006/tooling.json"
TOP_KEYS = {"schema", "packet_id", "target", "authority_refs", "provenance",
            "representation", "owner_descriptions", "researcher_mapping", "attachments"}
PROVENANCE_KEYS = {"claimed_provider", "affiliation", "acquisition_channel",
                   "acquired_utc", "owner_evidence_ref", "reuse_permission"}
ENTRY_KEYS = {"state", "summary", "evidence_refs"}
ATTACHMENT_KEYS = {"id", "path", "sha256", "role"}
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
RESERVED = re.compile(r"(?:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?\Z", re.I)


class Invalid(ValueError):
    """Invalid manifest or local integrity input; never scientific falsification."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Invalid("duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(value):
        raise Invalid("non-finite JSON constant: " + value)

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=constant)
    except Invalid:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Invalid("malformed UTF-8 JSON") from exc


def obj(value, keys, location):
    if type(value) is not dict or set(value) != set(keys):
        raise Invalid(location + ": missing or unknown object keys")


def text(value, location, nullable=False):
    if nullable and value is None:
        return None
    if type(value) is not str or not value.strip():
        raise Invalid(location + ": expected nonempty string")
    return value


def limits(value, max_string, depth=0):
    # Tooling recursion threshold only; not a scientific regularization.
    if depth > 16:
        raise Invalid("manifest nesting limit")
    if type(value) is str and len(value) > max_string:
        raise Invalid("manifest string limit")
    if isinstance(value, dict):
        for key, item in value.items():
            limits(key, max_string, depth + 1)
            limits(item, max_string, depth + 1)
    elif isinstance(value, list):
        for item in value:
            limits(item, max_string, depth + 1)


def read_bounded(path: Path, maximum: int) -> bytes:
    if not stat.S_ISREG(path.stat().st_mode):
        raise Invalid("not a regular file: " + path.name)
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise Invalid("file exceeds tooling size limit: " + path.name)
    return data


def load_policy():
    data = POLICY_PATH.read_bytes()
    if digest(data) != POLICY_SHA256:
        raise Invalid("intake policy fingerprint mismatch")
    policy = strict_json(data)
    for relative, expected in policy["protected_sources"].items():
        if digest((ROOT / relative).read_bytes()) != expected:
            raise Invalid("protected authority fingerprint mismatch: " + relative)
    return policy


def local_attachment(directory: Path, relative: str) -> Path:
    text(relative, "attachment.path")
    parts = relative.split("/")
    if any(not part or part in (".", "..") or part[-1:] in (".", " ")
           or any(ord(c) < 32 or c in '<>:"\\|?*' for c in part)
           or RESERVED.fullmatch(part) for part in parts):
        raise Invalid("unsafe attachment path")
    base = directory.resolve(strict=True)
    target = base
    for part in parts:
        target = target / part
        try:
            metadata = target.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode) or (
            getattr(metadata, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        ):
            raise Invalid("symlink or reparse attachment path")
    try:
        target.resolve(strict=True).relative_to(base)
    except FileNotFoundError:
        return target
    except ValueError as exc:
        raise Invalid("attachment outside packet directory") from exc
    return target


def inspect_packet(packet_path: Path) -> dict:
    receipt = {
        "schema": "tect/clock-intake-receipt/1.0",
        "policy_sha256": POLICY_SHA256,
        "packet_sha256": None,
        "intake_status": "REJECTED",
        "scientific_status": "HOLD_FOR_EVIDENCE",
        "empirical_use_authorized": False,
        "scientific_reentry_authorized": False,
        "mainline_gate_changed": False,
        "publication_authorized": False,
        "manual_content_review_required": True,
        "semantic_support": "NOT_EVALUATED",
        "locator_resolution": "NOT_EVALUATED",
        "owner_identity_and_permissions": "NOT_AUTHENTICATED",
        "new_template_calibration_capacity": "NOT_EVALUATED",
        "scientific_novelty": "NOT_EVALUATED",
        "researcher_mapping_state": "unknown",
        "missing_fields": [], "errors": [], "verified_attachments": [],
    }
    missing = receipt["missing_fields"]
    try:
        policy = load_policy()
        if not packet_path.exists():
            receipt["intake_status"] = policy["statuses"]["missing"]
            missing.append("packet")
            return receipt
        raw = read_bounded(packet_path, policy["limits"]["manifest_bytes"])
        receipt["packet_sha256"] = digest(raw)
        packet = strict_json(raw)
        limits(packet, policy["limits"]["string_characters"])
        obj(packet, TOP_KEYS, "packet")
        if packet["schema"] != "tect/clock-owner-intake/1.0":
            raise Invalid("unsupported packet schema")
        for name, expected in (("target", policy["target"]),
                               ("authority_refs", policy["protected_sources"])):
            if packet[name] != expected:
                raise Invalid(name + ": fixed authority or scope mismatch")
        if text(packet["packet_id"], "packet_id", True) is None:
            missing.append("packet_id")
        elif not ID.fullmatch(packet["packet_id"]):
            raise Invalid("invalid packet_id")
        representation = packet["representation"]
        if representation is None:
            missing.append("representation")
        elif representation not in policy["representations"]:
            raise Invalid("unsupported representation")

        attachments = packet["attachments"]
        if type(attachments) is not list or len(attachments) > policy["limits"]["attachments"]:
            raise Invalid("invalid attachment list or tooling count limit")
        ids, paths = set(), set()
        for attachment in attachments:
            obj(attachment, ATTACHMENT_KEYS, "attachment")
            aid = text(attachment["id"], "attachment.id")
            if not ID.fullmatch(aid) or aid.casefold() in ids:
                raise Invalid("invalid or duplicate attachment id")
            ids.add(aid.casefold())
            relative = text(attachment["path"], "attachment.path")
            if relative.casefold() in paths:
                raise Invalid("duplicate attachment path")
            paths.add(relative.casefold())
            expected = text(attachment["sha256"], "attachment.sha256")
            if not SHA.fullmatch(expected):
                raise Invalid("invalid attachment sha256")
            if attachment["role"] not in policy["attachment_roles"]:
                raise Invalid("invalid attachment role")
            path = local_attachment(packet_path.parent, relative)
            try:
                data = read_bounded(path, policy["limits"]["attachment_bytes"])
            except FileNotFoundError:
                missing.append("attachment:" + aid)
                continue
            if digest(data) != expected:
                raise Invalid("attachment hash mismatch: " + aid)
            receipt["verified_attachments"].append({"id": aid, "sha256": expected,
                                                     "bytes": len(data)})

        # References are syntactic declarations, not resolved content locators.
        exact_ids = {a["id"] for a in attachments}
        def reference(value, location):
            text(value, location)
            identifier, sep, locator = value.partition("#")
            if not sep or not locator.strip() or identifier not in exact_ids:
                raise Invalid(location + ": invalid attachment reference")

        provenance = packet["provenance"]
        obj(provenance, PROVENANCE_KEYS, "provenance")
        for key in sorted(PROVENANCE_KEYS - {"reuse_permission"}):
            value = text(provenance[key], "provenance." + key, True)
            if value is None:
                missing.append("provenance." + key)
            elif key == "owner_evidence_ref":
                reference(value, "provenance.owner_evidence_ref")
            elif key == "acquired_utc":
                if not value.endswith("Z"):
                    raise Invalid("acquired_utc must use UTC Z")
                try:
                    datetime.fromisoformat(value)
                except ValueError as exc:
                    raise Invalid("invalid acquired_utc") from exc
        if provenance["reuse_permission"] not in policy["reuse_values"]:
            raise Invalid("invalid reuse_permission")
        if provenance["reuse_permission"] == "unknown":
            missing.append("provenance.reuse_permission")

        def entry(value, location, required):
            obj(value, ENTRY_KEYS, location)
            state = value["state"]
            if state not in policy["entry_states"]:
                raise Invalid(location + ": invalid entry state")
            summary = text(value["summary"], location + ".summary", True)
            refs = value["evidence_refs"]
            if type(refs) is not list:
                raise Invalid(location + ": evidence_refs must be list")
            for ref in refs:
                reference(ref, location + ".evidence_refs")
            if required and (state != "provided" or summary is None or not refs):
                missing.append(location)
            return state

        descriptions = packet["owner_descriptions"]
        obj(descriptions, policy["owner_fields"], "owner_descriptions")
        for field in policy["owner_fields"]:
            entry(descriptions[field], "owner_descriptions." + field, True)
        # Optional researcher work never becomes an obligation imposed on the owner.
        receipt["researcher_mapping_state"] = entry(packet["researcher_mapping"],
                                                    "researcher_mapping", False)
        receipt["intake_status"] = policy["statuses"]["incomplete" if missing else "complete"]
    except (Invalid, OSError, TypeError, RecursionError) as exc:
        receipt["errors"].append(str(exc))
        receipt["intake_status"] = "REJECTED"
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--packet", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--check", action="store_true", help="reproduce saved tooling report")
    parser.add_argument("--json-report", action="store_true", help="self-test JSON on stdout")
    args = parser.parse_args()
    if args.self_test or args.check:
        suite = unittest.defaultTestLoader.discover(
            str(ROOT / "verification/tests"), pattern="test_tect_clk006_intake.py")
        test_module = sys.modules["test_tect_clk006_intake"]
        test_module.IntakeTests.records.clear()
        output = io.StringIO()
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
        sources = ["strategy/clock/TECT-CLK-006-intake-policy-v1.json",
                   "strategy/clock/TECT-CLK-006-intake-template-v1.json",
                   "verification/scripts/tect_clk006_intake.py",
                   "verification/tests/test_tect_clk006_intake.py"]
        report = {
            "schema": "tect/clock-intake-tooling-run/1.0",
            "fixture_role": "TEST_ONLY_NOT_OBSERVATIONS",
            "source_hashes": {p: digest((ROOT / p).read_bytes()) for p in sources},
            "success": result.wasSuccessful(), "unit_tests": result.testsRun,
            "skipped_tests": [test.id() for test, _ in result.skipped],
            "cases": sorted(test_module.IntakeTests.records, key=lambda x: x["case"]),
            "boundary": "Manifest syntax and byte checks only; no numerical payload, locator, ownership, permission, novelty or scientific validation. Real symlink test may be skipped by host privilege; mock reparse guard is separate.",
            "scientific_status": "HOLD_FOR_EVIDENCE",
            "empirical_use_authorized": False, "mainline_gate_changed": False,
            "Lean": "Not applicable to archival availability or provenance; not run.",
        }
        if args.check:
            expected = strict_json(RUN_PATH.read_bytes())
            def portable_core(item):
                # Actual symlink creation is optional host capability, not a bypass
                # of the required mocked guard or any other deterministic case.
                allowed_skip = "test_tect_clk006_intake.IntakeTests.test_symlink_rejection_if_host_permits"
                if any(value != allowed_skip for value in item["skipped_tests"]):
                    raise Invalid("unexpected skipped test")
                return {key: ([case for case in value if case["case"] != "symlink_rejection"]
                              if key == "cases" else value)
                        for key, value in item.items() if key != "skipped_tests"}
            if portable_core(report) != portable_core(expected):
                print("CLK006-CHECK: FAIL saved report differs", file=sys.stderr)
                return 1
        if args.json_report:
            print(json.dumps(report, indent=2, ensure_ascii=True))
        else:
            print(output.getvalue(), end="", file=sys.stderr)
            print("CLK006-CHECK: " + ("PASS" if result.wasSuccessful() else "FAIL"))
        return 0 if result.wasSuccessful() and result.testsRun else 1
    receipt = inspect_packet(args.packet)
    print(json.dumps(receipt, indent=2, ensure_ascii=True))
    return {"MANIFEST_COMPLETE_PENDING_CONTENT_REVIEW": 0, "PARTIAL": 2,
            "MISSING": 2, "REJECTED": 1}[receipt["intake_status"]]


if __name__ == "__main__":
    sys.exit(main())
