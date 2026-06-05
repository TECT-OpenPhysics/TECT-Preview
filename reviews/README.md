# reviews/ — external review record

One folder per round: `reviews/<YYYY-MM-DD>-<reviewer-or-topic>/` containing
scope (commit hash reviewed), verdicts, actions. Confirmed defects produce
errata in `reviews/errata/` linked to claim IDs (+ `negative-results/` rows
when a claim retires). Reviewer-found defects are credited.
