# EXP-001139 — fixed-beta Gibbs-weighted force cancellation

## Scope

This certificate records a route-local, one-site finite audit after the R308 obstruction to treating `V'(q)f'(q)` as a standalone K-form multiplier. The Q3 fixture is

`V(q)=17/12-q^2/2+3q^4/20` and `f(q)=16q/(16+q^2)`.

The proposed pairing is for a compactly supported `C^1` history `h` in a fixed-beta one-site Gibbs matrix element. Under the explicit zero-boundary contract,

`omega_beta(V'f'h) = beta^(-1) omega_beta((f'h)')`

and the product rule gives `(f'h)'=f''h+f'h'`. The exact derivative fixtures satisfy `|f'|<=1` and `|f''|<=1` on the audited rational grid, so Cauchy-Schwarz yields the conditional envelope

`|omega_beta(V'f'h)| <= beta^(-1)(||h||_2+||h'||_2)`.

## Reproduction

- Primary: `python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_weighted_force_cancellation.py`
- Independent: `python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_weighted_force_cancellation_independent.py`
- Integrated and Lean: `python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_gibbs_weighted_force_cancellation_verify.py`
- Lean source: `verification/lean/Tect/R309.lean`

Observed results: primary `135/135`, independent `77/77`, integrated `12/12`, Lean `R309 PASS`.

## Boundary and hostile review

This controls a linear fixed-beta state pairing only. It does not control the squared `V`-weighted norm that R308 obstructed. The history derivative `h'` is a one-site differentiable proxy, not the Q3 modular derivative `delta D`; the integration-by-parts boundary and operator-domain hypotheses are declared, not proved here. The explicit `beta^-1` factor prevents a beta-uniform claim. No volume/source-uniform D/delta-D Cauchy, product/core density, exhaustion independence, common alpha, OS/KMS/GNS identification, gap, continuum, C6, Sector A or Pre-A conclusion is licensed.

## Next gate

Construct the smallest finite edge-history fixture whose derivative-bearing history is the actual D/delta-D difference. Test source/cutoff uniformity at fixed beta. If the state-weighted pairing survives, promote only the finite-edge lemma; if it diverges, register the obstruction and move to the exact Hamiltonian common-core carrier.