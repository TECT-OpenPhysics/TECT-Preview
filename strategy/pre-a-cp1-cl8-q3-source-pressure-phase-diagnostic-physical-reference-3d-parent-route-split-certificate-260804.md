# Pre-A CP1/CL8 Q3 source-pressure, phase, physical-reference and 3D-parent route split

Date: 2026-08-04  
Candidate: `PA-CP1-CL8-Q3-SOURCE-PRESSURE-PHASE-DIAGNOSTIC-PHYSICAL-REFERENCE-AND-3D-PARENT-ROUTE-SPLIT-v0`  
Result: `PA-CP1-CL8-Q3-ALL-SOURCE-BOUNDARY-INDEPENDENT-CONVEX-EVEN-PRESSURE-WITH-PHASE-REFERENCE-AND-PARENT-OBSTRUCTIONS`  
Exploration: `EXP-000779`
Authority: claim-nonbearing T0 analytic theorem and exact route no-gos

## 1. Result first

Retain exactly the newly declared massive, plane-Wick, eight-component
`1+1`-dimensional Q3 comparator of `EXP-000778`, with `m0>0`, `g>0`,
`lambda>=0`, and fixed real symmetric `K_pl`.  For every constant external
source `J in R^8`, define

\[
 u_J(\Phi)=u(\Phi)-J\mathbin{\cdot}\Phi.              \tag{1.1}
\]

Write `P_K(q)=q^TK_pl q/2+W4(q)`.  For every Section-VIII covariance/Wick
pair `X;Y` in `F,D,N,P`, define

\[
 p_A^{X;Y}(J)={1\over |A|}\log\int
 \exp\left[-\int_A :P_K(\Phi(x)):_Ydx
             +J\mathbin{\cdot}\int_A\Phi(x)dx\right]d\mu_A^X. \tag{1.2}
\]

For rectangles `A_(s,t)` with both side lengths tending independently to
infinity, the thermodynamic limit

\[
 p(J)=\lim_{\substack{s,t\to\infty\\
                      \text{independently}}}
       p_{A_{s,t}}^{X;Y}(J)                            \tag{1.2a}
\]

exists, is finite, is independent of `X;Y`, and is locally uniform in `J`.
Moreover,

\[
 p(J)\ \hbox{is convex},\qquad p(J)=p(-J),\qquad
 p(0)=\alpha_\infty>0.                               \tag{1.3}
\]

For every direction `v in R^8`, the finite convex even function

\[
 f_v(h)=p(hv)                                         \tag{1.4}
\]

has finite one-sided derivatives at zero, and

\[
 m_v:=f'_{v,+}(0)\geq0,\qquad f'_{v,-}(0)=-m_v.       \tag{1.5}
\]

Thus `m_v>0` is an exact pressure-level cusp criterion for spontaneous
response in direction `v`.  This package does **not** determine whether any
`m_v` is positive or zero, construct plus/minus states, or prove phase
transition or uniqueness.

Two exact obstructions are also closed.

1. The already known value `p(0)=alpha_infinity` cannot classify the phase:
   smooth and cusped finite convex even functions can have that same value.
2. A transverse-zero restriction of a three-dimensional Q3 lattice action is
   not its interacting transverse marginal.  Integrating even one discarded
   transverse mode produces a nonconstant effective term.  Therefore the
   inserted `1+1` comparator is not thereby derived from ST8/Q3LOCK.

The additive-scalar mutation also reuses the registered absolute-anchor
no-go: normalized states, correlations, KL divergence, and `p(J)-p(0)` are
unchanged while raw pressure and energy density shift.  No result here
identifies the named Gaussian comparator with physical empty space.

## 2. All-source pressure theorem

### 2.1 Coercive absorption of the source

The Q3 quartic obeys

\[
 W_4(q)\geq c_4|q|^4,\qquad c_4={g\over32}>0.         \tag{2.1}
\]

For every `epsilon>0`, Holder--Young duality with exponents `4` and `4/3`
gives

\[
 |J\mathbin{\cdot}q|
 \leq \epsilon |q|^4
 +C\epsilon^{-1/3}|J|^{4/3}.                         \tag{2.2}
\]

Taking `epsilon<c4` preserves a positive quartic coefficient.  The source is
therefore a degree-one subdominant coupling with exponent `4/(4-1)=4/3`.
`EXP-000778` formally stated its uniform perturbation theorem only for the
matrix-quadratic and scalar terms needed there.  The next paragraph proves,
rather than assumes, the required vector-linear extension.

More explicitly, let `k=||K_pl^-||_op` be the norm of the negative part of
the fixed quadratic matrix.  Splitting the quartic lower bound into one half
retained and two quarters used for absorption gives

\[
 W_4(q)+{1\over2}q^TK_{\rm pl}q-J\mathbin{\cdot}q
 \geq {c_4\over2}|q|^4
 -{k^2\over4c_4}
 -{3\over4}c_4^{-1/3}|J|^{4/3}.                      \tag{2.2a}
\]

For each compact source ball `|J|<=R`, repeat the `EXP-000778` Section 4
Duhamel proof with the eight additional degree-one chaos labels.  Product
Ornstein--Uhlenbeck hypercontractivity gives the scalar degree-one power, and
(2.2)--(2.2a) give its factorially summable `4/3` majorant.  The label count is
finite and independent of cutoff and rectangle, so this proves one cutoff-,
rectangle-, and boundary-uniform two-sided normalized pressure bound.  The
same conditioning, boundary Wick reordering, convex Lipschitz argument, and
all-sixteen theorem apply because a linear polynomial has no Wick
contraction.  Hence all covariance/Wick pressures have the common limit
(1.2a).  Pointwise convergence of finite convex functions on the open source
space, together with local boundedness, is locally uniform on `R^8`.

This is not a new general multivariate constructive theorem.  It is the
degree-one specialization of the already proved radially coercive Q3 port.

### 2.2 Convexity and global Z2

At finite `A`, Holder's inequality makes

\[
 p_A(J)={1\over|A|}\log Z_A(J)                       \tag{2.3}
\]

convex in `J`.  Pointwise convergence of finite convex functions on every
compact source ball preserves convexity of the finite limit.  The centered
Gaussian law and the interaction `u` are invariant under
`Phi -> -Phi`.  Changing variables gives

\[
 Z_A(J)=Z_A(-J)                                       \tag{2.4}
\]

for every cutoff, rectangle, and admitted boundary/Wick convention.  Thus
the limit is even.  Equation (1.3) at the origin is exactly `EXP-000778`.

### 2.3 Directional derivative and order of limits

A finite convex function on the real line has finite left and right
derivatives at every interior point.  Since `f_v` is even and convex, zero is
a minimum and (1.5) follows.

At every finite cutoff, rectangle, and admitted `X;Y` convention, source
integrability permits differentiation under the integral:

\[
 {d\over dh}p_A(hv)
 ={1\over|A|}\mathbb E_{A,hv}[M_A(v)],\qquad
 {d^2\over dh^2}p_A(hv)
 ={1\over|A|}\operatorname{Var}_{A,hv}(M_A(v))\geq0,
 \quad M_A(v)=\int_Av\mathbin{\cdot}\Phi(x)dx.        \tag{2.5}
\]

Field inversion, rather than any spatial symmetry assumption, then gives

\[
 {d\over dh}p_A(hv)\big|_{h=0}
 ={1\over|A|}\mathbb E_{A,0}
   M_A(v)=0.                                          \tag{2.5a}
\]

Consequently a nonzero spontaneous response, if present, can only be tested
with the difference quotient

\[
 q_A(h)={p_A(hv)-p_A(0)\over h}                       \tag{2.5b}
\]

in the ordered limit

\[
 s,t\to\infty\ \hbox{independently first},\qquad
 h\to0^\pm\quad\hbox{second}.                        \tag{2.6}
\]

Neither finite-volume symmetry nor pressure boundary-independence permits
these limits to be exchanged.  Precisely,

\[
 \lim_{h\downarrow0}\lim_{\substack{s,t\to\infty\\
                                      \mathrm{independently}}}q_{A_{s,t}}(h)=m_v,
 \qquad
 \lim_{\substack{s,t\to\infty\\
                  \mathrm{independently}}}\lim_{h\downarrow0}q_{A_{s,t}}(h)=0.
                                                            \tag{2.7}
\]

The second equality is the finite-volume symmetry statement; the two
expressions need not be equal.  For example,
`f_n(h)=n^(-1) log cosh(nh)` is smooth and even with `f_n'(0)=0`, while

\[
 0\leq |h|-f_n(h)\leq{\log 2\over n}                 \tag{2.8}
\]

for every real `h`; hence it tends locally uniformly to `|h|`.  No
universal convergence of finite-volume
derivatives at nondifferentiability points is asserted.  Finally, `p` is
fully differentiable at `J=0` exactly when `m_v=0` for every direction `v`,
not merely for one selected direction.

The curve `p(hv)` restricts the **source variable** to the line through `v`.
The functional integral still ranges over all eight field components.  It is
not a field restriction `Phi=qv` and not a dimensional marginal.

## 3. Exact phase-information boundary

Knowing one pressure value does not determine a derivative or a phase.  For
any fixed `alpha` and `m>0`, both growth-compatible convex pressure controls

\[
 f_0(h)=\alpha+m\log\cosh h,\qquad
 f_1(h)=\alpha+m|h|                                  \tag{3.1}
\]

are finite, convex, even, and have value `alpha` at zero.  The first is
differentiable there; the second has right derivative `m` and left derivative
`-m`.  This is a logical countermodel to any inference from the scalar datum
`p(0)` alone.  It is not a claim that either function is the Q3 pressure.

Even knowledge that `m_v=0` in every direction would not by itself prove
uniqueness of every infinite-volume state.  Conversely, `m_v>0` would certify
a pressure cusp but construction and inequivalence of extremal plus/minus
states would still require source-state compactness and identification of
their tangent functionals.

Scalar `phi4_2` phase transitions and Ising/Lee--Yang correlation tools are
established prior art.  They do not apply verbatim to the coupled Q3
interaction.  A positive Q3 phase theorem requires an ordered parameter
window and ultraviolet-uniform block-order or contour estimates, followed by
construction of distinct limiting states.

## 4. Physical-reference obstruction

Let `c` be any real local scalar and set

\[
 u_{J,c}=u_J+c.                                       \tag{4.1}
\]

Then, exactly at every cutoff and volume,

\[
 Z_{A,c}(J)=e^{-c|A|}Z_A(J),\qquad
 p_c(J)=p(J)-c.                                      \tag{4.2}
\]

The scalar cancels from the normalized Gibbs density.  Hence normalized
states, correlations, source-response differences `p(J)-p(0)`, and relative
entropy are unchanged, whereas every raw Hamiltonian energy density shifts
by `+c`.  This reuses
`NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR`.

Therefore no normalized Euclidean or operator-algebraic datum in this package
can identify an absolute gravitational vacuum energy or prove that the named
massive Gaussian law is cosmic empty space.  Such a statement needs an
independently selected reference state on the same algebra and geometry, a
common renormalized stress tensor, and an external renormalization or
observable difference condition.  Curved-spacetime local covariance still
leaves finite renormalization parameters; it does not supply the missing
TECT selection by itself.

## 5. Exact restriction-versus-marginal obstruction

The ST8/Q3LOCK parent is a three-spatial-dimensional finite lattice with
continuous oscillator variables.  Setting every transverse nonzero mode to
zero defines a classical restricted submanifold.  It does not identify the
interacting quantum or Euclidean marginal obtained by integrating those
modes.

The insufficiency of bare restriction data is already exact in a two-cell
scalar control block.  Put

\[
 \phi_1={q+r\over\sqrt2},\qquad
 \phi_2={q-r\over\sqrt2}.                             \tag{5.1}
\]

Then

\[
 \phi_1^4+\phi_2^4
 ={1\over2}q^4+3q^2r^2+{1\over2}r^4.                 \tag{5.2}
\]

For `a,b>0`, take the full two-cell action

\[
 S(q,r)={a\over2}(q^2+r^2)
       +b\left({q^4\over2}+3q^2r^2+{r^4\over2}\right). \tag{5.3}
\]

The restriction `r=0` gives
`S_rest(q)=aq^2/2+bq^4/2`.  In contrast, integrating the transverse mode
gives, up to an additive normalization constant,

\[
 S_{\rm eff}(q)=S_{\rm rest}(q)+F(q^2)-F(0),          \tag{5.4}
\]

\[
 F(s)=-\log\int_{\mathbb R}
 \exp\left[-\left({a\over2}+3bs\right)r^2
            -{b\over2}r^4\right]dr.                 \tag{5.5}
\]

Differentiation under the integrable coercive weight gives

\[
 F'(s)=3b\,\mathbb E_s[r^2]>0,\qquad
 F''(s)=-9b^2\operatorname{Var}_s(r^2)<0.            \tag{5.6}
\]

Thus the discarded-mode integral produces a nonconstant effective
interaction.  This exact block refutes the inference that agreement after
setting transverse modes to zero is, by itself, enough to identify an
interacting marginal or state.  It does not calculate the full registered
ST8/Q3LOCK marginal or exclude cancellations in a separately proved full
effective action.

This no-go does not forbid a deliberately constrained parent, a decoupling
limit, a dressed embedding, or a proved renormalization-group effective
action.  It requires one of those explicit mechanisms before the `1+1` Q3
comparator can be called derived from the registered three-dimensional
ST8/Q3LOCK family.

There is also a dimension/type firewall.  A direct classical
three-dimensional equilibrium parent is a Euclidean `Phi4_3`-type problem.
A quantum theory with three spatial dimensions is instead associated with a
four-dimensional Euclidean construction.  The present `P(Phi)_2` comparator
proves neither merely by relabelling its coordinates.

## 6. Prior-art boundary

The following component results are established outside TECT.

- Guerra--Rosen--Simon prove scalar `P(phi)_2` pressure existence,
  boundary-condition independence, and the half-pressure machinery.  The Q3
  finite-component port was written in `EXP-000778`.
- Glimm--Jaffe--Spencer prove a phase transition for a scalar `phi4_2` model
  in a two-phase parameter region.  Simon--Griffiths supply the classical
  Ising approximation and Lee--Yang/GHS tools for scalar `phi4_2`.
- Chandra--Gunaratnam--Weber prove low-temperature phase-transition estimates
  for scalar `phi4_3`.
- Wald and Hollands--Wald classify stress-tensor/local Wick ambiguities under
  appropriate axioms; those results explain why an observable renormalization
  condition is required, but do not select the TECT physical vacuum.

No located source proves the complete horizon-boundary-state to high-energy
bulk to cooling/ordering to emergent-spacetime TECT chain.  This package makes
no first-in-the-world claim: its positive theorem is the Q3 source extension
of a classical constructive method, while its two no-gos are elementary
interface separations.

## 7. Gate split and next theorem

This package closes:

1. all-constant-source Q3 pressure existence and boundary independence;
2. convexity, global-Z2 evenness, and directional derivative existence;
3. the exact cusp diagnostic `m_v`;
4. the no-go from `p(0)` alone to phase classification;
5. the exact transverse restriction-versus-marginal obstruction; and
6. the normalized-data absolute-reference firewall.

It leaves open:

1. positivity or vanishing of any `m_v`;
2. construction, purity, clustering, or inequivalence of source-selected
   states;
3. a Q3 Peierls/contour or other phase theorem;
4. physical empty-space and stress-tensor anchoring;
5. a regulator-compatible derivation from the original fixed-raw CL8 or
   three-dimensional ST8/Q3LOCK parent;
6. state/vector/gap/correlator limits and interacting microlocal spectrum;
7. C0/N1--N5, C6, CP1, Sector A, and Pre-A.

The next constructive gate is

`PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-PARENT-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT`.

It must first prove the thermodynamic pressure and ground-energy-density
existence of the already registered fixed-lattice three-dimensional
ST8/Q3LOCK quantum oscillator family, then distinguish a genuine effective
reduction from the refuted bare transverse-zero marginal identification.

## 8. Devil's-advocate review

1. **GRS scalar source theory is being quoted verbatim for Q3. DISMISSED.**
   The only new coupling is degree one.  Equation (2.2) places it inside the
   explicit finite-component, radially coercive subdominant-coupling theorem
   already proved in `EXP-000778`.
2. **Boundary-pressure equality proves a unique phase. UPHELD AS FALSE.**
   Section 3 exhibits the missing derivative information and retains the
   state/phase gate.
3. **Finite-volume derivative zero proves `m_v=0`. UPHELD AS FALSE.**  The
   thermodynamic and zero-source limits need not commute; (2.6) fixes the
   required order.
4. **A pressure cusp automatically constructs pure plus/minus states. UPHELD
   AS FALSE.**  The cusp is a scalar diagnostic; state compactness,
   identification, extremality, and clustering are separate.
5. **The positive centered density is below physical empty space. UPHELD AS
   FALSE.**  Equation (4.2) leaves normalized data invariant while moving raw
   energy, and the Gaussian reference has not been selected physically.
6. **A transverse-zero invariant sector is the parent marginal. UPHELD AS
   FALSE.**  Equations (5.2)--(5.5) give an exact nonconstant marginal
   correction.
7. **The two-cell obstruction rules out every dimensional reduction.
   DISMISSED.**  It rules out only bare restriction-equals-marginal.  Tuned,
   constrained, decoupling, dressed, or exact-RG routes remain admissible.
8. **This proves Pre-A. UPHELD AS FALSE.**  The parent, phase, physical
   reference, C0/N1--N5, and C6 interfaces remain open.

## 9. Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_source_pressure_phase_diagnostic_physical_reference_3d_parent_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_source_pressure_phase_diagnostic_physical_reference_3d_parent_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_cl8_q3_source_pressure_phase_diagnostic_physical_reference_3d_parent_route_split_verify.py --self-test
```

The executable checks audit the degree-one Young exponent, finite-source
convexity and evenness, smooth-versus-cusp underdetermination, finite-volume
zero response, scalar-shift invariance of normalized laws and KL, the exact
two-cell quartic transform, strict source dependence of the discarded-mode
marginal, scope firewalls, source provenance, and unchanged C6 authority.
They do not replace the analytic GRS/Q3 theorem written in Section 2.
