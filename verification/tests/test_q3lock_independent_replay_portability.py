"""Real relocated-copy and adversarial tests; no theorem certification."""

import contextlib
import copy
import io
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path("verification/scripts/q3lock_independent_replay.py")


class IndependentReplayPortability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = runpy.run_path(str(ROOT / SCRIPT), run_name="portable_test")
        cls.payload = cls.module["build_payload"]()

    def test_environment_strings_are_not_scientific_payload(self):
        with mock.patch.object(sys, "version", "test-only runtime marker"), \
             mock.patch("platform.python_implementation", return_value="CPython"), \
             mock.patch("platform.platform", return_value="test-only OS marker"):
            self.assertEqual(self.module["build_payload"](), self.payload)
            environment = self.module["producer_environment"]()
        self.assertEqual(environment["python"], "test-only runtime marker")
        self.assertEqual(environment["platform"], "test-only OS marker")
        self.assertNotIn("producer", self.payload)

    def test_actual_relocated_exact_byte_dependency_copy(self):
        child = runpy.run_path(str(self.module["INDEPENDENT_SCRIPT"]),
                               run_name="portable_child_dependencies")
        paths = {ROOT / SCRIPT, self.module["INDEPENDENT_SCRIPT"],
                 self.module["HISTORICAL_RESULT"], self.module["EXP_MANIFEST"],
                 self.module["PAPER_MANIFEST"]}
        paths.update(child[name] for name in
                     ("MANIFEST", "CERTIFICATE", "STATUS", "PRIMARY_SCRIPT", "PRIMARY_RESULT"))
        manifest = json.loads(self.module["PAPER_MANIFEST"].read_text(encoding="utf-8"))
        paths.add(ROOT / manifest["manuscript"])
        with tempfile.TemporaryDirectory(prefix="q3lock relocated \u03b2-") as directory:
            target = Path(directory)
            for source in paths:
                destination = target / source.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                self.assertEqual(source.read_bytes(), destination.read_bytes())
            moved = runpy.run_path(str(target / SCRIPT), run_name="relocated_wrapper")
            self.assertNotEqual(moved["ROOT"], ROOT)
            self.assertEqual(moved["build_payload"](), self.payload)

    def test_relative_manuscript_locator(self):
        row = next(row for row in self.payload["assertions"]["rows"]
                   if row["name"] == "current manuscript exists")
        self.assertEqual(row["actual"], self.payload["files"]["current_manuscript"])
        self.assertFalse(Path(row["actual"]).is_absolute())

    def test_readonly_check_accepts_distinct_outer_environment(self):
        with tempfile.TemporaryDirectory(prefix="q3lock-check-") as directory:
            output = Path(directory) / "result.json"
            self.module["atomic_no_replace"](output, {
                "replay": self.payload,
                "producer_environment": {"python": "different recorded runtime"},
            })
            before = output.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(self.module["main"](["--check", "--output", str(output)]), 0)
            self.assertEqual(output.read_bytes(), before)

    def test_every_scientific_mutation_is_rejected(self):
        mutations = []
        for name, mutate in (
            ("child_count", lambda p: p["fresh_independent"].update(assertions_passed=-1)),
            ("child_hash", lambda p: p["fresh_independent"].update(payload_sha256="changed")),
            ("source_hash", lambda p: p["files"].update(current_manuscript_sha256="changed")),
            ("source_path", lambda p: p["files"].update(current_manuscript="different.tex")),
            ("wrapper_hash", lambda p: p["files"].update(wrapper_script_sha256="changed")),
            ("row", lambda p: p["assertions"]["rows"][0].update(actual="changed")),
            ("promotion", lambda p: p.update(claim_bearing=True)),
            ("unknown_field", lambda p: p.update(unlisted_science=None)),
            ("missing_field", lambda p: p.pop("source_separation")),
            ("old_embedded_producer", lambda p: p.update(producer={"python": "legacy"})),
        ):
            value = copy.deepcopy(self.payload)
            mutate(value)
            mutations.append((name, value))
        with tempfile.TemporaryDirectory(prefix="q3lock-mutations-") as directory:
            for name, value in mutations:
                with self.subTest(mutation=name):
                    output = Path(directory) / (name + ".json")
                    self.module["atomic_no_replace"](output, {"replay": value})
                    before = output.read_bytes()
                    with contextlib.redirect_stderr(io.StringIO()):
                        self.assertEqual(self.module["main"](["--check", "--output", str(output)]), 1)
                    self.assertEqual(output.read_bytes(), before)

    def test_changed_child_payload_rejected_before_packaging(self):
        changed = json.loads(self.module["HISTORICAL_RESULT"].read_text(encoding="utf-8"))
        changed["assertions"]["total"] += 1
        scope = self.module["build_payload"].__globals__
        with mock.patch.dict(scope, run_independent=lambda: (changed, "EXP-000782 INDEPENDENT PASS")):
            with self.assertRaisesRegex(AssertionError, "fresh payload equals frozen"):
                self.module["build_payload"]()

    def test_write_records_environment_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="q3lock-write-") as directory:
            output = Path(directory) / "result.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(self.module["main"](["--write-new", "--output", str(output)]), 0)
            stored = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(stored["replay"], self.payload)
            self.assertEqual(stored["producer_environment"], self.module["producer_environment"]())
            before = output.read_bytes()
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(self.module["main"](["--write-new", "--output", str(output)]), 1)
            self.assertEqual(output.read_bytes(), before)

    def test_optimized_python_rejected(self):
        completed = subprocess.run([sys.executable, "-O", str(ROOT / SCRIPT), "--self-test"],
                                   capture_output=True, text=True, timeout=30)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("assertions must be enabled", completed.stderr)


if __name__ == "__main__":
    unittest.main()
