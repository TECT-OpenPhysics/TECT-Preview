# Specialist novelty-review form — A2/R-157/R-158

Status: `BLANK / NO NOVELTY DISPOSITION RECORDED` (manuscript v0.1.38,
2026-09-04).

This form requests a specialist literature and publishability opinion.  It is
not a priority claim, a proof audit, or evidence that a specialist has already
reviewed the paper.

## Frozen review object and residual proposition

- Manuscript SHA-256:
  `c6b2b5be29ca5bf567fd68ce2647bba24e3b242a433ddb44b5295bbfc545da24`
- PDF SHA-256:
  `87f145e1c8744e1ee2c7a10656d919bcaba17c7c8b0e5c5b3658e1670a573860`
- Detailed bounded crosswalk: `literature-crosswalk.md`

The only proposed residual contribution is the model-specific conjunction,
on one fixed side-16 three-torus, of:

1. all-`H^2` global well-posedness and positive-time smoothing for the exact
   six-real-component regularized fourth-order gradient flow with the printed
   derivative Class-II term;
2. exact neutral radial rejection, unique zero critical point/global
   minimizer, and global exponential decay for the pinned unconstrained
   functional; and
3. an exact fixed-charge and chemical-potential shell completion with a
   zero/nonzero coexistence point for a separately imposed ensemble.

The paper does not claim that analytic semigroups, maximal regularity,
Swift--Hohenberg/Brazovskii analysis, Bregman completion, constrained
minimization, or first-order coexistence methods are individually new.

## Required search coverage

The specialist should search primary literature and citation chains in at
least the following families, recording databases, exact queries, dates, and
screening criteria:

| ID | literature family | subsumption question |
|---|---|---|
| N-01 | rigorous scalar and vector Swift--Hohenberg/PFC evolution | Is there an all-data three-dimensional multicomponent theorem with derivative lower-order coefficients matching this functional? |
| N-02 | quasilinear and fully nonlinear fourth-order parabolic PDE | Does an abstract theorem directly cover the printed map with the claimed `H^2` initial space, global energy control, and smoothing? |
| N-03 | Landau--Brazovskii and modulated-phase variational theory | Is the exact finite-torus neutral radial rejection or shell equality classification already proved for an equivalent functional? |
| N-04 | multicomponent coupled-mode and complex Swift--Hohenberg models | Does a continuum theorem, rather than a numerical optimization result, subsume all three main theorems? |
| N-05 | fixed-mass/charge constrained minimizers and chemical-potential transitions | Is the exact Bregman completion, threshold, and zero/nonzero coexistence statement a direct special case of a published theorem? |
| N-06 | phase-transition and first-order terminology | Is “first-order coexistence” acceptable for the restricted grand-potential statement, or must the terminology be narrowed? |
| N-07 | recent papers and forward/backward citations of the closest sources | Does any source omitted by the bounded crosswalk materially narrow or eliminate the residual conjunction? |

At minimum, verify the sources already listed in `literature-crosswalk.md`,
including Brazovskii; Swift--Leitner; Giorgini; Asai; Ruan; Bao--Chen--Jiang;
Mi--Cui--You; Martine-La Boissoniere--Choksi--Lessard;
Duchesne--Lessard--Takayasu; and both Belin--Schneider comparisons.  A title
match or abstract-only screen is insufficient for a `SUBSUMED` disposition.

## Source-by-source response block

Copy once for every retained close source:

```text
source_id: N-__ / reviewer-assigned ID
full_primary_citation: <citation and stable identifier>
full_text_checked: YES | NO
exact_theorem_or_section: <location>
source_object_and_scope: <field, dimension, domain, equation, data class, limit>
hypotheses_matching_this_paper: <list>
hypotheses_not_matching: <list>
paper_conclusion_subsumed: A2 | R-157 | R-158 | COMBINATION | NONE
disposition: SUBSUMES | PARTIALLY-OVERLAPS | DOES-NOT-SUBSUME | UNCLEAR
reason: <theorem-level comparison>
required_manuscript_change: <citation/wording/theorem change, or NONE>
```

## Required proposition-level decisions

Return one disposition for each row.

| ID | decision | allowed disposition |
|---|---|---|
| D-01 | Is Theorem `thm:a2-flow` publishably distinct after the closest fourth-order/quasilinear results are applied? | `DISTINCT`, `INCREMENTAL`, `SUBSUMED`, `UNCLEAR` |
| D-02 | Is Theorem `thm:r157-neutral` publishably distinct as an exact model-specific sign/equality theorem? | `DISTINCT`, `INCREMENTAL`, `SUBSUMED`, `UNCLEAR` |
| D-03 | Is Theorem `thm:r158-ensemble` publishably distinct after constrained Brazovskii/PFC results are applied? | `DISTINCT`, `INCREMENTAL`, `SUBSUMED`, `UNCLEAR` |
| D-04 | Does the conjunction of the three theorems have independent paper value even if no individual method is new? | `YES`, `NO`, `UNCLEAR` |
| D-05 | Is the title/abstract/introduction novelty language proportionate and free of priority overclaim? | `PASS`, `REPAIR` |
| D-06 | Is “first-order coexistence” acceptable at the paper's explicitly restricted scope? | `PASS`, `NARROW`, `REMOVE` |
| D-07 | Are any essential citations missing or any current comparisons inaccurate? | `NO`, `YES-LIST-REPAIRS` |

For any `SUBSUMED`, `NO`, `REPAIR`, `NARROW`, `REMOVE`, or
`YES-LIST-REPAIRS` response, provide exact replacement language and identify
the affected theorem, abstract sentence, and crosswalk rows.

## Global signed disposition

```text
reviewer_name: <name>
affiliation: <affiliation>
specialist_area: <area>
independence_statement: <relationship to author and project>
search_dates: <YYYY-MM-DD through YYYY-MM-DD>
databases_and_indexes: <complete list>
queries_and_citation_chains: <reproducible list or attached record>
manuscript_sha256_checked: c6b2b5be29ca5bf567fd68ce2647bba24e3b242a433ddb44b5295bbfc545da24
decisions_completed: D-01,...,D-07
global_disposition: PUBLISHABLY-DISTINCT | REPAIR-AND-REREVIEW | SUBSUMED | INCONCLUSIVE
required_repairs: <exact list, or NONE>
signature_or_verifiable_review_record: <reference>
date: <YYYY-MM-DD>
```

Only a signed `PUBLISHABLY-DISTINCT` disposition, after any required repairs
are incorporated and rechecked, can close the specialist novelty gate.  It
does not by itself close the mathematical proof, source-sign, operator,
commit/backup, capstone, or submission-authorization gates.
