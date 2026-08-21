# R-177: A1 two-root common-heat and root-incidence ledger

## Status

R-177 is a T0, claim-nonbearing finite ledger result. It is an input
discipline checkpoint for the A13 proof, not an A13 closure.

## Frozen chart

The chart uses the actual A1 `k` and `2k` covariance roots instantiated by
R-176. The owner order is

`common_heat -> root_1 -> root_2 -> future_residual`.

The root-2 fixture is `g2(h,r1,r2)=h+beta*g1(h,r1)+r2` with registered
`beta=1/2`. This coefficient is a structural ledger fixture, not a claim
that the full production feedback has already been evaluated.

## Exact identities

For `m=(x+y)/2`, Lean proves

`((x-m)^2+(y-m)^2)/2=(x-y)^2/4`.

With the same heat in both replicas, the heat cancels from their endpoint
difference. If heat is independently replicated, its difference survives.
Changing root 1 by `delta` changes root 2 and the endpoint by `beta*delta`.
Thus root-1 feedback cannot be frozen while evaluating root 2. The future
residual is the only item in this ledger that is replica-specific after root
2.

The mean-only counterexample is exact: the two values `1` and `-1` have mean
zero but positive variance. A conditional mean therefore cannot replace the
future-variance rebate required by R-125/R-136.

## Lean and independent verification

`verification/lean/Tect/R177.lean` contains the theorem markers
`two_replica_variance`, `common_heat_cancels`, `root2_feedback_dependence`,
`endpoint_feedback_dependence`, `independent_heat_does_not_cancel`,
`root_two_after_root_one`, and `future_after_root_two`. The primary SymPy
lane binds the identities to the R-176 actual A1 roots and the independent
lane recomputes the rational fixture with the standard library only.

## Adversarial boundary

Replacing common heat by independent heat, deleting root-1 feedback, moving
future residual before root 2, or recovering variance from means alone is
rejected by the integrated mutation suite. None of these identities supplies
the complete scalar owner, the R-125 forest, a nonlocal projector sign, a
source/sextic one-use estimate, T-050, A13, Nelson, a measure, phase/PDE
selection, physical-empty comparison, a removal or continuum limit, Sector-A
or Pre-A closure.

## Reproduction

```text
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 verification/scripts/lean_a13_two_root_heat_incidence_ledger.py --no-store
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_root_heat_incidence_ledger_independent.py --output %TEMP%\r177-independent.json
E:\Dev\TECT.venv\Scripts\python.exe -B -X utf8 codes/foundations/lean_a13_two_root_heat_incidence_ledger_verify.py --staged --no-store
```

No R-177 PDF is issued. The next proof action is to differentiate the complete
finite scalar owner with every ordered R-174 cross block retained exactly once
and then test the R-125 future-variance, source and sextic windows.
