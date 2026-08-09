# publish/website/ — live-fetch static shell (P2)

The deployable shell is `index.html`, `app.js`, and `style.css`; this README is
operator documentation. Research records do not live here. At view time the
shell fetches the repository's `main` branch. The overview
starts from the small `verification/catalog-summary.json`, whose exact
top-level `claim_status_paths` prevent frozen bundle copies from appearing as
duplicate live claims. The Catalog route reads
`verification/catalog/index.json`, fetches only the selected kind shard, and
renders at most 100 rows. Loading all shards is explicit. The Changelog route
uses `changelog/INDEX.md`, not the frozen compatibility volume.

Push = the site is current by construction. The Pages workflow runs the
repository release gate before deployment, so the published shell and generated
data surfaces come from the same verified commit. Rules W1'/W2' and deployment
via `.github/workflows/pages.yml`:
`governance/publication-tiers.md`. Local preview:
`python -m http.server` here, then open `?repo=owner/name`.
