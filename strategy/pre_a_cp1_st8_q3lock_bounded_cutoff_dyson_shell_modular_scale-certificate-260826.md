# EXP-001091 — bounded-cutoff Dyson shell and modular scale certificate

## Decision

Under the explicit bounded-cutoff hypotheses in the manifest, the
interaction-picture Dyson series has a factorial first-passage shell bound,
and the declared sublinear scale `L=R^alpha` makes both the dynamic weighted
shell and the registered static Gaussian shell decay for both signs/orientations.
The primary, independent, and integrated lanes agree, and the exact fixture
arithmetic compiles in Lean R273.

This is a conditional bridge only.  It does not prove the exact Q3
modular-history envelope, the comparison of the unbounded Q3 dynamics with the
cutoff dynamics, or any downstream QFT, C6, Sector A, or Pre-A closure.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale_independent.py
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale_verify.py
lake env lean Tect/R273.lean
```

The primary lane passes 20/20, the independent lane 15/15, and the
integrated verifier 14/14 with Lean PASS.  The canonical JSON artefacts are
under the three `2026-08-26-*bounded_cutoff_dyson_shell_modular_scale`
directories below `claims/C6-SPACETIME-SIGNATURE/runs/`.

## Conditional bridge

Let `Delta` be the graph degree bound, `T` the time horizon, and let every
cutoff interaction-picture bond have norm at most

\[
V_L=v_0+v_2L^2.
\]

The declared commutator estimate gives

\[
\lambda_L=\frac{2\Delta T}{\hbar}(v_0+v_2L^2).
\]

If a response at graph distance `R` requires at least `R` bond insertions,
then for every weight base `b>1`

\[
\sum_{n\ge R}\frac{\lambda_L^n}{n!}
 \le b^{-R}\exp(b\lambda_L).
\]

The factor two in the certificate is the explicit sum over the two time
signs/orientations.  For `delta-D`, the same calculation is conditional on an
additional modular multiplier `m1` that is uniform in volume, source, and
intermediate background.  With `L=R^alpha`, `0<alpha<1/2`, the coefficient of
`R^(2 alpha)` is dominated by the linear `-R log b` term.  Combining this with
the declared static shells gives

\[
C_jR^dL^{m_j}\exp\bigl(-(a_j-\kappa_jT)L^2\bigr),
\qquad a_j>\kappa_jT,
\]

for `j=0,1` (D and `delta-D`).  Thus the displayed conditional shells tend
to zero as `R` tends to infinity.

## Exact fixture and independent agreement

The manifest fixture is `Delta=6`, `hbar=T=1`, `v0=1/50`, `v2=1/100`,
`b=2`, `m1=2`, `alpha=1/3`, dimension `d=3`, and radii `64,512,4096` with
cutoffs `4,8,16`.  The exact coefficients and margins are

```text
kappa_D              = 6/25
kappa_delta-D        = 12/25
a_D - kappa_D        = 244/25
a_delta-D-kappa_delta-D = 288/25
2*alpha - 1          = -1/3
```

The primary and independent JSON rows agree to the integrated verifier's
`1e-12` comparison threshold.  The corrected two-sign log rows are:

| R | D dynamic | delta-D dynamic | D static | delta-D static |
|---:|---:|---:|---:|---:|
| 64 | -39.3482723753 | -35.0282723753 | -137.4450261249 | -162.8324374026 |
| 512 | -338.3582092661 | -322.5182092661 | -596.9141127776 | -705.3952296942 |
| 4096 | -2776.5177043930 | -2714.5977043930 | -2461.8231994303 | -2906.8380219858 |

R273 checks the exact rational coefficients, scale inequalities, margins,
orientation count, perfect-cube radii, and the finite-only scope firewall.
Lean is used here for arithmetic fixtures; it does not formalize Dyson
convergence, unbounded operator domains, thermodynamic limits, or the modular
history hypothesis.

## Adversarial review

1. **Bounded versus unbounded Q3.**  The estimate is proved only for the
   declared cutoff bond bound. **UPHELD as an open gate:** an unbounded
   full-versus-cutoff comparison is still required.
2. **Onsite flow.**  Norm-isometry and support preservation of the onsite flow
   are hypotheses, not consequences of the finite fixture. **UPHELD as an
   explicit hypothesis.**
3. **First-passage distance.**  The `R`-insertion lower bound is conditional
   on the chosen local graph and support notion. **UPHELD conditionally; actual
   Q3 implementation remains open.**
4. **Modular multiplier.**  The `delta-D` shell uses a uniform multiplier
   `m1`. **UPHELD as an open modular-history/locality gate; it is not inferred
   from finite matrices.**
5. **Two signs.**  Both orientations are included through the explicit factor
   two and both dynamic/static rows. **UPHELD.**
6. **Asymptotic inference.**  The three radii are a finite arithmetic fixture,
   not a proof of a limit. **UPHELD; the symbolic scale inequality carries the
   conditional asymptotic statement.**
7. **Lean scope.**  R273 proves exact rational fixtures only. **UPHELD; no
   operator-theoretic or QFT theorem is claimed from its compilation.**
8. **QFT promotion.**  Common alpha, KMS/OS/GNS identification, a physical
   gap, continuum, C6, Sector A, and Pre-A are not supplied. **UPHELD as open.**

## Boundary and next action

Closed in this package: the bounded-cutoff factorial Dyson shell envelope,
the two-sign arithmetic scale balance under the declared modular hypothesis,
independent reproduction, and R273 exact checks.  Open: the actual Q3
source/volume-uniform modular-history estimate, unbounded tail comparison,
all-shape exhaustion/Cauchy, common alpha, and the downstream QFT bridge
through KMS/OS/GNS and the gap.  The next proof action is therefore to derive
the modular-history bound on the actual Q3 common core (or obtain a rigorous
route-local obstruction), then compare the full and cutoff dynamics before
reassessing the common-alpha gate.

No claim tier, result authority, negative authority, changelog event, or PDF is
created by this certificate.

## Provenance

```text
primary       906a44df734043372a2984601a5a9bd6d6bc2e29b358af38946223aa15fed889
independent   7f77a14962856708eb95b5dd295eb4a5557e1d3a3cd9bf394e5a4c52af964b3b
manifest      12b3288bc0aabd7dd58339ac9eb8124fffd24f21ef7d53c9e7b49898e0477f9f
R273          4c7dbe4999d57ad8ba65e4845eec7cde5c61e9d9c07f558c3e8978ca02c7afce
integrated    claims/C6-SPACETIME-SIGNATURE/runs/2026-08-26-integrated-pre_a_cp1_st8_q3lock_bounded_cutoff_dyson_shell_modular_scale/integrated.json
```
