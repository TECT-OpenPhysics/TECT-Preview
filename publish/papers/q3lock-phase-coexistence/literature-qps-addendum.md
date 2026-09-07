# Broader-theorem comparison: quantum Pirogov--Sinai and oscillator stability

Date: 2026-09-07. Content-only addendum to manuscript v0.1.7.
Status: BOUNDED INTERNAL REVIEW / NO PRIORITY CLAIM / PDF DEFERRED.
This document changes no theorem, analytic import, registered tier or result.
The sole paper authority remains EXP-000780 -> EXP-000781 -> EXP-000782,
registered as R-497 / EXP-001598, T0, claim_bearing=false.

## Target and comparison rule

The target is finite-temperature coexistence for the actual, untruncated
positive-lambda Q3LOCK Hamiltonian on Z^3, with onsite space L^2(R^8), the
collective-source pressure cusp and two tempered Euclidean DLR states in the
stated sufficient regime. A finite-spin theorem, a cutoff-dependent theorem,
or a ground-state stability theorem does not supply that conclusion merely
because its title mentions quantum systems or infinite degeneracy.

The following are comparison citations, not additional proof premises. A
failed direct application is not a proof that every reduction is impossible.
Source equation numbers refer to the linked versions, not a guessed journal
pagination. No numerical experiment can decide this applicability question.

## Original-source checks

### DFF I: norm-small quantum perturbations

Primary source: N. Datta, R. Fernandez and J. Frohlich,
*Low-temperature phase diagrams of quantum lattice systems. I*,
[author-hosted text](https://webspace.science.uu.nl/~ferna107/papers/pirogov.pdf).
Locators: Section 2.1, pp. 5--11; Section 2.2, H1.1--H1.5 and H2,
pp. 14--16; Theorems 2.2--2.3, pp. 23--24.

| Hypothesis | Direct Q3 coordinate-space split | Disposition |
|---|---|---|
| Finite-range, translation-invariant reference | Onsite potential and nearest-neighbor spatial terms | SATISFIED structurally |
| H1.1 common product eigenbasis | Coordinate multiplication is not the displayed discrete product eigenbasis | UNASSESSED as a replacement construction |
| H1.2 bounded operator-norm interactions and parameter derivatives | Quartic multiplication and the collective coordinate are unbounded | FAILED |
| H1.3--H1.5 reference configurations, Peierls bound and regular diagram | No matching reference package is supplied here | UNASSESSED |
| H2 / (2.62) operator-norm decay for the quantum perturbation | The kinetic Laplacian is unbounded at every finite positive mass | FAILED |

Disposition: DOES-NOT-APPLY to this direct split; no phase conclusion imported.
The source also discusses bosonic algebras. Exclusion based only on its
finite-dimensional spin introduction would be an inadequate argument.
Its perturbation parameter is not Q3LOCK's onsite locking coefficient.

### FRU: finite onsite spaces, including restricted ensembles

Primary source: J. Frohlich, L. Rey-Bellet and D. Ueltschi,
*Quantum Lattice Models at Intermediate Temperature*,
[arXiv:math-ph/0012011v3](https://arxiv.org/pdf/math-ph/0012011v3).
Locators: Section 2.1 / (2.1), p. 3; Theorems 4.1--4.4, pp. 15--18.

The finite-dimensional onsite-space hypothesis is FAILED for L^2(R^8).
The finite alphabet in Sections 4.1--4.2 does not become a continuous
oscillator merely because the later restricted ensembles can contain
infinitely many configurations. The theorem constants explicitly depend on
the local dimension M. The required norm and reference-gap estimates for a
new cutoff family are UNASSESSED. No uniform removal of M follows here.

Disposition: DOES-NOT-APPLY directly. This is not a no-go against a separately
proved cutoff-uniform extension. In particular, its KMS conclusions are not
imported into the paper's Euclidean DLR statement.

### Yarotsky: unbounded perturbations, but a different target

Primary source: D. A. Yarotsky,
*Ground states in relatively bounded quantum perturbations of classical
lattice systems*,
[arXiv:math-ph/0412040v1](https://arxiv.org/pdf/math-ph/0412040v1).
Locators: (1)--(2), Theorem 1 and Example 1, pp. 2--4; Theorem 2, p. 4.

Possibly infinite-dimensional onsite spaces are allowed: that domain
objection does not apply. The reference has a nondegenerate gapped product
ground vector, with suitably small relative-form perturbations. Example 1
explicitly treats an anharmonic crystal at sufficiently weak spatial
coupling. A matching reference and quantitative smallness regime for this
paper are UNASSESSED. The stated ground-state stability conclusion is not
the requested finite-temperature two-phase theorem.

Disposition: DOES-NOT-APPLY as a direct source for the target conclusion;
potential applicability in another parameter regime is left open. The
relative-form framework also shows why the DFF operator-norm obstruction
cannot be generalized to all perturbative methods.

## Model-side domain check

For a real normalized smooth compactly supported function phi on R^8, put
psi_k(q)=exp(i k q_1) phi(q). Then

    <psi_k, (-Delta/(2m)) psi_k>
      = (||grad phi||_2^2 + k^2)/(2m).

The cross term vanishes because phi is real. Thus increasing a finite mass
does not make the kinetic operator bounded. Translating the support of phi
to large coordinate values likewise witnesses unbounded quartic
multiplication. These elementary domain observations concern the direct
coordinate-potential/kinetic split only. Moving kinetic energy into a new
reference changes the hypothesis problem and requires a fresh crosswalk.
No numerical threshold or new phase theorem is asserted by this check.

## Legacy quarantine and unresolved source access

The separate R-167 route already records a fixed-Ritz DFFR construction in
EXP-000837 and its lack of automatic cutoff-uniform extension in EXP-000838.
The linked authority certificates are
[fixed-Ritz scope](../../../strategy/pre-a-cp1-st8-q3lock-fixed-ritz-dffr-two-level-qps-zero-source-two-phase-route-split-certificate-260813.md)
and [Hilbert--Schmidt uniformity boundary](../../../strategy/pre-a-cp1-st8-q3lock-dffr-hilbert-schmidt-uniformity-and-yarotskii-gap-route-split-certificate-260813.md).
Their order is fixed M first, then sufficiently large N and low temperature;
they are not a proof for the untruncated paper model. They are comparison
history only, not additions to the paper's authority chain. This audit does
not rerun or reaccept those legacy analytic arguments.

DFFR II was initially unavailable in EXP-001612. A subsequent public-source
download from the [author-linked reprint](https://luc-umass.github.io/pdf/ql2.pdf)
succeeded on 2026-09-07. The scan's article title page credits N. Datta,
J. Frohlich, L. Rey-Bellet and R. Fernandez (the archive cover omits the last
author). It is *Helvetica Physica Acta* 69 (1996), 752--820,
DOI 10.5169/seals-116979. The privately cached source is not redistributed
with this package; its SHA-256 is
`7f130e15e90d75b49b193d75cc5f647f713f2abf1a90c0a795a930f3ccb11fbd`.
This is a comparison-source capture, not a modification of the R-497 manifest.

### DFFR II primary reassessment

Text extraction was checked against rendered pages 772, 776 and 796--800
(PDF pages 22, 26 and 46--50; the cover accounts for the offset).
Equation (4.7) uses the Hilbert--Schmidt norm; (4.10)--(4.13) give a
dimension-dependent comparison with operator norm. Section 4.2, p. 776,
requires bosonic occupation regularity (4.38), not unrestricted infinite
occupation by default. Theorem 5.2, pp. 799--800, requires reference-data,
two-level Peierls and block-smallness hypotheses, including parameter
derivatives in (5.21) and the strict condition (5.22).

| Requirement | Q3LOCK assessment for a direct import |
|---|---|
| Classical reference, regular parameter family, low/high projections and two-level Peierls data | UNASSESSED for an untruncated replacement construction; the R-167 fixed-Ritz data do not provide one |
| Actual Hilbert--Schmidt block bounds and derivatives | FAILED for the direct kinetic perturbation, which is unbounded; UNASSESSED for a different transformed reference |
| Bosonic regularity of the stated type | UNASSESSED for an identified Q3 occupation representation; coordinate-loop moments are not this hypothesis |
| Uniform strict smallness and passage to the same untruncated states | UNASSESSED; no cutoff-uniform constants or state-identification theorem supplied here |

Disposition: DOES-NOT-APPLY to the direct coordinate/kinetic split; a
different construction remains NOT-YET-ASSESSED. This replaces the earlier
source-access gap with a checked applicability boundary, not a proof that
all infinite-onsite contour methods fail. Neither a DFFR phase conclusion
nor the R-167 cutoff result is added to the paper's authority chain.

### Why occupation regularity cannot be replaced by trace finiteness

This is an elementary comparison fixture, not the Q3LOCK Hamiltonian.
For a single harmonic oscillator with occupation operator N and Gibbs ratio
q=exp(-beta omega) in (0,1), the probabilities are p_n=(1-q)q^n. Hence

    E exp(t N) = (1-q)/(1-q exp(t))    if t < beta omega,
              = infinity            if t >= beta omega.

Indeed, the summands form a geometric series; at the endpoint they are
constant and positive, and above it they grow. Every polynomial occupation
moment is finite, by the ratio test. Thus a finite heat trace and finite
polynomial moments do not imply an occupation MGF finite for all real t.
This does not show that Q3 fails (4.38): its number operator, reference and
state mapping must first be specified. It only prevents an unsupported
replacement of the newly checked hypothesis by existing moment statements.

Schneider--Beck--Stoll, *Quantum effects in an n-component vector model for
structural phase transitions*, Phys. Rev. B 13, 1123 (1976), is verified in
the [publisher record](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.13.1123).
The full text required authorization. Its applicability is NOT-YET-ASSESSED;
the abstract's broken mathematical rendering is not repaired by guessing,
and neither a rigorous finite-component theorem nor an approximation is
attributed to it without the text.

## Search coverage and adversarial disposition

Discovery queries included:

- "quantum" "anharmonic" "Pirogov" phase transition;
- "nonradial" "quantum" "phase transition";
- "anisotropic" "anharmonic crystals" phase transition theorem;
- "quantum lattice" "unbounded" "phase diagrams" Pirogov;
- "Quantum Lattice Models at Intermediate Temperature";
- "Quantum effects in an n-component vector model";
- "Convergent perturbation expansions" "Rey-Bellet".

Author-origin and publisher sources supplied the comparisons above. Search
snippets and third-party copies served only as discovery leads. Broader
anisotropic oscillator and continuous-spin contour theorems remain a
specialist follow-up, not an exhausted literature class.

1. Convention: a Pirogov--Sinai small perturbation parameter must not be
   identified with the positive internal locking lambda. UPHELD as a firewall.
2. Domain: unbounded operator norm does not imply failure of relative-form
   methods. UPHELD; Yarotsky is retained as the counterexample to that shortcut.
3. Limits: fixed-cutoff coexistence does not imply cutoff-uniform coexistence.
   UPHELD; the R-167 scope is retained without re-promotion.
4. Conclusion: ground-state stability is not finite-temperature DLR
   coexistence. UPHELD; no spectral or real-time conclusion is imported.
5. Evidence: source access failure is not mathematical non-applicability,
   and failure of listed imports is not novelty. UPHELD; unexamined items
   stay NOT-YET-ASSESSED and external signatures remain OPEN.

## Publication-value question and next gate

This narrows several direct-import shortcuts; it does not prove priority or
guarantee publishability. The candidate contribution remains the actual
positive-lambda collective lower bound and its loop/DLR composition. The
manuscript's standard infrared and threshold mechanisms remain standard.

The next useful review must identify an exact covering theorem, give a
hypothesis-level reduction, or explain the model-specific residual. Repeating
finite diagnostics cannot replace that decision. Obtain accessible source
text for the remaining Schneider--Beck--Stoll candidate and a signed specialist disposition;
keep every analytic review gate open until independently resolved. Do not
generate the paper PDF before the final content-review checkpoint.

## Documentation checkpoint replay

The EXP-001612 historical snapshot command was:

    E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_literature_addendum_snapshot.py

That script calls the existing manuscript checker in memory, compares its
entire nested payload with the preserved v0.1.7 run, and permits only source
hash changes for this addendum, README.md and external-review-handoff.md.
It records a new JSON under the claim runs directory; it does not overwrite
the old source-audit result. These are documentation/provenance checks, not
additional mathematical proof tests. A whole-payload byte-equality check
initially failed precisely because those paper-document hashes changed;
no diagnostic assertion changed. The scoped comparison makes that expected
difference explicit rather than replacing historical hashes.

Adversarial code boundary: an unexpected mathematical assertion, manuscript
hash, source hash, or canonical authority difference must fail the comparison.
No derived physical number is hardcoded, no new numerical approximation is
used, and the script cannot establish the applicability dispositions above.

For the current DFFR reassessment, use instead:

    E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_dffr_source_audit.py --source-pdf PATH_TO_AUTHOR_REPRINT

The new command checks the source bytes and exact geometric-series fixtures,
invokes the prior manuscript diagnostics in memory, and writes a compact
replay record with deduplicated source hashes. It does not duplicate the full
historical assertion payload or overwrite either older run. Source-page
interpretation is a recorded human-readable audit, not an automated theorem
certificate. Do not run an older standalone writer against revised documents.

Adversarial checks for this checkpoint: the regularity parameter t is not
the inverse temperature beta or the locking lambda; a finite truncation
has an entire MGF while the infinite oscillator need not; the equality
endpoint diverges; polynomial moments alone are insufficient. The fixture
changes no Q3 parameter, proves no absence of Q3 regularity, and cannot
replace the independent mathematical or literature review. The collective
proof section was also reread at this checkpoint; no new lemma or
independent acceptance is claimed from that repeated inspection.
