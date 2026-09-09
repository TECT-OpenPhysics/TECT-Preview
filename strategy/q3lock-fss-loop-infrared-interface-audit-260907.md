# Q3LOCK FSS-to-loop and infrared interface audit

Date: 2026-09-07. Exploration: EXP-001627. Task: T-054.
Status: T0, claim_bearing=false, conditional finite-mesh/source-limit audit.
The sole Q3LOCK authority remains EXP-000780 -> EXP-000781 -> EXP-000782 / R-497.
This note does not certify the infinite-volume phase theorem or create a PDF.

## Primary finite-dimensional input

The source is J. Fröhlich, B. Simon and T. Spencer, *Infrared Bounds, Phase
Transitions and Continuous Symmetry Breaking*, Commun. Math. Phys. 50,
79--85 (1976), Section 2, Theorem 2.1 and proof pages 81--84:
https://math.caltech.edu/SimonPapers/65.pdf.

The theorem is stated for a periodic rectangular nearest-neighbour lattice,
fixed finite spin dimension, positive dot-product coupling, and a common
single-site measure with all positive quadratic exponential moments.  It does
not require radiality or a phase conclusion.  The Q3LOCK use is only this
finite-mesh Gaussian-domination inequality.

## Exact Q3LOCK map

At fixed even spatial size `L` and time mesh `N`, put
`s_y=(sqrt(epsilon) x_{y,k})_{k,e}` in `R^(8N)`.  After allocating the
positive spatial diagonal `3c |x|^2` to the one-site prior, the action is

`sum_y V_N(s_y) - c sum_{<y,z>} s_y dot s_z`.

The prior is common at every site and has a positive quartic lower bound,
which gives all quadratic exponential moments for each fixed `N`.  The
FSS source is not the vertex norm.  For a real zero-sum spatial field `f`,

`eta_y(t)=t sqrt(epsilon) (f_y u)_k`,
`h_t=G L_sp^{-1} eta(t)`, and `B h_t=eta(t)`.

The exact edge energy is

`||h_t||^2 = beta t^2 <f,L_sp^{-1}f>`.

The source pairing is exactly `t X_{N,L}(f)`, and the theorem with coupling
`J=c` therefore gives

`E exp(t X_{N,L}(f)) <= exp(beta <f,L_sp^{-1}f> t^2/(2c))`.

The constant is dimension-independent; no uniform bound on the prior's
moments as `N` grows is imported.

## Passage order and uniform integrability

The cyclic polygonal interpolation is order-preserving and satisfies the
exact identity `X_L(f)(I_N x)=X_{N,L}(f)`.  At fixed `L,beta,f`, the already
separate interacting weak-limit argument gives `mu_{N,L,0} => mu_{L,0}` on
the finite-volume loop sup-norm space.  For every real `t` and cutoff `R`,
`min(exp(t X_L),R)` is bounded and continuous.  Weak convergence followed by
monotone convergence transfers the MGF inequality to the continuous loop
law without assuming convergence of an unbounded expectation first.

The two signs imply

`sup_N E exp(T |X_{N,L}|) <= 2 exp(K_L(f) T^2)`.

The elementary series bound
`|x|^(2k) exp(2T|x|) <= (2k)! a^(-2k) exp((2T+a)|x|)`
then supplies uniform integrability for the source derivatives and second
moments.  This is a fixed-volume statement; it gives no spatially uniform
constant-mode control.

## Duhamel and infrared boundary

Time translation gives
`Var(X_L(f))=beta^2 <f,D_L f>`.  Differentiating the finite MGF bound at
zero gives
`<f,D_L f> <= (beta c)^(-1) <f,L_sp^{-1}f>`.

The spatial Laplacian has eigenvalue `2 E(p)` with
`E(p)=sum_j(1-cos p_j)`.  Thus the nonzero modes satisfy
`Dhat_L(p)<=1/(2 beta c E(p))`.  The inverse is used only on the zero-sum
subspace; the constant mode is never inverted.  The three-dimensional shell
estimate is a separate Riemann-sum argument and yields the finite singular
integral `I_3` before the `L -> infinity` limit.

## Adversarial boundary checks

1. Replacing the edge Poisson norm by `||eta||^2` gives the wrong spatial
   inverse and fails the source normalization.
2. Importing a prior moment bound uniform in `N` is invalid; the FSS constant
   is dimension-independent, while the prior constants are not claimed to be.
3. Passing `exp(tX)` directly through weak convergence is invalid; bounded
   truncation and the two-sided exponential UI estimate are required.
4. The FSS inequality does not bound the spatial constant mode.  The zero mode
   is subtracted before the infrared sum is combined with the separate local
   Falk--Bruch lower bound.
5. The source theorem's Theorems 2.2--2.3 are comparators only; the manuscript
   derives the Duhamel and Fourier consequences with its own normalization.

## Remaining acceptance boundary

The finite-mesh hypothesis map, source typing, factors of `epsilon`, `beta`,
`c`, and the fixed-volume loop/UI order are internally consistent.  Independent
review is still required for the actual FSS theorem invocation, the interacting
weak-limit argument, and the passage from the loop covariance to the
thermodynamic infrared bound.  No strict zero-mode lower bound or phase
coexistence conclusion follows from this audit alone.

No theorem tier, claim-bearing status, priority, novelty, publication
readiness, KMS dynamics, ground-state gap, continuum limit, physical vacuum,
C6, CP1, or Sector A conclusion changes.
