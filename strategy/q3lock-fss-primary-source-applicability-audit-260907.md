# Q3LOCK FSS primary-source applicability audit

Date: 2026-09-07. EXP-001617. T0, claim_bearing=false,
INTERNAL_REVIEW_ONLY.  The research authority remains EXP-000780 ->
EXP-000781 -> EXP-000782 / R-497.  This note is a finite model-side
cross-check; it is not an independent acceptance of the FSS theorem or of
the Q3LOCK phase package.  The paper PDF remains deferred until content review
and final organization.

## 1. Primary source and exact scope

The checked source is J. Froehlich, B. Simon, and T. Spencer, *Infrared
Bounds, Phase Transitions and Continuous Symmetry Breaking*, Commun. Math.
Phys. 50 (1976), 79--95, Section 2, Theorem 2.1 and the proof on printed
pages 82--84:

    https://math.caltech.edu/SimonPapers/65.pdf

The source-freeze record already pins the retrieved bytes as 1,404,869 bytes
with SHA-256
`108b70f69d707c77c46bb4d4870c9df43be635394d3013be043f8f1a566178e1`.
The first-page scan prints an inconsistent `79--85` masthead; the body and
bibliographic record give 79--95, which is the citation range used here.

Section 2 of the source assumes a finite vector spin dimension, a periodic
rectangular nearest-neighbour box with each pair counted once, a positive
ferromagnetic dot-product coupling, and a common a priori measure with

    integral exp(a |sigma|^2) d lambda(sigma) < infinity

for every positive `a`.  The theorem's edge-difference source is bounded by
the squared edge-field norm divided by `2J`.  The source remarks that the
constant is independent of the single-spin distribution and of the number of
components, and that no internal rotational symmetry is required.  Those are
the only FSS facts used here.

## 2. Q3LOCK model-side crosswalk

At a fixed time mesh `epsilon=beta/N`, the history at one spatial site is
`s_y=(sqrt(epsilon) x_(y,k))_k` in `R^(8N)`.  The exact finite-mesh action
has the form

    sum_y V_N(s_y) - c sum_{<y,z>} s_y . s_z,

so the FSS coupling is `J=c>0`, and the same prior `exp(-V_N(s)) ds` is used
at every spatial site.  A cubic torus has one positive-direction bond per
site and direction; hence the spatial square contributes `3c |s|^2` to the
one-site action and `-c s_y . s_z` to each bond.

The Q3 quartic term gives, for every fixed `N`,

    V_N(s) >= (g/(4 epsilon)) sum_(k,e) s_(k,e)^4
             + ((r+6c)/2) |s|^2
           >= (g/(32 beta)) |s|^4 + ((r+6c)/2) |s|^2.

The positive quartic coefficient therefore supplies all quadratic exponential
moments of the finite-dimensional prior.  This is a fixed-mesh statement;
it does not supply a mesh-uniform normalizer or uniform integrability.

For a zero-sum spatial source `f`, use the oriented difference `G`, its
adjoint divergence `B=G^*`, and `L_sp=G^*G=BB^*` on the zero-sum subspace.
With `eta=t sqrt(epsilon) (f u)` at every time slice and
`h=G L_sp^{-1} eta`, one has `B h=eta` and

    ||h||^2 = beta t^2 <f, L_sp^{-1} f>,

because the normalized collective vector satisfies `||u||=1`.  The finite
FSS input therefore yields the manuscript's finite-mesh MGF coefficient
`||h||^2/(2c)`.  A nonzero spatial mean is intentionally excluded because
`L_sp^{-1}` has the constant zero mode.

The executable audit checks these identities on exact rational cubic-torus
fixtures, including the rescaling factors, bond count, quartic coercivity
coefficient, adjoint source map, Poisson norm, square-completion factor, and
the non-radial nature of the Q3 prior.

## 3. Result and adversarial boundary

The result is stored at
`claims/C6-SPACETIME-SIGNATURE/runs/2026-09-07-q3lock-fss-applicability-audit/result.json`.
Run it with:

    E:/Dev/TECT.venv/Scripts/python.exe -X utf8 verification/scripts/q3lock_fss_applicability_audit.py --check

The check is deliberately finite and algebraic.  It does **not** establish:

1. the FSS theorem independently of its published proof;
2. the finite-mesh-to-continuous-loop weak limit or source-uniform
   integrability;
3. the Duhamel normalization, the three-dimensional infrared sum, or a
   positive zero-mode lower bound;
4. pressure convergence, DLR passage, a cusp, or two infinite-volume states.

The adversarial checks are:

1. the spin dimension changes with the mesh, but FSS is applied separately at
   each fixed finite `N`; no uniform-in-`N` conclusion is inferred;
2. replacing `J=c` by the vertex-source norm or inserting an extra factor of
   eight fails the exact Poisson-norm rows;
3. equal-norm vectors with different Q3 quartic values confirm that the prior
   is non-radial, while the source theorem's allowance of arbitrary priors is
   not misread as a Q3 phase theorem;
4. the zero mode is excluded rather than inverted by a pseudoinverse;
5. finite quadratic exponential moments at each mesh are not treated as the
   uniform estimates required by the later loop passage.

## 4. Disposition

At internal review level, the Q3LOCK finite-mesh model-side hypotheses match
the cited FSS Section 2 input.  The disposition is therefore
`APPLIES-CONDITIONALLY`, not `PROVED` or `EXTERNALLY-ACCEPTED`.  The existing
open audit items for the loop passage, Duhamel factors, infrared limit, zero
mode, collective lower bound, DLR composition, and signed external review are
unchanged.  No claim tier, manuscript theorem, sector status, submission
permission, or PDF status changes.
