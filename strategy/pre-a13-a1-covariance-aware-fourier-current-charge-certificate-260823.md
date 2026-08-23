# Finite covariance-aware A1 Fourier current charge

## Status and exact scope

This is a T0, claim-nonbearing finite QFT-compatible proxy.  Let (X_p) be
centered proper complex two-component Fourier roots with PSD covariance blocks
(C_p).  For a nonzero output mode (r), set

\[
m_{a,r}=\sum_p X_p^\dagger\sigma_a X_{p+r},\qquad
J_{a,i}(r)=i r_i m_{a,r}.
\]

The registered screen uses one finite block pair and a declared output decay
\(\mathbb E|J_{a,i}(t;r)|^2=e^{-2\lambda_r t}\mathbb E|J_{a,i}(0;r)|^2\).
The charge convention is
\[
q_r=2\int_0^\infty \mathbb E\sum_{a,i}|J_{a,i}(t;r)|^2\,dt.
\]

## Exact Fierz calculation

The Pauli identity gives
\[
\sum_{a=1}^3\operatorname{tr}(\sigma_a C_{p+r}\sigma_a C_p)
=2\operatorname{tr}(C_{p+r})\operatorname{tr}(C_p)
-\operatorname{tr}(C_{p+r}C_p).
\]
For the registered opposite-correlation pair,
\(\operatorname{tr}C_p=\operatorname{tr}C_{p+r}=2\) and
\(\operatorname{tr}(C_{p+r}C_p)=3/2\), hence \(S_r=13/2\).  With
\(|r|^2=1\), charge prefactor 2, decay multiplier 2, and
\(\lambda_r=2\), the exact heat integral is \(1/2\) and
\(q_r=13/4\).  The identity and the heat arithmetic are cross-checked by
Lean `Tect.R201`.

The identity block gives \(S_r=6,q_r=3\); the orthogonal rank-one pair gives
\(S_r=2,q_r=1\).  All are nonnegative, as required for a finite PSD fixture.

## Two-lane and adversarial checks

The primary and independent scripts use exact `Fraction` arithmetic and derive
the trace contractions from the registered matrices.  The integrated verifier
requires equal derived fixtures, source hashes, the Lean source hash, the
finite/no-production boundary, and all eight hostile-mutation clauses.
The mutation clauses specifically forbid dropping the \(\sigma_2\) channel,
splitting the coherent output into root charges, or treating the declared heat
rate as the production rate.

## Non-transfer boundary

This calculation does not identify the A1 production mobility, heat-root
incidence, nonlinear conditional filtration, complement/forest/returned-mean
placement, raw-current spatial intertwiner, or once-owned cutoff-uniform
nonnegative \(q_k\) ledger.  It does not promote the finite Gaussian proxy to
the interacting `F_ref` Gibbs law, and it gives no thermodynamic, continuum,
real-time, physical-empty, Sector-A, Pre-A, A13, or T-050 conclusion.

The correct next obligation is therefore still the first R-192 owner slot:
hash-pin the actual `heat_root_incidence` and rerun the finite formula with
that owner before attempting any q-ledger theorem.

## Reproduction

Run the primary and independent scripts, then the integrated verifier in the
pinned TECT environment.  Run `lean_toolchain_check.py --metadata` and the
registered Lean entrypoint check.  No PDF is issued for this local screen.
