# Q3LOCK manuscript integration: collective forms and spectral cutoffs

Date: 2026-09-06. Status: internal T0 content review; no external signature.
Research authority: EXP-000780 -> EXP-000781 -> EXP-000782, through R-497.
PDF: deferred until content review and final organization are complete.

## Scope and source distinction

Section 8 of the manuscript now transfers the full finite-volume content of
`strategy/q3lock-collective-falk-bruch-content-260905.md`, Sections 2--7.
The canonical source remains unchanged and hash-pinned. The transfer uses
the scalar-Jensen variational replacement, not the older trace-differentiation
route. The positive-lambda, eight-component, nonradial model and the sufficient
threshold are unchanged. No independent acceptance or novelty is asserted.

The source comparator is Kargol--Kondratiev--Kozitsky,
https://arxiv.org/pdf/0710.2303v1 , Proposition 3.18, equations (3.65) and
(3.68), printed page 34. The manuscript now includes a direct finite spectral
proof of that standard inequality, so it is not left as an unproved imported
step. This does not import the radial moments or phase theorems 3.20--3.21.
The source text was checked online; no new source-PDF visual inspection or
Q3LOCK PDF generation is claimed in this checkpoint.

## Transferred analytic content

After a constant shift, the heat trace at beta/2 bounds the thermal energy at
beta and hence the quartic moments. Smooth radial cutoffs followed by compact
mollification give a form core. Translation preserves both H^1 and the
quartic weighted norm. For the translated Hamiltonian H(t), the diagonal
spectral Jensen inequality and a second Jensen inequality for Gibbs weights
give rho(H(t)-H)>=0. Only its integrable scalar polynomial is differentiated.

The unit collective shift has squared norm one. Its Hessian is
r+3g sum S/(8V)+lambda sum D_int/(8V). The physical momentum double
commutator is hbar^2 times that Hessian on the core. Positivity is separately
proved in Gibbs expectation, not pointwise or by cycling three unbounded
operators. Actual zero-source FKG and parity give rho(D_int)<=3rho(S) and
rho(Q^2)>=rho(S)/8, hence theta_Q=-r/[3(g+lambda)].

The Duhamel form is expressed through positive logarithmic means, including
their equal-probability value. This proves b<=g and its Cauchy--Schwarz bound
and identifies the nonnegative heat-kernel spectral sum. No positive-time
operator exponential is presumed bounded.

For A_R=R tanh(Q/R), both A_R and its square preserve the form domain.
Subtracting the eigenvector form equation leaves the gradient square over
2m. Before rearranging spectral terms, two explicit nonnegative
energy-weighted sums are bounded by the finite thermal energy. This yields
c_R=(beta/m)rho(sech^4(Q/R)), not a pointwise value for the expectation.

The first-M spectral restrictions are normalized by q_M=Z_M/Z. Multiplying
each finite g,b,c by q_M gives the restrictions of their full nonnegative
sums. Their limits follow at fixed R,L,beta; normalized terms need not be
monotone. Only afterwards is R removed using thermal L2 convergence and
two-time loop Cauchy--Schwarz. The coefficient tends to beta/m, the local
Duhamel form equals D_L(0,0), and the monotonicity of s f(k/s)=k/x_s^2
allows substitution of theta_Q. The final scalar bound has no volume factor;
no common infinite-volume operator core has been constructed.

## Direct finite inequality, not a numerical inference

For a finite self-adjoint matrix and positive Gibbs probabilities, let b be
the logarithmic-mean sum and use weights
w_ij=L(p_i,p_j)|A_ij|^2/b. Set x_ij=|log(p_i)-log(p_j)|/2.
Then g/b=sum w_ij Phi(x_ij^2) and c/(4b)=sum w_ij x_ij^2, with
Phi(u)=sqrt(u)coth(sqrt(u)) and Phi(0)=1.

For x>0 its second derivative with respect to u, evaluated at u=x^2, is

    Phi''(x^2)=cosh(x)/(4x^3 sinh(x)^3)
                       * [2x^2-x tanh(x)-sinh(x)^2].

The bracket is negative globally: tanh(x)<=x and
(tanh(x)-x+x^3/3)'=x^2-tanh(x)^2>=0 imply
tanh(x)>=x-x^3/3. Taylor's nonnegative remainder gives
sinh(x)>=x+x^3/6. Their combination bounds the bracket above by
-x^6/36. Continuity at zero gives concavity on the closed half-line.
This is an analytic argument for all x, not a sampled plot or root test.

Jensen gives g/b<=Phi(c/(4b)). If c=0 then b=g. Otherwise set
z=sqrt(c/(4b)); the bound gives c/(4g)>=z tanh(z).
If x tanh(x)=c/(4g), monotonicity gives x>=z and
b=c/(4z^2)>=c/(4x^2)=g tanh(x)/x. This proves the standard finite
Falk--Bruch inequality at the exact normalization used in the manuscript.
The zero matrix is handled separately. The subsequent infinite spectral
passage is a distinct form-domain argument, not finite matrix algebra.

## Reproduction and evidence limits

```powershell
& E:/Dev/TECT.venv/Scripts/python.exe -X utf8 E:/Dev/TECT/verification/scripts/q3lock_manuscript_collective_audit.py
```

The new diagnostic independently differentiates the physical Q3 polynomial
under a common shift, checks the analytic derivative identities above, and
compares direct finite matrix commutators with spectral formulas. Integer
energy fixtures at beta=log(2) give rational Gibbs probabilities; logarithmic
means are evaluated symbolically, including degenerate energies. Two-level
fixtures check saturation without numerical implicit roots. Normalization
and bounded-coordinate derivative checks reject the wrong beta, hbar and
finite-rank normalization substitutions. These are exact finite and symbolic
diagnostics, not proof certification of infinite-dimensional limits.

The integrated lane invokes the preceding infrared, DLR, loop and content
checkers in memory, preserving all four historical run files. It writes
current hashes only to
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-06-q3lock-manuscript-collective-audit/result.json`.
Counts include structure-only locators. The independent signed mathematical
review is not supplied by this script or by the author's self-review.
The registered EXP-001608 replay passes 150 current checks, with the prior
612 infrared, 81 DLR, 203 loop and 32 content checks nested in the output.

## Adversarial review

| Objection | Disposition |
|---|---|
| The translation argument differentiates an unbounded cubic heat-trace perturbation. | DISMISSED for this text: two scalar Jensen steps replace trace differentiation; all polynomial coefficients are integrable. |
| B_L or D_int<=3S is positive/bounded pointwise. | UPHELD as a danger: the manuscript now states only Gibbs expectation inequalities and explicitly uses parity and FKG. |
| The global momentum and local coordinate commutators have the same hbar and beta factors. | DISMISSED: the distinct observables and beta H convention are explicit; exact hostile fixtures reject both substitutions. |
| Scalar concavity is merely fitted at a grid of values. | DISMISSED: the derivative, global bracket bound and Jensen proof are printed; symbolic tests verify identities only. |
| Degenerate eigenvalues give a zero denominator. | DISMISSED: L(a,a)=a is retained and degenerate finite fixtures are included. |
| Absolute convergence is assumed when energies are rearranged. | VALID-with-mitigation: both energy-weighted sums are displayed before regrouping and bounded using h_C and thermal energy. Independent review remains required. |
| Finite spectral matrices preserve the exact coordinate commutation relation. | DISMISSED: no such assertion is used; q_M times the finite spectral sums are taken to their limits. |
| Normalized finite g,b,c increase monotonically. | UPHELD as false: only the unnormalized restrictions are monotone; a decreasing/increasing g fixture is retained. |
| R and M can be removed simultaneously, or the volume can be sent to infinity first. | DISMISSED for the declared proof: M at fixed R,L,beta precedes R at fixed L,beta; the spatial limit is later. |
| Passing the diagnostics closes the cusp theorem or proves novelty. | DISMISSED: full composition, literature and signed reviews remain open. The scalar inequality is standard. |

Units and conventions: m=chi/hbar^2; the local c_R has beta/m and the
global Hessian has no extra hbar^2. Sign: probabilities decrease with energy,
so each paired c summand is nonnegative. Convergence is analytic; no numerical
quadrature or approximate root certifies a limit. Hardcode masking: derived
coefficients and means are recomputed; expected formulas are labelled oracles.
Limit cases include zero and diagonal observables, repeated energies and
two-level saturation. External mathematical reviewers are invited to rerun
the command and attack the form-domain, absolute-sum and cutoff arguments.

## Next gate

Review the entire pressure/infrared/collective/Griffiths/source-tangent
composition for compatible hypotheses, normalizations and limit orders,
then complete the literature and signed mathematical review. The manuscript
is still an internal T0 draft, not a verified submission-ready theorem.
R-497, physical gates, shared-tree admission hold and PDF deferral are unchanged.
