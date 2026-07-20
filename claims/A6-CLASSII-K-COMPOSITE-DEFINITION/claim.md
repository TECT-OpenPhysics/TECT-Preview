# A6-CLASSII-K-COMPOSITE-DEFINITION -- canonical Class-II K current

**Tier**: T5 PINNED-CLOSURE@FIXED-FLOOR-CANONICAL-SPECTRAL-K-LIFT (TSv2) |
**Lifecycle**: ACTIVE |
**Last review**: 2026-07-20

## Result

Let the three-complex-component production Gaussian be realified as
`X:T^3_L -> R^6`.  For an embedded Pauli generator `S_A`, define

$$
\rho=X^T X,\qquad m_A=X^T S_A X,\qquad
q_A={m_A\over \rho+\varepsilon_\rho},
$$

and the one-form

$$
\omega_A=dm_A-q_A,d\rho=(\rho+\varepsilon_\rho)dq_A.
$$

At fixed `rho_regularizer=1e-12`, use one common real-even scalar Fourier
multiplier on all six coordinates, uniformly bounded and converging pointwise
to one, with compact support or a uniform Schwartz tail.  Nonlinear products
are exact convolutions or sufficiently de-aliased.  Then

$$
K_{A,i}^{(\Lambda)}=\omega_A(X_\Lambda)\,\partial_iX_\Lambda
\longrightarrow K_{A,i}
$$

in $L^p(\Omega;\mathcal C^{-1/2-\kappa})$ for every finite $p$ and every
$\kappa>0$.  Sharp cube, sharp ball, and smooth-even regulators therefore
select the same canonical geometric/Stratonovich current.  A dyadic
subsequence converges almost surely.

This is a probabilistic composite, not an ordinary deterministic product.
The one-form is generically non-exact:

$$
d\omega_A={1\over\rho+\varepsilon_\rho},d\rho\wedge dm_A.
$$

Consequently the Gaussian second level is load-bearing.  For the admitted
even regulators,

$$
\mathbb E[X_\Lambda^a\partial_iX_\Lambda^b]
=\partial_iC_\Lambda^{ab}(0)=0,
$$

so `K_A` itself requires no divergent subtraction.  This statement does not
define `J_A*K_A` or `|K_A|^2`.

## Why the limit exists

The production covariance behaves as $|k|^{-4}$, hence
$X\in\mathcal C^{1/2-}$ and $\partial X\in\mathcal C^{-1/2-}$.  Deterministic
Holder multiplication is insufficient.  The only unresolved resonant input
after paralinearising $\omega_A(X)$ is

$$
\mathbb X_i^{ab}=X^a\circ\partial_iX^b.
$$

For comparable Fourier modes, Wick contraction gives

$$
\mathbb E|\widehat{\mathbb X_i^{ab}}(p)|^2
\lesssim
\sum_{k+\ell=p,\ |k|\asymp|\ell|}
\langle k\rangle^{-4}\ell_i^2\langle\ell\rangle^{-4}
\lesssim\langle p\rangle^{-3}.
$$

At fixed output mode the omitted variance is
$\sum_{|k|>\Lambda}O(|k|^{-6})=O(\Lambda^{-3})$.  Dominated convergence makes
the lift common to every admitted multiplier.  First-order
paralinearisation leaves a remainder in $\mathcal C^{2\alpha}$; multiplying
it by $\partial X\in\mathcal C^{\alpha-1}$ is classical once
$\alpha>1/3$.  This reconstructs `K_A` continuously from `(X,mathbb X)`.
The proof note records the full argument and the endpoint exclusions.

This mechanism follows the controlled-distribution construction introduced
by [Gubinelli, Imkeller and Perkowski](https://arxiv.org/abs/1210.2684).
Canonical Gaussian lifts and approximation convergence are consistent with
[Friz and Victoir](https://arxiv.org/abs/0711.0668), while the identification
with symmetric-Stratonovich integration is supported by
[Ohashi and Russo](https://arxiv.org/abs/2206.06865).  The repository proof
specialises the needed Fourier-Wick estimates to the pinned torus covariance.

## Counterterm review -- kept separate from the K definition

For the production Class-II coefficient matrix

$$
Q_{II}=\begin{pmatrix}a&b\\b&c\end{pmatrix}>0,
\qquad s=|\Psi_1|^2+|\Psi_2|^2,
$$

the exact Pauli/Fierz bounds are

$$
9\lambda_{\min}(Q_{II})s\le W_\varepsilon(\Psi)
\le9(a+2b+c)s.
$$

Thus $W_\varepsilon=0$ exactly on the pure-third-component subspace.  But the
literal subtraction

$$
F_N^{\rm naive}=F_{\rm core}+F_{{\rm II},N}
-\delta_{\rm cube}N\int W_\varepsilon
$$

fails as a cutoff-uniform coercivity route.  On a homogeneous field in the
first two components, `J_A=K_A=F_II,N=0`, while the negative counterterm
survives.  The sextic term balances it only at

$$
|\Psi_N|\asymp N^{1/4},\qquad
\inf F_N^{\rm naive}/|\mathbb T^3|\le-cN^{3/2}+O(N).
$$

At the production point,

```text
9 lambda_min(Q_II)                 = 0.0113311035083346
w_infinity                         = 0.0770624999999807
|Psi_N| / N^(1/4)                  -> 0.198135127774404
inf energy density / N^(3/2)       -> -3.26710156480221e-05
```

A vacuum-energy recentering cannot prevent the minimising amplitude from
escaping.  A running family mass can restore nonnegativity, but it also tends
to force the first two components to zero; that is a new renormalisation
condition, not closure of the original route.  The counterterm gate therefore
remains open.

## Bare concentration review -- local results only

Two different local proxies can be solved exactly.  Put
$t=\delta_{\rm cube}N$, $z=(\Psi_1,\Psi_2)\in\mathbb C^2$,
$g=a+2b+c$, and $h=9g$.

For the mean-contraction proxy with density proportional to
$e^{-tW_\varepsilon}$,

$$
t|z|^2\Longrightarrow {\rm Gamma}(2,{\rm rate}=h),
\qquad \mathbb E[N|z|^2]\longrightarrow {2\over\delta_{\rm cube}h}
=1294.94082886623.
$$

If the exact local Gaussian derivatives are integrated first, the limiting
factor is $(1+2g|y|^2)^{-9/2}$ and

$$
f_R(r)=35g^2r(1+2gr)^{-9/2},\qquad
\mathbb E[N|z|^2]\longrightarrow {2\over3\delta_{\rm cube}g}
=3884.82248659868.
$$

The unequal constants prove that these proxies must not be identified.  Both
support concentration toward `Psi_1=Psi_2=0`, but neither includes spatial
correlations, Fourier-mode entropy, the rational mode coupling, or tightness
of the third component.  Full-field bare concentration is a separate open
gate.

## Reproduction

```powershell
python codes/foundations/a6_classii_k_composite_verify.py
```

The current package reports primary `29/29`, non-importing independent
`16/16`, and aggregate `64/64` PASS.  The direct area variance tails are
approximately `N^-3` in all three admitted schemes.  A deliberately
component-split asymmetric $q^{-4}$ regulator gives a nonzero stable area
anomaly, demonstrating that the admitted symmetry class is necessary.

## Devil's-advocate

1. **VALID-with-mitigation -- deterministic Holder power counting alone does
   not prove divergence or ambiguity.**  The claim uses the special Gaussian
   second-level summability and horizontal one-form structure.  The older A6
   wording is corrected from a bare marginal-product diagnosis to this
   probabilistic construction.
2. **DISMISSED -- the rational denominator could introduce a new K-level
   divergence.**  Fixed positive `eps_rho` makes the one-form smooth with all
   required Gaussian moments.  The only resonant input is the canonical
   second level, whose local contraction is zero for common-even regulators.
3. **VALID-with-mitigation -- regulator independence is not unrestricted.**
   It is claimed only for a common real-even scalar multiplier class.  The
   asymmetric negative control has a finite anomaly and is explicitly outside
   the theorem.
4. **DISMISSED -- defining K automatically defines its square.**  It does not.
   `J*K` and `|K|^2` require their own renormalised products and remain under
   the counterterm gate.
5. **UPHELD -- literal W subtraction is not a stable fixed-parameter
   prescription.**  The homogeneous `-Theta(N^(3/2))` trial falsifies that
   route.  The failure is registered as a no-go rather than hidden by a vacuum
   shift.
6. **VALID-with-mitigation -- W's zero set does not prove bare Gibbs
   concentration.**  Only two local proxy theorems are closed.  The full-field
   entropy/tightness problem is registered separately.
7. **VALID-with-mitigation -- the very small floor may make constants large.**
   The theorem fixes the floor and makes no uniform `eps_rho -> 0` statement.
8. **DISMISSED -- the factor-three convention in W is ambiguous.**  The A6
   source docstring is corrected: the function already returns
   `W=3*sum_A(...)`, and the conditional term is `delta_cube*N*W`.

## History

- 2026-07-20: entered directly at scoped T5 as a one-shot fixed-floor
  Fourier-Wick/paracontrolled closure with hash-pinned dual reproduction.
  Counterterm closure and full-field bare concentration remain separate.

## No-overclaim boundary

No renormalised Class-II energy or measure, arbitrary-regulator universality,
floor removal, full-field bare concentration, infinite-volume limit, phase
transition, BCC result, T6, or T7 follows from this card.
