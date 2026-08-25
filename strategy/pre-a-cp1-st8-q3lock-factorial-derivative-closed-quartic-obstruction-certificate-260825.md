# EXP-001118 / R-290 route certificate

## Finding

The candidate coefficient seminorm is

[
  |f|_{S,!}=sum_{ngeq0}|c_n|,n!S^n,
  qquad f(a)=sum_{ngeq0}c_na^n.
]

For finite polynomials, differentiation is exactly closed at one radius:
[
 |D_af|_{S,!}=S^{-1}|f|_{S,!}.
]

This repairs the derivative-only defect isolated in EXP-001117. It does not
repair quartic source insertion. Rebuilding the registered center and reverse
source polynomials gives the same pure source coefficient
[
 [a^4]P_+=[a^4]P_-=-fractionrac{51}{140}.
]

The positive absolute-value top branch is therefore
[
 T=fractionrac{51}{140}a^4D_a.
]
On the witness f_0(a)=a,
[
 T^m f_0
 =left(fractionrac{51}{140}ight)^m
   prod_{j=0}^{m-1}(1+3j),a^{1+3m}.
]

At input radius S=1/4 and output radius S'=1/8, the exact factorial-norm
ratio at order sixteen is
[
 fractionrac{(51/140)^{16}
       (1cdot4cdot7cdot10cdot13cdot16cdot19cdot22cdot25
        cdot28cdot31cdot34cdot37cdot40cdot43cdot46)
       49!,(1/8)^{49}}{1/4}
 =
 fractionrac{16852401249880525043166743609120334459341208478260995138186151899470933533}
      {244347413243905574267593745054566029721600}
 > 12^{16}=184884258895036416.
]

The factor 12 is retained only as the six-neighbour/two-orientation finite
history comparison. More generally, the last 2m factors in (1+3m)! are at
least m, so (1+3m)! >= m^(2m). The exact recurrence therefore has a
superexponential lower envelope relative to every fixed exponential base when
both radii remain positive. The primary and independent lanes reproduce the
source coefficient, derivative constant, recurrence rows and order-sixteen
witness; Lean R290 checks the rational derivative identity, the order-sixteen
inequality and the factorial fixture.

## Decision

This parks the positive top-monomial envelope in the factorial coefficient
topology. It is a route-level result only. The signed complete Q3 commutator
may contain cancellations not represented by the absolute-value branch, and a
state-weighted or different common-core construction remains logically open.

## QFT boundary

Nothing here constructs an unbounded Q3 common core, a source/volume/history
uniform estimate, direct D or delta-D Cauchy convergence, exhaustion
independence, a common automorphism group, KMS/OS identification, a GNS gap,
the continuum, C6, Sector A or Pre-A. The physical BCC premise remains
blocked by C6-BCC-PREMISE-BLOCKED.

## Devil's-advocate review

- Derivative closure — UPHELD. The index factor cancels exactly against the
  factorial weight; no radius shrink is hidden in the derivative identity.
- Source provenance — UPHELD. The -51/140 coefficient is recomputed from the
  registered center and reverse source formulas.
- Majorant versus signed history — UPHELD-OPEN. The top branch is an
  absolute-value envelope, not an asserted equality for the full Q3 history.
- Radius loss — UPHELD. The finite S=1/4 to S'=1/8 witness is exact; the
  factorial lower bound supplies the asymptotic route boundary.
- Orientation/branching — UPHELD-OPEN. Both orientations have the same top
  coefficient, while the 12 comparison is not a thermodynamic count.
- Lean scope — UPHELD. R290 encodes only rational finite fixtures and no
  operator-domain or limit theorem.
- QFT promotion — UPHELD. Common alpha, KMS/OS, GNS gap, continuum, C6,
  Sector A and Pre-A remain open.

## Reproduction

    python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_factorial_derivative_closed_quartic_obstruction.py --self-test
    python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_factorial_derivative_closed_quartic_obstruction_independent.py --self-test
    python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_factorial_derivative_closed_quartic_obstruction_verify.py

The integrated command also compiles verification/lean/Tect/R290.lean when the
pinned Lake toolchain is available.