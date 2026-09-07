# Q3LOCK manuscript content repair: pressure, association and citations

Date: 2026-09-06. Status: T0 internal content audit; no signed review.
Authority: EXP-000780 -> EXP-000781 -> EXP-000782, through R-497.
PDF: deferred until content review and final organization are complete.

## Findings and scope

The v0.1.0 manuscript introduced two mathematical transcription defects that
are absent from the cited research notes:

1. In `eq:log-supermodular` it printed a minus sign before the mixed
   derivative of the log density. For rho=exp(-S)/Z, the required condition
   is partial_i partial_j log rho = -partial_i partial_j S >= 0. A spatial
   bond alone gives +epsilon*c, so the old displayed sign is contradicted
   even before considering the Q3 quartic. The source note
   `q3lock-continuous-loop-fkg-content-260905.md`, Sections 2--3, has the
   correct sign. The manuscript now reproduces that sign and the complete
   finite-dimensional conditioning/likelihood-ratio induction.
2. Section 3 called p=log(Z)/V entire in the complex source. The source note
   `q3lock-finite-volume-pressure-content-260905.md`, Section 5, correctly
   asserts entire Z and real-analytic p. Exponential integrability gives
   holomorphic Z, while positivity on the real line gives only local
   nonvanishing neighborhoods and local logarithms. Complex zero exclusion
   was never established. The manuscript now gives precisely this argument.
   The elementary MGF cosh(z), which vanishes at i*pi/2, tests the invalid
   general implication; it is not claimed to be a Q3LOCK partition function.

Section 4 also compressed the thermodynamic limit too far for independent
reading: the displayed trace upper bound did not supply a finite lower bound,
and the moving-temperature comparison was only asserted. The manuscript now
includes the Gaussian Jensen lower bound, the retained quartic estimate,
the exact remainder-volume inequality, the two trace comparisons, the
enlarged-interval secant estimate, and the local uniformity argument from
`q3lock-thermodynamic-pressure-content-260905.md`, Sections 2--7. These
arguments still depend on the finite-volume loop representation in Section 3.

This repair does not replace a missing proof of the loop representation,
periodic source-uniform moments, weighted DLR passage, FSS passage or
Falk--Bruch cutoff passage with an assumption that those claims are true.
Their detailed transfer into the manuscript remains required. A conditional
composition alone does not satisfy the user's self-contained-paper objective.

## Bibliographic reconciliation

The three malformed manuscript entries have been checked against primary
source title pages and records accessed on 2026-09-06:

| Key | Correct identity | Primary locator |
|---|---|---|
| KP | Y. Kozitsky and T. Pasurek, Euclidean Gibbs Measures of Interacting Quantum Anharmonic Oscillators | https://arxiv.org/pdf/math-ph/0609045v1, title page |
| KKK | A. Kargol, Y. Kondratiev and Y. Kozitsky, Phase Transitions and Quantum Stabilization in Quantum Anharmonic Crystals | https://arxiv.org/pdf/0710.2303v1, title page |
| KK-asym | A. Kargol and Y. Kozitsky, A Phase Transition in a Quantum Crystal with Asymmetric Potentials | https://arxiv.org/abs/math-ph/0611017 |

The KKK endpoint locator is Proposition 3.9, equation (3.23). Its vector
rotation-invariant phase discussion and its symmetric scalar discussion are
distinct from the asymmetric scalar comparison. The revised crosswalk keeps
these cases distinct. Peripheral phase-field citations are removed from the
paper's comparison table; their relevance and metadata were not established
by this review. No comprehensive novelty search is claimed by this repair.
The existing external-source freeze remains unchanged, including its hashes.

## Reproduction

Run from the repository root:

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_manuscript_content_audit.py
```

The script differentiates the Q3 and quadratic-bond energies symbolically,
recomputes Gaussian polynomial expectations from Wick moments and the cube
graph, and checks the manuscript's corrected formulas. It tests deliberately
reintroduced sign, analyticity and bibliography errors. It also verifies TeX
references and citations without invoking a compiler. Its result is written
to `claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-q3lock-manuscript-content-audit/result.json`.
Run fingerprints bind the current draft for this audit; they are not the
final release hash freeze.

The initial executed run passed all 32 assertions, including the deliberate
sign, analytic-domain and author-name mutations. The unchanged upstream
pressure and FKG verifiers also replayed at 55/55 and 504/504. These counts
describe finite checks only. They do not change the registered T0 status.

## Adversarial review

| Objection | Disposition |
|---|---|
| The old FKG sign can be hidden by calling rho an action. | UPHELD against v0.1.0: rho is explicitly the density exp(-S)/Z. Corrected in the draft; the old sign is a rejecting mutation fixture. |
| Entire Z implies entire log Z. | UPHELD against v0.1.0: cosh is an exact counterexample to this general inference. Real-analytic pressure is the sufficient corrected statement. |
| The Gaussian pressure constants were copied without checking graph multiplicities. | DISMISSED for the new finite diagnostic: enumerate Q3 edges, integrate the polynomial by exact Gaussian moments, and compare with separately stated formula oracles. |
| Finite symbolic tests prove the thermodynamic or loop limit. | UPHELD as a prohibited inference: the tests cover algebra and transcription. The limit arguments must be read as analysis, and several other manuscript blocks remain compressed. |
| The new audit is an independent signed referee report. | UPHELD as false: this is a local internal audit. External mathematical and literature signatures are still absent. |
| New equation numbers will silently invalidate the audit tables. | MITIGATED: use stable TeX labels in the applicability and proof-audit tables and check that each label resolves. |

Units: the entire/real-analytic distinction does not alter h, beta or the
pressure normalization. Sign: log density and action have opposite Hessians.
Limit cases: zero locking leaves the positive spatial-bond sign intact;
lambda>0 is retained in the phase model. No quadrature or convergence rate is
inferred from floating-point samples. External reviewers should challenge the
analytic pressure argument as well as replay the mutation tests above.

## Next content gate

Transfer the detailed fixed-volume Gaussian/weighted-loop limit into Section 3,
then expand the periodic moment and source-zero DLR arguments. Keep their
inputs explicit until that work is complete. The claim tier, authority chain,
external-review requirements and deferred PDF rule are unchanged.
