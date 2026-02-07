<!--
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Admin layout reference (CSS and structure)
Path: docs/ADMIN_LAYOUT.md
Created: 2026-02-05
Last Modified: 2026-02-06
-->

# Admin layout – reference for revert

If the admin layout breaks again (sidebar at top, footer wrong, etc.), revert to this approach:

## Key principles (Feb 2026)

1. **Do not override Django’s layout**
   - Do **not** set `body.admin-page` to `display: flex; flex-direction: column`.
   - Do **not** set `#container` or `#main` to `flex-direction: column`.
   - Use `body.admin-page { display: block !important; }` so Django’s default admin CSS controls sidebar (left) + content (right).

2. **Footer**
   - Admin: `#footer` gets full-width breakout (`width: 100vw`, `margin-left/right: calc(-50vw + 50%)`). Inner content uses `.footer-content` with `max-width: 980px`.
   - Portal and other pages: use the same footer content via `includes/site_footer.html`, wrapped in `.site-footer-wrapper` (portal) or `.admin-footer-wrapper` (admin).

3. **Content width**
   - All admin `#content` (including dashboard): `max-width: 980px`, `margin: 0 auto`.

4. **Dashboard**
   - Hide `#nav-sidebar` only on the index (`body.admin-page.dashboard #nav-sidebar { display: none }`).
   - Show only “Authentication and Authorization” and “Portal” app panels; use `.dashboard-grid-two` (2 columns, wider panels).

Files involved: `src/static/admin_custom.css`, `src/pmg_portal/templates/admin/base.html`, `src/pmg_portal/templates/admin/index.html`, `src/portal/templates/portal/base.html`.
