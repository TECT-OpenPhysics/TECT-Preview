# EXP-001063 / conditional orbit-EGF insertion into the fixed-beta Duhamel remainder

## Decision

The two conditional inputs registered in EXP-001048 can be composed with the
finite-member remainder of EXP-001062.  If the four central contexts are all
bounded by the one-step rate (B) and the actual two-orientation factorial
history has coefficients bounded by 
\(\eta^n\), then for (0\le\eta<1)

\[
 G(T)=\sum_{n\ge0}\eta^n=\frac1{1-\eta}
\]

is a conditional orbit envelope.  Replacing (K_{\rm initial}) by
\(K_{\rm initial}G(T)) in EXP-001062 gives the single-orientation and
two-orientation (t^2/2) remainder bounds, with the same separate modular
multiplier condition.

## Exact fixture

The registered weighted mixed graph rate is recomputed as

\[
B=\frac{1382807}{7168}.
\]

With two orientations, degree bound six, spatial base two and
\(T=1/10000\),

\[
 \eta=2\cdot6\cdot2\,B\,T=\frac{4148421}{8960000}<1,
 \qquad
 G(T)=\frac{8960000}{4811579}.
\]

Using the EXP-001062 safety ceiling (K_{\rm initial}=163) gives

\[
 K_{\rm orbit}(T)\le\frac{1460480000}{4811579},
\]

and therefore

\[
 \|R_\sigma(T)\|_{\beta,\#}\le\frac{4564}{3007236875},
\quad
 \|R_+-R_-\|_{\beta,\#}\le\frac{9128}{3007236875}.
\]

For the declared modular multiplier two, the corresponding orientation bound
is (18256/3007236875).

## Adversarial review

1. **Rate provenance — UPHELD.**  The primary and independent lanes recompute
   (B) from the registered source fixture.
2. **Four contexts — UPHELD.**  The all-four-context estimate remains a
   hypothesis and is not inferred from EXP-001045.
3. **History — UPHELD.**  The geometric majorant assumes a nonnegative
   factorial history coefficient envelope; actual Q3 words, domains and
   cancellations remain open.
4. **Small time — UPHELD.**  The denominator is used only after the exact
   (eta<1) check at (T=1/10000).
5. **Orientation — UPHELD.**  Both directions remain in the triangle bound.
6. **Modular derivative — UPHELD.**  The modular multiplier and commutation
   condition are separate inputs, not a Hamiltonian-domain conclusion.
7. **Lean — UPHELD.**  R245 checks rational composition only.
8. **QFT/TECT — UPHELD.**  No thermodynamic identification, gap, continuum,
   C6, Sector A, Pre-A or TECT production owner follows.

## Boundary and next gate

EXP-001063 closes the scalar composition of the two conditional envelopes.  It
does not close the actual Q3 central-context or factorial-history theorem.  The
next mathematical step is therefore an operator-level four-context estimate
with both orientations and a genuine history recurrence; failure must be
recorded as an exact obstruction.
