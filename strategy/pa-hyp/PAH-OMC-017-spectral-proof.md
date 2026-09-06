# PAH-OMC-017: spectral argument and applicability audit

Companion to `PAH-OMC-017-transfer-certificate.md`. The latter proves the
exact Gibbs factorization, Hilbert-Schmidt property, positivity improving
and positive spectral radius used here. No extra model hypothesis is added.

## Literature-first applicability

Bounded search: PAH-001, OMC-004/016 and R-509; external queries for
Jentzsch/positive compact integral operators, weak Krein-Rutman,
non-self-adjoint compact spectral theory and the spectral-radius formula.
Q3LOCK transfer records and self-adjoint-only formalizations were found but
are NOT inputs. This is standard transfer-operator methodology, not a claim
to a new general spectral theorem or a world-first research result.

The intended imports, primary locators and crosswalks are:

1. J. Lu and Y. Lu, *A priori generalization error analysis of two-layer
   neural networks for solving high dimensional Schrodinger eigenvalue
   problems*, Communications of the AMS 2 (2022), Theorem 5.2, printed p.16,
   DOI 10.1090/cams/5. Primary paper:
   https://par.nsf.gov/servlets/purl/10324294
   Retrieved 2026-09-06; PDF SHA-256
   `eb8849c6d9a29a6206cae58ac8e5505f8773f00ee40572f89018f9d472d8be67`.
   Use ONLY the abstract weak Krein-Rutman theorem: positive right and
   dual eigenvectors exist at the positive spectral radius of a compact
   positive operator on a Banach space with a total cone. SATISFIED: real
   L2 is Banach; its nonnegative cone is closed and reproducing by positive
   and negative parts; K is positive and compact by the product envelope;
   r(K)>=256 exp(-319/12)>0. Disposition APPLIES. No PDE, quantum or
   neural-network result is imported. Theorem 5.3 of that paper requires a
   solid cone; this L2 positive cone has empty interior, so its strong
   version DOES-NOT-APPLY. The same distinction appears in Y. Du's chapter
   *Krein-Rutman Theorem and the Principal Eigenvalue*, Theorems 1.1/1.2,
   hosted at https://people.math.ethz.ch/~grsam/HS16/NumPDE/Extras/krein_rutman.pdf .
2. J. Schenker, *Functional Analysis Lecture Notes*, Michigan State,
   Lecture 32 Theorem 32.1, printed 32-1, PDF page 150:
   https://users.math.msu.edu/users/schenke6/920/920notes.pdf
   Retrieved 2026-09-06; PDF SHA-256
   `cc1a31ec17a90cdb6c35b41faf7f0582656de75e5e651b58debdd2858a0ef82e`.
   Import only the discreteness and finite multiplicity of nonzero compact
   spectra, with possible accumulation only at zero. SATISFIED: the
   complexification of H is a complex Banach space and the same K is
   compact. Disposition APPLIES. No orthogonal eigenbasis or normality is
   assumed. Theorem 31.4 also applies to the adjoint, already covered by
   the explicit transpose-kernel bound here.
3. T. O. Sorensen, LMU Functional Analysis 2, winter 2011/12, November 14
   lecture on the bounded-operator spectral-radius formula:
   https://www.mathematik.uni-muenchen.de/~sorensen/Lehre/WiSe2011-12/content-FA2-WS11-12.html .
   Retrieved 2026-09-06. SATISFIED: bounded operator on a Banach space.
   Disposition APPLIES: use r(A)=lim ||A^k||^(1/k), not ||A||=r(A).
   The needed estimate also follows from the resolvent proof below.
4. R-509: APPLIES only to its exact fixed-n dr Gibbs state and n-uniform
   bounded-witness/moment estimates. Preregistration verifies identity of
   functional, all labels, reference, couplings, boundary, amplitude
   observables and j-before-n order. Its theorem does not imply Cauchy
   convergence; that is the new residual proposition proved here.

The imports' hypotheses are discharged analytically, not by checking that
their names occur in JSON. Executable lanes check source fingerprints and
model-specific algebra; they do not independently prove the imported
functional analysis. Lean is a limited exact-algebra bridge, not full
formalization. No T6/T7 or physical claim promotion is made.

## Weak eigenvector existence to simple leading eigenvalue

Write lambda=r(K)>0. Weak Krein-Rutman gives K phi=lambda phi and
K*psi=lambda psi with nonzero nonnegative phi,psi. Positivity improving
makes both strictly positive almost everywhere. Normalize ||phi||_2=1
and <psi,phi>=1; the latter pairing is finite and positive.

Let Kw=z w with w complex, nonzero and |z|=lambda. The integral triangle
inequality gives K|w|>=|Kw|=lambda|w|. Pair the nonnegative difference
with psi. Its integral is zero, hence it vanishes a.e. Equality for one
row with strictly positive kernel forces w to have a constant complex
phase: rotate the row integral to be positive real and integrate the
nonnegative function K(x,y)(|w(y)|-Re w(y)). A zero integral makes this
function zero a.e. The row integral is nonzero because K|w|>0. Thus
w=c|w| for one unit complex c, and necessarily z=lambda.

In particular every real leading eigenvector has constant sign. If two
positive ones were not proportional, their ratio would not be essentially
constant; choose a number between two essential ratio values to obtain a
sign-changing real leading eigenvector, a contradiction. Real/imaginary
parts prove the complex eigenspace is also one-dimensional. There is no
generalized vector (K-lambda I)v=c phi with c nonzero: pairing with psi
gives 0=c. Any longer Jordan chain would contain such a length-two chain.
Therefore lambda is algebraically simple, with no other peripheral value.

Let P h=phi<psi,h>. Then P^2=P and KP=PK=lambda P. In the complex space
use the usual sesquilinear pairing; phi,psi are real positive. The closed
complement ker psi is invariant. The direct decomposition span(phi) plus
ker psi shows A=K/lambda-P is zero on span(phi) and the remaining
normalized K on the complement. It is compact. Compact spectral theory
and the absence of competitors at modulus lambda imply s=r(A)<1: a
sequence of remaining spectral values approaching lambda in modulus
would have a nonzero accumulation point, which is impossible.

## Exact operator-defined power constants

Set q=(1+s)/2 in (0,1). Let p be the least integer >=1 satisfying
||A^p||<=q^p; the spectral-radius formula ensures it exists. Set

    C=max(1, ||I-P||, max_(0<=r<p) ||A^r||/q^r).

This is a finite exact expression in the original integral operator, not
a numerical eigenvalue fit. For k=lp+r, submultiplicativity proves
||A^k||<=||A^p||^l ||A^r||<=C q^k. For k>=1 the identity PA=AP=0
gives lambda^(-k)K^k=P+A^k. For k=0 the residual is I-P, NOT A^0.
The separate ||I-P|| entry in C covers that case. Consequently

    ||lambda^(-k)K^k-P||<=C q^k for every k>=0.

Independent analytic reconstruction: on |z|=q the resolvent (zI-A)^(-1)
has finite maximum norm M. The contour integral formula for A^k follows
first from the norm-convergent Neumann series at radius >||A||, and then
by deforming through the resolvent annulus down to q. It yields
||A^k||<=M q^(k+1). This is bounded-operator complex analyticity, not a
self-adjoint spectral calculus. Increasing C covers k=0. Both derivations
give analytic constants with proved existence, not certified numerical
gap intervals or uniformity in changed beta, width or regulator.

## Independent and hostile analytic review

The independent executable reconstructs exact edge/face terms and proof
constants without importing primary code. It tests ratio cross products
rather than inheriting a computed primary difference. The universal
proof is the incidence bijection, positive-kernel argument and normalized
estimate, not extrapolation of finite fixtures. The contour argument
above is a second derivation of power decay. These are INTERNAL independent
reconstructions, not a signed external referee report. External review is
invited on the applicability and strict-kernel steps.

1. Convention/sign: omitting endpoint halves or deleting the terminal
   square changes F. DISMISSED for the exact bijection; hostile mutations
   must be detected. The Gibbs sign stays exp(-F).
2. Domain/regularity: the L2 cone is not solid and K need not be symmetric.
   UPHELD against the strong-form/Rayleigh shortcuts, which are excluded.
   Weak eigenvectors plus strictly positive rows suffice as proved above.
3. Compactness on an unbounded space: DISMISSED by the Hilbert-Schmidt
   product envelope and finite-rank approximation, not a compact cutoff.
4. Positive compact operators may have zero radius. DISMISSED here only
   by the explicit proof-box lower bound; no general false assertion used.
5. Nonnormal norms or Jordan blocks can invalidate naive power estimates.
   DISMISSED by left-pairing exclusion of generalized leading vectors and
   the spectral-radius/resolvent bound, not ||A||<1.
6. Ratio denominators can approach zero. DISMISSED by positive d_m and
   the explicit D_m q^k<=1/2 threshold. Omitting it is invalid.
7. Limit order: finite n->infinity convergence implies neither a reversed
   j/n passage nor discrete-to-continuous total variation. UPHELD against
   those inferences, both excluded in the main certificate.
8. C,q are numerically certified or common to moving supports. UPHELD
   against that interpretation; constants are operator-defined, D_m
   depends on the fixed prefix, and no width/regulator uniformity is claimed.
9. Static convergence constructs dynamics or resolves PAH-OMC-014.
   UPHELD against either inference. No temporal generator limit is proved.

No physical Pre-A, spacetime, gravity, QFT, continuum, mass gap or TOE
conclusion. The exact source identities and all scope firewalls remain
mandatory even if every executable algebra check returns PASS.
