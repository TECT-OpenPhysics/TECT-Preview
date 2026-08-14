# R-169 v1.2 certificate: Reading-H covariance-to-P1 interface

Issued: 2026-08-14  
Task: T-055  
Exploration: EXP-000858  
Tier: T0, claim-bearing false

## 1. Result and scope

This certificate resolves two narrow mathematical parts of the open
Reading-H-to-pinned-P1 interface.

First, phase-complete Reading-H shell data have an exact real scalar synthesis
and an exact positive-definite covariance.  The isotropic Gaussian-Hartree
dressing likewise gives a radial covariance.  Multiplication by the registered
rank-one internal projector gives a canonical covariance/composite embedding.
If the shell is additionally commensurate with the side-16 reciprocal lattice,
one obtains a chosen scalar-polarized P1 field with an exact norm and covariance.

Second, three automatic promotions are false:

1. stationary covariance-only data do not deterministically and
   translation-equivariantly select a nonzero BCC mean field;
2. the printed Reading-H `q0` shell is not an exact side-16 reciprocal shell;
3. the historical Reading-H scalar nonlinear convention is not the
   hash-pinned P1 `F_ref` convention used by R-157.

The result does not close the parent interface.  A full bridge still needs a
declared symmetry-breaking or phase datum, reciprocal projection or changed
domain, polarization and normalization, image of `G_*`, common reference and
ensemble, and an exact or error-budgeted full-energy intertwiner.

## 2. Source objects and coefficient convention

The Reading-H referee authority defines a competitor `Q` as a finite point set
on the Brazovskii shell `|k|=q0`, with amplitudes.  The reference `G_*` is the
rotation-invariant Gaussian-Hartree dressing.  A supporting registered note
fixes phase-complete coefficients

`c_-k=conj(c_k),     I=sum_(k in Q)|c_k|^2`.                    (2.1)

The source hashes are frozen in the manifest.  In particular:

- the cFull referee package defines `Q` and `G_*`;
- the weighted coefficient note defines (2.1);
- Math424 fixes the historical scalar convention;
- the A1/P1 manifest distinguishes the known-obstructed `F_decl` from the
  hash-pinned `F_ref` used by R-157.

The target of R-157 is different in type.  It is a classical mean or condensate
field

`Psi in H^2(T^3_16;C^3)`                                      (2.2)

for one fixed side-16, eta-shell-zero, unconstrained functional.  A covariance
and a mean field are not interchangeable data.

## 3. Exact scalar synthesis and discrete covariance

For finite antipodal `Q` satisfying (2.1), define

`phi_Q(x)=sum_(k in Q)c_k exp(i k dot x)`.                       (3.1)

Pairing `k` with `-k` shows that `phi_Q` is real.  It is a finite
Bohr-almost-periodic field.  Let `M_x` denote the Bohr mean.  Distinct
characters are orthogonal under that mean, so

`C_Q(z)=M_x[phi_Q(x+z)phi_Q(x)]`

`      =sum_(k in Q)|c_k|^2 exp(i k dot z)`,                    (3.2)

and `C_Q(0)=I`.

The kernel is positive definite.  For any finite points `x_j` and complex
numbers `a_j`,

`sum_(i,j) conj(a_i)a_j C_Q(x_i-x_j)`

` =sum_k |c_k|^2 |sum_j a_j exp(-i k dot x_j)|^2 >=0`.          (3.3)

Antipodal equality of the weights also makes `C_Q` real and even.

## 4. Isotropic dressing and the pinned internal composite

Assume the registered dressing is nonnegative and integrable in its declared
`d^3q` convention.  Define

`C_*(z)=integral exp(i q dot z) G_*(q) d^3q`.                    (4.1)

The same square identity as (3.3), now under the integral, proves positive
definiteness.  Isotropy of `G_*` makes `C_*` radial.  Its value `C_*(0)` is the
integrated spectral weight and is not the internal projector below.

The pinned P1 manifest supplies `z0=(1,1,1)`.  Put

`u0=z0/sqrt(3),     P0=u0 u0^dagger=z0 z0^dagger/3`.            (4.2)

Then

`K_Q(z)=C_Q(z)P0,     K_*(z)=C_*(z)P0`                         (4.3)

are positive-definite `C^(3x3)` covariance/composite kernels.  Equation (4.3)
is the strongest canonical crosswalk supplied here.  It is not a deterministic
P1 mean field and has no asserted energy identity.

## 5. Conditional commensurate P1 lift

Suppose additionally that every frequency belongs to the exact side-16
reciprocal lattice:

`Q subset (2pi/16)Z^3`.                                        (5.1)

Write its phase-complete coefficients as `c_n` and define

`Psi_Q(x)=u0 sum_n c_n exp(2pi i n dot x/16)`.                   (5.2)

This is a smooth member of (2.2).  Orthogonality of side-16 torus characters
gives

`||Psi_Q||_2^2=16^3 sum_n|c_n|^2=4096 I`.                      (5.3)

The normalized outer-product covariance is

`16^-3 integral Psi_Q(x+z)Psi_Q(x)^dagger dx=C_Q(z)P0`.         (5.4)

The factor 4096 is load-bearing.  Fixed Reading-H intensity maps to fixed P1
norm.  Thus the lift does not turn the Reading-H tournament into the
unconstrained variational problem of R-157.  R-157 can test the value of one
specified P1 field, but its unconstrained critical/local conclusion is not a
fixed-norm tangent theorem and it does not compare the Hartree functional.

## 6. Deterministic equivariant nonextraction from covariance

Let `C` be stationary covariance-only data.  Translation acts trivially on
`C`: `T_y C=C` for every `y`.  Suppose a deterministic section `S` from such
data to mean fields is translation equivariant:

`S(T_y C)=tau_y S(C)`.                                         (6.1)

Then (6.1) gives `tau_y S(C)=S(C)` for every translation.  Hence `S(C)` is
spatially constant.  If the section preserves centering, or if its output is
required to have spectral support away from zero, the constant is zero:

`S(C)=0`.                                                       (6.2)

Consequently the centered isotropic `G_*` covariance cannot by itself select a
nonzero BCC mean field through a deterministic equivariant rule.  A phase,
origin, orientation, external source, random choice, set-valued orbit, or other
non-invariant datum is necessary.  This no-section theorem does not apply to
phase-complete `(Q,c)` and does not prohibit covariance/composite observables.

## 7. Exact side-16 shell obstruction

The hash-pinned manifest prints the literal decimal

`q0=0.6801747616=212554613/312500000`.                           (7.1)

Side-16 reciprocal frequencies are

`k_n=(pi/8)n,     n in Z^3`.                                   (7.2)

For a rational proof that does not rely on floating-point equality, use
Machin's identity

`pi=16 atan(1/5)-4 atan(1/239)`.                                (7.3)

Alternating rational partial sums through powers 23 and 7 give lower and
upper bounds whose width is below `8e-17`.  Direct exact Fraction arithmetic
then proves

`3pi^2/64 < q0^2 < 4pi^2/64`.                                  (7.4)

If `|k_n|=q0`, equations (7.2)-(7.4) would require the integer `|n|^2` to lie
strictly between 3 and 4.  Therefore the literal exact side-16 `q0` shell is
empty.

If the decimal is instead reinterpreted as the exact commensurate value

`q0=pi sqrt(3)/8`,                                              (7.5)

then the shell contains exactly the eight indices

`n=(+/-1,+/-1,+/-1)`.                                          (7.6)

The registered Reading-H BCC support has twelve `{110}` directions, so there
is no support-preserving injection into (7.6).  R-169 v1.1 used `4{110}` on
the side-16 torus; those indices have `|n|^2=32`, so that construction preserves
BCC combinatorics only after changing the wavelength.  It is not an on-shell
Reading-H embedding.

A tolerance, snapping rule, off-shell map, domain change, or new shell
parameter can avoid this obstruction only after its map and error budget are
registered.

## 8. Bare nonlinear convention firewall

Math424 fixes

`u=2lambda=-0.86,     v=2gamma=3.24`,                           (8.1)

so its bare scalar nonlinear density is

`V_RH(phi)=(lambda/2)phi^4+(gamma/3)phi^6`.                     (8.2)

The hash-pinned `F_ref` used by R-157 instead contains

`V_P1(Psi)=(lambda/4)rho^2+(gamma/6)rho^3`,                    (8.3)

with `rho=Psi^dagger Psi`.  On the direct scalar polarization
`Psi=phi u0`, `phi` real, equations (8.2)-(8.3) give

`V_RH(phi)-V_P1(phi u0)`

` =lambda phi^4/4+gamma phi^6/6`

` =phi^4(108phi^2-43)/400`.                                    (8.4)

The defect changes sign at

`phi^2=43/108`.                                                 (8.5)

Two exact fixtures are

`phi^2=1/4:  defect=-1/400`,                                   (8.6)

`phi^2=1/2:  defect=11/1600`.                                  (8.7)

It is therefore neither a candidate-independent additive constant nor a
one-sided ordering correction.  A fixed amplitude rescaling with unchanged
energy units cannot repair both terms: quartic matching requires `s^4=2`,
while sextic matching requires `s^6=2`, which is inconsistent.

Equation (8.4) is only a bare-density crosswalk.  It is not the difference of
the complete functionals.  Math424 also contains determinant, self-consistent
trial-mass, mixed amplitude-mass, and gap-minimization terms.  P1 uses different
quadratic data and has separately owned family, lock, and Class-II terms.  The
historical bare convention agrees with the obstructed `F_decl`, whereas R-157
applies only to the hash-pinned half-coefficient `F_ref`.

Thus identical printed `lambda`, `gamma`, and `q0` names do not provide a full
energy or ensemble intertwiner in either direction.

## 9. Exact negative-result boundaries

The covariance no-section result rejects only automatic deterministic
equivariant extraction of a nonzero mean from stationary covariance-only data.
It does not reject phase-complete fields, random symmetry breaking, or
set-valued phase orbits.

The scalar convention result rejects only automatic direct scalar or fixed
amplitude-normalization identification at unchanged energy units.  It does not
reject a separately declared renormalized map, parameter retuning, counterterm
matching, or a proved full-energy error budget.

The shell result rejects only an exact on-shell, support-preserving side-16
lift using the literal registered `q0` and BCC `{110}` support.  It does not
reject off-shell fields, projections with error control, a changed cell, or a
new commensurate parameter.

These three scopes are registered separately because they have different
revisit conditions.

## 10. Nonduplication

R-169 v1.1 constructed and eliminated one explicit off-shell P1 BCC field but
only recorded the absence of a Reading-H map.  The present result supplies the
first exact covariance/composite crosswalk, conditional phase-complete lift,
equivariant no-section proof, rational torus-shell obstruction, and nonlinear
coefficient crosswalk.

R-169 v1.0 concerned realization combinatorics, finite-part scheme dependence,
and matched sign/stability transfer.  It did not compare covariance with a mean
field or the two scalar coefficient conventions.

R-157 remains the exact unconstrained pinned-P1 theorem.  R-158 remains the
changed fixed-charge or grand-canonical escape.  Neither identifies the
Reading-H Hartree energy with `F_ref`.

## 11. Devil's-advocate review

**Sign and factor audit.**  The antipodal field uses the full coefficient list
once.  It does not multiply both a cosine factor two and two antipodal
coefficients.  The covariance keeps `|c_k|^2`; the torus norm carries volume
`16^3=4096`.  The nonlinear difference is Reading-H minus P1 and has the signs
in (8.6)-(8.7).

**Convention audit.**  `P0` is the internal rank-one projector, not `C_*(0)`.
The `d^3q` normalization is inherited and not silently replaced by a Fourier
normalization.  The direct lift fixes one internal polarization and is not
claimed to intertwine spatial and internal rotations.

**Units audit.**  Shell coordinates, torus length, Fourier normalization,
intensity, L2 norm, and energy units remain distinct.  Equation (8.4) compares
only terms written in the same declared scalar amplitude convention.

**Convergence audit.**  The discrete covariance is finite.  The continuous
covariance assumes `G_*` integrable.  The pi bracket uses alternating rational
series with explicit remainder order; no decimal rounding decides (7.4).

**Hardcode audit.**  The scripts derive every reported number from `q0`, side,
coefficient fractions, supports, and series orders.  Expected outputs occur
only in named `TEST_ORACLE` dictionaries and are compared after derivation.

**Limit and failure cases.**  At `I=0`, the conditional field is zero and no
mean extraction is claimed.  Without phase completeness only covariance data
remain.  Without integrability (4.1) is not asserted.  If a new q0 tolerance,
domain, energy rescaling, symmetry-breaking seed, or ensemble is introduced,
this package requires a new owner rather than silently extending its result.

External review is invited on the Bohr/Fourier normalization, the covariance
versus mean-field type split, the translation action in the no-section proof,
the exact Machin bounds, the sign of (8.4), and all ensemble firewalls.

## 12. Formal boundary

This is a T0, claim-nonbearing analytic/exact/executed route result.  It closes
only the two scoped child gates named in the manifest.  The full
`PA-T055-READING-H-REALIZATION-TO-PINNED-P1-OR-DECLARED-ESCAPE` gate remains
OPEN.  No B1/B3 ranking is promoted or refuted.  No physical empty reference,
vacuum, BCC resurrection, C6 spacetime conclusion, Round-1 admission, physical
Sector A theorem, or Pre-A closure follows.  No R-169 v1.2 PDF is issued.
