# Q3LOCK KP vector-hypothesis crosswalk and theorem-domain audit

**Status:** T0 independent source-to-model audit; no claim-card promotion  
**Date:** 2026-09-05  
**Owner task:** T-054  
**Research authority:** EXP-000780 -> EXP-000781 -> EXP-000782  
**Primary source:** Kozitsky--Pasurek, arXiv:math-ph/0609045v1, Assumption (A),
Assumption (B), equations (2.1)--(2.8), (2.16), (2.33)--(2.54), and
Theorems 3.1--3.3  
**PDF:** deferred until content freeze, independent mathematical review, clean
replay and final release review

## 1. Question and strict boundary

The earlier KP/FSS source audit identified the correct general-vector KP
theorems but left the line-by-line Q3LOCK hypothesis map as an open gate.  This
note checks that map without importing KP's separate scalar order results.  It
also separates the fixed-source conclusion of KP Theorems 3.1--3.3 from the
source-window and thermodynamic uniformity needed by the Q3LOCK phase route.

The disposition is a **T0 theorem-domain crosswalk only**.  It does not certify
that the Q3LOCK local specification, source-tangent sequence, pressure limit,
infrared estimate, cusp, or DLR multiplicity is complete.  No claim card,
manuscript release or PDF is created.

## 2. Frozen model and notation map

The Q3LOCK spatial lattice is `L=Z^3`, with periodic finite boxes
`Lambda_L=(Z/LZ)^3` and `V=L^3`.  At each site the displacement is
`q_y in R^8`, the collective unit vector is

```text
u=(1,...,1)/sqrt(8),       Q_y=(u,q_y),
```

and the Hamiltonian uses the source `-h*sum_y Q_y`.  The exact onsite and
spatial terms are

```text
r/2*|q_y|^2 + g/4*sum_e q_(y,e)^4
  + lambda/4*sum_{ {e,f} in E(Q3) }
      (q_(y,e)-q_(y,f))^2*(q_(y,e)^2+q_(y,f)^2),
```

and

```text
(c/2)*sum_{<yz>} |q_y-q_z|^2,
```

with `hbar,chi,c,g,lambda>0` and `r<0`.  The KP oscillator dimension is
therefore `nu=8`, the lattice dimension in KP's notation is `d=3`, and the
Euclidean mass parameter after the declared canonical rescaling is
`m=chi/hbar^2>0`.  The auxiliary KP harmonic rigidity is an arbitrary fixed
`a>0`; the compensating quadratic is kept in the Q3LOCK local potential and is
recombined before the exact Hamiltonian is stated.

For the periodic positive-direction edge convention, each site has six
endpoint incidences.  Expanding the spatial difference term gives

```text
(c/2)*sum_{<yz>} |q_y-q_z|^2
 = 3c*sum_y |q_y|^2 - c*sum_{<yz>} (q_y,q_z).
```

Thus the ordered KP matrix has `J_(y,z)=c` on each directed nearest-neighbour
edge, `J_(y,z)=J_(z,y)`, and

```text
Jhat_0 = sup_y sum_z |J_(y,z)| = 6c.
```

The open-box diagonal convention is different and is not used in this
periodic crosswalk.

## 3. Assumption (A): line-by-line verification

### 3.1 Continuous local potential and normalization

After the harmonic split, the one-site KP potential at source `h` is

```text
V_(h,a)(q) = ((r+6c-a)/2)*|q|^2
             + (g/4)*sum_e q_e^4
             + W_Q3(q) - h*(u,q),
```

where `W_Q3` is the nonnegative twelve-edge Q3 locking polynomial.  This is a
polynomial on `R^8`, hence continuous, and `V_(h,a)(0)=0`.  No radial or
`O(8)` invariance is asserted or needed for the general KP theorems.

### 3.2 Coercive lower bound and the KP exponent

The explicit Q3LOCK quartic audit gives, for every fixed `a` and every compact
source window `|h|<=h_0`,

```text
V_(h,a)(q) >= A_4*|q|^4 - C_(a,h_0),
A_4 = g/128 > 0.
```

Consequently KP Assumption (A), equation (2.5), is met with the unambiguous
notation

```text
r_KP = 2 > 1,
A_V = g/128,
B_V = -C_(a,h_0).
```

The symbol `r_KP` is kept distinct from the Q3LOCK quadratic coefficient `r`.
The bound is uniform on the declared source window but is only a fixed-window
statement; it is not a claim uniform over all sources.

### 3.3 Continuous upper function

The same audit gives the continuous upper function

```text
V^+_(a,h_0)(q) = (g/4+3*lambda)*sum_e q_e^4
                  + R_a*|q|^2 + h_0*|q|,
R_a=abs(r+6c-a)/2,
```

with `V_(h,a)(q)<=V^+_(a,h_0)(q)` for `|h|<=h_0` and
`V^+_(a,h_0)(0)=0`.  This supplies the upper side of KP (2.5), including the
linear collective source, without replacing the nonradial Q3 potential by a
radial comparator.

### 3.4 Interaction norm and finite range

The periodic nearest-neighbour matrix is symmetric, has zero diagonal, and
has finite range one.  Therefore KP (2.6) holds with `Jhat_0=6c`.  The
Q3LOCK locking polynomial is onsite in KP's spatial lattice index; it is not
part of `J_(y,z)` and must not be counted a second time in `Jhat_0`.

### 3.5 Finite-volume operator input

The quartic lower bound plus the nonnegative spatial difference term gives a
finite-volume confining potential.  The associated quadratic form is defined
on

```text
H^1(R^(8V)) cap L^2(R^(8V), (sum_y |q_y|^4)dq),
```

and is closed and bounded below after a finite constant shift.  This is the
Q3LOCK-local input needed to match KP's finite-volume statement (2.8):
self-adjointness, lower boundedness, compact resolvent and finite heat trace.
The source audit does not treat (2.8) as a substitute for the separate
unbounded collective-commutator/core audit.

## 4. Lattice regularity and Assumption (B)

KP's lattice regularity condition (2.1) is satisfied by `Z^3`: for every
positive epsilon, the sum of `(1+|y-z|)^(-3-epsilon)` is finite uniformly in
`y`.  Because the Q3LOCK interaction has finite range, the exponential weight
family in KP (2.42)--(2.43) is available for every `alpha>0`,

```text
w_alpha(y,z)=exp(-alpha*|y-z|).
```

For this family, KP's weighted interaction norm is finite; with the declared
nearest-neighbour convention one may write the explicit bound

```text
Jhat_alpha = 6c*exp(alpha),
Jhat_alpha-Jhat_0 = 6c*(exp(alpha)-1) -> 0 as alpha downarrow 0.
```

The logarithmic weighted sum in (2.39) is also finite.  Hence, for every
delta required in KP's compactness construction, alpha can be chosen small
enough that (2.41) holds.  This is the precise finite-range reason that the
weighted tempered topology can be used without a long-range decay assumption.

The resulting spaces are KP's `Omega_alpha` and projective-limit
`Omega_t`, built from periodic continuous loops with weighted sitewise
`L^2_beta` control.  The finite-volume interpolation arguments in P-06 first
produce weak convergence in a finite product of periodic sup-norm loop spaces;
that topology must not be silently identified with global `Omega_t` convergence.

## 5. What KP Theorems 3.1--3.3 do and do not supply

Under the preceding hypotheses, KP's general-vector results have the following
permitted Q3LOCK use.

| KP input | Q3LOCK use after the map | boundary |
|---|---|---|
| Theorem 3.1 | For each fixed `beta>0` and fixed `h`, nonempty tempered Euclidean DLR set and `W_t` compactness | does not give compactness of the union over a source interval or a thermodynamic pressure limit |
| Theorem 3.2 | Uniform-over-states exponential loop moments at that fixed model/source | source-window uniform constants still need the Q3LOCK quartic majorant and a common-compactness argument |
| Theorem 3.3 | Tempered-state support control in the KP weighted topology | support control is not a phase distinction and does not imply a cusp |
| KP (2.53)--(2.59), Lemma 2.11 | finite specification continuity and accumulation mechanism | boundary/source uniformity and the chosen periodic-volume sequence remain Q3LOCK-local obligations |

The finite source `h` is a vector source `J=h*u` in `R^8`; restricting the
source to this one-dimensional line does not change the eight-component local
potential.  Global parity maps `h` to `-h`, but no componentwise sign flip or
internal rotation is introduced.

## 6. Source-window and source-tangent firewall

The pressure-to-DLR construction uses sources `h_n -> 0` and requires one
subsequence of source-varying DLR states.  Pointwise application of Theorem 3.1
is insufficient for that purpose.  The needed additional Q3LOCK-local steps
are:

1. use the window-uniform quartic lower bound and the finite-range boundary
   estimate to obtain a common weighted-tempered tightness bound for the
   selected states;
2. prove uniform-on-compact source continuity of each finite-region
   specification, including a source-uniform normalizer lower bound; and
3. pass the DLR identity to the zero-source weak limit by the compact-boundary
   split and KP Feller continuity.

These are the obligations recorded in the source-window Feller audit.  KP's
fixed-source compactness theorem is a necessary input, not the complete
source-tangent theorem.  Likewise, the KKK endpoint inequality and the
EXP-000780 pressure limit are not consequences of KP Theorems 3.1--3.3.

## 7. Scalar-theorem firewall

KP's Section 3.2 order/phase results explicitly specialize to `nu=1` and
ferroelectric `J_(y,z)>=0`.  In particular, Theorems 3.8, 3.10, 3.12 and the
associated scalar FKG/correlation propositions cannot be cited as the
continuous-loop FKG, infrared bound, pressure cusp or phase theorem for the
nonradial `R^8` Q3LOCK model.  The Q3LOCK proof uses its own mixed-derivative
association calculation and the finite-vector FSS estimate instead.  KP is
used here only for the general vector finite-volume and tempered-DLR inputs.

## 8. Dependency table and open hypotheses

| downstream step | KP crosswalk status | remaining independent check |
|---|---|---|
| finite-volume Feynman--Kac loop law | matched conditionally | exact `hbar`/mass convention and common form core |
| fixed-source DLR existence | matched for each fixed source | external theorem acceptance and exact periodic-to-infinite specification |
| source-varying compactness | not supplied by KP alone | common source-window weighted moment/tightness estimate |
| P-06 continuous-loop FKG | not a KP theorem in `nu=8` | Q3LOCK finite-grid, interpolation and clip-removal chain |
| P-09 infrared/Duhamel passage | not a KP theorem | FSS map, source/UI and loop second-derivative convergence |
| pressure cusp and tangent pair | not supplied by KP | EXP-000780, KKK, zero-mode and source-to-zero composition |

The crosswalk therefore advances only the theorem-domain gate.  It does not
remove any of the analytic or external-review gates listed in the R-497
manifest.

## 9. Adversarial checks

1. **The KP exponent `r` can be identified with the Q3LOCK coefficient `r`.**
   Rejected: KP's exponent is renamed `r_KP=2`; the Q3LOCK `r<0` is only a
   quadratic coefficient.
2. **The positive Q3 locking term must be inserted into the KP pair matrix.**
   Rejected: it is onsite in the lattice index and belongs in `V_(h,a)`;
   inserting it into `J` would change both the model and `Jhat_0`.
3. **Finite range makes the KP weighted topology automatic without checking
   (2.39)--(2.41).**  Rejected: the exponential weights and the
   `Jhat_alpha-Jhat_0` limit are displayed explicitly.
4. **Theorem 3.1 gives source-uniform compactness for `h_n -> 0`.**  Rejected:
   its statement is pointwise in the model/source; a common source-window
   bound is a separate Q3LOCK lemma.
5. **KP's scalar FKG/phase results apply because the collective source is
   one-dimensional.**  Rejected: source restriction does not reduce the
   field dimension, and the local Q3LOCK law remains nonradial in `R^8`.
6. **KP compactness proves a strict cusp or two distinct DLR states.**
   Rejected: it supplies existence/compactness only; pressure slope, zero-mode
   positivity, parity and distinctness remain conditional.
7. **The source crosswalk authorizes a final manuscript or PDF.** Rejected:
   claim registration, independent referee review, content freeze, clean replay
   and final PDF generation remain deferred.

## 10. Disposition and next gate

The KP theorem-domain map is internally consistent at T0: Q3LOCK has
`nu=8`, `L=Z^3`, a continuous quartically confining residual potential with
`r_KP=2`, finite-range `Jhat_0=6c`, admissible exponential weights, and the
finite-volume form needed for the general KP construction.  The scalar KP
phase route is explicitly excluded.

The result is **T0 crosswalk advanced; no theorem or claim closure**.  The next
gate is an independent line-by-line acceptance of the mass/form-domain map,
source-window common constants, and the exact `W_t`/specification passage,
followed by a bounded claim/result-lineage decision.  PDF creation remains a
final-stage action only after content freeze, independent audit, clean replay
and release review.

## 11. Explicit nonclaims

This note does not assert a strict infrared lower bound, source cusp, phase
coexistence, extremality, purity, clustering, common real-time dynamics,
algebraic KMS state, ground-state phase, spectral gap, continuum limit,
physical vacuum, cosmological interpretation, C6/CP1/Sector-A/Pre-A closure,
or Yang--Mills conclusion.  It creates no claim card, P2 manuscript,
submission, upload, tag, release or PDF.
