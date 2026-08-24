# EXP-001071 Static finite-support multi-character double-commutator envelope

## Decision

For a fixed finite support (S) and real amplitudes (a_x), the configuration character

[
W_{mathbf a}=exp!left(isum_{xin S}a_xq_x/hbaright)
]

has a finite static two-sided Gibbs-seminorm envelope in the registered finite periodic Q3 family.

## Exact interface

Set (P_x=p_x+a_x/2) and (Q_+=sum_x(a_x/(chihbar))P_x). On the polynomial CCR core,

[
delta_H^2(W_{mathbf a})=-W_{mathbf a}Q_+^2
-iW_{mathbf a}sum_x(a_x/(chihbar))F_x.
]

Since the (P_x) commute across distinct sites,

[
N_ho(W_{mathbf a}Q_+^2)^2
le 2|S|^3sum_x(a_x/(chihbar))^4
(32chi^2m_5+a_x^4/2).
]

The force functions commute with (W_{mathbf a}) and each other. If
(G_{m force4}) is the registered fourth-moment envelope, then

[
N_ho(W_{mathbf a}sum_x(a_x/(chihbar))F_x)^2
le 2left(sum_x|a_x|/(chihbar)ight)^2sqrt{G_{m force4}}.
]

The final estimate uses the seminorm triangle inequality.

## Fixture and Lean cross-check

For (S={1,2}), (a=(1/4,-1/3)), (chi=hbar=1), and (m_5=3), the shifted fourth-moment bounds are (49153/512) and (15553/162). The kinetic squared envelope is (1341774241/53747712). Using the registered force ceiling (423000), the force squared envelope is at most (287875<537^2), and the conservative total squared envelope is (293764=(5+537)^2). Lean R253 checks these exact rational fixtures.

## Adversarial review

- Cross-site CCR: only commuting distinct-site momentum variables are combined.
- Power inequality: the (|S|^3) cost is explicit.
- Force orientation: both two-sided products reduce to the same configuration moment.
- Support dependence: no support-uniform product claim is hidden.
- Force input: only the registered compact-source force grid is used.
- Triangle: no kinetic/force orthogonality is assumed.
- History: static bounds are not applied to evolved split histories.
- Domain: no unbounded-generator closure or modular multiplier is inferred.
- QFT: product-core density, direct (D,delta D), OS/KMS/GNS, gap, continuum, C6, Sector A and Pre-A remain open.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_static_double_commutator_bound.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_static_double_commutator_bound_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_multicharacter_static_double_commutator_bound_verify.py
lake env lean Tect/R253.lean
```

## Scope firewall

This is a static finite-support interface only. It is not a product-core density theorem, split-history theorem, direct projected (D) or (delta D) Cauchy theorem, common-alpha theorem, OS reconstruction, KMS/GNS result, mass-gap proof, continuum result, C6/Sector-A/Pre-A result, TECT production map or Clay result.
