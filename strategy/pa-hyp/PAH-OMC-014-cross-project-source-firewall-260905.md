# PAH-OMC-014 cross-project source firewall

## Purpose

This note records a read-only semantic audit of two external references that
contain sector-weight terminology. It does not import either reference into
TECT and does not alter PAH-001, PAH-OMC-010, PAH-OMC-012, or PAH-OMC-013.

## Exact search

The following search was run from the TECT workspace:

```powershell
$roots=@('E:\Dev\YangMills','E:\Dev\TECT-YM')
foreach($root in $roots){
  rg -n -i --glob '*.json' --glob '*.md' --glob '*.jsonl' --glob '*.tex' --glob '*.txt'  'PAH-OMC-014|w_\s*\(\s*n\s*,\s*R\s*,\s*Q\s*\)|cross-Q|sector.weight|sector weights' $root
}
```

An exact `PAH-OMC-014` search returned zero matches in both external roots.

## Audited references

1. `E:\Dev\YangMills\research_db
otes\2026-08-24-obl070-global-vacuum-projection.md`
   SHA-256: `c717d747733cea0e3384c25546092877d55ebeaafaf1338a3528dc7a8a5736c2`.
   The displayed `2^(-chi)` values are finite OS Gram quotient bookkeeping for
   one global vacuum label and 32 labelled sectors. The moving cross-Gram
   branch is an orthogonality diagnostic. It defines no PAH charge grade Q,
   fixed-Q Gibbs functional, cross-Q probability law, or cylinder projection.

2. `E:\Dev\TECT-YM\proof\61-sector-resolved-schur-core-lift.md`
   SHA-256: `e23ee3d99296105c18d0d4093a80c77bab8b0006533fbb9847be94674ee53915`.
   The symbols `w_n(sigma)` are endpoint/sector weights inside a proposed
   nonnegative Schur majorant. The note explicitly treats them as bookkeeping
   and requires separate equivalence with the physical norm. It supplies no
   PAH Q-indexed Gibbs mixture, normalization over Q, projective identity, or
   `mu_(n,R)` cylinder family.

## Disposition

Both candidates are semantically ineligible as the PAH-OMC-014 source-owned
sector law. This is an exclusion of two candidate imports, not a universal
no-go theorem: a future source owner may still provide a correctly typed,
hash-pinned law.

The active verdict therefore remains `HOLD_FOR_EVIDENCE`. The single required
payload is unchanged: a source-owned nonnegative normalized law
`w_(n,R,Q)` (or an equivalent projective kernel), together with its topology,
explicit cylinder error bound, holdout observable, and stationarity domain.

## Non-claims

- No full-Q Gibbs state, projective limit, or infinite-volume state is defined.
- No PAH dynamics, continuum limit, physical Pre-A, spacetime, QFT, gravity,
  Yang--Mills, mass-gap, or TOE conclusion follows.
- No external project is modified and no external result is promoted to a TECT
  authority.

