# Controller-Free Two-Kick CL8 Macro, Routed Seam, and State Route Split

**Package:** PA-CP1-CL8-CONTROLLER-FREE-TWO-KICK-MACRO-BRIDGE-v0  
**Result:** PA-CP1-CL8-EXACT-GLOBAL-SIDEWAYS-MACRO-AND-FIXED-REGULATOR-SPLITTING-BRIDGE  
**Task:** T-054  
**Authority:** claim-nonbearing T0  
**Issued:** 2026-08-09

## 1. Question and answer

Can the inherited CL8 drift repair the one-kick rank-eight sideways
obstruction without an inserted controller, and can the resulting open
two-arm recurrence be joined to a periodic parent?

Yes at the local macro and routed fixed-regulator levels. Two exact
bond-potential kicks separated by inherited drift give a global polynomial
symplectic macro with four explicit mixed inverses. Every open acyclic
monotone cut is reconstructible. On a square cylinder, an exact all-k
swap-dressed seam-frame conjugacy exists.

Two stronger conclusions are false. The straight-routed block rectangle is
not the raw fixed-site even/odd circuit. Also, the full admitted mixed-inverse
domain does not have a universal positive quadratic invariant, tangent-circuit
Gaussian, or zero-centred nonlinear Gaussian. An arbitrary off-centre
nonlinear stationary Gaussian is not excluded. These results select no
physical candidate.

<a id="section-2-fixed-regulator"></a>
## 2. Fixed regulator and normalization firewall

Work on the inserted one-dimensional CL8 chain per unit transverse area.
There are eight Q3 species. Let

\[
 w=\frac a8,\qquad \mu=\chi w,\qquad
 \kappa=\frac{wc}{a^2}=\frac{c}{8a},
\]

and

\[
 V(x,y)=w\left[
 \frac{c}{2a^2}\lVert y-x\rVert^2+
 \frac{W_{\rm Q3}(x)+W_{\rm Q3}(y)}2
 \right].
\]

The mixed Hessian is field independent:

\[
 D_xD_yV=-\kappa I_8.
\]

A bond owns half of each endpoint kinetic energy:

\[
 h_b(x,p,y,r)=
 \frac{\lVert p\rVert^2+\lVert r\rVert^2}{4\mu}+V(x,y).
 \tag{2.1}
\]

When (2.1) is written as a standard two-particle kinetic energy, its exact-flow
mass is

\[
 m=2\mu. \tag{2.2}
\]

This mass is distinct from the full-node drift mass \(\mu\). Confusing them
changes the exact-flow determinant by a factor four.

## 3. Controller-free macro

Let

\[
 D_t(q,p)=(q+t p/\mu,p),
\]

and let \(K_s\) be the exact bond-potential kick. Put

\[
 h=\frac{\Delta}{8},\qquad s=\frac{\Delta}{2},
\]

and define, in application order,

\[
 M_\Delta=D_hK_sD_{2h}K_sD_h. \tag{3.1}
\]

Both endpoint legs receive every drift and kick. Equivalently, (3.1) is two
Strang substeps of length \(\Delta/2\) for (2.1). It is a symmetric
second-order integrator, not the exact autonomous flow.

The dimensionless cross parameter is

\[
 \rho=\frac{2hs\kappa}{\mu}
 =\frac{\kappa\Delta^2}{8\mu}
 =\frac{c\Delta^2}{8\chi a^2}. \tag{3.2}
\]

The exact mixed-inverse domain is

\[
 \rho\ne0,\qquad \rho^2\ne1. \tag{3.3}
\]

The simple positive safe domain is \(0<\rho<1\).

<a id="section-4-global-mixed-inverses"></a>
## 4. Exact global mixed inverses

Write the incoming legs as \(W=(x,p)\), \(S=(y,r)\), and the outgoing legs
as \(E=(e,P_2)\), \(N=(n,R_2)\). Let \(f=(w/2)\nabla W_{\rm Q3}\).

Given \(W,E\), define

\[
\begin{aligned}
x_1&=x+h p/\mu,&x_2&=e-hP_2/\mu,\\
P_1&=\mu(x_2-x_1)/(2h),\\
y_1&=x_1+\frac{P_1-p+s f(x_1)}{s\kappa},\\
y_2&=x_2+\frac{P_2-P_1+s f(x_2)}{s\kappa},\\
R_1&=\mu(y_2-y_1)/(2h),\\
r&=R_1+s[f(y_1)+\kappa(y_1-x_1)],\\
y&=y_1-h r/\mu,\\
R_2&=R_1-s[f(y_2)+\kappa(y_2-x_2)].
\end{aligned} \tag{4.1}
\]

Then \(S=(y,r)\) and \(N=(y_2+hR_2/\mu,R_2)\) are recovered globally.

Given \(W,N\), define

\[
\begin{aligned}
x_1&=x+h p/\mu,&y_2&=n-hR_2/\mu,\\
A&=x_1+\frac{2h}{\mu}[p-s(f(x_1)+\kappa x_1)],\\
B&=R_2+s[f(y_2)+\kappa(y_2-A)],\\
y_1&=\frac{y_2-(2h/\mu)B}{1-\rho^2},&
x_2&=A+\rho y_1.
\end{aligned} \tag{4.2}
\]

The remaining momenta and \(S,E\) follow linearly from the two drift and kick
relations. Leg exchange gives the other two mixed orientations. The nonlinear
force is evaluated only after the middle positions have been solved, so no
branch choice or caustic is hidden.

<a id="section-5-determinants"></a>
## 5. Exact determinants and noncommutativity firewall

Differentiating the explicit inverses gives

\[
 \det\left(\frac{\partial E}{\partial S}\Big|_W\right)
 =\det\left(\frac{\partial N}{\partial W}\Big|_S\right)
 =\rho^{16}, \tag{5.1}
\]

and

\[
 \det\left(\frac{\partial N}{\partial S}\Big|_W\right)
 =\det\left(\frac{\partial E}{\partial W}\Big|_S\right)
 =(1-\rho^2)^8. \tag{5.2}
\]

No onsite-Hessian commutativity is assumed. The ordered block cancellation is

\[
 DA-\beta C=(1-\rho^2)I,\qquad \beta=2h/\mu, \tag{5.3}
\]

not an illegally reordered product. A rational Q3 fixture with noncommuting
onsite Hessians verifies the full 32-dimensional Jacobian.

The exact negative controls are \(\rho=0\) for the first determinant and
\(\rho^2=1\) for the second.

## 6. Symplecticity and coefficient ownership

Every factor in (3.1) is an exact polynomial symplectomorphism. Therefore

\[
 M_\Delta^*\Omega=\Omega,\qquad
 \det DM_\Delta=1,\qquad
 M_\Delta^{-1}=M_{-\Delta}. \tag{6.1}
\]

The two kicks give \(2s=\Delta\), so the bond potential occurs exactly once.
The four endpoint drift parameters give \(4h=\Delta/2\), exactly the
time-\(\Delta\) coefficient of the half-owned endpoint kinetic energy.
On an even ring the two bond colors partition the bonds and every node belongs
to two bonds. This is exact coefficient occurrence, not exact autonomous
exponentiation or energy conservation.

<a id="section-7-exact-flow-check"></a>
## 7. Exact bond-flow consistency lemma

Let \(\Phi_t\) be the exact flow of (2.1), with \(m=2\mu\). On every compact
phase set \(K\),

\[
\begin{aligned}
D_yX&=\frac{\kappa t^2}{2m}I_8+O_K(t^4),&
D_rX&=\frac{\kappa t^3}{6m^2}I_8+O_K(t^5),\\
D_yP&=\kappa tI_8+O_K(t^3),&
D_rP&=\frac{\kappa t^2}{2m}I_8+O_K(t^4).
\end{aligned} \tag{7.1}
\]

Hence

\[
 \det D_{(y,r)}(X,P)=
 \left(\frac{\kappa^2}{48\mu^2}\right)^8t^{32}
 +O_K(t^{34}). \tag{7.2}
\]

The macro species-leading factor is instead

\[
 \frac{\kappa^2\Delta^4}{64\mu^2}. \tag{7.3}
\]

The denominators 48 and 64 must not be interchanged. Exact flow has only a
compact-uniform local small-time sideways theorem here; the macro has the
global mixed theorem.

<a id="section-8-open-all-cut"></a>
## 8. Open acyclic all-cut theorem

Place \(M_\Delta\) at each vertex of an open directed \(m\)-by-\(n\)
rectangle, with \(m+n=M\). Temporal inversion, the four mixed inverses, and
induction on the directed partial order prove:

1. every west-south input has one global field assignment;
2. incomparable ready vertices commute;
3. every monotone order-ideal cut has \(M\) complete legs;
4. every input-to-cut map is a global polynomial symplectic diffeomorphism;
5. complementary monotone arms reconstruct one another exactly.

Here "all" means all open acyclic monotone cuts. It excludes wrapped seams and
periodic monodromy until the routing data below are supplied.

<a id="section-9-periodic-quotient"></a>
## 9. Quotient incidence, raw-EO no-go, and all-k routed seam theorem

For \(T=(m,-n)\), the quotient
\(\Gamma=\mathbb Z^2/\langle T\rangle\) has the well-defined height

\[
 \vartheta([i,j])=ni+mj. \tag{9.1}
\]

It strictly increases on both directed edge types. The block transfer contains
\(mn\) vertices and has occurrence graph \(K_{n,m}\). A raw fixed-site
even/odd ring period has graph \(C_M\), \(M=m+n\) gates, and degree two.
Direct ledger equality forces \(m=n=2\).

For \(m=n=2\), write

\[
 A=M_{H_1V_1},\quad B=M_{H_1V_2},\quad
 C=M_{H_2V_1},\quad D=M_{H_2V_2}.
\]

Then

\[
 U_{\rm block}=DCBA,\qquad F=(DA)(BC),\qquad
 AU_{\rm block}=FA. \tag{9.2}
\]

Thus the C4 block is conjugate but not directly equal to the raw ring circuit.
An exact rational tangent separates their action on the \(q_{H_1}\) basis
vector.

For a general square \(m=n=k\), define

\[
 G_{j,i}=M_{\Delta;(H_j,V_i)},\qquad
 [x]_k=1+((x-1)\bmod k). \tag{9.3}
\]

Let \(U_k\) be the square word ordered by increasing \(i+j\), let \(C_k\) be
its triangular subword \(i+j\le k\), and let

\[
 L_\ell=\prod_{j=1}^kG_{j,[\ell-j]_k},\qquad
 F_k=L_k\cdots L_1. \tag{9.4}
\]

Projection of \(C_kU_k\) and \(F_kC_k\) onto every pair of letters sharing a
horizontal or vertical wire gives the same word. All other pairs commute.
The Cartier-Foata trace-monoid criterion therefore proves

\[
 C_kU_k=F_kC_k \tag{9.5}
\]

for every \(k\) and any common invertible local gate.

The repository uses straight routing: \(M_\Delta(W,S)=(E,N)\), while a
geometric frontier orders outgoing legs as \((N,E)\). Therefore the geometric
gate is \(P\circ M_\Delta\). On the initial cut
\((H_k,V_1,H_{k-1},V_2,\ldots,H_1,V_k)\), define

\[
\begin{aligned}
\operatorname{pos}_r(H_j)&=2(k-j)+r\pmod{2k},\\
\operatorname{pos}_r(V_i)&=2(i-1)+1-r\pmod{2k}.
\end{aligned} \tag{9.6}
\]

If \(\Pi_r\) is this slot permutation and \(\widehat F_k\) is the product of
swap-dressed alternating geometric layers, then

\[
 \widehat F_k=\Pi_kF_k\Pi_0^{-1},\qquad
 \Pi_k=R^k\Pi_0. \tag{9.7}
\]

With \(C_k^{\rm ring}=\Pi_0C_k\),

\[
 C_k^{\rm ring}U_k(C_k^{\rm ring})^{-1}
 =R^{-k}\widehat F_k. \tag{9.8}
\]

For odd \(k\), \(R^k\) flips the two bond colors, and two transfers restore the
frame. Exact rational audits for \(k=2,3,4\) verify each routed layer, the
half-turn, (9.5), and (9.8). Omitting the swap first fails at \(k=3\). Hence
the all-k swap-dressed routed theorem is positive while raw direct equality
remains false.

<a id="section-10-invariant-state-split"></a>
## 10. Invariant-state route split

The macro fixes the all-zero phase. For \(r<0\), with
\(v=\sqrt{-r/g}\), it also fixes the globally collective all-\(+v\) and
all-\(-v\) phases. Therefore

\[
 \delta_0,\qquad \frac12(\delta_{+v}+\delta_{-v}) \tag{10.1}
\]

are exact normalized stationary classical probabilities on every admitted cut.
They are singular and nonselecting. Liouville volume is invariant but has
infinite mass.

For one quadratic bond \(V(q)=q^TKq/2\), \(K=K^T>0\), if

\[
 \sigma\left(\frac{hs}{\mu}K\right)\subset(0,2), \tag{10.2}
\]

then one Strang substep, and hence \(M_\Delta\), preserves

\[
 \widetilde H_b(q,p)=
 \frac{\lVert p\rVert^2}{4\mu}
 +\frac12q^TK
 \left[I-\frac{hs}{2\mu}K\right]^{-1}q. \tag{10.3}
\]

This yields a normalized single-bond classical Gibbs law. The shadow is
bond-correlated and pairing-dependent, so it does not automatically tile the
open or alternating circuit.

A universal positive-quadratic theorem on the whole mixed-inverse domain is
false. For one species, use the local order

\[
 m=(q_H,p_H,q_V,p_V).
\]

Both implementations derive from the macro, rather than merely share as an
input, the exact tangent

\[
 L=\begin{pmatrix}
 1/4&11/16&3/4&5/16\\
 -1&1/4&1&3/4\\
 3/4&5/16&1/4&11/16\\
 1&3/4&-1&1/4
 \end{pmatrix}. \tag{10.4}
\]

The full zero-phase 32-dimensional bond tangent is verified to be eight
decoupled identical species blocks. For the one-species C4 circuit, use the
eight-dimensional order

\[
 (q_{H_1},p_{H_1},q_{H_2},p_{H_2},
   q_{V_1},p_{V_1},q_{V_2},p_{V_2}),
\]

and let \(F=(DA)(BC)\) act right-to-left. At \(\rho=1/2\), its exact
characteristic polynomial is

\[
 (\lambda-1)^2(\lambda^2+\lambda+1)
 (\lambda^2+3\lambda+1)^2. \tag{10.5}
\]

The reciprocal real eigenvalues \((-3\pm\sqrt5)/2\) include a modulus larger
than one. If \(G>0\) obeyed \(F^TGF=G\), an eigenvector would force
\(|\lambda|=1\), a contradiction. Thus the tangent circuit has no
positive-definite quadratic invariant and no nondegenerate invariant Gaussian.
For the full nonlinear fixture, there is no \(C^2\) invariant with a strict
nondegenerate minimum at zero, hence no zero-centred invariant Gaussian. This
argument does not exclude an arbitrary off-centre nonlinear stationary
Gaussian. C4 conjugacy transfers exactly these scoped obstructions to the
routed block.

This is
NG-2026-08-09-PRE-A-CP1-CL8-UNIVERSAL-PERIODIC-QUADRATIC-SHADOW-GIBBS.
It does not reject a smaller Floquet-stable domain, correlated non-Gaussian
states, singular fixed-point measures, arbitrary off-centre nonlinear
stationary Gaussians, or an energy-preserving redesign.

The state/reference reuse boundary is already partly negative. The new delta
fixed measures are singular, and the one-bond shadow Gibbs law is
pairing-dependent. Neither is the inherited regular oscillator-number
vacuum/Gibbs/reference. Therefore
NG-2026-08-04-PRE-A-CP1-CL8-PASSIVE-TWO-ARM-NUMBER-STATE-QUARTIC-REUSE,
NG-2026-08-04-PRE-A-CP1-CL8-CAUSAL-SPLIT-ORIGINAL-H-STATE, and
NG-2026-08-04-PRE-A-CP1-CL8-PRINCIPAL-FLOQUET-GIBBS-REFERENCE remain in force;
no common reference match is proved here.

<a id="section-11-gate-status"></a>
## 11. Gate status and A13 route

The alternative controller-free two-kick bond macro, open-cut, and all-k
swap-dressed seam subgates are closed on the inserted one-dimensional fixed
regulator. This does not reopen or replace the classical inserted-1D D-K-D
common-parent result already closed by EXP-000758/759. For this new bond macro,
however, a common regular positive state, preferred reference, counterterm
ledger, effective reduction to the three-dimensional Q3LOCK parent, and
regulator-compatible continuum state remain open.

The next CP1 test is a periodic/routed Bloch-Floquet and positive Lyapunov
feasibility package with an explicit collective-zero-mode convention and
cut-covariance check. The primary cross-candidate T-054 gate is instead
PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE.

A5 remains its published seven-hypothesis T6 conditional composition theorem.
The current registered SA-F4 route still passes through A13/T-050. T-050 is
mathematically preserved but parked from the main physical priority until a
registered reopen condition holds.

<a id="section-12-devils-advocate"></a>
## 12. Devil's-advocate audit

1. **Mass convention objection - DISMISSED after correction.** Exact bond flow
   uses \(m=2\mu\); the full-node macro drift uses \(\mu\). The determinant
   denominators are 48 and 64 respectively.

2. **Noncommuting Hessian objection - DISMISSED.** The explicit inverses do not
   invert onsite Hessians, and the ordered Schur identity is verified on a
   hostile noncommuting fixture.

3. **Earlier rank-eight no-go erased - DISMISSED.** One q-only kick remains
   rank eight. The positive theorem uses the explicitly surviving macro-cut
   route.

4. **Coefficient matching implies exact flow - UPHELD as prohibited.**
   Occurrence and second-order consistency do not imply autonomous
   exponentiation, inherited energy conservation, or Gibbs stationarity.

5. **Open cuts imply raw periodic EO - DISMISSED.** The exact all-k object is
   swap dressed and carries the seam rotation. Raw equality fails at \(k=3\).

6. **Symplecticity implies a universal Gaussian state - DISMISSED in the
   proved scope.** The admitted C4 tangent is hyperbolic, excluding a tangent
   Gaussian and a zero-centred nonlinear invariant Gaussian. An arbitrary
   off-centre nonlinear stationary Gaussian remains open. Mixed invertibility
   is not state stability.

7. **Classical mixed inverse implies quantum dual-unitarity - UPHELD as outside
   scope.** Forward unitary transport on \(B(L^2)\) does not prove unitary
   reshuffling, nonlinear Weyl normalization, or a preferred quantum state.

## 13. Reproduction contract

The primary audit verifies symbolic determinants, full Q3 rational fixtures,
explicit inverses, symplecticity, coefficient ownership, open cuts, quotient
incidence, the all-k trace-monoid and slot tables for \(k=2,3,4\), raw
counterexamples, the macro-derived C4 local tangent and full eight-species
decoupling, the C4 characteristic polynomial, and the one-bond shadow identity.
A non-importing standard-library Fraction/jet implementation repeats the
critical calculations. The integrated verifier reruns both, checks stored
freshness, records, generated surfaces, and scope.

## 14. No-overclaim boundary

This certificate proves only a controller-free global mixed macro, open
acyclic monotone-cut reconstruction, exact coefficient occurrence,
compact-local exact-flow consistency, quotient-incidence/raw-EO no-go,
all-k swap-dressed routed seam conjugacy, singular fixed-point probabilities,
a conditional one-bond quadratic shadow, and one C4 obstruction to a universal
positive-quadratic invariant, tangent-circuit Gaussian, or zero-centred
nonlinear Gaussian on the inserted one-dimensional fixed regulator.

It does not exclude arbitrary off-centre nonlinear stationary Gaussians. Nor
does it prove the exact autonomous CL8 flow, inherited energy conservation, a
common regular or preferred physical state/reference, strict quantum
dual-unitarity, nonlinear Weyl closure, a one-dimensional-to-three-dimensional
parent, regulator removal, a continuum or Hadamard state, physical vacuum,
phase transition, Lorentzian signature, light speed, gravity, cooling, C6
advancement, CP1 or Pre-A completion, a Sector-A tier change, or nature's
equation.
