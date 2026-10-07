# GREAT final analysis provenance and response enquiry

Status: unsent draft, 2026-10-07 UTC. Sending requires operator approval and
the operator's chosen name, reply email and truthful affiliation. This file
does not authorize external contact. Do not send the internal routing notes.

## Message

Subject: GREAT final-analysis product provenance and estimator-response enquiry

Dear GSSC Helpdesk,

I am studying the applicability of the GREAT Galileo clock and orbit products
to a hypothetical weak-field model in which both atomic-clock frequencies and
satellite acceleration change. I am not treating the published phenomenological
redshift uncertainty as an uncertainty bound for this different signal.

Could you please route this archival enquiry to the appropriate GREAT/ESOC
or SYRTE analysis contact? The initial target is Delva et al., Physical Review
Letters 121, 231101 (2018), DOI 10.1103/PhysRevLett.121.231101.

1. Which clock/orbit campaign and product versions were used in the final
   published analysis? How do they correspond to the public repro3 sample
   and the later repro4 products? We have the public E18/GSAT0201 sample for
   29 May 2016. Was that day retained in the final analysis, and is a matching
   final-version day with its reference clock and accepted-epoch mask available?
2. Are the historical processing configuration and the article's supplemental
   processing description available? Relevant details include time/frame/units,
   estimated versus fixed parameters (especially GM), clock datum, force model,
   clock and orbit priors/constraints, observation weighting, ambiguity/epoch
   selection, pre-applied relativistic corrections, and final clock-data fitting.
3. If full software or normal equations cannot be distributed, are saved
   directional sensitivities or validated injection/recovery outputs available
   that include a perturbation of both clock rates and the orbital force law?
   An alpha injection only into postprocessed clock data is not sufficient
   for this use, even when its template includes gravitational and Doppler terms.
   We would be happy first to receive an availability/provenance answer, rather
   than ask for a new custom analysis.
4. What accompanying systematic-error definitions, covariance or projected-error
   information, validation range and reuse conditions are available? We would
   distinguish statistical coverage from a deterministic bound and would not
   assume that nominal clock stability bounds the full processing error.

A pointer to an existing archive, configuration record or appropriate analysis
contact would be very helpful. No unpublished material would be redistributed
without permission.

Thank you.

## Internal routing notes

Official contact: <https://gssc.esa.int/contact/> and
`gssc-helpdesk@cosmos.esa.int`; public form:
<https://gssc.esa.int/contact/submit/>. Verified read-only on 2026-10-07.
The form requires identity fields, consent and CAPTCHA. Do not fabricate an
institutional address or affiliation. No attachment is needed for this first
availability enquiry.

The fixed model is pinned by `TECT-CLK-002-prereg-v1.json`, SHA-256
`eed93e6aa01b4bacc780bba0a24f53ccf7c6b7f6daab394ae20e54afa270c92f`.
The full response question remains as admitted in CLK009; this short enquiry
does not replace it with a clock-only template. A returned generic manual,
archive URL or single clock product is not automatically sufficient.
