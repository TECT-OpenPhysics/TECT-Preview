# EXP-001080 finite structured-cutoff Q3 audit

## Decision

This checkpoint advances the QFT interface at tier T0 only.  It constructs a
finite, explicitly declared two-site oscillator regularization of the registered
Q3 onsite Hamiltonian and bond, computes the full-H Gibbs state, and compares
the full and smoothly coordinate-cutoff Heisenberg evolutions of a bounded
configuration character.  The two-sided Gibbs seminorm and the commutator with
the same full Hamiltonian (the finite-Gibbs modular derivative) are both
computed.  No thermodynamic, OS, KMS, GNS, continuum, C6, Sector-A or Pre-A
claim is made.

## Reproducible checks

```text
PRIMARY FINITE-STRUCTURED-CUTOFF-Q3 PASS 212/212
INDEPENDENT FINITE-STRUCTURED-CUTOFF-Q3 PASS 162/162
INTEGRATED FINITE-STRUCTURED-CUTOFF-Q3 PASS 94/94; Lean=PASS
```

The integrated lane runs the two scripts separately, compares every dimension
and cutoff summary within the declared `1e-7` tolerance, and compiles
`verification/lean/Tect/R262.lean` with the pinned Lake toolchain.

## Finite model

For each `n` in `{4,6,8,10}`, each site has the truncated oscillator

\[
q=(a+a^*)/\sqrt 2,\qquad p=(a-a^*)/(i\sqrt 2).
\]

The onsite term is

\[
h_x=p_x^2/(2\chi)+r q_x^2/2+g q_x^4/4,
\]

and the two-site bond is

\[
B=c(q_1-q_2)^2/2+\lambda(q_1-q_2)^2(q_1^2+q_2^2)/4.
\]

The fixture is `chi=1`, `r=-1`, `g=3/5`, `c=1`, `lambda=1/10`, `beta=1`,
and character amplitude `a=1/4`.  The cutoff replaces each `q` by the
declared cosine-taper spectral multiplier `q_L`, with
`L` in `{3/4,1,5/4,3/2}`.  The state is the normalized Gibbs state of the full
Hamiltonian, not of the cutoff Hamiltonian.

For `D_L(t)=alpha_t^H(A)-alpha_t^{H_L}(A)`, the recorded seminorm is

\[
N_{\beta,#}(X)^2=\operatorname{Tr}(\rho X^*X)+
\operatorname{Tr}(\rho XX^*),
\]

and the modular companion is `delta_H(D_L)=i[H,D_L]/hbar`.  The configuration
character commutes with the bond tail, so the first boundary derivative at
`t=0` vanishes in the finite matrix model; this is checked directly.

## Observed finite diagnostics

The static two-sided tail decreases across the four declared radii for every
tested oscillator dimension and stays above the numerical floor `1e-6`.  Across
all dimensions, times, and radii, the largest measured ratios are

```text
max N_beta,#(D_L(t)) / (|t| N_beta,#(B-B_L)) = 0.38845601874272084
max N_beta,#(delta_H D_L(t)) / N_beta,#(B-B_L) = 1.4854915307864307
```

The second number is not a theorem or a negative result.  It records that the
modular companion is numerically load-bearing even after the static tail is
small, and that four finite oscillator sizes do not supply a dimension- or
volume-uniform constant.

## Adversarial boundary

1. Truncated oscillator matrices do not preserve the exact CCR or the domains
   of the infinite Q3 operators.
2. The cosine taper is a finite structured-cutoff test, not the infinite-volume
   multiplier theorem.
3. The Gibbs state is full-H and both seminorm legs are retained; no dual-state
   equality is assumed.
4. The observed ratios are diagnostics only.  They neither prove nor refute a
   uniform estimate as `n` or lattice volume tends to infinity.
5. Lean R262 checks rational fixture algebra and the scope firewall, not the
   floating-point matrix exponentials or any unbounded limit.

The live gate remains the analytic, volume/source-uniform projected Duhamel
and modular-C1 estimate on a common Q3 core, followed by a common faithful
representation, exhaustion independence, group law, Hamiltonian-to-OS
identification, and common KMS dynamics.  The GNS gap, continuum, C6,
Sector A, Pre-A, and the canonical `heat_root_incidence`/A1/R-192 production
owner remain outside this checkpoint.
