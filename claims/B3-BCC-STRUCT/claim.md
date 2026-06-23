# B3-BCC-STRUCT — structural selection among tested ordered condensates (corrected continuum basis)

**Tier**: T4 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · **Migration**: clean (batch 4, reframed 2026-06-23)

## Statement

Within the tested ordered-condensate class, no competitor reading lowers the TECT free energy below the selected Reading-H (H-layer, BCC-type) condensate at $r_{\rm braz}=\mu^2=0.005$: $\Delta F[\mathcal R]=F_{\rm TECT}[\mathcal R]-F_{\rm TECT}[\mathcal R_H]>0$ for the tested representatives (LAM/HEX/FCC explicit via Math431), at estimator grade — the structure-named projection of B1-RH-ENUM. The legacy single-shell-SMA / 1-mode $\Delta F$–$L_4$ ranking purporting $F_{\rm BCC}<F_{\rm FCC}<F_{\rm SC}$ (Math194/Math383) is **REFUTED** (Math400) and retained only as superseded history.

## Scope

Corrected continuum-anchored basis (B1-RH-ENUM evidence). Tested representatives at estimator grade; **not** an exhaustiveness statement. The original single-shell-SMA framing (fixed ordered structures ranked by $\Delta F/L_4$) is **RETIRED**: Math400 (T0, binding) shows lamellar is the deepest single-shell SMA configuration and the canonical-$\mu^2$ "BCC minimum" is a saddle, and independently refutes the Math383 $K_4/K_6$ table; the fixed-ordered-BCC-vacuum reading is retired (`negative-results/registry.md` `NG-2026-legacy-ordered-vacuum`). Multi-shell / exhaustiveness tracked by G3PB-III.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV; evidence shared with B1-RH-ENUM
- Hypotheses (registered in `claims/GATES.md`): none
- Soft dependencies (context only): B1-RH-ENUM (B3 is its structure-named projection)
- Open gates: G3PB-III

## Evidence

Grades: EXECUTED, ESTIMATOR. Migration-clean (batch 4, 2026-06-23). Reframe + refutation record:
`claims/B3-BCC-STRUCT/notes/b3-reframe-continuum-260623-260623-v1.0.tex.txt`.

Surviving (continuum-anchored, B1 chain):

- `archive/legacy/notes/Math431/...LAM-HEX-FCC-PASS...` — LAM/HEX/FCC races (all channels PASS)
- `archive/legacy/notes/Math436/...HEX-Exact-Wick-Bracket-PASS...` — HEX exact-Wick bracket
- `archive/legacy/notes/Math432/...Two-Shell-Ensemble-Race-PASS...` — two-shell ensemble race
- `archive/legacy/notes/Math428/...BCC-Bloch-LogDet-Race-PASS-Continuum-Anchored...` — Bloch log-det
- `archive/legacy/notes/Math434/...ReadingH-Selection...` — Reading-H selection record

Superseded / REFUTED predecessors (kept for history; **not** active support):

- `archive/legacy/notes/Math194/...BCC-uniqueness-among-3D-crystallographic-competitors...` — single-shell SMA ranking; re-running its script yields BCC **rank 9** (lamellar rank 1); refuted by Math400
- `archive/legacy/notes/Math383/...BCC-vs-Competitors-Analytical-and-Numerical...` — 1-mode $K$-table; main claim + §2 table **T0-refuted** by Math400

## Falsifier

A tested-class competitor reading with lower TECT free energy than Reading-H at the operating point under the corrected continuum-anchored convention (estimator grade). NOTE: under the **refuted** single-shell-SMA convention this falsifier already fires (Math194 script: lamellar $<\dots<$ bcc); that convention is retired.

## Reproduction

Status: **AVAILABLE** (via the B1 chain). Command: `cd archive/legacy/scripts && python Math431_g1pp3_lam_hex_fcc.py && python Math436_hex_exact_wick_bracket.py && python Math432_g3prime_multishell_ensemble.py && python Math428_g1doubleprime_bloch_logdet.py` (LAM/HEX/FCC + exact-Wick + two-shell + Bloch log-det PASS). Refutation demo: `python archive/legacy/scripts/Math194_brazovskii_lattice_ranking.py` prints `BCC is Rank 9`.

## No-overclaim

BCC global optimality over all admissible structures; any fixed-ordered-BCC-vacuum reading (retired, `NG-2026-legacy-ordered-vacuum`); exhaustiveness beyond the tested representatives; and the refuted single-shell-SMA $F_{\rm BCC}<F_{\rm FCC}<F_{\rm SC}$ ordering.

## Devil's-advocate record

Reframe self-test (3 concrete objections, full record in the reframe note §4):

- (α) *"B3 now duplicates B1."* VALID-with-mitigation: B3 is retained as the **structure-named projection** of B1 (the tested ordered-structure view), distinct in framing from B1's reading-enumeration; the operator chose reframe over supersede.
- (β) *"Citing refuted notes as evidence."* DISMISSED: Math194/Math383 are listed only as **SUPERSEDED/REFUTED predecessors, explicitly not active support**; the active evidence is the B1 continuum chain.
- (γ) *"Tier T4 is stale after refutation."* DISMISSED for now: the reframed claim rests on the B1 chain (estimator grade, T7-supporting), so T4 STRONG EVIDENCE is consistent; any tier change is a separate operator-authorized action.

## History

- 2026-06-05 — Seeded from the legacy `TOE-FACT-SHEET.md` snapshot (Math442), translated per `governance/tier-system.md` §4. The seeded `legacy:Packet-B lineage` pointer carried the pre-Math400 single-shell-SMA evidence.
- 2026-06-23 — Migration batch 4: the seeded evidence (Math194/Math383) was found **REFUTED** (Math400; Math194 script re-run reproduces BCC rank 9). B3 reframed onto the corrected continuum-anchored B1 evidence; Math194/Math383 archived as SUPERSEDED. Migration-clean; no tier change (T4).

## Next required action

Assemble Minimal Review Packet B from the B1 continuum-anchored evidence (Math431/434/436/428/432) restricted to the tested ordered-structure projection; tighten the estimator error bound (ESTIMATOR-UPGRADE / G3PB-III).
