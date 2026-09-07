# Q3LOCK manuscript: source-to-phase composition audit

Date: 2026-09-06. Status: internal content audit, not signed acceptance.
Authority: EXP-000780 -> EXP-000781 -> EXP-000782, through R-497.
PDF: deferred until content review and final organization are complete.

## Question and reviewed authorities

Do the existing pressure, DLR, FKG, infrared and collective blocks apply to
the same model and supply exactly the inputs used in the strict-cusp and
state-distinctness conclusion, without reversing source or volume limits?

The local authority for the final implication is
`strategy/q3lock-strict-cusp-tangent-content-260905.md`, Sections 1--7.
The current manuscript interfaces reviewed are the exact Hamiltonian and
source; finite source moments and derivatives; all of Section 4's pressure
argument; Section 5's topology, specification map, compactness and source
tangents; the Duhamel/Fourier/singular-sum interface; the previously integrated
collective conclusion; and the entire final cusp/state composition.
This is an interface audit, not a new independent line-by-line acceptance of
every upstream proof. The frozen research notes are not rewritten.

Primary comparators checked online:

* Kargol--Kondratiev--Kozitsky, arXiv:0710.2303v1, Proposition 3.9,
  equations (3.21)--(3.24), printed pages 26--27:
  https://arxiv.org/pdf/0710.2303v1 . Its endpoint specialization is
  proved directly in the manuscript; no model-specific phase theorem is used.
* Kozitsky--Pasurek, arXiv:math-ph/0609045v1, equations (2.47)--(2.49)
  and Theorem 3.1: https://arxiv.org/pdf/math-ph/0609045v1 . The source
  topology includes local continuous-loop norms as well as weighted L2
  norms. The manuscript's cofinal metric induces that same topology.

These online source checks are not signed theorem-applicability reviews.
No source-PDF visual inspection or Q3LOCK PDF generation is claimed here.

## Interface findings and manuscript changes

| Interface | Exact match and necessary qualification |
|---|---|
| Physical model | Same positive-lambda Q3 polynomial, spatial difference bonds, unit collective vector, fixed lattice and m=chi/hbar^2 throughout. |
| Harmonic allocation | The finite physical residual keeps spatial differences; the DLR potential contains the allocated 6c diagonal and only the negative pair term. These are two representations, not two diagonals. |
| Pressure | p=log Z/V, P=p/(8 beta); X already integrates time. The MGF ratio uses exp(hX), and p'=beta E Q, P'=E Q/8. |
| Pressure derivatives | At fixed differentiability source h, finite-volume derivatives are squeezed between two secants. Volume is taken before the secant width tends to zero. No derivative convergence is used at the cusp. |
| All-state compactness | KP's general-vector fixed-source theorem and its actual projective topology are mapped explicitly. This does not identify all DLR states with selected periodic limits. |
| Selected source family | Direct periodic source-window moments, compactness, kernel continuity and two clipping passages supply the tangent states. No uniformization of a fixed-model KP bound is assumed. |
| Zero-source covariance | D is the covariance of time-averaged collective coordinates: Var X(f)=beta^2 <f,Df>. Local Duhamel and Fourier expressions are the same object. |
| Collective versus infrared | FKG supplies the local lower bound through the ordered operator cutoffs; nonzero Fourier upper bounds must all be subtracted before a zero-mode density is obtained. |
| Strict sign | I3 is positive finite, A0=8cm theta^2, and 2 beta c delta=A0 tanh(x_beta)^2-I3. The sufficient set is nonempty but is not the exact critical region. |
| Endpoint step | Finite MGFs on a common interval and a finite even limiting pressure give the squared-tail estimate. The liminf lower bound and limsup upper bound are joined before taking square roots. |
| Phase selection | At each h_j>0 first select a periodic-volume DLR accumulation; only then take h_j down to zero and preserve the unbounded expectation by clipping. |
| Parity and distinctness | An explicit specification intertwining identity yields the second DLR state. A finite bounded cylinder clip separates the two laws. |

The old abstract and status remark still said that the already integrated DLR,
infrared and operator passages had not been expanded. That reader-facing
status drift is corrected. The replacement says that the arguments are
present but independently unaccepted; it does not upgrade T0.
The seam energy is now denoted B_L^seam to distinguish it from the collective
displacement Hessian B_L. The nonclaim about regulator removal is narrowed
to spatial lattice-spacing removal: the time-mesh limit is actually part of
the proof, whereas a spatial continuum limit is not. These are notation and
scope clarifications, not new results or changes to the frozen inputs.

## The two branches and limit order

The two branches share the exact finite loop law, not a common limiting law.
In the zero-source branch, take time mesh N to infinity at fixed L,beta;
remove spectral M at fixed coordinate cutoff R and L, then R at fixed L;
combine the local lower bound with the finite nonzero-mode bound, and take
even L to infinity with the singular cutoff removed afterwards. For the
Griffiths argument the small Chernoff source is fixed during the volume limit;
the endpoint error is sent to zero last.

In the state branch, take the loop limit first, then spatial accumulation at
each fixed positive differentiability source h_j, then source-to-zero
accumulation. The moment clips are removed after each corresponding weak
limit. The numerical strict regime is selected at fixed beta before these
constructions; it is not a zero-temperature limit or a final extra limit.
Neither an arbitrary simultaneous h=h(L) nor a zero-source periodic
accumulation is substituted for the positively selected phase.

## Bounded witness and final implication

Let a_beta=sqrt(delta_beta)>0. The constructed states satisfy
mu_plus(Q)>=a_beta and mu_minus(Q)=-mu_plus(Q). Their common second-moment
bound is C2=C_per/ell_sigma. For f_R=clip_R(Q),

    mu_plus(f_R)-mu_minus(f_R) >= 2 a_beta-2 C2/R > a_beta
    whenever R>2 C2/a_beta.

Thus a bounded continuous cylinder observable distinguishes the laws. This
is a direct consequence within the existing state-distinctness claim, not a
new assertion of extremality, uniqueness, purity or clustering.

The manuscript now includes a proof after its conditional package theorem,
linking the finite pressure and compactness claims and each cusp/state step
to their upstream equations. The hypotheses remain upstream analytic inputs;
neither a cusp nor multiplicity is assumed. The internal conditional statement
is not the final accepted model theorem required by the full publication goal.

## Reproduction and code self-review

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 E:/Dev/TECT/verification/scripts/q3lock_manuscript_composition_audit.py
```

The new checker recomputes source and threshold algebra symbolically, evaluates
the squared-tail integral exactly, checks bounded-witness inequalities on
rational laws and uses a symmetric two-point toy law to expose noncommuting
source/volume limits. The toy law is not Q3LOCK and its slope is not a measured
Q3LOCK order parameter. No numerical value of I3 or approximate implicit root
is used to certify the phase condition.

All five older manuscript outputs are preserved. Their checkers are called
in memory and only the new composition result is written. The frozen R-497
manifest's full source list is hash-checked without changing expected hashes.
Structure checks locate the interfaces and reject stale status wording; they
do not evaluate analytic validity. Finite PASS is not external acceptance.
The EXP-001609 replay passes 59 current checks, integrating 150 collective,
612 infrared, 81 DLR, 203 loop and 32 prior content checks. All 91 frozen
source hashes match; all five historical manuscript outputs are preserved.

| Objection | Self-review disposition |
|---|---|
| X/V and the time-averaged mean are the same random variable. | DISMISSED: their squared moments differ by beta^2; the dictionary is now displayed at the join. |
| The liminf infrared bound can be combined with a weak limit without moment control. | DISMISSED: a direct squared-tail integral supplies the limsup second-moment bound. |
| Finite-volume parity forces the thermodynamic right derivative to vanish. | DISMISSED: fixed-source derivative limits are used only at differentiability points; the exact two-point toy law rejects the exchange at zero. |
| A finite h(L) selection always gives the endpoint tangent phase. | DISMISSED: the toy law at h proportional to 1/V gives a different slope; the actual proof uses iterated limits. |
| The KP weak topology might omit local continuous-loop control. | DISMISSED after source check: (2.48) includes local sup norms, and the cofinal metric is topologically equivalent. Signed applicability review remains open. |
| A pressure cusp alone proves a DLR state exists. | DISMISSED: selected-family tightness, finite-kernel passage and clipped expectation are independent required inputs. |
| Different unbounded expectations are being used without integrability. | DISMISSED: a common second moment is supplied, and a bounded cylinder witness is now explicit. |
| The threshold is an exact critical temperature or a zero-temperature limit. | DISMISSED: only a sufficient finite-parameter region is asserted; equality and its complement remain undecided. |
| A current theorem label or green script means the paper is externally accepted. | DISMISSED: T0, all independent signature fields and final release gates remain unchanged. |

Conventions/signs: the energy source, factor eight, beta squared covariance
and positive liminf/limsup chain are checked separately. Units: beta/m and
theta are inherited from the common Hamiltonian, not refitted. Convergence is
proved by the displayed estimates; the finite examples are hostile diagnostics,
not numerical evidence for a limiting theorem. Derived outputs are recomputed;
literal fixtures and reproduction oracles are labelled. Limit cases include
threshold equality, subthreshold parameters, finite-volume zero slope and
nonzero source scaling. External reviewers are invited to rerun the command
and challenge every interface and upstream analytic premise.

## Next gate

Complete the internal citation/theorem-hypothesis and literature comparison
audit, consolidate any remaining manuscript defects, and prepare an exact
reviewer handoff for signed mathematical and specialist novelty review.
Final clean-snapshot replay, scope admission and source/hash freeze remain
open. The shared PAH-OMC-018 hold, no-submission boundary and deferred PDF
are unchanged; the full goal is not complete.
