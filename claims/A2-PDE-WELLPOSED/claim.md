# A2-PDE-WELLPOSED — Well-posedness of the TECT gradient flow and minimisation problem

**Tier**: T1 (TSv2) · **Lifecycle**: ACTIVE · **Last review**: 2026-06-09

## Statement

$$
The TECT free-energy minimisation and the associated gradient flow $\partial_t\phi=-\delta F_{\rm TECT}/\delta\phi$ are well-posed: local existence, uniqueness, and regularity of solutions in the relevant Sobolev class, with global-in-time control on Brazovskii free-energy sublevel sets.
$$

## Scope

OPEN scaffold. Well-posedness (existence/uniqueness/regularity) of the dynamical and variational problem underlying $F_{\rm TECT}$ at the production convention. The existence of minimisers is the variational counterpart consumed by Sector B; this claim is the analytic foundation, not a vacuum-selection statement.

## Dependencies and hypotheses

- Hard dependencies: A1-KERNEL-CONV
- Hypotheses: none registered yet
- Soft dependencies (context only): none
- Legacy pillar(s): foundation

## Evidence

OPEN scaffold registered 2026-06-09 by the TOE-completeness audit
(`governance/toe-completeness-audit-260609.md`). No evidence migrated yet; this
card reserves the verification-package slot for the pillar so that migrated or
newly derived results have a canonical home.

## Falsifier

$$
\text{ A finite-time blow-up, loss of uniqueness, or regularity failure in the admissible Sobolev class at the production convention. }
$$

## Reproduction

`PACKAGE-PENDING`.

## No-overclaim

Registering the target does not establish well-posedness; no existence/uniqueness theorem is claimed yet.

## Devil's-advocate record

Scaffold (T1 OPEN): no tier promotion claimed, so no promotion-grade
devil's-advocate is required. The honest status is that this is a registered
TOE target with no established result.

## History

- 2026-06-09: registered as an OPEN scaffold by the TOE-completeness audit to close
  a Sector-A coverage gap (pillar foundation).

## Next required action

Migrate or derive the local well-posedness estimate for the quartic Brazovskii functional; identify the Sobolev class and the sublevel-set a priori bound.
