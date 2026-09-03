# Verification protocol for the A2/R-157/R-158 manuscript

This is a repository-facing draft protocol.  It points to the canonical P1
source files and does not replace the claim-level reproduction bundles.  A
standalone capstone bundle must be built only after operator confirmation of
the integrated referee note, as required by the repository bundle policy.

Run from `E:\Dev\TECT` with the repository environment:

```powershell
$py = "E:\Dev\TECT.venv\Scripts\python.exe"
& $py codes/foundations/a2_full_production_verify.py
& $py codes/foundations/a2_pinned_functional_unique_zero_global_minimizer.py
& $py codes/foundations/a2_pinned_functional_unique_zero_global_minimizer_independent.py
& $py codes/foundations/a2_charge_ensemble_first_order_shell_transition.py
& $py codes/foundations/a2_charge_ensemble_first_order_shell_transition_independent.py
& $py codes/foundations/a2_charge_ensemble_first_order_shell_transition_verify.py
```

Expected registered results are:

* full-production evolution audits: `20/20`, `14/14`, `12/12`, and `15/15`
  PASS;
* R-157 primary and independent lanes: `26/26` and `24/24` PASS;
* R-158 primary and independent lanes: `35/35` and `24/24` PASS;
* integrated R-157/R-158 authority, artifact, PDF, and legacy checks: PASS;
* R-472 exact-core sidecar: primary `30/30`, independent `22/22`, hostile
  `12/12`, integrated `22/22`, with Lean compilation PASS.

These executable checks recompute the exact constants, signs, spectral
intervals, normalizations, and hostile mutations recorded by the claim.  They
are not substitutes for the analytic proof, the literature crosswalk, or an
external referee audit.

## Canonical evidence paths

* `claims/A2-FULL-PRODUCTION-WELLPOSED/claim.md`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/status.json`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-full-production-wellposedness-260717-v2.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-pinned-functional-unique-zero-global-minimizer-260803-v1.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-charge-ensemble-first-order-shell-transition-260803-v1.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/bundle/A2-Full-Production-WellPosedness-T6-260717/`

The manuscript's numerical table is valid only at the registered scope.  Any
failed command, source-hash drift, or proof-audit objection must stop the
publication lane and be recorded before the status can advance beyond draft.
