# EXP-001150 — Inductive-limit bounded Lipschitz cylinder form contract

## Question

Can the bounded finite-support C1 cylinder class be embedded consistently into every larger bounded-degree Q3 graph without changing its local weighted form constants?

## Exact checkpoint

For a multiplier with `||f||∞ <= M` and `||grad f||∞ <= L`, the shifted Q3 form product estimate is

```text
q_K[f psi] <= 2 M^2 q_K[psi] + (L^2/chi) ||psi||^2.
```

The cross orientation inherits `K_edge <= 21 K_on`. At the declared fixture `chi=1`, `M=1`, `L=1`, a support of size `S` therefore has squared bounds

```text
same orientation: 2 + S
cross orientation: 21 (2 + S).
```

The multiplier is extended from an ambient graph `Lambda` to a larger graph `Lambda'` by keeping the same finite support and acting as the identity outside it. The exact constants are unchanged for every declared `V >= S`.

For two fixed-support factors `(M1,L1)=(1,1)` and `(M2,L2)=(2,3/2)`, the bounded C1 product rule gives

```text
M12 <= M1 M2 = 2,
L12 <= M1 L2 + M2 L1 = 7/2,
same bound = 81/4,
cross bound = 1701/4.
```

## Verification

- Primary: `92/92` exact Fraction assertions.
- Independent: `61/61` exact Fraction assertions.
- Integrated: `15/15` assertions.
- Lean: `lake env lean Tect/R320.lean` PASS; registry metadata PASS with 156 entrypoints and 2329 assertions.

## QFT meaning and boundary

This closes a bounded fixed-support test-algebra/form contract suitable as an inductive-limit input. It does not prove convergence of finite-volume dynamics, a common `alpha_t`, exhaustion-independent states, modular transfer, OS/KMS/GNS reconstruction, a mass gap, a continuum limit, C6, Sector A or Pre-A. Support growth, unbounded polynomial products, and all dynamics-limit gates remain explicit successor obligations.

## Adversarial review

The volume independence is only at fixed support; the cross-orientation factor 21 is retained; the product gradient uses the full Leibniz bound; and algebraic compatibility is not identified with dynamical convergence. These boundaries remain open by construction.
