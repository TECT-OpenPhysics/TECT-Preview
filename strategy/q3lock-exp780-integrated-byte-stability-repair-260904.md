# Q3LOCK EXP-000780 integrated byte-stability repair

**Status:** T0 reproducibility/tooling audit; claim-nonbearing  
**Date:** 2026-09-04  
**Owner task:** T-054  
**Scope:** EXP-000780 integrated verifier only  
**PDF:** deferred

## 1. Trigger

Two executions of the EXP-000780 integrated verifier both passed all
`187/187` assertions, but their JSON hashes differed.  A recursive payload
comparison isolated the difference to the string representation of the Python
set used as the expected value for the parent exploration relation check:

```text
{('EXP-000779', 'continues'), ('EXP-000719', 'continues')}
```

versus the same two elements in the opposite order.  The scientific payload
and every assertion condition were unchanged.

## 2. Repair

The verifier now constructs

```text
related_pairs = sorted((item.get("id"), item.get("relation"))
                       for item in exploration.get("related", []))
```

and records both the actual and expected values as sorted lists.  The Boolean
condition remains the same set-inclusion check, so this repair changes only
the serialization of a diagnostic assertion row.  The file was rewritten
atomically with UTF-8 and the existing newline convention; `py_compile`
passes.

## 3. Reproduction

From the repository root:

```powershell
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_fixed_lattice_3d_quantum_pressure_ground_density_effective_reduction_route_split_verify.py --output .tmp/q3-rerun-20260904/780-integrated.json
E:\Dev\TECT.venv\Scripts\python.exe codes/foundations/pre_a_cp1_st8_q3lock_fixed_lattice_3d_quantum_pressure_ground_density_effective_reduction_route_split_verify.py --output .tmp/q3-rerun-20260904b/780-integrated.json
```

Both executions pass `187/187`.  Their SHA-256 is

```text
6E21186241C6486136B2E2752602C4C8E9F957281F3B43E8E298916B4FFE8B93
```

for both files.  The previously repaired EXP-000781 and EXP-000782
integrated verifiers remain byte-stable as well.

## 4. Boundary

This repair establishes deterministic diagnostic serialization only.  It does
not prove any Q3LOCK theorem, alter EXP-000780's registered scope, or promote
the C6 claim.  It does not replace the final clean-snapshot replay; all three
integrated verifiers must be rerun after the manuscript and claim set are
frozen.

## 5. Nonclaims and publication boundary

No strict cusp, DLR multiplicity, real-time dynamics, KMS state, ground/gap,
continuum limit, physical-vacuum result, claim registration, P2 manuscript,
release or PDF is created by this tooling repair.  PDF generation and visual
review remain final-stage actions after mathematical and independent audits.
