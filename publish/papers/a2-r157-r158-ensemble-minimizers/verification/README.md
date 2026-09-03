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
& $py verification/scripts/a2_r472_lean_crosscheck_verify.py --output tmp/r472-integrated.json
```

Expected registered results are:

* full-production evolution audits: `20/20`, `14/14`, `12/12`, and `15/15`
  PASS;
* R-157 primary and independent lanes: `26/26` and `24/24` PASS;
* R-158 primary and independent lanes: `35/35` and `24/24` PASS;
* integrated R-157/R-158 authority, artifact, PDF, and legacy checks: PASS;
* R-472 exact-core sidecar: primary `30/30`, independent `22/22`, hostile
  `12/12`, integrated `22/22`, with Lean compilation PASS.

The last command is assurance-only: R-472 is explicitly non-bearing and must
not be used to promote the A2/R-157/R-158 theorem claims.  The manuscript
version 0.1.7 records the self-contained functional and spectral specification
and a bounded primary-source literature crosswalk; the displayed data and those
sources are context and audit inputs, not new proof claims.

These executable checks recompute the exact constants, signs, spectral
intervals, normalizations, and hostile mutations recorded by the claim.  They
are not substitutes for the analytic proof, the literature crosswalk, or an
external referee audit.

## Current replay boundary

On 2026-09-03 the A2 wrapper and all four R-157/R-158 child lanes reproduced
their registered PASS counts.  A shared record predicate in the two integrated
verifiers was then repaired in v1.0.2: the lookup key, structured title, status,
and exact gate are authoritative, while the free-form task note is no longer
required to repeat those tokens.  The repair and its adversarial boundary are
recorded as `EXP-001372`, correcting the earlier replay boundary `EXP-001370`.

A fresh replay now passes R-157 integrated verification `144/144` (including
legacy A2 `61/61`) and R-158 integrated verification `155/155` (including the
R-157/A2 regression).  Manuscript v0.1.8 additionally displays the generators,
internal matrices, density floor, Class-II coefficient formulas, explicit
shell-bottom scalar symbol, the integration-by-parts sign in `N_II`, and the
nonlinear energy `Phi`, alongside the direct-method
coercivity/weak-lower-semicontinuity route for the `mu>mu_t` minimizer, the full
lower-order map `N=N_loc+N_II`, the Gelfand-triple chain-rule hypotheses, and
the bounded primary-source crosswalk.  These are self-containedness and
proof-text/literature-boundary clarifications, not a new claim or tier change;
the latest repair is recorded as `EXP-001379`.
This closes the repository synchronization gate only; it does not replace the
analytic proof, specialist literature review, external proof audit, operator
confirmation, capstone bundle, or release check.

## Canonical evidence paths

* `claims/A2-FULL-PRODUCTION-WELLPOSED/claim.md`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/status.json`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-full-production-wellposedness-260717-v2.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-pinned-functional-unique-zero-global-minimizer-260803-v1.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/notes/a2-charge-ensemble-first-order-shell-transition-260803-v1.0.tex.txt`
* `claims/A2-FULL-PRODUCTION-WELLPOSED/bundle/A2-Full-Production-WellPosedness-T6-260717/`
* `publish/papers/a2-r157-r158-ensemble-minimizers/proof-audit.md`

The manuscript's numerical table is valid only at the registered scope.  Any
failed command, source-hash drift, or proof-audit objection must stop the
publication lane and be recorded before the status can advance beyond draft.
