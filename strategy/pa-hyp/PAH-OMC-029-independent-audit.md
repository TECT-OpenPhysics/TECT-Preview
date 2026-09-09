# PAH-OMC-029 independent formulation and hostile review

Internal analytic reconstruction, 2026-09-09. This is a different derivation
and non-importing executable audit, not a signed external referee report or
an independent human review. The full theorem remains conditional on the
exact R-510/R-511/R-512/R-567 inputs named in the preregistration.

## A. Boundary estimate without a graphical construction

Fix M,N and the amplitude vector in E_M. Combine channels algebraically
ONLY for this proof: the finite-root generator can be written

    L_N=sum_j b_j(x)(tau_j-I),    0<=b_j<=2q_N.

Here tau_j flips one of the two-valued phase, aperture or link bits, and
b_j is the SUM of the existing admissible channels for that bit. No channel
is removed from A: PH/LK still have two contributions. AP's inadmissible
potential channel contributes zero. Frozen outside bits have b_j=0.
The tau_i commute because they change different binary coordinates.

For u(t)=P_N(t)f define w_i(t)=tau_i u(t)-u(t). The exact commutator identity
is

    w_i'=L_N w_i + sum_j (tau_i b_j-b_j) tau_i(tau_j-I)u.

Use the finite matrix variation-of-constants formula and its sup-norm
contraction. With delta_i(u)=||tau_i u-u||_infinity this gives

    delta_i(u(t))<=delta_i(f)+integral_0^t sum_j C_ij delta_j(u(s)) ds,
    C_ij=sup |tau_i b_j-b_j|.

The matrix C is finite and nonnegative. Each entry is <=2q_N, not 4q_N:
both values lie in [0,2q_N]. It vanishes unless i belongs to the rate
dependency neighborhood of j. Every root has radius <=R_c, so the same
radius applies in the reversed dependency matrix. Each row has at most
b(2R_c+1) possible j. Hence its row sum is <=B_c q_N, where
B_c=2b(2R_c+1), exactly the primary count.

Iterate the integral inequality k times. The remainder is bounded by a
finite maximum of delta(u(s)) times (||C||t)^k/k!, which tends to zero at
this FIXED finite N. Therefore componentwise delta(u(t))<=exp(tC)delta(f).
For a bit centered beyond N and f in columns <=m, the matrix entries
(C^k)_ij vanish for k<d_N=ceil((N+1-m)/R_c). Thus

    delta_i(P_N(t)f)<=2||f||_infinity
           sum_(k>=d_N) (B_c q_N t)^k/k!.

This is at least as strong as the certificate's bound, which additionally
overcounts the initial support by k_f>=1. It uses neither independent
graphical paths nor a presumed infinite process. Multiplication by the
number p R_c of exterior active roots and their rate bound gives the same
boundary remainder (7). The subsequent arbitrary-N factorial domination
is analytic and is NOT replaced by this fixed-N integral iteration.

## B. Audit of the three non-combinatorial bridges

1. **Uniform marginal tail: accepted under the R-510 transfer input.**
   Start from rho_i=l_i phi/(lambda^i <u,phi>), not the stationary phi*psi
   density. The anchored law generally is not translation invariant.
   The left power estimate l_i<=8B lambda^(i-1)U^2u and the right estimate
   phi<=8Uu/lambda give the factor lambda^-2 for i>=1. The i=0 case is
   separate. The spatial spectral constants are finite by their inherited
   proof, not by a numerical spectral-gap estimate. This yields a uniform
   COLUMN tail but no uniformity in other source parameters.
2. **All-extension radial localization: accepted.** The closed kernel of
   every generator contains the H closure of the radial cylinders. A
   positive conservative operator fixing chi and 1-chi preserves their
   disjoint order intervals. Linearity then proves the module identity.
   This requires only the scalar lattice structure of the original
   invariant H; no disintegration or path regularity is assumed.
3. **All-extension domain bridge: accepted.** The finite matrix exponential
   is compact-amplitude locally Lipschitz. A finite-prefix radial cutoff
   puts it in the ORIGINAL D. The cutoff equals one on E_M and its nonradial
   generator increment is zero. Multiplication by 1_(E_M), already shown
   to commute with every semigroup and its generator, supplies exactly (5).
   Graph-norm continuity along the time-dependent test is obtained from
   finite root bounds on that same box before differentiating S(t-s)v_s.

## C. Hostile attempt and disposition

- If arbitrary semigroups were not required to extend A on ALL D, radical
  behavior could escape the argument: UPHELD as a scope boundary. The
  extension class explicitly requires D subset Dom(G), G|D=A.
- A form-core conclusion would not control a larger Markov domain:
  UPHELD against that alternative. No form-domain equality is used.
- Frozen labels exterior to N may enter interior rates and P_Nf: UPHELD
  against treating them as absent. They are retained as parameters and
  their generator action produces the explicit boundary remainder.
- A bounded-energy estimate alone does not bound maximal rates: UPHELD.
  This proof instead uses a separately derived column tail, frozen radial
  multipliers, and the exact quadratic increment.
- A radial-dependent time rescaling could manufacture slow propagation:
  UPHELD against such a change. q_N bounds proposal rates; accepted rates
  stay c_r and the matrix generator remains the original finite-root sum.
- State-conditioned finite matrices could hide a new measure: UPHELD.
  All finite matrices are pointwise tests; H norms and final comparisons
  use the original mu. No normalized restriction to E_M appears.
- A nonzero fixed tail probability would leave an uncontrolled remainder:
  UPHELD. The final error is 2||f|| sqrt(mu(E_M^c)), which tends to zero
  by (2) after N->infinity. The square root may not be dropped.
- A rate bound q_N of order N need not be beaten by the factorial:
  UPHELD. The proof derives subpolynomial growth and explicitly uses
  exponent delta=1/2<1. A negative test checks the vanishing log coefficient
  at delta=1 and its wrong sign above one; this is not a model counterexample.
- Essential self-adjointness or finite-to-target convergence follows:
  UPHELD against either promotion. Neither follows from the proved class
  equality alone.

## D. Verification coverage and remaining external review

The independent program reconstructs the local range bound by endpoint
ranges rather than the primary formula, enumerates potential channels by
bits, and checks factorial coefficients through binomial integers. The
primary program separately builds the source incidence stencil and checks
its dependency radius. Lean checks closed-graph zero-kernel passage,
common-comparison uniqueness, scalar localization-error removal, exact
source-scope arithmetic, the negative log coefficient, and the cubic
optimization identity. Measure extension, the R-510 spectral input, the
finite matrix commutator comparison, and the complete analytic passage
(1)--(9) are not fully formalized in Lean.

No exact pair of distinct admissible extensions was found. Within the
named inherited hypotheses the two boundary formulations support the same
uniqueness proof. This review supplies no new physical, finite-convergence,
or source-owner conclusion. External review is specifically invited on
Sections A and B, with all original source hashes and formulas retained.
