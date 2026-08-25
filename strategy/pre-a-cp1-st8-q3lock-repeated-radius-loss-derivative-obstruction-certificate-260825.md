# EXP-001117 — Repeated radius-loss derivative budget obstruction

## Scope

This is a T0, claim-nonbearing boundary test for the formal Q3 coefficient
topology. It starts from the registered actual source polynomial and asks only
whether the radius-loss derivative estimate can be iterated with an exponential
history constant. It is not an operator-domain theorem and is not a QFT
construction.

## Exact source input

The upstream source polynomial is

\[
 P(q,v,a)=P_{\rm on}(q,a)+3P_{\rm edge,u}(q,v,a)+6P_{\rm bond,u}(q,v,a),
\]

with the registered radii
\((R_q,R_v,S)=(4,8,1/4)\). Reconstructing the polynomial gives source degree
four. Both the source-centered and source-at-neighbor orientations have the
same weighted coefficient rate
\[
 B=1382807/7168.
\]
These facts are rederived by the primary lane and independently checked by the
Fraction lane; they are formal coefficient data only.

## Repeated derivative witness

Let \(A_S\) be the weighted coefficient \(\ell^1\) space in the source
variable. For the monomial \(f_n(a)=a^n\),
\[
 \|f_n\|_S=S^n,\qquad D_a^n f_n=n!,
\]
and the output is constant, so its norm is \(n!\) at every reduced radius
\(0<S'\le S\). Therefore
\[
 \|D_a^n:A_S\to A_{S'}\|\ \ge\ n!/S^n.
\]
For the registered \(S=1/4\), the order-eight ratio is
\(8!4^8=2642411520>12^8=429981696\), where 12 is the declared
six-neighbour/two-orientation branch count. The order-32 row supplies a
larger exact witness. More generally, for even \(n\),
\[
 n!\ge (n/2)^{n/2},
\]
so \((n!/S^n)^{1/n}\) is unbounded. Given any fixed \(C\), choose an even
\(n>2(CS)^2\); the displayed lower bound then gives
\(n!/S^n>C^n\). This argument is independent of the final reduced radius.

## Finding and decision

The pure repeated radius-loss derivative architecture cannot supply the
required exponential \(C^n\) history envelope. Radius loss is necessary for a
one-step derivative, but it does not cure the factorial cost of iterating that
derivative. The route is therefore parked at the formal level.

This does not reject the actual Q3 history. A surviving proof must use a
derivative-closed cancellation or a genuinely different analytic/Frechet,
symmetric, modular or state-weighted seminorm, and must still prove the common
core, both orientations, factorial spatial incidence, volume-uniform history,
exhaustion Cauchy property and common alpha before any OS/KMS/GNS or QFT
promotion.

## Adversarial review

1. The source polynomial and \(B\) are loaded from the registered upstream
   manifests; no physical number is fitted to the factorial rows.
2. The witness applies to the pure formal derivative \(D_a^n\), not to every
   Q3 commutator word; cancellations are an explicit open escape route.
3. Since the differentiated witness is constant, shrinking the output radius
   cannot improve the lower bound.
4. Lean R289 checks only rational fixtures and finite factorial inequalities; it
   does not formalize the coefficient completion, unbounded operators, history,
   or limits.
5. No OS/KMS reconstruction, GNS gap, continuum, C6, Sector A, Pre-A, or TECT
   production owner is inferred.

## Reproducibility

```text
python codes/foundations/pre_a_cp1_st8_q3lock_repeated_radius_loss_derivative_obstruction.py --self-test
python codes/foundations/pre_a_cp1_st8_q3lock_repeated_radius_loss_derivative_obstruction_independent.py --self-test
python codes/foundations/pre_a_cp1_st8_q3lock_repeated_radius_loss_derivative_obstruction_verify.py --skip-lean
lake env lean verification/lean/Tect/R289.lean
```

The generated JSON run artefacts record the exact assertions and source
hashes. No formal result, negative-result authority, tier change or PDF is
created by this checkpoint.
