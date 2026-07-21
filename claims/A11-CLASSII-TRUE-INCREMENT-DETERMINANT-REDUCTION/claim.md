# A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION -- exact action successor

**Tier**: T4 PROVED-STRUCTURAL-REDUCTION@FIXED-FLOOR-FINITE-CUTOFF
(TSv2) | **Lifecycle**: ACTIVE | **Last review**: 2026-07-21

## Result

For the hash-pinned A1 production Gaussian and the A7--A10 sharp-cube
filtration, the direct A10 candidate

\[
\mathbb E_\nu E_J\le \alpha_dH(\nu\mid\gamma_J)
+\epsilon_d\mathbb E_\nu\|\phi_J\|_6^6
+K_d\mathbb E_\nu\|\phi_J\|_4^4+C_d
\]

is false for any cutoff-independent constants.  At the base Gaussian,
(H(\gamma_J\mid\gamma_J)=0), the terminal fourth and sixth moments are
uniformly bounded, but

\[
\frac{\mathbb E_{\gamma_J}E_J}{L^3 2^J}
\longrightarrow \kappa_{\rm II}>0.
\]

This route is registered as
`F-2026-07-21-A10-PAST-ENERGY-UPPER-FORM`.

The exact replacement is

\[
I_j:=Q_j^{\rm fr}-q_{B(\phi_{j-1})}(D\phi_{j-1}).
\]

With (phi_0=0), (Gamma_{\le0}=0), and (V_0=0),

\[
I_j+\mathcal C_j=V_j-V_{j-1},
\qquad
V_J=\sum_{j\le J}(I_j+\mathcal C_j).
\]

Condition on the past and set

\[
A_j=M_{B(x_j)}^{1/2}G_j,
\quad r_j=M_{B(x_j)}^{1/2}Dx_j,
\quad T_j=A_j^*A_j,
\quad \ell_j=A_j^*r_j.
\]

Then

\[
I_j=\frac12\{\langle\xi_j,T_j\xi_j\rangle-\operatorname{Tr}T_j\}
+\langle\ell_j,\xi_j\rangle
\]

and, for (p>0),

\[
\log\mathbb E_j e^{-pI_j}
=\frac12\{p\operatorname{Tr}T_j-\log\det(I+pT_j)\}
+\frac{p^2}{2}
\langle\ell_j,(I+pT_j)^{-1}\ell_j\rangle.
\]

Consequently,

\[
\log\mathbb E_j e^{-pI_j}
\le \frac{p^2}{4}\|T_j\|_{\mathfrak S_2}^2
+\frac{p^2}{2}\|\ell_j\|^2.
\]

The source-square has positive sign and cannot be removed.  In one dimension
with (T=\tau>0), (ell=\sqrt\tau q), it equals

\[
\frac{p^2\tau q^2}{2(1+p\tau)},
\]

which diverges for fixed (|T|_{\mathfrak S_2}) as (|q|\to\infty).
Therefore a Hilbert--Schmidt-only continuation of A9 is impossible.

## Executable evidence

The primary audit recomputes the Class-II UV ladder, exact endpoint Gaussian
moments, a genuine three-component spectral telescope, and a deterministic
two-dimensional Gaussian determinant.  It passes 24/24 assertions and finds

\[
\kappa_{\rm II}=0.000542469581748385,
\qquad
\frac{\sum_{N<64}e_N}{64}=0.000506948292202567.
\]

The non-importing independent audit directly enumerates cube modes and all
three Pauli current contractions.  It passes 18/18 assertions and finds

\[
\kappa_{\rm II}=0.000540500145647357.
\]

The integrated verifier passes 58/58 assertions, pins every authority hash,
and checks the proof PDF contract.

## Proof order

1. The direct past-energy upper-form route is refuted and retired.
2. The true-increment telescope and determinant are now closed.
3. Prove `A11-CLASSII-ADAPTED-SOURCE-SQUARE-BOUND`:

   \[
   \sum_j\|G_j^*B(P_{\le j-1}\phi)D P_{\le j-1}\phi\|_2^2
   \le C_{\rm src}\|\phi\|_6^6.
   \]

4. Prove `A11-CLASSII-TRUE-INCREMENT-STABILISED-LOG-LAPLACE` for
   (	heta I_j+\mathcal C_j), not for the historical
   (	heta Q_j^{\rm fr}+\mathcal C_j).
5. Recompute the explicit sextic budget and only then reassemble the A7
   Nelson argument.

## Devil's-advocate self-test

1. **DISMISSED -- positive (E_J) helps the endpoint lower bound.**  The
   actual endpoint is the shell sum minus (E_J); the sign is adverse.  The
   base-Gaussian asymptotic proves that it cannot be absorbed as proposed.
2. **VALID WITH MITIGATION -- a boundary term is hidden at the first scale.**
   The theorem explicitly fixes (phi_0=0), (Gamma_{\le0}=0), and
   (V_0=0).  Any other initial scale must retain (V_0).
3. **DISMISSED -- the determinant source has negative sign.**  Completing
   the square gives the positive term above; both executable routes verify
   it by deterministic quadrature.
4. **UPHELD -- A10's individual (L^4) projector estimate closes the new
   source sum.**  It does not.  A genuine cutoff-uniform (L^6)
   vector-valued or multilinear sharp-cube theorem is still required.
5. **UPHELD -- rational (B(P_{\le j}\phi)) is band-limited.**  It is not.
   The positive floor removes a singularity but does not create polynomial
   Fourier support.
6. **UPHELD -- the historical relative variable can be reused.**  It differs
   from the required variable by
   (	heta q_{B(x_j)}(Dx_j)), exactly the refuted past-energy term.
7. **UPHELD as an overclaim -- this closes A7 or establishes T5/T6.**  It
   closes only a scoped T4 structural reduction.  The two named analytic
   gates remain open; no interacting measure or higher-tier closure follows.

## Reproduction

```powershell
C:\Users\jtkor\AppData\Local\Programs\Python\Python312\python.exe codes/foundations/a11_classii_true_increment_determinant_verify.py
```

Expected terminal lines:

```text
PASS: primary (24/24)
PASS: independent (18/18)
ASSERTS: 58/58
A11-CLASSII-TRUE-INCREMENT-INTEGRATED-PASS
```

## Boundary

This claim does not prove the adapted source-square estimate, the new
stabilised relative log-Laplace estimate, a positive remaining production
sextic budget, the A7 Nelson bound, an interacting full three-component Gibbs
measure, regulator or floor removal, infinite volume, a phase transition,
BCC existence or selection, T5, T6, or T7.
