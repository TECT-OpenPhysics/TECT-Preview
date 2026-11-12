# Reproduce the finite checks

The standalone audit needs Python3.10+ and NumPy. It reads only the copied
production input and provenance beside the paper and does not require Git,
the full TECT repository, a numerical solver or a Lean cache.

From the repository root:

```text
python -X utf8 publish/papers/a6-a7-canonical-composites/verification/verify.py --self-test
```

To compare exact fields and floating diagnostics against the issued report:

```text
python -X utf8 publish/papers/a6-a7-canonical-composites/verification/verify.py --self-test --check claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/runs/2026-11-12-a6-a7-paper/algebra.json
```

Expected: 80 finite checks pass and13 hostile mutations are rejected.
The exact scalar Gaussian covariance fixtures are strictly diagonally
dominant, so positive definiteness does not depend on a floating eigenvalue.
Moment enumeration is exact rational arithmetic. Matrix conventions and
cube quadrature use the stated numerical tolerances. No numerical slope is
used as proof of convergence. Python -O is explicitly rejected.

The legacy source-hash/ingredient audits additionally need the full repository:

```text
python -X utf8 publish/papers/a6-a7-canonical-composites/verification/replay_legacy.py --work /absolute/path/inside/repository/to/new-audit-directory
```

The work directory must be absent. Outputs are new; historical issued runs
are checked unchanged. Expected A6 aggregate64/64 and A7 aggregate74/74.
The wrapper changes only output destinations of the historical A6 verifier
at runtime, not scientific functions or expected source hashes. The primary
and non-importing independent programs are executed as originally issued.

The analytic limits and their hypotheses must be reviewed in manuscript.tex.
Neither check count nor file integrity certifies the analytic proofs,
novelty, an interacting measure, external review or journal acceptance.

## Strengthened edition0.1.2 checks

```text
python -X utf8 publish/papers/a6-a7-canonical-composites/verification/strengthened_audit.py --check publish/papers/a6-a7-canonical-composites/verification/runs/strengthened-v012.json
python -X utf8 publish/papers/a6-a7-canonical-composites/verification/package_gates.py --self-test
```

Expected:59 finite checks and14 hostile mutations;35 visual/output-gate
mutations rejected. The dense eight-variate rational Wick fixture tests all
tensor indices and three nonzero connection families; P/Q/R-transpose,
family-factor and real-quadratic-variance mutations are rejected. Further
fixtures cover the phase kernel and PSD coefficient norm, signed spectral
cutoffs with noncommuting backgrounds, actual lattice-shell counts, six-real
spectral multiplicity, the full pinned symbol and homogeneous polynomial.
The numeric fixtures do not replace the analytic limit arguments.

The visual gate checks schema/status, an empty defect list, explicit
NOT_PERFORMED external-review provenance, complete page findings, and each
current PNG's path, size, hash and dimensions. The output preflight rejects
overlapping source/delivery/extraction/report/archive paths before writes.
All final inventories are checked before issuing a PASS build report.
The schema1.1 visual receipt and finite reports are preserved; older receipts
describe older editions. A review receipt is not a cryptographic signature.
