# Current fixed-torus QFT OS/KMS package revalidation

**Candidate:** `PA-CP1-CL8-Q3-FIXED-TORUS-OS-KMS-MARKOV-REFERENCE-ROUTE-SPLIT-v0`  
**Prior exploration:** `EXP-000773`  
**Current exploration:** `EXP-001007`  
**Scope:** claim-nonbearing T0 provenance/current-reader repair

## Finding

The historical child artifacts were stale only in provenance: both stored JSON files carried the pre-current certificate hash. After regeneration, the primary lane passes `65/65` and the independent lane passes `59/59`. The original integrated reader then exposed a second reader-contract drift: it required the old exploration ordinal and next gate inside `todo.json`, although the current protocol stores EXP ordinals in the append-only exploration/changelog ledgers and uses `todo.json` for live tasks.

The verifier was changed only to check the current live task plus the append-only exploration and changelog records. The canonical integrated run now passes `103/103`.

## Preserved mathematical scope

The package still establishes only the declared fixed finite `beta0` by `L` thermal QFT interface: Schwinger regularity, closed thermal reflection positivity, two-sided germ-domain Markov factorization, periodic OS reconstruction to an abstract `beta0`-KMS system, and strict free-energy ordering against the explicitly named Gaussian reference.

It still does not establish a beta-independent Hamiltonian, a positive-energy vacuum, an interacting Hadamard/microlocal spectrum condition, a thermodynamic or ground limit, physical empty space, C6, Sector A, or Pre-A closure. The next gate remains `PA-CP1-CL8-BETA-INDEPENDENT-HAMILTONIAN-THERMODYNAMIC-REFERENCE-AND-GROUND-LIMIT-ROUTE-SPLIT`.

## Reproduction

```text
python -X utf8 codes/foundations/pre_a_cp1_cl8_q3_fixed_torus_os_kms_markov_reference_route_split.py --output <primary-json>
python -X utf8 codes/foundations/pre_a_cp1_cl8_q3_fixed_torus_os_kms_markov_reference_route_split_independent.py --output <independent-json>
python -X utf8 codes/foundations/pre_a_cp1_cl8_q3_fixed_torus_os_kms_markov_reference_route_split_verify.py --output claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-fixed-torus-os-kms-markov-reference-route-split/result.json
```

Current outputs are `65/65`, `59/59`, and `103/103` respectively. The canonical child artifacts equal fresh executions and carry the current certificate hash.

## Adversarial boundary

- Certificate/hash drift is dismissed as a provenance defect after exact child-artifact regeneration.
- The obsolete TODO ordinal check is dismissed as a reader-contract defect; no historical EXP or changelog event is edited.
- Thermal KMS is not identified with a vacuum Hamiltonian or physical empty space.
- No new Lean theorem is asserted: this is a provenance/current-reader correction, not a new exact mathematical result. Existing Lean-backed finite QFT routes remain separately scoped.

No result card, tier change, lifecycle change, negative result, or PDF is created by this correction.
