# Pezulu Outdoor — website draft

Draft site for Pezulu Outdoor, hosted on GitHub Pages for review.

- `index.html` — main site draft
- `site-finder.html` — interactive site finder demo
- `pages.html` — Outdoor, Taxi & Rank, Instore, Work, Insights, About and Admin

All are self-contained single-file bundles: no build step, no dependencies.
Open either file directly in a browser, or view the hosted version.

Not for public release — pages carry `noindex, nofollow` and `robots.txt`
disallows crawling, but the repository itself is public so the link is
shareable with anyone who has it.

## Updating from a new export

Copy the new `index.html`, `site-finder.html` and `pages.html` over the ones
here, then run:

    python3 tools/apply_mobile.py

The export is desktop-only for the home page and site finder. The script adds
their phone layouts, the `noindex` tags, and the fix for the home page shifting
off-screen. It is safe to run more than once. Then commit and push; Pages
rebuilds in about 30 seconds.
