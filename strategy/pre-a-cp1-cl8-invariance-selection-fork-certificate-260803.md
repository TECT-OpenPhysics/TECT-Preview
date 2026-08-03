<a id="section-1-verdict"></a>
# PA-CP1-CL8-INVARIANCE-SELECTION-FORK-v0

## 1. Verdict

This certificate closes two finite classical subgates and fires one narrow
selection no-go.

1. Every fixed periodic CL8 regulator has a global Liouville-preserving
   Hamiltonian flow and a normalized invariant canonical Gibbs law for every
   `beta>0`.
2. For `r<0`, two distinct compactly supported measures on smooth phases are common to the
   continuum and every regulator: the zero-equilibrium Dirac law and the
   symmetric mixture of the two collective ordered equilibria.  Both obey all
   direct periodic seam conditions and compose with exactly zero error.
3. Consequently normalization, dynamical invariance, the declared exact
   symmetries, smooth seam support, and exact regulator compatibility do not
   uniquely select a preferred classical boundary measure.

The parent gate
`PA-CP1-CL8-PREFERRED-STATE-COMPOSITION-SELECTION` remains open.  No
temperature, mean energy, reservoir, preparation history, quantum boundary
map, continuum quantum state, Hadamard state, physical empty space, or
below-empty-space comparison is derived.

The formal negative is
`NG-2026-08-03-PRE-A-CP1-CL8-INVARIANCE-ONLY-PREFERRED-STATE`.

<a id="section-2-prior-art"></a>
## 2. Prior-art and novelty boundary

Liouville's theorem, finite-dimensional Gibbs measures, energy-shell
measures, and invariant equilibrium Dirac laws are standard Hamiltonian and
statistical mechanics.  This is not a new general theorem and no world-first
claim is made.

The repository-specific content is the convention-level composition audit:

- the exact `a/8` CL8 symplectic and Hamiltonian normalization;
- the eight-species Q3 potential and its collective equilibria;
- the direct null-seam trace image;
- exact compatibility with every centered regulator;
- the distinction between invariant-measure existence and physical
  preference.

The corrected high-regularity authority is `EXP-000735`.  Nothing below uses
the uncorrected cumulative derivative display recorded historically in
`EXP-000734`.

<a id="section-3-finite-hamiltonian"></a>
## 3. Fixed finite CL8 Hamiltonian

Fix `L>0`, a finite integer `M>=2`, and `a=L/M`.  There are eight real field
and momentum components at each periodic node.  Write `d=8M` and

\[
 \Gamma_a=\mathbb R^d_\psi\times\mathbb R^d_\Pi .
\]

The inherited structures are

\[
 \Omega_a={a\over8}\sum_{j,e}d\Pi_{j,e}\wedge d\psi_{j,e},       \tag{3.1}
\]

\[
 H_a={a\over8}\sum_j\left{
 { |\Pi_j|^2\over2\chi}
 +{c\over2}|D_a^+\psi_j|^2+W(\psi_j)\right\},                  \tag{3.2}
\]

where

\[
 W(z)=\sum_e\left({r\over2}z_e^2+{g\over4}z_e^4\right)
 +{\lambda\over4}\sum_{e\sim f}
 (z_e-z_f)^2(z_e^2+z_f^2).                                    \tag{3.3}
\]

Throughout, `chi,c,g>0`, `lambda>=0`, and `r` is real.  The Hamilton equations
are exactly

\[
 \dot\psi_j={\Pi_j\over\chi},\qquad
 \dot\Pi_j=c\Delta_a\psi_j-\nabla W(\psi_j).                  \tag{3.4}
\]

The Liouville measure

\[
 d\Lambda_a={|\Omega_a^d|\over d!}                            \tag{3.5}
\]

is a positive constant multiple of ordinary Lebesgue measure.  Its constant
normalization will cancel from every probability law.

<a id="section-4-coercivity"></a>
## 4. Coercivity and the exact energy floor

Let `r_- = max(-r,0)`.  For one real component,

\[
 {r\over2}z^2+{g\over4}z^4
 \ge {g\over8}z^4-{r_-^2\over2g},                              \tag{4.1}
\]

because, in the hostile case `r=-r_-`, the difference plus the stated
constant is

\[
 {g\over8}z^4-{r_-\over2}z^2+{r_-^2\over2g}
 ={(gz^2-2r_-)^2\over8g}.                                    \tag{4.2}
\]

The Q3 term and spatial-gradient term are nonnegative.  Summing all
components therefore gives

\[
 H_a(\psi,\Pi)\ge
 {a\over16\chi}|\Pi|^2
 +{ag\over64}\sum_{j,e}\psi_{j,e}^4
 -{Lr_-^2\over2g}.                                           \tag{4.3}
\]

This weaker quartic bound is enough for integrability.  Completing the full
onsite square gives the sharper exact minimum

\[
 H_{\min,a}=-{Lr_-^2\over4g}.                                 \tag{4.4}
\]

For `r<0`, set `v=sqrt(-r/g)`.  Spatially and species-constant `+v` and `-v`
attain (4.4).  If `lambda>0`, Q3 connectivity makes these the only two global
minimum configurations; at `lambda=0` additional independent species signs
have the same energy.  Formula (4.4), not uniqueness of its minimizers, is all
that the Gibbs proof needs.

Since energy is conserved and its sublevel sets are compact by (4.3), no
finite-time phase-space escape is possible.  The polynomial Hamiltonian flow
is therefore global.

<a id="section-5-liouville-gibbs"></a>
## 5. Liouville invariance and the finite Gibbs family

In block form the derivative of the vector field is

\[
 DX_{H_a}=\begin{pmatrix}
 0&\chi^{-1}I\\
 c\Delta_a-D^2W&0
 \end{pmatrix}.                                               \tag{5.1}
\]

Its trace is zero.  Equivalently the mixed partials in canonical coordinates
cancel, so `div X_H=0`.  The global flow `Phi_a^t` preserves `dLambda_a` and
also preserves `H_a`.

For every `beta>0`, define

\[
 Z_{\beta,a}=\int_{\Gamma_a}e^{-\beta H_a}\,d\Lambda_a,
 \qquad
 d\mu_{\beta,a}=Z_{\beta,a}^{-1}e^{-\beta H_a}\,d\Lambda_a.
                                                                    \tag{5.2}
\]

The Gaussian momentum integral and quartic field integral implied by (4.3)
show

\[
 0<Z_{\beta,a}<\infty.                                        \tag{5.3}
\]

At `beta=0`, phase-space Lebesgue volume is infinite.  At `beta<0`, already
the momentum integral diverges.  Thus `beta>0` is the exact normalization
range for this canonical exponential family.

Both factors in (5.2) are invariant, hence

\[
 (\Phi_a^t)_*\mu_{\beta,a}=\mu_{\beta,a}.                     \tag{5.4}
\]

The momentum factor separates exactly.  Every momentum component has

\[
 \mathbb E_{\mu_{\beta,a}}\Pi_{j,e}^2={8\chi\over\beta a}.    \tag{5.5}
\]

Therefore different positive `beta` values give different invariant
probabilities.  All of them have strictly positive densities, full
noncompact support, finite polynomial moments, and the lattice-translation,
Q3, global-Z2, momentum-reversal, and time-reversal symmetries inherited from
the Hamiltonian.

More generally, every nonnegative Borel function `F` satisfying

\[
 0<\int F(H_a)d\Lambda_a<\infty                               \tag{5.6}
\]

defines another invariant probability after normalization.  For every
`E>H_min,a`, the normalized uniform law on `{H_a<=E}` is an especially useful
compactly supported control: the set is compact, has positive finite volume,
and is flow invariant.  Compact support therefore does not restore unique
preference; it merely replaces the inserted `beta` by an inserted `E`.

Differentiation under the finite partition integral gives

\[
 {d\over d\beta}\mathbb E_{\mu_{\beta,a}}H_a
 =-\operatorname{Var}_{\mu_{\beta,a}}(H_a)<0.                 \tag{5.7}
\]

The variance is strictly positive because `H_a` is nonconstant on a measure
with full support.  Momentum equipartition makes the mean energy diverge as
`beta` decreases to zero, while the finite-dimensional Laplace principle
gives the limit `H_min,a` as `beta` tends to infinity.  Hence prescribing a
mean energy above `H_min,a` selects exactly one `beta`.  The prescribed mean
energy is, however, an additional condition; autonomous invariance does not
derive it.

<a id="section-6-common-witnesses"></a>
## 6. Two common invariant measures on smooth phases

The Gibbs family proves finite-regulator nonuniqueness, but it does not by
itself lie in the compact common `C8` trace class used by the existing
composition theorem.  A sharper witness removes that possible objection.

Assume `r<0` and set `v=sqrt(-r/g)`.  Define the three periodic phases

\[
 \zeta_0=(\psi_e(x),\Pi_e(x))=(0,0),                           \tag{6.1}
\]

\[
 \zeta_\pm=(\psi_e(x),\Pi_e(x))=(\pm v,0)                     \tag{6.2}
\]

for all species and all `x`.  The onsite force is `rz+gz^3`, which vanishes
at `0` and `plus-or-minus v`.  Every Q3 edge force vanishes on the collective
diagonal, and every spatial derivative vanishes.  Thus all three phases are
fixed points of the continuum and every centered lattice flow.

Now set

\[
 \mu_{\rm zero}=\delta_{\zeta_0},\qquad
 \mu_{\rm ord}={1\over2}(\delta_{\zeta_+}+\delta_{\zeta_-}).   \tag{6.3}
\]

Both are compactly supported measures on smooth classical phases.  Both preserve
spatial translations, Q3 automorphisms, global Z2, momentum reversal, and
time reversal.  Their characteristic traces are simply

\[
 A=B=0,\qquad A=B=+v,\qquad A=B=-v.                            \tag{6.4}
\]

Every value and derivative periodic seam condition holds.  Goursat
reconstruction returns the same constant solution.  Sampling and
trigonometric reconstruction are exact at every `M`, and neither continuum
nor semidiscrete evolution moves the support.  Consequently their common
phase and Wasserstein composition errors are exactly zero, not merely
`O(a^2)`.

The two measures are nevertheless distinct.  Their supports are disjoint,
their field second moments differ, and in the identical raw Hamiltonian
convention

\[
 H_a(\zeta_0)=0,
 \qquad H_a(\zeta_\pm)=-{Lr^2\over4g}.                         \tag{6.5}
\]

No compactness, smoothness, seam, or regulator-limit loophole remains in this
particular nonselection witness.

<a id="section-7-no-go"></a>
## 7. Exact selection no-go

Suppose a proposed rule claims that the following properties uniquely define
a preferred classical CL8 boundary probability:

1. normalization;
2. invariance under the CL8 Hamiltonian flow;
3. spatial-translation, Q3, global-Z2, momentum-reversal, and time-reversal
   symmetry;
4. compact support on smooth direct-seam phases;
5. exact compatibility with every centered regulator.

Both measures in (6.3) satisfy every item and are different.  The claimed
unique selection is therefore false.  This proves the scoped no-go

`NG-2026-08-03-PRE-A-CP1-CL8-INVARIANCE-ONLY-PREFERRED-STATE`.

The no-go does not reject selection after adding a physically justified mean
energy, temperature, KMS condition, reservoir, entropy principle,
preparation history, symmetry-breaking boundary condition, or ground-support
criterion.  It proves that one of those or an equally discriminating input
is indispensable.

For example, when `r<0` and `lambda>0`, the parent complete-square theorem says
that the classical global-minimum set is exactly `{zeta_+,zeta_-}`.  Requiring
support on that set and global-Z2 invariance uniquely gives `mu_ord`.  This is
a valid conditional selector, but the minimum-energy rule is not derived as
the high-energy Pre-A preparation principle.

<a id="section-8-composition-boundary"></a>
## 8. Why the parent preferred-state gate remains open

The finite Gibbs measure has full noncompact support and changes with `a`.
It is not the single supplied compact common `C8` trace measure in the
existing `W1=O(a^2)` theorem.  Energy truncation gives compact finite-a
support, but inserts an energy cutoff and supplies no cutoff-uniform `C8`
family.  The equilibrium witness measures do compose exactly, but they show
nonselection rather than a physical selection principle.

A classical phase probability is also not a density operator or a state on a
noncommutative field algebra.  The nonlinear classical Goursat map and its
variational symplectic-flux identity do not define a quantum
`star`-homomorphism.  Nothing here constructs a finite quantum CL8 state,
intertwines it with a characteristic boundary algebra, removes the regulator,
or proves a Hadamard wavefront condition.

The successor gates are therefore:

- `PA-CP1-CL8-CLASSICAL-PREFERENCE-CRITERION`;
- `PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-STATE`;
- `PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER`;
- `PA-CP1-CL8-CONTINUUM-STATE-AND-HADAMARD-LIMIT`;
- `PA-CP1-COMMON-PARENT-PHYSICAL-STATE-AND-REFERENCE`.

The next bounded proof target is the finite-regulator quantum state.  It must
declare `hbar` and the exact CCR normalization before importing the standard
confining-Schrodinger ground and Gibbs theorems.

<a id="section-9-energy-reference"></a>
## 9. Energy-reference boundary

The Goursat proof shift `C_star=2r_-^2/g` adds a constant to the energy and
does not change the Hamiltonian vector field.  It multiplies `Z_beta,a` by a
constant exponential that cancels from the normalized Gibbs measure.  It also
leaves every fixed point and invariant probability unchanged.

This proves neither an absolute energy zero nor a comparison with physical
empty space.  `mu_zero` is a Dirac law on the classical zero configuration;
it is not a normalized quantum no-condensate state.  Equation (6.5) is a
same-Hamiltonian classical comparison only.

<a id="section-10-adversarial"></a>
## 10. Devil's-advocate review

1. **Objection: negative `r` makes the partition function divergent.**
   **DISMISSED.**  The positive quartic gives (4.3); the negative quadratic
   changes only a finite lower-bound constant.
2. **Objection: Hamiltonian conservation does not imply phase-volume
   conservation.**  **DISMISSED.**  The zero trace in (5.1) separately proves
   Liouville preservation.
3. **Objection: different beta values might define the same probability after
   normalization.**  **DISMISSED.**  Their exact momentum variances (5.5)
   differ.
4. **Objection: Gibbs noncompactness invalidates the selection no-go.**
   **DISMISSED.**  The two measures (6.3) have compact support on smooth
   direct-seam phases and are exactly regulator compatible.
5. **Objection: the ordered mixture secretly breaks Z2.**  **DISMISSED.**  The
   equal mixture is exactly Z2 invariant; neither individual ordered Dirac law
   is used as the symmetric witness.
6. **Objection: the zero equilibrium is physical empty space.**
   **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  It is only a classical fixed
   configuration and is not a quantum or empirical reference state.
7. **Objection: invariance nonuniqueness rules out every possible preferred
   state.**  **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  The no-go concerns only
   the listed invariance-and-symmetry data; an independent physical selection
   principle can discriminate.
8. **Objection: a classical invariant measure supplies the missing quantum
   state.**  **UPHELD AS AN OVERCLAIM AND EXCLUDED.**  No quantum algebra or
   boundary intertwiner is constructed.

<a id="section-11-reproduction"></a>
## 11. Reproduction

Run

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_invariance_selection_fork.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_invariance_selection_fork_independent.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_invariance_selection_fork_verify.py
E:\Dev\TECT.venv\Scripts\python.exe codes\foundations\pre_a_cp1_cl8_invariance_selection_fork_verify.py --check-stored
```

The primary route uses symbolic polynomial and Hamiltonian checks.  The
independent route uses rational arithmetic and direct finite fixtures without
importing the primary module.  The integrated verifier pins the parent
authorities, compares both derivations, checks the formal negative and scope,
and can compare the fresh integrated payload with the stored result without
overwriting it.

<a id="section-12-no-overclaim"></a>
## 12. No-overclaim boundary

This package proves finite-regulator classical Gibbs existence and two
distinct common invariant measures on smooth classical phases.  It refutes only unique
preference from invariance, declared symmetries, smooth seams, and regulator
compatibility alone.  It does not derive beta, energy, a reservoir,
preparation history, physical classical state, quantum or Hadamard state,
quantum boundary map, physical empty space, absolute or below-empty-space
energy, continuum or thermodynamic state limit, full 3+1 dynamics, gravity,
cooling, C6 advancement, CP1, or Pre-A.
