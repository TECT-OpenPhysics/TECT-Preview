# Pre-A CP1/CL8 Q3 thermodynamic pressure and specific entropy density

Date: 2026-08-04  
Candidate: `PA-CP1-CL8-Q3-THERMODYNAMIC-PRESSURE-RELATIVE-ENTROPY-DENSITY-AND-PHASE-ROUTE-SPLIT-v0`  
Result: `PA-CP1-CL8-Q3-FIXED-BETA-VOLUME-COHERENT-NELSON-PRESSURE-SPECIFIC-RELATIVE-ENTROPY-AND-PERIODIC-LOCAL-SCHWINGER-LIMIT`  
Authority: claim-nonbearing T0 analytic theorem

## 1. Scoped theorem

Fix

\[
 m_0>0,\qquad g>0,\qquad \lambda\geq0,\qquad
 0<\beta<\infty .                                      \tag{1.1}
\]

Let `K_pl` be one fixed real symmetric eight-by-eight matrix and let `e_pl`
be one fixed scalar density.  On the eight-component massive plane Gaussian
field define

\[
 P_{\rm pl}(q)={1\over2}q^TK_{\rm pl}q+W_4(q),          \tag{1.2}
\]

where

\[
 W_4(q)={g\over4}\sum_e q_e^4
 +{\lambda\over4}\sum_{e\sim f}
 (q_e-q_f)^2(q_e^2+q_f^2).                             \tag{1.3}
\]

The family on every periodic rectangle `T_beta x S_L` is required to be the
same plane-Wick action expressed in the finite-volume Wick coordinates below.
For this volume-coherent family:

1. Nelson coordinate exchange gives a thermodynamic relative-pressure limit;
2. its raw sign depends on the additive scalar density convention;
3. the specific relative entropy of the free reference with respect to the
   interacting periodic law has a strictly positive, scalar-invariant limit;
4. periodic Schwinger functionals with bounded transfer-representable local
   insertions have an infinite-line limit at this externally fixed beta and
   mix exponentially in spatial separation.

This is not a theorem about a full noncommutative infinite-volume KMS algebra,
arbitrary `L`-dependent matrices, physical empty space, absolute vacuum energy,
the zero-temperature limit, the original fixed-raw CL8 regulator or Pre-A.

## 2. Plane-to-torus covariance and exact volume coherence

All coincident covariances in this section are first compared with one common
ultraviolet cutoff.  Their difference has a cutoff-free limit.  The massive
method-of-images formula gives

\[
 D^{\rm pl}_{\beta,L}:=C_{\beta,L}-C_{\rm pl}
 ={1\over2\pi}\sum_{(n,r)\in\mathbb Z^2\setminus\{(0,0)\}}
 K_0\!\left(m_0\sqrt{n^2\beta^2+r^2L^2}\right)>0.     \tag{2.1}
\]

Mass positivity makes the image sum absolutely convergent.  Relabelling the
two integers proves the exact exchange symmetry

\[
 D^{\rm pl}_{\beta,L}=D^{\rm pl}_{L,\beta}.            \tag{2.2}
\]

For the Q3 graph Laplacian `L_Q3`, put

\[
 A_{Q3}=(g+\lambda)I_8+\lambda L_{Q3},\qquad
 G=g+4\lambda,\qquad \operatorname{Tr}A_{Q3}=8G.       \tag{2.3}
\]

The exact EXP-000774 Wick dictionary, now with `C_star=C_pl`, says that the
same plane interaction is represented in whole-torus Wick order by

\[
 K_{\beta,L}=K_{\rm pl}+3D^{\rm pl}_{\beta,L}A_{Q3},   \tag{2.4}
\]

\[
 e_{\beta,L}=e_{\rm pl}
 +{D^{\rm pl}_{\beta,L}\over2}\operatorname{Tr}K_{\rm pl}
 +6(D^{\rm pl}_{\beta,L})^2G.                          \tag{2.5}
\]

Indeed, coefficient by coefficient,

\[
 :P_{K_{\beta,L}}:_{C_{\beta,L}}+e_{\beta,L}
 =:P_{K_{\rm pl}}:_{C_{\rm pl}}+e_{\rm pl}.           \tag{2.6}
\]

The same statement on a zero-temperature circle of circumference `L` uses

\[
 a_L=C_{*,L}-C_{\rm pl}
 ={1\over\pi}\sum_{n\geq1}K_0(m_0nL),                 \tag{2.7}
\]

\[
 K_{*,L}=K_{\rm pl}+3a_LA_{Q3},\qquad
 e_{*,L}=e_{\rm pl}+{a_L\over2}\operatorname{Tr}K_{\rm pl}
 +6a_L^2G.                                              \tag{2.8}
\]

Equations (2.4)--(2.8) are extra structure.  An arbitrary list of fixed-circle
EXP-000774 matrices is not a thermodynamic family.

Separate the image sum in (2.1) into the two coordinate axes and the mixed
winding sector:

\[
 D^{\rm pl}_{\beta,L}=a_\beta+a_L+M_{\beta,L},         \tag{2.9}
\]

\[
 M_{\beta,L}={1\over2\pi}
 \sum_{n\ne0,\,r\ne0}
 K_0\!\left(m_0\sqrt{n^2\beta^2+r^2L^2}\right)>0.    \tag{2.10}
\]

Massive exponential decay gives

\[
 D^{\rm pl}_{\beta,L}\longrightarrow a_\beta,\qquad
 e_{\beta,L}\longrightarrow e_{*,\beta}               \tag{2.11}
\]

as `L->infinity`.  In the first orientation `H_L` below is represented by
the circle-vacuum coordinates `K_(*,L),e_(*,L)` of (2.8).  After exchange,
`H_beta^perp` uses `K_(*,beta),e_(*,beta)`.  This is the explicit bridge from
one plane action to both Hamiltonians.

## 3. The finite-component constructive input

For every finite circumference, the quartic stability estimate

\[
W_4(q)\geq {g\over32}|q|^4                           \tag{3.1}
\]

dominates the arbitrary quadratic part.  More explicitly,

\[
 P_{\rm pl}(q)+e_{\rm pl}
 \geq {g\over32}|q|^4-{\|K_{\rm pl}\|\over2}|q|^2+e_{\rm pl}
 \geq e_{\rm pl}-{2\|K_{\rm pl}\|^2\over g}.           \tag{3.2}
\]

This is the bounded-below polynomial input to the transfer construction.
EXP-000774 supplied the
component-indexed Wick-kernel estimates, product hypercontractivity, closed
lower-bounded Hamiltonian form, direct limiting Feynman--Kac--Nelson formula,
compact resolvent, positivity improvement and simple ground for the
eight-component nonradial Q3 interaction.  Those estimates depend on a finite
list of components and monomials; radial symmetry is not used.

The cited scalar constructive results establish the Nelson-symmetry mechanism.
The present theorem uses their proof with the finite Q3 index set and the exact
coherence identity (2.6).  The executable checks audit the finite-index
algebra and limiting spectral identities; they do not replace the analytic
constructive theorem.

## 4. Nelson coordinate exchange and the pressure limit

Let `H_L` denote quantization on the spatial circle `S_L`, with Euclidean time
circumference `beta`.  Quantize the identical plane-Wick rectangle after
interchanging its axes.  This gives a transfer Hamiltonian
`H_beta^perp` on the dual spatial circle `S_beta`; its Euclidean time has
length `L`.  Because (2.1)--(2.6) are invariant under the exchange, the common
finite-cutoff identity passes to the Feynman--Kac limit:

\[
 Z^{\rm rel}_{\beta,L}
 ={\operatorname{Tr}e^{-\beta H_L}
   \over\operatorname{Tr}e^{-\beta H_{0,L}}}
 ={\operatorname{Tr}e^{-L H_\beta^\perp}
   \over\operatorname{Tr}e^{-L H_{0,\beta}}}.          \tag{4.1}
\]

Normalize the free ground energy to zero and write

\[
 E_\beta=\inf\operatorname{spec}H_\beta^\perp.        \tag{4.2}
\]

Both dual heat operators are trace class.  Compact resolvent gives the direct
spectral asymptotics

\[
 \lim_{L\to\infty}{1\over L}\log Z^{\rm rel}_{\beta,L}
 =-E_\beta.                                             \tag{4.3}
\]

Consequently the declared raw relative pressure exists:

\[
 p_{\rm rel}(\beta)
 :=\lim_{L\to\infty}{1\over\beta L}\log Z^{\rm rel}_{\beta,L}
 =-{E_\beta\over\beta}.                               \tag{4.4}
\]

This is an existence theorem, not an invariant sign theorem.  Adding a scalar
density `c` to the interaction sends

\[
 H_\beta^\perp\mapsto H_\beta^\perp+c\beta I,quad
 E_\beta\mapsto E_\beta+c\beta,quad
 p_{\rm rel}\mapsto p_{\rm rel}-c.                    \tag{4.5}
\]

Thus an unqualified statement that the raw pressure or vacuum-energy density
is below empty space is not defined until an external scalar reference is
fixed.

## 5. Finite-volume relative entropy identity

Let `mu_(beta,L)` be the free periodic Gaussian law and write the interacting
law as

\[
 {d\nu_{\beta,L}\over d\mu_{\beta,L}}
 ={e^{-I_{\beta,L}}\over Z^{\rm rel}_{\beta,L}}.       \tag{5.1}
\]

Here `I_(beta,L)` includes the declared plane-Wick interaction and its scalar
density in the chosen convention.  Direct substitution gives

\[
 D(\mu_{\beta,L}\Vert\nu_{\beta,L})
 =\log Z^{\rm rel}_{\beta,L}
  +\mathbb E_{\mu_{\beta,L}}I_{\beta,L}.               \tag{5.2}
\]

A scalar shift adds `c beta L` to the expectation and subtracts the same
quantity from `log Z`.  Equation (5.2) is therefore exactly scalar invariant.

The whole-torus form of the same action makes the insertion limit exact before
any thermodynamic passage.  Gaussian expectation of every whole-torus Wick
monomial vanishes, so

\[
 \mathbb E_{\mu_{\beta,L}}I_{\beta,L}
 =\beta L e_{\beta,L}.                                 \tag{5.3}
\]

Equations (2.11) and (5.3) give

\[
 \lim_{L\to\infty}{1\over L}
 \mathbb E_{\mu_{\beta,L}}I_{\beta,L}
 =\beta e_{*,\beta}=:T_\beta.                          \tag{5.4}
\]

On the dual circle, circle-vacuum Wick ordering gives directly

\[
 T_\beta=\langle\Omega_{0,\beta},V_\beta
 \Omega_{0,\beta}\rangle
 =q_{H_\beta^\perp}[\Omega_{0,\beta}].                 \tag{5.5}
\]

No coupling derivative or interchange of such a derivative with the
thermodynamic limit is used.  Combining (4.3), (5.2) and (5.4),

\[
 \lim_{L\to\infty}{1\over L}
 D(\mu_{\beta,L}\Vert\nu_{\beta,L})
 =T_\beta-E_\beta.                                    \tag{5.6}
\]

## 6. Strictness from the Q3 four-particle witness

The variational principle with the free-vacuum trial already gives

\[
 T_\beta-E_\beta\geq0.                                 \tag{6.1}
\]

The Q3 interaction makes it strict.  Choose one component and the normalized
four-zero-mode vector `chi` on `S_beta`.  The coefficient of its pure quartic
is `(g+3lambda)/4`; hence the dual closed-form cross term is

\[
 A_\beta=q_{H_\beta^\perp}(\chi,\Omega_{0,\beta})
 ={(g+3\lambda)\sqrt{4!}\over16\beta m_0^2}>0.        \tag{6.2}
\]

The free and quadratic parts do not connect the vacuum to four particles.
Put `B_beta=q[chi]`, which is finite.  For

\[
 \psi_t={\Omega_{0,\beta}-t\chi\over\sqrt{1+t^2}},    \tag{6.3}
\]

the form expectation relative to the free-vacuum trial is

\[
 q[\psi_t]-T_\beta
 ={ -2tA_\beta+t^2(B_\beta-T_\beta)\over1+t^2}<0      \tag{6.4}
\]

for all sufficiently small positive `t`.  Therefore

\[
 E_\beta<T_\beta.                                     \tag{6.5}
\]

The strict scalar-invariant specific relative entropy per Euclidean area is

\[
 \boxed{
 s_{\rm rel}(\beta)
 :=\lim_{L\to\infty}{D(\mu_{\beta,L}\Vert\nu_{\beta,L})
 \over\beta L}
 ={T_\beta-E_\beta\over\beta}>0.}                     \tag{6.6}
\]

Equivalently, with the centered dual Hamiltonian

\[
 \widehat H_\beta=H_\beta^\perp-T_\beta I,            \tag{6.7}
\]

its ground energy is strictly negative and

\[
 \lim_{L\to\infty}-{D(\mu_{\beta,L}\Vert\nu_{\beta,L})
 \over\beta L}
 ={E_0(\widehat H_\beta)\over\beta}<0.                \tag{6.8}
\]

This is the rigorous thermodynamic descendant of the fixed-volume
below-named-Gaussian-reference comparison.  It is not a physical-empty-space
identification.

## 7. Periodic bounded-local Schwinger limit and transfer mixing

Positivity improvement and compact resolvent give a unique normalized dual
ground `Omega_beta` and, because the next eigenvalue is isolated,

\[
 \delta_\beta=E_{1,\beta}-E_\beta>0.                   \tag{7.1}
\]

After removing the scalar `E_beta`, the normalized transfer semigroup
converges to the ground projection.  Insert any fixed finite collection of
bounded transfer-representable local multiplication observables into (4.1).
The trace formula then gives convergence of the associated periodic Schwinger
functionals.  This is a bounded-local Euclidean functional limit across the
increasing spatial circles, not convergence of global density matrices living
on different Hilbert spaces.

The same spectral expansion gives, for transfer-representable bounded local
observables separated by spatial distance `r`, a connected-correlation bound
of the form

\[
 |\langle AB_r\rangle-\langle A\rangle\langle B\rangle|
 \leq C_{A,B}e^{-\delta_\beta r}.                       \tag{7.2}
\]

where fixed support widths are absorbed into `C_(A,B)`.  This proves transfer
mixing for that bounded observable class.  Ground projection alone does not
construct a common noncommutative infinite-volume local algebra or its time
dynamics.  A full beta-KMS state requires an explicit finite-component
Gerard--Jaekel/Araki--Woods local-algebra bridge and remains open, together with
uniqueness among all possible boundary conditions and every statement uniform
as `beta->infinity`.

## 8. What remains open

The strict theorem (6.6) compares two named mathematical laws.  The free
Gaussian law uses inserted `m0`, Euclidean geometry and field normalization.
`K_pl` and `e_pl` instead specify the interacting comparison theory and its
scalar convention.  No argument here derives the Gaussian law as cosmic empty
space.  The raw sign (4.4) can be changed by (4.5), so no absolute
gravitational vacuum-energy zero is fixed.

Positive specific relative entropy normally means the total relative entropy
grows extensively.  The result concerns finite-volume restrictions and their
density.  It does not assert a finite global Radon--Nikodym derivative or
finite total relative entropy between infinite-volume measures.

The following remain separate gates:

- arbitrary volume-dependent `K_L,e_L` families;
- `beta->infinity` and `L->infinity` interchange;
- a zero-temperature thermodynamic ground-energy density;
- spontaneous symmetry breaking or a phase transition;
- uniqueness for all boundary conditions;
- a full noncommutative infinite-volume local algebra and beta-KMS state;
- interacting Hadamard or microlocal-spectrum control;
- the original fixed-raw CL8 and three-dimensional Q3LOCK parent;
- physical light, C0, N1--N5, C6, CP1, Sector A and Pre-A.

## 9. Prior art boundary

Guerra, Rosen and Simon proved Nelson symmetry and infinite-volume vacuum
energy results for scalar `P(phi)_2`:

- `Commun. Math. Phys. 27 (1972) 10--22`, DOI
  `10.1007/BF01649655`;
- `Commun. Math. Phys. 29 (1973) 233--247`, DOI
  `10.1007/BF01645249`.

Gerard and Jaekel treat one real scalar field with a real bounded-below
polynomial in `arXiv:math-ph/0403048`: Proposition 5.4 supplies the circle
Hamiltonian and unique ground, while Sections 6--7 supply their thermodynamic
KMS/local limit and clustering mechanism.  They do not state the vector Q3
theorem, and their local-algebra bridge is not silently imported here.  Nagoji's
`arXiv:2305.19583` supplies broad finite-torus multivariate polynomial
normalizability, not this thermodynamic Q3 theorem.

Those works establish the mechanism but do not state the arbitrary
eight-component nonradial Q3 result verbatim.  This package supplies the
finite-index adaptation and exact TECT Wick/reference interface.  It does not
claim that Nelson symmetry, pressure limits or thermal transfer theory are new,
and it does not claim a world-first result.

## 10. Adversarial review

1. **Fixed-L strictness automatically survives per unit length. UPHELD AS
   FALSE.**  An `O(1)` improvement can vanish after division by `L`; Nelson
   exchange and the dual strict witness are essential.
2. **Any EXP-000774 matrix family has a thermodynamic limit. UPHELD AS
   FALSE.**  Equations (2.4)--(2.8) or an equivalent volume-coherence theorem
   are required.
3. **The raw pressure sign is invariant. UPHELD AS FALSE.**  Equation (4.5)
   is an exact scalar-shift counterexample.
4. **The KL sign has the opposite scalar correction. DISMISSED.**  Direct
   substitution in (5.1) gives `D=log Z+E_mu I`; the two scalar changes cancel.
5. **A factor of beta is missing. DISMISSED.**  `D/L=T_beta-E_beta`, while the
   density per Euclidean area is `(T_beta-E_beta)/beta`.
6. **The free-vacuum variational bound proves strictness by itself. UPHELD AS
   FALSE.**  It gives only nonnegativity; the nonzero four-particle form
   matrix element proves strictness.
7. **The quadratic term could cancel the witness. DISMISSED.**  It changes
   particle number by at most two, whereas (6.2) is a vacuum-to-four-particle
   matrix element.
8. **Strong semigroup convergence alone passes periodic traces. UPHELD AS
   FALSE.**  The proof uses the direct limiting Feynman--Kac--Nelson theorem
   and its trace-ideal domination, inherited from EXP-000774.
9. **A unique dual ground proves all-boundary uniqueness or no phase
   transition. UPHELD AS FALSE.**  Only the periodic bounded-local Schwinger
   limit at fixed beta is registered.
10. **Positive specific KL gives a global density. UPHELD AS FALSE.**  The
    theorem is about finite-volume/local restrictions; total KL is extensive.
11. **Ground projection alone constructs the full infinite-volume KMS algebra.
    UPHELD AS FALSE.**  The finite-component local-algebra and time-dynamics
    bridge remains an explicit open gate.
12. **The named Gaussian reference is physical empty space. UPHELD AS
    UNPROVED.**  Its mass, Euclidean geometry and field normalization are
    inserted; `K_pl,e_pl` belong to the interacting comparison theory.
13. **This closes Pre-A. UPHELD AS FALSE.**  The zero-temperature/reference,
    microlocal, three-dimensional parent and C0/N1--N5 gates remain open.

## 11. Reproduction

Run:

```text
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_q3_thermodynamic_pressure_relative_entropy_density_phase_route_split.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_q3_thermodynamic_pressure_relative_entropy_density_phase_route_split_independent.py --self-test
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_q3_thermodynamic_pressure_relative_entropy_density_phase_route_split_verify.py --self-test
```

The scripts verify the exact algebra, factors, spectral limits, KL identity,
strict witness, scalar mutations, record integrity and every scope firewall.
