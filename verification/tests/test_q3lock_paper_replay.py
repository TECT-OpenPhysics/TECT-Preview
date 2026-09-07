"""Adversarial tooling tests; no mathematical theorem acceptance."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import io
import json
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/q3lock_paper_replay.py"
SPEC = spec_from_file_location("paper_replay", SCRIPT)
REPLAY = module_from_spec(SPEC)
SPEC.loader.exec_module(REPLAY)


class ReplaySafetyTests(unittest.TestCase):
    def test_embedded_guards(self):
        rows = REPLAY.guard_self_tests()
        self.assertTrue(rows)
        self.assertTrue(all(row["pass"] for row in rows))

    def test_only_declared_document_hash_addition_is_allowed(self):
        old = {"source_hashes": {}}
        new = {"source_hashes": {"document": "new"}}
        self.assertEqual(len(REPLAY.require_document_only(old, new, {"document": "new"})), 1)
        with self.assertRaises(ValueError):
            REPLAY.require_document_only(new, old, {"document": "new"})
        with self.assertRaises(ValueError):
            REPLAY.require_document_only(old, new, {})

    def test_deep_assertion_is_not_a_document_change(self):
        old = {"nested": {"source_hashes": {"document": "old"}, "assertions": [True]}}
        new = deepcopy(old)
        new["nested"]["assertions"] = [False]
        with self.assertRaises(ValueError):
            REPLAY.require_document_only(old, new, {"document": "old"})

    def test_removed_key_and_added_null_fail(self):
        for before, after in (({"key": None}, {}), ({}, {"key": None})):
            with self.assertRaises(ValueError):
                REPLAY.require_document_only(before, after, {})

    def test_unlisted_source_cannot_be_whitelisted_by_its_leaf_name(self):
        old = {"source_hashes": {"code/document": "old"}}
        new = {"source_hashes": {"code/document": "new"}}
        with self.assertRaises(ValueError):
            REPLAY.require_document_only(old, new, {"document": "new"})

    def test_scope_promotion_and_pdf_release_are_rejected(self):
        valid = {"claim_status": {"result_id": "R-497", "tier": "T0",
                                 "claim_bearing": False, "publication_status": "RESEARCH_ONLY"},
                 "status": "UNFROZEN_CONTENT_REVIEW", "pdf_status": "DEFERRED"}
        REPLAY.require_draft_scope(valid)
        for field, value in (("tier", "T6"), ("claim_bearing", True)):
            mutant = deepcopy(valid)
            mutant["claim_status"][field] = value
            with self.assertRaises(ValueError):
                REPLAY.require_draft_scope(mutant)
        mutant = {**valid, "pdf_status": "READY"}
        with self.assertRaises(ValueError):
            REPLAY.require_draft_scope(mutant)

    def test_new_publication_is_complete_and_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            payload = {"fixture": "complete"}
            REPLAY.write_new(target, payload)
            before = target.read_bytes()
            self.assertEqual(json.loads(before), payload)
            with self.assertRaises(FileExistsError):
                REPLAY.write_new(target, {"fixture": "replacement"})
            self.assertEqual(target.read_bytes(), before)
            self.assertEqual(list(Path(folder).glob("*.tmp")), [])

    def test_concurrent_publication_has_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            def publish(value):
                try:
                    REPLAY.write_new(target, {"fixture": value})
                    return True
                except FileExistsError:
                    return False
            with ThreadPoolExecutor(max_workers=2) as executor:
                outcomes = list(executor.map(publish, ("first", "second")))
            self.assertEqual(outcomes.count(True), 1)
            self.assertIn(json.loads(target.read_text())["fixture"], ("first", "second"))
            self.assertEqual(list(Path(folder).glob("*.tmp")), [])

    def test_default_check_does_not_write_missing_stale_or_matching_result(self):
        payload = {"canonical_replay": [], "manuscript_replay": [],
                   "historical_records_preserved": 0}
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            with patch.object(REPLAY, "build_payload", return_value=payload) as builder:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(REPLAY.main(["--output", str(target)]), 1)
                    builder.assert_not_called()
                    self.assertFalse(target.exists())
                    REPLAY.write_new(target, {"stale": True})
                    before = target.read_bytes()
                    self.assertEqual(REPLAY.main(["--output", str(target)]), 1)
                    self.assertEqual(target.read_bytes(), before)
                    fresh = Path(folder) / "fresh.json"
                    REPLAY.write_new(fresh, payload)
                    before = fresh.read_bytes()
                    self.assertEqual(REPLAY.main(["--output", str(fresh)]), 0)
                    self.assertEqual(fresh.read_bytes(), before)

    def test_existing_output_refused_before_any_builder_execution(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            REPLAY.write_new(target, {"fixture": "history"})
            before = target.read_bytes()
            with patch.object(REPLAY, "build_payload") as builder, redirect_stderr(io.StringIO()):
                self.assertEqual(REPLAY.main(["--write-new", "--output", str(target)]), 1)
                builder.assert_not_called()
            self.assertEqual(target.read_bytes(), before)

    def test_default_target_is_selected_by_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            relative = REPLAY.RUNS + "fixture/result.json"
            REPLAY.write_new(root / (REPLAY.PAPER + "verification/package-manifest.json"),
                             {"tooling_checkpoint": relative})
            with patch.object(REPLAY, "ROOT", root):
                self.assertEqual(REPLAY.default_output(), (root / relative).resolve())

    def test_manifest_target_cannot_escape_public_runs(self):
        for relative in ("../escape.json", "/absolute.json", "C:/outside.json",
                         REPLAY.RUNS + "../escape.json", "publish/result.json",
                         REPLAY.RUNS + "fixture/result.txt"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                REPLAY.write_new(root / (REPLAY.PAPER + "verification/package-manifest.json"),
                                 {"tooling_checkpoint": relative})
                with patch.object(REPLAY, "ROOT", root), self.assertRaises(ValueError):
                    REPLAY.default_output()

    def test_missing_dependency_is_clear_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "result.json"
            REPLAY.write_new(target, {"fixture": "history"})
            before = target.read_bytes()
            errors = io.StringIO()
            with patch.object(REPLAY, "build_payload", side_effect=ImportError("sympy")):
                with redirect_stderr(errors):
                    self.assertEqual(REPLAY.main(["--output", str(target)]), 1)
            self.assertIn("missing research dependency", errors.getvalue())
            self.assertNotIn("Traceback", errors.getvalue())
            self.assertEqual(target.read_bytes(), before)

    def test_r1_archive_matches_original_result_not_current_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = "fixture/source.py"
            archive = str(Path(REPLAY.R1).parent / "sources/fixture.txt").replace("\\", "/")
            REPLAY.write_new(root / archive, {"fixture": "original bytes"})
            expected = REPLAY.digest(root / archive)
            REPLAY.write_new(root / REPLAY.R1, {"source_hashes": {source: expected}})
            REPLAY.write_new(root / REPLAY.R1_SOURCES, {
                "checkpoint": REPLAY.R1,
                "files": [{"source": source, "archive": archive, "sha256": expected}]})
            with patch.object(REPLAY, "ROOT", root):
                hashes = REPLAY.preserved_r1_sources()
                self.assertEqual(hashes[archive], expected)
                # The current source need not be the archived historical source.
                self.assertFalse((root / source).exists())
                with patch.object(REPLAY, "digest", return_value="fixture-wrong-hash"):
                    with self.assertRaises(ValueError):
                        REPLAY.preserved_r1_sources()

    def test_optimized_python_is_rejected(self):
        process = subprocess.run([sys.executable, "-O", str(SCRIPT), "--self-test"],
                                 text=True, capture_output=True, check=False)
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("assertion-enabled", process.stderr)


if __name__ == "__main__":
    unittest.main()
