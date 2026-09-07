"""Adversarial tooling checks with real temporary Git worktrees, no research data."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/lane_control.py"
spec = importlib.util.spec_from_file_location("lane_control", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class LaneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="tect-lanes-")
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        mod.git(self.root, "init", "-b", "main")
        mod.git(self.root, "config", "user.email", "test@example.invalid")
        mod.git(self.root, "config", "user.name", "Lane test")
        (self.root / ".gitignore").write_bytes(b"internal/\n")
        (self.root / ".gitattributes").write_bytes(b"* -text\n")
        (self.root / "source.txt").write_bytes(b"base\n")
        mod.git(self.root, "add", ".")
        mod.git(self.root, "commit", "-m", "fixture")
        self.ctl = mod.Controller(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def lane(self, name):
        self.ctl.register(name, "task-" + name, "proof", self.root)
        return Path(self.ctl.provision(name)["workspace"])

    def checkpoint(self, workspace, name="result.txt"):
        (workspace / name).write_bytes(b"checkpoint\n")
        mod.git(workspace, "add", name)
        mod.git(workspace, "commit", "-m", "checkpoint")
        return mod.commit(workspace, "HEAD")

    def test_isolation_dirty_writer_and_duplicate_submission(self):
        a, b = self.lane("a"), self.lane("b")
        head = self.checkpoint(a)
        (a / "source.txt").write_bytes(b"continuous next work\n")
        request = self.ctl.submit("a", head)
        self.assertEqual(request, self.ctl.submit("a", head))
        frozen = Path(self.ctl.prepare(request["id"])["workspace"])
        self.assertEqual((frozen / "source.txt").read_bytes(), b"base\n")
        self.assertEqual((b / "source.txt").read_bytes(), b"base\n")
        self.assertEqual(mod.git(self.root, "status", "--porcelain"), "")
        self.assertEqual(len(self.ctl.requests()), 1)

    def test_outdated_request_does_not_hide_other_lanes(self):
        a, b = self.lane("a"), self.lane("b")
        one = self.ctl.submit("a", self.checkpoint(a))
        self.ctl.submit("b", self.checkpoint(b, "second.txt"))
        mod.git(self.root, "merge", "--ff-only", one["head"])
        self.ctl.receipt(one["id"])
        actions = self.ctl.tick()["actions"]
        self.assertEqual([(v["kind"], v["lane"]) for v in actions], [("REBASE_REVIEW_REQUIRED", "b")])
        with self.assertRaises(ValueError):
            self.ctl.receipt(self.ctl.requests()[1]["id"] if self.ctl.requests()[1]["lane"] == "b" else self.ctl.requests()[0]["id"])
        c = self.lane("c")
        self.ctl.submit("c", self.checkpoint(c, "third.txt"))
        self.assertIn("VALIDATE_CHECKPOINT", [v["kind"] for v in self.ctl.tick()["actions"]])

    def test_registration_rejects_shared_root_duplicate_task_and_traversal(self):
        a = self.lane("a")
        for kwargs in (
            dict(lane="bad", thread="task-b", role="paper", repo=self.root, workspace=self.root),
            dict(lane="bad", thread="task-a", role="paper", repo=self.root),
            dict(lane="bad", thread="task-b", role="paper", repo=self.root, workspace=a),
            dict(lane="../escape", thread="task-b", role="paper", repo=self.root),
            dict(lane="bad", thread="task-b", role="paper", repo=self.root, workspace=a, external=True),
        ):
            with self.assertRaises(ValueError):
                self.ctl.register(**kwargs)
        with self.assertRaises(ValueError):
            self.ctl.request("../registry")

    def test_stable_actions_changed_inputs_and_review_deadline(self):
        self.lane("a")
        path = self.root / "source.txt"
        data = self.ctl.registry()
        data["blockers"]["a:input"] = {"lane": "a", "inputs": [str(path)],
            "snapshot": mod.input_state([path]), "review_at": "2999-01-01T00:00:00Z", "reason": "bounded review"}
        mod.save(self.ctl.db, data)
        self.assertEqual(self.ctl.tick()["actions"], [])
        path.write_bytes(b"changed evidence\n")
        first = self.ctl.tick()["actions"]
        self.assertEqual(first, self.ctl.tick()["actions"])
        self.assertEqual(first[0]["kind"], "REVIEW_REQUIRED")
        data["blockers"]["a:input"]["snapshot"] = mod.input_state([path])
        data["blockers"]["a:input"]["review_at"] = "2000-01-01T00:00:00Z"
        mod.save(self.ctl.db, data)
        self.assertEqual(self.ctl.tick()["actions"][0]["kind"], "REVIEW_REQUIRED")
        with self.assertRaises(ValueError):
            mod.due("2026-09-07")

    def test_lock_contention_and_crash_release(self):
        path = self.ctl.home / "locks/controller.lock"
        code = "import sys; sys.path.insert(0,sys.argv[1]); from lane_control import lock; from pathlib import Path\nwith lock(Path(sys.argv[2])): print('acquired')"
        with mod.lock(path):
            blocked = subprocess.run([sys.executable, "-c", code, str(SCRIPT.parent), str(path)], capture_output=True)
            self.assertNotEqual(blocked.returncode, 0)
        resumed = subprocess.run([sys.executable, "-c", code, str(SCRIPT.parent), str(path)], capture_output=True)
        self.assertEqual(resumed.returncode, 0)

    def test_source_fingerprint_detects_edit_after_stage(self):
        path = self.root / "source.txt"
        path.write_bytes(b"checkpoint\n")
        mod.git(self.root, "add", "source.txt")
        before = mod.dirty_fingerprint(self.root)
        path.write_bytes(b"next checkpoint\n")
        self.assertNotEqual(before, mod.dirty_fingerprint(self.root))

    def test_dispatch_receipt_is_durable_without_poll_churn(self):
        self.ctl.register("a", "task-a", "proof", self.root)
        action = self.ctl.tick()["actions"][0]
        data = self.ctl.registry()
        data["deliveries"][action["id"]] = {"state": "dispatching", "note": "uncertain send"}
        mod.save(self.ctl.db, data)
        restarted = mod.Controller(self.root).tick()["actions"][0]
        self.assertEqual(restarted["id"], action["id"])
        self.assertEqual(restarted["delivery"], "dispatching")

    def test_promote_is_release_gated_and_rejects_dirty_canonical(self):
        a = self.lane("a")
        scripts = a / "verification/scripts"
        scripts.mkdir(parents=True)
        (scripts / "release_check.py").write_bytes(b"import sys; sys.exit(1)\n")
        (scripts / "verify_note_pdfs.py").write_bytes(b"print('NOTE-PDF: PASS (0 current notes)')\n")
        mod.git(a, "add", "verification")
        mod.git(a, "commit", "-m", "failing-check fixture")
        req = self.ctl.submit("a", "HEAD")
        baseline = mod.commit(self.root, "HEAD")
        with self.assertRaises(ValueError):
            self.ctl.promote(req["id"])
        self.assertEqual(mod.commit(self.root, "HEAD"), baseline)
        self.assertFalse((self.ctl.home / "receipts" / (req["id"] + ".json")).exists())

    def test_identical_committed_pdf_reuse_does_not_accept_changed_source(self):
        notes = self.root / "claims/TEST/notes"
        notes.mkdir(parents=True)
        source, pdf = notes / "note.tex.txt", notes / "note.pdf"
        source.write_bytes(b"source\n")
        pdf.write_bytes(b"pdf-fixture\n")
        mod.git(self.root, "add", "claims")
        mod.git(self.root, "commit", "-m", "PDF fixture")
        a = self.lane("a")
        target = a / "claims/TEST/notes/note.pdf"
        import os
        os.utime(target, (1, 1))
        self.assertEqual(mod.inherit_pdf_freshness(a, self.root), 1)
        (a / "claims/TEST/notes/note.tex.txt").write_bytes(b"different source\n")
        os.utime(target, (1, 1))
        self.assertEqual(mod.inherit_pdf_freshness(a, self.root), 0)
        self.assertEqual(target.stat().st_mtime, 1)

    def test_successful_promotion_and_dirty_canonical_refusal(self):
        a = self.lane("a")
        scripts = a / "verification/scripts"
        scripts.mkdir(parents=True)
        for name in ("release_check.py", "verify_note_pdfs.py"):
            (scripts / name).write_bytes(b"print('NOTE-PDF: PASS (0 current notes)')\n")
        mod.git(a, "add", "verification")
        mod.git(a, "commit", "-m", "passing checks fixture")
        req = self.ctl.submit("a", "HEAD")
        (self.root / "source.txt").write_bytes(b"busy integration workspace\n")
        with self.assertRaises(ValueError):
            self.ctl.promote(req["id"])
        (self.root / "source.txt").write_bytes(b"base\n")
        (a / "source.txt").write_bytes(b"research continues during validation\n")
        receipt = self.ctl.promote(req["id"])
        self.assertEqual(receipt["canonical_head"], req["head"])
        self.assertFalse(receipt["push_verified"])
        self.assertEqual(receipt, self.ctl.receipt(req["id"]))
        self.assertEqual((a / "source.txt").read_bytes(), b"research continues during validation\n")

    def test_reviewed_resubmission_preserves_old_request(self):
        a = self.lane("a")
        old = self.ctl.submit("a", self.checkpoint(a))
        (self.root / "later.txt").write_bytes(b"other lane\n")
        mod.git(self.root, "add", "later.txt")
        mod.git(self.root, "commit", "-m", "other lane")
        replacement_tree = self.lane("replay")
        head = self.checkpoint(replacement_tree)
        new = self.ctl.resubmit(old["id"], head)
        self.assertEqual(self.ctl.request(old["id"]), old)
        self.assertEqual(new["supersedes"], old["id"])
        self.assertEqual(len(self.ctl.tick()["actions"]), 1)
        self.assertEqual(self.ctl.tick()["actions"][0]["kind"], "VALIDATE_CHECKPOINT")


if __name__ == "__main__":
    unittest.main()
