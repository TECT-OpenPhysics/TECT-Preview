# EXP-001052 — Q3 ordinary multiplication-norm boundary

## Status

This is a T0, claim-nonbearing QFT route boundary.  It does not change a claim
tier, result ledger, negative-result registry, common-alpha status, or
production-kernel ownership.

Primary: 20/20 PASS  
Independent Fraction lane: 18/18 PASS  
Integrated lane: 22/22 PASS  
Lean: R234 PASS

Run artefacts:

- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-unbounded-multiplication-norm-boundary/primary.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-unbounded-multiplication-norm-boundary/independent.json`
- `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre-a-cp1-st8-q3lock-unbounded-multiplication-norm-boundary/integrated.json`

## Exact slice

Using the registered Q3 polynomial and the canonical fixture, restrict to
\(v=0\) and \(a=1/4\).  The resulting exact polynomial is

\[
P_0(q)=\frac{51}{140}q^3-\frac{153}{1120}q^2
       +\frac{2291}{2240}q-\frac{4531}{35840}
 =\frac{(8q-1)(1632q^2-408q+4531)}{35840}.
\]

Its leading coefficient is \(51/140>0\), and

\[
\lim_{q\to+\infty}P_0(q)/q^3=51/140.
\]

The exact values at \(q=4,8,16,32,64\) are respectively

\[
899341/35840,\quad 190287/1024,\quad 10561193/7168,
\quad 84794793/7168,\quad 486405643/5120.
\]

The two arithmetic lanes reproduce these values and their strict growth.  In
particular the \(q=32\) value already exceeds the formal source rate
\(B=1382807/7168\).

## QFT meaning and boundary

If the field coordinate is represented on the full real line and the source
acts by multiplication by \(P_0\), the positive cubic asymptotic means that
the ordinary global multiplication-operator norm is not finite.  This rules
out using the EXP-001051 coefficient norm as an ordinary global operator norm
without an energy/domain restriction.

The surviving QFT route is therefore an energy-weighted or state-weighted
seminorm.  The candidate \(A(q)=1+q^4\) has \(A^{3/4}\) cubic growth, so it is
the correct matching target for a future domain estimate.  No bound for
\(P_0A^{-3/4}\), no common-core invariance, and no unbounded Q3 realization is
proved here.

This is not a global Q3 no-go: a cutoff, a different representation, an
energy-weighted domain, or an analytic/state-weighted topology is outside the
ordinary-norm architecture tested here.

## Adversarial review

- The growth statement is conditional on the full real scalar multiplication
  representation; it is not silently identified with the canonical Q3 Hilbert
  space.
- Only ordinary multiplication boundedness is obstructed; weighted/domain
  estimates remain open.
- All coefficients come from the registered Q3 source and are reconstructed
  independently; the growth values are not fitted.
- The finite values are witnesses, while the exact leading coefficient and
  ratio limit carry the asymptotic route boundary.
- \(A(q)=1+q^4\) is a proposed matching weight, not a proved Hamiltonian or
  domain operator.
- R234 verifies exact rational fixtures only, not domain closure or dynamics.
- No factorial incidence, first passage, exhaustion, common alpha, KMS/OS,
  GNS gap, continuum, C6, Sector A, Pre-A, or TECT production result follows.
- No `heat_root_incidence` or A1/R-192 production owner is supplied.

## Next gate

Prove or obstruct the energy-weighted Q3 slice estimate for the candidate
\(A(q)=1+q^4\) on a declared common core, then reconnect both source
orientations to the independent factorial spatial-incidence audit.
