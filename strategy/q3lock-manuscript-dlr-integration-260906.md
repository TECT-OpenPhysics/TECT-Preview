# Q3LOCK manuscript integration: periodic moments and source-tangent DLR limits

Date: 2026-09-06. Status: internal T0 content review; no external signature.
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782, through R-497.
PDF: deferred until content review and final organization are complete.

## Integrated proof content

Manuscript Section 5 now expands the registered source argument in
`strategy/q3lock-dlr-source-tangent-content-260905.md`, Sections 2--6.
The other unchanged inputs are
`strategy/q3lock-source-zero-dlr-kernel-determining-class-audit-260905.md`
and `strategy/q3lock-kp-vector-hypothesis-crosswalk-independent-audit-260905.md`.
The first supplies finite-range kernel/source continuity and the determining
class; the second locates the general-vector KP hypotheses. These are paper
content inputs within R-497, not a replacement research authority chain.

The transferred argument includes the allocated onsite potential with its
single negative pair interaction, explicit source-window quartic envelopes,
the one-site numerator and positive denominator estimates, finiteness of the
periodic exponential moment before the Holder recursion, and the resulting
volume-independent bound. It specifies a complete separable tempered metric,
diagonal compact sets, and the stronger-weight tail used for each target
weighted L2 norm. Periodic zero extension is not spatially invariant; only
the eventual local-cylinder identities establish invariance of its limits.

For each finite region, the manuscript additionally spells out constants
previously left implicit in the compact-boundary continuity argument. With
A=g/128 and J0=6c, the internal and boundary degree allocation gives

    I_Delta^h >= (A/2) Q_Delta - C_Delta,K,
    C_Delta,K = beta |Delta| (C0 + J0^2/(8A)) + B_K.

Here Q_Delta is the spacetime integral of |omega_y|^4 and B_K is half the
compact-boundary supremum of the weighted squared neighbor L2 norms. From
Gaussian Fernique, R_F^2=log(2 F_sigma)/ell_sigma yields reference probability
at least one half for each sup-norm ball. The product event then proves
Z_Delta(h,xi)>=2^(-|Delta|) exp(-U_Delta,K)>0 before division. The displayed
U includes the upper onsite envelope, internal pairs, and compact-boundary
Cauchy--Schwarz terms. This is a lower bound, not an exact partition formula.

Holder bounds the absolute source by (beta |Delta|)^(3/4) Q_Delta^(1/4).
Maximizing Q^(1/4) exp(-A Q/2) yields (2 A e)^(-1/4). Thus the normalized
kernel is source-Lipschitz on every compact boundary set with constant
2 M_Delta,K/z_Delta,K. The quotient bound uses |N|<=||f|| Z for its own
normalizer; it does not assume a source-independent denominator. The direct
finite-range Feller proof applies to all bounded continuous functions on the
specified Polish space, which determine the full Borel DLR equation.

Finally, the manuscript separately passes (i) fixed-source periodic limits
and their clipped local expectations, then (ii) positive differentiability
sources to zero, using compact-set kernel control and a second clipping
limit. The normalization remains P=p/(8 beta), p'_L=E X_L/V=beta E Q0,
and mu_h(Q0)=8 P'(h). Parity creates the opposite expectation, but distinctness
still needs the later strict-cusp argument.

## Primary-source check

KP v1 was rechecked at https://arxiv.org/pdf/math-ph/0609045v1 on 2026-09-06:
Assumption (A), (2.5)--(2.6), the exponential-weight alternative in Assumption
(B), Proposition 2.2/(2.27), Theorems 3.1--3.2, and Lemma 4.1. The citation
applies to general vector potentials, not an imported scalar or radial phase
theorem. Its fixed-model moment statement is not silently made uniform in a
source window or applied to finite periodic laws; the manuscript proves the
needed window bound. The all-state fixed-source compactness import remains
subject to signed applicability review. The selected-family construction
does not claim to exhaust all states or prove uniqueness.

## Reproduction and evidence limits

Run from any directory with the project environment:

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 E:/Dev/TECT/verification/scripts/q3lock_manuscript_dlr_audit.py
```

The new diagnostic independently recomputes exact Young/envelope identities,
nearest-neighbor allocation for finite regions, source factors, the Holder
exponent, compact-boundary quotient decomposition, and the Gaussian event
and source-polynomial maxima. Hostile finite fixtures reject reversed
weighted embeddings and convergence of expectations from weak convergence
alone. A separately labelled integrated lane calls the previous loop checker
in memory, which itself calls the earlier content checker in memory. Both
historical result files are hash-checked and preserved. The new output is
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-q3lock-manuscript-dlr-audit/result.json`.
The current source hashes are replay fingerprints, not a final release freeze.

These finite checks and symbolic identities are not a proof of compactness,
an infinite-dimensional DLR equation, or full theorem correctness. Text-label
checks only locate the manuscript arguments. They are not independent signed
mathematical review. The older canonical DLR content diagnostic is also
replayed separately without altering its source.

## Adversarial review

| Objection | Disposition |
|---|---|
| Allocating r+6c-a onsite allows another positive spatial diagonal in the specification. | UPHELD as false: only the negative pair terms remain; finite-region degree allocation tests both internal and exterior edges. |
| M<=exp(C1) sqrt(M) bounds M even when M is infinite. | UPHELD as false: quartic absorption and Gaussian Fernique prove finite M first. |
| A faster-decaying weight controls the slower-decaying target. | UPHELD as false: alpha_(k+1)<alpha_k is the stronger premise; the escaping constant-loop fixture rejects reversal. |
| Normalizers are merely positive pointwise, so source differences of normalized kernels pass uniformly. | UPHELD as incomplete: the compact-boundary product-ball lower bound is proved before the quotient estimate. |
| An extra beta is needed in the final tangent identity. | UPHELD as false: the source already integrates time, and division by 8 beta leaves E Q0/8. |
| Weak convergence alone preserves the unbounded local expectation. | UPHELD as false: both limit passages use a common second moment and clipping; an escaping-mass fixture fails without it. |
| The selected source-zero limit is automatically different from its parity image. | UPHELD as false: distinctness needs a strictly positive collective expectation from the later cusp. |
| The new exact tests certify every analytic passage. | UPHELD as false: analytic arguments and imported hypotheses still require signed external review. |

Sign/factors: J0 is a row sum; the internal ordered sum carries one half,
whereas an exterior edge occurs once. The Young allocations are checked
against the actual envelope, not inserted as derived inputs. Units/conventions:
beta multiplies integrated local quantities once; the finite pressure is
divided by 8 beta. Convergence: source constants are uniform only on a fixed
window at fixed beta, with fixed-source spatial limits preceding h down to
zero. Limit cases: no beta-infinity or continuum assertion, no conclusion of
distinctness when the right derivative vanishes. The verifier labels input
fixtures and reproduction oracles separately and contains no pasted output
used as an upstream mathematical parameter. External reviewers should
challenge the Polish topology, kernel domination and the two clipping limits.

## Next manuscript gate

Expand the Hilbert reflection/FSS source and loop passages, singular spatial
Fourier sum, and collective spectral/form cutoff argument from the registered
inputs. Signed mathematical and literature reviews, final clean replay and
PDF inspection remain open. No tier, physical gate, host claim, submission or
release is changed by this content checkpoint.
