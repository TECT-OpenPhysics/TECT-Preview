# Q3LOCK literature source freeze (content-audit stage)

**Status:** T0 source-hash and bibliography freeze; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**PDF:** deliberately deferred until content freeze, independent proof audit,
clean replay, and release review

## 1. Purpose and boundary

This note records the exact external source bytes inspected for the Q3LOCK
proof-text audit.  It fixes a reproducible URL, version (where the source
provides one), byte count, SHA-256 digest, bibliography entry, and the theorem
locations that the eventual manuscript may cite.  The downloaded PDFs were
placed only in a temporary audit directory; they are not the Q3LOCK manuscript
or a publication artifact.

The note is a source-identification result, not a mathematical proof.  It does
not close P-04, P-06, P-09, P-12, the operator/form-domain gate, the pressure
or source-tangent composition, or the DLR multiplicity conclusion.  The three
upstream records remain the only research authority chain; this note only
freezes the external references used to audit that chain.

## 2. Reproduction command and capture date

The following PowerShell procedure was run from the repository root on
2026-09-04 UTC (2026-09-05 KST), using a temporary directory outside the
repository.  `Invoke-WebRequest` was run with the explicit versioned URLs below,
and `Get-FileHash -Algorithm SHA256` was applied to each completed file.

```powershell
$tmp = Join-Path $env:TEMP 'tect-q3lock-source-check-260905'
New-Item -ItemType Directory -Path $tmp -Force | Out-Null
Invoke-WebRequest 'https://arxiv.org/pdf/math-ph/0609045v1' `
  -OutFile (Join-Path $tmp 'kp-math-ph-0609045v1.pdf')
Invoke-WebRequest 'https://math.caltech.edu/SimonPapers/65.pdf' `
  -OutFile (Join-Path $tmp 'fss-cmp-50-79-95.pdf')
Invoke-WebRequest 'https://arxiv.org/pdf/0710.2303v1' `
  -OutFile (Join-Path $tmp 'kkk-arxiv-0710.2303v1.pdf')
Get-ChildItem $tmp -File | Get-FileHash -Algorithm SHA256
```

The captured files and digests are:

| key | retrieval URL | source bytes | SHA-256 |
|---|---|---:|---|
| KP-v1 | `https://arxiv.org/pdf/math-ph/0609045v1` | 697493 | `607c534774f04481b0af8ddbb891e4caac2c0ca0fd28116c081fabe7c78bc532` |
| FSS-Caltech | `https://math.caltech.edu/SimonPapers/65.pdf` | 1404869 | `108b70f69d707c77c46bb4d4870c9df43be635394d3013be043f8f1a566178e1` |
| KKK-v1 | `https://arxiv.org/pdf/0710.2303v1` | 712731 | `90f0f42b017c71d194159cdfe59f180aed06f8c928847816e7bfced57b490e1d` |

The KKK digest above is written without whitespace in the machine manifest as
`90f0f42b017c71d194159cdfe59f180aed06f8c928847816e7bfced57b490e1d`.

## 3. Frozen bibliography and allowed citation scope

### 3.1 Kozitsky--Pasurek (KP)

Y. Kozitsky and T. Pasurek, *Euclidean Gibbs Measures of Interacting Quantum
Anharmonic Oscillators*, arXiv:math-ph/0609045v1 (16 September 2006); journal
version, *Journal of Statistical Physics* **127** (2007), 985--1047,
DOI `10.1007/s10955-006-9274-9`.

The audited source locations are Assumption (A) and equations (2.5)--(2.6),
the finite-volume operator statement (2.8), the periodic Ornstein--Uhlenbeck /
Feynman--Kac construction (2.16), Lemma 2.11, and Theorems 3.1--3.3.  They
may be used only after the Q3LOCK continuous eight-component potential, positive
harmonic split, interaction norm, and declared finite-volume boundary have been
matched line by line.  KP Propositions 7.1--7.4 are a separate scalar,
order/convexity route; they are not an allowed replacement for the Q3LOCK
nonradial R^8 FKG argument.

### 3.2 Fröhlich--Simon--Spencer (FSS)

J. Fröhlich, B. Simon and T. Spencer, *Infrared Bounds, Phase Transitions and
Continuous Symmetry Breaking*, *Communications in Mathematical Physics* **50**
(1) (1976), 79--95, DOI `10.1007/BF01608557`.

The audited Caltech PDF has 18 PDF pages, with the body ending on printed page
95.  Its first-page masthead displays `79--85`, which conflicts with the
printed page sequence and the DOI landing-page bibliographic record.  The
release bibliography therefore uses **79--95**, and the masthead discrepancy
is retained here as a source-audit note rather than silently discarded.

The allowed Q3LOCK citation is Section 2 and Theorems 2.1--2.3: periodic cubic
nearest-neighbour geometry, finite vector spins, an arbitrary one-site prior
with all quadratic exponential moments, and Gaussian-domination/gradient/
Laplacian bounds whose constants are independent of component count and
internal symmetry.  The finite-grid source scaling and zero-sum Poisson shift
remain Q3LOCK-local obligations.

### 3.3 Kargol--Kondratiev--Kozitsky (KKK)

A. Kargol, Y. Kondratiev and Y. Kozitsky, *Phase Transitions and Quantum
Stabilization in Quantum Anharmonic Crystals*, arXiv:0710.2303v1 (11 October
2007; PDF title page dated 15 January 2019), DOI
`10.1142/S0129055X08003353`.

The audited locations used by the Q3LOCK crosswalk are the periodic loop and
weighted path-space definitions (2.16)--(2.28), the finite-volume
Feynman--Kac formulas (2.33)--(2.37), the Feller statement in Proposition 2.4,
the weighted tempered topology (2.45)--(2.48) and (2.87), Propositions 2.12
and 2.21 for compactness/DLR accumulation, Proposition 3.9 and equation
(3.23) for the Griffiths pressure-slope step, and Proposition 3.18 for the
Bruch--Falk inequality.  Every one of these imports remains conditional on the
Q3LOCK form-domain, source-integrability, and limit-order checks.

## 4. Source-scope firewall

| source statement | permitted use | explicitly forbidden shortcut |
|---|---|---|
| KP Assumption (A), (2.8), (2.16), Theorems 3.1--3.3 | finite-volume loop representation, general-vector tempered DLR inputs after the Q3LOCK hypothesis map | treating KP as a proof of the Q3LOCK cusp or multiplicity |
| KP Propositions 7.1--7.4 | none in the nonradial Q3LOCK proof unless a separate scalar reduction is proved | importing scalar FKG/GKS/Lebowitz conclusions into R^8 |
| FSS Section 2, Theorems 2.1--2.3 | finite time-grid vector Gaussian-domination ingredient at fixed spatial volume | claiming that FSS alone supplies the continuous-loop limit, pressure limit, or DLR states |
| KKK path/FK/topology propositions | topology and pressure/commutator crosswalks after local hypotheses are checked | identifying finite-grid sup-norm convergence with global tempered DLR convergence |

## 5. Remaining release gates

The source bytes and bibliography are now reproducibly identified, but the
following are still open before any theorem or paper promotion:

1. an independent line-by-line audit of the P-06 finite-grid-to-continuous-loop
   FKG passage;
2. an independent audit of the P-09 FSS-to-loop Duhamel passage, including the
   source scaling and factor-two Fourier normalization;
3. an operator/form-domain and unbounded-commutator audit for the collective
   double commutator, Falk--Bruch, and Griffiths composition;
4. a bounded claim/result-lineage decision and content freeze with all source
   hashes included;
5. clean primary/independent/integrated replay and release review; and
6. external mathematical referee review.

Only after those gates pass may the final LaTeX source be frozen and the PDF be
compiled, rendered, visually inspected page by page, and hash-captured.  No PDF
is created by this source freeze.

## 6. Adversarial checks

1. **The FSS first-page range can be copied as 79--85 without checking the
   article.**  Rejected: the body reaches printed page 95 and the DOI landing
   record gives 79--95; the discrepancy is recorded explicitly.
2. **An arXiv URL without a version is a sufficient release pin.**  Rejected:
   the KP and KKK URLs include `v1`, while the FSS byte URL and digest are
   recorded separately.
3. **A source digest proves the imported theorem applies.**  Rejected: digest
   identity is provenance only; every Q3LOCK hypothesis and common-core map
   still requires independent review.
4. **The source PDFs can be treated as a Q3LOCK proof artifact.**  Rejected:
   they are external references in a temporary audit directory, not a claim
   card, manuscript, or phase proof.
5. **Creating the source freeze authorizes PDF generation.**  Rejected: PDF
   generation remains explicitly deferred by the user instruction and by the
   R-497 release gate.
