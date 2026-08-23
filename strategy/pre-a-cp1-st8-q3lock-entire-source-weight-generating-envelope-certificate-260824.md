# EXP-001032 certificate: conditional entire source-weight envelope

## Finding

For the prescribed repeated onsite words from EXP-001031, the exact absolute
coefficient at `q=r=0` is

\[
|R_m(a)|=m c\left(\frac{G}{4}\right)^{m-1}|a|^{4m-3}.
\]

The factorial generating sum therefore has the exact exponential form

\[
\sum_{m\ge1}\frac{t^m}{m!}|R_m(a)|
 =c t|a|\exp\!\left(\frac{tG}{4}|a|^4\right).
\]

The candidate entire source weight

\[
w_\sigma(a)=(1+|a|)\exp(\sigma|a|^4)
\]

dominates this prescribed-word sum whenever `sigma >= tG/4`, leaving a ratio
at most `c t`.  For the fixture `g=3/5`, `lambda=2/7`, `c=2/3`, `t=1/3`, the
rate is `17/140`; with `sigma=1/5` the margin is `11/140` and the prefactor is
`2/9`.  The primary lane passes 14/14, the independent lane passes 13/13, the
integrated lane passes 22/22, and Lean R216 passes.

## Conditional boundary

This is an entire-weight envelope for a declared prescribed-word family, not
the actual Q3 first-passage theorem.  The Q3 Duhamel word incidence, onsite
cancellations, six-neighbour and reverse-orientation coefficients, domain
continuity, volume-uniform history summability, exhaustion Cauchy, common alpha,
KMS, ground/GNS gap and continuum remain open.  The weight is a candidate
topology, not a representation-independent result.

## Adversarial review

- **Word-family assumption — UPHELD:** the exponential identity is applied only
  to the prescribed coefficients from EXP-001031.
- **Weight topology — UPHELD:** the entire weight is a candidate input; no
  domain or representation-independent seminorm theorem is claimed.
- **Finite truncation — UPHELD:** finite Taylor checks verify positive terms but
  do not replace the infinite Q3 history theorem.
- **Volume and orientations — UPHELD:** no six-neighbour path count, reverse
  orientation sum, or exhaustion estimate is supplied.
- **Lean promotion — UPHELD:** R216 checks rational rate, margin and prefactor
  arithmetic only.
- **QFT-to-TECT promotion — UPHELD:** no `heat_root_incidence` or A1/R-192
  production owner is supplied.

## Next gate

Define this entire source seminorm on the actual Q3 common core and prove the
six-neighbour, two-orientation, volume-uniform history bound.  Only after that
should exhaustion Cauchy and the QFT interface be attempted.
