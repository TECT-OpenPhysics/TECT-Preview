# EXP-001061 / compact-source endpoint third-moment bridge

## Decision

The compact-source extension of the endpoint moment bridge is discharged in
the registered finite-periodic compact-source scope.  It uses two existing
authorities without copying their proofs:

1. the source-uniform onsite form split with
   \(k_{x,h}\ge 1+\gamma |q_x|^4\), \(0<\gamma<g/32\); and
2. the R-167 v2.2 source-uniform Gibbs fifth moment
   \(m_5=\sup_{\Lambda,|h|\le h_0,x}\varphi_{\Lambda,h}(k_{x,h}^5)<\infty\).

This is a new algebraic bridge, not a new Gibbs-moment theorem.

## Exact bound

For one endpoint coordinate define

\[
 e(q)=\frac r2q^2+\frac g4q^4+\frac{r^2}{2g},\qquad r<0.
\]

Because \(q^4\le |q_x|^4\le (k_{x,h}-1)/\gamma\) and the quadratic term is
nonpositive,

\[
 e(q)\le \frac{g}{4\gamma}k_{x,h}+\frac{r^2}{2g}
      =:a_\gamma k_{x,h}+A_r.                         \tag{1.1}
\]

For a tested edge \(x\sim y\), let \(E_{xy}=1+e(q_x)+e(q_y)\).  Then

\[
 E_{xy}\le C_0+a_\gamma(k_{x,h}+k_{y,h}),\qquad C_0=1+2A_r.       \tag{1.2}
\]

The three-term power-mean inequality gives

\[
 E_{xy}^3\le 9\left(C_0^3+a_\gamma^3k_{x,h}^3+a_\gamma^3k_{y,h}^3\right).\tag{1.3}
\]

Since \(k_{x,h}\ge1\), \(k_{x,h}^3\le k_{x,h}^5\).  Taking the Gibbs
expectation and using the registered \(m_5\) therefore yields the explicit
volume- and compact-source-uniform endpoint estimate

\[
 \sup_{\Lambda,|h|\le h_0,x\sim y}\varphi_{\Lambda,h}(E_{xy}^3)
 \le M_{\rm bridge}^{\rm compact}
 :=9\left(C_0^3+2a_\gamma^3m_5\right).                 \tag{1.4}
\]

No sum over the ambient volume appears: only the two endpoints enter.

## Exact fixture

For the labelled fixture

\[
 g=\frac35,\quad r=-\frac92,\quad \gamma=\frac1{100},\quad m_5=3,
\]

the derived values are

\[
 a_\gamma=15,\qquad A_r=\frac{135}{8},\qquad C_0=\frac{139}{4},\qquad
 M_{\rm bridge}^{\rm compact}=\frac{35834571}{64}.                \tag{1.5}
\]

The primary SymPy lane, the independent Fraction lane, and Lean R243 derive
these values from the labelled inputs.  The scalar grid checks the upper
bound for all seven listed field values and exact nonnegative cube-majorant
fixtures; it is an executable oracle, not an operator-domain proof.

## Adversarial review

1. **Source dependence — UPHELD.**  The lower bound on \(k_{x,h}\) is the
   registered compact-source form split; no zero-source \(\xi_0\) is reused.
2. **Coefficient — UPHELD.**  \(a_\gamma=g/(4\gamma)\) follows directly from
   the quartic lower bound and is recomputed by both lanes.
3. **Quadratic sign — UPHELD.**  The \(r<0\) term is dropped only in an upper
   bound and \(A_r=r^2/(2g)\) is retained.
4. **Uniformity — UPHELD.**  The bound has two endpoint moments only, and the
   upstream \(m_5\) is uniform over the declared periodic compact-source set.
5. **Order — UPHELD.**  \(k^3\le k^5\) uses the explicit \(k\ge1\) input; no
   history moment or all-order estimate is smuggled in.
6. **Lean — UPHELD.**  R243 checks exact rational identities and the scope
   firewall, not unbounded operator closure.
7. **Duhamel promotion — UPHELD.**  (1.4) is a static endpoint moment only;
   direct \(D,\delta D\) Cauchy and the two-sided remainder remain open.
8. **QFT/TECT promotion — UPHELD.**  No OS/KMS/GNS/continuum or canonical
   TECT production-owner conclusion follows.

## Boundary and next gate

EXP-001061 advances the QFT-facing direct-\(D,\delta D\) route by removing the
compact-source endpoint third-moment hypothesis in the registered periodic
scope.  Arbitrary boundaries, all-time history summation, product/core density,
exhaustion independence, group law, common \(\alpha\), Hamiltonian-to-OS
identification, KMS/GNS, continuum, C6, Sector A and Pre-A remain open.

The next exact target is a genuinely two-sided Duhamel remainder estimate on the
predeclared fixed-\(\beta\) OS-mixture word class, with the modular/dual-state
topology gate kept explicit.
