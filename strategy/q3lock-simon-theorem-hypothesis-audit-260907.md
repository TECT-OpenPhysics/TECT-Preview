# Q3LOCK Simon theorem-hypothesis audit

**Date:** 2026-09-07 UTC  
**Exploration:** EXP-001642  
**Task:** T-054  
**Status:** T0, claim_bearing=false, internal source-applicability audit  
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782 / R-497  
**Paper PDF:** deferred until content review and final organization

## 1. Audit question and boundary

The manuscript cites Barry Simon's version-pinned arXiv paper for the finite-
volume Brownian-bridge formula. The audit asks whether the printed hypothesis
being used is Theorem 1.1's bounded-below condition, or the weaker growth
condition used by the source's unbounded-semigroup Theorem 1.2. This note checks
the distinction against the primary source and records the model map. It does
not sign the operator proof, the harmonic reweighting passage, the mesh limit,
or any phase conclusion.

## 2. Primary-source reading

The source is B. Simon, *A Feynman--Kac Formula for Unbounded Semigroups*,
arXiv:math-ph/9907022v1, Theorem 1.1 and equations (1.1)--(1.3), printed
page 2. Theorem 1.1 states the Brownian-bridge formula for a continuous
potential on finite-dimensional Euclidean space that is bounded from below,
with kinetic operator `H_0=-Delta/2`. The source subsequently introduces the
condition

    V(x) >= -epsilon |x|^2 - C_epsilon  for every epsilon>0

as equation (1.4) and uses that condition in Theorem 1.2, the unbounded-
semigroup extension. The manuscript explicitly does not invoke Theorem 1.2.
Therefore (1.4) must not be presented as the hypothesis of the finite-volume
Theorem 1.1 application.

## 3. Model map

At fixed even periodic volume and fixed source, the unitary change
`z=sqrt(m) q` gives kinetic operator `-Delta_z/2` and potential
`U_{L,h}(z/sqrt(m))`. The retained quartic term and the finite-volume lower
envelope in `manuscript.tex` (Lemma `lem:finite-form-truncation`) give a global
lower bound for this continuous polynomial. Thus the displayed Theorem 1.1
hypothesis is met at the finite-volume level, conditional on the line-by-line
algebra and form identification.

The harmonic-reference identity uses the residual `R_{a,h}` and the upper
truncations `R_M=min(R_{a,h},M)`. The bounded-potential bridge identities,
monotone form/semigroup passage, endpoint kernel continuity, and absolute trace
normalization are manuscript arguments. They are not imported from Simon's
Theorem 1.2 and remain open for signed analytic review.

## 4. Disposition

This audit resolves a wording ambiguity rather than advancing a theorem tier:

* keep the manuscript citation to Theorem 1.1 and its bounded-below hypothesis;
* state explicitly that source condition (1.4) and Theorem 1.2 are not used;
* keep the harmonic reweighting and residual-truncation arguments visible as
  internal steps requiring independent review;
* preserve the T0, `claim_bearing=false`, R-497 and PDF-deferred boundaries.

The exact Simon source bytes still belong to the final source-freeze packet, and
an external mathematician must still inspect the common-core, form,
semigroup, kernel and trace passages.

## 5. Reproduction and adversarial checks

The content replay must record the synchronized manuscript and package after
this wording repair. The finite and independent replay wrappers must preserve
all earlier result bytes and reject any source/result mutation. A finite script
PASS is provenance evidence only; it is not acceptance of Simon's theorem or
of the Q3LOCK operator passage.

## 6. Non-claims

No claim tier, result lineage, source freeze, A1--A23 disposition, literature
novelty decision, DLR phase theorem, cusp theorem, TECT-sector status,
real-time/KMS statement, ground-state gap, continuum limit, physical-vacuum
interpretation, cosmology, Yang--Mills result, submission, or paper PDF follows
from this audit.
