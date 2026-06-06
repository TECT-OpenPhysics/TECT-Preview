# =============================================================================
# commit_watcher.ps1 - Windows-side auto-commit daemon for the TECT repository
# Version: 1.1.2 -- first issued 2026-06-05; this version issued 2026-06-06
#   1.1.2 (2026-06-06): git add --all via call operator (the -A token still
#   mangled to a single-dash pathspec under the operator PowerShell); paths ignored.
#   1.1.1 (2026-06-06): FIX git add -A splat bug (23 queued commits silently
#   failed); only move to done/ on commit success (rc=0), else leave in queue.
#   1.1.0 (2026-06-06): pre-commit JSON-integrity gate (blocks truncated
#   status.json from entering history; leaves the request in the queue).
#
# WHY: the AI collaborator's sandbox cannot run git (the mount blocks the
# unlink operations git requires), so commits were handed to the operator as
# PowerShell blocks each turn - and were sometimes skipped, leaving code
# version bumps unrecorded. This watcher closes that gap: the AI writes a
# commit-request JSON into internal/commit-queue/ (gitignored, P0), and this
# script - running on the operator's Windows side - performs the commit with
# the standard maintainer signature.
#
# USAGE (from the repository root):
#   .\verification\scripts\commit_watcher.ps1            # watch loop (10 s)
#   .\verification\scripts\commit_watcher.ps1 -Once      # drain queue once
#
# Request format (internal/commit-queue/<utc-timestamp>-<slug>.json):
#   { "message": "<commit message>", "paths": ["-A"] }
# Processed requests move to internal/commit-queue/done/ with a result echo.
# SAFETY: refuses to run outside a git worktree; refuses empty messages;
# never force-pushes or pushes at all (push stays a manual operator action).
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

function Process-Queue {
    Get-ChildItem -Path $queue -Filter *.json -File | Sort-Object Name | ForEach-Object {
        $req = Get-Content $_.FullName -Raw | ConvertFrom-Json
        if (-not $req.message -or $req.message.Trim().Length -eq 0) {
            Write-Warning "skip (empty message): $($_.Name)"; return
        }
        # FIX 1.1.2: every queued commit stages the whole tree. Use the
        # long-form --all via the call operator so PowerShell cannot mangle a
        # single-dash token into pathspec dash (the v1.0/v1.1.1 bug that
        # stranded 23+ commits). The req.paths field is intentionally ignored.
        & git add --all
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "[commit-watcher] git add --all failed for $($_.Name); request left in queue."
            return
        }
        # PRE-COMMIT INTEGRITY GATE (added 2026-06-06 after the autonomous
        # subagent truncated three status.json cards): refuse to commit if any
        # staged status.json / *.json fails to parse. This stops a truncated
        # card from entering history silently. Bypass intentionally absent.
        $bad = @()
        git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.json$' } | ForEach-Object {
            $jf = $_
            if (Test-Path $jf) {
                & python -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" $jf 2>$null
                if ($LASTEXITCODE -ne 0) { $bad += $jf }
            }
        }
        if ($bad.Count -gt 0) {
            Write-Warning "[commit-watcher] BLOCKED $($_.Name): invalid JSON staged -> $($bad -join ', '). Fix and re-queue; request left in queue."
            return
        }
        & git -c user.email="jtkor@outlook.com" -c user.name="Jusang Lee" commit -m $req.message
        $rc = $LASTEXITCODE
        if ($rc -eq 0) {
            $stamp = (Get-Date -Format "yyyyMMdd-HHmmss")
            Move-Item $_.FullName (Join-Path $done "$stamp-$($_.Name)")
            Write-Host "[commit-watcher] committed: $($req.message.Substring(0, [Math]::Min(80, $req.message.Length)))..."
        } else {
            Write-Warning "[commit-watcher] git commit exited $rc for $($_.Name); request LEFT IN QUEUE (likely nothing staged or empty diff). Not moved to done/."
        }
    }
}

if ($Once) { Process-Queue; exit 0 }
while ($true) { Process-Queue; Start-Sleep -Seconds 10 }
