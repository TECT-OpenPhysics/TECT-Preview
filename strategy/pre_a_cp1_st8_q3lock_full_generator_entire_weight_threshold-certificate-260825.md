# Full-generator entire-weight threshold certificate

## Scope

This T0, claim-nonbearing checkpoint connects the full formal Taylor
filtration of EXP-001114 to the only remaining plausible source topology: an
entire analytic/Frechet weight. It is an exact coefficientwise threshold, not an
operator or thermodynamic result.

## Exact threshold

R286 shows that the full formal Heisenberg coefficient has a unique top source
term

`-m c (-G/4)^(m-1) a^(4m-3)`.

For positive `G` and `c`, its absolute top sequence is

`A_m(a) = m c (G/4)^(m-1) |a|^(4m-3)`.

The exponential generating identity is therefore

`sum_(m>=1) t^m A_m(a)/m! = c t |a| exp((tG/4)|a|^4)`.

Against `w_sigma(a)=(1+|a|) exp(sigma |a|^4)`, the exact coefficientwise ratio
is

`[c t |a|/(1+|a|)] exp(((tG/4)-sigma)|a|^4)`.

Consequently `sigma >= tG/4` is sufficient for the displayed envelope, with
ratio at most `ct`; when `sigma < tG/4`, the ratio has positive quartic
exponent and is unbounded as the source amplitude grows. This is a necessary
condition for any topology that claims to absorb this full coefficient
sequence.

For the registered fixture, `G=51/35`, `c=2/3`, `t=1/3`, so the rate is
`17/140`. The good choice `sigma=1/5` leaves margin `11/140` and prefactor
`2/9`; the bad choice `sigma=1/10` has deficit `3/140`. Primary and independent
lanes evaluate finite partial envelopes at the declared amplitudes and verify
the exact margins. Lean R287 checks the rational fixtures.

## Adversarial review

1. **Full versus selected word — UPHELD WITH COEFFICIENT BOUNDARY.** The input
   sequence is the noncancellable top term of the full formal expansion from
   R286, not a claim about only one chosen word.
2. **Threshold direction — UPHELD.** The rate is recomputed from `tG/4`; good
   and bad margins are derived from the same upstream fixture.
3. **Infinite series — OPEN.** The exponential identity concerns the formal
   coefficient generating function. It is not an actual Q3 history summation.
4. **Topology — OPEN.** No representation-independent entire seminorm,
   common-core continuity, or closure theorem is supplied.
5. **QFT promotion — OPEN.** Word incidence, volume uniformity, dual modular
   tail, exhaustion, common alpha, OS/KMS/GNS, gap, continuum, C6, Sector A and
   Pre-A remain open.
6. **Lean — UPHELD.** R287 formalizes exact arithmetic only.

## Next gate

The next proof obligation is to define this threshold weight on an actual Q3
common CCR core and prove generator continuity plus a two-orientation,
volume-uniform history recurrence. Only then can direct/modular D Cauchy and
exhaustion be tested.

## Non-claims

This certificate does not prove actual Q3 dynamics, a thermodynamic QFT,
KMS/GNS, a gap or continuum limit, C6, Sector A, Pre-A, TECT production, or a
Clay result.
