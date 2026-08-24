# EXP-001060 / Q3 fifth-moment to endpoint third-moment bridge

## Decision

The endpoint moment hypothesis left conditional by EXP-001059 is discharged in
the already registered fixed-beta, finite-periodic, zero-source Q3 scope.  This
is a bridge to an existing authority, not a new fifth-moment proof.

Let `k_x=h_site-xi_0-delta_1 P_1` be the positive shifted onsite operator from
the R-167 authority, with `k_x>=1`, and let

\[
 e(q)=\frac r2q^2+\frac g4q^4+\frac{r^2}{2g},\qquad
 A_0=\max\left(0,\xi_0+\delta_1+\frac{r^2}{2g}\right).
\]

The onsite form identity gives

\[
 e(q_x)\le k_x+A_0.
\]

For an edge `e=<xy>`, put `E_xy=1+e(q_x)+e(q_y)` and `C_0=1+2A_0`.
Then, by the elementary nonnegative three-term cube inequality,

\[
 E_{xy}^3\le (C_0+k_x+k_y)^3
 \le 9\left(C_0^3+k_x^3+k_y^3\right).
\]

Since `k_x>=1`, functional calculus gives `k_x^3<=k_x^5`.  The registered
R-167/R-168 fifth-moment gate supplies

\[
 m_5=\sup_{\Lambda,x}\varphi_\Lambda(k_x^5)<\infty,
\]

uniformly over the declared periodic volumes and translates.  Therefore

\[
 \boxed{\sup_{\Lambda,x\sim y}\varphi_\Lambda(E_{xy}^3)
 \le M_{\mathrm{bridge}}:=9(C_0^3+2m_5)<\infty.}
\]

This is exactly the moment input needed to instantiate the local force bound in
EXP-001059, without paying the extensive global shift.

## Scope boundary

The result is closed only for the registered fixed-beta finite-periodic
zero-source Q3 family.  A compact-source version needs a separately recorded
uniform affine form-domination bound for its source-dependent `A_0`; it is not
silently inferred here.  Arbitrary boundaries, all-shape exhaustion, and the
thermodynamic limit remain open.

The bridge does not prove the all-time projected `D` or `delta-D` Cauchy
estimates, product/core density, exhaustion independence, group law,
Hamiltonian-to-OS identification, KMS/GNS gap, continuum, C6, Sector A or
Pre-A closure.

## Adversarial review

1. **Source convention.** The theorem is restricted to the zero-source onsite
   operator already used by the canonical Q3 form. **UPHELD.**
2. **Spectral shift sign.** The constant `A_0` is defined with a max and is not
   assumed positive from an unverified ground-energy sign. **UPHELD.**
3. **Operator versus scalar inequality.** The domination is a quadratic-form
   statement followed by functional calculus for the positive onsite operator;
   it is not an assertion about commuting full Hamiltonian factors. **UPHELD.**
4. **Volume dependence.** Only two endpoint moments occur; no sum over all
   sites is introduced. **UPHELD.**
5. **Moment exponent.** The step `k^3<=k^5` uses the registered `k>=1`; no
   unproved interpolation exponent is hidden. **UPHELD.**
6. **Existing-authority reuse.** The R-167 fifth-moment theorem is cited as an
   input and is not counted as a new proof or a new QFT result. **UPHELD.**
7. **Lean.** R242 checks exact arithmetic fixtures and scope markers only; it
   does not formalize Gibbs traces or unbounded operator domains. **UPHELD.**
8. **QFT promotion.** Direct dynamics, OS/KMS, GNS, continuum, C6, Sector A
   and Pre-A remain open. **UPHELD.**

## Next gate

Insert `M_bridge` into a two-sided Duhamel remainder estimate for the direct
projected `D` and `delta-D` route.  Keep the source-uniform `A_0` extension as a
named hypothesis unless its owner is separately discharged.
