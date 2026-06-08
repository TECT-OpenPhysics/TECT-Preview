# Operator decision -- H-ADM-COH discharge authorization (2026-06-08)

**Context**: review of dr2-hadmcoh-discharge-decision v1.0 (R-028), dr2-step5b-integration v1.1
(R-027), dr2-lattice-divisor-closure v1.2 (R-026).

## Decision (verbatim intent)

For the crystallographic momentum-shell competitor class of TECT, the H-ADM-COH assumption is
discharged from the active B1 hypothesis set:

    {H-LAYER, H-ADM-COH, SC-SCOPE}  ->  {H-LAYER, SC-SCOPE}.

The arbitrary real-point DR-2 problem remains open and is retained only as a legacy fallback
branch; it is not needed for the B1 mainline.

## Endorsed ledger status

- G1'''-AE_lattice : CLOSED@T7
- H-ADM-COH        : DISCHARGED@lattice class
- DR2-SHARE        : MOOT for the lattice mainline; OPEN for arbitrary Q
- B1-RH-ENUM       : T6 CONDITIONAL on {H-LAYER, SC-SCOPE}

## Basis accepted

- (a) finite margin: K_adm = 1+T'(Q) <= K_allowed(n) = 8 + 4 sqrt(14) sqrt(n), verified
  (dr2_hadmcoh_margin.py 3/3) with margin 10.6x-15.8x (growing); worst sub-pattern ratio 0.307.
  The former subpolynomial-K judgment is now a numerical inequality.
- (b) competitor class = crystallographic-shell subsets (physical setup).
- (c) the non-transversal multi-circle high-n corner is a lattice subset, hence covered.
- The c_R = 4 sqrt(14) dependency is acknowledged; the >10x margin is robust to O(1) drift.

## Enactment

- B1-RH-ENUM/status.json: hypotheses -> {H-LAYER, SC-SCOPE}; scope/falsifier/no_overclaim updated;
  tier UNCHANGED T6 (hypothesis-set reduction strengthens the conditional claim).
- GATES.md: H-ADM-COH -> DISCHARGED@lattice; DR2-SHARE -> MOOT@lattice / OPEN@arbitrary.
- dr2-hadmcoh-discharge-decision re-issued v1.0 -> v1.1 (operator ACCEPTED; flip enacted) -> v1.2 ((beta) self-review consistency fix).
- DR-2 programme chronicle written (dr2-programme-consolidation v1.0).
