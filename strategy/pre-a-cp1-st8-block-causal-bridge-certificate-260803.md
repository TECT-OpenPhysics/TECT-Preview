# PA-CP1-ST8-CB-v0: staggered block factorization and causal-boundary certificate

- Candidate: `PA-CP1-ST8-CB-v0`
- Parent: `PA-CP1-LT3-RS-v0`
- Task: `T-054`
- Authority: T0 exact finite candidate certificate; no TECT claim or tier change
- Date: 2026-08-03

## Result first

The current LT3 parent is not one interacting eight-valley bulk.  For every
fine side `N=4m`, it is exactly a sum of eight decoupled ordinary
nearest-neighbour coarse real `phi4` Hamiltonians.  The transformation is the
signed parity-block map

\[
 \phi_{2y+\epsilon}=(-1)^{y_1+y_2+y_3}\psi_\epsilon(y),\qquad
 \pi_{2y+\epsilon}=(-1)^{y_1+y_2+y_3}\rho_\epsilon(y).
\]

It is canonical and factorizes the kinetic, mass, stiffness and quartic terms
without approximation.  The eight fine nodes are therefore eight folded
coarse-species zero modes.  The registered `256=2^8` classical minima and the
finite quantum tensor product are exact analytic corollaries, but no one
species or ordered sign is selected.

A separately declared harmonic regulator family has the fixed-band
Klein--Gordon symbol limit and a bounded group speed.  On the exact PA-H1
circle, a selected one-species ordered tangent can be tuned to the registered
frequencies `(3,5,5)`.  This does not derive the selection or the boundary
map.  Moreover, the continuous-time lattice propagator has a nonzero
nearest-neighbour response of order `t^2` at arbitrarily small time.  Hence a
bounded group speed is not an exact finite-regulator domain of dependence.

The package advances the common-parent search but does not close CP1 or
Pre-A.

## 1. Imported parent and fixed conventions

Let

\[
 \Lambda_N=(\mathbb Z/N\mathbb Z)^3,\qquad N=4m,
\]

and let `S_i` denote the positive unit translation in direction `i`.  The LT3
parent uses

\[
 B_i=-S_i-S_i^{-1}
\]

and

\[
 H_N(\phi,\pi)=
 \sum_x\frac{\pi_x^2}{2\chi}
 +\frac c2\sum_{x,i}(B_i\phi)_x^2
 +\frac r2\sum_x\phi_x^2
 +\frac g4\sum_x\phi_x^4,
\]

with `c,g,chi>0`.  The finite Weyl representation, additive convention and
same-Hamiltonian classical comparison are exactly those of
`PA-CP1-LT3-RS-v0`; this certificate does not alter them.

Set `M=N/2` and write every fine site uniquely as

\[
 x=2y+\epsilon,\qquad y\in\Lambda_M,\quad
 \epsilon\in\{0,1\}^3.
\]

Because `N=4m`, `M` is even and

\[
 (-1)^{|y+Me_i|}=(-1)^{|y|}.
\]

Thus the staggered sign is periodic on the coarse torus.  The hostile control
`N=6`, `M=3` instead changes the sign around a coarse cycle and produces an
antiperiodic or twisted block.  The periodic theorem is deliberately limited
to `N` divisible by four.  In general, `N=4m+2` produces an antiperiodic or
twisted coarse boundary rather than the periodic eight-block theorem.

## 2. Exact canonical map

Define

\[
 \psi_\epsilon(y)=(-1)^{|y|}\phi_{2y+\epsilon},\qquad
 \rho_\epsilon(y)=(-1)^{|y|}\pi_{2y+\epsilon}.
\]

This is a signed permutation of the `N^3` coordinates and the same signed
permutation of the momenta.  Therefore

\[
 \sum_x(\phi_x\pi'_x-\pi_x\phi'_x)
 =\sum_{\epsilon,y}
 (\psi_\epsilon(y)\rho'_\epsilon(y)
 -\rho_\epsilon(y)\psi'_\epsilon(y)).
\]

The map is an exact linear canonical bijection.  In the quantum coordinate
representation, its Jacobian has absolute determinant one and its pullback is
an `L2` unitary.

<a id="section-3-exact-full-hamiltonian-factorization"></a>
## 3. Exact full-Hamiltonian factorization

For `x=2y+epsilon`, the two fine neighbours in direction `i` lie in the
opposite parity class.  Direct substitution gives

\[
 (B_i\phi)_{2y+\epsilon}
 =(-1)^{|y|}\bigl(
 \psi_{\epsilon'}(y+\delta)-\psi_{\epsilon'}(y)\bigr),
\]

where the precise `epsilon'` and coarse origin depend only on whether
`epsilon_i` is zero or one.  Summing over every fine site relabels these terms
once and yields

\[
 \sum_x(B_i\phi)_x^2
 =\sum_{\epsilon,y}
 \bigl(\psi_\epsilon(y+e_i)-\psi_\epsilon(y)\bigr)^2.
\]

The signed permutation separately preserves

\[
 \sum_x\pi_x^2,\qquad \sum_x\phi_x^2,\qquad \sum_x\phi_x^4.
\]

Hence the identity is nonlinear and exact:

\[
 H_N(\phi,\pi)=
 \sum_{\epsilon\in\{0,1\}^3}
 H_M^{\rm std}(\psi_\epsilon,\rho_\epsilon),
\]

where

\[
 H_M^{\rm std}=
 \sum_y\frac{\rho_y^2}{2\chi}
 +\frac c2\sum_{y,i}(\psi_{y+e_i}-\psi_y)^2
 +\frac r2\sum_y\psi_y^2
 +\frac g4\sum_y\psi_y^4.
\]

The eight sectors do not interact in v0.  The primary audit proves the
side-four operator Gram conjugacy in all three directions and checks exact
termwise energies at sides 4, 8 and 12.  Those fixtures corroborate, but do
not replace, the index-level all-`N=4m` proof above.

## 4. Meaning of the eight nodes

The coarse harmonic symbol is

\[
 K_{\rm coarse}(q)=r+4c\sum_i\sin^2(q_i/2).
\]

For every sign vector `sigma`, the fine branch about
`Q_sigma=(sigma_1*pi/2,sigma_2*pi/2,sigma_3*pi/2)` satisfies

\[
 4c\sum_i\cos^2(Q_{\sigma,i}+q_i/2)
 =4c\sum_i\sin^2(q_i/2).
\]

Each fine node is therefore a constant mode of one coarse species after the
staggered carrier is removed.  The cubic reciprocal-lattice closure found in
LT3 is compatible with this identity, but it is species bookkeeping rather
than evidence for one connected eight-node interaction.

The common fine stencil kernel has dimension eight.  Combining the block
identity with the LT3 complete-square classification gives exactly two
constant signs per coarse copy and therefore

\[
 2^8=256
\]

fine classical minima.  The executable ground fixture enumerates these 256
sign combinations.  The assertion that there are no additional minima is
imported from the registered LT3 complete-square theorem, not inferred from
enumerating only the candidates.

## 5. Finite quantum corollary and its provenance

Let `U_T` be the `L2` unitary induced by the signed coordinate permutation.
On the algebraic tensor core, the differential and multiplication terms give

\[
 U_T H_N U_T^{-1}
 =\sum_{\epsilon} I\otimes\cdots\otimes
 H_M^{\rm std,(\epsilon)}\otimes\cdots\otimes I.
\]

The equality extends to the registered self-adjoint realizations by their
quadratic forms.  The LT3 finite confining-Schrodinger theorem supplies a
unique positive ground for each block, so the fine ground is the inverse
unitary image of their tensor product.

This is an analytic consequence of the exact coordinate factorization,
standard tensor-product operator facts and imported ground uniqueness.  The
scripts do not claim an independent numerical test of unbounded operator
domains.  The product ground is symmetric and selects neither one species nor
one of the 256 classical signs.

## 6. Restricted connected-standard-scalar no-go

Consider one real scalar on a connected finite graph with positive edge
weights `J_xy`, uniform onsite potential and positive inertia:

\[
 H_{\rm conn}=
 \sum_x\frac{\Pi_x^2}{2\chi}
 +\frac12\sum_{xy}J_{xy}(\psi_x-\psi_y)^2
 +\frac r2\sum_x\psi_x^2
 +\frac g4\sum_x\psi_x^4.
\]

At `r=0`, positivity of every edge term and connectedness give

\[
 \ker L_J=\{\text{constant fields}\},
\]

so the configuration Hessian, and therefore the full phase-space Hessian,
has nullity one.  ST8 has nullity eight.  If an invertible `C1` canonical map
identifies two Hamiltonians up to a positive scale and additive constant at a
critical point, their Hessians are related by an invertible congruence and
have the same nullity.  Thus no such exact identification exists.

For `r<0`, the comparator also obeys

\[
 H_{\rm conn}+\frac{V r^2}{4g}
 =\text{kinetic}+\text{positive Dirichlet squares}
 +\frac g4\sum_x(\psi_x^2+r/g)^2.
\]

Connectedness forces a constant field, and the onsite squares leave exactly
the two signs.  ST8 has 256.  This supplies a second obstruction.

The conclusion is narrow.  It does not exclude noninvertible reduction,
constraints or quotients, extra species, enlarged unit cells, auxiliaries,
signed or frustrated couplings, higher-range or higher-derivative stencils,
controlled infrared equivalence, or a connected one-field model with a
nonstandard positive-square stencil.  In particular, it is false that every
connected one-field parent must have only one node.

<a id="section-7-declared-harmonic-regulator-family"></a>
## 7. Declared harmonic regulator family

This section introduces a new family; it is not an automatic limit of the
fixed-spacing LT3 parent.  Let `a` be the coarse spacing, so the inherited fine
spacing is `a/2`.  Write the physical continuum stiffness as `c_phys` and set

\[
 c_{\rm LT3}(a)=c_{\rm phys}/a^2
\]

with `chi` fixed.  Suppressing the `phys` subscript below, the harmonic symbol
is

\[
 K_a(k)=r+\frac{4c}{a^2}
 \sum_i\sin^2(ak_i/2).
\]

At fixed physical momentum,

\[
 K_a(k)=r+c|k|^2
 -\frac{ca^2}{12}\sum_i k_i^4+O(a^4).
\]

Thus the fixed-band harmonic limit is the Klein--Gordon symbol
`r+c|k|^2`.  This proves only symbol convergence.  It does not prove
interacting classical convergence, a quantum continuum measure, counterterm
removal or state convergence.

For

\[
 \omega_a(k)^2=K_a(k)/\chi,
\]

direct differentiation gives

\[
 |\nabla_k\omega_a|^2=
 \frac{c^2\sum_i\sin^2(ak_i)}
 {a^2\chi\left(r+4c a^{-2}\sum_i\sin^2(ak_i/2)\right)}.
\]

The exact identity

\[
 4\sin^2(z/2)-\sin^2 z=4\sin^4(z/2)\geq0
\]

implies

\[
 |\nabla_k\omega_a|^2\leq c/\chi
\]

for `r>0`.  At `r=0`, the same statement holds off the zero mode and yields
the corresponding Lipschitz envelope at it.  This speed uses coarse physical
momentum.  The factor-of-two difference from the LT3 fine-node coordinate is
exactly the relation between coarse spacing `a` and fine spacing `a/2`:

\[
 (a/2)^2\frac{4c_{\rm LT3}(a)}{\chi}
 =\frac{c_{\rm phys}}{\chi}.
\]

Thus both descriptions give the same physical speed
`sqrt(c_phys/chi)`.

<a id="section-8-exact-pa-h1-tangent-calibration"></a>
## 8. Exact PA-H1 tangent calibration

Use the registered PA-H1 spatial circle, not an isospectral substitute:

\[
 L=\pi/2,\qquad
 e_0=\sqrt{2/\pi},\quad
 e_c=2\cos(4x)/\sqrt\pi,\quad
 e_s=2\sin(4x)/\sqrt\pi.
\]

Select one coarse species, one spatial axis and the transverse-zero sector.
Choose

\[
 c/\chi=1,\qquad r=-9\chi/2.
\]

At the ordered constant background `Phi_0^2=-r/g`, the potential curvature is

\[
 r+3g\Phi_0^2=-2r=9\chi.
\]

The three normalized modes then have

\[
 \Omega^2=\operatorname{diag}(9,25,25),\qquad
 \Omega=(3,5,5).
\]

This exactly matches the registered PA-H1 quadratic spectrum and basis
normalization.  It is nevertheless a tuned classical tangent calibration:
the species, axis, transverse sector and ratios were inserted.  No nonlinear
PA-H1 flow, quantum-state embedding, characteristic trace or selection law is
derived.

<a id="section-9-continuous-time-exact-support-obstruction"></a>
## 9. Continuous-time exact-support obstruction

On a coarse periodic graph, let

\[
 A=\mu I+cL,\qquad \chi\ddot q+Aq=0,
\]

with `mu,c,chi>0`, `q(0)=delta_0` and `q_dot(0)=0`.  Then

\[
 q(t)=\cos(t\sqrt{A/\chi})\delta_0
 =\sum_{n\geq0}\frac{(-1)^n t^{2n}}{(2n)!\chi^n}A^n\delta_0.
\]

For a nearest neighbour `e`, `A_{e0}=-c`, hence

\[
 q_e(t)=\frac{c}{2\chi}t^2+O(t^4).
\]

It is nonzero for every sufficiently small positive `t`.  Given any proposed
finite strict support speed `v`, choose such a time with

\[
 t<d(0,e)/v.
\]

The response is then nonzero outside `d<=vt`.  A side-four distance-two
control independently gives

\[
 q_{2e}(t)=\frac{c^2}{12\chi^2}t^4+O(t^6).
\]

Therefore this continuous-time semidiscrete harmonic propagator has no exact
compact-support cone.  The calculation also excludes a uniform exact cone for
a differentiable nonlinear law with this linearization.  It does not compute
an interacting quantum commutator and does not exclude exponential
Lieb--Robinson bounds, a controlled Lorentzian continuum limit, an exact-causal
discrete-time rule or a separately supplied hyperbolic continuum parent.

## 10. Why this does not yet reconstruct a characteristic boundary

The PA-H1 double-null package proves a characteristic reconstruction only
after a `1+1` Lorentzian diamond, null coordinates and characteristic data are
inserted.  ST8 supplies none of the following:

1. two characteristic sheets from the parent dynamics;
2. corner compatibility and constraint data;
3. a cutoff-uniform interacting limit;
4. symplectic flux convergence;
5. restriction of the same selected parent state;
6. a dimension-changing bulk-to-boundary map;
7. gravity or a global event horizon.

The finite lattice tail shows precisely why the harmonic speed alone cannot
fill this gap.

## 11. Energy-reference boundary

The LT3 same-Hamiltonian classical result remains valid:

\[
 H_{\min}=-Vr^2/(4g)<H(0,0)=0
\]

for `r<0`.  The block factorization explains its eight-sign multiplicity but
does not create a normalized quantum no-condensate state or identify physical
empty space.  Additive constants remain conventional.  No below-empty-space
physical claim is made.

## 12. Adversarial review

### Objection 1: the staggered sign is not periodic for every even N

**VALID with the stated restriction.**  It is periodic only when `M=N/2` is
even.  The theorem uses `N=4m`; the executable `N=6` control records the twist.

### Objection 2: the operator check at N=4 cannot prove every N

**VALID with provenance separation.**  The general proof is the index
relabeling in Sections 2--3.  The side 4, 8 and 12 calculations are regression
fixtures, not finite sampling promoted to a theorem.

### Objection 3: eight nodes imply eight interacting physical valleys

**UPHELD against that interpretation.**  The exact nonlinear factorization
shows eight decoupled species in v0.  Physical-valley or unified-bulk language
is not licensed.

### Objection 4: enumerating 256 candidates proves there are no more minima

**VALID with imported authority.**  Exhaustion comes from the LT3
complete-square theorem.  The new executable enumerates the factorized sign
corollary only.

### Objection 5: the quantum tensor statement was numerically proved

**DISMISSED as a description of this package.**  It is explicitly an analytic
corollary of coordinate unitarity, tensor domains and the imported standard
finite-ground theorem; no finite occupation truncation is used.

### Objection 6: the PA-H1 frequency match is hardcoded

**DISMISSED at calculation scope, VALID at selection scope.**  The scripts
derive the ordered curvature from `r+3gPhi_0^2`, integrate the exact
`L=pi/2` basis and compute the energy matrix.  The ratios and selected sector
are declared inputs, so the match is calibration rather than prediction.

### Objection 7: a bounded group speed is already a strict causal cone

**UPHELD as false.**  The exact nearest-neighbour Taylor coefficient gives a
nonzero response outside every proposed finite strict cone at sufficiently
small time.

### Objection 8: absence of a strict cone means arbitrarily large observable
signals

**DISMISSED.**  The theorem concerns exact support.  It leaves quasi-local
exponential bounds and effective wave-packet velocities open.

### Objection 9: no connected real-scalar parent can have eight nodes

**UPHELD as too broad.**  The registered no-go covers only exact equivalence
to one connected standard positive-edge scalar of the same phase dimension.
Nonstandard positive-square stencils can evade it.

### Objection 10: the symbol limit proves the interacting quantum continuum

**UPHELD as false.**  Only fixed-band harmonic symbol convergence and its
leading error are proved.  Uniform nonlinear estimates, counterterms, state
convergence and characteristic reconstruction remain open.

### Objection 11: the speed has a hidden factor of two

**DISMISSED after fixing units.**  `a` is the coarse spacing and the inherited
fine spacing is `a/2`.  Coarse momentum is twice the fine deviation coordinate;
the two registered speed formulas then agree.

### Objection 12: negative classical energy is below physical empty space

**UPHELD as an overclaim.**  The comparison is only to the zero field in the
same additive convention.  Physical empty space remains unidentified.

## 13. Reproduction

From the repository root, run:

```powershell
& 'E:\Dev\TECT.venv\Scripts\python.exe' codes/foundations/pre_a_cp1_st8_block_causal_bridge.py --self-test
& 'E:\Dev\TECT.venv\Scripts\python.exe' codes/foundations/pre_a_cp1_st8_block_causal_bridge_independent.py --self-test
& 'E:\Dev\TECT.venv\Scripts\python.exe' codes/foundations/pre_a_cp1_st8_block_causal_bridge_verify.py --self-test
```

The primary route uses exact SymPy algebra.  The independent route does not
import it and uses standard-library `Fraction`, direct lattice arithmetic,
Fourier evaluation, quadrature controls and direct matrix products.  The
integrator reruns both routes, compares stored artifacts, checks upstream
authority and scope, and rejects missing negative-result and no-overclaim
anchors.

## 14. Prior-art and novelty boundary

Staggered variables, block decomposition, zone folding, lattice species
doubling, finite-difference continuum symbols, semidiscrete dispersive
propagation and Lieb--Robinson quasi-local bounds are established ideas.  In
particular, harmonic and anharmonic lattice locality estimates appear in
Nachtergaele--Raz--Schlein--Sims (arXiv:0712.3820) and Raz--Sims
(arXiv:0902.0025), while semidiscrete wave dispersion is studied by
Marica--Zuazua (arXiv:1008.0197).

The repository's prior-art matrix found no single compatible source closing
the entire declared Pre-A sequence.  That negative search is not proof of
novelty or a world-first result.  The contribution here is the exact
convention-level audit of this particular LT3 parent against the PA-H1 and CP1
contracts.

## 15. Final boundary

Established here:

- exact finite canonical and nonlinear eight-block factorization;
- folded-species interpretation of the eight nodes;
- finite quantum tensor factorization as an analytic corollary;
- a narrow exact-equivalence no-go for one connected standard scalar;
- a declared harmonic fixed-band Klein--Gordon symbol limit and group-speed
  bound;
- exact PA-H1-geometry tuned ordered tangent frequencies `(3,5,5)`;
- absence of a strict compact-support cone for the continuous-time harmonic
  lattice regulator.

Not established here:

- an interacting classical or quantum continuum limit;
- a selected PA-H1 species, sector or state;
- nonlinear PA-H1 embedding;
- two-sheet characteristic reconstruction, corner constraints or symplectic
  state restriction;
- one connected bulk;
- physical empty space or a below-empty-space sign;
- cooling, gravity or an event horizon;
- CP1 or Pre-A completion.
