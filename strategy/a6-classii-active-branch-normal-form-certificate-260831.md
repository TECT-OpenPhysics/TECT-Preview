# R-462 certificate — fixed-floor active-branch normal form

## Route role

R-462 is an additive T0 local lemma for the existing A6/A7 fixed-floor
Class-II functional. It does not replace the T-054 forward method, the
T-059/T-061 observation-first lane, or the registered owner order. It supplies
the active-branch coordinates needed before a branch-aware tube and entropy
estimate.

## Exact statement

At an active point write the Bloch vector as `m = s n`, with `s > 0`,
`n dot n = 1`, and let `t = grad(n)` satisfy `n dot t = 0`. For one spatial
derivative set `d_s = grad(s)`, `d_rho = grad(rho)`,
`D = rho + epsilon_rho > 0`, and
`delta = d_s - s*d_rho/D`. The existing currents are then

```text
J = d_s*n + s*t
K = delta*n + s*t.
```

For the unchanged positive matrix `Q = [[a,b],[b,c]]`,

```text
2 e_II = a*d_s^2 + 2*b*d_s*delta + c*delta^2
         + (a + 2*b + c)*s^2*(t dot t).
```

The radial form is positive definite. Moreover
`a + 2*b + c = ((a+b)^2 + (a*c-b^2))/a > 0`, so the angular jet is coercive
when `s > 0`. Consequently a zero active local jet has `t = 0`, `d_s = 0`,
and `d_rho = 0`; common doublet phases and singlet directions remain outside
this current-level control.

## Scope and assumptions

The coefficient entries are derived from the hash-pinned A1 production
functional manifest. The statement is an exact rational one-point jet identity
under the active-frame and fixed-floor assumptions. The connected-domain and
C1 frame hypotheses are analytic assumptions of the surrounding pathwise
branch result, not hidden Lean conclusions.

## Reproduction

```text
python -X utf8 verification/scripts/a6_classii_active_branch_normal_form.py
python -X utf8 codes/foundations/a6_classii_active_branch_normal_form_independent.py
python -X utf8 codes/foundations/a6_classii_active_branch_normal_form_hostile.py
python -X utf8 verification/scripts/a6_classii_active_branch_normal_form_verify.py
```

The primary lane exhausts six rational frames, positive `s` values, singlet
densities, spatial jets, and tangent coordinates. The independent lane uses a
separate component implementation. The hostile lane rejects eight mutations,
including a wrong floor sign, omitted radial cross term, non-tangent frame,
semidefinite coefficient matrix, and premature tube promotion. The integrated
lane compiles the pinned `verification/lean/Tect/R462.lean` source.

## Adversarial review

1. A non-tangent frame would create radial-angular cross terms. The theorem
   requires `n dot t = 0`, and the hostile lane rejects the non-tangent fixture.
2. Replacing `rho + epsilon_rho` by `rho` changes `delta` at the fixed floor;
   the hostile denominator mutation is rejected.
3. Constant total density alone is insufficient: a nonzero radial jet remains
   positive. This is tested separately from angular nonnullity.
4. A negative mixed coefficient cannot overturn the angular sign because the
   determinant identity is checked exactly.
5. The normal form does not control common phases or the singlet field. Those
   flat directions are retained as missing entropy/tube inputs.
6. No local identity is silently promoted to a Gibbs concentration theorem;
   the manifest and integrated checks retain the T0 firewall.

## Boundary and next gate

R-462 proves only a local active-branch decomposition. It gives no branch
tube probability, entropy budget, partition convergence, tightness,
renormalisation, regulator removal, continuum limit, physical branch choice,
QFT/Yang--Mills correspondence, or mass gap. The next additive step is to use
the radial/angular split to define branch-specific tube metrics and test their
entropy budgets under the unchanged finite-cutoff Gibbs law, while separately
continuing source-owned Q3LOCK intake and the observation-first inverse lock.
