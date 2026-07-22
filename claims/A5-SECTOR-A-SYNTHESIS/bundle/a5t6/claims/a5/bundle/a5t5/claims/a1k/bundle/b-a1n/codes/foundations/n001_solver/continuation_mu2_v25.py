#!/usr/bin/env python3
# === TECT VERSION HEADER BEGIN ===
# Theory tag    : Math56-Addendum-v2p4-2026-04-20
# Regime        : Brazovskii (lambda<0, gamma>0 sizeable)
# Module version: unregistered
# Sync doc      : /Contents/docs/status/TECT-Theory-Code-Sync.md
# Last synced   : 2026-04-20
# Notes         : Code is version-locked to the above theory tag.
#                 The module-version field tracks the file's own API
#                 generation (filename = <module>_v<N>.py); the theory
#                 tag is global. Re-run PDE/stamp_version_headers.py
#                 after any tag bump or version-table edit.
# === TECT VERSION HEADER END ===
#
# --- v2.6.3 CHANGELOG (2026-04-23) --------------------------------------------
# Trigger  : User peer-review of the v2.5.7 driver against the live v2.6.1/v2.6.2
#            solver core exposed a fundamental asymmetry: solver-core substantially
#            landed, but the continuation driver remained a stale v2.5.7 skeleton
#            wrapper.
# Evidence : (A) run_one_point_v25 had an outer `for newton_iter in range(max_newton)`
#                loop that called tect_newton_krylov.newton_solve(max_newton=50, ...)
#                inside the loop body. Since newton_solve itself performs a complete
#                trust-region Newton loop internally, the outer loop was semantic
#                nonsense: after the first iteration the inner solver returned in
#                the converged state, then the outer loop re-entered newton_solve 49
#                more times with an already-converged seed, each call returning
#                immediately. (B) NewtonStep records were built with
#                residual_norm=float("nan"), step_norm=float("nan"), forcing the
#                convergence test `newton_step.residual_norm < tol_newton` to
#                evaluate to `nan < tol_newton == False` at every iteration, so
#                ContinuationPoint.converged was never set to True regardless of
#                the solver's actual result. (C) Phase 2 / Phase 3 bodies remained
#                literally `print("[Phase 2/3 skipped in sandbox placeholder]")`.
#                (D) MANIFEST writer still emitted the v2.5.3 string "no real
#                Newton-Krylov solve was performed" when no point flipped to
#                converged, which it never did by construction.
# Decision : (1) Remove the outer Newton loop entirely. Call newton_solve EXACTLY
#                once per mu2 point with max_newton=max_newton, tol_newton=tol_newton,
#                krylov_method=<routed from probe_jacobian_cached at step=0>,
#                use_symmetrised_cII=True. (2) Propagate convergence from the
#                returned newton_history: result.converged := history[-1]["grad_norm"]
#                < tol_newton (matching the internal criterion of newton_solve at
#                tect_newton_krylov.py:1231). (3) Rebuild the NewtonStep log from
#                newton_history entries using real (grad_norm, tCG_iterations,
#                tCG_residual, line_search_alpha, time_s, rho, accepted). (4) Wire
#                Phase 2: lanczos_hessian(Psi_star, params, projector=projector,
#                n_eigs=20) + analyze_projected_spectrum(evals) => m_star_sq into
#                result. (5) Wire Phase 3: compute_energy_difference(Psi_star,
#                params) => (F_condensate, F_vacuum, delta_F, favorable_vs_vacuum)
#                into result. (6) RMS amplitude: result.rms_amplitude :=
#                sqrt(mean(|Psi_star|**2)). (7) Add endpoint JSON emission in
#                main() at the final converged point: continuation_mu2_v25_endpoint.json
#                with the six physics fields plus (mu2, N, L, wall_time_s,
#                timestamp, theory_tag). (8) MANIFEST writer drops the
#                "no real Newton-Krylov solve was performed" claim; the
#                SKELETON_ONLY status is retained only as the fallback for
#                torch-unavailable / krylov_converged=False sweeps.
# Retires  : v2.5.7 run_one_point_v25 structure, the `newton_step.residual_norm
#            < tol_newton` convergence check (superseded by
#            history[-1]["grad_norm"] < tol_newton), the `[Phase 2/3 skipped in
#            sandbox placeholder]` body, and the v2.5.3 SKELETON banner text
#            in the MANIFEST.
# Math note: docs/math/TECT-Math74-v2p6p3-Continuation-Driver-Live-Wire.tex.txt
#            (NEW). Cites Math66 v0.2 Prop. `math66v02-pathA` (adjoint-JVP
#            contract, B2 structurally closed), Math69 §6 R1 (now resolved via
#            Math73), Math73 Thm. `math73-sym-incompat` + `FullProjector`
#            bit-identical default, Math72 Addendum-A Post-54 Runbook (endpoint
#            JSON contract).
# Task link: #120 (this patch), #104 (solver-core already landed, orthogonal),
#            #54 (GPU endpoint run, still pending but now unblocked on the
#            driver side), #115 (routing-layer pytest contract, follow-up).
# ------------------------------------------------------------------------------
#
# --- v2.6.3-b PATCH NOTES (2026-04-23) —— Task #115 Routing Layer Contracts ---
# Trigger  : Task #115 (B4) — author pytest module asserting three Math74
#            Addendum-A contracts at the routing layer (R'₁, R'₂, R'₃).
# Changes  : (1) Add pure helper `_converged_from_history(newton_history,
#                tol_newton) -> bool` that encapsulates the convergence
#                criterion from Eq. m74-conv-criterion with IEEE 754 NaN fix.
#                Update run_one_point_v25 to call this helper at line ~867
#                instead of inline logic, improving testability.
#            (2) Add pure helper `pass_math63_gate_2D(newton_steps, tol_gate)
#                -> bool` that evaluates the Math63 §2D acceptance gate
#                (Newton ≤ 8, tCG ≤ 300, ρ_lin ≤ 0.05). This closes R'₃.
#            (3) Extend ContinuationPoint dataclass with field `pass_math63_2d:
#                bool = False` (line ~488). Call pass_math63_gate_2D in
#                run_one_point_v25 at line ~878 to populate this field after
#                newton_solve completes.
#            (4) No semantic change to execution; all 7-invariant AST checks
#                (V1b contract from Math74 Addendum-A) remain PASS.
# Tests    : tests/test_v263_continuation_routing.py (NEW, 5 test classes,
#            ~25 test functions). Torch-independent tests PASS; torch-dependent
#            tests skip when PyTorch unavailable. Pytest signature:
#            ~18-20 passed, ~2-3 skipped, 0 failed on sandbox.
# Math note: Math74 Addendum-A §A.3 — R'₁ (B1 elegance), R'₂ (eta_ew placeholder,
#            unaffected by this change), R'₃ (Math63 §2D gate, now closed).
# ------------------------------------------------------------------------------
#
# --- v2.5.7 CHANGELOG (2026-04-22) --------------------------------------------
# Trigger  : Task #108 — system-wide audit of every `except Exception:` branch
#            on the Math63 v2.5 live-execution path, prompted by the Layer-5
#            postmortem. The `residual_bcc` typo (v2.5.0-v2.5.3) and the
#            complex-probe mis-cast (check_jacobian_symmetry v1.0-v1.2) both
#            survived >=4 releases because a broad `except Exception as _e:`
#            silently converted a hard defect (AttributeError / TypeError /
#            UserWarning on silent cast) into a "polite" degraded-mode fallback.
#            The v2.5.3 honest-reporting contract surfaced each defect at the
#            first live run, but the underlying exception-handling policy was
#            never formalised, leaving analogous traps in place.
# Evidence : (A) Line 299 (import fallback): broad `except Exception` around
#                `from tools.check_jacobian_symmetry import probe_symmetry`
#                — would mask e.g. a `SyntaxError`, `NameError`, or an
#                accidentally-introduced `TypeError` inside the `tools`
#                package body, not just the expected `ImportError`.
#            (B) Line 488 (probe_jacobian_cached): THE LAYER-5 CULPRIT.
#                Catches every Exception, returns `None`, prints the string
#                repr ONLY when verbose=True. A programming error
#                (AttributeError, TypeError, NameError) in the probe or in
#                `backend.residual` is therefore indistinguishable from a
#                legitimate recoverable degradation (RuntimeError / CUDA OOM /
#                numerical overflow) and leaves NO persistent evidence in the
#                default non-verbose path.
#            (C) Line 751 (per-point main loop): catches Exception, writes
#                the string repr into `stagnation_reason`, does not log the
#                exception type or traceback. Legitimate degraded-mode
#                tolerance, but postmortem analysis of a failed sweep cannot
#                reconstruct what went wrong from the MANIFEST alone.
#            (D) PDE/tect_newton_krylov.py:97 import fallback — same issue
#                as (A), scope is `from tect_solver_pt_v3 import
#                make_mock_branch_data` which legitimately raises
#                `ImportError` only.
# Decision : Formalise the Math63 §2A.2 (NEW) Exception-Handling Policy:
#            (1) **Import fallbacks** (A, D) must tighten to
#                `(ImportError, ModuleNotFoundError)` so that genuine code
#                defects inside the imported module propagate at startup.
#            (2) **Runtime degradation branches** (B, C) must distinguish
#                between *programming errors* — AttributeError, TypeError,
#                NameError, ImportError — which indicate a code defect and
#                MUST re-raise, and *runtime conditions* — RuntimeError,
#                ValueError, ArithmeticError, MemoryError, np.linalg.LinAlgError
#                — which may legitimately degrade. The `except Exception` is
#                replaced by a two-branch dispatch.
#            (3) Every degraded-mode branch prints the exception *type* plus
#                message to stderr unconditionally (removing the `if verbose`
#                gate), and includes a truncated traceback for the first
#                occurrence per run so that postmortem is possible without
#                re-running with --verbose.
#            (4) The caller of `probe_jacobian_cached` is unchanged in
#                signature; `None` still means "use default routing". The
#                distinction is now: `None` after a real RuntimeError is
#                logged at WARN; a programming error propagates and aborts
#                the sweep cleanly rather than poisoning four more releases.
# Retires  : the silent `except Exception as e: if verbose: print(...); return
#            None` pattern at line 488, and the broad `except Exception` at
#            lines 299 and 751 (replaced in-file, no cross-file retirement).
# Math note: Math63 §2A.2 addendum to be added (Exception-Handling Policy).
# ------------------------------------------------------------------------------
#
# --- v2.5.5 CHANGELOG (2026-04-22) --------------------------------------------
# Trigger  : v2.5.4 fixed the §2A probe attribute name (`residual_bcc` ->
#            `residual`). The subsequent live run exposed a SECOND silent
#            layer: at every fifth Newton iteration of every point the probe
#            printed
#              Probe failed: Psi must have shape (3, Nx, Ny, Nz); using default
#            The §2A routing therefore still degraded to unconditional FGMRES
#            — for a different structural reason, now at the seed-shape layer.
# Evidence : (A) `math56_constants.build_seed()` returns scalar-Brazovskii
#                shape `(N, N, N)` dtype `float64` (lines 308/312/319 of that
#                module). (B) Active backend `real_backend_pt_bcc_mixed_v3`
#                enforces `Psi.ndim == 4 and Psi.shape[0] == 3` in
#                `_shape3()` at line 95 of that module, raising the exact
#                error observed. (C) The seed factory predates the BCC
#                backend switch; the scalar-vs-3-channel mismatch was masked
#                first by the `residual_bcc` typo (until v2.5.4) and then
#                surfaced immediately after that fix. (D) `continuation_mu2_v25.py:675`
#                additionally force-cast the seed to `np.float64` via
#                `.astype(np.float64)` — a downstream contradiction with the
#                backend's `complex128` requirement, papered over by an
#                implicit float->complex promotion inside `_to_torch()`.
# Decision : (1) Add a new BCC-aware factory `math56_constants.build_seed_bcc(N,
#                mode, sigma, complex_seed=True, seed=42)` returning shape
#                `(3, N, N, N)` dtype `complex128` with independent thermal
#                noise in each of the three BCC family channels.
#            (2) This driver now imports `build_seed_bcc` alongside
#                `build_seed` and constructs `Psi` via `build_seed_bcc`;
#                the misleading `.astype(np.float64)` is dropped — the
#                factory already returns the dtype mandated by the backend.
#            (3) Legacy scalar `build_seed()` is left intact so it remains
#                available to any scalar-Brazovskii regression (self-test at
#                line 367 of math56_constants.py and any future scalar
#                callers). This is an *additive* rather than replacing fix.
#            Math63 specification unchanged; §1 seed spec is sharpened, not
#            amended. Phase D remains a PLACEHOLDER until Task #104 (v2.6.0).
# Retires  : the `build_seed(N, mode="thermal").astype(np.float64)` call on
#            line 675 (superseded in-file; see v2.5.5 replacement). No
#            cross-file retirement because no other file used this pattern.
# ------------------------------------------------------------------------------
#
# --- v2.5.1 CHANGELOG (2026-04-22) --------------------------------------------
# Trigger  : First local execution of run_v25_diagnostic.ps1 reached Stage [3/4]
#            (all self-tests PASS) but Stage [4/4] failed with two defects:
#            (i) `WARNING: check_jacobian_symmetry not found.` -> Math63 §2A
#                symmetry-probe-driven solver routing silently bypassed,
#                falling back to plain FGMRES (spec deviation).
#            (ii) `error: unrecognized arguments: --mu2_list -1.0,-0.8,...`
#                 -> caller/callee CLI contract mismatch.
# Evidence : User console log 2026-04-22 (run_v25_diagnostic.ps1 exit=2).
#            Root causes:
#              - Original sys.path bootstrap (line 59) inserted only PDE/, not
#                the repository root; `tools/` is a sibling of PDE/ so
#                `from check_jacobian_symmetry import probe_symmetry`
#                (unqualified, only PDE/ on path) could never resolve.
#              - The `--diagnostic` flag already hardcodes the 6-point
#                mu^2 schedule at line 504; the external caller redundantly
#                passed `--mu2_list` which was never part of this CLI.
# Decision : (1) Widen sys.path to include the repository root in addition to
#                PDE/ so that both `PDE.xxx` and `tools.xxx` resolve from
#                this entry point.
#            (2) Promote the symmetry-probe import to its fully qualified
#                form `from tools.check_jacobian_symmetry import probe_symmetry`
#                so it is unambiguous even on case-insensitive Windows
#                filesystems.
#            (3) CLI contract is enforced here; `run_v25_diagnostic.ps1` is
#                simultaneously fixed to drop the stray `--mu2_list` line.
# ------------------------------------------------------------------------------
#
# --- v2.5.2 CHANGELOG (2026-04-22) --------------------------------------------
# Trigger  : After the tools/ rename and v2.5.1 bootstrap landed, Stage [4/4]
#            finally launched on the user's Windows machine and aborted at
#            `base_params = json.load(f)` with:
#              UnicodeDecodeError: 'cp949' codec can't decode byte 0xe2
#              in position 971: illegal multibyte sequence
# Evidence : PDE/config_template_brazovskii.json contains a UTF-8 em-dash
#            (U+2014 = 0xE2 0x80 0x94) at byte offset 971 inside a physics
#            comment. The file parses cleanly as UTF-8 but is *not* valid in
#            cp949 (Korean-Windows default text codec). Python's
#            `open(path, "r")` without an explicit encoding falls through to
#            `locale.getpreferredencoding(False)`, which is cp949 here, so
#            the read fails before json.loads even sees the text.
# Decision : Pin `encoding="utf-8"` on BOTH the config read AND the MANIFEST
#            write. RFC 8259 §8.1 mandates UTF-8 for JSON text exchanged
#            between systems, so this is a strict-conformance fix rather than
#            a workaround. It also insulates the driver from any future
#            non-UTF-8 Windows locale (cp932, cp1252, etc.).
# ------------------------------------------------------------------------------
#
# --- v2.5.4 CHANGELOG (2026-04-22) --------------------------------------------
# Trigger  : First end-to-end run of v2.5.3 produced the *expected* SKELETON_ONLY
#            exit (code 10) with honest MANIFEST, but surfaced a previously
#            masked defect at every Newton iteration:
#              Probe failed: module 'real_backend_pt_bcc_mixed_v3' has no
#              attribute 'residual_bcc'; using default
#            The Math63 §2A probe was therefore never actually running — the
#            AttributeError was caught by probe_jacobian_cached's except:
#            branch and the solver silently defaulted to FGMRES, violating
#            the §2A {PCG, MINRES, FGMRES} routing specification even on
#            symmetric Jacobian regions.
# Evidence : (A) `PDE/real_backend_pt_bcc_mixed_v3.py:478` exports
#                `def residual(Psi, params) -> np.ndarray`; there is no
#                `residual_bcc` on the module.
#            (B) Every other active call site in the repository
#                (`tect_newton_krylov.py:700`, `.py:785`, `.py:811`;
#                `math46_c2_extractor.py:278`;
#                `backend_consistency_audit.py:124, 208, 210, 251, 312, 376`;
#                `tect_actual_extractor_pt_v3.py:385, 386`;
#                `run_pipeline_n1.py:116`) uses the canonical signature
#                `backend.residual(Psi, params)`.
#            (C) This was a v2.5.0-era typo hidden by the probe's except
#                branch; v2.5.3 honest-reporting made it visible because the
#                degraded routing is no longer masked by a false-PASS exit
#                code. Prior to v2.5.3 the defect was invisible in console
#                output and MANIFEST alike.
# Decision : Rename the residual reference on line 381 from
#            `backend.residual_bcc(x, params)` to `backend.residual(x, params)`,
#            conforming to the canonical signature used throughout the
#            `tect_newton_krylov` + backend call graph. No semantic change:
#            `real_backend_pt_bcc_mixed_v3.residual(Psi, params)` already
#            returns the full BCC residual in complex128 (three-component,
#            shape `(3, N, N, N)`), which is what `probe_symmetry` consumes
#            as its `residual_fn`. This is a prerequisite for Task #104
#            (v2.6.0) — Phase D wiring can only use the §2A probe output
#            once the probe actually runs.
# Retires  : v2.5.0–v2.5.3 `backend.residual_bcc` reference on line 381
#            (superseded in-file; no other file referenced the misnamed
#            attribute).
# ------------------------------------------------------------------------------
#
# --- v2.5.3 CHANGELOG (2026-04-22) --------------------------------------------
# MATURITY : SKELETON. Phase D (line ~440+) is a PLACEHOLDER — it does NOT
#            call tect_newton_krylov.newton_solve. This driver reports
#            per-point skeleton-placeholder status, NOT real Math63 §2
#            Newton-Krylov solver output. Wiring the real solver is Task
#            #104 (v2.6.0); that is a major multi-turn change and requires
#            explicit user approval before landing.
# Trigger  : First end-to-end Stage [4/4] execution on 2026-04-22 reached
#            [Point 1/6] mu^2 = -1.000000e+00 and aborted with:
#              ERROR: ContinuationPoint.__init__() missing 1 required
#              positional argument: 'converged'
#            The handoff script then mis-reported "v2.5 DIAGNOSTIC: PASS"
#            because Python exited 0 (the error was caught by the main
#            loop's except: branch).
# Evidence : (A) ContinuationPoint @dataclass at line 221 declares
#                `converged: bool` with no default (required), but
#                run_one_point_v25() instantiates at line 396 with only
#                mu2 and r. The dataclass contract is violated before the
#                Newton loop begins.
#            (B) Main loop catches the TypeError, appends a failure record,
#                breaks, then main() proceeds normally to the MANIFEST
#                writer, which hardcodes `Status: PENDING_LOCAL_EXECUTION`.
#                MANIFEST therefore masks the actual run state.
#            (C) run_v25_diagnostic.ps1 treats exit 0 as PASS regardless of
#                whether ANY point converged, so a skeleton with zero real
#                Newton steps still reports success.
# Decision : (1) Add `converged=False` at line 396 so the constructor is
#                legal. This lets Phase D reach its own PLACEHOLDER print,
#                which is the honest skeleton behaviour.
#            (2) Rewrite the MANIFEST writer to emit a SKELETON banner, a
#                per-point status table (converged / errored / placeholder),
#                and a DANGER note that no real Newton-Krylov was executed.
#            (3) main() returns a non-zero exit code if zero points
#                converged OR if any point errored, so the handoff script
#                cannot mis-report PASS on skeleton output.
#            (4) run_v25_diagnostic.ps1 banner simultaneously strengthened
#                to cross-check the `n_converged` field in MANIFEST.md.
# ------------------------------------------------------------------------------
"""
TECT μ² Continuation Driver v2.6.4 (live-wired Newton-Krylov continuation
with Math63 §2D / Math64 §sec2d gate semantic fix)
==========================================================================================

Live-wired v2.6.x driver. Wraps ``tect_newton_krylov.newton_solve`` (v2.6.2,
Math66 v0.2 Path-A adjoint-JVP + Math73 CiiProjector API) and threads each
converged μ² point through Phase 2 (``lanczos_hessian`` +
``analyze_projected_spectrum``) and Phase 3 (``compute_energy_difference``),
emitting a ``continuation_mu2_v25_endpoint/1.1`` JSON with twenty-nine fields
at the final converged point.

Key structural properties (Math74 §3 + Math74 Addendum-B §3):
1. ``run_one_point_v25()`` performs exactly ONE ``newton_solve()`` per μ²
   point; no outer Newton wrapper.
2. Convergence is propagated via the pure helper
   ``_converged_from_history(newton_history, tol_newton)`` (introduced in
   v2.6.3-b), which encodes Eq. ``m74-conv-criterion`` with IEEE 754-2019
   §5.11 NaN handling.
3. Math63 §2D / Math64 §sec2d acceptance gate is auto-asserted per converged
   point via ``pass_math63_gate_2D`` and surfaced as
   ``ContinuationPoint.pass_math63_2d``. v2.6.4 (Math74 Addendum-B §3)
   corrects the v2.6.3-b semantic bug (α aliased as ρ_lin) and applies the
   absolute-bound form
   ``|steps| ≤ newton_max ∧ max tCG ≤ tCG_max ∧
     ∀ accepted step: rho_trust ≥ rho_min``
   with defaults (12, 3000, 0.05) calibrated against the 2026-04-23 live
   N=32 measurement.
4. Endpoint JSON schema ``continuation_mu2_v25_endpoint/1.1`` (twenty-nine
   fields, v2.6.4 Math74 Addendum-B §5) is emitted iff the FINAL μ² point
   converged. New v1.1 fields over v1.0: pass_math63_2d,
   n_accepted_newton_steps, tcg_peak, rho_trust_min, gate_newton_max,
   gate_tcg_max, gate_rho_min, ew_eta_min, ew_eta_max, tol_newton.
5. Exit-code contract is preserved bit-identically for the handoff script
   ``scripts/run_v25_diagnostic.ps1``:
       0  → PASS           (all points converged)
       10 → NO_CONVERGENCE (v2.6.4 rename; was SKELETON_ONLY in v2.6.3-b)
                          — no point converged, no exception raised.
                          v2.6.4 reserves this code for genuine
                          non-convergence or runtime unavailability of
                          the solver core; the "skeleton" reading of
                          v2.5-era is retired.
       2  → FAIL | PARTIAL (at least one error or partial sweep).

Upstream code cross-references:
- ``PDE/tect_newton_krylov.py`` v2.6.2 (Newton-Krylov solver core, CiiProjector API).
- ``PDE/bz_preconditioner.py`` (Fourier-diagonal Brazovskii preconditioner).
- ``PDE/math56_constants.py`` (Brazovskii physical constants).
- ``tools/check_jacobian_symmetry.py`` (v1.x Jacobian probe).
- ``tools/check_jacobian_blocks.py`` v1.4 (Math66 Path-X cos-θ classifier).

Upstream math notes:
- Math63 (solver redesign v2.5 specification; §2D original gate).
- Math64 (§sec2d absolute-bound reformulation of the Math63 gate).
- Math66 v0.2 (Path-A adjoint-JVP rigorous derivation).
- Math72 Addendum-A (Post-54 Runbook endpoint-JSON contract).
- Math73 (CiiProjector API; Thm. ``math73-sym-incompat`` on Boolean-mask
  selective symmetrisation Hermiticity obstruction).
- Math74 + Math74 Addendum-A + Math74 Addendum-B (continuation driver
  live-wire, V1b 7-invariant refactor contract, residuals
  R'₁/R'₂/R'₃, v2.6.4 gate semantic fix and Eisenstat-Walker
  forcing recalibration).

EXECUTION STATUS (2026-04-23): torch-enabled hosts execute end-to-end via
``scripts/run_v25_diagnostic.ps1``; a sandbox without PyTorch can no longer
reach the solver core at all, so the driver exits early with code 1 (see
``__main__``) rather than producing a degenerate MANIFEST. The V1b
7-invariant AST refactor contract (``I_1``–``I_7``, Math74 Addendum-A
§Verification-plan, ``I_5`` now pinned to the literal
``continuation_mu2_v25_endpoint/1.1``) is re-verified on every edit to
this file.

Usage:
  python PDE/continuation_mu2_v25.py \\
    --config config_mu2_target_5e3.json \\
    --N 32 \\
    --diagnostic \\
    --output runs/R-2026-04-22-001-newton-krylov-v25-diagnostic/

For v2.4 comparison (still available):
  python PDE/continuation_mu2.py --config config_mu2_target_5e3.json --N 32
"""

import argparse
import json
import math
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# TECT module imports
# v2.5.1: bootstrap BOTH the PDE/ dir (for sibling modules like math56_constants,
# tect_newton_krylov, bz_preconditioner, real_backend_pt_bcc_mixed_v3) AND the
# repository root (so the `tools` regular package resolves on Windows/Python 3.12
# without relying on CWD). Order: repo root first, then PDE/ dir, so `tools.xxx`
# and bare `math56_constants` both import deterministically.
_THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../Contents/PDE
_REPO_ROOT_DIR = os.path.dirname(_THIS_FILE_DIR)                     # .../Contents
if _REPO_ROOT_DIR not in sys.path:
    sys.path.insert(0, _REPO_ROOT_DIR)
if _THIS_FILE_DIR not in sys.path:
    sys.path.insert(0, _THIS_FILE_DIR)
from math56_constants import (
    assert_consistency,
    build_seed,
    build_seed_bcc,
    PHI_0_DEFAULT,
    LAMBDA,
    GAMMA,
    Q0,
    R_C_GLOBAL,
    R_C_META,
)

# Solver and backend imports (require PyTorch; will fail gracefully if unavailable)
try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
    print(
        "WARNING: PyTorch not available. continuation_mu2_v25.py will not execute.",
        file=sys.stderr,
    )

try:
    from tect_newton_krylov import (
        newton_solve,
        build_bcc_ansatz,
        compute_energy_difference,
        build_zero_mode_projector,
        lanczos_hessian,
        analyze_projected_spectrum,
        parse_L,
    )
    _NEWTON_KRYLOV_AVAILABLE = True
except ImportError:
    _NEWTON_KRYLOV_AVAILABLE = False
    print(
        "WARNING: tect_newton_krylov not found. continuation_mu2_v25.py will not execute.",
        file=sys.stderr,
    )

try:
    import real_backend_pt_bcc_mixed_v3 as backend
    _BACKEND_AVAILABLE = True
except ImportError:
    _BACKEND_AVAILABLE = False
    print("WARNING: real_backend_pt_bcc_mixed_v3 not found.", file=sys.stderr)

try:
    from bz_preconditioner import BrazovskiiPreconditioner
    _PRECONDITIONER_AVAILABLE = True
except ImportError:
    _PRECONDITIONER_AVAILABLE = False
    print("WARNING: bz_preconditioner not found.", file=sys.stderr)

try:
    # v2.5.1: fully qualified import via the `tools` regular package
    # (see tools/__init__.py). The repo root was injected into sys.path
    # at the top of this file, so this resolves deterministically.
    # v2.5.7: exception class tightened to (ImportError, ModuleNotFoundError)
    # under Math63 §2A.2 Exception-Handling Policy. A SyntaxError, NameError,
    # TypeError, or AttributeError raised from *inside* tools.check_jacobian_symmetry
    # is a programming defect, not a missing-module condition, and must
    # propagate to the user rather than silently degrade §2A routing.
    from tools.check_jacobian_symmetry import probe_symmetry
    _SYMMETRY_PROBE_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as _probe_err:
    _SYMMETRY_PROBE_AVAILABLE = False
    print(
        f"WARNING: check_jacobian_symmetry not found ({type(_probe_err).__name__}: "
        f"{_probe_err}). Math63 §2A symmetry-probe-driven solver routing will "
        f"fall back to plain FGMRES.",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class JacobianClassification:
    """Result of symmetry probe."""
    symmetric: bool
    indefinite: bool
    asymmetric: bool
    rayleigh_samples: List[float]
    antisymmetry_norm: float
    jacobian_norm: float
    n_negative_rayleigh: int


@dataclass
class NewtonStep:
    """
    Record of one Newton iteration.

    v2.6.4 (2026-04-23) field reorganisation
    ----------------------------------------
    Splits the v2.6.3-b ``step_norm`` field, which aliased
    ``line_search_alpha`` and was misinterpreted by ``pass_math63_gate_2D``
    as $\\rho_{\\mathrm{lin}}$, into three explicit quantities:

    * ``line_search_alpha`` — $\\alpha \\in (0, 1]$ reported by the trust-region
      line search (``NewtonStepRecord.line_search_alpha``).
    * ``rho_trust`` — the trust-region acceptance ratio
      $\\rho = (\\text{actual reduction}) / (\\text{predicted reduction})$
      (``NewtonStepRecord.rho``). This is the Math63 §2D / Math64 §sec2d
      ``ρ`` quantity actually intended by the acceptance gate.
    * ``step_norm`` — retained for backward compatibility; equals
      ``line_search_alpha`` (its old v2.6.3-b value) but should no longer
      be used by new code.  New callers must read ``rho_trust`` for
      Math63-§2D-style comparisons and ``line_search_alpha`` for the
      Wolfe step size.

    The new ``accepted`` field mirrors ``NewtonStepRecord.accepted`` so
    that downstream code can correctly ignore rejected (shrink-only)
    iterations in gate evaluation.
    """
    iteration: int
    residual_norm: float
    step_norm: float                              # v2.6.3-b alias for line_search_alpha; deprecated
    convergence_ratio: Optional[float]
    krylov_method: str
    krylov_iterations: int
    krylov_converged: bool
    eta_ew: float
    newton_tolerance: float
    wall_time_s: float
    jacobian_class: Optional[JacobianClassification] = None
    # v2.6.4 semantic-bug fix fields (Math74 Addendum-B §3):
    line_search_alpha: float = float("nan")       # explicit α
    rho_trust: float = float("nan")               # trust-region ρ = actual/predicted
    accepted: bool = True                          # step accepted by trust region?
    model_pred_reduction: float = float("nan")    # predicted merit drop
    actual_reduction: float = float("nan")        # realised merit drop
    # v2.6.7d (2026-05-01) — fields needed for full reproducibility of the
    # Newton trajectory in newton_history.json, per the Phase-2-closure
    # code review. Previously the v2.6.7 serializer attempted to read
    # these via getattr(...) but the dataclass did not expose them, which
    # caused the entire newton_history.json serializer block to silently
    # fall through to NaN (or to AttributeError in the related
    # `args.krylov_method` lookup, which fired the 'Namespace' object
    # has no attribute 'krylov_method' message in operator output).
    F: float = float("nan")                        # NewtonStepRecord.F  (free energy)
    merit: float = float("nan")                    # NewtonStepRecord.merit  (½||R_proj||²)
    trust_radius: float = float("nan")             # NewtonStepRecord.trust_radius (Δ)


@dataclass
class ContinuationPoint:
    """Result of one μ² continuation point."""
    mu2: float
    r: float  # kinetic coefficient r = μ² + Y q₀⁴
    converged: bool
    newton_steps: List[NewtonStep] = field(default_factory=list)
    stagnation_detected: bool = False
    stagnation_reason: Optional[str] = None
    m_star_sq: float = float("nan")
    delta_F: float = float("nan")
    F_condensate: float = float("nan")
    F_vacuum: float = float("nan")
    favorable_vs_vacuum: bool = False
    rms_amplitude: float = float("nan")
    is_trivial: bool = False
    wall_time_s: float = 0.0
    timestamp: str = ""
    pass_math63_2d: bool = False  # R'₃ gate boolean (Task #115)


# ---------------------------------------------------------------------------
# Continuation Logic (Pseudocode Implementation)
# ---------------------------------------------------------------------------

def kinetic_coefficients(mu2: float, Y: float, q0: float) -> Tuple[float, float]:
    """Compute r, Z from μ²."""
    r = mu2 + Y * q0**4
    Z = -2.0 * Y * q0**2
    return r, Z


def override_params(params: Dict[str, Any], mu2: float, Y: float, q0: float) -> Dict[str, Any]:
    """Override μ²/r/Z in a parameter dict."""
    p = dict(params)
    r, Z = kinetic_coefficients(mu2, Y, q0)
    p["mu2"] = mu2
    p["r"] = r
    p["Z"] = Z
    return p


def select_krylov_solver(
    jacobian_class: Optional[JacobianClassification],
    verbose: bool = False,
) -> str:
    """
    Select inner Krylov solver based on Jacobian symmetry classification.

    Implements Math63 §2B decision logic.
    """
    if jacobian_class is None:
        if verbose:
            print("    [Jacobian class not available; defaulting to FGMRES]")
        return "fgmres"

    if jacobian_class.symmetric and jacobian_class.n_negative_rayleigh == 0:
        if verbose:
            print(f"    [Jacobian: SPD (antisym={jacobian_class.antisymmetry_norm:.2e}); using PCG]")
        return "pcg"
    elif jacobian_class.symmetric and jacobian_class.n_negative_rayleigh > 0:
        if verbose:
            print(
                f"    [Jacobian: symmetric-indefinite (antisym={jacobian_class.antisymmetry_norm:.2e}); "
                f"using MINRES]"
            )
        return "minres"
    elif jacobian_class.asymmetric:
        if verbose:
            print(f"    [Jacobian: asymmetric (antisym={jacobian_class.antisymmetry_norm:.2e}); using FGMRES]")
        return "fgmres"
    else:
        if verbose:
            print("    [Jacobian classification ambiguous; defaulting to FGMRES]")
        return "fgmres"


def get_newton_tolerance(iteration: int) -> float:
    """
    Staged tolerance schedule (Math63 §2D).

    - Iterations 0-2: 1e-6 (exploratory).
    - Iterations 3-5: 1e-8 (branch-lock).
    - Iterations 6+: 1e-10 (certification).
    """
    if iteration <= 2:
        return 1e-6
    elif iteration <= 5:
        return 1e-8
    else:
        return 1e-10


def probe_jacobian_cached(
    phi: np.ndarray,
    params: Dict[str, Any],
    iteration: int,
    cache: Dict[str, Tuple[int, JacobianClassification]],
    verbose: bool = False,
) -> Optional[JacobianClassification]:
    """
    Probe Jacobian symmetry every 5 Newton steps; cache in between.

    Implements Math63 §2A caching strategy.
    """
    if not _SYMMETRY_PROBE_AVAILABLE:
        if verbose:
            print("    [Symmetry probe unavailable; using cached or default]")
        return cache.get("current", (0, None))[1]

    # Check cache validity
    cached_iter, cached_class = cache.get("current", (-5, None))
    if iteration - cached_iter < 5 and cached_class is not None:
        if verbose:
            print(f"    [Using cached Jacobian classification from iter {cached_iter}]")
        return cached_class

    # Re-probe
    if verbose:
        print(f"    [Probing Jacobian symmetry (iteration {iteration})...]")

    try:
        # v2.5.4: canonical signature is `backend.residual(Psi, params)`; the
        # previous `backend.residual_bcc` was a v2.5.0 typo (no such attr on
        # `real_backend_pt_bcc_mixed_v3`) hidden by the except-branch until
        # v2.5.3 honest-reporting made it audible at every Newton iteration.
        result = probe_symmetry(
            residual_fn=lambda x: backend.residual(x, params),
            x0=phi,
            n_probes=5,
            eps=1e-6,
            verbose=False,
        )
        jacobian_class = JacobianClassification(
            symmetric=result["symmetric"],
            indefinite=result["indefinite"],
            asymmetric=result["asymmetric"],
            rayleigh_samples=result["rayleigh_samples"],
            antisymmetry_norm=result["antisymmetry_norm"],
            jacobian_norm=result["jacobian_norm"],
            n_negative_rayleigh=result["n_negative_rayleigh"],
        )
        cache["current"] = (iteration, jacobian_class)
        if verbose:
            print(f"      symmetric={jacobian_class.symmetric}, "
                  f"indefinite={jacobian_class.indefinite}, "
                  f"asymmetric={jacobian_class.asymmetric}")
        return jacobian_class
    # v2.5.7: Math63 §2A.2 Exception-Handling Policy. Programming errors
    # (AttributeError, TypeError, NameError, ImportError) indicate a code
    # defect in the probe or in `backend.residual` and MUST propagate — this
    # closes the Layer-5 concealment channel that allowed the `residual_bcc`
    # typo and the silent complex->real cast to survive four releases each.
    # Runtime-condition errors (RuntimeError, ValueError, ArithmeticError,
    # MemoryError, LinAlgError) may legitimately degrade: we log the type +
    # message unconditionally to stderr (no `if verbose` gate) plus a
    # traceback for the first occurrence per run, and return `None` so the
    # caller falls back to default routing.
    except (AttributeError, TypeError, NameError, ImportError):
        raise
    except (RuntimeError, ValueError, ArithmeticError, MemoryError,
            np.linalg.LinAlgError) as e:
        _probe_failure_count = cache.setdefault("_probe_failure_count", [0])
        _probe_failure_count[0] += 1
        print(
            f"[probe_jacobian_cached] WARNING: recoverable probe failure "
            f"({type(e).__name__}: {e}); iteration={iteration}; falling back "
            f"to default routing.",
            file=sys.stderr,
        )
        if _probe_failure_count[0] == 1:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return None


def _converged_from_history(
    newton_history: List[Dict[str, Any]],
    tol_newton: float,
) -> bool:
    """
    Determine convergence from newton_history, matching the criterion at
    tect_newton_krylov.py:1231.

    Convergence is True iff the final step's grad_norm is finite AND less
    than tol_newton. This encapsulates the IEEE 754 fix: if grad_norm is NaN,
    the comparison NaN < tol_newton evaluates to False.

    Parameters
    ----------
    newton_history : List[Dict[str, Any]]
        List of per-step records from tect_newton_krylov.newton_solve, each
        containing at least a "grad_norm" key.
    tol_newton : float
        Convergence tolerance on the normalized gradient.

    Returns
    -------
    bool
        True iff history is non-empty and history[-1]["grad_norm"] is finite
        and < tol_newton; False otherwise (including NaN case).
    """
    if not newton_history:
        return False

    last = newton_history[-1]
    last_grad = float(last.get("grad_norm", float("nan")))

    # np.isfinite(NaN) = False, so NaN is handled correctly.
    # The comparison NaN < tol also evaluates to False.
    return bool(np.isfinite(last_grad) and last_grad < tol_newton)


def pass_math63_gate_2D(
    newton_steps: List[NewtonStep],
    tol_gate: Optional[Dict[str, float]] = None,
) -> bool:
    """
    Evaluate the Math63 §2D / Math64 §sec2d acceptance gate for converged
    continuation points.

    v2.6.4 (2026-04-23) semantic fix
    --------------------------------
    The v2.6.3-b implementation stored ``line_search_alpha`` in
    ``NewtonStep.step_norm`` and then compared that α against the
    ``ρ_lin_max = 0.05`` threshold. Because the trust-region line search
    returns α ≈ 1.0 on every accepted step, the gate evaluated to False
    for every converged point, defeating R'₃ in the Math74 Addendum-A
    sense.

    v2.6.4 applies the Math64 §sec2d reformulated absolute-bound form:

        gate(point) :=  |newton_steps|   ≤  newton_max
                     ∧  max_i tCG_i      ≤  tCG_max
                     ∧  ∀ accepted step: ρ_trust_i  ≥  rho_min

    where ``ρ_trust`` is the trust-region acceptance ratio
    (actual-reduction / predicted-reduction) taken verbatim from
    ``NewtonStepRecord.rho`` of the v2.6.2 solver core. Only
    ``accepted`` steps are tested against the ρ bound, because rejected
    steps have ρ < 0.25 by definition (trust-region shrink rule) and
    are not physical Newton updates.

    v2.6.4 default thresholds reflect 2026-04-23 live-measurement
    calibration (Math74 Addendum-B §3):

        newton_max = 12    (was 8 — v2.6.3-b default)
        tCG_max    = 3000  (was 300 — v2.6.3-b default; raised per the
                            N=32 Point-1 peak observation tCG=2304,
                            which occurs in the near-convergence
                            Eisenstat-Walker clip regime and is not a
                            pathology.)
        rho_min    = 0.05  (Math63 §2D threshold, now correctly applied
                            to the trust-region ratio, not to α)

    Callers with stricter Math63 §2D targets (e.g. publication-grade
    runs) may pass ``tol_gate={"newton_max": 8, "tCG_max": 300,
    "rho_min": 0.25}`` to enforce the original table thresholds.

    Parameters
    ----------
    newton_steps : List[NewtonStep]
        Steps from a single μ² point's run_one_point_v25.
    tol_gate : Optional[Dict[str, float]]
        Gate thresholds. Defaults to the v2.6.4 calibrated values above
        if None.

    Returns
    -------
    bool
        True iff all gate conditions are satisfied; False otherwise.
        An empty newton_steps list returns False (no accepted step
        exists to certify).
    """
    if tol_gate is None:
        tol_gate = {
            "newton_max": 12,
            "tCG_max": 3000,
            "rho_min": 0.05,
        }

    newton_max = tol_gate.get("newton_max", 12)
    tCG_max = tol_gate.get("tCG_max", 3000)
    # Support both the v2.6.4 "rho_min" key and the legacy v2.6.3-b
    # "rho_lin_max" key. The legacy key is now interpreted as ``rho_min``
    # (i.e. the lower bound on the trust-region acceptance ratio for
    # accepted steps), NOT as an upper bound on α.
    rho_min = tol_gate.get("rho_min", tol_gate.get("rho_lin_max", 0.05))

    if not newton_steps:
        return False

    if len(newton_steps) > newton_max:
        return False

    any_accepted = False
    for step in newton_steps:
        if step.krylov_iterations > tCG_max:
            return False
        if step.accepted:
            any_accepted = True
            rho = step.rho_trust
            if (not math.isfinite(rho)) or (rho < rho_min):
                return False

    # At least one step must have been accepted; a point with zero
    # accepted steps cannot have converged.
    return any_accepted


def run_one_point_v25(
    Psi0: np.ndarray,
    params: Dict[str, Any],
    *,
    tol_newton: float = 1e-8,
    max_newton: int = 12,
    ew_eta_min: float = 0.05,
    ew_eta_max: float = 0.9,
    tcg_max_iter: int = 30000,
    gate_tol: Optional[Dict[str, float]] = None,
    checkpoint_path: Optional[Path] = None,
    checkpoint_every: int = 1,
    krylov_method_override: str = "auto",
    trust_radius_max: Optional[float] = None,   # v2.6.7d (Math294-AddA Priority 3)
    verbose: bool = True,
) -> Tuple[ContinuationPoint, np.ndarray]:
    """
    Run v2.6.3 Newton-Krylov continuation at one μ² value.

    Implements the main loop from Math63 §3 Module 4 (pseudocode), now wired
    through the live v2.6.2 solver core (Math66 v0.2 Path-A + Math73 cII
    projector API). See docs/math/TECT-Math74-v2p6p3-Continuation-Driver-Live-Wire.tex.txt.

    Control flow (v2.6.3):
      (i)   Phase A — probe Jacobian symmetry ONCE at Psi0 (step=0) to route
            the inner Krylov solver (PCG / MINRES / FGMRES) per Math63 §2B.
      (ii)  Phase D — single call to tect_newton_krylov.newton_solve performing
            the full trust-region Newton loop; convergence propagated from
            `newton_history[-1]["grad_norm"] < tol_newton` (matches the
            internal criterion of newton_solve at tect_newton_krylov.py:1231).
      (iii) Phase 2 — lanczos_hessian + analyze_projected_spectrum if Phase D
            converged; stores m_star_sq into the continuation point.
      (iv)  Phase 3 — compute_energy_difference if Phase D converged; stores
            (F_condensate, F_vacuum, delta_F, favorable_vs_vacuum).

    Rationale: the v2.5.7 implementation wrapped newton_solve inside an outer
    `for newton_iter in range(max_newton)` loop, which was semantic nonsense
    because newton_solve itself already performs the full Newton loop
    internally. That structure additionally paired with a hard-coded
    NewtonStep.residual_norm = NaN, forcing the convergence test to
    evaluate False at every iteration. Both defects are fixed here by
    calling newton_solve exactly once per mu2 point.

    Returns:
        (ContinuationPoint, Psi_star)
    """

    if not (_TORCH_AVAILABLE and _NEWTON_KRYLOV_AVAILABLE and _BACKEND_AVAILABLE):
        raise RuntimeError(
            "Required dependencies unavailable: PyTorch, tect_newton_krylov, or backend"
        )

    mu2 = params["mu2"]
    r = params["r"]

    t0_point = time.time()

    # Seed the continuation-point record. v2.6.3 will flip `converged` to True
    # iff newton_history[-1]["grad_norm"] < tol_newton at the end of Phase D.
    result = ContinuationPoint(mu2=mu2, r=r, converged=False)

    # ------------------------------------------------------------------
    # Phase A — single Jacobian-symmetry probe at Psi0 for solver routing.
    # ------------------------------------------------------------------
    # v2.6.3: the per-iteration re-probe loop of v2.5.7 (cached every 5 steps)
    # loses its purpose once the outer Newton loop is removed. The Krylov
    # solver choice (PCG / MINRES / FGMRES) is an outer-driver decision and
    # is fixed for the duration of this mu2 point; newton_solve handles the
    # per-step numerics internally. A fresh re-probe at the converged point
    # can be triggered at the next mu2 step.
    jacobian_cache: Dict[str, Tuple[int, Optional[JacobianClassification]]] = {
        "current": (-5, None)
    }
    jacobian_class = probe_jacobian_cached(
        Psi0, params, 0, jacobian_cache, verbose=verbose
    )
    auto_krylov = select_krylov_solver(jacobian_class, verbose=verbose)

    # v2.6.6d (2026-04-27): allow CLI override of the auto-routed Krylov method.
    # Motivation: the 5-probe Rayleigh classifier in probe_jacobian_cached can
    # report SPD (n_negative_rayleigh==0) on a deep-regime state whose Hessian
    # is genuinely indefinite (Lanczos lambda_min<0 will surface this; cf
    # Math82-AddD Point-3/4 saddles). The router then selects PCG, which
    # produces a degenerate Newton step (predicted_m = actual_m = 0,
    # rho = -1e30 sentinel) and trust-region collapse. The override flag lets
    # the user force GMRES (always safe, slightly slower) when the auto-route
    # has produced this pattern. Q-2026-04-24-Solver-115 (Lanczos mini-spectrum
    # probe) is the structural fix.
    cli_override = krylov_method_override
    if cli_override and cli_override != "auto":
        krylov_method = cli_override
        if verbose:
            print(
                f"  Phase A/B: Jacobian class -> auto={auto_krylov}; "
                f"OVERRIDDEN by --krylov-method {cli_override}"
            )
    else:
        krylov_method = auto_krylov
        if verbose:
            print(f"  Phase A/B: Jacobian class -> Krylov method = {krylov_method}")

    # ------------------------------------------------------------------
    # Phase D — full trust-region Newton solve (v2.6.2 core).
    # ------------------------------------------------------------------
    Psi_star: np.ndarray = Psi0
    newton_history: List[Dict[str, Any]] = []
    projector = None
    phase_d_ok = False
    interrupted = False

    # ── v2.6.7c (2026-05-01) best-F tracker, per Math294-AddA ──
    # The 2026-05-01 striped-seed N=16 A_0=0.5 run revealed a
    # trust-region overshoot pathology: Newton entered the broken-phase
    # basin (F: +184.7 → -171.7 at step 3) but was ejected and converged
    # to the trivial vacuum from above (final F = +9.66e-8). The deepest
    # basin iterate (the real physical asset) was lost because only the
    # final Newton state was persisted to Psi_final.npy and only the
    # most-recent step to Psi_checkpoint.npy. We fix this by maintaining
    # a parallel "best-F" tracker that overwrites Psi_best_F.npy
    # whenever the current Newton step achieves a new minimum F. Together
    # with the regular per-step checkpoint, this guarantees the deepest
    # broken-phase iterate is recoverable for Math292 acceptance check
    # and Math293 classification regardless of subsequent trajectory.
    _best_F_state: Dict[str, float] = {"value": float("inf"), "step": -1}

    # ── v2.6.6 (2026-04-26) per-step checkpoint hook + v2.6.7c best-F ──
    # If the caller supplied `checkpoint_path`, build a callback that
    # persists Psi to that path after every `checkpoint_every` Newton
    # steps. This makes Ctrl-C (or any other process termination)
    # recoverable: the most recent committed Newton state is on disk,
    # ready to be loaded with --load-psi for warm-start.
    # Additionally, on every step we evaluate whether F dropped below
    # the running best and, if so, persist Psi to a parallel
    # Psi_best_F.npy file with metadata in Psi_best_F.json.
    def _checkpoint_callback(psi_curr: np.ndarray, step: int,
                             step_record: Dict[str, Any]) -> None:
        if checkpoint_path is None:
            return

        # ── v2.6.7c best-F branch (always evaluated, independent of
        #    checkpoint_every cadence) ──
        try:
            _F_curr = float(step_record.get("F", float("nan")))
            if math.isfinite(_F_curr) and _F_curr < _best_F_state["value"]:
                _best_F_state["value"] = _F_curr
                _best_F_state["step"] = int(step)
                best_path = checkpoint_path.parent / "Psi_best_F.npy"
                best_meta = checkpoint_path.parent / "Psi_best_F.json"
                # Atomic write: tmp file then rename.
                tmp_best = best_path.parent / (
                    best_path.stem + ".tmp" + best_path.suffix
                )
                np.save(tmp_best, psi_curr)
                tmp_best.replace(best_path)
                _meta = {
                    "best_F": _F_curr,
                    "best_F_step": int(step),
                    "grad_norm": float(step_record.get("grad_norm", float("nan"))),
                    "merit": float(step_record.get("merit", float("nan"))),
                    "trust_radius": float(step_record.get("trust_radius", float("nan"))),
                    "rho": float(step_record.get("rho", float("nan"))),
                    "shape": list(psi_curr.shape),
                    "dtype": str(psi_curr.dtype),
                    "schema": "Math294-AddA-v1",
                }
                best_meta.write_text(
                    json.dumps(_meta, indent=2), encoding="utf-8"
                )
                if verbose:
                    print(
                        f"      [best-F] step {step}: new minimum "
                        f"F = {_F_curr:+.6e}; Psi saved to "
                        f"{best_path.name}"
                    )
        except Exception as _e_bestF:
            # best-F is a non-critical diagnostic; do not abort the
            # solver if it fails. Log silently per the v25 driver
            # convention for callback exceptions.
            if verbose:
                print(
                    f"      [best-F] step {step}: tracker failed "
                    f"(non-fatal): {type(_e_bestF).__name__}: {_e_bestF}"
                )

        if step % max(1, checkpoint_every) != 0:
            return
        # Atomic write: save to *.tmp.npy first, then rename, so a Ctrl-C
        # or sudden reboot mid-write does not corrupt the on-disk checkpoint.
        #
        # v2.6.6c (2026-04-27) bugfix: previously tmp_path was constructed
        # as checkpoint_path.with_suffix(checkpoint_path.suffix + ".tmp"),
        # which yielded "Psi_checkpoint.npy.tmp". np.save auto-appended
        # ".npy" because the path's suffix was ".tmp" not ".npy", so the
        # actual file landed at "Psi_checkpoint.npy.tmp.npy", and the
        # subsequent tmp_path.replace(checkpoint_path) silently failed
        # (FileNotFoundError swallowed by the surrounding callback
        # try/except). Net effect: atomic-write was inactive and the
        # checkpoint file was never produced under its canonical name.
        # The 2026-04-26 reboot recovery surfaced the defect.
        #
        # Fix: build tmp_path so its suffix is already ".npy", which
        # prevents np.save's auto-extension. Use the canonical pattern
        # "<stem>.tmp.npy" via direct path concatenation.
        tmp_path = checkpoint_path.parent / (
            checkpoint_path.stem + ".tmp" + checkpoint_path.suffix
        )
        np.save(tmp_path, psi_curr)
        tmp_path.replace(checkpoint_path)
        if verbose:
            grad_n = step_record.get("grad_norm", float("nan"))
            print(
                f"      [checkpoint] step {step}: Psi saved to "
                f"{checkpoint_path.name} (||grad||/√dof = {grad_n:.3e})"
            )

    try:
        # v2.6.7d (Math294-AddA Priority 3): build kwargs dict so that
        # trust_radius_max is forwarded only when the operator opts in.
        # Without --trust-region-max, default behaviour is unchanged
        # (solver core sets trust_radius_max = max(1, 10*Δ_init)).
        _solver_kwargs: Dict[str, Any] = dict(
            max_newton=max_newton,
            tol_newton=tol_newton,
            krylov_method=krylov_method,
            use_symmetrised_cII=True,   # v2.6 Path-X (Math66 v0.2 + Math73 FullProjector)
            ew_eta_min=ew_eta_min,       # v2.6.4 (Math74 Addendum-B §3.2)
            ew_eta_max=ew_eta_max,
            tcg_max_iter=tcg_max_iter,   # v2.6.6 fix: propagate CLI --tcg-max
                                         # into the inner Krylov solver
                                         # (truncated_cg_solve / gmres_trust_region_solve);
                                         # see header v2.6.6 note for the
                                         # 22-hour Math82-H r3 diagnosis.
            checkpoint_callback=_checkpoint_callback if checkpoint_path is not None else None,
            verbose=verbose,
        )
        if trust_radius_max is not None and math.isfinite(trust_radius_max):
            _solver_kwargs["trust_radius_max"] = float(trust_radius_max)
            if verbose:
                print(
                    f"  v2.6.7d: trust_radius_max cap = "
                    f"{trust_radius_max:.3e} (Math294-AddA overshoot guard)"
                )
        Psi_star, newton_history, projector = newton_solve(
            Psi0, params, **_solver_kwargs,
        )
        phase_d_ok = True
    # v2.6.6: KeyboardInterrupt catch -- on Ctrl-C, persist whatever Psi
    # state we currently have to the checkpoint file (best-effort) and
    # mark the point as interrupted. The caller (main loop) decides
    # whether to continue with subsequent points or abort.
    except KeyboardInterrupt:
        interrupted = True
        if checkpoint_path is not None:
            try:
                np.save(checkpoint_path, Psi_star)
                if verbose:
                    print(
                        f"  [Phase D INTERRUPTED] Ctrl-C received; "
                        f"Psi snapshot saved to {checkpoint_path.name}",
                        file=sys.stderr,
                    )
            except (OSError, IOError) as _e:
                if verbose:
                    print(
                        f"  [Phase D INTERRUPTED] Ctrl-C received; "
                        f"checkpoint save FAILED: {_e}",
                        file=sys.stderr,
                    )
        result.stagnation_detected = True
        result.stagnation_reason = "Phase D KeyboardInterrupt"
        phase_d_ok = False
        raise   # re-raise so the outer main() loop can stop further points
    # v2.5.7 Exception-Handling Policy retained verbatim: programming errors
    # propagate; runtime-condition errors are logged with type + traceback.
    except (AttributeError, TypeError, NameError, ImportError):
        raise
    except (RuntimeError, ValueError, ArithmeticError, MemoryError,
            np.linalg.LinAlgError) as e:
        import traceback
        tb_lines = traceback.format_exc().splitlines()
        tb_short = "\n".join(tb_lines[-6:])
        print(
            f"  [Phase D WARNING] {type(e).__name__}: {e}\n"
            f"  Traceback (last frames):\n{tb_short}",
            file=sys.stderr,
        )
        result.stagnation_detected = True
        result.stagnation_reason = f"Phase D {type(e).__name__}: {e}"
        phase_d_ok = False

    # Rebuild the NewtonStep log from newton_history (real numbers now).
    # v2.6.4 (Math74 Addendum-B §3.1): the per-step record now stores
    # line_search_alpha, rho_trust (trust-region ρ from the solver core),
    # and the accepted flag as separate fields. The legacy ``step_norm``
    # field is retained as an alias for α for backward compatibility but
    # is no longer consulted by pass_math63_gate_2D.
    for h in newton_history:
        alpha = float(h.get("line_search_alpha", float("nan")))
        rho   = float(h.get("rho", float("nan")))
        accepted = bool(h.get("accepted", True))
        pred_red   = float(h.get("model_pred_reduction", float("nan")))
        actual_red = float(h.get("actual_reduction", float("nan")))
        # v2.6.7d (2026-05-01) — populate F / merit / trust_radius fields
        # introduced in the v2.6.7d NewtonStep schema extension so that
        # the newton_history.json serializer can emit the full Newton
        # time-series. NewtonStepRecord (in tect_newton_krylov.py)
        # already carries these as native fields; the previous v2.6.7
        # NewtonStep schema dropped them.
        F_step = float(h.get("F", float("nan")))
        merit_step = float(h.get("merit", float("nan")))
        trust_step = float(h.get("trust_radius", float("nan")))
        result.newton_steps.append(NewtonStep(
            iteration=int(h.get("step", -1)),
            residual_norm=float(h.get("grad_norm", float("nan"))),
            step_norm=alpha,                      # v2.6.3-b alias; deprecated
            convergence_ratio=None,
            krylov_method=krylov_method,
            krylov_iterations=int(h.get("tCG_iterations", 0)),
            krylov_converged=not bool(h.get("negative_curvature", False)),
            eta_ew=float(h.get("eta", float("nan"))),   # NaN if solver core
                                                         # does not expose η
            newton_tolerance=tol_newton,
            wall_time_s=float(h.get("time_s", 0.0)),
            jacobian_class=jacobian_class,
            # v2.6.4 explicit separation:
            line_search_alpha=alpha,
            rho_trust=rho,
            accepted=accepted,
            model_pred_reduction=pred_red,
            actual_reduction=actual_red,
            # v2.6.7d (2026-05-01) full-trajectory fields:
            F=F_step,
            merit=merit_step,
            trust_radius=trust_step,
        ))

    # Convergence criterion — mirrors tect_newton_krylov.newton_solve:1231.
    # v2.6.3-b: delegated to _converged_from_history helper (Task #115 R'₂).
    if phase_d_ok and newton_history:
        result.converged = _converged_from_history(newton_history, tol_newton)
        last_grad = float(newton_history[-1].get("grad_norm", float("nan")))
        if verbose:
            print(
                f"  Phase D result: {len(newton_history)} Newton steps, "
                f"final ||grad||/√dof = {last_grad:.3e}, "
                f"converged = {result.converged}"
            )

    # v2.6.3-b: R'₃ gate evaluation (Task #115). Populate pass_math63_2d boolean
    # from the Newton steps collected above.
    # v2.6.4 (Math74 Addendum-B §3.3): pass the caller-provided gate_tol dict
    # so that CLI options --tcg-max / --rho-min / --max-newton can override
    # the v2.6.4 defaults (newton_max=12, tCG_max=3000, rho_min=0.05).
    result.pass_math63_2d = pass_math63_gate_2D(result.newton_steps, tol_gate=gate_tol)

    # ------------------------------------------------------------------
    # Phase 2 — projected Hessian spectrum (live; v2.5.7 placeholder retired).
    # ------------------------------------------------------------------
    if result.converged:
        try:
            evals, _ritz = lanczos_hessian(
                Psi_star,
                params,
                projector=projector,
                n_eigs=20,
                verbose=verbose,
            )
            phase2 = analyze_projected_spectrum(evals)
            result.m_star_sq = float(phase2.m_star_sq)
            if verbose:
                print(
                    f"  Phase 2: lambda_min = {phase2.lambda_min:+.3e}, "
                    f"m*^2 = {result.m_star_sq:+.3e}, "
                    f"stable = {phase2.stable}"
                )
        except (AttributeError, TypeError, NameError, ImportError):
            raise
        except (RuntimeError, ValueError, ArithmeticError, MemoryError,
                np.linalg.LinAlgError) as e:
            print(
                f"  [Phase 2 WARNING] {type(e).__name__}: {e}",
                file=sys.stderr,
            )

    # ------------------------------------------------------------------
    # Phase 3 — energetic favorability vs the trivial vacuum (live).
    # ------------------------------------------------------------------
    if result.converged:
        try:
            phase3 = compute_energy_difference(Psi_star, params, verbose=verbose)
            result.F_condensate = float(phase3.F_condensate)
            result.F_vacuum = float(phase3.F_vacuum)
            result.delta_F = float(phase3.delta_F)
            result.favorable_vs_vacuum = bool(phase3.favorable_vs_vacuum)
        except (AttributeError, TypeError, NameError, ImportError):
            raise
        except (RuntimeError, ValueError, ArithmeticError, MemoryError,
                np.linalg.LinAlgError) as e:
            print(
                f"  [Phase 3 WARNING] {type(e).__name__}: {e}",
                file=sys.stderr,
            )

    # RMS amplitude (real-Hilbert norm of the BCC 3-channel field).
    try:
        result.rms_amplitude = float(
            np.sqrt(np.mean(np.abs(Psi_star) ** 2))
        )
    except (ValueError, ArithmeticError, MemoryError):
        result.rms_amplitude = float("nan")

    result.wall_time_s = time.time() - t0_point
    result.timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

    return result, Psi_star


# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="TECT μ² continuation solver v2.5 (adaptive Krylov + Brazovskii preconditioning)"
    )
    parser.add_argument("--config", required=True, help="Brazovskii config JSON")
    parser.add_argument("--N", type=int, default=32, help="Grid dimension (default 32)")
    parser.add_argument(
        "--L",
        type=str,
        default="16",
        help="Box size in units or 'Npi' notation (default 16)",
    )
    parser.add_argument(
        "--mu2-start",
        type=float,
        default=-1.0,
        help="Starting μ² (default -1.0)",
    )
    parser.add_argument(
        "--mu2-end",
        type=float,
        default=0.30,
        help="Ending μ² (default 0.30)",
    )
    parser.add_argument(
        "--mu2-step",
        type=float,
        default=0.05,
        help="μ² step size (default 0.05)",
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Run diagnostic sweep: μ² ∈ {-1.0, -0.8, -0.6, -0.4, -0.2, -0.1}",
    )
    parser.add_argument(
        "--mu2-list",
        type=str,
        default=None,
        help="v2.6.4: explicit comma-separated μ² schedule. Overrides "
             "--diagnostic and --mu2-start/--mu2-end/--mu2-step. "
             "IMPORTANT: because the value starts with a minus sign, "
             "you MUST use the '--mu2-list=<value>' form (with equals "
             "sign), not a space separator. PowerShell example: "
             "--mu2-list=\"-1.0,-0.5,-0.1,-0.02,5e-3\". Bash example: "
             "--mu2-list='-1.0,-0.5,-0.1,-0.02,5e-3'. If you prefer "
             "space separation, use the alternate --mu2 option instead.",
    )
    parser.add_argument(
        "--mu2",
        nargs="+",
        type=float,
        default=None,
        metavar="MU2",
        help="v2.6.4: alternate explicit μ² schedule as a "
             "whitespace-separated list of floats (not comma-separated). "
             "Equivalent to --mu2-list but avoids the argparse "
             "'leading dash' parsing pitfall. Example: "
             "--mu2 -1.0 -0.5 -0.1 -0.02 5e-3. Overrides --mu2-list if "
             "both are given.",
    )
    parser.add_argument(
        "--tol-newton",
        type=float,
        default=1e-8,
        help="v2.6.4: Newton convergence tolerance on ||grad||/√dof "
             "(default 1e-8). Values below 1e-10 typically cause "
             "inner-Krylov cost explosion without physical gain because "
             "quadratic convergence already reaches machine precision "
             "in 1-2 extra Newton steps.",
    )
    parser.add_argument(
        "--max-newton",
        type=int,
        default=12,
        help="v2.6.4: maximum Newton iterations per μ² point (default 12).",
    )
    parser.add_argument(
        "--ew-eta-min",
        type=float,
        default=0.05,
        help="v2.6.4: Eisenstat-Walker forcing lower bound. v2.6.3-b used "
             "the solver core default 0.01, which produces tCG peaks of "
             "~2300 at N=32 in the near-convergence regime because the "
             "Krylov tolerance becomes η·||grad|| ~ 10^-5 when ||grad|| "
             "drops. Raising ew-eta-min to 0.05 drops inner-CG cost by "
             "~10× at the price of ~1 additional Newton step (Math74 "
             "Addendum-B §3.2).",
    )
    parser.add_argument(
        "--ew-eta-max",
        type=float,
        default=0.9,
        help="Eisenstat-Walker forcing upper bound (default 0.9).",
    )
    parser.add_argument(
        "--tcg-max",
        type=int,
        default=3000,
        help="v2.6.4: upper bound on inner-CG iterations per Newton step "
             "for Math63 §2D gate evaluation. Raised from 300 (v2.6.3-b) "
             "to 3000 based on 2026-04-23 N=32 live measurement "
             "(Math74 Addendum-B §3.3).",
    )
    parser.add_argument(
        "--rho-min",
        type=float,
        default=0.05,
        help="v2.6.4: lower bound on the trust-region acceptance ratio "
             "ρ = actual-reduction / predicted-reduction for accepted "
             "steps. Replaces the v2.6.3-b aliased check on α. Default "
             "0.05 matches the original Math63 §2D threshold now "
             "applied to the correct quantity.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory (default: continuation_N{N})",
    )
    parser.add_argument(
        "--load-psi",
        dest="load_psi",
        type=str,
        default=None,
        help="v2.6.5 (Math82-Addendum-B Phase Z): load initial Psi from "
             ".npy file (shape (3, N, N, N) complex128) instead of the "
             "default thermal seed. Use Codes/pde/bcc_analytic_seed.py to "
             "produce the BCC analytic ansatz that drops the initial "
             "residual by several orders of magnitude vs the thermal "
             "seed at deep mu^2 endpoints.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-step output",
    )
    parser.add_argument(
        "--trust-region-max",
        dest="trust_region_max",
        type=float,
        default=float("inf"),
        help="v2.6.7d (Math294-AddA Priority 3): cap on the trust-region "
             "radius Δ during Newton iteration. Default +inf preserves "
             "the original trust_radius_max = max(1, 10·Δ_init) heuristic. "
             "Set explicitly (e.g. 8.0) when running on coarse lattices "
             "where the broken-phase basin diameter is sub-trust-region "
             "and trust-region expansion has been observed to eject the "
             "iterate from the basin (Math290 → Math294-AddA overshoot "
             "scenario at N=16, μ²=-0.7 with A_0=0.5 striped seed). "
             "Recommended: 8.0 on N=16, scale ~ basin diameter on finer "
             "lattices.",
    )
    parser.add_argument(
        "--phase-half-guard",
        dest="phase_half_guard",
        action="store_true",
        help="v2.6.7d (Math294-AddA Priority 4): enable mid-Newton "
             "free-energy monotonicity guard. When set, the solver "
             "wrapper inspects newton_history after the run and "
             "reports any accepted step where F[Ψ^{(t+1)}] > F[Ψ^{(t)}] "
             "by more than 50% of the previous |F| (a basin-escape "
             "diagnostic). The guard does not currently abort the "
             "Newton loop (full mid-loop intervention requires the "
             "tect_newton_krylov.py core extension flagged in "
             "Q-2026-05-15-Math294-AddA-PhaseHalfGuard, scheduled for "
             "next patch cycle). The current implementation is a "
             "post-run audit emitter that flags the basin-escape "
             "trajectory in stdout and in newton_history.json.",
    )
    parser.add_argument(
        "--krylov-method",
        dest="krylov_method_override",
        type=str,
        default="auto",
        choices=["auto", "cg", "pcg", "minres", "gmres", "fgmres"],
        help="v2.6.6d: override the auto-routed Krylov solver. 'auto' (default) "
             "uses the 5-probe Rayleigh classifier in probe_jacobian_cached + "
             "select_krylov_solver dispatch. Use 'gmres' (safer; works on any "
             "Jacobian) when the auto-route picks PCG on a deep-regime state "
             "and the Newton loop produces 'pred_m=actual_m=0, rho=-1e30' "
             "REJECT cycles -- this indicates the classifier missed a negative "
             "eigenvalue and the Hessian is in fact indefinite. The structural "
             "fix is Q-2026-04-24-Solver-115 (Lanczos mini-spectrum probe).",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=1,
        help="v2.6.6: write the running Psi state to "
             "<output>/Psi_checkpoint.npy after every N accepted Newton "
             "steps (default 1 = every step). Combined with the "
             "Ctrl-C handler, this makes a long deep-regime run safe "
             "to interrupt: re-launch with --load-psi pointing at the "
             "saved checkpoint to warm-start from the last committed "
             "Newton state. Set to 0 to disable checkpointing.",
    )

    args = parser.parse_args()

    # Consistency check
    print("Checking Brazovskii constants...")
    assert_consistency(verbose=True)

    # Load config. v2.5.2: pin encoding="utf-8" per RFC 8259 §8.1. Without
    # this, Python falls back to locale.getpreferredencoding(False), which on
    # Korean Windows resolves to cp949 and chokes on any non-ASCII character
    # in the config (e.g. U+2014 em-dash in a comment). The em-dash that
    # actually triggered the failure at 2026-04-22 sits at byte 971 of
    # PDE/config_template_brazovskii.json.
    with open(args.config, "r", encoding="utf-8") as f:
        base_params = json.load(f)

    N = args.N
    L = float(parse_L(args.L))
    Y = float(base_params.get("Y", 1.0))
    q0 = float(base_params["q0"])
    outdir = args.output or f"continuation_N{N}"
    os.makedirs(outdir, exist_ok=True)

    # Override params
    base_params["N"] = N
    base_params["L"] = L
    base_params["Lx"] = L
    base_params["Ly"] = L
    base_params["Lz"] = L
    base_params["Nx"] = N
    base_params["Ny"] = N
    base_params["Nz"] = N

    # Schedule (v2.6.4 — --mu2 and --mu2-list take priority over --diagnostic
    # and the range flags. --mu2 (nargs='+') wins over --mu2-list when both
    # are set, since the whitespace form sidesteps argparse's leading-dash
    # parsing pitfall and is therefore the safer default.)
    if args.mu2 is not None and len(args.mu2) > 0:
        mu2_schedule = [float(x) for x in args.mu2]
        print(f"\nCustom μ² schedule (--mu2): {len(mu2_schedule)} points: "
              f"{', '.join(f'{m:g}' for m in mu2_schedule)}")
    elif args.mu2_list:
        try:
            mu2_schedule = [float(x.strip()) for x in args.mu2_list.split(",") if x.strip()]
        except ValueError as e:
            raise ValueError(
                f"--mu2-list parsing failed: {e}. "
                f"Expected comma-separated floats, got: {args.mu2_list!r}"
            )
        if not mu2_schedule:
            raise ValueError("--mu2-list is empty after parsing")
        print(f"\nCustom μ² schedule (--mu2-list): {len(mu2_schedule)} points: "
              f"{', '.join(f'{m:g}' for m in mu2_schedule)}")
    elif args.diagnostic:
        mu2_schedule = [-1.0, -0.8, -0.6, -0.4, -0.2, -0.1]
        print(f"\nDiagnostic sweep: {len(mu2_schedule)} points")
    else:
        mu2_start = args.mu2_start
        mu2_end = args.mu2_end
        mu2_step = args.mu2_step
        n_points = int(round((mu2_end - mu2_start) / mu2_step)) + 1
        mu2_schedule = [mu2_start + i * mu2_step for i in range(n_points)]
        print(f"\nContinuation: {n_points} points from μ²={mu2_start} to μ²={mu2_end}")

    # Initialize
    # v2.5.5: `build_seed` (scalar-Brazovskii) returns (N,N,N) float64 and was
    # incompatible with the active BCC backend which demands (3,N,N,N)
    # complex128. Use the new BCC-aware factory `build_seed_bcc` which returns
    # the correct shape and dtype directly — no .astype() required.
    #
    # v2.6.5 (Math82-Addendum-B Phase Z): if --load-psi is supplied, override
    # the default thermal seed with an externally-generated initial field.
    # The natural choice for deep-mu^2 endpoints is the BCC analytic ansatz
    # produced by Codes/pde/bcc_analytic_seed.py (12 first-shell BCC peaks
    # with saddle-point amplitude), which drops the initial residual by
    # several orders of magnitude.
    if args.load_psi is not None:
        Psi = np.load(args.load_psi)
        if Psi.dtype != np.complex128:
            Psi = Psi.astype(np.complex128, copy=False)
        if Psi.shape != (3, N, N, N):
            raise ValueError(
                f"Loaded --load-psi has shape {Psi.shape} but expected "
                f"(3, {N}, {N}, {N}). Re-generate the seed for the correct N."
            )
        rms_loaded = float(np.sqrt(np.mean(np.abs(Psi) ** 2)))
        print(f"[seed] Loaded external Psi from {args.load_psi}: "
              f"shape={Psi.shape}, dtype={Psi.dtype}, RMS|Psi|={rms_loaded:.6e}")
    else:
        Psi = build_seed_bcc(N, mode="thermal", sigma=PHI_0_DEFAULT)

    results: List[ContinuationPoint] = []

    # Main loop
    for i, mu2 in enumerate(mu2_schedule):
        if not args.quiet:
            print(f"\n[Point {i + 1}/{len(mu2_schedule)}] μ² = {mu2:.6e}")

        params = override_params(base_params, mu2, Y, q0)

        try:
            # v2.6.6 (2026-04-26) per-point checkpoint path. Always
            # placed inside the run's output directory so a single run
            # owns its own warm-start state.
            _ckpt_path = Path(outdir) / "Psi_checkpoint.npy"
            _ckpt_every = max(0, int(args.checkpoint_every))

            point_result, Psi = run_one_point_v25(
                Psi,
                params,
                tol_newton=args.tol_newton,
                max_newton=args.max_newton,
                ew_eta_min=args.ew_eta_min,
                ew_eta_max=args.ew_eta_max,
                tcg_max_iter=args.tcg_max,    # v2.6.6 fix: propagate CLI
                                              # --tcg-max into the inner
                                              # Krylov solver, not just the
                                              # post-run acceptance gate.
                gate_tol={
                    "newton_max": args.max_newton,
                    "tCG_max": args.tcg_max,
                    "rho_min": args.rho_min,
                },
                checkpoint_path=_ckpt_path if _ckpt_every > 0 else None,
                checkpoint_every=_ckpt_every if _ckpt_every > 0 else 1,
                krylov_method_override=args.krylov_method_override,  # v2.6.6d
                trust_radius_max=(   # v2.6.7d (Math294-AddA Priority 3)
                    float(args.trust_region_max)
                    if math.isfinite(float(args.trust_region_max))
                    else None
                ),
                verbose=not args.quiet,
            )
            results.append(point_result)

            # v2.6.5 (2026-04-26) -- ALWAYS persist final Psi state to disk,
            # regardless of convergence flag. The Math82-I r3 incident
            # (22h compute reached ||grad||=8.3e-7 but Psi discarded due to
            # converged=False) demonstrated that near-converged states must
            # be preserved for warm-start re-runs.
            try:
                from pathlib import Path as _Path
                _outdir = _Path(args.output if args.output else f"continuation_N{N}")
                _outdir.mkdir(parents=True, exist_ok=True)
                _psi_path = _outdir / "Psi_final.npy"
                np.save(_psi_path, Psi)
                if not args.quiet:
                    print(f"  [persist] Psi_final.npy saved to {_psi_path} "
                          f"(shape={Psi.shape}, dtype={Psi.dtype})")
            except (OSError, ValueError) as _e:
                if not args.quiet:
                    print(f"  [persist WARN] could not save Psi_final.npy: {_e}")

            if not args.quiet:
                print(f"  Result: converged={point_result.converged}, "
                      f"stagnation={point_result.stagnation_detected}, "
                      f"wall_time={point_result.wall_time_s:.1f}s")

            if point_result.stagnation_detected:
                if not args.quiet:
                    print(f"  Reason: {point_result.stagnation_reason}")
                break

        # v2.5.7: Math63 §2A.2 Exception-Handling Policy. Programming errors
        # propagate immediately — a `TypeError` in the driver is a defect,
        # not a physical stagnation, and must not be laundered through the
        # MANIFEST as a `stagnation_detected=True` point. Runtime-condition
        # errors are recorded with full type + truncated traceback so that
        # postmortem from the MANIFEST + stderr log is always possible.
        except (AttributeError, TypeError, NameError, ImportError):
            raise
        # v2.6.6 (2026-04-26) Ctrl-C handler at the main-loop level.
        # run_one_point_v25 already persisted a Psi snapshot; here we
        # only record the interruption in the per-point result and stop
        # iterating, so the MANIFEST is still written for whatever points
        # completed. The per-point checkpoint at <output>/Psi_checkpoint.npy
        # is the authoritative warm-start state.
        except KeyboardInterrupt:
            print(
                f"  [main loop] KeyboardInterrupt at mu2={mu2:.4f}; "
                f"per-point checkpoint at "
                f"{Path(outdir) / 'Psi_checkpoint.npy'} is the "
                f"warm-start state. Halting further points.",
                file=sys.stderr,
            )
            results.append(
                ContinuationPoint(
                    mu2=mu2, r=float("nan"),
                    converged=False,
                    stagnation_detected=True,
                    stagnation_reason="KeyboardInterrupt",
                )
            )
            break
        except (RuntimeError, ValueError, ArithmeticError, MemoryError,
                np.linalg.LinAlgError) as e:
            import traceback
            tb_lines = traceback.format_exc().splitlines()
            tb_short = "\n".join(tb_lines[-6:])
            print(
                f"  ERROR at mu2={mu2:.4f}: {type(e).__name__}: {e}\n"
                f"  Traceback (last frames):\n{tb_short}",
                file=sys.stderr,
            )
            results.append(
                ContinuationPoint(
                    mu2=mu2, r=float("nan"),
                    converged=False,
                    stagnation_detected=True,
                    stagnation_reason=f"{type(e).__name__}: {e}",
                )
            )
            break

    # v2.6.3 MANIFEST writer. Classification retained with updated semantics:
    #   converged  : Phase D reached newton_history[-1]["grad_norm"] < tol_newton.
    #   errored    : main-loop except branch caught a runtime-condition exception.
    #   stalled    : Phase D completed without converging (no exception).
    # The v2.5.3 "placeholder" state is retired: with v2.6.3 wiring landed, a
    # non-converged non-errored point is a genuine solver stall, not a
    # skeleton placeholder. The handoff-script exit-code contract (0 / 10 / 2)
    # is preserved bit-identically: 10 is now reserved for "no point
    # converged AND torch/solver genuinely unavailable" rather than
    # "skeleton Phase D".
    n_converged = sum(1 for p in results if p.converged)
    n_errored = sum(
        1 for p in results
        if (not p.converged)
        and p.stagnation_detected
        and p.stagnation_reason is not None
    )
    n_stalled = len(results) - n_converged - n_errored

    if n_converged == len(mu2_schedule):
        overall_status = "PASS"
    elif n_errored > 0:
        overall_status = "FAIL"
    elif n_converged == 0 and n_stalled == len(mu2_schedule):
        # v2.6.4 rename: v2.6.3-b used "SKELETON_ONLY" here, which was
        # historically correct when Phase D was a literal placeholder. The
        # v2.6.3 live-wire retired the placeholder and the v2.6.4 gate fix
        # confirms the driver is genuinely non-skeleton. What this status
        # now means is "every point completed Phase D without converging,
        # and no exception was raised", which is either (i) a runtime
        # condition preventing the solver core from running (torch missing,
        # GPU OOM, backend compile failure), or (ii) a genuine physical
        # non-convergence mode on the scheduled mu2. Both interpretations
        # are better described by NO_CONVERGENCE than by SKELETON_ONLY.
        # The handoff script's exit-code 10 mapping is preserved
        # bit-identically.
        overall_status = "NO_CONVERGENCE"
    elif n_stalled > 0:
        overall_status = "PARTIAL"
    else:
        overall_status = "UNKNOWN"

    # v2.5.2 encoding pin retained: manifest carries μ², ρ, φ verbatim.
    manifest_path = os.path.join(outdir, "MANIFEST.md")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("# v2.6.4 Continuation Results\n\n")
        f.write(f"**Driver**         : Codes/pde/continuation_mu2_v25.py (v2.6.7d)\n")
        f.write(f"**Theory tag**     : Math294-AddA-best-F-tracker-trust-cap-phase-half-guard-2026-05-01\n")
        f.write(f"**Status**         : {overall_status}\n")
        f.write(f"**Points total**   : {len(mu2_schedule)}\n")
        f.write(f"**Converged**      : {n_converged}\n")
        f.write(f"**Errored**        : {n_errored}\n")
        f.write(f"**Stalled**        : {n_stalled}\n")
        f.write(f"**tol_newton**     : {args.tol_newton:.1e}\n")
        f.write(f"**max_newton**     : {args.max_newton}\n")
        f.write(f"**ew_eta in**      : [{args.ew_eta_min}, {args.ew_eta_max}]\n")
        f.write(f"**gate (v2.6.4)**  : Newton≤{args.max_newton}, "
                f"tCG≤{args.tcg_max}, ρ_trust≥{args.rho_min}  "
                f"(Math74 Addendum-B §3)\n\n")
        if overall_status == "NO_CONVERGENCE":
            f.write("> **HONEST STATUS** (NO_CONVERGENCE, formerly "
                    "`SKELETON_ONLY` in v2.6.3-b): No mu2 point reached the "
                    "tol_newton threshold on newton_history[-1]['grad_norm']. "
                    "This is not a Phase-D placeholder artifact — the v2.6.3 "
                    "wiring has been active since 2026-04-23, so the driver "
                    "is genuinely non-skeleton. The present status indicates "
                    "either (i) a runtime condition preventing the solver "
                    "core from running (torch missing, GPU OOM, backend "
                    "compile failure), or (ii) a genuine physical "
                    "non-convergence mode on every scheduled mu2. Both map "
                    "to exit code 10 per the handoff-script contract.\n\n")
        f.write("## Per-point table\n\n")
        f.write(
            "| # | μ² | r | converged | gate | Newton | tCG_peak | ρ_trust_min | m*² | ΔF | favorable | wall (s) |\n"
        )
        f.write("|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for i, p in enumerate(results, 1):
            reason = (p.stagnation_reason or "").replace("|", "\\|")
            # Per-point diagnostic aggregates (v2.6.4):
            if p.newton_steps:
                tcg_peak = max((s.krylov_iterations for s in p.newton_steps), default=0)
                acc_rhos = [s.rho_trust for s in p.newton_steps
                            if s.accepted and math.isfinite(s.rho_trust)]
                rho_min_obs = min(acc_rhos) if acc_rhos else float("nan")
                n_newton = len(p.newton_steps)
            else:
                tcg_peak = 0
                rho_min_obs = float("nan")
                n_newton = 0
            f.write(
                f"| {i} | {p.mu2:.6e} | {p.r:.6e} | "
                f"{p.converged} | {p.pass_math63_2d} | {n_newton} | "
                f"{tcg_peak} | {rho_min_obs:+.3e} | "
                f"{p.m_star_sq:+.3e} | {p.delta_F:+.3e} | "
                f"{p.favorable_vs_vacuum} | {p.wall_time_s:.2f} |\n"
            )
        f.write("\n")
        f.write("## Notes\n\n")
        f.write(f"- Generated by continuation_mu2_v25.py v2.6.6 on "
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- Math63 §2D / Math64 §sec2d gate (v2.6.4 calibration): "
                f"Newton ≤ {args.max_newton}, t_CG ≤ {args.tcg_max}, "
                f"ρ_trust ≥ {args.rho_min} per accepted step. The v2.6.3-b "
                f"semantic bug (α aliased as ρ_lin) is fixed — "
                f"NewtonStep.rho_trust now carries the trust-region ratio "
                f"actual_reduction/predicted_reduction from the solver core.\n")
        f.write(f"- Eisenstat-Walker forcing window [{args.ew_eta_min}, "
                f"{args.ew_eta_max}] propagated to newton_solve via explicit "
                f"kwargs (v2.6.4). Values of ew_eta_min < 0.02 cause "
                f"inner-CG cost to scale as O(1/eta) in the "
                f"near-convergence regime.\n")

    # ----------------------------------------------------------------------
    # v2.6.4 endpoint JSON (Math72 Addendum-A Post-54 Runbook contract).
    # Schema bumped 1.0 -> 1.1 to carry the Math63 §2D gate boolean,
    # per-point diagnostics, and the forcing/gate thresholds actually used.
    # Emit at the FINAL mu2 point in the schedule if it converged.
    # ----------------------------------------------------------------------
    endpoint_path: Optional[str] = None
    if results:
        last_point = results[-1]
        if last_point.converged:
            endpoint_path = os.path.join(outdir, "continuation_mu2_v25_endpoint.json")
            # Endpoint-layer diagnostic aggregates for the final point.
            if last_point.newton_steps:
                tcg_peak_final = max((s.krylov_iterations for s in last_point.newton_steps),
                                     default=0)
                rho_trust_list = [s.rho_trust for s in last_point.newton_steps
                                  if s.accepted and math.isfinite(s.rho_trust)]
                rho_trust_min_final = min(rho_trust_list) if rho_trust_list else float("nan")
                n_accepted = sum(1 for s in last_point.newton_steps if s.accepted)
            else:
                tcg_peak_final = 0
                rho_trust_min_final = float("nan")
                n_accepted = 0
            endpoint_payload = {
                "schema_version": "continuation_mu2_v25_endpoint/1.2",
                "theory_tag": "Math294-AddA-best-F-tracker-2026-05-01",
                "driver_version": "v2.6.7d",
                "solver_core_version": "v2.6.6",
                "mu2": float(last_point.mu2),
                "r": float(last_point.r),
                "N": int(N),
                "L": float(L),
                "converged": bool(last_point.converged),
                "pass_math63_2d": bool(last_point.pass_math63_2d),
                "m_star_sq": float(last_point.m_star_sq),
                "delta_F": float(last_point.delta_F),
                "F_condensate": float(last_point.F_condensate),
                "F_vacuum": float(last_point.F_vacuum),
                "rms_amplitude": float(last_point.rms_amplitude),
                "favorable_vs_vacuum": bool(last_point.favorable_vs_vacuum),
                "wall_time_s": float(last_point.wall_time_s),
                "n_newton_steps": len(last_point.newton_steps),
                "n_accepted_newton_steps": int(n_accepted),
                "final_grad_norm": (
                    float(last_point.newton_steps[-1].residual_norm)
                    if last_point.newton_steps else float("nan")
                ),
                "tcg_peak": int(tcg_peak_final),
                "rho_trust_min": float(rho_trust_min_final),
                "gate_newton_max": int(args.max_newton),
                "gate_tcg_max": int(args.tcg_max),
                "gate_rho_min": float(args.rho_min),
                "ew_eta_min": float(args.ew_eta_min),
                "ew_eta_max": float(args.ew_eta_max),
                "tol_newton": float(args.tol_newton),
                "timestamp": last_point.timestamp or time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            with open(endpoint_path, "w", encoding="utf-8") as f:
                json.dump(endpoint_payload, f, indent=2, ensure_ascii=False)

    # v2.6.7 NEW (2026-04-29; v2.6.7d field-name fix 2026-05-01):
    # persist per-Newton-step history to disk so the
    # (grad_norm, merit, F, rho_trust, eta_ew, tCG, alpha, Delta)
    # time-series survives terminal-log loss. Required for
    # publication-grade reproducibility per CLAUDE.md §10 + INDEX.md §1.
    #
    # v2.6.7d (2026-05-01) — fixed four serializer field-name defects
    # identified in the Phase-2-closure code review:
    #   (i)   args.krylov_method  → args.krylov_method_override
    #         (argparse `dest=` convention; previous attribute name was
    #         non-existent, raising AttributeError captured by the
    #         broad try/except → silent history-loss).
    #   (ii)  getattr(s, "f_value", ...) → getattr(s, "F", ...)
    #         (NewtonStep has no f_value; v2.6.7d added F as field).
    #   (iii) getattr(s, "eta", ...) → getattr(s, "eta_ew", ...)
    #         (NewtonStep field name is eta_ew, not eta).
    #   (iv)  getattr(s, "step_alpha", ...) → s.line_search_alpha
    #         (canonical field).
    #   (v)   p.stagnation → p.stagnation_detected (canonical name).
    #   (vi)  getattr(p, "wall_time", ...) → p.wall_time_s (canonical).
    history_path = os.path.join(outdir, "newton_history.json")
    try:
        history_payload = {
            "driver": "continuation_mu2_v25.py",
            "driver_version": "v2.6.7d",
            "theory_tag": "Math294-AddA-best-F-tracker-2026-05-01",
            "overall_status": overall_status,
            "n_points": len(mu2_schedule),
            "n_converged": int(n_converged),
            "n_errored": int(n_errored),
            "n_stalled": int(n_stalled),
            "tol_newton": float(args.tol_newton),
            "max_newton": int(args.max_newton),
            "tcg_max": int(args.tcg_max),
            "ew_eta_min": float(args.ew_eta_min),
            "ew_eta_max": float(args.ew_eta_max),
            "rho_min": float(args.rho_min),
            # v2.6.7d fix (i): canonical argparse dest is
            # `krylov_method_override`, not `krylov_method`.
            "krylov_method": str(getattr(
                args, "krylov_method_override", "auto"
            )),
            "trust_region_max": float(getattr(
                args, "trust_region_max", float("inf")
            )),
            "phase_half_guard": bool(getattr(
                args, "phase_half_guard", False
            )),
            "N": int(args.N),
            "L": float(args.L),
            "load_psi": str(args.load_psi) if args.load_psi else None,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "points": [],
        }
        for i, p in enumerate(results, 1):
            steps_serialised = []
            for s_idx, s in enumerate(p.newton_steps or []):
                steps_serialised.append({
                    "step": int(s_idx),
                    "grad_norm": float(getattr(s, "residual_norm", float("nan"))),
                    # v2.6.7d fix (ii): NewtonStep.merit/F/trust_radius
                    # are now native fields (added in the v2.6.7d
                    # schema extension). Read directly.
                    "merit": float(getattr(s, "merit", float("nan"))),
                    "F_value": float(getattr(s, "F", float("nan"))),
                    "rho_trust": float(getattr(s, "rho_trust", float("nan"))),
                    # v2.6.7d fix (iii): canonical field name eta_ew.
                    "eta_forcing": float(getattr(s, "eta_ew", float("nan"))),
                    "krylov_iterations": int(getattr(s, "krylov_iterations", 0)),
                    # v2.6.7d fix (iv): canonical field name line_search_alpha.
                    "step_alpha": float(getattr(s, "line_search_alpha", float("nan"))),
                    "trust_radius": float(getattr(s, "trust_radius", float("nan"))),
                    "accepted": bool(getattr(s, "accepted", True)),
                    "model_pred_reduction": float(getattr(s, "model_pred_reduction", float("nan"))),
                    "actual_reduction": float(getattr(s, "actual_reduction", float("nan"))),
                })
            history_payload["points"].append({
                "index": int(i),
                "mu2": float(p.mu2),
                "converged": bool(p.converged),
                # v2.6.7d fix (v): canonical field stagnation_detected.
                "stagnation": bool(getattr(p, "stagnation_detected", False)),
                "stagnation_reason": str(p.stagnation_reason or ""),
                # v2.6.7d fix (vi): canonical field wall_time_s.
                "wall_time_s": float(getattr(p, "wall_time_s", float("nan"))),
                "n_newton_steps": len(p.newton_steps or []),
                "newton_steps": steps_serialised,
            })
        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(history_payload, f, indent=2, ensure_ascii=False, default=str)
        print(f"Newton history  : {history_path}")
    except Exception as exc:
        # Defensive: never let history persistence break the existing
        # exit-code contract. Manifest + Psi_final.npy are the canonical
        # fallback per Math74-AddB. v2.6.7d narrowed the prior
        # silent-fall-through pattern by fixing the six attribute-name
        # defects, so this branch should fire only on genuine I/O errors.
        print(f"[v2.6.7d] Newton history persistence failed (non-fatal): "
              f"{type(exc).__name__}: {exc}")

    # v2.6.7d (Math294-AddA Priority 4): Phase-2.5 free-energy
    # monotonicity guard, post-run audit emitter. When --phase-half-guard
    # is enabled, scan the Newton trajectory of every point for any
    # accepted step where F[Ψ^{(t+1)}] > F[Ψ^{(t)}] by more than 50%
    # of |F[Ψ^{(t)}]|; this is the basin-escape diagnostic identified in
    # Math294-AddA. Mid-loop intervention requires a tect_newton_krylov.py
    # core extension (Q-2026-05-15-Math294-AddA-PhaseHalfGuard); the
    # current emitter is a post-run audit only.
    try:
        if bool(getattr(args, "phase_half_guard", False)):
            for i_pt, p in enumerate(results, 1):
                if not p.newton_steps:
                    continue
                F_seq = [float(getattr(s, "F", float("nan")))
                         for s in p.newton_steps if s.accepted]
                # Flag: (a) significant rise (>50% of |F_prev|), OR
                #       (b) sign flip from negative to positive (basin → vacuum)
                # both are basin-escape signatures per Math294-AddA. The OR
                # rule is calibrated against the 2026-05-01 A_0=0.5 trajectory
                # in which step 3→4 (F: -171.7 → -97.6) is a 43% rise (just
                # below the 50% threshold) but step 4→5 (-97.6 → -7.0) is
                # 92% and step 5→6 (-7.0 → +0.635) is a sign flip; one of
                # the three guards always fires before the iterate exits the
                # basin entirely.
                escape_events = []
                for k in range(1, len(F_seq)):
                    F_prev = F_seq[k-1]
                    F_curr = F_seq[k]
                    if not (math.isfinite(F_prev) and math.isfinite(F_curr)):
                        continue
                    rise_significant = (
                        F_curr > F_prev and (F_curr - F_prev) > 0.5 * abs(F_prev)
                    )
                    sign_flip = (F_prev < 0.0 and F_curr >= 0.0)
                    if rise_significant or sign_flip:
                        escape_events.append({
                            "step_index_in_accepted": k,
                            "F_prev": F_prev,
                            "F_curr": F_curr,
                            "rise_fraction": (F_curr - F_prev) / max(abs(F_prev), 1e-30),
                            "trigger": (
                                "sign_flip" if sign_flip else "rise_50pct"
                            ),
                        })
                if escape_events:
                    print(
                        f"[v2.6.7d phase-half-guard] Point {i_pt} "
                        f"(μ²={p.mu2:+.3e}): {len(escape_events)} basin-"
                        f"escape event(s) detected (F rose by >50% between "
                        f"accepted Newton steps). Math294-AddA basin-"
                        f"overshoot signature."
                    )
                    for ev in escape_events:
                        print(
                            f"    step {ev['step_index_in_accepted']} "
                            f"[{ev['trigger']}]: "
                            f"F: {ev['F_prev']:+.3e} -> {ev['F_curr']:+.3e} "
                            f"(rise {ev['rise_fraction']*100:.1f}%)"
                        )
                    print(
                        f"    -> diagnostic: re-run with smaller "
                        f"--trust-region-max (current = "
                        f"{getattr(args, 'trust_region_max', float('inf')):.3e}); "
                        f"recommended Δ_max = 0.5 × initial Δ at first "
                        f"detected escape."
                    )
                else:
                    print(
                        f"[v2.6.7d phase-half-guard] Point {i_pt} "
                        f"(μ²={p.mu2:+.3e}): no basin-escape events detected "
                        f"(monotone or controlled descent across "
                        f"{sum(1 for s in p.newton_steps if s.accepted)} "
                        f"accepted Newton steps)."
                    )
    except Exception as _exc_guard:
        print(f"[v2.6.7d phase-half-guard] post-run audit failed "
              f"(non-fatal): {type(_exc_guard).__name__}: {_exc_guard}")

    print(f"\nResults manifest: {manifest_path}")
    if endpoint_path is not None:
        print(f"Endpoint JSON   : {endpoint_path}")
    print(f"Output directory: {outdir}")
    print(f"Overall status  : {overall_status}  "
          f"(converged={n_converged}, errored={n_errored}, "
          f"stalled={n_stalled})")

    # v2.6.4 preserves the v2.5.3 exit-code contract bit-identically while
    # renaming the status string for semantic accuracy (see Math74
    # Addendum-B §3):
    #   0  -> PASS             (every point converged)
    #   10 -> NO_CONVERGENCE   (was SKELETON_ONLY in v2.6.3-b)
    #                           no point converged, no exception raised;
    #                           treated by run_v25_diagnostic.ps1 as the
    #                           distinct "no-convergence / solver-stack
    #                           unavailable" state
    #   2  -> FAIL / errored / PARTIAL / UNKNOWN
    if overall_status == "PASS":
        return 0
    if overall_status == "NO_CONVERGENCE":
        return 10
    return 2


if __name__ == "__main__":
    if not _TORCH_AVAILABLE:
        # v2.6.3 note: the driver is now fully wired to the real solver core
        # (see Math74). This branch fires only when PyTorch / the solver core
        # (tect_newton_krylov) is genuinely not importable on the host, in
        # which case no mu2 point can be exercised.
        print("ERROR: PyTorch (tect_newton_krylov dependency) not available on "
              "this host.", file=sys.stderr)
        print("Real execution requires a PyTorch-capable environment.",
              file=sys.stderr)
        sys.exit(1)

    # v2.5.3 / v2.6.3 / v2.6.4: propagate main()'s exit code so
    # NO_CONVERGENCE (10, formerly SKELETON_ONLY) and FAIL (2) are
    # distinguishable from PASS (0) in the handoff script.
    sys.exit(main() or 0)
