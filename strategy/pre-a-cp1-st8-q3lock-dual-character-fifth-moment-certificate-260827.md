# EXP-001122 — finite actual-Q3 dual-character fifth-moment audit

## Finding

The primary and independent matrix lanes both pass 72/72 assertions, and Lean
R293 compiles.  For the declared Q3 graph family, beta=1, character
`W_a=exp(+i*(1/3)*q_0)`, and shifted positive operator `K=H-min(H)+I`, the
reference and dual fifth moments are:

| volume | oscillator dimension | reference `Tr(rho K^5)` | dual `Tr(W rho W* K^5)` | dual/reference |
|---:|---:|---:|---:|---:|
| 2 | 3 | 63.9954164591 | 68.7011134934 | 1.0735317823 |
| 2 | 4 | 104.0420763738 | 140.9261910350 | 1.3545115202 |
| 2 | 5 | 222.5786307139 | 369.1684837778 | 1.6585980541 |
| 4 | 3 | 675.1442618509 | 708.5442416574 | 1.0494708786 |
| 6 | 3 | 2917.7670562653 | 3007.4102681582 | 1.0307232244 |

For each row and each declared global spectral cutoff `Q_R=1_[K>R]` with
`R` in `{4,8,16,32}`, both states satisfy the finite Markov check
`R^5 Tr(rho Q_R) <= Tr(rho K^5)`.  The largest observed dual/reference
moment ratio is 1.6585980541.  A diagnostic tail ratio can be larger (the
largest recorded weighted-tail ratio is about 24.7035), so the rows do not
support replacing a dual-tail theorem by a reference-tail theorem.

## Interpretation and boundary

This is a T0, claim-nonbearing finite bridge for the actual truncated Q3
Hamiltonian.  It supplies evidence that a local character produces a finite
dual energy moment in the declared fixtures and instantiates the missing
actual-state direction identified by EXP-001079.  It does not establish a
uniform dual-state or modular-energy tail, a local projected-bond estimate,
unbounded-domain transfer, source/volume/beta/orientation uniformity, direct
`D`/`delta-D` Cauchy convergence, exhaustion independence, a common alpha,
Hamiltonian-to-OS/KMS identification, a GNS gap, continuum removal, C6,
Sector A, or Pre-A.

The spectral projector here is global for the shifted finite H.  It is not the
local modular projector required by the direct D/delta-D route.  All matrices
use truncated oscillator CCR, so the scalar kinetic-shift identity checked by
R293 is not an infinite-dimensional Weyl theorem.

## Verification

- Primary: `codes/foundations/pre_a_cp1_st8_q3lock_dual_character_fifth_moment.py`
- Independent: `codes/foundations/pre_a_cp1_st8_q3lock_dual_character_fifth_moment_independent.py`
- Integrated: `codes/foundations/pre_a_cp1_st8_q3lock_dual_character_fifth_moment_verify.py`
- Lean: `verification/lean/Tect/R293.lean`
- Manifest: `strategy/pre_a_cp1_st8_q3lock_dual_character_fifth_moment_manifest.json`
- Run JSONs: `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-primary-pre_a_cp1_st8_q3lock_dual_character_fifth_moment/primary.json`, `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-independent-pre_a_cp1_st8_q3lock_dual_character_fifth_moment/independent.json`, and `claims/C6-SPACETIME-SIGNATURE/runs/2026-08-27-integrated-pre_a_cp1_st8_q3lock_dual_character_fifth_moment/integrated.json`

Commands:

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_character_fifth_moment.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_character_fifth_moment_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_dual_character_fifth_moment_verify.py
```

## Adversarial review

1. Character sign and state side: both lanes use the recorded `+i` sign and
   `rho_dual=W rho W*`; no continuum CCR convention is silently substituted.
   **Disposition: UPHELD.**
2. Gibbs and dual normalization: the reference weights are normalized after
   shifting by the finite spectral minimum, and both traces and character
   unitarity residuals are checked. **Disposition: UPHELD.**
3. Tail direction: reference and dual tails are computed separately against the
   same global `Q_R`; one-sided reference control is not identified with the
   dual quantity. **Disposition: UPHELD.**
4. Local-versus-global projector: the tested projector is global shifted-H,
   not the local bond/modular cutoff in the D/delta-D proof. **Disposition:
   UPHELD-OPEN.**
5. Cutoff and volume: the five rows are finite oscillator/volume diagnostics;
   their ratios are not a uniform bound or asymptotic theorem. **Disposition:
   UPHELD-OPEN.**
6. Truncated CCR: the matrix character is a finite approximation and does not
   prove the Weyl relation or a common analytic core. **Disposition:
   UPHELD-OPEN.**
7. QFT promotion: common alpha, OS/KMS/GNS, gap, continuum, C6, Sector A and
   Pre-A are explicitly false in the manifest and integrated result.
   **Disposition: UPHELD-OPEN.**
8. Lean role: R293 contains only scalar algebra and finite fixture constants;
   it has no `axiom`, `sorry`, unbounded operator statement, or limit claim.
   **Disposition: UPHELD.**

## Next gate

Turn this finite diagnostic into a theorem only by proving a local/modular
dual-tail estimate on a specified common core, uniformly in the source,
volume, beta and orientation parameters.  Then retest the two-sided direct
`D`/`delta-D` Cauchy route; do not promote these finite rows to QFT dynamics.
