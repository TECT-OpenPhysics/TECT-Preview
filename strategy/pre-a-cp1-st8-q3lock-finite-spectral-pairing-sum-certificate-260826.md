# Finite spectral-sum pairing certificate

## Scope

EXP-001142 is a claim-nonbearing finite checkpoint. It rewrites the actual
Q3 full-generator Kubo-Mori pairing in the spectral basis of the reference
Hamiltonian. The result isolates the analytic quantity that a common-alpha
proof must control; it does not itself provide that control.

## Exact finite identity

For a finite Hamiltonian eigenbasis with Gibbs probabilities `p_i`,
logarithmic-mean weights `L(p_i,p_j)`, and

`delta_H(X)=i[H,X]/hbar`,

the two-sided Kubo-Mori form gives

`<delta_H D,delta_H D>_KM`

`= 2 sum_ij L(p_i,p_j) ((E_i-E_j)/hbar)^2 |D_hat_ij|^2 >= 0`.

The companion full-generator term is the negative of the same finite sum:

`<delta_H^2 D,D>_KM + <delta_H D,delta_H D>_KM = 0`.

R312 formalizes the finite rational sum identity and nonnegativity. The
primary commutator lane and independent eigenbasis lane test the identity on
18 actual rows: volumes 2, 4, and 6; beta values 0.5, 1, and 2; radius 0.5;
time 0.05; and both cutoff orientations. They pass 87/87, 85/85, and the
integrated verifier passes 12/12.

## Finite diagnostic

The largest primary spectral-sum reconstruction error is
`2.778268066994105e-19`; the largest full-pairing error is
`2.0330385858425025e-20`.

The maximum spectral second moment at volume 6 divided by that at volume 2 is
`10.050582897427127` for beta 0.5, `15.069311246350424` for beta 1, and
`22.16814654693396` for beta 2. The corresponding delta-D Kubo-Mori norm
ratios are `3.1702654301220785`, `3.8819210767802113`, and
`4.708306122899608`.

These values diagnose finite growth of the state-weighted derivative moment.
They are not a monotonicity theorem, an asymptotic lower bound, or a proof
that every common-core topology fails.

## Adversarial review

1. **Sign and positivity — UPHELD.** Both numerical lanes use the same
   `i[H,·]/hbar` convention and independently recover the positive spectral
   sum and its negative companion.
2. **Finite versus infinite — OPEN.** The identity is a finite eigenbasis sum;
   no limit interchange or uniform constant is established.
3. **Gibbs degeneracies — UPHELD.** The equal-probability logarithmic-mean
   limit is explicitly used in every finite spectrum.
4. **Volume ratios — OPEN.** Three finite volumes and one cutoff/time do not
   prove divergence or a route-wide obstruction.
5. **Common core — OPEN.** The missing theorem is a source/volume/beta/uniform
   high-energy tail bound for the actual history on an unbounded common core.
6. **QFT promotion — OPEN.** Product/core density, exhaustion independence,
   common alpha, OS/KMS/GNS identification, gap, continuum, C6, Sector A, and
   Pre-A remain open.

## Next gate

Prove or refute a uniform high-energy spectral-tail estimate for the actual Q3
history on a declared common core. If a lower bound is obtained, it must be
attached to the exact candidate topology and its source/volume/beta scope;
finite growth alone does not fire a no-go gate.

## Non-claims

This certificate does not prove thermodynamic Q3 dynamics, a QFT, a mass gap,
a continuum limit, C6, Sector A, Pre-A, or any Clay result.
