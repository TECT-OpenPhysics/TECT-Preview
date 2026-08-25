# EXP-001127 — local quartic-tail force obstruction to the A^(3/4) factorization

## Result first

The proposed local operator-norm bridge

`|| W_L F K^(-3/4) || < infinity`

does not hold for the quartic Q3 bond when `lambda>0`.  This is an exact
route-local obstruction, not a numerical extrapolation.

For the declared cosine cutoff, choose the exact tail sector `v=0` and
`q>=2L`.  Then `q_L=v_L=0`, so

\[
B(q,0)=\frac c2q^2+\frac\lambda4q^4,\qquad
F(q,0)=cq+\lambda q^3,
\]

and therefore

\[
W_LF=\frac{c^2}{2}q^3+\frac{3c\lambda}{4}q^5
      +\frac{\lambda^2}{4}q^7.                 \tag{1}
\]

On translated fixed-width Schwartz packets, the local quartic energy has
graph size `K^(3/4)=O(q^3)`, while (1) is bounded below by
`lambda^2 q^7/4` for positive `c,lambda`.  A bounded factorization through
`K^(-3/4)` would imply `||W_LF psi|| <= C||K^(3/4)psi||`; the translated
packets make the ratio grow at least as a positive constant times `q^4`.
Thus the quartic tail-force product cannot be handled by the same
`A^(3/4)` operator norm used for the first/double commutator boundary.

The boundary is important: if `lambda=0`, the degree drops to three and the
scalar exponent is critical rather than obstructed.  The present package does
not remove that separate quadratic-bond subcase.

## QFT meaning and surviving routes

The no-go retires one tempting local graph-norm factorization.  It does not
retire the actual QFT programme.  The remaining admissible routes are a
state-weighted or modular estimate with cancellation, a product-level
Volterra/linked-cluster estimate that never isolates `W_LF` in operator norm,
or a higher graph power with a new volume-uniform proof.  Direct projected
`D,delta-D` locality also remains independent.

## Adversarial review

- **Cutoff:** the taper is exactly zero on `q>=2L`; no asymptotic cutoff claim
  is used.
- **Force sign and coefficient:** (1) is differentiated from the registered
  bond and checked independently; the leading coefficient is `lambda^2/4`.
- **Kinetic term:** the scalar statement is promoted only through translated
  fixed-width Schwartz packets and the implication of a bounded graph
  factorization.  It does not replace the Schrödinger operator by a pointwise
  multiplication operator.
- **Boundary case:** `lambda=0` remains explicitly open.
- **QFT boundary:** no common alpha, OS/KMS/GNS, gap, continuum, C6, Sector A
  or Pre-A conclusion follows.
- **Lean:** R298 checks the exact polynomial and rational power-count
  identities only.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_tail_force_a34_operator_obstruction.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-local-tail-force-a34-operator-obstruction/primary.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_tail_force_a34_operator_obstruction_independent.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-independent-pre-a-cp1-st8-q3lock-local-tail-force-a34-operator-obstruction/independent.json
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_local_tail_force_a34_operator_obstruction_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-integrated-pre-a-cp1-st8-q3lock-local-tail-force-a34-operator-obstruction/integrated.json
```

These are finite exact-arithmetic route checks; they do not constitute a
thermodynamic QFT proof.
