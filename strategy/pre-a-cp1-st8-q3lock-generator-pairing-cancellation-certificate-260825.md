# EXP-001140 — full-generator Kubo-Mori pairing cancellation

## Scope

This finite audit tests the cancellation-aware replacement for the EXP-001138 termwise `V'(q)f'(q)` estimate. It uses the actual Q3 histories on the two-site edge and four-site square:

`D_sigma(t)=U_(H+sigma W_L)(t) A_2 U_(H+sigma W_L)(t)^* - U_H(t) A_2 U_H(t)^*`,

with `delta_H(X)=i[H,X]/hbar` and `W_L=H-H_L`.

In the finite H eigenbasis, the two-sided Kubo-Mori form obeys the exact skew-adjoint identity

`<delta_H^2 D,D>_KM + <delta_H D,delta_H D>_KM = 0`.

This is a full-generator identity. It does not split or independently bound the kinetic and quartic-force pieces.

## Reproduction

- Primary: `python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_generator_pairing_cancellation.py`
- Independent: `python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_generator_pairing_cancellation_independent.py`
- Integrated and Lean: `python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_generator_pairing_cancellation_verify.py`
- Lean source: `verification/lean/Tect/R310.lean`

Results: primary `316/316`, independent `240/240`, integrated `12/12`, Lean `R310 PASS`, with 72 history rows in both numerical lanes.

## Finite diagnostics

The maximum Kubo-Mori `delta-D` norm on the square divided by the edge value was `2.4036` at beta `0.5`, `2.7175` at beta `1`, and `3.1214` at beta `2`. These are two-volume diagnostics only. They do not establish monotonicity, an asymptotic lower bound, or nonexistence of another topology.

## Hostile-review boundary

The full-generator cancellation error is at the numerical floor, but the identity alone supplies no source/volume/beta-uniform bound. It also does not prove modular-domain control, product/core density, exhaustion independence, a beta-independent common alpha, OS/KMS/GNS identification, a gap, continuum, C6, Sector A or Pre-A closure. The finite growth must therefore remain a diagnostic until an analytic family or certified lower bound is supplied.

## Next gate

Run the same pairing on the registered six-site 2x3 graph and an increasing structured cutoff/source family. Either derive a uniform Kubo-Mori delta-D estimate on the common core or record a route-specific obstruction, then return to the all-shape common-core theorem.