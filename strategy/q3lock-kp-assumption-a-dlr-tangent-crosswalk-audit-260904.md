# Q3LOCK KP Assumption (A) and DLR tangent crosswalk audit

**Status:** T0 source-scope audit; no claim-card promotion  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782, with the cited
Kozitsky--Pasurek finite-volume and Euclidean-DLR results  
**PDF:** deferred until mathematical content, source audit and independent
review are complete

## 1. Purpose and boundary

The Q3LOCK proof uses the general quantum-crystal results of
Kozitsky--Pasurek (KP) for the finite-volume loop representation and the
nonempty, compact tempered Euclidean DLR set.  This note checks the exact
hypothesis map instead of referring to a generic "standard Feynman--Kac
argument".  It also separates what is imported from KP from the
Q3LOCK-specific time-grid, FKG, reflection-positivity, source-tangent and
phase arguments.

The symbol `r_KP>1` below denotes the superquadratic exponent in KP's
Assumption (A).  It must not be confused with the Q3LOCK quadratic coefficient
`r<0`.  The audit is at fixed spacing, fixed positive `hbar`, `chi`, `c`, `g`
and `lambda`, fixed finite spatial volume when a loop law is constructed, and
compact source interval.  It proves no continuum limit, real-time dynamics,
KMS identification for one common thermodynamic dynamics, ground-state phase,
gap, physical-vacuum statement, C6, CP1, Sector A or Pre-A conclusion.

## 2. KP source statement to be used

The primary source is Y. Kozitsky and T. Pasurek, *Euclidean Gibbs States of
Interacting Quantum Anharmonic Oscillators*, arXiv:math-ph/0609045.  The
manuscript must cite the version actually audited and reproduce the relevant
finite-volume assumptions and equation/theorem numbers from that version.

In KP notation a finite-volume Hamiltonian has the form

```text
H_Lambda = sum_l [H_har_l + V_l(q_l)]
           - (1/2) sum_(l,l') J_(l,l') (q_l,q_l'),
```

with a positive harmonic reference and a symmetric interaction matrix.  KP's
Assumption (A), stated here with its source symbol renamed where needed,
requires:

1. each `V_l` is continuous and normalized at the origin;
2. for some `r_KP>1`, `A_V>0`, `B_V` and a continuous upper function `V`,

   ```text
   A_V |x|^(2*r_KP) + B_V <= V_l(x) <= V(x);
   ```

3. the interaction sum is finite,

   ```text
   Jhat_0 = sup_l sum_(l') |J_(l,l')| < infinity.
   ```

Under these hypotheses KP supplies the finite-volume self-adjoint,
lower-bounded Hamiltonian with discrete spectrum, positivity-preserving heat
semigroup and finite heat trace for every positive Euclidean time.  The same
source constructs the periodic Ornstein--Uhlenbeck loop reference and its
Feynman--Kac Gibbs modification, and proves nonemptiness/compactness and
moment control for the corresponding tempered Euclidean DLR specification in
the stated vector quantum-crystal setting.

Only these finite-volume and Euclidean-DLR consequences are imported.  No
KP scalar attractive-phase theorem, rotation-invariant vector corollary, or
real-time KMS theorem is being used for the positive-`lambda` Q3LOCK claim.

## 3. Exact Q3LOCK-to-KP parameter map

Fix an eight-component field `q_y in R^8` on a three-dimensional spatial
lattice.  The kinetic part of the Q3LOCK oscillator is normalized so that the
periodic OU covariance operator has

```text
m = chi / hbar^2 > 0,
A = -m*d^2/dtau^2 + a,
a > 0.
```

The parameter `a` is an auxiliary harmonic split, not a physical coupling.
The Q3 internal graph has eight vertices and is 3-regular; write its edge set
as `E(Q3)`.  The nonnegative locking polynomial is recorded in the form

```text
W_Q3(q) = (lambda/4) sum_(e={i,j} in E(Q3))
             (q_i-q_j)^2 (q_i^2+q_j^2),
```

and the component quartic is a positive multiple of `sum_i q_i^4`.  A source
in the collective direction is `-h u dot q`, with
`u=(1,...,1)/sqrt(8)`; for the source audit `|h|<=h0` is fixed.

For a periodic cubic spatial box, set the symmetric KP coupling
`J_yz=J_zy=c` on each nearest-neighbour pair and zero otherwise.  Expanding
the spatial difference form gives the exact identity

```text
c/2 sum_{<yz>} |q_y-q_z|^2
 = 3c sum_y |q_y|^2
   - c sum_{<yz>} (q_y,q_z).
```

Here `<yz>` is the explicit positive-direction periodic edge multiset; it has
`3|Lambda|` terms and six endpoint incidences per site, with `L=2` multiplicity
retained.  Open boxes use `(c/2)d_R(y)` instead of a translation-invariant `3c`
diagonal.  See EXP-001512 for the full correction audit.

The second term is exactly
`-(1/2) sum_(y,z) J_yz (q_y,q_z)` when the ordered KP sum contains both
orientations.  The positive `3c` contribution belongs to the onsite
potential and must not be counted again in the pair interaction.  The
nearest-neighbour interaction has

```text
Jhat_0 = 6c.
```

After the split, the residual one-site potential is the sum of the original
Q3LOCK quadratic and quartic terms, the nonnegative `W_Q3`, the source term,
the onsite `3c |q|^2` contribution, and the subtraction
`-a|q|^2/2` associated with the harmonic reference.  Recombining the split
recovers the exact Q3LOCK Hamiltonian; the normalized loop law is independent
of the auxiliary choice of `a`.

## 4. Verification of Assumption (A)

### 4.1 Lower bound

The Q3 locking term is nonnegative.  The component quartic satisfies the
finite-dimensional norm comparison

```text
sum_i q_i^4 >= |q|^4/8.
```

On a compact source interval, the negative quadratic coefficient and the
linear source are absorbed by quartic Young inequalities.  For every fixed
`a>0` this gives constants `A>0` and `C<infinity`, uniform in `|h|<=h0`,

```text
V_(h,a)(q) >= A |q|^4 - C.
```

This is KP's lower bound with `r_KP=2`; the distinction between the Q3LOCK
coefficient `r<0` and the KP exponent is essential.  The constants are
allowed to depend on the declared compact source interval and the fixed
microscopic parameters, but not on the time-grid size in the later
fixed-volume uniform-integrability argument.

### 4.2 Upper bound

Every Q3 edge obeys a continuous quartic bound of the form

```text
(q_i-q_j)^2(q_i^2+q_j^2) <= 4(q_i^4+q_j^4).
```

Together with the finite 3-regular internal graph, the component quartic,
quadratic and source terms are bounded above by one continuous quartic
function.  Thus the same compact source interval supplies the upper function
required by KP.  The estimate is local in the eight-dimensional onsite
variable and does not assert radial or `O(8)` symmetry.

### 4.3 Interaction and finite-volume consequences

The finite-range coupling gives `Jhat_0=6c<infinity`; the mass condition is
`m>0`; all onsite terms are continuous.  Therefore the KP finite-volume
operator and periodic loop representation apply after the displayed sign and
factor map.  At fixed source, the general vector theorem supplies the
tempered Euclidean DLR nonemptiness, compactness and the cited exponential
moment bounds used by EXP-000781.  The theorem does not by itself select a
zero-source tangent branch or establish a cusp.

## 5. What the KP representation supplies

Let `chi_Lambda^a` denote the product periodic OU law for `A` and let
`I_(Lambda,h)` contain the residual local and spatial Euclidean integrals.
The finite-volume loop state has the source convention

```text
mu_(Lambda,h)(domega)
 = exp[-I_(Lambda,h)(omega)] chi_Lambda^a(domega)
   / Z_(Lambda,h).
```

The Hamiltonian source `-h sum_y u dot q_y` therefore appears as the positive
factor `exp(+h X_L)` in the Euclidean exponential moment, where

```text
X_L = sum_y integral_0^beta u dot omega_y(tau) d tau.
```

KP identifies the finite-volume bounded multiplication correlators with loop
functionals of this measure.  This justifies the starting probability law for
the Q3LOCK proof at fixed spatial volume and source.  It does not justify
passing an unbounded source exponential through a weak limit; that passage is
the separate quartic uniform-integrability argument in the P-09 audit.

## 6. Obligations that remain Q3LOCK-local

| Item | KP status | Q3LOCK obligation |
|---|---|---|
| Finite-volume self-adjointness, lower bound, discrete spectrum and heat trace | supplied after Assumption (A) match | state the exact cited result and form-domain map |
| Periodic OU reference and finite-volume Feynman--Kac law | supplied | retain `m=chi/hbar^2`, `a>0`, source sign and edge factors |
| Fixed-source Euclidean DLR nonemptiness/compactness and moments | supplied in the general vector scope | verify the Q3 local potential and interaction hypotheses; keep source fixed at this stage |
| Time-grid Gaussian covariance, interpolation tightness and grid-to-loop weak limit | not supplied for the Q3 discretization | prove the covariance-tail, compactness, Riemann-sum and normalizer steps |
| Continuous-loop FKG for the nonradial Q3 onsite law | not supplied | finite-grid MTP2, order-preserving interpolation, weak-limit association and clipped UI (P-06) |
| Hilbert-valued spatial reflection positivity and FSS bound | not supplied | finite `8N` spin transfer, zero-sum source, shifted limit and Duhamel normalization (P-09) |
| Source removal and tangent-state selection | not automatic from fixed-source DLR existence | combine EXP-000780 pressure convexity with EXP-000781 source-uniform moments and specification continuity |
| Strict cusp and two-state conclusion | not supplied | complete P-06, P-09, Falk--Bruch, infrared and Griffiths composition in the explicit sufficient regime (P-12) |

The order of limits is fixed: first take the time-grid limit at fixed finite
spatial volume and source; only then take the spatial thermodynamic limit and
source tangent.  No spatial continuum limit is hidden in this order.

## 7. Independent audit checklist

Before registering the bounded Q3LOCK result, an independent reviewer must
sign each item below.

1. **Bibliography pin.**  Record the exact KP version, section and theorem
   numbers used for the finite-volume and DLR statements; verify that the
   quoted hypotheses are unchanged in that version.
2. **Form-domain map.**  Match the Q3LOCK quadratic, quartic and source terms
   to the KP closed-form domain and confirm that the auxiliary harmonic split
   is recombined before the final Hamiltonian is stated.
3. **Edge convention.**  Recompute the ordered/unordered pair sum and the
   onsite `3c` term for every finite-volume geometry used by EXP-000780;
   do not use the periodic degree-six identity for an open boundary without a
   separate boundary statement.
4. **Source units.**  Check that the Hamiltonian source sign produces
   `+h X_L`, that `X_L` is time-integrated, and that the factor-eight
   fine/coarse normalization is applied only where EXP-000781/782 require it.
5. **Grid topology.**  Verify that the piecewise-linear interpolation and
   compact cutoff are continuous in the exact periodic sup-norm topology used
   for the weak-limit argument.
6. **Uniform integrability.**  Recompute the quartic Young constants and the
   fixed-volume normalizer lower bound for source exponentials, second
   derivatives and clipped coordinate products.
7. **Theorem firewall.**  Confirm that no imported KP result assumes scalar
   order, radial symmetry, a one-dimensional oscillator chain, an already
   constructed real-time dynamics, extremality, purity or clustering.

Failure of any item keeps P-06/P-09 at `PROOF TEXT AND EXTERNAL AUDIT
REQUIRED`; it is not evidence against the Q3LOCK phase theorem, but it blocks
claim registration and publication.

## 8. Decision and publication boundary

The Q3LOCK model is inside the finite-volume and fixed-source Euclidean-DLR
scope of KP once the displayed parameter, potential and interaction checks
are included in the manuscript.  KP therefore supplies the correct starting
loop law and fixed-source compactness input for EXP-000781.  It does not close
the two load-bearing Q3LOCK limit passages: continuous-loop FKG (P-06) and
Hilbert-valued FSS/Duhamel differentiation (P-09).  The strict cusp and the
two parity-related zero-source DLR states remain conditional on those audits
and on the subsequent Griffiths composition.

This note is research documentation only.  It creates no claim card, no P2
manuscript and no release artifact.  In accordance with the project protocol,
PDF generation, compilation, rendering and visual review are deliberately
deferred until the mathematical text is independently audited, the claim and
manuscript are content-frozen, and the final reproducibility/release checks
pass.

## 9. Primary source

Y. Kozitsky and T. Pasurek, *Euclidean Gibbs States of Interacting Quantum
Anharmonic Oscillators*, arXiv:math-ph/0609045.  Relevant scope: finite-volume
Hamiltonian and Assumption (A), periodic Ornstein--Uhlenbeck loop
representation, Feynman--Kac Gibbs modification, and the general tempered
Euclidean-DLR existence/compactness framework.

