# Q3LOCK manuscript integration: finite time mesh to interacting loops

Date: 2026-09-06. Status: internal T0 content review; no external signature.
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782, through R-497.
PDF: deferred until content review and final organization are complete.

## Integrated proof content

Manuscript v0.1.2 transfers the fixed-volume arguments from the unchanged
research notes into Sections 3 and 6:

* `q3lock-p06-gaussian-weak-limit-quantitative-audit-260905.md`, Sections
  2--7: retained Fourier modes, omitted tail, arbitrary-time covariance and
  increments, Gaussian tightness and bounded-weight transfer;
* `q3lock-harmonic-residual-reconciliation-260905.md`, Sections 2--5:
  actual physical residual, retained quartic, Gaussian Jensen normalizer,
  compact Riemann convergence and source moments;
* `q3lock-finite-volume-pressure-content-260905.md`, Sections 2--7:
  absolute mesh prefactor, cyclic determinant, split independence, heat
  trace identification and source normalization;
* `q3lock-continuous-loop-fkg-content-260905.md`, Sections 4--7:
  weighted weak passage for F,G,FG, measurable upper-set extension,
  selected-state scope and coordinate clipping.

The manuscript now derives the covariance and increment bounds before
asserting tightness. It proves convergence of the interacting numerators and
normalizers before dividing, and includes a positive normalizer lower bound.
The time-constant integrated source on an interpolated polygon equals its
cyclic trapezoidal/vertex sum exactly. Source uniform integrability follows
from quartic absorption. Point-evaluation moments instead use Gaussian
density domination; integrated L4 control is not substituted for a supremum.

The finite-dimensional Feynman--Kac formula remains an identified external
analytic input, with continuous lower-bounded residual, positive reference
mass/rigidity, common semibounded form and integrable diagonal majorant
displayed in the manuscript. KP v1 Section 2.3, equations (2.28)--(2.32),
supplies the normalized correlation/density comparison. Its residual
normalizer is explicitly distinguished from the absolute trace. The source
was rechecked at https://arxiv.org/pdf/math-ph/0609045v1 on 2026-09-06.

## Dependency boundary

This is a time-mesh limit at fixed finite spatial volume. Its Gaussian
density constants grow with volume. The manuscript does not use them to
replace the periodic volume-uniform moment estimate or the projective DLR
compactness proof. The zero-source parity argument is explicitly limited to
parity-invariant periodic laws and their limits, not every zero-source DLR
state. The positive-source tangent states may have nonzero expectation.

The remaining internal expansions are the periodic moment recursion,
projective weighted DLR/source-zero construction, Hilbert reflection/FSS
source and loop passage, singular spatial Fourier sum, and collective
spectral/form cutoff argument. The full phase theorem remains conditional.
No R-497 tier, host claim, physical gate or research authority is changed.

## Reproduction and evidence limits

Run from any directory with the project environment:

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 E:/Dev/TECT/verification/scripts/q3lock_manuscript_loop_audit.py
```

This diagnostic recomputes scalar cyclic Gaussian covariances by exact
rational precision-matrix inversion, independently of the earlier trigonometric
Fourier implementation. It tests vertex and polygonal increments, the
Gaussian diagonal bound, interpolation and cyclic source integration. Its
integrated part runs the v0.1.1 content checks against the current draft
without overwriting the older result file. It requires the new proof labels
and records exact-byte hashes of the manuscript and cited source notes.
Finite matrix probes and presence checks do not prove an infinite limit or
certify that every sentence is mathematically correct.

The output is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-q3lock-manuscript-loop-audit/result.json`.
Older content-audit result bytes are preserved. Current-draft audit hashes
are replay fingerprints, not the final release freeze.

## Adversarial review

| Objection | Disposition |
|---|---|
| Convergence of grid covariances suffices for continuous-path weak convergence. | UPHELD as false: arbitrary-time interpolation and tightness estimates are supplied separately. |
| Pointwise Riemann convergence alone permits changing measures under the integral. | UPHELD as false: compact-uniform convergence, common tightness and a globally bounded weight control the three terms. |
| A normalizer can be divided out before proving a positive limit. | UPHELD as false: the Gaussian Jensen bound is given before division. |
| Integrated quartic control bounds a point evaluation. | UPHELD as false: the pointwise fourth moment comes from Gaussian density domination; a narrow continuous spike is a rejecting fixture. |
| The finite time-mesh estimate is uniform in spatial volume. | UPHELD as false: the constants retain exp(beta V times a constant); the DLR step needs a different bound. |
| The new rational calculations are merely calls to the old Fourier routine. | DISMISSED: the precision matrix and interpolation vectors are constructed independently; only the separately labelled integrated manuscript checks reuse the old checker. |
| Finite tests or manuscript labels amount to an external proof audit. | UPHELD as false: signatures and line-by-line mathematical review are still absent. |
| Both zero-source phases must have zero coordinate means by parity. | UPHELD as false: only parity-invariant laws have that consequence. The manuscript specifies the selected-law scope. |

Sign and factors: the precision is (m/epsilon) L_cycle+a epsilon I; the
zero mode is retained for the diagonal, and only zero-sum increments use
the pseudoinverse comparison. Units: beta and epsilon remain time lengths;
massless increment variance is bounded by circular time distance divided by m.
No floating-point quadrature or extrapolated convergence rate is used in
the new diagnostic. External reviewers should replay the rational tests and
challenge the analytic interpolation, normalizer and Feynman--Kac passages.

## Next manuscript gate

Expand the periodic moment and weighted DLR/source-zero arguments using the
already registered source notes, with every source-window constant and limit
order visible in the paper. Keep the final PDF deferred.
