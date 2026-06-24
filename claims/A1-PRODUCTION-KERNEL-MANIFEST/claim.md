# A1-PRODUCTION-KERNEL-MANIFEST — parameter-consistency gates (current config is a mock)

**Tier**: T1 OPEN (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-23 · *(A1 split; the current solver-template config FAILS)*

## Statement

A production kernel config is admissible iff $|Z+2Yq_\star^2|\le\varepsilon$, $|r-(m_{\rm sh}^2+Yq_\star^4)|\le\varepsilon$, $|\texttt{mu2}-(r-Z^2/4Y)|\le\varepsilon$, and $m_{\rm sh}^2=r-Z^2/4Y>0$. The current solver template $(r,Z,Y,q_0)=(0.35,-1,0.50,0.68017)$ **FAILS** (m_sh²$=-0.15<0$; $q_\star^2=1\ne q_0^2=0.4626$; `mu2`$=0.35=r$, the zero-momentum alias): a **working/mock** config, NOT an N-001 production manifest.

## Scope
Parameter-consistency gate for production kernel configs; **OPEN** until a certified config passes.

## Dependencies and hypotheses
- Hard dependencies: A1-KERNEL-IDENTITY, A1-SCALAR-ANALYTIC-BRANCH
- Hypotheses: none · Open gates: none

## Evidence
Grades: ANALYTIC, EXECUTED. `claims/A1-PRODUCTION-KERNEL-MANIFEST/notes/a1-production-kernel-manifest-260623-260623-v1.5.tex.txt`; `codes/foundations/a1_kernel_checks.py` (14/14, v1.5: reads the full runtime scalar_slice from JSON -> ORIGINAL bloch_matrix_linear; schema-completeness assert; all scalar_slice settings shown load-bearing).

## Falsifier
A config passing all gates with $m_{\rm sh}^2>0$ closes the OPEN status for that config.

## Reproduction
Status: **AVAILABLE**. `python codes/foundations/a1_kernel_checks.py` → 14/14 PASS (incl. `production_manifest_mock_config_FAILS`).

## No-overclaim
The current mock config is NOT certified; A2/A3 are NOT numerically implemented by it; no production run may be cited as the theorems' implementation until a config passes.

## v1.1 schema (2026-06-23)
The v1.0 gate $|r-(m_sh^2+Y q_*^4)|$ was identically 0 (vacuous). v1.1 gates the **independent stored fields** $(r_{zero}, mu2_{shell}, q0)$ with separate tolerances $(\varepsilon_Z,\varepsilon_m,\varepsilon_r)$, forbids the `mu2=r` alias, and splits into **CONSISTENCY** + **ANALYTIC-BRANCH** scopes (only the latter is A2/A3-citable). The verifier reads the five stored fields AS-IS from `canonical_n001_kernel.json` and imports the **ORIGINAL N-001 solver** (`codes/foundations/n001_solver/`, byte-identical, full sha256 pinned) and passes the **full runtime `scalar_slice` read from JSON** (laplacian_mode, bcc_mix_epsilon, a_bcc, family_masses, k_lock, z0, eta_shell) to `bloch_matrix_linear`, so the verified symbol IS the runtime symbol = stored kernel (8.9e-16). Each setting is shown load-bearing (k_lock=0.15→0.1, eta_shell=0.1→0.231, mixed_bcc→2.0, family→0.05); a schema-completeness assert prevents stale-config KeyErrors; a corrupted stored `q0` is detected. The canonical N-001 config PASSES both manifests — **numerical gates pass, operator certification pending** (card stays T1 OPEN, not yet A2/A3-citable); the legacy template $(0.35,-1,0.50)$ FAILS.

## History
- 2026-06-23 — Created in the A1 split: the production-config gates; the current solver template fails them ($m_{\rm sh}^2<0$).

## Next required action
Produce + certify an N-001 production config ($m_{\rm sh}^2>0$, all gates) before any Class-II/condensate solver run is cited as the A2/A3 implementation.
