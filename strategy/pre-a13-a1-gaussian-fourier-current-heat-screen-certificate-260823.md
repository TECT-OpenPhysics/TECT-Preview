# A1 diagonal-Gaussian Fourier current and heat-rate screen

## Status and scope

This is an exploration-level, claim-nonbearing finite screen.  It uses the
hash-pinned A1 three-generator backend profile but replaces the unknown full
production Gibbs covariance by the explicit diagonal proxy

\[
\gamma_n=(1+|n|^2)^{-2},\qquad n\in\mathbb Z^3.
\]

The proxy has the fourth-order ultraviolet decay of the A1 Brazovskii kernel;
it is not the full A1 Gibbs law and it does not select the missing A13 heat
generator.

## Exact current convolution

Write the first two field components as

\[
u(x)=\sum_p a_p e^{ipx},\qquad v(x)=\sum_q b_q e^{iqx}.
\]

For output frequency \(r=q-p\), define

\[
C_r=\sum_p\overline{a_p}b_{p+r},\quad
D_r=\sum_p\overline{b_p}a_{p+r},\quad
E_r=\sum_p(\overline{a_p}a_{p+r}-\overline{b_p}b_{p+r}).
\]

The registered generators give, for each spatial derivative direction,

\[
\widehat J_{1,r}=ir(C_r+D_r),\quad
\widehat J_{2,r}=r(C_r-D_r),\quad
\widehat J_{3,r}=irE_r.
\]

Under independent centered equal-covariance Gaussian roots and \(r\ne0\),
\(\mathbb E|C_r|^2=\mathbb E|D_r|^2=S_r\) and
\(\mathbb E|E_r|^2=2S_r\), where

\[
S_r=\sum_p\gamma_p\gamma_{p+r}.
\]

Summing the three generators and the spatial directions therefore gives the
exact diagonal-Gaussian proxy spectrum

\[
\mathbb E\sum_{A,i}|\widehat J_{A,i}(r)|^2=6|r|^2S_r.
\]

The factor six is not a rootwise allocation: it is the post-convolution,
coherent output owner.

## UV consequence and heat-rate test

Because \(\gamma\in\ell^1(\mathbb Z^3)\) and has a fourth-order tail, the
convolution retains fourth-order tail order,
\(S_r=O(\langle r\rangle^{-4})\), not fifth-order order.  Thus the current
spectrum is \(O(\langle r\rangle^{-2})\) before heat.  A finite proxy charge

\[
Q_N(s)=\sum_{0\ne r\in[-N,N]^3}
 \frac{6|r|^2S_{N,r}}{1+(1+|r|^2)^{s/2}}
\]

is exactly evaluated for \(s=0,2,4\) and \(N=1,\ldots,5\).  The unweighted
screen grows strictly over the registered cutoffs.  The quadratic and quartic
heat screens are smaller and numerically stable over this finite test.  The
finite table is evidence for a load-bearing heat-rate hypothesis, not a proof
of a cutoff-uniform production ledger.

## Adversarial boundary

The calculation does not identify the A1 production heat/root filtration,
conditional replicas, spatial raw-current intertwiner, complement/low/forest/
returned-mean placement, or a once-owned nonnegative \(q_k\) family.  It does
not promote a diagonal Gaussian proxy to the interacting Class-II measure,
and it gives no thermodynamic, continuum, real-time, physical-empty,
Sector-A, Pre-A, or A13 closure.  The unchanged R-192 owner order must reject
this screen as a substitute for those missing fields.

## Reproduction

Run the primary and independent scripts followed by the integrated verifier in
the pinned TECT virtual environment.  The verifier checks exact Fraction
agreement, the A1 backend hash, coherent output factor, finite heat ordering,
and all non-claim-bearing boundary tokens.  No PDF is issued for this local
screen.
