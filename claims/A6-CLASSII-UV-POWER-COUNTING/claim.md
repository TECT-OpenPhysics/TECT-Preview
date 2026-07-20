# A6-CLASSII-UV-POWER-COUNTING -- derivative Class-II ultraviolet power counting

**Tier**: T4 STRONG-EVIDENCE@BARE-GAUSSIAN-UV (TSv2) |
**Lifecycle**: ACTIVE |
**Last review**: 2026-07-20

## Result

For the canonical A1 full-production quadratic Gaussian on the fixed
three-torus, with three complex components, the six-real-field Gaussian
normalisation induced by the quadratic energy, fixed positive regularisers,
`eta_shell=0`, and the sharp cube projector `max_j |n_j|<=N`, let

```text
A(k) = [r+Z|k|^2+Y|k|^4] I
       + diag(family_masses) + k_lock(I-P0),
C_N  = (2/V) sum A(k_n)^-1,
D_N  = (2/(3V)) sum |k_n|^2 A(k_n)^-1.
```

The factor two in `C_N` and `D_N` is fixed by treating the real and imaginary
parts as six real Gaussian coordinates with covariance `A(k)^-1`.  Then

\[
 C_N\longrightarrow C_\infty<\infty,
 \qquad
 \frac{D_N}{N}\longrightarrow\delta_{\rm cube}I_3,
\]

\[
 \delta_{\rm cube}
 =\frac{I_{\rm cube}}{6\pi^2YL},\qquad
 I_{\rm cube}=\int_{[-1,1]^3}\frac{dx}{|x|^2}
 =15.348248444887457\ldots .
\]

At the production values `L=16`, `Y=1`,

```text
delta_cube = 0.01619898645075695.
```

For `m_A=Psi^dagger T_A Psi`, `q_A=m_A/(rho+eps_rho)`,
`J_A=grad m_A`, and `K_A=J_A-q_A grad rho`, value and derivative at one
point are independent under the symmetric cutoff.  Conditional Gaussian
contraction gives exact formulas for `E|J_A|^2`, `E J_A.K_A`, and
`E|K_A|^2`.  With

\[
 a=\frac{c_{JJ}\alpha_X^2}{M_X^2+\varepsilon_M},\quad
 b=\frac{c_{JK}\alpha_X\beta_X}{M_X^2+\varepsilon_M},\quad
 c=\frac{c_{KK}\beta_X^2}{M_X^2+\varepsilon_M},
\]

the derivative-pair contraction is

\[
 \mathbb E[e_{{\rm II},N}(x)\mid\Psi_N(x)]
 =\delta_{\rm cube}N\,W_{\varepsilon}(\Psi_N(x))+o(N),
\]

where, writing `s=|Psi_1|^2+|Psi_2|^2` and `rho=|Psi|^2`,

\[
 W_\varepsilon
 =9(a+2b+c)s
 -\frac{6b s^2}{\rho+\varepsilon_\rho}
 -\frac{3c s^2(\rho+2\varepsilon_\rho)}
              {(\rho+\varepsilon_\rho)^2}.
\]

The pinned coefficient matrix `[[a,b],[b,c]]` has eigenvalues
`0.0012590115009260615` and `0.005584738499072227`, so the contraction is
nonnegative and strictly positive on an open set.  Consequently

\[
 \mathbb E F_{{\rm II},N}/N\longrightarrow\kappa_{\rm II}>0.
\]

Thus the unrenormalised positive Class-II energy is not uniformly bounded in
`L1` under the canonical Gaussian reference.  A scalar vacuum constant cannot
cancel the nonconstant, orientation-dependent local contraction
`delta_cube*N*W_eps(Psi)`.  Subtracting that term is the first counterterm
candidate for a nondegenerate full-component limit at fixed low-order
parameters.  This result does not prove that subtraction is necessary for
every possible weak limit: an unmodified sequence could instead collapse onto
the zero set of `W_eps`.  The existing family mass plus `rho^2/rho^3` parameter
family does not absorb the two rational terms when `b` or `c` is active.

The primary high-cutoff evaluation gives the non-interval diagnostic

```text
E F_II,N / (V N) ~= 0.000542394795319287.
```

The independent cutoff increment gives `0.000544664650759017`; the two
implementations agree at common cutoff `N=64` to relative error
`0.00180614`.  These decimal slopes are numerical diagnostics, not physical
predictions or rigorous enclosures of the `C_infinity` expectation.

## What the result decides

The A4 scalar bounded-density/dominated-convergence construction cannot be
copied unchanged to the full derivative Class-II functional.  Any
nondegenerate three-component construction must control the field-dependent
linear contraction, either through a counterterm or through a separately
proved cutoff-concentration mechanism.  The subtraction is a candidate route,
not a theorem that every weak limit requires it.  This is an obstruction to
the unchanged A4 proof route, not a no-go theorem for a bare degenerate or
renormalised measure.

The power-counting degree for a graph with `V_D` two-derivative Class-II
vertices, `V_0` local-potential vertices, and `I` internal lines is

\[
 \omega=3L+2V_D-4I=3-I-V_D-3V_0.
\]

This leaves the one-vertex differentiated contraction as the leading primitive
candidate and makes a fixed-floor rational-counterterm construction plausible;
finite counterterm closure has not yet been proved.

## Composite-definition boundary

The `q^-4` Gaussian has spatial regularity below one half derivative.  The
continuous composites `m_A` and `rho` have distributional derivatives, but

\[
 K_A=(\rho+\varepsilon_\rho)
     \nabla\left(\frac{m_A}{\rho+\varepsilon_\rho}\right)
\]

is at the marginal product boundary `C^alpha * C^(alpha-1)` with
`alpha<1/2`.  Therefore cutoff convergence and scheme independence of `K_A`
itself require a separate lift/construction.  This is registered as
`A6-CLASSII-K-COMPOSITE-DEFINITION`.

## Dependencies and gates

- Hard dependencies: `A1-KERNEL-IDENTITY`,
  `A1-PRODUCTION-FUNCTIONAL-REALISATION`.
- Soft dependencies: `A3-UV-SUPERRENORMALISABILITY`,
  `A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE`, `A5-SECTOR-A-SYNTHESIS`.
- Open gates: `A6-CLASSII-COUNTERTERM-CLOSURE`,
  `A6-CLASSII-K-COMPOSITE-DEFINITION`.

## Reproduction

```powershell
python codes/foundations/a6_classii_uv_power_counting_verify.py
```

Expected:

```text
PASS: primary (19/19)
PASS: independent (12/12)
ASSERTS: 44/44
A6-CLASSII-UV-POWER-COUNTING-INTEGRATED-PASS
```

Evidence is written under
`claims/A6-CLASSII-UV-POWER-COUNTING/runs/2026-07-20-*`.

## Devil's-advocate record

1. **"The complex covariance is `A^-1`, so the coefficient is smaller by a
   factor two."** DISMISSED for the declared convention.  The canonical
   quadratic energy is one half of the six-real quadratic form; each real
   coordinate has covariance `A^-1`, hence the complex covariance is
   `2 A^-1`.  The manifest and integrated verifier fail closed on this factor.
2. **"A fitted line was promoted to an asymptotic theorem."** DISMISSED.  The
   exponent and `delta_cube` follow from the exact symbol expansion and a cube
   Riemann-sum limit.  Finite-cutoff rows only check that theorem.  The full
   decimal Class-II slope remains explicitly non-interval diagnostic evidence.
3. **"The positive density floor removes the UV problem."** UPHELD as false.
   The floor controls the denominator at `rho=0`; the universal derivative
   covariance slope is independent of it.
4. **"Divergent mean energy proves that no Gibbs measure exists."** UPHELD as
   false.  It rules out the unmodified A4 `L1` argument and identifies a
   field-dependent contraction.  A bare sequence could concentrate on the
   zero set `W_eps=0`; singular, degenerate, renormalised, or cutoff-dependent
   measures are not excluded.
5. **"Subtracting the expectation as a vacuum constant is sufficient."**
   UPHELD as false.  `W_eps(Psi)` takes different positive values on explicit
   fields; the leading contraction is field dependent and includes rational
   orientation terms absent from the current local-potential family.
6. **"The `J_A` calculation automatically defines `K_A` in the continuum."**
   UPHELD as false.  `K_A` is a marginal rough product and has its own named
   composite-definition gate.
7. **"Family and lock masses change the linear exponent."** DISMISSED.  They
   change `C_infinity` and the finite coefficient, while
   `A(k)^-1=(Y|k|^4)^-1 I+O(|k|^-6)` fixes the universal exponent and cube
   coefficient.
8. **"The legacy Class-II guarded quotient is the same object."** UPHELD as
   false.  This claim concerns the derivative `J/K` energy only; solver
   convergence/rejection diagnostics are outside scope.

## Quantitative sanity checks

- `I_cube` is reconstructed by two-dimensional surface quadrature and an
  independent one-dimensional integral; they agree to floating precision.
- Direct cube enumeration and FFT multiplicity convolution agree through the
  integrated comparison.
- At `N=128`, the three eigenvalues of `D_N/N` lie between
  `0.0163072859843` and `0.0163866362110`, converging toward
  `0.0161989864508`.
- Tensor Gauss-Hermite and fixed-seed Monte Carlo Class-II expectations agree
  at `N=64` within `0.181%`.
- The full-production shell mass is independently reconstructed as
  `0.260000000009475` and is separated from the scalar `0.005` anchor.

## Falsifier

The result is falsified by an incorrect Gaussian factor, generator
normalisation, Fourier/per-volume factor, a failure of `D_N/N` to approach the
positive cube coefficient, a vanishing or negative pinned contraction, a
primary/independent mismatch outside the declared tolerances, or a source-hash
failure.

## No-overclaim

This T4 result does not construct a renormalised composite, prove finite
counterterm sufficiency, establish stability/tightness or a Gibbs measure,
classify a possible bare concentration limit, prove that a counterterm is
necessary for every weak limit, remove either regulariser, prove regulator
independence, take infinite volume, establish a phase transition or BCC state,
or justify T5/T6/T7.

## Next required action

Obtain an independent operator run, then construct a regulator-independent
`K_A` composite and test whether the symmetry-preserving rational
`W_eps` subtraction closes the fixed-floor counterterm family with a uniform
lower bound.
