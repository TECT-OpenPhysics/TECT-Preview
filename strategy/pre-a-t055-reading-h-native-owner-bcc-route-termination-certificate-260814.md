# R-169 v1.3 certificate: native Reading-H BCC realization and route termination

**Date:** 2026-08-14
**Exploration:** EXP-000860
**Task:** T-055
**Tier:** T0
**Claim-bearing:** false
**PDF:** no R-169 v1.3 PDF is issued

## 1. Result and boundary

This certificate closes one narrow child:

`PA-T055-READING-H-NATIVE-ZERO-PHASE-BCC-ORBIT-CELL-AND-GSTAR-SIGN`.

The registered Math424 Reading-H ansatz contains an equal-amplitude,
zero-phase, twelve-mode `{110}` branch.  We identify its exact real-space
translation orbit, its BCC center lattice and its regular
truncated-octahedron Voronoi cell.  At the registered production endpoint we
then specialize the existing B1/B2 theorem and obtain

```text
F_RH[Q_BCC,A] - F_RH[G_*] > 0.
```

Thus this explicit native geometry-bearing BCC branch loses to the isotropic
`G_*` reference in the native Reading-H Gaussian-Hartree owner.  This is not a
sign relative to a physical empty or disordered reference.

The result also strengthens the already closed R-169 v1.2 direct-interface
firewall.  Even after allowing one constant field-amplitude rescaling and one
positive global energy-unit rescaling, the registered Reading-H scalar
coefficients cannot equal the hash-pinned P1 constant-polarization pullback.

The generic parent
`PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE` remains OPEN.
The new result owns only one zero-phase equal-amplitude native branch.  It does
not supply the generic phase/nonuniform-amplitude realization map, the image
of `G_*`, a full Reading-H-to-P1 energy and ensemble intertwiner, or a certified
projection error.  `C6-BCC-PREMISE-BLOCKED` and Round-1 remain OPEN.

## 2. Frozen authorities

The exact source set and normalized SHA-256 digests are frozen in the machine
manifest.  The load-bearing authorities are:

1. the Reading-H cFull referee package, which defines the finite antipodal
   competitor class and proves the strict `F[Q]-F[G_*]>0` comparison in the
   registered physical region;
2. the coefficient note, which fixes `c_-k=conj(c_k)` and
   `I=sum_k |c_k|^2`;
3. `Math424_AddA_reading_uniqueness.py`, which actually instantiates the
   twelve signed `{110}` modes with one amplitude and zero phases;
4. the B2 T7 proposition assembly;
5. the R-169 v1.0, v1.1 and v1.2 manifests; and
6. the hash-pinned P1, R-157 and R-158 manifests used only for the interface
   and ensemble firewalls.

The legacy source is used as a frozen provenance owner, not as executable
proof authority.  The exact derivations in the three v1.3 scripts are the
reproducible audit.

## 3. The registered native `{110}` field

Let

```text
S_110 = {s in {0,+/-1}^3 : |s|^2=2}.
```

It has twelve signed vectors.  Put

```text
q0    = 212554613/312500000,
alpha = q0/sqrt(2),
ell   = 2*pi/alpha = 2*pi*sqrt(2)/q0.
```

For `A>0` and an origin coordinate `o`, define

```text
phi_(A,o)(x) = A sum_(s in S_110) exp(i alpha s dot (x-o)).       (3.1)
```

The full antipodal support is listed once.  Since the coefficient of `-s` is
the conjugate of the coefficient of `s`, the field is real.  Writing

```text
p = cos(alpha(x_1-o_1)),
q = cos(alpha(x_2-o_2)),
r = cos(alpha(x_3-o_3)),
```

the antipodal pairs give

```text
phi_(A,o) = 4A(pq+pr+qr).                                      (3.2)
```

The origin is an orbit coordinate, not a new physical parameter.  Under the
translation convention `(tau_y phi)(x)=phi(x-y)`, one has

```text
tau_y phi_(A,o) = phi_(A,o+y).                                  (3.3)
```

The registered intensity convention gives

```text
I = sum_k |c_k|^2 = 12A^2.                                     (3.4)
```

At the production endpoint `I=1/500`, hence `A^2=1/6000`.

## 4. Exact center lattice

Set `h(p,q,r)=pq+pr+qr` on the cube `[-1,1]^3`.  It is affine in each
coordinate separately, so every maximum and minimum occurs at a cube corner.
At a corner:

* if all three signs agree, `h=3`;
* if exactly one sign differs, `h=-1`.

Therefore

```text
max |h| = 3,
```

and equality occurs only at `(1,1,1)` and `(-1,-1,-1)`.  Notice the important
sign: at both equality corners `h=3`.  In particular, the often tempting
statement that the signed-field maximum is only the simple-cubic coset is
false for this ansatz.

The first corner occurs when every `alpha(x_i-o_i)` is `0 mod 2pi`; the second
when every one is `pi mod 2pi`.  Hence, for `A>0`,

```text
argmax phi_(A,o)
  = argmax |phi_(A,o)|
  = argmax phi_(A,o)^2
  = o + Lambda_BCC,                                             (4.1)

Lambda_BCC
  = ell Z^3 union ((ell/2,ell/2,ell/2)+ell Z^3).                (4.2)
```

Thus the registered zero-phase field itself, not covariance-only data,
supplies an exact translation-equivariant BCC center orbit.  The phase/origin
coordinate is indispensable: the covariance retains relative separation but
forgets the absolute translate `o`.

## 5. The regular truncated-octahedron cell

At the origin of `Lambda_BCC`, the relevant neighbor translations are

```text
+/- ell e_i,
(ell/2)(sigma_1,sigma_2,sigma_3), sigma_i in {+/-1}.
```

Their Euclidean bisectors give the Wigner-Seitz inequalities

```text
|x_i| <= ell/2,
sigma dot x <= 3ell/4 for every sigma in {+/-1}^3.              (5.1)
```

The vertices are the twenty-four permutations of

```text
(0,+/-ell/4,+/-ell/2).                                         (5.2)
```

The six coordinate bisectors carry square faces and the eight diagonal
bisectors carry regular hexagons.  The lattice basis

```text
ell e_1, ell e_2, (ell/2)(1,1,1)
```

has determinant `ell^3/2`.  Consequently the cell is the regular truncated
octahedron with

```text
(vertices,edges,faces) = (24,36,14),
faces = 6 squares + 8 regular hexagons,
volume = ell^3/2.                                               (5.3)
```

This is a Euclidean Voronoi statement for the exact BCC lattice.  It must not
be confused with the merely affine, generally non-Voronoi descendants in the
separate R-169 v1.0 deformation family.

## 6. Mean-square normalization and the natural torus

Bohr averaging of (3.1) kills every nonzero total frequency.  Because the
support is antipodal, exactly the `s+(-s)=0` terms remain:

```text
M_Bohr(phi_(A,o)^2) = 12A^2 = I.                               (6.1)
```

On the natural torus `T^3_(N ell)`, the physical frequency `alpha s` is the
integer Fourier mode `Ns`:

```text
alpha s = (2pi/(N ell))(Ns).                                   (6.2)
```

For the unit constant-polarization lift `Psi=u phi`, orthogonality gives

```text
||Psi||_2^2 = (N ell)^3 I.                                     (6.3)
```

The torus contains `2N^3` centers and cells, each of volume `ell^3/2`.
This is an exact on-shell periodic owner.  Its side length is not the
hash-pinned P1 side 16.

## 7. Native Reading-H sign specialization

The branch satisfies the registered cFull structural hypotheses:

1. it is real and antipodal;
2. it has twelve signed modes;
3. the largest normalized dot product of distinct, nonantipodal `{110}`
   vectors is `1/2`, so the minimum angle is `pi/3`;
4. `pi/3>1>627/1000`, using the elementary `pi>3` bound; and
5. `12<1017/25=40.68`, the registered packing cap.

At `(I,mu2_shell)=(1/500,1/200)` the B1/B2 T7 proposition therefore applies
directly.  It yields the inherited strict sign

```text
F_RH[Q_BCC,A] - F_RH[G_*] > 0.                                 (7.1)
```

No P1 or R-157 premise is used in (7.1).  This is a specialization of an
existing theorem to an explicitly realized geometry-bearing branch.  It
terminates that branch as a native Reading-H winner: the isotropic `G_*`
reference wins.

Equation (7.1) does not compare either state with an empty or disordered
physical reference.  It therefore cannot select a physical vacuum or revive
the retired BCC structural claim.

## 8. Side-16 commensurability firewall

The natural length `ell` cannot equal 16.  Equality would require

```text
q0 = pi sqrt(2)/8,
```

whereas R-169 v1.2 proves that the literal rational `q0` lies strictly above
the side-16 `|n|^2=3` radius `pi sqrt(3)/8`, hence also above the `{110}`
radius `pi sqrt(2)/8`.

There are two different approximations and neither is an identity:

* the side-16 `{110}` shell preserves all twelve BCC directions but changes
  the radius to `pi sqrt(2)/8`;
* the side-16 `{111}` shell is extremely close radially to the printed `q0`
  but has only eight modes and destroys the BCC support.

The natural torus `T^3_(N ell)` has zero shell-projection error, but it changes
the domain owner.  Moreover a small frequency displacement does not control
the field in the Bohr mean.  If the original and snapped finite frequency
sets are disjoint and each has intensity `I`, orthogonality gives

```text
M_Bohr(|phi-phi_snap|^2) = I+I = 2I.                            (8.1)
```

Thus a side-16 projection requires a finite-box pullback and a separately
proved derivative, nonlinear and counterterm error budget.  Radius mismatch
alone is not such a budget.

## 9. Stronger direct-P1 rescaling obstruction

R-169 v1.2 showed that an unchanged-energy-unit amplitude rescaling cannot
simultaneously match the Reading-H quartic and sextic coefficients.  We now
allow more: let

```text
Psi = s u phi,  ||u||=1,  s>0,
```

and allow a positive global target-energy multiplier `c_E`.  Suppose the
zero-reference-subtracted Reading-H scalar expression equals `c_E` times the
registered P1 constant-polarization pullback for every constant real `phi`.
Matching quartic and sextic terms gives

```text
c_E s^4 = 2,
c_E s^6 = 2.                                                   (9.1)
```

Dividing the equations forces

```text
s^2=1, c_E=2.                                                   (9.2)
```

The quadratic term would then require

```text
r_RH = 2(r_P1+h_u).                                            (9.3)
```

The hash-pinned constants obey

```text
r_P1 = 4740336473/10000000000,
h_u > 7/250,

2(r_P1+h_u) > 5020336473/5000000000.                           (9.4)
```

In the Reading-H convention,

```text
r_RH = 1/200 + (212554613/312500000)^4,
```

and exact rational arithmetic gives

```text
r_RH < 5020336473/5000000000.                                  (9.5)
```

Equations (9.3)-(9.5) contradict one another.  Hence the natural constant-
polarization, constant-amplitude, globally rescaled and zero-preserving class
contains no exact Reading-H-to-pinned-P1 intertwiner.

This is deliberately scoped.  It does not exclude a separately owned domain,
projection, nonlocal map, coefficient retuning, counterterm scheme or
ensemble change.  It also does not identify the full Hartree determinant,
trial-mass and gap terms with the P1 family, lock and Class-II terms.

## 10. Ensemble boundary

The conditional side-16 lift of R-169 v1.2 sends intensity to P1 charge as

```text
Q_P1 = (1/2)||Psi||_2^2 = 2048 I.                              (10.1)
```

At `I=1/500`, this is `Q_P1=512/125`.  The R-158 fixed-charge coexistence
intensity is `I_*=43/216`, so

```text
I_*/I = 5375/54.                                                (10.2)
```

R-158 therefore neither certifies nor eliminates the production-intensity
BCC field.  Its saturator is a changed-owner constant-density complex plane
wave, not this real antipodal BCC branch.  R-157 remains an unconstrained
neutral P1 theorem and supplies no Reading-H Hartree ordering.

## 11. Nonduplication and route verdict

The contribution is not a repetition of the earlier R-169 versions:

* v1.0 owns the abstract BCC Voronoi cell and an affine tile family, but no
  Reading-H field or energy sign;
* v1.1 owns a side-16 off-shell P1 BCC-periodic fixture and R-157 conditional
  elimination, but not the native Reading-H shell;
* v1.2 separates covariance from mean fields and proves the generic
  commensurability and direct-energy firewalls, but it does not instantiate
  the actual Math424 native branch;
* v1.3 joins the registered native `(Q,c)` to its exact center/cell orbit and
  then specializes the existing B1/B2 sign theorem.

Only the named native child is CLOSED.  The generic interface parent remains
OPEN because generic phase-complete and nonuniform branches, the `G_*` target
image and an exact or error-budgeted common functional are still absent.  The
three v1.2 negatives and the older structural-selection negative remain valid;
no new negative is registered.

## 12. Devil's-advocate audit

### 12.1 Sign audit

The `(-1,-1,-1)` cosine corner gives `pq+pr+qr=+3`, not `-3`.  Therefore the
signed maximum contains both BCC cosets.  The package explicitly rejects the
false simple-cubic signed-argmax shortcut.  The inherited energy sign is
`F_RH[Q_BCC]-F_RH[G_*]>0`; it eliminates the BCC branch relative to `G_*` and
must never be reversed into a below-empty statement.

### 12.2 Factor and convention audit

The support is the full twelve-vector antipodal list once.  Consequently
`I=12A^2`; no extra cosine factor two is inserted.  Pairing exponentials gives
the displayed `4A(pq+pr+qr)`.  The translation convention is written before
the orbit formula.  The BCC fundamental volume is `ell^3/2`, consistent with
two centers per conventional cube.

### 12.3 Units and owner audit

`q0` and `alpha` are inverse-length quantities; `ell` is a length.  Side 16
and `N ell` are different domain owners.  The native sign belongs to the
Reading-H Gaussian-Hartree ensemble.  The P1 calculation is only a direct-map
obstruction and never changes the owner of (7.1).

### 12.4 Convergence and limit audit

The field and cell statements are finite Fourier/algebraic statements.  No
thermodynamic, continuum or regulator limit is taken.  Bohr means are used
only where explicitly stated.  Equation (8.1) is a warning that frequency
closeness does not by itself provide a Bohr or functional convergence bound.

### 12.5 Hardcode-masking audit

The primary SymPy and non-importing stdlib/Fraction scripts separately derive
the support, corner values, lattice residues, normalization, exact rational
quadratic contradiction and ensemble ratio.  Manifest numbers are labelled
test oracles and are compared only after derivation.  Source hashes are
checked before their conclusions are cited.

### 12.6 Limit cases

`A=0` is the isotropic zero-amplitude reference and the center-extraction rule
is not applied.  Negative `A` changes a signed representative and does not
create the claimed BCC signed maximum; the registered scan uses `A>=0`, and
the theorem uses `A>0`.  Generic phase and unequal-amplitude fields are out of
scope.  A covariance-only input still has no equivariant deterministic mean
field section.  A coefficient-retuned or domain-changed model is a declared
new owner.

### 12.7 External review invitation

External review is invited on the antipodal counting, the sign at the second
cosine corner, the Wigner-Seitz facet set, the inherited cFull membership, the
Bohr snap error, and the coefficient/prefactor convention in (9.1)-(9.5).

## 13. No-overclaim conclusion

R-169 v1.3 is additive T0, claim-nonbearing route work.  It owns exactly one
native zero-phase BCC branch and shows that branch loses to `G_*` in its own
Reading-H comparison.  It does not prove a physical empty-reference sign,
generic Reading-H realization, P1 energy identity, transverse or continuum
stability, candidate completeness, BCC vacuum selection, C6, Round-1,
physical Sector A or Pre-A.  No R-169 v1.3 PDF is issued.
