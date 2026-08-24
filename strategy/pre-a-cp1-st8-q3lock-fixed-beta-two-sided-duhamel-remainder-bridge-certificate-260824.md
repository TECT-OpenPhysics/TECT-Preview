# EXP-001062 / fixed-beta two-sided Duhamel remainder bridge

## Decision

The exact local Q3 force coefficient can be inserted into a standard
two-sided second-order Duhamel remainder estimate on the already registered
fixed-beta OS-mixture word class, provided the finite-member orbit has a
uniform second-derivative bound.  This is a conditional finite-member bridge;
the positive-time orbit bound is recorded as the next live gate rather than
being inferred from the static endpoint moment.

## Bound

For a finite-volume orientation σ define

\[
 R_\sigma(t)=\tau_\sigma(t)(W_a)-\tau_0(t)(W_a)
             -t(\mathcal L_\sigma-\mathcal L_0)(W_a).
\]

The Q3 bond is a configuration multiplier, so the last term vanishes for the
configuration character \(W_a\).  If the word-class seminorm satisfies

\[
 \sup_{0\le s\le T}\|R_\sigma''(s)\|_{\beta,\#}\le K_\sigma(T),
\qquad R_\sigma(0)=R_\sigma'(0)=0,
\]

then the Bochner/Fundamental-Theorem identity gives

\[
 \|R_\sigma(t)\|_{\beta,\#}\le \frac{t^2}{2}K_\sigma(T),
 \qquad
 \|R_+(t)-R_-(t)\|_{\beta,\#}
 \le \frac{t^2}{2}\bigl(K_+(T)+K_-(T)\bigr).                 \tag{1.1}
\]

If the first modular derivation \(\mathfrak m\) commutes with the two
Hamiltonian derivations on this word class and has a separate bound
\(K_{\sigma,\mathfrak m}(T)\), the same argument gives the identical estimate
for \(\mathfrak mR_+-\mathfrak mR_-\).  This is the direct \(D,\delta D\)
shape required by the open Hamiltonian-identification gate, but only after
the orbit bounds are proved uniformly in volume and source.

## Static coefficient insertion

EXP-001061 supplies the initial endpoint moment
\(M_{\rm bridge}^{\rm compact}=35834571/64\).  Combining it with the exact
force constant \(C=122099/35840\), \(w=\max(1,8/g)=40/3\), and the character
amplitude \(|a|=1/4\) gives

\[
 K_{\rm initial}^4
 =\left(\frac{|a|}{\hbar\chi}\right)^4 C^4 w^3M_{\rm bridge}^{\rm compact}
 =\frac{884928390316245388540002019}{1267165160779284480}.
\]

The smallest integer safety ceiling is \(K_{\rm initial}\le163\).  For the
fixture \(T=1/100\), the declared conditional orbit inputs
\(K_\sigma(T)=163\) and \(K_{\sigma,\mathfrak m}(T)=2\cdot163\) produce

\[
 \frac{T^2K_\sigma(T)}2=\frac{163}{20000},\quad
 \|R_+-R_-\|_{\beta,\#}\le\frac{163}{10000},\quad
 \|\mathfrak mR_+-\mathfrak mR_-\|_{\beta,\#}\le\frac{163}{5000}.
\]

These are exact rational fixtures, not thermodynamic constants.

## Adversarial review

1. **Taylor remainder — UPHELD.**  The \(t^2/2\) factor uses both zero initial
   data and an all-time second-orbit hypothesis; EXP-001061 is not promoted to
   that hypothesis.
2. **Orientation — UPHELD.**  Both orientations remain in the triangle bound;
   no parity identification is assumed.
3. **Modular derivative — UPHELD.**  A separate commutation/domain condition
   and a separate modular bound are required.
4. **Moment input — UPHELD.**  The compact-source endpoint bridge supplies only
   the initial coefficient, not the positive-time orbit envelope.
5. **Volume — UPHELD.**  The fixture is one finite member; no exhaustion or
   volume-uniform claim is made.
6. **Topology — UPHELD.**  The \(\|\cdot\|_{\beta,\#}\) seminorm is the existing
   fixed-beta mixture target, not a newly constructed Hamiltonian embedding.
7. **Lean — UPHELD.**  R244 checks rational identities and the safety ceiling,
   not unbounded domains or convergence.
8. **QFT/TECT — UPHELD.**  No GNS gap, continuum, C6, Sector A, Pre-A or
   canonical TECT production-owner conclusion follows.

## Boundary and next gate

EXP-001062 advances the QFT-facing route by converting the exact local force
coefficient into the correct two-sided finite-time remainder shape and by
isolating the missing positive-time orbit estimate.  The next mathematical
target is a volume/source-uniform bound for the second orbit derivative (and
its modular companion) on the fixed-beta common word class.  Until that is
proved, direct \(D,\delta D\) Cauchy, exhaustion independence, Hamiltonian-to-OS
identification, common \(\alpha\), GNS gap, continuum, C6, Sector A and Pre-A
remain open.
