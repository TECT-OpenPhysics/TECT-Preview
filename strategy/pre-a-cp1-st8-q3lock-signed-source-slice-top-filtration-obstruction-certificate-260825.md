# EXP-001119 / R-291 route certificate

## Finding

The registered center and reverse source polynomials have the same exact
q=v=0 slice:

    P(a) = -(51/140) a^4 - 2 a^2.

Consider the signed finite-polynomial generator L=P(a) D_a and the witness
f_0(a)=a. The quartic branch raises degree by three after differentiation and
the quadratic branch raises degree by one. Therefore the coefficient at degree
1+3m cannot receive a contribution from the quadratic branch. Exact iteration
gives

    [a^(1+3m)] L^m(a)
      = (-51/140)^m product_{j=0}^{m-1}(1+3j).

At S=1/4 and S'=1/8, the absolute factorial-seminorm contribution at m=16 is

    (51/140)^16 product(1,4,7,...,46) 49! (1/8)^49 /(1/4)

    = 16852401249880525043166743609120334459341208478260995138186151899470933533
      /244347413243905574267593745054566029721600

    > 12^16 = 184884258895036416.

Primary and independent exact polynomial lanes agree on the slice, every top
coefficient row, and the order-sixteen witness. Lean R291 checks the rational
slice, degree fixture, signed top-product identity, and finite inequality.

## Decision

The strongest immediate sign-cancellation objection is rejected on this formal
source slice: the signed quartic top degree survives. This is a route boundary,
not a no-go theorem for the full multivariate Q3 commutator. Cancellations that
mix q, v, component indices, bond histories, or state weights remain open.

## QFT boundary

No unbounded Q3 common core, source/volume/history-uniform estimate, direct D or
delta-D Cauchy limit, exhaustion independence, common automorphism group,
KMS/OS identification, GNS gap, continuum, C6, Sector A or Pre-A is derived.
The physical BCC premise remains blocked by C6-BCC-PREMISE-BLOCKED.

## Devil's-advocate review

- Slice provenance — UPHELD: both orientations are recomputed from the
  registered source formulas.
- Degree filtration — UPHELD: the quadratic term cannot reach degree 1+3m.
- Signed versus norm — UPHELD: iteration is signed; absolute values appear
  only in the final norm lower witness.
- Orientation — UPHELD: both slices and all top rows agree.
- Finite radius — UPHELD: the order-sixteen rational row is exact and no limit
  is inferred.
- Lean scope — UPHELD: R291 does not encode operator domains or thermodynamics.
- QFT promotion — UPHELD: common alpha, KMS/OS, GNS gap, continuum, C6,
  Sector A and Pre-A remain open.

## Reproduction

    python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_signed_source_slice_top_filtration_obstruction.py --self-test
    python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_signed_source_slice_top_filtration_obstruction_independent.py --self-test
    python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_signed_source_slice_top_filtration_obstruction_verify.py
