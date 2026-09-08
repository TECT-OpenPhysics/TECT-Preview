# Q3LOCK Schneider--Beck--Stoll primary-source audit -- 2026-09-08

## Scope and status

This is a bounded primary-source and applicability audit for the remaining
Schneider--Beck--Stoll comparison item in the Q3LOCK literature packet. It
resolves source access and records the exact model/conclusion boundary. It does
not add a theorem premise, promote R-497, establish priority, certify novelty,
or authorize a PDF or submission.

The sole Q3LOCK research authority remains
EXP-000780 -> EXP-000781 -> EXP-000782, registered as R-497 / EXP-001598,
T0 and claim_bearing=false.

## Captured source

- T. Schneider, H. Beck, and E. Stoll, *Quantum effects in an n-component
  vector model for structural phase transitions*, Phys. Rev. B **13**,
  1123--1130 (1976), DOI: 10.1103/PhysRevB.13.1123.
- Publisher record: https://journals.aps.org/prb/abstract/10.1103/PhysRevB.13.1123
- Full-text endpoint used for the capture:
  https://harvest.aps.org/v2/journals/articles/10.1103/PhysRevB.13.1123/fulltext
- Version/date: published 1 February 1976; eight-page publisher PDF.
- Capture time: 2026-09-08T04:40:28Z.
- Local capture: ignored local source-capture cache (path intentionally
  outside the public package).
- Byte length: 516155.
- SHA-256: `4063397ab5af4502b69f2f030192fbd98b5ecc0ffb115b481dccee2ae2f0793c`.
- Visual check: all eight rendered pages inspected; text extraction agrees with
  the displayed equations and appendix layout.

## What the source actually studies

The paper studies an n-component displacement vector on a cubic lattice with
quadratic kinetic energy, an isotropic onsite quadratic-plus-radial-quartic
potential, bilinear ferromagnetic nearest-neighbour coupling, and a uniform
external field (Eq. (1), p. 1123). Its main question is whether quantum
zero-point fluctuations suppress a structural phase transition near the
classical displacive limit. The large-n section then computes critical
behaviour in an exactly tractable limit.

The source's quantum correlation inequality (Eq. (11), pp. 1124--1125) is
stated as rigorously available for n=1, n=2, and n=infinity; the paper
explicitly says that the proof had not been extended to 2<n<infinity. The
appendix derives a Trotter ferromagnetic-measure representation and explains
why classical continuous-variable inequalities can be transferred in the
ferromagnetic setting, but that appendix does not turn Eq. (11) into an
n=8 theorem for the Q3LOCK onsite interaction.

The source's conclusions concern suppression of an ordered state and critical
exponents at a quantum-mechanical displacive limit. It does not construct a
positive-source pressure cusp, a source-selected zero-source Euclidean DLR
state, or a parity-related pair of distinct tempered DLR states for an
untruncated finite-temperature n=8 model.

## Model-side comparison

| Source requirement or conclusion | Q3LOCK model-side fact | Disposition |
|---|---|---|
| Isotropic radial onsite quartic in the n-component vector | Q3LOCK has the nonradial Q3 edge polynomial `(q_e-q_f)^2(q_e^2+q_f^2)` with positive lambda, in addition to componentwise quartics | Direct model identity fails |
| Proven quantum inequality range in the paper | Q3LOCK fixes n=8, while the paper records the inequality only for n=1, 2, and infinity | Direct theorem import fails |
| Bilinear ferromagnetic spatial coupling | Q3LOCK has a positive spatial difference form, which can be expanded into a bilinear ferromagnetic part plus onsite terms | This structural overlap does not repair the onsite and n-range mismatch |
| Displacive-limit suppression / large-n critical exponents | Q3LOCK target is a low-temperature positive-lambda collective-source cusp and two infinite-volume DLR states | Different conclusion and quantifier |
| Trotter ferromagnetic-measure construction | Q3LOCK proves its own finite-mesh continuous-loop FKG with the actual Q3 internal edges and then passes to the loop/DLR limits | Historical/method comparison only; not an imported Q3 theorem |

The Q3LOCK polynomial is not made radial by an orthogonal change of variables:
its equal-norm coordinate and collective directions have different quartic
values, as recorded in `eq:nonradial-witness`. Flattening component and spatial
indices also leaves nonbilinear internal edge terms, as recorded in
`eq:nonbilinear-scalar-obstruction`.

## Applicability disposition

**Direct Schneider--Beck--Stoll phase-theorem import: DOES-NOT-APPLY.** The
source-access question is resolved, but the paper is not a covering theorem
for the untruncated positive-lambda Q3LOCK result. The decisive boundaries are
(i) the source's displayed rigorous inequality range does not include finite
n=8, (ii) its onsite interaction is radial whereas Q3LOCK is nonradial with
internal quartic edges, and (iii) its conclusion is quantum-fluctuation
suppression/large-n critical behaviour rather than the stated finite-temperature
DLR coexistence conclusion.

This disposition is not a no-go theorem for every possible anisotropic
reduction and is not a priority or novelty claim. Q3LOCK's loop FKG, DLR
compactness/tangent construction, infrared estimate, collective lower bound,
and strict-cusp composition remain internal proof obligations subject to the
A1--A23 signed review. The source is retained as a comparison citation and as
evidence that the earlier source-access gap has been replaced by a checked
applicability boundary.

## Next action

Update the literature crosswalk, imported-source ledger, theorem-applicability
matrix, and external-review handoff with this exact source/hash and the
n=8/nonradial/conclusion boundary. At final content/hash freeze, recapture the
publisher bytes and verify the hash again. Keep the PDF gate closed until the
mathematics and specialist literature reviews are signed.
