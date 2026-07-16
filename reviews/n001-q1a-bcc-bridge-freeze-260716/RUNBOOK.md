# N-001 q1a evidence-freeze runbook

## 1. Verify the frozen repository evidence

Run this from the repository root.  It verifies every locked file and then the
lock-list digest.  It needs no external PDE tree and does not rerun numerics.

```powershell
$lock = Get-Content reviews/n001-q1a-bcc-bridge-freeze-260716/SHA256SUMS.txt
foreach ($line in $lock) {
  $expected, $path = $line -split '  ', 2
  $actual = (Get-FileHash -Algorithm SHA256 $path).Hash.ToLower()
  if ($actual -ne $expected) { throw "hash mismatch: $path" }
}
$bytes = [Text.Encoding]::UTF8.GetBytes(([string]::Join("`n", $lock) + "`n"))
$sha = New-Object Security.Cryptography.SHA256Managed
$digest = -join ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
if ($digest -ne 'ecb48ed407a9eecce757554f37a8ccadf541a0f54253521ba0d037d6f04af766') { throw 'lock digest mismatch' }
Write-Host 'N-001 q1a evidence freeze: PASS'
```

Expected final line:

```text
N-001 q1a evidence freeze: PASS
```

## 2. Recompute the N32 BCC-star probe only when needed

This is not a repository-only command.  First compare the external source and
run-artifact hashes against the `source_sha256` fields in
`reviews/2026-07-16-n001-bcc-star-curvature-n32-fullstar.json`.  Then run:

```powershell
C:\Users\jtkor\AppData\Local\Programs\Python\Python312\python.exe codes/foundations/n001_bcc_star_curvature.py `
  --run-root C:\Dev\Runs\q1a_final_pubgrade_compat_v2\refinement `
  --pde-root C:\Dev\Codes\PDE `
  --grids 32 `
  --output reviews/2026-07-16-n001-bcc-star-curvature-rerun.json
```

Compare the new JSON with the frozen full-star JSON.  Do not overwrite the
frozen file.  A changed result is a new diagnostic record, not a correction by
default; first determine whether the external inputs or numerical convention
changed.

## 3. Conditions for reopening the BCC bridge

Open a new dated record only if at least one condition is explicit:

1. a new parameter or operator regime is declared;
2. a distinct box or grid-transfer question is declared; or
3. a candidate passes the q0-shell/BCC structure audit.

Before any BCC interpretation, preserve the solver output, run the structure
audit, state the admissible scope, and keep candidate discovery, residual
certification, projected-Hessian checks, and BCC structure classification as
separate stages.  The present positive N32 BCC-star result is not a reason to
silently conclude BCC nonexistence elsewhere.
