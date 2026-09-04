# Q3LOCK spatial edge-count and onsite-factor audit

**Status:** T0 normalization audit; P-04/P-09 remain open
**Date:** 2026-09-05
**Owner task:** T-054
**Authority:** EXP-000780 -> EXP-000781 -> EXP-000782
**Primary sources:** Q3LOCK fixed-lattice certificate (2026-08-04); Kargol--Kondratiev--Kozitsky, [arXiv:0710.2303](https://arxiv.org/pdf/0710.2303)
**PDF:** deferred until mathematical content and all independent audits are complete

## 1. Why this audit was opened

The Q3LOCK Hamiltonian uses the spatial difference term

```text
(c/2) sum_(y in Lambda) sum_(i=1,2,3)
      |q_(y+e_i)-q_y|^2,
```

with periodic wrapping in the finite-volume pressure and FSS arguments.  Several
recent KP crosswalk notes wrote the onsite term produced by this expansion as
`(3c/2)|q_y|^2`, while simultaneously using `J_yz=c` on the six nearest
neighbours and `Jhat_0=6c`.  The coefficient must be checked before any
load-bearing manuscript statement is frozen.  This note is a correction audit,
not a claim promotion or a phase theorem.

## 2. Declared edge conventions

Let `Lambda_L=(Z/LZ)^3` and `V=L^3`.  Define the positive-direction edge
multiset

```text
E_plus = {(y,y+e_i): y in Lambda_L, i=1,2,3}.
```

It has `3V` bond terms.  For `L>=3` these are the usual undirected nearest-
neighbour edges listed once.  For `L=2`, a coordinate neighbour reached by
`+e_i` is also reached by `-e_i`; the displayed Hamiltonian is then naturally
read as a periodic multigraph with the corresponding parallel bond terms.  The
incidence count below remains valid in either interpretation.  The final paper
must either impose `L>=3` or state this multiplicity convention explicitly.

Every site occurs three times as a tail and three times as a head in `E_plus`.
Thus the total endpoint incidence is `6V`, and the periodic degree counted with
multiplicity is six.  If `E` denotes the same bonds as an undirected edge list,
the Q3LOCK sum is the sum over `E` once (with multiplicity when `L=2`).

The KP pair convention is an ordered sum over both orientations.  Set
`J_yz=c` for each directed nearest-neighbour occurrence (or use the equivalent
aggregated coupling when two periodic occurrences have the same endpoint).
Then

```text
sum_z |J_yz| = 6c,
Jhat_0 = 6c,
-(1/2) sum_(y,z) J_yz (q_y,q_z) = -c sum_E (q_y,q_z).
```

The last identity is also true for the `L=2` multigraph when the pair sum keeps
the bond multiplicities rather than collapsing them without aggregation.

## 3. Exact expansion

For vector-valued site variables, expand each bond and use translation
invariance of the periodic box:

```text
sum_E |q_y-q_z|^2
 = sum_E |q_y|^2 + sum_E |q_z|^2
   - 2 sum_E (q_y,q_z)
 = 6 sum_y |q_y|^2 - 2 sum_E (q_y,q_z).
```

Therefore the Q3LOCK spatial term is exactly

```text
(c/2) sum_E |q_y-q_z|^2
 = 3c sum_y |q_y|^2 - c sum_E (q_y,q_z).
```

Equivalently, after the KP harmonic split, the local potential must contain
`+3c|q|^2` at each periodic site, or, when written with a one-half quadratic
coefficient,

```text
V_(h,a)(q) = ... + ((r + 6c - a)/2)|q|^2 - h*(u,q).
```

This agrees with the already registered Q3LOCK source-coercivity expression
`b=(r+6c-a)/2` in the pre-A fixed-lattice certificate.  The value `Jhat_0=6c`
is unchanged; it is the local onsite allocation, not the pair norm, that was
mis-normalized in the affected crosswalk notes.

## 4. Three decisive checks

### 4.1 Constant-field check

Set `q_y=q` at every site.  The original difference energy is zero.  The
correct decomposition gives

```text
3c V |q|^2 - c (3V) |q|^2 = 0.
```

The previously written coefficient would give

```text
(3c/2) V |q|^2 - c (3V) |q|^2 = -(3c/2)V|q|^2,
```

which is nonzero and has the wrong sign.  Hence `3c/2` cannot represent the
declared `(c/2)` difference Hamiltonian under the stated edge convention.

### 4.2 Product-trial check

The fixed-lattice certificate uses a centered independent product Gaussian with
coordinate variance `s^2`.  Each scalar spatial bond contributes
`(c/2) E[(X-Y)^2]=c s^2`.  There are `3V` bond terms and eight components, so
the spatial contribution per coarse site is `24c s^2`, exactly the coefficient
shown in its trial expression.  The incorrect `3c/2` local allocation would
produce only `12c s^2` when the centered pair term has zero expectation, in
conflict with that independent check.

### 4.3 General-degree check

For any undirected graph with degree `d_y` and edge coefficient `c/2`, the
identity is

```text
(c/2) sum_{ {y,z} } |q_y-q_z|^2
 = (c/2) sum_y d_y |q_y|^2
   - c sum_{ {y,z} } (q_y,q_z).
```

The periodic cubic value is `d_y=6`, hence `3c`.  An onsite coefficient
`3c/2` would correspond instead to edge coefficient `c/4` on the same graph,
or to an undeclared half-incidence convention that is not the Hamiltonian in
the fixed-lattice certificate.

## 5. Open boxes and boundary terms

For an open rectangular box `R`, the exact identity is

```text
(c/2) sum_{ {y,z} in E_R } |q_y-q_z|^2
 = (c/2) sum_y d_R(y)|q_y|^2
   - c sum_{ {y,z} in E_R } (q_y,q_z),
```

where `d_R(y)` is the open-box degree.  Interior sites have degree six, while
boundary sites have smaller degree.  There is no uniform `3c/2` allocation in
an open box.  If an open-volume KP representation is used, its local potential
must retain the site-dependent diagonal `(c/2)d_R(y)` or state an explicitly
uniform upper/lower comparison.  The periodic pressure/FSS route may use the
translation-invariant `3c` allocation, but it must not silently be copied to an
open boundary argument.

## 6. Consequences for the Q3LOCK proof chain

1. The FSS ferromagnetic pair coupling remains `J=c`, the spatial Laplacian
   remains `L_sp=D^*D`, and `Jhat_0=6c` remains correct.
2. The KP local potential in every exact periodic crosswalk must use `+3c|q|^2`
   (equivalently `(r+6c-a)|q|^2/2` before the source term), not `+3c|q|^2/2`.
3. The registered coercivity line `b=(r+6c-a)/2` is consistent with the
   corrected expansion.  Any estimate that was derived from an explicit
   `3c/2` potential must nevertheless be recomputed from the corrected line.
4. The collective uniform mode, for which the spatial difference term vanishes,
   and the FSS source-shift constant are not changed by this bookkeeping
   correction.  This is not permission to skip the full recomputation: all
   finite-volume normalizers, form-domain maps, and pressure comparisons must
   use one convention throughout.
5. P-04 (KP topology/crosswalk) and P-09 (continuous-loop FSS passage) remain
   open.  P-12 remains conditional on them.  No strict cusp, DLR multiplicity,
   or phase conclusion is promoted by this audit.

## 7. Affected notes and required repair

The following research notes contained the uncorrected `3c/2` identity and
must be corrected or explicitly superseded before manuscript drafting:

* `strategy/q3lock-feynman-kac-finite-volume-crosswalk-260904.md`
* `strategy/q3lock-kp-assumption-a-dlr-tangent-crosswalk-audit-260904.md`
* `strategy/q3lock-kp-theorem-number-and-form-domain-independent-audit-260904.md`
* `strategy/q3lock-kp-loop-topology-interpolation-crosswalk-260905.md`
* `strategy/q3lock-fss-source-differentiation-audit-260904.md`
* `strategy/q3lock-p09-constant-source-loop-limit-audit-260905.md`

The correction is a research-text repair, not a claim-tier change.  After the
repair, an independent reviewer must re-run the full source/form-domain map,
the periodic/open pressure comparison, the grid normalizer estimates, and the
FSS-to-Duhamel normalization using the corrected local coefficient.  The final
paper must include the edge multiset convention and the `L=2` treatment.

## 8. Adversarial checks

1. **The pair norm changes from `6c` to another value.**  UPHELD as a concern,
   but the exact ordered incidence count gives `Jhat_0=6c`; only the onsite
   diagonal changes.
2. **The old `3c/2` coefficient can be retained by calling `<yz>` oriented.**
   UPHELD as a possible notation ambiguity, not a valid repair: orienting both
   directions doubles the difference sum and gives a different factor, while
   orienting only one endpoint is not an algebraic expansion.  The paper must
   use an explicit edge multiset.
3. **The constant-field mode is irrelevant because the source is zero-sum.**
   UPHELD as a proof-safety objection: even if the FSS source is zero-sum, the
   Hamiltonian/KP crosswalk must be an identity for all fields.  The constant
   mode exposes the mismatch immediately.
4. **The correction invalidates the registered coercivity regime.**
   DISMISSED: the pre-A certificate already uses `(r+6c-a)/2`; the regime and
   `Jhat_0` are not thereby certified, but their displayed quadratic ledger is
   consistent with the corrected expansion.
5. **A finite-box algebra check closes P-09.**  DISMISSED: it repairs one
   normalization seam only.  Grid-to-loop uniform integrability, topology,
   source tangents, and external proof audit remain required.

## 9. Disposition

The `3c/2` identity is **REJECTED for the declared Q3LOCK Hamiltonian**.  The
correct periodic onsite allocation is `3c`; open boxes require
`(c/2)d_R(y)`.  This note records a necessary correction and leaves the
load-bearing Q3LOCK result at its existing T0/research status.  PDF generation,
rendering and visual review remain reserved for the final content-frozen stage.
