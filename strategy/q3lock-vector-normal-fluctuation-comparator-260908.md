# Q3LOCK vector normal-fluctuation literature comparator

Date: 2026-09-07.  Status: T0 comparison-only literature audit; no analytic
import, novelty or priority claim, result-tier change, submission, or PDF.

## Question

Does the earlier vector-oscillator literature already provide the
positive-lambda, non-radial eight-component Q3LOCK phase-coexistence theorem,
or does it only provide a quantum-stabilization/normal-fluctuation
comparator?

## Primary sources inspected

1. Y. Kozitsky, *Quantum Effects in a Lattice Model of Anharmonic Vector
   Oscillators*, **Letters in Mathematical Physics 51** (2000), 71--81,
   DOI [10.1023/A:1007675606191](https://doi.org/10.1023/A:1007675606191).
   The accessible primary abstract describes a model of (D)-dimensional
   quantum anharmonic oscillators with polynomial anharmonicity and a
   ferroelectric pair interaction.  Its stated result is bounded/normal
   displacement fluctuations under a strong-quantum condition for all
   (D,d), not a low-temperature multiplicity or source-cusp theorem.

2. Y. Kozitsky, *Quantum Effects in an Anharmonic Crystal*, **Condensed
   Matter Physics 5** (2002), 601--616, DOI
   [10.5488/CMP.5.4.601](https://doi.org/10.5488/CMP.5.4.601),
   [author-hosted PDF](https://icmp.lviv.ua/journal/zbirnyk.32/001/art01.pdf).
   The printed model has (D)-component oscillators with a radial polynomial
   onsite term (V((q_l,q_l))) and a ferroelectric translation-invariant
   interaction.  Theorem 1 bounds nonzero Matsubara susceptibilities; Theorem
   2 gives a strong-quantum sufficient condition for bounded static
   susceptibility at all temperatures.

## Q3LOCK comparison

The Q3LOCK onsite block is a positive-λ, endpoint-weighted non-radial
polynomial on (mathbb R^8), and the claimed conclusion is instead a
finite-temperature strict collective-source cusp followed by two
zero-source tempered Euclidean DLR states related by global (Z_2) parity.
The two Kozitsky vector papers therefore do not directly supply the Q3LOCK
phase-coexistence conclusion.  Their fluctuation/stabilization estimates are
useful context and possible method comparators, but no theorem, hypothesis
reduction, or constant is imported from them here.

This is not an absence or priority result.  The accessible material does not
settle whether another anisotropic continuous-oscillator theorem covers the
Q3LOCK polynomial.  A specialist literature reviewer must give the final
disposition before content freeze.

## Adversarial boundary

- Vector dimension alone is not enough: the cited models use radial or
  isotropic onsite structure, whereas Q3LOCK uses a non-radial Q3 locking
  polynomial.
- A bounded susceptibility or quantum-stabilization theorem is not a
  positive cusp or DLR-multiplicity theorem.
- The comparator does not discharge A1--A23 and does not change R-497 from T0
  or `claim_bearing=false`.

## Next gate

Add this comparator to the manuscript crosswalk and bibliography, send the
exact source boundary to the literature specialist, and keep the signed
literature disposition and all proof rows open.  No PDF is generated at this
checkpoint.
