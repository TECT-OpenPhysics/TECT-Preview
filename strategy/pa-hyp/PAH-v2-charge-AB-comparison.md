# PAH-v2: fixed-integer and fixed-displayed-amplitude comparison

Date: 2026-09-11 UTC. Exploration: EXP-001732. Task: T-090.
Disposition: AUXILIARY_SUPPORT; comparative definition research only.
Neither A nor B is adopted as an operative refinement contract.

## 1. New authorization and immutable baseline

The operator requested both alternatives be tried rather than choosing blindly.
This authorizes the present two explicit, new comparison proposals. It does
not retroactively approve a full refinement tower, change PAH-001-v1/v2-r2,
or close a mathematical or physical gate. EXP-001731 and its uninstantiated
draft remain historical records; their missing full-map input remains real.
However, waiting for a charge choice is no longer the next research action:
the newly authorized comparison can inform that choice.

Source locators and SHA-256:

- `strategy/pa-hyp/PAH-001-v1.json`:
  `03e7ccdf7ff26fbd902ddc2c46a0cfd693ba2c5e861489aa87fb696882c2ea37`.
  Locators: functional_or_action, dynamics, finite_regulator, ordered_limits.
- `strategy/pa-hyp/PAH-001-v2-r2.json`:
  `2e1f5f21796a224f80141572dd9dd6451dd2cbba86233998ea992aa2bff6e36a`.
  Locators: integer_counting_space, root_partial_maps, operators_and_pairings.
- `strategy/pa-hyp/PAH-v2-finite-result-v1.json` (R-570):
  `9595fbb674443962c2790e4c0737eece6cb086ed9ba9d47783e7777907c678e7`.
  Applicability: exactly finite v2 identities, not comparison or convergence.
- `strategy/pa-hyp/PAH-v2-charge-AB-prereg.json`:
  `33fe50af87c588715b18fed5415cdad5dc5b17f0b9c3d3a25edd6e2874c06457`.
  Written and pinned before the primary calculation. Other input pins are
  inside it. Its hash is integrity evidence, not branch-adoption authority.

No old OMC comparison, Q3LOCK or TECT-YM theorem supplies a premise. No external
theorem is imported; the arguments use the displayed finite definitions and
elementary integer, root-of-unity and finite-sum identities.

## 2. Exactly what the two proposals compare

Work on one fixed admitted finite anchored two-cell complex G. There is no
new carrier or physical dimension/metric/volume. The execution fixture is
exactly the triangle and real parameters already pinned for R-570. Keep all
edges, closed faces, O/C anchors, boundary, epsilon, couplings, beta, nu and
external stochastic time fixed. The stationary law at each regulator remains
the full tuple-counting Gibbs law, not its conditional law on an image.

To avoid confusing the stage with aperture index j_v, write the stage r>=0.
The proposed schedule is, for integers q>=1, m>=q and real R0>0,

    K_r = 2*2^r,  M_s,r = 2^r,
    M_psi,r = m*4^r,  R_max,r = R0*2^r,
    d_r = R_max,r/M_psi,r = (R0/m)*2^(-r).

All four local-state cutoffs grow in this explicit schedule. It is one
prospective diagonal, not all possible cutoff paths, a proof of path
independence, or a replacement for later stages of the source order.
The order remains local cutoff, lattice, volume/exhaustion, selector,
aperture collapse, optional ground state, then observation time. No limit
is taken in this checkpoint.

| Proposal | Q_r | State injection, coarse to fine | What it preserves |
|---|---|---|---|
| A: fixed integer sector | q | J_A(j,ell,n,u)=(2j,ell,2n,2u) | Every ell and total Q, aperture and displayed phase/link |
| B: fixed displayed amplitude sum | q*2^r | J_B(j,ell,n,u)=(2j,2ell,2n,2u) | All displayed s, psi, U, and sum_v abs(psi_v) |

For both injections, coordinate ranges follow from doubling and the
quadrupled radial bound. They preserve the relevant sum constraint and are
injective on the full integer tuples. Doubling modulo 2K embeds Z_K into
Z_(2K); it does not quotient distinct labels. In particular zero-radius phase
labels and epsilon=1 aperture labels survive. The maps commute with carried
anchor-preserving cell permutations, including edge sign reversal, and with
the coarse gauge group embedded by g -> 2g. This does NOT say the image is
invariant under all fine gauge transformations or fine dynamics.

The displayed identities hold at every proposed stage, independently of the
fixture: s and U are unchanged; psi(J_A x)=psi(x)/2, while psi(J_B x)=psi(x).
Since occupations are nonnegative,

    sum_v abs(psi_v) = d_r Q_r.

Thus A gives (R0/m)q*2^(-r) and B gives (R0/m)q. This quantity is a displayed
amplitude sum, NOT physical mass, electric charge, energy, spatial density,
or an integral of abs(psi)^2. A different radial-mesh schedule could have
different behavior at fixed Q: the comparison does not disprove all fixed-Q
architectures. Changing Q between regulators in B does not make Q
nonconserved under the unchanged dynamics within any one finite regulator.

## 3. Static preservation is not dynamic preservation

Every term of the unchanged displayed functional depends only on s, psi, U,
fixed couplings and the same incidence/face data. Therefore

    F_(r+1,B)(J_B x) = F_(r,B)(x).

This is a substitution identity on the image, not equality of whole state
spaces or Gibbs laws. J_B has a proper image: for example an odd aperture
index is a valid fine coordinate but is never an image coordinate. Every
fine tuple has strictly positive Gibbs weight for finite beta and finite F.
Consequently, with the unchanged full tuple normalization,

    Z_(r+1,B) = Z_(r,B) + sum_(y not in image J_B) exp(-beta F_(r+1,B)(y))
                > Z_(r,B),
    pi_(r+1,B)(J_B x) = (Z_(r,B)/Z_(r+1,B)) pi_(r,B)(x).

No large fine partition sum is numerically evaluated. Normalizing after
conditioning on the image would remove the second term, but would change the
state used in the question; that substitution is not made. No free-energy
ranking or physical preference is inferred between the A and B ensembles.

In A, matter amplitudes are halved, so image F equality is not an identity.
On the frozen first-pair seed (all indices zero, occupations (1,0,0)), the
exact values are F_coarse=23/12 and F_image,A=295/384. These are computed
outputs of the unchanged formula, not adjusted inputs or a physical sign test.

## 4. Root correspondence, directions and a separating observable

The exact finite generator remains

    L h(x) = sum_(valid labelled roots a) m_a(x)
             exp[-beta (F(ax)-F(x))/2] (h(ax)-h(x)).

There is no averaging of coincident labels, rate multiplication, mobility
fit, or time acceleration. For a valid coarse root, compare its injected
endpoint with the original fine root at the injected initial point. On A,
TR requires one fine step; PH, LK and AP require two successive same-signed
fine steps. On B all four require two. Intermediate range validity follows
from the linear coordinate updates, with PH/LK modular wrapping. In the
K=2 case the two signs remain distinct paths even if final endpoints agree.
An identity loop TR is a harmless exception to minimum-step language; the
issued triangle has no loops. No universal minimal-path theorem is claimed.

Two steps of a continuous-time Markov chain do not become one generator
root. Moreover an injection supplies the REVERSE observable trace

    J*: A_fine -> A_coarse,  J*h = h composed with J,

not the requested forward pullback I=p*: A_coarse -> A_fine from a total
fine-to-coarse state map p. The following diagnostic is carefully typed:

    h(y) = indicator(any fine aperture index is odd).

This full finite observable is gauge- and every cell-automorphism-invariant.
For either proposed J, J*h=0 on the entire coarse space, so L_coarse J*h=0.
At the prescribed seed image all fine aperture indices are zero. Each valid
AP+ root makes h=1; AP- is invalid; PH/TR/LK leave h=0. The AP mobility is
strictly positive because epsilon>0, and all rate exponents are finite.
Hence J*L_fine h is strictly positive at the seed. The exact first-pair rates
at epsilon=1/2, beta=1, nu=2, obtained independently twice, are

    A: (3/8) [exp(59/1280) + 2 exp(13/320)],
    B: (3/8) [exp(11/80)   + 2 exp(37/320)].

This diagnoses failure of exact TRACE intertwining for these injections at
this finite pair, not the forward-generator defect for a nonexistent p/I.
It is not a contradiction in the v2 finite model, an all-map no-go, or an
eventual or weak-L2 convergence obstruction. Although parity observables can
be written at successive regulators, no one fixed common observable f and
comparison realization is identified by this argument.

For B there is a separate full-domain obstruction to naively inverting the
occupation doubling while preserving every displayed radial amplitude. The
first fine sector contains ell=(1,1,0), with Q_fine=2 and M_psi,fine=4.
An amplitude-preserving coarse tuple would require ell=(1/2,1/2,0), outside
integer counting states. Rounding, image restriction, conditional averaging
and label erasure are not implemented. This does not rule out other total
comparison maps with explicitly measured field/generator discrepancies.

## 5. Reproduction, coverage and author hostile review

From the repository root with the ready Python runtime:

    python -X utf8 verification/scripts/pah_v2_charge_ab_primary.py --check
    python -X utf8 verification/scripts/pah_v2_charge_ab_independent.py --check

Omit --check to regenerate each run, primary before independent. Runs are in
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-11-pah-v2-charge-ab/`.
Both scripts assert immutable input pins and derive every reported quantity.
Primary uses the frozen root enumerator and Gaussian-rational field algebra;
independent imports neither it nor primary, uses flat tuples and a separate
scalar-energy calculation, and only then cross-checks the stored primary run.

Each implementation exhausts 1536 coarse fixture states and 26112 labelled
coarse incidences per branch. AP/PH/LK/TR totals are 4608/9216/9216/3072.
Both reproduce the prescribed path endpoints for every incidence. Only A's
3072 TR incidences match a single fine step. Primary checks phase-general
image energies on all 1536 states (A: zero equal; B: all equal). Independent
energy coverage is the 24-state zero-phase/link slice plus exact seed/AP
rate exponents; it does not claim a second phase-general energy enumeration.
Generality of the field identities above is established by substitution, not
by the fixture counts. No floating tolerance, quadrature or extrapolation is
used. Finite inputs are dimensionless relational-model coordinates; no units
or physical scale are inferred.

| Concrete objection | Disposition and test |
|---|---|
| The wrong sign or missing half in exp[-beta Delta F/2] could mask a rate error. | DISMISSED for the fixture: independent scalar energies reproduce every rational exponent and positive AP coefficient. |
| A keeps Q, so it must keep displayed amplitude on this schedule. | UPHELD as a false shortcut: d halves; the code recomputes the discrepancy. Not a rejection of other fixed-Q schedules. |
| B keeps F, so the two normalized Gibbs states are identical. | UPHELD as false: positive off-image counting states contribute to Z_fine. No conditioning is used. |
| Two fine steps are equivalent to one coarse generator channel. | UPHELD as false: primitive endpoints are checked separately; the positive parity witness separates the actual generators in trace direction. |
| J can simply be inverted on every fine tuple. | UPHELD as false for amplitude-preserving inversion: odd occupations demand half-integer coarse states; even aperture images are not dynamically closed. |
| Invisible zero-radius or epsilon=1 labels can be erased. | DISMISSED as an allowed operation: controls retain distinct integer labels despite coincident displayed values. |
| A finite parity witness refutes eventual or weak-Gibbs-L2 compatibility. | UPHELD scope objection: those targets need a fixed common algebra/map and quantified estimates, neither supplied. |
| Imported primary code, derived constants or an external reviewer are hidden. | DISMISSED for code independence and hardcode masking: independent uses separate arithmetic; outputs are derived from pinned inputs. UPHELD regarding authorship: both are same-task work, not independent-person review. |

The independent run separates eight mathematical shortcut controls from four
documentary scope guards. This is not an external hostile audit. External
review is invited using the two reproduction commands, especially on map
direction, Gibbs counting normalization and labelled-root multiplicities.
Lean: NOT_RUN at this unadopted comparison checkpoint. R-570's prior Lean
PASS is not counted as a new comparison proof. A future formal result must
add its own source-specific formalization and independent admission review.

## 6. Decision and exactly one next question

Both proposals have been examined; neither is parked merely for lack of a
preliminary choice. B is the more useful field-preserving design candidate
on this declared schedule. A remains a fixed-integer-sector control. That is
a criterion-dependent research recommendation, not empirical ranking,
branch adoption, or a claim B supplies a common-core dynamics.

Next single question: can B be extended to an explicit TOTAL fine-to-coarse
comparison p and full observable pullback I=p* that retain every odd/invisible
counting state, are gauge/anchor-compatible, and have a well-defined full
labelled-root discrepancy under the unchanged sup norm, Gibbs states and
Markov time? State the gauge-group comparison and all unmatched roots; do
not silently replace p by image inversion, conditioning or rounding.

One bounded design attempt is appropriate; re-review on either an actual
full-domain algorithm with symmetry witnesses or an exact obstruction to its
declared requirements. If no such new input is produced, preserve this
boundary and HOLD_FOR_EVIDENCE without re-running A/B tables or old owner
searches. Later lattice/volume/selector maps and owner adoption remain open.

There is no change to T-054's active gate or C6 tier, no new result/claim-card
promotion, and no gate-level synthesis PDF. Full contract completion remains
open. No physical Pre-A, spacetime, QFT, gravity, continuum, infinite-volume
dynamics, Yang-Mills, causal cone, mass gap, event horizon or TOE conclusion.
