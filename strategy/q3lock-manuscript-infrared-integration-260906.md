# Q3LOCK manuscript integration: Hilbert reflection and the infrared bound

Date: 2026-09-06. Status: internal T0 content review; no external signature.
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782, through R-497.
PDF: deferred until content review and final organization are complete.

## Integrated proof content

Manuscript Section 7 expands the unchanged registered content in
`strategy/q3lock-reflection-infrared-content-260905.md`, Sections 2--7.
The exact FSS source map and coupling distinction are also checked against
`strategy/q3lock-fss-theorem-factor-transcription-audit-260905.md` and
`strategy/q3lock-fss-coupling-rescaling-audit-260905.md`. The frozen literature
locator is `strategy/q3lock-literature-source-freeze-260905.md`.

The local loop measure uses the physical onsite potential minus the auxiliary
harmonic term, without the allocated spatial diagonal. All spatial bonds
remain positive differences. Their bounded Gaussian kernels admit positive
finite-dimensional Fourier representations; finite complex measures and
dominated convergence pass positivity to the loop Hilbert space. The paper
then explicitly splits the even torus through both separating planes and
pushes a finite plus-half measure through its boundary loops. The result
covers bounded complex Borel half-loop tests, not only polynomials.

Gaussian domination is a separate finite-dimensional input. The scaled history
s_y=(sqrt(epsilon) x_yk)_k has dimension 8N and coupling J=c. The exact local
prior includes the temporal term and B_0+3c|q|^2; its lower bound is
g|s|^4/(32 beta)+(r+6c)|s|^2/2. This checks the prior moment condition at
each mesh without claiming a mesh-independent prior normalization.

The manuscript fixes G as the backward vertex difference, B=G* as the forward
edge divergence, and L_sp=G*G=BB*. All inverses are restricted to zero-sum
vertex fields. For eta_y(t)=t sqrt(epsilon)(f_y u)_k, the FSS theorem field
h_t=G L_sp^(-1) eta has norm squared beta t^2 <f,L_sp^(-1)f>. The completed
square instead uses h_t/c. The vertex norm and either edge displacement
cannot be silently interchanged.

The finite FSS bound supplies zero-sum-source uniform integrability. The paper
first transfers the bound by bounded truncation under the already established
interacting weak limit, then proves convergence of MGFs and their polynomial
source moments using exponential bounds at larger source parameters. Two
time integrals give Var(X_L(f))=beta^2 <f,D_L f>; the nearest-neighbor Fourier
eigenvalue is 2E(p). Their combination gives the nonzero-mode constant
1/(2 beta c E(p)), with no factor eight or extra factor from complex modes.

The singular spatial sum is handled by explicit continuous and discrete
tails, respectively sqrt(3) delta/4 and 13 delta/(8 pi). Their proof uses
the shell count (2n+1)^3-(2n-1)^3 and the lower trigonometric bound for E.
Ordinary Riemann convergence applies away from zero; taking L to infinity
before delta to zero gives I_(3,L)->I_3. The trace identity then states the
zero-mode subtraction with the local lower bound left as a separate input.
No decimal value of I_3 or positive sign is inferred from this upper bound.

## Primary-source visual check

Source: Froehlich--Simon--Spencer, Section 2, Theorem 2.1, printed page 81;
proof and immediate consequences on printed pages 82--84.
URL: https://math.caltech.edu/SimonPapers/65.pdf .
The previously captured source PDF was hash-checked and its complete relevant
pages rendered for inspection on 2026-09-06. The digest remains
`108b70f69d707c77c46bb4d4870c9df43be635394d3013be043f8f1a566178e1`.
The inspected local copy is an external source, not a Q3LOCK paper PDF.

The visual check confirms the arbitrary-prior hypothesis, the forward
divergence convention, and the exponential coefficient (2J)^(-1). The
source's square-completion formula explicitly uses J^(-1) h. Theorems
2.2--2.3 are comparisons, not extra load-bearing imports here: the manuscript
derives its moment and Fourier consequences from Theorem 2.1 with the exact
Q3LOCK source. Source identity is provenance, not signed applicability review.

## Reproduction and evidence limits

Run from any directory with the project environment:

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 E:/Dev/TECT/verification/scripts/q3lock_manuscript_infrared_audit.py
```

The independent finite lane uses all Fourier modes of an actual L=4 torus,
exact complex fourth roots, and explicit forward/backward differences. It
checks the adjoint Poisson field, edge energy, source and Duhamel factors and
real/imaginary decomposition. Separate rational Gaussian-kernel principal
minors test projected Gram positivity, while exact shell enumeration and
symbolic integration coefficients check the tail constants. These are finite
reproduction diagnostics, not a proof of FSS or any infinite-dimensional limit.

The integrated lane runs the previous DLR, loop and content checkers in memory
without invoking their writers. All three historical manuscript result files
are hash-checked and preserved. Current fingerprints are written only to
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-q3lock-manuscript-infrared-audit/result.json`.
The older canonical reflection/infrared content checker is replayed separately.
Structure-only labels locate arguments; they cannot validate their meaning.

## Adversarial review

| Objection | Disposition |
|---|---|
| Hilbert reflection positivity requires a Gaussian with identity covariance on the full infinite Hilbert space. | UPHELD as false: only finite-dimensional Fourier Gaussians and bounded-kernel dominated convergence are used. |
| A common arbitrary prior in FSS means no integrability hypothesis. | UPHELD as false: the full quadratic exponential-moment hypothesis is checked from the actual scaled quartic. |
| The vertex source norm can replace its minimum-energy edge preimage norm. | UPHELD as false: exact nonzero Fourier modes distinguish these norms. |
| The FSS theorem field is also the unscaled bond displacement. | UPHELD as false: square completion uses h_t/c; a coupling different from one rejects the wrong identity. |
| A time-mesh theorem in dimension 8N is already an infinite-loop theorem. | UPHELD as false: weighted weak convergence, truncation and source UI are separate displayed steps. |
| Splitting a complex Fourier mode adds a factor two. | UPHELD as false: the real and imaginary quadratic forms add to the original norm on both sides. |
| An integrable continuous singularity automatically gives convergence of the discrete sums. | UPHELD as incomplete: a separate uniform discrete shell bound is supplied. |
| Nonzero-mode domination alone gives a positive zero mode or a cusp. | UPHELD as false: the local collective/Falk--Bruch lower bound remains a separate load-bearing input. |
| Passing finite fixtures or inspecting a source PDF counts as a signed proof audit. | UPHELD as false: neither is an independent expert acceptance record. |

Sign/conventions: each spatial bond is counted once, G and B have explicit
domains, and the source field in square completion is divided by c. Units:
the mesh factor is sqrt(epsilon) in ordinary source coordinates; the energy
norm sums to beta, while the integrated covariance carries beta squared.
Convergence: the finite L loop passage precedes the spatial sum, with the
singular cutoff removed only after L to infinity. No numerical quadrature
is used. Hardcode masking: counts, Fourier eigenvalues, edge energies and
tail constants are recomputed; any literal expected formula is labelled as
an oracle and never supplied as a computed coefficient. Limit cases include
the excluded constant mode, empty shell sums and projection-induced singular
Gram matrices. External reviewers are invited to replay the command and
challenge the source map, quotient conventions and analytic limit passages.

## Next manuscript gate

Expand the collective translation/form-domain argument and the bounded
coordinate, finite spectral cutoff and Falk--Bruch passage, then review the
entire cusp/tangent composition and literature comparison. Signed mathematical
and literature reviews, final clean replay and PDF inspection remain open.
R-497 stays T0 and claim_bearing=false; no physical gate, submission or release
is changed at this content checkpoint.
