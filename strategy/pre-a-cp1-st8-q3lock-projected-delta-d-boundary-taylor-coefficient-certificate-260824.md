# EXP-001058 / projected D,delta-D boundary Taylor coefficient

## Finding

Take a local configuration character

\[
W_a(x)=\exp(i a q_x/\hbar)
\]

and add one neighboring canonical Q3 bond

\[
B(q,v)=\frac c2(q-v)^2+\frac\lambda4(q-v)^2(q^2+v^2).
\]

On the finite polynomial CCR core, `delta=i[H,.]/hbar`.  Because `B` and
`W_a` are both configuration multipliers,

\[
\delta_{H_0+B}(W_a)-\delta_{H_0}(W_a)=0.
\]

The first nonzero boundary coefficient is therefore the second generator
difference:

\[
\delta_{H_0+B}^2(W_a)-\delta_{H_0}^2(W_a)
 =-\frac{i a}{\hbar\chi}\,W_a\,\partial_qB,
\]

where

\[
\partial_qB=c(q-v)+\frac\lambda2(q-v)(2q^2-qv+v^2).
\]

This is an actual cubic force of the canonical Q3 bond.  On the registered
`6 x 6` real field grid, the exact fourth-power bound with
`C=122099/35840` is satisfied, so the force fits the same
`(1+q^4+v^4)^(3/4)` carrier used by EXP-001055.

## Verification

- Primary exact SymPy lane: 49/49.
- Independent Fraction lane: 46/46.
- Integrated verifier: 21/21; Lean R240 compiles.
- Lean checks the force value, cubic-degree fixture, second coefficient,
  `hbar*chi` normalization, and first-difference zero.

## Adversarial review

1. **CCR convention:** signs and `hbar` factors are explicit. UPHELD.
2. **Order:** the first difference is zero; the force first appears at order
   two. UPHELD.
3. **Q3 force:** differentiated from the registered bond, not imported.
   UPHELD.
4. **Weight:** the bound is finite-grid evidence only, not an operator theorem.
   UPHELD.
5. **Taylor:** one coefficient does not sum the real-time series or histories.
   UPHELD.
6. **Lean:** R240 is an arithmetic cross-check, not a domain proof. UPHELD.
7. **QFT:** projected D,delta-D, OS/KMS, GNS, continuum, C6, Sector A and
   Pre-A remain open. UPHELD.
8. **TECT owner:** no `heat_root_incidence` or A1/R-192 production owner is
   supplied. UPHELD.

## Boundary and next gate

This is a claim-nonbearing finite CCR-core bridge.  The next step is to turn
the force coefficient into a two-sided Duhamel estimate using the canonical
shifted form from EXP-001057, then test volume/source uniformity on the fixed-
beta OS mixture word class.
