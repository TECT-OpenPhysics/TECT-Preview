# Semigroup-dressed Petz collar: proposed route

This document records a claim-nonbearing route design for T-054. It is a
candidate continuation of R-396, not a result certificate and not a tier or
gate change.

## 1. Why change the cutoff interface

R-394 and R-395 use a hard local energy window. Their finite Markov and gentle
inequalities are exact, but the adjacent-cutoff ratios are large. R-396 then
shows that a fixed projected reference state gives a valid finite Petz
transport budget, while its transported-error profile still changes with the
oscillator cutoff. The common difficulty is the rank-changing boundary of a
hard projector. A smoother interface should be tested before spending another
uniformity proof on the same discontinuous object.

## 2. Proposed construction

On a finite local core, shift the Hamiltonian to

\[
 K_L=H_L-\inf\sigma(H_L)\geq 0,
 \qquad F_s=\exp(-sK_L/2),\quad s>0.
\]

The filtered Gibbs state is

\[
 \rho_s=\frac{F_s\rho F_s}{m_s},
 \qquad m_s=\operatorname{Tr}(\rho e^{-sK_L}).
\]

The exact scalar inequality

\[
 1-e^{-sx}\leq sx\quad(x\geq0)
\]

gives the finite mass estimate

\[
 1-m_s\leq s\operatorname{Tr}(\rho K_L).
\]

This is useful because the filter has semigroup composition
`F_s F_t=F_(s+t)` and does not change rank when the cutoff moves. It also has
the interpretation of a finite Euclidean-time collar. The filtered state on
`A-B-C` supplies the BC and B reference marginals for one fixed Petz map, and
R-396's triangle/contractivity accounting is then reapplied to `rho_s`.

No normalized-filter trace-distance envelope is assumed. The first decisive
lemma is to derive one from the mass and a local energy moment, or to discover
by an increasing-cutoff test that such a dimension-safe envelope is false.

## 3. Finite discriminator

The proposed finite package reuses the complete R-396 grid and adds a small
positive grid of collar parameters `s`. For each row it records the filter
mass, normalized state, exact Petz recovery, semigroup composition, projected
and transported distances, and the profiles at fixed `s` and at a
moment-scaled `s`. It must preserve both orientations, all buffers, every
declared beta and source shape.

The independent lane rebuilds the filter and Petz map without importing the
primary implementation. The hostile lane intentionally omits normalization,
uses a hard projector while claiming smooth calculus, changes one exponential
leg, removes each displacement term, and reverses semigroup order. These
mutations are meant to fail before any analytic interpretation is made.

## 4. QFT-facing interface

The parameter `s` is Euclidean smoothing, not physical time. If the finite
collars admit a common local form-core limit, semigroup composition can be
compared with reflection-positive OS/KMS constructions. Only after a common
generator and analytic continuation are established may a Lorentzian
statement be considered. Heat-kernel positivity alone cannot provide a
finite-speed cone or the C6 signature claim.

## 5. Adversarial boundary

The mass estimate still depends on a cutoff-independent bound for the local
first energy moment. A small finite disturbance at one `s` does not prove a
uniform modulus. The Petz map must be held fixed from the filtered reference;
choosing a different map for the unfiltered state would erase the transport
question. Finally, Euclidean reflection positivity, KMS compatibility and
real-time common-alpha convergence are separate gates. Failure of any one of
these conditions leaves this route finite and claim-nonbearing.

## 6. Promotion and stop rule

Promotion requires the finite primary/independent/hostile/Lean package, a
dimension-safe normalized-filter lemma with explicit moment hypotheses, and a
cutoff/source/shape-stable shell modulus. If the filter mass collapses, if the
disturbance keeps growing at every admissible scaling, or if every modulus
requires a logarithmic dimension factor, the route is retired with that
scoped obstruction. No common-alpha, OS/KMS/GNS, mass-gap, continuum, C6,
Sector-A or Pre-A status changes follow from the proposal itself.
