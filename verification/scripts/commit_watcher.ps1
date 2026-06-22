# =============================================================================
# commit_watcher.ps1 - Windows-side auto-commit daemon for the TECT repository
# Version: 1.6.0 -- first issued 2026-06-05; this version issued 2026-06-22
#   1.6.0 (2026-06-22): `git add` resilient to Google-Drive sync races
#       (--ignore-errors + 5x retry with 3s settle); .gitignore extended to
#       all Drive/transient artifacts so the operator need not pause sync.
#   1.5.0 (2026-06-12): commit message passed via temp file + `git commit -F`
#     instead of inline `-m $msg`. Root cause of the 2026-06-12 failure: a
#     queued message containing embedded double quotes ('"3M g_3"') broke
#     PowerShell's native-argument quoting, so git received the message tail
#     as a PATHSPEC ("error: pathspec ... did not match any file(s)") and the
#     commit failed with the queue left intact. -F is robust against quotes,
#     newlines and special characters; the temp file lives inside internal/
#     (P0, gitignored) and is removed after the attempt.
#   1.4.0 (2026-06-10): pre-commit NOTE-PDF build -- run verify_note_pdfs.py
#     --build before staging, so every CURRENT note enters history with a fresh
#     PDF (operator-side, no sandbox 44s timeout). Closes the recurring missing-
#     PDF defect systemically. release_check/doctor report it as an advisory.
#   1.3.0 (2026-06-09): pre-commit RELEASE gate -- run release_check.py before
#     every commit; refuse (queue left intact) on failure. Closes the commit-
#     time enforcement gap: no stale/broken tree can enter history. Portable
#     because the watcher is a tracked file (unlike .git/hooks). The gate list
#     is single-sourced in gates.py (doctor + release_check + watcher agree).
#   1.2.0 (2026-06-07): BATCH-DRAIN (systemic fix for the recurring stuck-queue).
#     The whole pending queue is now committed as ONE commit with a COMBINED
#     message, instead of one commit per JSON. Root cause of the recurrence:
#     `git add --all` per JSON meant that with N>1 pending, the first commit
#     swept ALL changes and the remaining JSONs hit "nothing to commit"
#     (exit 1) -> stranded in the queue forever, and their messages were lost
#     from history (content folded under the oldest message). This happened
#     repeatedly (2026-06-06 / 2026-06-07). Batch-drain eliminates it:
#       - all pending JSONs are staged once (`git add --all`) and committed once
#         with a numbered combined message (per-entry detail stays in CHANGELOG);
#       - if there is NO staged diff (content already committed by an earlier
#         run), the pending JSONs are moved to done/ with an EMPTYDIFF- marker
#         instead of being stranded;
#       - all drained JSONs move to done/ only on commit success (rc=0).
#   1.1.2 (2026-06-06): git add --all via call operator (-A token mangled).
#   1.1.1 (2026-06-06): FIX git add -A splat bug; move to done/ only on rc=0.
#   1.1.0 (2026-06-06): pre-commit JSON-integrity gate.
#
# WHY: the AI collaborator's sandbox cannot run git (the mount blocks the
# unlink operations git requires), so the AI writes a commit-request JSON into
# internal/commit-queue/ (gitignored, P0) and this operator-side script commits
# with the maintainer signature.
#
# USAGE (from the repository root):
#   .\verification\scripts\commit_watcher.ps1            # watch loop (10 s)
#   .\verification\scripts\commit_watcher.ps1 -Once      # drain queue once
#
# Request format: { "message": "<commit message>", "paths": ["-A"] }
# (paths is intentionally ignored; the whole tree is staged.)
# SAFETY: refuses to run outside a git worktree; refuses empty messages;
# never pushes (push stays a manual operator action).
# =============================================================================
param([switch]$Once)

$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repo
if (-not (Test-Path (Join-Path $repo ".git"))) {
    Write-Error "Not a git repository root: $repo"; exit 1
}
$queue = Join-Path $repo "internal\commit-queue"
$done  = Join-Path $queue "done"
New-Item -ItemType Directory -Force -Path $done | Out-Null
Write-Host "[commit-watcher] watching $queue (Ctrl+C to stop)"

function Move-ToDone($file, $prefix) {
    $stamp = (Get-Date -Format "yyyyMMdd-HHmmss")
    Move-Item $file.FullName (Join-Path $done "$stamp-$prefix$($file.Name)")
}

function Process-Queue {
    $pending = @(Get-ChildItem -Path $queue -Filter *.json -File | Sort-Object Name)
    if ($pending.Count -eq 0) { return }

    # collect (file, message) pairs; drop empty-message requests (left in queue)
    $items = @()
    foreach ($f in $pending) {
        $req = Get-Content $f.FullName -Raw | ConvertFrom-Json
        if (-not $req.message -or $req.message.Trim().Length -eq 0) {
            Write-Warning "[commit-watcher] skip (empty message): $($f.Name) -- left in queue."
            continue
        }
        $items += [pscustomobject]@{ File = $f; Message = $req.message }
    }
    if ($items.Count -eq 0) { return }

    # pre-commit NOTE-PDF build: every current note must enter history with a fresh
    # PDF. Build missing/stale ones now (operator-side; no sandbox timeout).
    & python verification/scripts/verify_note_pdfs.py --build | Out-Host

    # stage the whole tree; resilient to Google-Drive sync races. Drive briefly
    # creates then deletes temp files (e.g. .tmp.driveupload/*) during sync; if one
    # vanishes mid-add, git errors. .gitignore skips the known temp dirs, and this
    # retry lets Drive settle so the operator need not pause sync manually.
    $added = $false
    for ($try = 1; $try -le 5; $try++) {
        & git add --all --ignore-errors
        if ($LASTEXITCODE -eq 0) { $added = $true; break }
        Write-Warning "[commit-watcher] git add transient error (attempt $try/5; likely Google Drive sync) -- retrying in 3s..."
        Start-Sleep -Seconds 3
    }
    if (-not $added) {
        Write-Warning "[commit-watcher] git add --all still failing after 5 tries; queue left intact. Briefly pause Google Drive sync, then re-run -Once."
        return
    }

    # pre-commit JSON-integrity gate: refuse if any staged .json fails to parse
    $bad = @()
    git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.json$' } | ForEach-Object {
        if (Test-Path $_) {
            & python -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" $_ 2>$null
            if ($LASTEXITCODE -ne 0) { $bad += $_ }
        }
    }
    if ($bad.Count -gt 0) {
        Write-Warning "[commit-watcher] BLOCKED: invalid JSON staged -> $($bad -join ', '). Fix and re-run; queue left intact."
        return
    }

    # is there anything to commit?
    & git diff --cached --quiet
    $hasDiff = ($LASTEXITCODE -ne 0)
    if (-not $hasDiff) {
        # content already committed by an earlier run; these are empty-diff
        # leftovers -- move them to done/ (do NOT strand them).
        foreach ($it in $items) { Move-ToDone $it.File "EMPTYDIFF-" }
        Write-Host "[commit-watcher] no staged diff; moved $($items.Count) empty-diff request(s) to done/ (content already committed)."
        return
    }

    # pre-commit RELEASE gate (single source: release_check.py = the publication
    # gate; gate list in gates.py). Refuse to commit a stale/broken tree.
    & python verification/scripts/release_check.py | Out-Host
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "[commit-watcher] BLOCKED: release_check failed (stale generated surface or hygiene/policy error). Queue left intact -- run python verification/scripts/regen_all.py (or fix the reported error), then re-run."
        return
    }

    # build the commit message: single -> as-is; multiple -> numbered batch
    if ($items.Count -eq 1) {
        $msg = $items[0].Message
    } else {
        $msg = "Batch commit: $($items.Count) queued change sets (per-entry detail in CHANGELOG).`n"
        for ($i = 0; $i -lt $items.Count; $i++) {
            $msg += "`n[$($i + 1)/$($items.Count)] " + $items[$i].Message + "`n"
        }
    }

    # v1.5.0: pass the message via a temp file (-F). Inline -m breaks when the
    # message contains double quotes (PowerShell native-arg quoting); -F is
    # robust against quotes/newlines. Temp file is P0 (inside internal/).
    $msgFile = Join-Path $queue ".commit-msg.tmp"
    [System.IO.File]::WriteAllText($msgFile, $msg, (New-Object System.Text.UTF8Encoding($false)))
    & git -c user.email="jtkor@outlook.com" -c user.name="Jusang Lee" commit -F $msgFile
    $rc = $LASTEXITCODE
    Remove-Item $msgFile -ErrorAction SilentlyContinue
    if ($rc -eq 0) {
        foreach ($it in $items) { Move-ToDone $it.File "" }
        $head = $items[0].Message.Substring(0, [Math]::Min(72, $items[0].Message.Length))
        Write-Host "[commit-watcher] committed $($items.Count) change set(s) in one commit: $head..."
    } else {
        Write-Warning "[commit-watcher] git commit failed; queue left intact (no JSON moved)."
    }
}

if ($Once) { Process-Queue; exit 0 }
while ($true) { Process-Queue; Start-Sleep -Seconds 10 }
