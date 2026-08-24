# EXP-001066 / finite Gibbs-isometric Duhamel remainder

## Decision

For one fixed finite Gibbs Hamiltonian, the separate all-time orbit-envelope
hypothesis used in the earlier finite-member bridge is unnecessary.

Let (H=H^*) be finite dimensional, (U_t=exp(-itH/\hbar)),
(\alpha_t(X)=U_t^*XU_t), and

\[
 \delta_H(X)=\frac{i}{\hbar}[H,X],\qquad
 R_t(X)=\alpha_t(X)-X-t\delta_H(X).
\]

Finite-dimensional differentiation gives

\[
 R_t(X)=\int_0^t (t-s)\,\alpha_s(\delta_H^2(X))\,ds.
\]

If (\rho_\beta=Z^{-1}e^{-\beta H}), the two-sided Gibbs seminorm is
\(\alpha_t\)-isometric.  Hence, for (t\geq0),

\[
 N_\beta(R_t(X))
 \leq \int_0^t(t-s)N_\beta(\delta_H^2(X))\,ds
 =\frac{t^2}{2}N_\beta(\delta_H^2(X)).
\]

The exact fixture uses (H=\operatorname{diag}(0,1)),
(\rho=\operatorname{diag}(2/3,1/3)), (W=\sigma_x), and (\hbar=1).
The second derivation is (-W), both squared seminorms are (2), and at
(t=1/10) the squared remainder envelope is (1/20000).  The primary
SymPy lane, independent Fraction lane and Lean R248 reproduce these exact
values.

## Boundary

This removes only the all-time orbit assumption at fixed finite dimension.  The
constant (N_\beta(\delta_H^2(X))) can depend on volume, source, cutoff and
orientation.  No common OS embedding, direct thermodynamic (D,\delta D)
Cauchy estimate, exhaustion independence, common alpha, KMS/GNS gap,
continuum, Sector A or Pre-A conclusion follows.

## Adversarial review

1. **Generator sign — UPHELD.**  The (i[H,\cdot]/\hbar) convention is used
   consistently; the second commutator's sign does not affect the seminorm.
2. **Gibbs invariance — UPHELD.**  Isometry uses (\rho_\beta=f(H)), not an
   arbitrary fixed state.
3. **Remainder identity — UPHELD.**  The integral formula is finite-dimensional
   and does not hide a uniform orbit estimate.
4. **Orientation — UPHELD.**  Each finite orientation has its own Gibbs state
   and double-commutator constant.
5. **Thermodynamic promotion — UPHELD.**  Finite-dimensional boundedness is not
   promoted to volume/source/cutoff uniformity.
6. **Lean — UPHELD.**  R248 checks exact rational fixtures, not unbounded
   domains or limits.
7. **QFT — UPHELD.**  No OS/KMS/GNS gap, continuum, C6, Sector A or Pre-A
   closure follows.
8. **Negative boundary — UPHELD.**  No global negative authority is added.

## Next gate

Estimate (N_\beta(\delta_H^2(W_a))) for the actual Q3 common core uniformly in
volume/source/cutoff, or record an exact growth obstruction.  Only that result
can feed a direct (D,\delta D) exhaustion theorem.
