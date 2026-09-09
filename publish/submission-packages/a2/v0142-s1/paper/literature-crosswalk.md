# Literature-first crosswalk for the A2/R-157/R-158 paper

Status: bounded draft crosswalk, 2026-09-04.  This file records applicability
and residual novelty; it is not a claim promotion or a world-first search.

## Target statements

1. Global well-posedness and smoothing for the declared fourth-order,
   three-component, regularized gradient flow on a fixed torus.
2. Exact neutral minimizer and radial derivative inequalities for the pinned
   functional.
3. Exact finite-torus spectral/ensemble completion and first-order
   grand-potential coexistence after imposing `Q` or `mu`.

## Primary-source dispositions

| source | exact role considered | crosswalk disposition |
|---|---|---|
| A. Giorgini, CPAA 15 (2016), 219--241, DOI `10.3934/cpaa.2016.15.219` | scalar Swift--Hohenberg slow/fast well-posedness and attractors | `DOES-NOT-APPLY` as a complete theorem: scalar equation and different nonlinear structure; useful background only |
| A. Pazy, *Semigroups of Linear Operators* (1983) | analytic semigroup and fractional estimates | `APPLIES` as standard background, with the operator positivity and domains checked in Sec. 4 |
| H. Amann, *Linear and Quasilinear Parabolic Problems* (1995) | quasilinear parabolic existence framework | `APPLIES-CONDITIONALLY`: the declared Class-II map must satisfy the displayed local Lipschitz and order-two estimates |
| J. Kargol, Y. Kondratiev, Y. Kozitsky, arXiv:0710.2303 | Euclidean Gibbs/DLR phase-transition methods, infrared and reflection tools | `DOES-NOT-APPLY` to the present classical finite-torus theorem; not used as a load-bearing premise |
| Aubin--Lions compactness and polynomial Bregman identities | standard functional-analytic/algebraic tools | `APPLIES` under the spaces and coefficient signs explicitly checked in the manuscript |

## Crosswalk checks

- **Object and symmetry:** the paper uses the pinned P1 functional, six real
  components, real pairing, positive density floor, and fixed periodic torus.
  It does not silently substitute the historical solver or a scalar slice.
- **Signs and domains:** the fourth-order symbol is positive, the Class-II
  matrix is positive definite, and the radial matrix is checked for every
  `theta` in `[0,1]`.  Removing the floor or changing the pairing is outside
  scope.
- **Limits:** all PDE and ensemble conclusions are finite-torus statements.
  No thermodynamic, continuum, zero-temperature, or source-removal limit is
  imported or implied.
- **Ensemble boundary:** `Q` and `mu` are imposed mathematical parameters.
  No conserved-charge or reservoir conclusion is imported from the literature.
- **Independent check:** the registered primary, non-importing independent,
  integrated, and Lean sidecar audits are listed in `verification/README.md`.
  They verify algebra and provenance, not every analytic lemma.

## Residual proposition

The residual model-specific content is the exact combination of the full
regularized Class-II continuum estimate, the neutral global rejection, and
the imposed-ensemble shell completion.  A specialist literature search and
external proof audit are still required before making a novelty or submission
readiness claim.


## Specialist-source expansion (2026-09-04)

This bounded primary-source search was run to test whether a single existing
result already subsumes the paper's combined theorem.  The search covered
APS/DOI records, arXiv, the JETP archive, and a university journal record, using
queries for vector Swift--Hohenberg well-posedness, multicomponent Brazovskii
functionals, fourth-order quasilinear flows, and rigorous PFC minimizers.  No
source below is used as a load-bearing premise.

| source | exact feature inspected | disposition for this paper |
|---|---|---|
| S. A. Brazovskii, ``Phase transition of an isotropic system to a nonuniform state,'' Sov. Phys. JETP 41, 85 (1975), [JETP record](https://jetp.ras.ru/cgi-bin/index/r/68/1/p175?a=list) | fluctuation theory for scalar/vector order parameters with a nonzero-momentum minimum | `DOES-NOT-APPLY` as a proof: it is a fluctuation/field-theory analysis, not the declared finite-torus exact variational theorem |
| J. Swift and P. Leitner, ``Models for phase transitions with continuous constant energy surfaces,'' Phys. Rev. B 16, 4137 (1977), [APS DOI](https://doi.org/10.1103/PhysRevB.16.4137) | continuous nonzero-wavevector energy surfaces and fluctuation-driven transition order | `DOES-NOT-APPLY` to the exact fixed-shell completion; the geometry and statistical treatment differ |
| T. Asai, ``Quasilinear parabolic equation and its applications to fourth order equations with rough initial data,'' J. Math. Sci. Univ. Tokyo 19 (2012), 507--532, [journal record](https://www.ms.u-tokyo.ac.jp/journal/abstract_e/jms190402_e.html) | continuous-maximal-regularity framework for fourth-order quasilinear equations | `APPLIES-CONDITIONALLY` as background only; the present constant fourth-order operator and order-two Class-II lower-order map require a model-specific verification |
| G. Martine-La Boissoniere, R. Choksi, and J.-P. Lessard, ``Microscopic Patterns in the 2D Phase-Field-Crystal Model,'' arXiv:2102.02338 (2021), [arXiv record](https://arxiv.org/abs/2102.02338) | rigorously validated numerical steady states and local minimizers for scalar 2D PFC | `DOES-NOT-APPLY` as a theorem for this work: dimension, scalar field, constraint, flow, and proof target differ |

The bounded search did not identify a source proving the full conjunction of
(a) a three-component complex field with the positive-floor derivative
Class-II term, (b) the fixed side-16 periodic torus, (c) the exact neutral
radial rejection, and (d) the imposed-charge/chemical-potential completion.
This is a bounded non-subsumption result, not a priority or world-first claim.
A specialist literature search and novelty opinion remain required before any
submission-readiness statement.

## Current quasilinear amplitude-theory check (2026-09-04)

Two 2026 primary sources were added because they are closer to the evolution
part of the paper than the earlier scalar Swift--Hohenberg references.  Their
presence narrows the residual contribution: quasilinear or fully nonlinear
Swift--Hohenberg analysis, maximal regularity, and small-amplitude modulation
are not claimed as new here.

| source | exact feature inspected | disposition for this paper |
|---|---|---|
| T. Belin and G. Schneider, ``On the Ginzburg--Landau approximation for quasilinear pattern forming reaction--diffusion--advection systems,'' *Chaos* 36 (2026), 053129, [DOI](https://doi.org/10.1063/5.0324316), [arXiv record](https://arxiv.org/abs/2601.16145) | maximal-regularity justification of a Ginzburg--Landau approximation for quasilinear reaction--diffusion--advection systems near first instability, with a Gray--Scott--Klausmeier application | `DOES-NOT-SUBSUME`: it is a small-amplitude modulation result near instability for a different second-order system, not the present all-data fourth-order torus flow or either exact variational theorem |
| T. Belin and G. Schneider, ``A Ginzburg--Landau approximation theorem for quasilinear pattern-forming systems in uniformly local Sobolev spaces,'' arXiv:2608.19035 (v1, 2026), [arXiv record](https://arxiv.org/abs/2608.19035) | one-dimensional fully nonlinear Swift--Hohenberg example $u_t=-(1+\partial_x^2)^2u+\varepsilon^2u-\partial_x^4(u^3)$ and an $O(\varepsilon^{3/2})$ modulation estimate on $0\le t\le T_0/\varepsilon^2$ in uniformly local Sobolev spaces | `DOES-NOT-SUBSUME`: the theorem is a finite-long-time small-amplitude approximation on $\mathbb R$, not all-data global well-posedness for the present three-component $\mathbb T^3_{16}$ gradient flow, and it contains no neutral radial or ensemble minimization conclusion |
| B. Hilder and C. Kuehn, ``Pattern formation and nonlinear waves close to a 1:1 resonant Turing and Turing--Hopf instability,'' arXiv:2508.21183 (v1, 2025), [arXiv record](https://arxiv.org/abs/2508.21183) | coupled Swift--Hohenberg system with dispersive terms; rigorous coupled complex Ginzburg--Landau approximation near simultaneous resonant instabilities; selected global spatially periodic solutions | `DOES-NOT-SUBSUME`: this is a near-instability amplitude-reduction and selected-solution theorem, not all-data global $H^2$ well-posedness for the present three-dimensional gradient flow, and it supplies neither the neutral radial theorem nor the imposed-ensemble minimization identities |
| M. Becker, T. Frenzel, T. Niedermayer, S. Reichelt, A. Mielke, and M. B\"ar, ``Local control of globally competing patterns in coupled Swift--Hohenberg equations,'' *Chaos* 28 (2018), 043121, [WIAS primary record](https://www.wias-berlin.de/publications/wias-publ/run.jsp?number=2457&template=abstract&type=Preprint&year=2017), [DOI](https://doi.org/10.1063/1.5018139) | weakly nonlinear analysis and simulations for two anti-symmetrically coupled one-dimensional Swift--Hohenberg equations, with spatial coexistence of dynamically stable patterns and interface control | `DOES-NOT-SUBSUME`: the amplitude equations are formally justified and the coexistence notion concerns spatially competing patterns; it is not an all-data three-dimensional gradient-flow theorem or equality classification of global constrained/grand-potential minimizers |

This check establishes only a documented non-subsumption comparison.  The
Hilder--Kuehn paper materially narrows any broad claim about rigorous coupled
Swift--Hohenberg analysis, while the Becker et al. paper separates dynamical
pattern coexistence from the variational coexistence proved here.  It does
not replace a specialist search, citation-chain review, or independent novelty
opinion.

## Focused primary-source additions (2026-09-03)

The following primary records were inspected after the first bounded crosswalk
to test the two closest possible subsumption routes: rigorous Swift--Hohenberg
evolution and multicomponent/constrained Brazovskii minimization.

| source | exact feature inspected | disposition for this paper |
|---|---|---|
| G. W. Duchesne, J.-P. Lessard, and A. Takayasu, ``A rigorous integrator and global existence for higher-dimensional semilinear parabolic PDEs via semigroup theory,'' arXiv:2402.00406 (v2, 2025), [arXiv record](https://arxiv.org/abs/2402.00406), related DOI `10.1007/s10915-024-02785-x` | computer-assisted global existence and convergence for scalar 2D/3D Swift--Hohenberg and a derivative-bearing Ohta--Kawasaki application | `DOES-NOT-SUBSUME`: the validated semilinear/scalar framework does not prove the present three-component regularized Class-II analytic flow, exact radial neutral rejection, or imposed-shell ensemble identities |
| Y. Ruan, ``Nontrivial Periodic Minimizer for Landau-Brazovskii Model with Constraint,'' arXiv:1603.06181 (v2, 2016), [arXiv record](https://arxiv.org/abs/1603.06181) | self-contained constrained Landau--Brazovskii variational construction of a nontrivial periodic minimizer | `DOES-NOT-SUBSUME`: the model and reduction target differ from the six-real-component fourth-order flow, the neutral radial sign theorem, and the grand-potential coexistence statement |
| C. Bao, C. Chen, and K. Jiang, ``An adaptive block Bregman proximal gradient method for multicomponent coupled-mode Swift--Hohenberg models,'' *CSIAM Trans. Appl. Math.* 3 (2022), 133--171, [full text](https://global-sci.com/index.php/csiam-am/article/download/7797/15528) | constrained multicomponent coupled-mode PFC discretization, algorithmic convergence, and binary/ternary/quinary numerical experiments | `DOES-NOT-SUBSUME`: the result is a finite-dimensional numerical optimization analysis, not the present continuum well-posedness proof or exact finite-shell/Bregman completion |
| L. Mi, W. Cui, and H. You, ``Periodic and Quasi-Periodic Solutions for the Complex Swift--Hohenberg Equation,'' *J. Appl. Anal. Comput.* 10 (2020), 297--313, [journal record](https://www.jaac-online.com/article/doi/10.11948/20190152) | one-dimensional complex Swift--Hohenberg periodic and quasi-periodic solutions obtained with an infinite-dimensional KAM theorem | `DOES-NOT-SUBSUME`: the equation is not the declared real gradient flow and has no matching Class-II coefficient, neutral rejection, or imposed-charge ensemble |

These additions sharpen the residual proposition but do not certify novelty or
priority.  A specialist must still review the broader literature, verify every
scope comparison, and decide whether the combined theorem package is
publishably distinct.
