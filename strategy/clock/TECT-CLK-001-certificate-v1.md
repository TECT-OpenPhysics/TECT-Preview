# TECT-CLK-001: clock-observable admission boundary

Version 1.0, 2026-09-14. One bounded audit, not a new physical model.
Authority: the operator-approved TECT-CLK-001 goal and the immutable
[preregistration](TECT-CLK-001-prereg-v1.json). The
[evidence manifest](TECT-CLK-001-evidence-v1.json) fixes numerical inputs,
units, primary-page locators, data roles, source hashes and missing covariance.
The reproducible [assessment](TECT-CLK-001-assessment-v1.json) pins this
certificate and its verifiers. Standard finite algebra below is a diagnostic,
not a newly claimed TECT theorem or an R-result promotion.

## 1. Question and scope

Can the already-declared scalar Brazovskii response be evaluated against a
common clock-rate discriminator without adding a physical time or readout?
Keep the A2 scalar real-field gradient flow, on its fixed periodic three-torus,

\[
 F(\phi)=\int\left(\tfrac12\phi K\phi+
                 \tfrac\lambda4\phi^4+\tfrac\gamma6\phi^6\right),\quad
 \partial_t\phi=-K\phi-\lambda\phi^3-\gamma\phi^5,\quad
 K(k)=\mu^2+Y(|k|^2-q_0^2)^2.
\]

Here the exact A2 source supplies its normalization, domain and assumptions,
including positive Y, mu-squared and gamma, and 3/2 < s <= 2. No lattice,
volume or cutoff limit is performed. No source, parameter, carrier, projection,
state or time is added. The A2 note, sections 2, 3 and 6, is hash-pinned in the
preregistration. PAH-v1/v2 and the R-574 counterexample remain unchanged.
This scalar reference is not the production Class-II owner.

## 2. Exact diagnostic, independent of physical interpretation

Let I and A be nonempty finite sets of clock types and comparison conditions.
An entry w(i,a)>0 means a transition frequency in **one declared common readout
convention**, not an envelope decay rate. Correct independently characterized
instrumental effects; never remove the tested redshift and then claim its
reproduction. Set

\[
 R_i(a,b)=\frac{w(i,a)}{w(i,b)},\qquad
 D_{ij}(a,b)=\frac{w(i,a)w(j,b)}{w(i,b)w(j,a)}.
\]

For a complete positive table, all D equal one if and only if there are
positive k(i), N(a) with w(i,a)=k(i)N(a). Necessity follows by cancellation.
For sufficiency choose i0,a0, put k(i)=w(i,a0) and
N(a)=w(i0,a)/w(i0,a0), and use the (i,i0;a,a0) cross-product identity.
This is an exact finite rank-one criterion; no limit or fitted parameters
enter. If another positive factorization exists, its ratios at a0 imply
k'(i)=c k(i) for one c>0, then N'(a)=N(a)/c for every a. This proves only
normalization uniqueness, **not** physical uniqueness.

For incomplete tables consider the bipartite graph of observed entries.
In each connected component choose a root factor freely and propagate factors
along a spanning tree, dividing a positive observed entry by its known endpoint
factor. For a non-tree edge the two induced factors fit that edge exactly when
the alternating product around its fundamental cycle is one. These conditions
are necessary by telescoping, and sufficient since they test every remaining
edge. Every component retains one independent positive normalization; isolated
vertices are unconstrained. In particular, a forest fits arbitrary positive
observations, and a single clock supplies no cross-species universality test.
A missing corner of a square has both a factorizing completion bc/a and a
nonfactorizing positive completion 2bc/a with the same three observed entries.

For an ordered four-vector (w_ia,w_ib,w_ja,w_jb), the differential of log D is
(1/w_ia,-1/w_ib,-1/w_ja,1/w_jb). Its first-order propagated variance is
v^T Sigma v. This is a small-error linear approximation, not an exact
distributional identity. Off-diagonal covariance terms cannot be dropped
without evidence. A perfectly shared fractional error cancels in log D;
diagonal-only propagation would miss that cancellation. For deterministic
positive intervals [l_x,u_x] an exact enclosure is

\[
 \frac{l_{ia}l_{jb}}{u_{ib}u_{ja}}\le D\le
 \frac{u_{ia}u_{jb}}{l_{ib}l_{ja}}.
\]

Endpoints follow from monotonicity. Reported marginal standard errors do not
automatically form such a simultaneous-confidence box. A statistically
resolved non-unit double ratio can reject this *exact common-factor model*
under the stated readout and error assumptions, not gravity in general.

Even an exact complete rank-one table does not identify a metric lapse:
the map (k,N) -> w is unchanged if the same numerical N is assigned the
interpretation "universal environmental multiplier". This is observational
non-identifiability of that unrestricted alternative, not a constructed
consistent alternative gravity theory. Non-unit ratios can discriminate
against common factorization; unit ratios cannot identify its mechanism.

## 3. Primary observations and candidate crosswalk

The two primary publications are
[Bothwell et al. (2022)](https://doi.org/10.1038/s41586-021-04349-7) and
[Chou et al. (2010)](https://doi.org/10.1126/science.1192720).
The first is retrospective discovery; the independently performed second
experiment is retrospective validation, not a blind or prospective holdout.
No parameters were fit and no joint likelihood is constructed. Raw series and
their full covariance are unavailable in this extraction. The corrected
gradient, its published quadrature convention and the inserted weak-field
reference formula are reproduced by the scripts; this is not a new TECT
prediction. The manifest preserves the exact precision/error distinction and
the second paper's missing mechanical-height error.

| Source or object | Actual observable | Admitted use / missing correspondence |
|---|---|---|
| Bothwell primary aggregate | One Sr clock transition sampled vertically | Frequency-gradient/sign/unit input; not multiple clock species |
| Chou primary aggregate | Two Al clock transitions at changed elevation | Independent experimental context; auxiliary Be/Mg ions are not additional clock species |
| Combined publications | Different apparatus and comparison conditions | Not a measured complete multi-species frequency table; no observed D is manufactured |
| A2 linear response at zero background | delta phi_k(t)=exp(-K(k)t) delta phi_k(0) | K(k)>=mu-squared>0 is an amplitude relaxation rate in source time |
| Needed clock bridge | Atomic transition phase/readout under changed conditions | No such source-owned readout or physical-time map is declared in the frozen A2 contract |

The A2 response is obtained by linearizing its stated polynomial flow at zero;
no imaginary frequency or proper time follows from the negative real exponent.
Sharing inverse-time dimensions does not identify a decay rate with an atomic
transition frequency. Contrast lifetime, carrier phase and transition energy
are different observables. This absence is **NOT_ADMITTED_DEFINITION_MISSING**
for this candidate-to-clock test, not a no-go for every Brazovskii completion,
emergent-clock model, or TECT theory. It is not repaired by inserting an
oscillator, quantum state, detector coupling, lapse or species-specific fit.

## 4. Verification and hostile review

The primary implementation uses rational arithmetic for fixture identities,
source corrections and unit conversion. The independent implementation does
not import it: it differentiates and factors symbolically and reconstructs
source arithmetic using decimal arithmetic. Optional primary-PDF replay checks
exact bytes, page count and text markers; the located numerical tables and
equations were also visually inspected. Text extraction is not a substitute
for that visual source check. All verification authorship is the same task;
no external-person review is claimed.

Five Lean declarations check cross-product cancellation, basepoint-entry
reconstruction, the unit-ratio equivalence, normalization freedom and equality
of the same observable value under a renamed multiplier. The last is only an
algebraic identity, not a formal physical-identifiability theorem. The graph,
empirical provenance, uncertainty model and physical mapping are written
arguments, not fully formalized. Existing PAH code supplies only a hash-pinned
compiler harness; no PAH result is mathematical input.

Concrete hostile objections and dispositions:

- "A single-clock redshift proves universal clocks." **UPHELD** against that
  promotion: the missing observed cycle is explicit and no D is reported.
- "Dimension 1/time makes the A2 decay an atomic frequency." **UPHELD**:
  source readout and time identification are absent; the candidate is not admitted.
- "A common factor proves a metric." **UPHELD**: observational equivalence
  leaves the unrestricted mechanism unidentified, without asserting that every
  alternative is physically realizable.
- "Use the best precision as the gradient uncertainty, or assume zero
  covariance." **DISMISSED for this package** by separately typed inputs,
  original quadrature reconstruction and the covariance cancellation test.
- "The independent paper was a blind prediction." **DISMISSED for this
  package**: retrospective roles and prior exposure are recorded; no fit,
  prospective success or pooled significance is claimed.
- "Finite fixtures prove the quantified criterion." **DISMISSED for this
  package**: the constructive proof supplies the quantifiers; fixtures and
  partial Lean have explicitly narrower roles.
- "An absent readout disproves TECT." **UPHELD** against any such inference:
  the assessment is a source-definition boundary, not a global contradiction.

## 5. Single missing packet and stop condition

The sole next input is a **source-authorized clock-readout/time-map packet**
for a specifically identified candidate. As one coherent packet it must name
the unchanged response, operational transition/phase observable, its map to
the common readout/time convention, how comparison conditions act, and a
falsifiable frequency-ratio prediction without species-specific posterior
tuning. Merely proposing that packet is not verifying it. A model modification
would need separate explicit authorization and immutable versioning.

Re-entry requires that new hash-pinned packet, or a precise source/algebra/
extraction error in this audit. No unchanged owner search, finite table sweep,
automatic weaker PAH successor, or new clock model follows from this record.
The evidence-map admission audit is AUXILIARY_SUPPORT; the active T-054 gate
does not change. No new R-result, claim-card tier or physical conclusion is
issued. Pre-A, spacetime, QFT, gravity, horizons, continuum, causal cones,
Yang-Mills, mass gap and TOE are not established.

## 6. Reproduction and durable source retrieval

From the repository root, after installing the repository's pinned runtime:

```text
python -X utf8 verification/scripts/tect_clk001_verify.py --check --lean-cache E:/Dev/TECT/verification/lean/.lake/packages --elan-home C:/Users/NaEun/.elan
```

The Lean paths are host options, not scientific inputs. On another prepared
host use its pinned package cache and elan directory (or defaults).
To reproduce the optional PDF hash/page/text stage, first retrieve each exact
`sources.*.url` from the evidence JSON to its declared ignored `cache` path,
without rewriting an existing differing file, then append `--source-cache`.
The hash must match; changed publisher bytes require a new provenance review,
not replacement of the expected hash. No full copyrighted PDF is redistributed.
All durable input hashes and extracted factual inputs are tracked. This
definition-boundary checkpoint uses one strategy synthesis, not a new proof
note/PDF for standard algebra or a gate that remains open.
