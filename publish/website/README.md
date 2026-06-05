# publish/website/ — live-fetch static shell (P2)

Three files only: `index.html`, `app.js`, `style.css`. No content lives here:
at view time the shell fetches the repository's `main` branch
(`verification/catalog.json` as manifest, `claims/*/status.json`, the Markdown
registries) and renders with marked + MathJax. Push = the site is current, by
construction. Rules W1'/W2' and deployment via `.github/workflows/pages.yml`:
`governance/publication-tiers.md`. Local preview:
`python -m http.server` here, then open `?repo=owner/name`.
