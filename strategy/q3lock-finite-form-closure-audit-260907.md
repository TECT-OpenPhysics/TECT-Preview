# Q3LOCK finite-volume form closure and harmonic truncation audit

**Date:** 2026-09-07 UTC  
**Exploration:** EXP-001639  
**Task:** T-054  
**Status:** T0, claim_bearing=false, internal proof-interface audit  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 / R-497  
**Paper PDF:** deferred until content review and final organization

## 1. Purpose and boundary

The manuscript's first load-bearing interfaces are the finite-volume closed
form, the heat-trace comparison, and the unbounded residual used in the
harmonic Feynman--Kac split.  This note writes those interfaces as one finite-
dimensional lemma chain and checks the constants independently of the earlier
mesh determinant diagnostics.  It does not certify the Simon source
application, the mesh limit, any spatial limit, or any phase statement.

The finite-volume result is for an even periodic cube
`Lambda_L=(Z/LZ)^3`, `V=L^3`, with the Q3 internal graph on `d=8`
components.  Parallel positive-direction bonds at `L=2` are retained.  Put
`m>0`, `g>0`, `lambda>=0`, `c>=0`, `r in R`, and
`u=8^(-1/2)(1,...,1)`.  The source window is `|h|<=h0`.

## 2. Lower envelope and physical form

Write

    w(q) = sum_y |q_y|^4,
    U_h(q) = sum_y B_h(q_y) + (c/2) sum_{<y,z>} |q_y-q_z|^2,

where `B_h` is the printed onsite Q3LOCK polynomial.  The Q3 locking and
spatial difference terms are nonnegative.  Since

    sum_e q_{y,e}^4 >= |q_y|^4/8,

the onsite quartic is at least `g|q_y|^4/32`.  For an auxiliary `a>0`, set
`R_{a,h}=U_h-(a/2)sum_y|q_y|^2` and `b=|r-a|/2`.  The scalar maximisations

    b t^2 - (g/64)t^4 <= 16 b^2/g,
    h0 t - (g/128)t^4
       <= (3/4) h0^(4/3) (32/g)^(1/3)

give, for every finite volume and source in the window,

    R_{a,h}(q) >= (g/128) w(q) - V C_res,

where

    C_res = 16 b^2/g + (3/4) h0^(4/3)(32/g)^(1/3).

The same calculation with `b=|r|/2` gives a physical-potential lower bound.
No signed spatial pair term is discarded: the positive-difference expression
for `R_{a,h}` is used for this bound, while the physical form always contains
the full `U_h`.

For the upper side, the elementary inequalities

    (x-y)^2(x^2+y^2) <= 4(x^4+y^4),
    t^2 <= 1+t^4/4,       t <= 1+t^4/4

give the finite, explicit envelope

    |U_h(q)| <= C_abs + K_abs w(q),

with

    C_abs = V(|r|/2+h0+6c),
    K_abs = g/4 + 3 lambda + |r|/8 + h0/4 + 3c/2.

The coefficients `3 lambda` and `3c/2` use respectively the Q3 vertex degree
and the six spatial endpoint incidences.  They are not fitted numerical
constants.  The analogous bound for `R_{a,h}` adds `a/2` to the quadratic
envelope and `aV/2` to the constant envelope.

## 3. Closed form and compact embedding

On `L^2(R^(8V),dq)` define

    Q_L = H^1(R^(8V)) intersect L^2(w(q)dq),

and

    q_h[psi] = (1/(2m))||grad psi||_2^2 + integral U_h|psi|^2.

The lower and upper envelopes imply that, after adding a fixed multiple of
`||psi||_2^2`, the form norm is equivalent to

    ||grad psi||_2^2 + ||psi||_2^2 + ||w^(1/2)psi||_2^2.

The intersection of the two closed domains is therefore complete, and the
form is closed and semibounded.  Compactness of the embedding `Q_L -> L^2`
is direct: on a ball, Rellich compactness applies to the `H^1` part; outside
the ball,

    integral_{|q|>R}|psi|^2 <= R^(-4) integral w(q)|psi|^2,

uniformly on a form-bounded set.  This proves compact resolvent at fixed
volume.  It is not an infinite-volume or continuum compactness assertion.

## 4. Heat trace and residual truncation interface

The residual lower bound gives the form inequality

    H_h = H_a + R_{a,h} >= H_a - V C_res.

The min--max principle and the explicit oscillator trace therefore yield

    Tr exp(-beta H_h)
      <= exp(beta V C_res)
         [2 sinh(beta sqrt(a/m)/2)]^(-8V).

For the unbounded residual define `R_M=min(R_{a,h},M)`.  Each `R_M` is
continuous and bounded, `R_M` increases pointwise to `R_{a,h}`, and all
residual forms share the harmonic form domain.  The lower envelope keeps the
forms uniformly semibounded.  The monotone limit form is the physical form
on `Q_L`; the polynomial upper envelope supplies the common form-domain
identification.  For every fixed Brownian bridge,

    exp(-integral R_M) downarrow exp(-integral R_{a,h})

and the lower bound supplies the integrable majorant
`exp(beta V C_res)`.  Thus dominated convergence gives the pathwise limit of
the bounded-potential bridge formula.  The remaining operator identification
is the monotone-form/semigroup step stated in the manuscript and must still
receive a signed external audit; this note makes its exact hypotheses and
limit order explicit rather than treating a finite numerical check as proof.

The trace comparison above is independent of operator monotonicity of the
exponential.  Once the kernel/semigroup identification is accepted, symmetry
and the semigroup property give the Hilbert--Schmidt diagonal integral and
the absolute trace.  The reference factor `Z_a` remains present.

## 5. Reproduction and hostile checks

Run:

    E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_finite_form_closure_audit.py

The script computes the Q3 edge degree and spatial endpoint degree, derives
the lower and upper coefficients from the declared inputs, checks the Young
maxima on independent rational/real fixtures, evaluates the full physical
potential on generated finite fields, and verifies the manuscript labels.
Hostile fixtures omit the Q3 locking coefficient or the spatial endpoint
budget and must be rejected by the envelope test.  A truncation sequence is
checked to be monotone and to converge pointwise on generated residual values.
The result is a finite algebra/provenance diagnostic; it cannot certify form
closure, the monotone-form theorem, or any unbounded-operator limit by itself.

## 6. Adversarial disposition

1. **Residual versus physical potential:** using the residual as the physical
   form drops the harmonic term.  UPHELD as a prohibition; the note keeps the
   two forms separate.
2. **Spatial degree:** replacing six endpoint incidences by three breaks the
   upper envelope on a constant field.  UPHELD and tested hostile.
3. **Q3 degree:** replacing the Q3 vertex degree three by one breaks the
   locking envelope on a single nonzero component.  UPHELD and tested hostile.
4. **Compact resolvent versus trace class:** compact embedding alone is not
   used as a trace proof; the oscillator min--max comparison supplies the
   heat-trace bound.
5. **Truncation direction:** `min(R,M)` increases to `R`; replacing it by a
   lower truncation would reverse the pathwise monotone convergence.  UPHELD
   and tested by the result artifact.
6. **Scope:** no spatially uniform form bound, DLR state, FKG, infrared,
   cusp, parity pair, KMS, ground state, continuum, or cosmological result
   follows.

## 7. Remaining acceptance gate

This audit advances the internal A1--A3 proof interface but leaves those rows
OPEN in `proof-audit.md`.  A mathematician must still check the closed-form
identification, the monotone-form/semigroup passage, endpoint kernel
continuity, and the exact Simon hypothesis map on the manuscript's common
core.  No claim tier or R-497 lineage changes, and no paper PDF is generated.
