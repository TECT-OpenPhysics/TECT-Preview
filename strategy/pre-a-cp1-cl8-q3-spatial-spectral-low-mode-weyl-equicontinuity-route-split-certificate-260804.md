# Pre-A CP1/CL8 Q3 spatial-spectral low-mode Weyl equicontinuity

**Candidate:** `PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-LOW-MODE-WEYL-EQUICONTINUITY-ROUTE-SPLIT-v0`  
**Result:** `PA-CP1-CL8-Q3-RENORMALIZED-FORCE-VIRIAL-BOUND-AND-REGULAR-WEYL-CLUSTERS-WITH-FULL-SEQUENCE-SEAM-GATE`  
**Exploration:** `EXP-000771`
**Authority:** claim-nonbearing T0 theorem for the fixed-beta spatial-spectral Q3 comparator

## 1. Result

The spatial-spectral Q3 comparator already has a common periodic Gaussian
space and normalized densities `r_K` satisfying

\[
 \sup_K\|r_K\|_{L^2(\mu)}\leq
 \{\mathbb E_\mu e^{2R}\}^{1/2}<\infty.                 \tag{1.1}
\]

For every smooth real eight-component label `f` contained in one fixed
spatial Fourier band, this certificate proves

\[
 \sup_K\omega_K(P_K(f)^2)<\infty.                        \tag{1.2}
\]

It uses the exact renormalized Q3 force and a Gibbs virial identity, not the
ultraviolet-sensitive total energy.  Consequently the twisted heat-kernel
seams are uniformly continuous at zero on every fixed finite mode space and
all pointwise cofinal Weyl clusters are regular states.

This does not prove a unique or full-sequence seam limit.  It also does not
yet transfer (1.2) to the centered-nodal CL8 family.

## 2. Exact Q3 force

Write

\[
 P_{\rm int}(x)={1\over2}x^T K_{\rm int}x
 +{g\over4}\sum_e x_e^4
 +{\lambda\over4}\sum_{e\sim r}(x_e-x_r)^2(x_e^2+x_r^2). \tag{2.1}
\]

Wick differentiation commutes with ordinary differentiation.  For one cube
vertex `e`, which has three neighbours,

\[
 \begin{split}
 \partial_e:P_{\rm int}:_C={}&(K_{\rm int}x)_e+g:x_e^3:_C\\
 &+{\lambda\over2}\sum_{r\sim e}
 [2:x_e^3:_C-3:x_e^2x_r:_C+2:x_ex_r^2:_C-:x_r^3:_C].
                                                               \tag{2.2}
 \end{split}
\]

The factor `1/2` and the final minus sign are mutation sentinels.  The total
own-cubic coefficient is `g+3 lambda`.

At time zero the free covariance has Fourier coefficients of order
`1/(1+|k|)`.  The partial Fourier sums therefore have the uniform logarithmic
majorant

\[
 |C_K^0(x)|\leq C\{1+|\log|2\sin(x/2)||\},               \tag{2.3}
\]

and are uniformly bounded in every finite `Lp`, although `C_K^0(0)` diverges.
For the third-chaos part `N_K(f)` of the force, Wick isometry gives

\[
 \mathbb E|N_K(f)|^2
 \leq 6T_{Q3}(g,\lambda)^2\|f\|_2^2\|C_K^0\|_3^3.       \tag{2.4}
\]

The linear chaos is uniformly bounded for fixed smooth `f`.  Orthogonality
of chaos orders and degree-three hypercontractivity then yield

\[
 B_f:=\sup_K\|G_K(f)\|_{L^4(\mu)}<\infty.                \tag{2.5}
\]

Expanding `:x^3:_C=x^3-3C_K(0)x` and bounding the two raw terms separately
would destroy the estimate.  Equation (2.2) must be retained as a Wick
chaos.

## 3. Virial identity without total ultraviolet energy

Restore the canonical units by

\[
 H_K={P^2\over2\chi}+U_K(Q),\qquad[Q_i,P_j]=i\hbar\delta_{ij}. \tag{3.1}
\]

For `Q_f=Q_K(f)`, `P_f=P_K(f)`, `G_f=D_fU_K`, and
`A_f=(Q_fP_f+P_fQ_f)/2`, direct commutation on the polynomial Schwartz core
gives

\[
 [H_K,Q_f]=-{i\hbar\over\chi}P_f,
 \qquad [H_K,P_f]=i\hbar G_f,                              \tag{3.2}
\]

\[
 [H_K,A_f]=i\hbar\left(Q_fG_f-{P_f^2\over\chi}\right).   \tag{3.3}
\]

Polynomial confinement and heat smoothing justify spectral truncation and
removal in the Gibbs trace.  Trace cyclicity in (3.3) proves

\[
 \boxed{\omega_K(P_f^2)=\chi\,\omega_K(Q_fG_f)}.          \tag{3.4}
\]

The Feynman-Kac time-zero multiplication identity and Holder give

\[
 0\leq\omega_K(P_f^2)
 \leq\chi\|r_K\|_2\|Q_f\|_4\|G_f\|_4
 \leq\chi R_2A_fB_f.                                     \tag{3.5}
\]

On a fixed finite-dimensional smooth label space, `A_f` and `B_f` are bounded
linearly in the label norm.  No uniform bound on `omega_K(H_K)` occurs.

## 4. Twisted seam and regular Weyl clusters

The exact positive heat-kernel seam mass is

\[
 m_K(h)={1\over Z_K}\int K_{K,\beta_0}(x+h/2,x-h/2)dx
       =\omega_K(e^{iP_K(h)/\hbar}).                       \tag{4.1}
\]

It is real by time reversal, positive by kernel positivity, and at most one
by unitarity.  Hence

\[
 0\leq1-m_K(th)
 \leq {t^2\over2\hbar^2}\omega_K(P_K(h)^2),              \tag{4.2}
\]

uniformly on bounded subsets of every fixed label space.  Semigroup
Cauchy-Schwarz also gives the pointwise midpoint domination

\[
 D_{K,h}(x)\leq{D_{K,0}(x+h/2)+D_{K,0}(x-h/2)\over2}.     \tag{4.3}
\]

Together with the registered configuration bounds and the Weyl product,
(4.2) proves identity equicontinuity.  Finite Weyl positive-type matrices
pass to every cofinal pointwise cluster; identity continuity makes each
cluster regular.  A diagonal argument supplies a compatible regular state on
the inductive finite-mode Weyl algebra.

## 5. Exact remaining gate

The periodic density convergence of EXP-000769 is the diagonal `h=0` sector.
A momentum translation changes the heat-kernel boundary condition.  The
present theorem controls the seam near zero but does not identify its value at
fixed nonzero `h` along the full sequence.

A sufficient successor must prove locally uniform Cauchy convergence of the
projected off-diagonal seam measures, or provide common Hilbert embeddings,
Mosco or strong-resolvent convergence of the renormalized forms, convergence
of fixed-low-mode translations, and a trace-ideal step.  Strong semigroup
convergence by itself does not pass changing-Hilbert-space Gibbs traces.

The hostile oscillator family

\[
 H_N={1\over2}(P^2+N^2Q^2),\qquad
 \chi_N(u,v)=\exp[-{1\over4}\coth(\beta N/2)(u^2/N+Nv^2)] \tag{5.1}
\]

has configuration variance tending to zero while every nonzero momentum
characteristic tends to zero.  Thus configuration convergence and positive
heat kernels alone cannot replace (3.5) or full seam convergence.

## 6. Prior-art and scope boundary

Virial identities, Wick isometry, Nelson hypercontractivity, Feynman-Kac
kernels, and Weyl regularity criteria are established mathematics.  The
repository-specific step is the exact non-radial Q3 force calculation and its
composition with the already registered comparator density bound.  This is
not a world-first or novelty proof.

This certificate does not establish the centered-nodal uniform exponential
moment, centered density convergence, or full-sequence off-diagonal seam.  It
does not prove a beta-independent Hamiltonian family, KMS or ground-state
selection, complete OS/Markov/Hadamard structure, the original three-
dimensional Q3 parent, a physical vacuum, energy below empty space, physical
light, C0, N1--N5, C6, CP1, Sector A, or Pre-A.

## 7. Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_low_mode_weyl_equicontinuity_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_low_mode_weyl_equicontinuity_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_spatial_spectral_low_mode_weyl_equicontinuity_route_split_verify.py --self-test
```
