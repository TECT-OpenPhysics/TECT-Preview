"""Coordinate isolated research lanes; never infer a scientific verdict.

Only provisioning and prepare create Git worktrees. All other writes are P0
operational JSON with atomic UTF-8/LF replacement under an OS-held lock.
No shell execution, automatic merge, reset, deletion, force push or claim edits.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

__version__ = "1.0.0"
GIT_TIMEOUT = 120  # Tooling timeout, not a research budget.


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, sort_keys=True, indent=2)
            stream.write("\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def read(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


@contextmanager
def lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                            encoding="utf-8", errors="strict", timeout=GIT_TIMEOUT)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def slug(value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", value):
        raise ValueError("Expected a lowercase lane/key slug")
    return value


def commit(repo, ref):
    # Never interpret user-supplied revisions as Git options.
    if not re.fullmatch(r"[a-fA-F0-9]{7,40}|HEAD", ref):
        raise ValueError("Expected HEAD or a hexadecimal commit")
    return git(repo, "rev-parse", "--verify", ref + "^{commit}")


def canonical(path):
    return Path(path).resolve()


def repo_root(path):
    path = canonical(path)
    if canonical(git(path, "rev-parse", "--show-toplevel")) != path:
        raise ValueError("Workspace must be the actual Git checkout root")
    return path


def common(repo):
    return canonical(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))


def input_state(paths):
    result = {}
    for name in paths:
        path = canonical(name)
        result[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return result


def due(timestamp):
    date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ValueError("Review time must include a UTC offset")
    return date <= datetime.now(timezone.utc)


def dirty_fingerprint(repo):
    paths = set(git(repo, "diff", "--name-only", "-z", "HEAD").split("\0"))
    paths.update(git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0"))
    contents = {}
    for name in sorted(paths - {""}):
        path = Path(repo) / name
        contents[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return digest([commit(repo, "HEAD"), contents, git(repo, "diff", "--cached", "--raw", "-z")])


def inherit_pdf_freshness(destination, reference):
    """Preserve verified pair freshness across checkout, without changing bytes.

    Only an exact source AND PDF byte match to an already fresh reference pair
    qualifies. Changed source, missing PDF and stale reference are never blessed.
    """
    count = 0
    for source in (Path(destination) / "claims").glob("**/notes/*.tex.txt"):
        pdf = source.with_name(source.name[:-len(".tex.txt")] + ".pdf")
        ref_source = Path(reference) / source.relative_to(destination)
        ref_pdf = Path(reference) / pdf.relative_to(destination)
        if not all(p.is_file() for p in (pdf, ref_source, ref_pdf)):
            continue
        if ref_pdf.stat().st_mtime_ns < ref_source.stat().st_mtime_ns:
            continue
        if source.read_bytes() != ref_source.read_bytes() or pdf.read_bytes() != ref_pdf.read_bytes():
            continue
        if pdf.stat().st_mtime_ns < source.stat().st_mtime_ns:
            stamp = source.stat().st_mtime_ns
            os.utime(pdf, ns=(stamp, stamp))
            count += 1
    return count


class Controller:
    def __init__(self, root):
        self.root = repo_root(root)
        self.home = self.root / "internal/lane-control"
        self.db = self.home / "registry.json"

    def registry(self):
        return read(self.db, {"version": 1, "lanes": {}, "blockers": {}, "deliveries": {}})

    def requests(self):
        return [read(p) for p in sorted((self.home / "requests").glob("*.json"))]

    def register(self, lane, thread, role, repo, workspace=None, external=False):
        slug(lane)
        repo = repo_root(repo)
        if external and common(repo) == common(self.root):
            raise ValueError("External lane must have an independent Git repository")
        if not external and common(repo) != common(self.root):
            raise ValueError("Use --external for an independent repository")
        workspace = repo_root(workspace) if workspace else None
        if external and workspace != repo:
            raise ValueError("External lane must name its independent checkout")
        if workspace and common(workspace) != common(repo):
            raise ValueError("Workspace belongs to a different repository")
        if workspace == self.root:
            raise ValueError("Canonical checkout is reserved for integration")
        data = self.registry()
        existing = data["lanes"].get(lane)
        if existing:
            if (existing["thread"] == thread and existing["repo"] == str(repo)
                    and existing["role"] == role and existing["external"] == external
                    and (not workspace or existing["workspace"] == str(workspace))):
                return existing
            raise ValueError("Existing lane differs; reconcile explicitly before replacing")
        for other in data["lanes"].values():
            if thread == other["thread"]:
                raise ValueError("Task already owns another lane")
            if workspace and other["workspace"]:
                prior = canonical(other["workspace"])
                if workspace == prior or workspace in prior.parents or prior in workspace.parents:
                    raise ValueError("Writer workspaces must be disjoint")
        record = {"id": lane, "thread": thread, "role": role, "repo": str(repo),
                  "external": external, "workspace": str(workspace) if workspace else None,
                  "base": commit(repo, "HEAD"), "registered_at": now()}
        data["lanes"][lane] = record
        save(self.db, data)
        return record

    def provision(self, lane):
        data = self.registry()
        record = data["lanes"][lane]
        if record["workspace"]:
            repo_root(record["workspace"])
            return record
        destination = self.root / "internal/lane-workspaces" / slug(lane)
        branch = "codex/lane-" + lane
        if destination.exists():
            # Recover a crash between successful worktree creation and receipt.
            repo_root(destination)
            if common(destination) != common(self.root) or git(destination, "branch", "--show-current") != branch:
                raise ValueError("Existing destination is not the expected worktree")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            git(self.root, "worktree", "add", "-b", branch, str(destination), record["base"])
        inherit_pdf_freshness(destination, self.root)
        record["workspace"] = str(destination)
        save(self.db, data)
        return record

    def submit(self, lane, head):
        data = self.registry()
        record = data["lanes"][lane]
        if record["external"]:
            raise ValueError("External repository checkpoints use their own release/push policy")
        workspace = repo_root(record["workspace"])
        if common(workspace) != common(self.root):
            raise ValueError("Repository identity changed")
        head = commit(workspace, head)
        base = record["base"]
        git(workspace, "merge-base", "--is-ancestor", base, head)
        if base == head:
            raise ValueError("No committed checkpoint beyond the registered base")
        key = digest([lane, base, head])[:24]
        path = self.home / "requests" / (key + ".json")
        if path.exists():
            return read(path)
        if any(r["lane"] == lane and not (self.home / "receipts" / (r["id"] + ".json")).exists()
               for r in self.requests()):
            raise ValueError("One pending checkpoint per lane; research may continue")
        record = {"id": key, "lane": lane, "base": base, "head": head, "created_at": now(),
                  "paths": git(workspace, "diff", "--name-only", base, head).splitlines()}
        save(path, record)
        return record

    def tick(self):
        data = self.registry()
        actions = []
        target = commit(self.root, "HEAD")
        for lane in data["lanes"].values():
            if not lane["workspace"]:
                actions.append({"kind": "PROVISION", "lane": lane["id"]})
        for request in sorted(self.requests(), key=lambda r: (r["created_at"], r["id"])):
            if (self.home / "receipts" / (request["id"] + ".json")).exists():
                continue
            # Also recover an interrupted receipt after a successful promotion.
            try:
                git(self.root, "merge-base", "--is-ancestor", request["head"], target)
                kind = "RECONCILE_RECEIPT"
            except ValueError:
                kind = "VALIDATE_CHECKPOINT" if target == request["base"] else "REBASE_REVIEW_REQUIRED"
            actions.append({"kind": kind, "lane": request["lane"],
                            "request": request["id"], "target": target})
        for key, blocker in data["blockers"].items():
            current = input_state(blocker["inputs"])
            if current != blocker["snapshot"] or due(blocker["review_at"]):
                actions.append({"kind": "REVIEW_REQUIRED", "lane": blocker["lane"], "blocker": key,
                                "fingerprint": digest([current, blocker["review_at"]]), "reason": blocker["reason"]})
        for action in actions:
            action["id"] = digest(action)[:24]
            action["delivery"] = data["deliveries"].get(action["id"], {}).get("state", "pending")
        status = {"version": 1, "checked_at": now(), "canonical_head": target,
                  "lanes": data["lanes"], "actions": actions}
        save(self.home / "status.json", status)
        return status

    def prepare(self, key):
        request = self.request(key)
        if commit(self.root, "HEAD") != request["base"]:
            raise ValueError("REBASE_REVIEW_REQUIRED for this request only")
        destination = self.root / "internal/lane-workspaces" / ("validation-" + key)
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            git(self.root, "worktree", "add", "--detach", str(destination), request["head"])
        repo_root(destination)
        if common(destination) != common(self.root) or commit(destination, "HEAD") != request["head"]:
            raise ValueError("Validation snapshot identity changed")
        if git(destination, "status", "--porcelain"):
            raise ValueError("Validation snapshot is dirty; owner review required")
        inherit_pdf_freshness(destination, self.root)
        source_lane = self.registry()["lanes"][request["lane"]]
        inherit_pdf_freshness(destination, Path(source_lane["workspace"]))
        return {"request": key, "workspace": str(destination), "head": request["head"],
                "next": "Run release/PDF/scope checks here; only then promote under the release lock"}

    def request(self, key):
        if not re.fullmatch(r"[a-f0-9]{24}", key):
            raise ValueError("Invalid request ID")
        value = read(self.home / "requests" / (key + ".json"))
        if not value:
            raise ValueError("Unknown request")
        return value

    def receipt(self, key):
        request = self.request(key)
        existing = read(self.home / "receipts" / (key + ".json"))
        if existing:
            return existing
        head = commit(self.root, "HEAD")
        git(self.root, "merge-base", "--is-ancestor", request["head"], head)
        record = {"request": key, "integrated_at": now(), "canonical_head": head,
                  "push_verified": False}
        save(self.home / "receipts" / (key + ".json"), record)
        data = self.registry()
        data["lanes"][request["lane"]]["base"] = request["head"]
        save(self.db, data)
        return record

    def resubmit(self, key, head):
        """Replace a reviewed stale checkpoint without editing its history."""
        previous = self.request(key)
        data = self.registry()
        lane = data["lanes"][previous["lane"]]
        base = commit(self.root, "HEAD")
        head = commit(self.root, head)
        git(self.root, "merge-base", "--is-ancestor", base, head)
        if base == head:
            raise ValueError("Replacement must contain a reviewed change")
        if (self.home / "receipts" / (key + ".json")).exists():
            raise ValueError("Original request is already terminal; inspect its receipt")
        replacement = digest([previous["lane"], base, head])[:24]
        if replacement == key:
            raise ValueError("Replacement is unchanged")
        record = {"id": replacement, "lane": previous["lane"], "base": base, "head": head,
                  "created_at": now(), "supersedes": key,
                  "paths": git(self.root, "diff", "--name-only", base, head).splitlines()}
        save(self.home / "requests" / (replacement + ".json"), record)
        save(self.home / "receipts" / (key + ".json"),
             {"state": "superseded", "replacement": replacement, "at": now(), "integrated": False})
        lane["base"] = base
        save(self.db, data)
        return record

    def promote(self, key):
        # Source lanes keep running; validation sees only the immutable commit.
        with lock(self.home / "locks/release.lock"):
            snapshot = self.prepare(key)
            request = self.request(key)
            workspace = Path(snapshot["workspace"])
            for script, flags in (("release_check.py", []),
                                  ("verify_note_pdfs.py", ["--check", "--strict"])):
                run = subprocess.run([sys.executable, "-B", "-X", "utf8",
                                      str(workspace / "verification/scripts" / script), *flags],
                                     cwd=workspace, capture_output=True, encoding="utf-8",
                                     errors="replace", timeout=900)  # Tooling limit.
                save(self.home / "checks" / (key + "-" + script + ".json"),
                     {"head": request["head"], "exit_code": run.returncode,
                      "output": run.stdout, "error": run.stderr, "checked_at": now()})
                if run.returncode or (script == "verify_note_pdfs.py" and "NOTE-PDF: PASS (" not in run.stdout):
                    raise ValueError("Checkpoint check failed: " + script + "; see internal/lane-control/checks")
            if commit(self.root, "HEAD") != request["base"] or git(self.root, "status", "--porcelain"):
                raise ValueError("Canonical base/index changed; no promotion")
            if commit(workspace, "HEAD") != request["head"] or git(workspace, "status", "--porcelain"):
                raise ValueError("Validation snapshot changed; no promotion")
            git(self.root, "merge", "--ff-only", request["head"])
            with lock(self.home / "locks/controller.lock"):
                return self.receipt(key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    sub = parser.add_subparsers(dest="command", required=True)
    reg = sub.add_parser("register")
    reg.add_argument("--lane", required=True)
    reg.add_argument("--thread", required=True)
    reg.add_argument("--role", choices=["proof", "paper", "review", "tooling"], required=True)
    reg.add_argument("--repo", required=True)
    reg.add_argument("--workspace")
    reg.add_argument("--external", action="store_true")
    prov = sub.add_parser("provision")
    prov.add_argument("--lane", required=True)
    submit = sub.add_parser("submit")
    submit.add_argument("--lane", required=True)
    submit.add_argument("--head", default="HEAD")
    sub.add_parser("tick")
    sub.add_parser("fingerprint")
    for command in ("prepare", "receipt", "promote"):
        request = sub.add_parser(command)
        request.add_argument("--request", required=True)
    resubmit = sub.add_parser("resubmit")
    resubmit.add_argument("--request", required=True)
    resubmit.add_argument("--head", required=True)
    block = sub.add_parser("block")
    block.add_argument("--lane", required=True)
    block.add_argument("--key", required=True)
    block.add_argument("--input", action="append", required=True)
    block.add_argument("--review-at", required=True)
    block.add_argument("--reason", required=True)
    review = sub.add_parser("review")
    review.add_argument("--key", required=True)
    review.add_argument("--review-at", required=True)
    review.add_argument("--reason", required=True)
    ack = sub.add_parser("ack")
    ack.add_argument("--action", required=True)
    ack.add_argument("--state", choices=["dispatching", "sent"], required=True)
    ack.add_argument("--note", required=True)
    args = parser.parse_args()
    try:
        ctl = Controller(args.root)
        if args.command == "promote":
            # Expensive validation must not hold the registry/submission lock.
            print(json.dumps(ctl.promote(args.request), ensure_ascii=True, indent=2))
            return 0
        with lock(ctl.home / "locks/controller.lock"):
            if args.command == "register":
                result = ctl.register(args.lane, args.thread, args.role, args.repo, args.workspace, args.external)
            elif args.command == "provision":
                result = ctl.provision(args.lane)
            elif args.command == "submit":
                result = ctl.submit(args.lane, args.head)
            elif args.command == "resubmit":
                result = ctl.resubmit(args.request, args.head)
            elif args.command == "tick":
                result = ctl.tick()
            elif args.command == "fingerprint":
                print(dirty_fingerprint(ctl.root))
                return 0
            elif args.command in ("prepare", "receipt", "promote"):
                result = getattr(ctl, args.command)(args.request)
            else:
                data = ctl.registry()
                if args.command == "ack":
                    known = {a["id"] for a in ctl.tick()["actions"]}
                    if args.action not in known:
                        raise ValueError("Action no longer current; reconcile live state")
                    result = {"state": args.state, "note": args.note, "at": now()}
                    data["deliveries"][args.action] = result
                elif args.command == "block":
                    data["lanes"][args.lane]
                    due(args.review_at)
                    key = args.lane + ":" + slug(args.key)
                    if key in data["blockers"]:
                        raise ValueError("Use review to update an existing blocker")
                    result = {"lane": args.lane, "inputs": list(input_state(args.input)),
                              "snapshot": input_state(args.input), "review_at": args.review_at,
                              "reason": args.reason}
                    data["blockers"][key] = result
                else:
                    due(args.review_at)
                    result = data["blockers"][args.key]
                    result.update(snapshot=input_state(result["inputs"]), review_at=args.review_at,
                                  reason=args.reason)
                save(ctl.db, data)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print("LANE-CONTROL: REVIEW_REQUIRED: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
