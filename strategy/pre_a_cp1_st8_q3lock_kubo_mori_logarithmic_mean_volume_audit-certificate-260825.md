# EXP-001089 — actual-Q3 Kubo–Mori logarithmic-mean volume audit certificate

## Decision

The Kubo–Mori/Duhamel logarithmic-mean state topology is implemented for the
declared finite actual-Q3 models and is independently reproduced. It is
smaller than the arithmetic-mean comparison in these Gibbs states, but its
modular companion still grows across volumes 2, 4, and 6. The finite result
therefore does not provide the source/volume-uniform multiplier required by
the projected `D,delta-D` QFT gate. This is a route-local candidate diagnosis,
not a no-go theorem for every common-core topology.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_kubo_mori_logarithmic_mean_volume_audit.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_kubo_mori_logarithmic_mean_volume_audit_independent.py --self-test
python -X utf8 codes/foundations/pre_a_cp1_st8_q3lock_kubo_mori_logarithmic_mean_volume_audit_verify.py
lake env lean Tect/R271.lean
```

The primary lane passes 67/67, the independent lane passes 58/58, the
integrated verifier passes 47/47, and R271 compiles with no warnings, `sorry`,
`admit`, `axiom`, or `unsafe`. The canonical JSON artefacts are under
`claims/C6-SPACETIME-SIGNATURE/runs/2026-08-25-primary-pre_a_cp1_st8_q3lock_kubo_mori_logarithmic_mean_volume_audit/` and the independent run has its matching sibling directory.

## Model and exact finite identity

The finite models use oscillator dimension three on a two-site edge, a
four-site square face, and a six-site 2x3 rectangular grid. The observable is

\[
A_2=\exp\!\left(i a(q_0+q_1)/\hbar\right),\qquad a=1/3,
\]

and the smooth cosine cutoff changes only bond coordinates. With
`W_L=H-H_L` and `B=[W_L,[H,A_2]]`, the direct second coefficient is
`D''(0)=-B/hbar^2`. Its modular companion is evaluated as

\[
\delta D''(0)=-\beta[H,D''(0)]
 =\frac{\beta}{\hbar^2}[H,[W_L,[H,A_2]]].
\]

In the eigenbasis of the uncut full-volume Hamiltonian, the normalized Gibbs
probabilities are `p_i`. The Kubo–Mori/Duhamel weight is

`L(p_i,p_j)=(p_i-p_j)/(log p_i-log p_j)`,

with diagonal limit `L(p_i,p_i)=p_i`; the two-sided square norm is
`2*sum_ij L(p_i,p_j)|X_ij|^2`. The comparison weight replaces `L` by
`(p_i+p_j)/2`. R271 checks the diagonal-limit convention, symmetry, scalar
modular coefficient/sign, graph counts, and finite-only scope exactly over
the rationals. It does not claim to formalize floating-point spectral norms
or a thermodynamic limit.

## Results

The maxima over the declared radii are:

| volume | Kubo–Mori modular weighted | arithmetic modular weighted | Kubo–Mori direct weighted | arithmetic direct weighted |
|---:|---:|---:|---:|---:|
| 2 | 1.7578318425 | 2.1370416950 | 0.8072302323 | 0.9410369228 |
| 4 | 4.7969614982 | 7.3775956341 | 1.1972791969 | 1.7020060967 |
| 6 | 6.8384686282 | 11.9136100135 | 1.3418087918 | 2.1061615784 |

The exact direct-weighted values are present in the canonical JSON; the
decision uses the modular rows because the projected gate requires control of
the modular companion. Relative to volume two, the volume-six growth factors
are `3.8902860119` for Kubo–Mori and `5.5748140251` for the arithmetic
comparison. Arithmetic-to-Kubo–Mori modular ratios rise from
`1.2157258978` to `1.7421458898`. Source and disjoint-tail commutators remain
below `1e-8` in every row, and the radius-two tail is at the `1e-9` numerical
floor.

## Adversarial review

1. **Logarithmic-mean diagonal limit:** equal Gibbs probabilities use the
   exact limit `p_i`; both lanes avoid zero-log-gap division. **UPHELD.**
2. **State representation:** both lanes use the uncut full-volume Gibbs
   eigenbasis with normalized positive probabilities. **UPHELD.**
3. **Modular identity:** `delta D''=-beta[H,D'']` is compared to the explicit
   nested commutator without a Jacobi reorder. **UPHELD.**
4. **Support locality:** source and disjoint-tail commutators are measured in
   every volume and radius. **UPHELD.**
5. **Mean comparison:** the arithmetic mean is a comparison topology, not a
   replacement for the Kubo–Mori weight. **UPHELD.**
6. **Volume interpretation:** ratios use only volumes 2, 4, and 6; they are
   finite diagnostics, not asymptotic lower bounds. **UPHELD.**
7. **Independent reconstruction:** the independent lane rebuilds the model,
   cutoff, Gibbs state, commutators, and mean matrices without importing the
   primary lane. **UPHELD.**
8. **Lean boundary:** R271 checks exact rational fixtures and scope labels,
   not numerical spectral limits. **UPHELD.**
9. **QFT promotion:** uniform direct `D,delta-D` Cauchy, modular domain,
   product/core density, exhaustion, common dynamics/KMS, OS/GNS, gap,
   continuum, C6, Sector A, and Pre-A remain open. **UPHELD.**

## Boundary and next action

Closed here: finite Kubo–Mori/Duhamel and arithmetic state-weighted rows, the
finite modular identity, support-local commutation, independent reproduction,
and R271. Open: a source/volume-uniform weighted common-core theorem and the
downstream direct `D,delta-D` Cauchy gate. The next route is to derive a local
cancellation or alternative state topology with an analytic uniform
multiplier, or to enlarge the structured family and prove a route-specific
lower-bound obstruction for this exact candidate. No common-alpha or QFT
identification is promoted from this package.

Provenance hashes:

```text
primary       3e9af9daae717d5b8ea73fa9a9eea42fcbf4b454717f10a18cc255a9280183b5
independent   3f3d150e5d487bed4683cd90413c032f92053d03bcb31dd02bfe3a694de1cae3
manifest      05dd344d7e0e7a4d63aa42ed2a063a1a39df5cf57f604b102eebe5d42f35a18d
R271          05a4309a488af580cdb0ff03d6732f565828e9ba05a5172965b6b87e183fb420
```
