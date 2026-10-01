"""Synthetic intake regression tests; fixtures are NEVER observational evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/tect_clk006_intake.py"
SPEC = importlib.util.spec_from_file_location("clk006", SCRIPT)
INTAKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INTAKE)


class IntakeTests(unittest.TestCase):
    records = []

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="tect-clk006-test-")
        self.addCleanup(self.scratch.cleanup)
        self.base = Path(self.scratch.name)
        self.path = self.base / "packet.json"
        self.template = json.loads((INTAKE.ROOT /
            "strategy/clock/TECT-CLK-006-intake-template-v1.json").read_text(encoding="utf-8"))
        self.packet = copy.deepcopy(self.template)
        raw = b"TEST_ONLY synthetic attachment. No scientific or permission authority.\n"
        (self.base / "fixture.txt").write_bytes(raw)
        self.packet["packet_id"] = "TEST_ONLY"
        self.packet["representation"] = "estimator_recipe"
        self.packet["attachments"] = [{"id": "fixture", "path": "fixture.txt",
            "sha256": INTAKE.digest(raw), "role": "analysis_support"}]
        self.packet["provenance"] = {
            "claimed_provider": "TEST_ONLY", "affiliation": "TEST_ONLY",
            "acquisition_channel": "synthetic self-test, not received evidence",
            "acquired_utc": "2026-10-01T00:00:00Z",
            "owner_evidence_ref": "fixture#TEST_ONLY",
            "reuse_permission": "review_only"}
        for entry in self.packet["owner_descriptions"].values():
            entry.update(state="provided", summary="TEST_ONLY declaration, not real evidence",
                         evidence_refs=["fixture#TEST_ONLY"])

    def check(self, name, expected, packet=None, raw=None):
        if raw is not None:
            self.path.write_bytes(raw)
        else:
            self.path.write_text(json.dumps(self.packet if packet is None else packet),
                                 encoding="utf-8", newline="\n")
        receipt = INTAKE.inspect_packet(self.path)
        self.assertEqual(expected, receipt["intake_status"], receipt)
        self.assertEqual("HOLD_FOR_EVIDENCE", receipt["scientific_status"])
        for key in ("empirical_use_authorized", "scientific_reentry_authorized",
                    "mainline_gate_changed", "publication_authorized"):
            self.assertIs(receipt[key], False)
        self.assertIs(receipt["manual_content_review_required"], True)
        self.records.append({"case": name, "expected": expected,
                             "actual": receipt["intake_status"], "science_hold": True})
        return receipt

    def test_complete_is_not_scientific_admission(self):
        result = self.check("complete_fields_not_evidence", "MANIFEST_COMPLETE_PENDING_CONTENT_REVIEW")
        self.assertEqual("unknown", result["researcher_mapping_state"])
        self.assertEqual("NOT_EVALUATED", result["new_template_calibration_capacity"])

    def test_template_and_missing(self):
        self.check("blank_template", "PARTIAL", self.template)
        result = INTAKE.inspect_packet(self.base / "absent.json")
        self.assertEqual("MISSING", result["intake_status"])
        self.assertIs(result["scientific_reentry_authorized"], False)
        self.records.append({"case": "absent_packet", "expected": "MISSING",
                             "actual": result["intake_status"], "science_hold": True})

    def test_missing_details(self):
        mutations = [
            ("missing_attachment", lambda p: p["attachments"][0].update(path="absent.txt")),
            ("unknown_provider", lambda p: p["provenance"].update(claimed_provider=None)),
            ("unknown_reuse", lambda p: p["provenance"].update(reuse_permission="unknown")),
            ("not_retained", lambda p: p["owner_descriptions"]["nuisance_design"].update(state="not_retained")),
            ("not_applicable_no_bypass", lambda p: p["owner_descriptions"]["nuisance_design"].update(state="not_applicable_with_reason")),
            ("missing_summary", lambda p: p["owner_descriptions"]["nuisance_design"].update(summary=None)),
            ("missing_ref", lambda p: p["owner_descriptions"]["nuisance_design"].update(evidence_refs=[])),
        ]
        for name, change in mutations:
            with self.subTest(name=name):
                packet = copy.deepcopy(self.packet)
                change(packet)
                self.check(name, "PARTIAL", packet)

    def test_scope_types_and_reference_rejections(self):
        mutations = [
            ("unknown_top", lambda p: p.update(empirical_use_authorized=True)),
            ("wrong_model", lambda p: p["target"].update(model_status="REPLACED")),
            ("wrong_doi", lambda p: p["target"].update(publication_doi="other")),
            ("wrong_time", lambda p: p["target"].update(time_status="RESCALED")),
            ("false_holdout", lambda p: p["target"].update(data_role="HOLDOUT")),
            ("nested_unknown", lambda p: p["provenance"].update(certified=True)),
            ("authority_substitution", lambda p: p["authority_refs"].clear()),
            ("bool_as_string", lambda p: p["provenance"].update(claimed_provider=True)),
            ("bad_timestamp", lambda p: p["provenance"].update(acquired_utc="not-a-dateZ")),
            ("non_utc", lambda p: p["provenance"].update(acquired_utc="2026-10-01T00:00:00+09:00")),
            ("unsupported_representation", lambda p: p.update(representation="new_fit")),
            ("unknown_entry", lambda p: p["owner_descriptions"]["data_dependence"].update(extra="value")),
            ("invalid_entry_state", lambda p: p["owner_descriptions"]["data_dependence"].update(state="certified")),
            ("bad_refs_type", lambda p: p["owner_descriptions"]["data_dependence"].update(evidence_refs="fixture#x")),
            ("dangling_ref", lambda p: p["provenance"].update(owner_evidence_ref="absent#x")),
            ("empty_locator", lambda p: p["provenance"].update(owner_evidence_ref="fixture#")),
            ("bad_hash", lambda p: p["attachments"][0].update(sha256="0" * 64)),
            ("invalid_hash_syntax", lambda p: p["attachments"][0].update(sha256=False)),
            ("duplicate_id", lambda p: p["attachments"].append(dict(p["attachments"][0], path="other.txt"))),
            ("case_alias_path", lambda p: p["attachments"].append(dict(p["attachments"][0], id="other", path="FIXTURE.txt"))),
            ("unknown_role", lambda p: p["attachments"][0].update(role="trusted_science")),
            ("unexpected_attachment_field", lambda p: p["attachments"][0].update(url="https://invalid.example/")),
        ]
        for name, change in mutations:
            with self.subTest(name=name):
                packet = copy.deepcopy(self.packet)
                change(packet)
                self.check(name, "REJECTED", packet)

    def test_unsafe_paths(self):
        for path in ("../fixture.txt", "/fixture.txt", "C:/fixture.txt", "C:fixture.txt",
                     "//server/share", "fixture.txt:stream", "sub\\fixture.txt", "./fixture.txt",
                     "sub//fixture.txt", "NUL.txt", "fixture.txt.", "fixture.txt "):
            with self.subTest(path=path):
                packet = copy.deepcopy(self.packet)
                packet["attachments"][0]["path"] = path
                self.check("path:" + path, "REJECTED", packet)

    def test_malformed_json(self):
        for name, raw in (("duplicate_json_keys", b'{"x":1,"x":2}'),
                          ("nonfinite_json", b'{"x":NaN}'),
                          ("invalid_utf8", b'\xff'), ("array_root", b'[]'),
                          ("oversized_integer", ('{"packet_id":' + '9' * 5000 + '}').encode())):
            self.check(name, "REJECTED", raw=raw)

    def test_representation_and_permission_do_not_promote(self):
        policy = INTAKE.load_policy()
        for representation in policy["representations"]:
            packet = copy.deepcopy(self.packet)
            packet["representation"] = representation
            packet["provenance"]["reuse_permission"] = "publicly_redistributable"
            self.check("representation:" + representation,
                       "MANIFEST_COMPLETE_PENDING_CONTENT_REVIEW", packet)

    def test_symlink_rejection_if_host_permits(self):
        link = self.base / "linked.txt"
        try:
            link.symlink_to(self.base / "fixture.txt")
        except OSError as exc:
            self.skipTest("host does not allow symlink creation: " + str(exc))
        self.packet["attachments"][0]["path"] = "linked.txt"
        self.check("symlink_rejection", "REJECTED")

    def test_reparse_guard_mock(self):
        original = Path.lstat
        def reparse(path, *args, **kwargs):
            if path.name == "fixture.txt":
                return SimpleNamespace(st_mode=0o100644, st_file_attributes=0x400)
            return original(path, *args, **kwargs)
        with patch.object(Path, "lstat", reparse):
            self.check("mock_reparse_rejection", "REJECTED")


if __name__ == "__main__":
    unittest.main()
