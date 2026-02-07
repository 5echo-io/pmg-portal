<!--
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Build and release log
Path: BUILDLOG.md
Created: 2026-02-05
Last Modified: 2026-02-08
-->

# BUILDLOG

Chronological log of builds and releases (newest first). Each entry: date, branch, version (on bump), short summary.

---

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.35
  - Summary:
    - Release: All local/agent changes from [Unreleased] promoted to 4.8.0-beta.35. Theme (theme-dark/theme-light.css, THEME_COLORS.md, no flash); facility overlay/badges/overview/address/contacts/menu; buttons/modals/delete styling; document template preview; release notes popup; important info, technical support, devices, network PDF, FacilityContact; WeasyPrint service report PDF. CHANGELOG and BUILDLOG updated; VERSION 4.8.0-beta.34 → 4.8.0-beta.35.
  - Version bump: 4.8.0-beta.34 → 4.8.0-beta.35

- 2026-02-08 (Europe/Oslo)
  - Branch: dev
  - Summary:
    - Theme: Standardized colors – theme-dark.css and theme-light.css as single source; app.css uses var() throughout; docs/THEME_COLORS.md; theme flash removed (meta + script in head). Theme button between Service desk and Avatar, icon centered; red/green/primary adjusted.
  - (No version bump)

- 2026-02-08 (Europe/Oslo)
  - Branch: dev
  - Summary:
    - Portal facility: Service agreement status as overlay at bottom of facility image (gradient, centered badge); dot removed from badge; red text lighter (#fca5a5) for readability.
    - Portal facility: Overview boxes same size (min-height 64px, centered), labels with 2-line clamp and word-break against overflow.
    - Portal /facilities/: Street address shown under facility title; fallback to city/country.
    - Admin facility: important_info in FacilityForm and facility_form.html – section "Important info / Announcement (portal)" so announcement is edited from Edit Details.
  - (No version bump)

- 2026-02-08 (Europe/Oslo)
  - Branch: dev
  - Summary:
    - Portal: Release notes popup on first visit after final release – modal "New update" with descriptive text from RELEASE_NOTES.json, "View changelog" button, localStorage per version; context footer_info with release_notes_body/release_notes_version; RELEASE_NOTES.json (nb/en) and FILE_LOCATIONS updated.
  - (No version bump)

- 2026-02-08 (Europe/Oslo)
  - Branch: dev
  - Summary:
    - Design: Buttons in modals/forms with same height on one line (line-height, max-height 36px, vertical-align, inline-flex).
    - Design: Delete/danger buttons more visible red (#dc2626), not too dark; form-btn-danger, admin-btn-danger, admin-btn-sm.admin-btn-danger and backup-panel updated.
    - Modals: Inner border removed – modal-content, admin-modal-content, customer-switch-modal-content, rack-modal-dialog without border; box-shadow only (app.css, facility_card.html).
  - (No version bump)

- 2026-02-08 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.34
  - Summary:
    - CHANGELOG: Reorganized for readability – [Unreleased] grouped with #### (Portal, Admin, Design, Document template, Contacts); previous changes under "Previous changes (4.8.x)" with Fixes/Changes/Added and categories (PDF, Admin, compilemessages, Portal, Install, Service log).
    - BUILDLOG: Intro added; consistent "Version" on entries; short summaries where missing.
  - Version bump: 4.8.0-beta.33 → 4.8.0-beta.34

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.33
  - Summary:
    - Portal facility: Contacts at top of side menu and as default tab on open; overview route with Contacts first; default hash #contacts.
    - Portal facility: Important info on facility card – Facility.important_info (migration 0016), admin "Portal – important info", portal block "Important info" under overview.
    - Portal facility: Service agreement status in left column – green "Service agreement" / red "No service agreement" based on whether at least one device has SLA (is_sla).
    - Portal facility: Technical support / key contact – TechnicalSupportContact (migration 0017), admin Technical support contacts; portal box "Technical support" under service agreement badge with email/phone and support_info.
  - Version bump: 4.8.0-beta.32 → 4.8.0-beta.33

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: (no bump)
  - Summary:
    - Buttons and modals: View datasheet / Download PDF as app standard (primary/secondary); form-btn, modal-btn etc. adjusted; .modal-actions and .admin-form-actions standardized (app.css, backup_restore.html).

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: (no bump)
  - Summary:
    - Portal light/dark theme: CSS variables, improved light mode, theme toggle (sun/moon) at avatar (not pushed).

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.32
  - Summary:
    - Admin document template preview: white background in preview content; scrollbar styled to match admin; toolbar with icon buttons (Update, Open in new tab) on the right; preview box aligned with form start.
    - Admin document template edit: preview panel on the right (4/10 width); Update button and debounced auto-update for live draft preview; preview-draft endpoint (POST).
    - Portal facility: Product datasheets search field vertically centered with "Search"; Service log Type dropdown on same line as title; "View product datasheet" opens in new window.
    - Portal facility: Menu order changed to Devices, Racks, Network, Product datasheets, Service log, Documents, Contacts; default tab Devices; overview route updated.
    - Portal: Devices can be opened (facility_device_detail, /facilities/…/devices/&lt;id&gt;/, Open button); Network documentation under Network (equipment overview network devices only, Download PDF).
    - Master templates for PDF: DocumentTemplate (0014); admin Document templates (list/add/edit/delete, load default service report); WeasyPrint; service report PDF from template in admin and portal; print button on service report page generates PDF (facility_service_log_pdf).
    - Contacts: FacilityContact (migration 0015); admin tab Contacts on facility (CRUD, modal); portal tab and overview box Contacts; facility_contact_form + fragment; FILE_LOCATIONS.
  - Version bump: 4.8.0-beta.31 → 4.8.0-beta.32

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.31
  - Summary:
    - Portal datasheet: TOC 1/6 width, sticky with topbar offset, padding; removed Download PDF button; manufacturer PDF icon; custom tooltips only; print/PDF page breaks (before headings, no double break); th white text on dark bg in print/PDF
    - Portal /datasheets/: breadcrumb admin-breadcrumb; Create datasheet right; grid min 3 columns, Created/Updated dates; search with icon; datasheet_items view
    - Facility detail: Produktdatablader tab (unique datasheets, search, alphabetical); sidemenu URL hash (#racks, #devices, etc.); compact overview boxes
    - Footer: Knowledge base section with Produktdatablader link
    - Admin product datasheet list: title without duplicate; Create datasheet right; row actions as dots dropdown (View, Edit, Download PDF, Delete)
    - Version bump: 4.8.0-beta.30 → 4.8.0-beta.31

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.30
  - Summary:
    - WeasyPrint/pydyf: pin pydyf<0.12 in requirements (fix AttributeError 'super' has no attribute transform); portal and admin catch AttributeError and use xhtml2pdf fallback
    - Version bump: 4.8.0-beta.29 → 4.8.0-beta.30

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.29
  - Summary:
    - WeasyPrint PDF: portal and admin views catch OSError when Pango/Cairo missing and show friendly message with apt command; install.sh and update.sh add libcairo2 to WeasyPrint deps; docs/WEASYPRINT_PDF.md
    - Version bump: 4.8.0-beta.28 → 4.8.0-beta.29

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.28
  - Summary:
    - WeasyPrint PDF: install.sh and update.sh ensure Pango/GdkPixbuf system packages (libpango-1.0-0, libpangocairo-1.0-0, libgdk-pixbuf2.0-0) so service log PDF export works; update.sh runs an explicit apt-get install of these on every update
    - Version bump: 4.8.0-beta.27 → 4.8.0-beta.28

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.27
  - Summary:
    - Admin: product_datasheet_list expanded; portal: facility_service_log_detail and fragment; portal urls and views +59
    - Version bump: 4.8.0-beta.26 → 4.8.0-beta.27

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.26
  - Summary:
    - DocumentTemplate model (migration 0014); admin document_template list/form; portal facility_device_detail, facility_network_documentation_pdf and fragment; facility_detail, facility_detail_content; requirements +1
    - Version bump: 4.8.0-beta.25 → 4.8.0-beta.26

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.25
  - Summary:
    - Portal: datasheet_list, datasheet_detail; views; locale +3
    - Version bump: 4.8.0-beta.24 → 4.8.0-beta.25

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.24
  - Summary:
    - Portal: datasheet_detail, facility_detail, facility_detail_content, facility_service_log_detail and fragment (tweaks/layout)
    - Version bump: 4.8.0-beta.23 → 4.8.0-beta.24

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.23
  - Summary:
    - Portal: facility_detail, facility_detail_content, facility_service_log_detail and fragment; views; locale +3
    - Version bump: 4.8.0-beta.22 → 4.8.0-beta.23

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.22
  - Summary:
    - Admin: facility_card, facility_service_log_export_pdf; portal: datasheet_detail, facility_service_log_detail (layout/content)
    - Version bump: 4.8.0-beta.21 → 4.8.0-beta.22

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.21
  - Summary:
    - scripts/run_manage.sh: wrapper that loads .env and runs manage.py (fix manual commands missing POSTGRES_DB); update.sh migration message and SETUP_GUIDE, FILE_LOCATIONS, BUILDLOG updated
    - Portal: facility_detail, facility_service_log_detail and fragments, datasheet_detail, views; locale +15
    - Version bump: 4.8.0-beta.20 → 4.8.0-beta.21

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.20
  - Summary:
    - Locale: remove 2 duplicate msgid (Type, All) in nb django.po so compilemessages succeeds
    - Version bump: 4.8.0-beta.19 → 4.8.0-beta.20
  - Migration note: If update fails on portal.0014 with "relation ... already exists", migration 0014 may have been auto-generated on the server. If 0012 and 0013 are already applied, mark 0014 as applied: `sudo bash /opt/pmg-portal/scripts/run_manage.sh migrate --fake portal 0014` (only if 0014 exists). run_manage.sh loads .env so POSTGRES_DB etc. are set.

- 2026-02-07 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.19
  - Summary:
    - Admin: ServiceTypeAdmin search_fields (fix E040); register NetworkDevice (NetworkDeviceAdmin) for ServiceLogDeviceAdmin autocomplete (fix E039)
    - Version bump: 4.8.0-beta.18 → 4.8.0-beta.19
  - Versioning note: We stay on 4.8.0-beta.X for fixes and small changes in the 4.8 line. When stable: release as 4.8.0 (no suffix). Next minor line (e.g. new feature set): 4.9.0-beta.1. PATCH (4.8.1) for post-release bugfixes; MINOR (4.9.0) for new features; MAJOR (5.0.0) for breaking changes.

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.18
  - Summary:
    - Service log extensions: migrations 0012 (servicelog_extensions), 0013 (servicerapport, servicedevices); ServiceType, ServiceRapport, ServiceVisit; admin service_type list/form; facility_service_visit list/form/fragment; facility_service_rapport_form; attachment upload/fragment; export PDF; portal facility service log detail + datasheet updates; locale +153; SERVICEDESK_PLUS_INTEGRATION.md; requirements +1
    - Version bump: 4.8.0-beta.17 → 4.8.0-beta.18

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.17
  - Summary:
    - Locale: remove 2 more duplicate msgid (Search customers…, Inactive) in nb django.po
    - Install/update: full output logged to /var/log/pmg-portal-install-*.log and APP_DIR/logs/update-*.log; on failure print log path for debugging
    - Version bump: 4.8.0-beta.16 → 4.8.0-beta.17

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.16
  - Summary:
    - Scripts: compilemessages run with --locale nb in update.sh, install.sh, install-dual.sh, merge-dev-to-prod.sh (only project locale compiled)
    - Version bump: 4.8.0-beta.15 → 4.8.0-beta.16

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.15
  - Summary:
    - Locale: remove 12 duplicate msgid in nb django.po so compilemessages (msgfmt) succeeds on server
    - Version bump: 4.8.0-beta.14 → 4.8.0-beta.15

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.14
  - Summary:
    - FacilityAdmin: use Facility fields only (name, slug, customer_count; list_filter is_active); fix E108/E116 (no customer field, use customers M2M)
    - Version bump: 4.8.0-beta.13 → 4.8.0-beta.14

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.13
  - Summary:
    - Admin: register Facility in portal admin (FacilityAdmin) so ServiceLogAdmin autocomplete_fields works; fixes E039 and update/migrate on server
    - Version bump: 4.8.0-beta.12 → 4.8.0-beta.13

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.12
  - Summary:
    - ServiceLog model (portal); migration 0011_servicelog; admin facility_service_log_form + fragment; portal facility_service_log_detail + fragment; facility_card, facility_list, facility_detail updates
    - Admin: backup_restore, base, customer_*, portal (announcement, portal_link), user (role, user list); forms, views, urls; site_footer; portal admin, models, base, datasheet_detail/datasheet_pdf; locale nb +421
    - Version bump: 4.8.0-beta.11 → 4.8.0-beta.12

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.11
  - Summary:
    - Portal datasheet: datasheet_list view + URL /datasheets/; datasheet_detail TOC (left, no-print), actions centered, button visibility; back to Product datasheets; Norwegian strings; datasheet_pdf translated labels; datasheet_list.html
    - Version bump: 4.8.0-beta.10 → 4.8.0-beta.11

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.10
  - Summary:
    - Portal: datasheet_detail.html, datasheet_pdf.html template updates
    - Version bump: 4.8.0-beta.9 → 4.8.0-beta.10

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.9
  - Summary:
    - Migration 0010: fix AlterModelOptions (name= not model_name=) for Django compatibility
    - Version bump: 4.8.0-beta.8 → 4.8.0-beta.9

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.8
  - Summary:
    - Install/update: add pkg-config and libcairo2-dev for xhtml2pdf/pycairo; update.sh ensures system deps before pip install
    - Version bump: 4.8.0-beta.7 → 4.8.0-beta.8

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.7
  - Summary:
    - Product datasheet: content_md, updated_at, file optional; migration 0010_product_datasheet_content_updated; portal views/templates datasheet_detail, datasheet_pdf, datasheet_not_found; portal urls; admin forms/views/device templates updated
    - requirements.txt: markdown, xhtml2pdf (PDF generation); install wizard unchanged (pip -r + migrate cover new deps and migration)
    - Version bump: 4.8.0-beta.6 → 4.8.0-beta.7

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.6
  - Summary:
    - Admin templates restructure: moved to subdirs backup/, customer/, device/, facility/, notifications/, portal/, user/; urls.py and views.py updated for new paths; backup_restore.py template path
    - FILE_LOCATIONS.md; BACKWARDS_COMPATIBILITY, BUILDLOG, CHANGELOG, CHANGELOG_SUMMARY, IMPROVEMENTS, README, SETUP_GUIDE, docs/* updated; install.sh, update.sh; locale nb +9
    - Version bump: 4.8.0-beta.5 → 4.8.0-beta.6

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.5
  - Summary:
    - Admin device templates: device_category, device_instance, device_landing, device_type, facility_device_choose_type, home, manufacturer, product_datasheet – refinements
    - Version bump: 4.8.0-beta.4 → 4.8.0-beta.5

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.4
  - Summary:
    - Portal base.html updates; site_footer.html; app.css +81
    - Version bump: 4.8.0-beta.3 → 4.8.0-beta.4

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.3
  - Summary:
    - Backwards compatibility: SystemInfo (portal), migration 0009_systeminfo; pmg_portal.versioning + version_middleware; set_stored_version management command; install.sh/update.sh run set_stored_version after migrate
    - Backup manifest: app_version in manifest; backup_restore supports versioned format; settings middleware
    - Portal: base.html, views; models SystemInfo; app.css tweaks
    - BACKWARDS_COMPATIBILITY.md: upgrade/downgrade, feature and file compatibility guidelines
    - Version bump: 4.8.0-beta.2 → 4.8.0-beta.3

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.2
  - Summary:
    - Admin: notifications (list), announcements (list/form); admin_app models.py, migration 0001_add_admin_notifications
    - Admin: device categories, manufacturers, product datasheets (list/form each); device_landing; device type/instance templates and views updates; urls +30
    - Portal models: announcements, preferences; devices, manufacturer, category, datasheet, SLA; migrations 0007, 0008
    - Portal: base.html +238, facility_detail + fragments refactor; customer_home_content, no_customer; urls, views, context_processors
    - app.css +370; site_footer; forms.py, views.py major updates
    - Version bump: 4.8.0-beta.1 → 4.8.0-beta.2

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.8.0-beta.1
  - Summary:
    - Device types: admin list, detail, form (device_type_list, device_type_detail, device_type_form); urls, views, forms
    - Device instances (rack devices): add choose facility, form, form fragment; facility card device choose type fragment; views, urls, forms
    - Portal models: DeviceType and device instance type/product FK; migration 0006_device_type_and_product_fk
    - facility_card.html, home.html; locale nb +12; docs/UI_UX_IMPROVEMENT_IDEAS.md
    - Version bump: 4.7.0-beta.15 → 4.8.0-beta.1 (MINOR: device types & instances)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.15
  - Summary:
    - Admin: network device add – choose facility (network_device_add_choose.html, view, URL); home.html, network_device_list.html, urls.py, views.py updates
    - Portal: facility_list.html, facility_list_content.html tweaks
    - app.css: +20 lines; locale nb django.po: +6 strings
    - Version bump: 4.7.0-beta.14 → 4.7.0-beta.15

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.14
  - Summary:
    - Facility card: refactored to use fragment templates for modals; views.py updated to serve fragments
    - New fragment templates: facility_customers_edit_fragment, facility_document_form_fragment, ip_address_form_fragment, network_device_form_fragment, rack_form_fragment
    - facility_card.html, views.py: +211/-107
    - Version bump: 4.7.0-beta.13 → 4.7.0-beta.14

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.13
  - Summary:
    - settings.py: config update (+3 lines)
    - Version bump: 4.7.0-beta.12 → 4.7.0-beta.13

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.12
  - Summary:
    - ip_address_form.html, views.py: small form and view tweaks
    - Version bump: 4.7.0-beta.11 → 4.7.0-beta.12

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.11
  - Summary:
    - ip_address_form.html, views.py: IP address form and view updates (+26/-6)
    - Version bump: 4.7.0-beta.10 → 4.7.0-beta.11

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.10
  - Summary:
    - ip_address_form.html, views.py: IP address form and view tweaks
    - Version bump: 4.7.0-beta.9 → 4.7.0-beta.10

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.9
  - Summary:
    - IP address: delete button partial _ip_address_delete_btn.html; ip_address_form.html update
    - Version bump: 4.7.0-beta.8 → 4.7.0-beta.9

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.8
  - Summary:
    - views.py: small tweak
    - Version bump: 4.7.0-beta.7 → 4.7.0-beta.8

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.7
  - Summary:
    - views.py: admin view logic updates and refinements (+46/-8)
    - Version bump: 4.7.0-beta.6 → 4.7.0-beta.7

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.6
  - Summary:
    - ip_address_form.html, views.py: small tweaks
    - Version bump: 4.7.0-beta.5 → 4.7.0-beta.6

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.5
  - Summary:
    - Admin: network device list page (network_device_list.html, view, URL); admin home link
    - views.py: network device list logic and refactor; urls.py: new route
    - Version bump: 4.7.0-beta.4 → 4.7.0-beta.5

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.4
  - Summary:
    - rack_detail.html: template refactor and layout updates
    - ip_address_form.html, site_footer.html, portal base.html: small tweaks
    - app.css: styling updates
    - Version bump: 4.7.0-beta.3 → 4.7.0-beta.4

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.3
  - Summary:
    - backup_restore.py + backup_restore.html: backup/restore logic and UI improvements
    - facility_card.html, rack_detail.html: layout and template refinements
    - admin home.html, views.py: small updates
    - admin base.html, site_footer.html, portal base.html: layout/footer tweaks
    - portal facility_list + facility_list_content: updates
    - app.css: styling changes
    - locale nb django.po: +3 strings
    - Version bump: 4.7.0-beta.2 → 4.7.0-beta.3

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.2
  - Summary:
    - Locale: removed duplicate msgid entries in src/locale/nb/LC_MESSAGES/django.po so compilemessages (msgfmt) succeeds on install/update
    - update.sh: compilemessages with verbosity 1 and clearer error message on failure
    - Version bump: 4.7.0-beta.1 → 4.7.0-beta.2

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-beta.1
  - Summary:
    - Stage: alpha → beta (features complete, ready for testing)
    - URLs: facility_customer_add, ip_address add/edit/delete, facility_document upload/delete, network_device delete
    - Templates: ip_address_form.html, facility_document_form.html, facility_customer_add.html (add-one customer to facility)
    - Shared footer: site_footer.html include (version, About, View Changelog, language dropdown with flags); portal base and admin use it
    - Install scripts: comment that postgresql-client provides pg_dump/psql for Backup & Restore
    - Facility card, facility_customers_edit, rack_detail, rack_form, network_device_form: refinements and breadcrumb/modal
    - Norwegian: +168 translation strings in django.po
    - CSS: footer and layout adjustments
    - Version bump: 4.7.0-alpha.1 → 4.7.0-beta.1 (beta release)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.7.0-alpha.1
  - Summary:
    - Backup & Restore: backup_restore.py (pg_dump + media tar), backup_restore view and template, URL server/backup-restore/, admin home "Server management" panel for superusers
    - Facility customers edit: FacilityCustomersEditForm (checkboxes), facility_customers_edit view and template (search filter), URL facilities/<slug>/customers/; replaces add-one flow with batch edit
    - Facility card: Edit facility and "Manage access" open in modals (iframe); postMessage pmg-facility-modal-close to close and reload; Remove per customer; Delete rack in Racks tab; i18n ({% trans %}) on tabs and labels
    - facility_edit: in_modal support, redirect with ?modal_close=1
    - Rack detail: rack-detail-grid layout; Front/Rear view tabs (rack-view-tabs); device units and empty units call openDeviceModal(deviceId, position); rear view placeholder
    - network_device_add/edit: in_modal and cancel_url/redirect with modal_close=1 for rack detail
    - Views: gettext (_) for facility and facility_customer messages
    - Portal base: removed 38 lines (cleanup)
    - Norwegian translations: django.po +33 strings
    - CSS: admin-backup-form, rack-detail-grid, rack-view-tabs, etc.
    - Version bump: MINOR increment from 4.6.0-alpha.1 to 4.7.0-alpha.1 (backup/restore, facility modals, rack grid/front-rear)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.6.0-alpha.1
  - Summary:
    - Rack detail: two-column layout (rack-detail-layout) – left: rack-detail-left (visual + rack-detail-card + rack-detail-sidemenu), right: rack-detail-main with tab panels
    - Edit Rack in modal: Edit link uses ?modal=1; rack-edit-modal with backdrop, dialog, iframe; JS opens iframe to edit URL, closes on backdrop/close button; iframe detects modal_close=1 and posts message to parent to close and reload
    - rack_edit view: in_modal=request.GET.get('modal')==1; redirect appends ?modal_close=1 when in_modal; cancel_url uses modal_close when in_modal
    - Danger buttons: form-btn-danger and admin-btn hover use rgba for softer look; admin-btn-sm.admin-btn-danger hover rgba
    - Rack container: max-width 1280px, margin auto (removed full-width override); breadcrumb-row margin-bottom 24px; removed .rack-detail-tabs margin
    - Version bump: MINOR increment from 4.5.0-alpha.1 to 4.6.0-alpha.1 (rack detail layout and edit modal)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.5.0-alpha.1
  - Summary:
    - Facility customer access: FacilityCustomerAddForm; facility_customer_add and facility_customer_remove views to add/remove customers from facility
    - IP address management: IPAddressForm (ip_address, subnet, reserved_for, description, device); ip_address_add, ip_address_edit, ip_address_delete views
    - Facility document management: FacilityDocumentForm (title, description, file, category); facility_document_upload and facility_document_delete views
    - Network device: network_device_delete view
    - Rack detail: header redesigned to card style (rack-card-header, customer-card-header); icon, title block with U/location/serial, Active/Inactive badge, Edit icon button, Add Seal button, meta and description; tabs use customer-card-tabs
    - List pages: toolbar search/filter layout changed to admin-search-group and admin-filter-group (label above input); Search button separate at end
    - CSS: breadcrumb-back-btn as pill (padding, border, border-radius, focus outline); admin-search-wrap align flex-end, admin-search-group column layout; admin-btn-sm height 32px, View buttons transparent/outline, danger red tint; rack-detail-container full width, rack-card-header icon wrap
    - Version bump: MINOR increment from 4.4.0-alpha.1 to 4.5.0-alpha.1 (IP/document/customer access management, UI)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.4.0-alpha.1
  - Summary:
    - Breadcrumb: added breadcrumb-row and contextual back button (← Admin, ← Customers, etc.) on all admin pages
    - Each template overrides breadcrumb_back for list or parent (e.g. facility form → Facilities, network device form → rack or facility)
    - Card title block: customer/facility/user cards show slug under name in customer-card-title-block
    - Facility card: country flag (admin_extras country_flag filter), active/inactive badge, created/updated meta in header
    - Information tab removed from customer card and facility card; key info moved to header
    - Smart cancel: facility_form and network_device_form use cancel_url from view context for Cancel button
    - Views: facility_edit and network_device_add/edit pass cancel_url for contextual cancel
    - New templatetags: admin_app/templatetags/admin_extras.py with country_flag filter (country name/code → flag emoji)
    - List pages: Add buttons use admin-toolbar-add-btn only; table action columns use admin-table-actions class
    - Rack detail: tab switching refactor with activateTab; tab IDs for visual, devices, seals, info
    - Portal facility detail: breadcrumb/layout alignment with admin
    - CSS: breadcrumb-back-btn, breadcrumb-row, customer-card-title-block, customer-card-slug, customer-card-badge, customer-card-flag, customer-card-meta
    - Version bump: MINOR increment from 4.3.0-alpha.1 to 4.4.0-alpha.1 (UI/UX and navigation)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.3.0-alpha.1
  - Summary:
    - Card header redesign: Edit and Delete actions moved to card header as icon buttons (customer, facility, user cards)
    - Icon buttons: compact 36x36px icon buttons with hover states and color coding (blue for edit, red for delete)
    - Header actions: customer-card-name-wrapper with flexbox layout for name and action buttons
    - Admin content width: increased from 980px to 1280px for consistency with portal layout
    - Rack detail width: increased max-width from 1200px to 1280px
    - Customer selection width: increased max-width from 1000px to 1280px
    - Tab styling: improved hover states (light blue background), active state (blue text, blue border, blue background tint, bold font)
    - Tab spacing: reduced gap from 8px to 4px, added padding to container, reduced tab padding
    - Tab border radius: added border-radius to tabs for rounded top corners
    - CSS updates: customer-card-icon-btn styles with transitions, hover effects, and color variants
    - User card: delete button only shows if user is not the current user (prevents self-deletion)
    - Version bump: MINOR increment from 4.2.0-alpha.1 to 4.3.0-alpha.1 (UI/UX improvements)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.2.0-alpha.1
  - Summary:
    - Network Device Management: complete CRUD operations for network devices in admin panel
    - NetworkDeviceForm: new form with facility and rack filtering, pre-selection of rack and position
    - Network device views: network_device_add, network_device_edit, network_device_remove_from_rack
    - Add device from rack: can add device directly from rack detail view with rack and position pre-selected
    - Add device at position: can add device at specific U-position from rack visualization
    - Remove from rack: removes device from rack (clears rack and rack_position) while keeping device in facility
    - Device links: network devices in facility and rack views show rack name and U-position as clickable links
    - Edit device: automatic redirect back to rack detail if device is assigned to rack
    - Network device URLs: nested under facility URLs (facilities/<slug>/devices/<id>/)
    - Rack integration: rack detail view JavaScript functions now redirect to actual device forms
    - Template: network_device_form.html for adding/editing network devices
    - Migration reorganization: deleted 0004_rack_serial_and_seals.py, created 0004_facility_and_racks.py and 0005_rack_serial_and_seals.py
    - Version bump: MINOR increment from 4.1.0-alpha.1 to 4.2.0-alpha.1 (new features: Network Device Management)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.1.0-alpha.1
  - Summary:
    - Rack Management: complete CRUD operations for racks in admin panel
    - Rack model: added serial_number field for asset tracking
    - Rack methods: added get_active_seals() and get_devices_by_position() helper methods
    - RackSeal model: new model for tracking security seals on racks with installation/removal history
    - Rack forms: RackForm with name uniqueness validation within facility, RackSealForm with active seal validation, RackSealRemovalForm for seal removal tracking
    - Rack views: rack_add, rack_detail, rack_edit, rack_delete views with full CRUD functionality
    - Rack detail page: interactive rack visualization showing U-positions and devices
    - Rack seal management: rack_seal_add and rack_seal_remove views for seal installation/removal
    - Seal tracking: tracks installed_by, installed_at, removed_by, removed_at, removal_reason, removal_notes
    - Active seal validation: prevents duplicate active seal IDs on same rack
    - Rack URLs: nested under facility URLs (facilities/<slug>/racks/<id>/)
    - Templates: rack_detail.html with U-position visualization, rack_form.html, rack_seal_form.html, rack_seal_remove_form.html
    - Migration: 0004_rack_serial_and_seals.py adds serial_number to Rack and creates RackSeal model
    - UI improvements: unified breadcrumb styling (admin-breadcrumb class), customer switch redirects to referer
    - Version bump: MINOR increment from 4.0.0-alpha.1 to 4.1.0-alpha.1 (new features: Rack Management)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 4.0.0-alpha.1
  - Summary:
    - URL structure: changed Facility URLs from primary key (pk) to slug-based (slug) for better SEO and user-friendly URLs
    - Breaking change: all Facility URLs now use slug instead of pk (admin and portal views updated)
    - Slug validation: added unique slug validation in FacilityForm to prevent duplicate slugs
    - Admin URLs: updated admin_app URLs to use slug pattern (<slug:slug> instead of <int:pk>)
    - Portal URLs: updated portal URLs to use slug pattern (<slug:slug> instead of <int:pk>)
    - Views updated: facility_detail, facility_edit, facility_delete now accept slug parameter instead of pk
    - Templates updated: all Facility templates updated to use slug in URLs (admin and portal)
    - UI improvements: added breadcrumb navigation and back button to Facility detail page
    - Network tab: combined Network Devices and IP Addresses into single Network tab with combined statistics
    - Norwegian translations: added 159 new Norwegian translation strings for Facility management features
    - Placeholder functionality: added "coming soon" alerts for Add Rack, Add Device, Add IP Address, Upload Document buttons
    - CSS updates: added styles for breadcrumb navigation and facility back button
    - Version bump: MAJOR increment from 3.1.0-alpha.1 to 4.0.0-alpha.1 (breaking change: URL structure)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 3.1.0-alpha.1
  - Summary:
    - HTMX support: added HTMX navigation to Facility list and detail views for seamless page transitions
    - Facility views: detect HX-Request header and return fragment templates for HTMX requests
    - Facility link: added HTMX attributes (hx-get, hx-target, hx-swap, hx-push-url) to Facility button in topbar
    - Title updates: Facility views set HX-Trigger header to update page title dynamically
    - Production readiness: Facility templates now kept in main branch (no longer removed during cleanup)
    - Install/update scripts: updated to keep Facility templates in production (commented out removal logic)
    - Version bump: MINOR increment from 3.0.3-alpha.1 to 3.1.0-alpha.1 (new features/UI improvements)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 3.0.3-alpha.1
  - Summary:
    - Migration fake command: fixed Django migrate --fake syntax to use separate app label and migration name arguments
    - Split migration identifier (e.g., "portal.0004_facility") into APP_LABEL and MIGRATION_NAME for correct Django command format
    - Added fallback to old format if migration identifier doesn't match expected pattern
    - Improved migration faking reliability by using correct Django command syntax: migrate --fake <app_label> <migration_name>
    - Version bump: PATCH increment from 3.0.2-alpha.1 to 3.0.3-alpha.1 (bugfix/stability improvement)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 3.0.2-alpha.1
  - Summary:
    - Migration handling: improved migration error handling in update.sh script
    - Enhanced migration name detection with multiple patterns (Applying portal.XXXX_, portal.XXXX_ anywhere, Django showmigrations fallback)
    - Better error messages and fallback instructions when migration detection fails
    - Improved error handling to continue with other steps instead of exiting on migration detection failure
    - Version bump: PATCH increment from 3.0.1-alpha.1 to 3.0.2-alpha.1 (bugfix/stability improvement)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 3.0.0-alpha.1
  - Release Type: Alpha Release
  - Summary:
    - Initial Facility (Anlegg) management system implementation
    - Added Facility model with comprehensive fields and customer-facility many-to-many relationship
    - Admin panel: Facility CRUD operations, list, detail card page with tabs
    - Portal: Facility list and detail pages with overview, racks, network devices, IP addresses, documents tabs
    - Related models: FacilityDocument, Rack, NetworkDevice, IPAddress for complete facility management
    - UI/UX: Modern facility cards, tabbed detail view, responsive design
    - Context processor updated to include user facilities based on active customer
    - Foundation for future facility features: installations, management, operations, maintenance, documentation, network management

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 3.0.0-alpha.1
  - Release Type: Alpha Release
  - Summary:
    - Complete Facility (Anlegg) management system implementation
    - Added Facility model with comprehensive fields (name, slug, description, address, city, postal code, country, contact information)
    - Customer-Facility many-to-many relationship for access control
    - Admin Panel: Full CRUD operations for Facilities (list, add, detail card, edit, delete)
    - Portal: Facility list and detail pages with overview statistics
    - Related models: FacilityDocument, Rack, NetworkDevice, IPAddress
    - Context processor updated to include user facilities based on active customer
    - Facility button enabled in portal topbar when customer profile is selected
    - Facility link added to admin home in Portal management section
    - Removed dev feature protection (ENABLE_DEV_FEATURES, DEV_ACCESS_USERS) - Facility features now directly available
    - All Facility views use standard @staff_required decorator (admin) and @login_required (portal)
    - Fixed: Added Facility import to context_processors.py
    - Fixed: Updated install.sh rsync to use --delete flag to ensure all templates are synced
    - Foundation for future facility features: installations, management, operations, maintenance, documentation, network management

- 2026-02-06 (Europe/Oslo)
  - Branch: dev → main
  - Version: 2.0.0
  - Release Type: Final Release (Major)
  - Summary:
    - Final release v2.0.0: Major release consolidating all features and improvements from 0.1.0-alpha.1 through 1.18.0-beta.1
    - Complete admin panel: Custom admin app with user management, customer management, and portal management
    - Customer management: Logo upload, customer card page, selection flow, switch modal, search functionality
    - User management: User card page, profile settings, delete functionality with confirmation modals
    - Internationalization: Full Norwegian (Norsk) support with language switcher
    - UI/UX: Modern dark theme, responsive design, toast notifications, animated transitions
    - Developer tools: Debug view, comprehensive logging, update checks
    - Documentation: Setup guides, i18n documentation, admin layout documentation
    - Hundreds of bug fixes, improvements, and enhancements across all areas
    - Version bump: Major version from 0.1.0 to 2.0.0 reflecting significant feature additions and improvements

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.18.0-beta.1
  - Summary:
    - Delete functionality: implemented delete functionality for customers and users with warning modal and 3-second countdown
    - User card page: created user detail page similar to customer card showing user info, memberships, and details
    - UI improvements: standardized button widths, made delete buttons darker red, updated delete modal design to match profile settings
    - Width adjustments: increased customer selection width to 1000px, made customer card use full container width
    - Modal fixes: fixed delete modal positioning to center on screen, updated design to match profile settings modal
    - Version bump: incremented minor version from 1.17.51 to 1.18.0 due to new features (delete functionality, user card page)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.51-beta.1
  - Summary:
    - Customer selection scroll fix: improved CSS flexbox layout to prevent entire page from scrolling
    - CSS: added overflow: hidden to #main-content and improved customer-selection-container height constraints
    - Version bump: incremented patch version from 1.17.50 to 1.17.51 due to multiple fixes and improvements

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.50-beta.27
  - Summary:
    - Customer selection flow: implemented explicit customer profile selection on login (no auto-select for multiple customers)
    - Customer selection page: compact list layout with search field (when >4 customers), scroll only on list not entire page
    - Customer switch: moved from topbar dropdown to avatar menu with modal interface
    - Auto-selection: automatically select single customer profile when user has access to only one
    - UI improvements: changed text to "customer profile" throughout, updated icons, fixed scroll behavior
    - Translations: added Norwegian translations for all customer profile selection texts
    - JavaScript: fixed syntax errors by replacing inline onclick with data attributes and event listeners
    - CSS: improved customer selection container layout with proper flexbox and overflow handling

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.50-beta.26
  - Summary:
    - Customer card page: modern customer detail page with logo upload/delete, member management, and portal links tabs
    - Logo upload: AJAX-based upload with client-side preview, automatic old logo deletion when replacing
    - Logo storage: explicit file saving to Django storage before model assignment to ensure files are written to disk
    - Media file serving: Django view added to serve media files in production as fallback when nginx is not serving them
    - Logo deletion: improved cleanup of old logo files when new logos are uploaded or customers are deleted
    - Logging: added admin_app logger with INFO level for debugging logo upload and file storage issues
    - File storage debugging: enhanced logging with file existence checks, directory listings, and permissions verification
    - Customer form: improved redirect flow to customer card page after add/edit operations
    - URL routing: fixed duplicate import and added proper media file serving for production environments

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.50-beta.25
  - Summary:
    - Customer logo display: fixed layout with logo on left (120x120px), customer name and description text on right
    - Media files: updated nginx config to serve /media/ files; Django serves media files as fallback
    - CSS: improved customer-header layout with flexbox for better alignment

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.49-beta.24
  - Summary:
    - Customer logo: added ImageField to Customer model with upload_to="customer_logos/"
    - Customer form: added logo upload field with preview of current logo (if exists)
    - Media files: configured MEDIA_ROOT and MEDIA_URL in settings; added URL routing for media files in development
    - Dashboard: logo displayed next to customer name on dashboard (customer_home.html and fragments)
    - File cleanup: Customer.delete() override to automatically delete logo file when customer is deleted
    - Admin views: updated customer_add and customer_edit to handle request.FILES for logo uploads
    - CSS: added .customer-title and .customer-logo styles for logo display
    - Migration: created 0003_customer_logo.py migration
    - Translations: added Norwegian translation for logo help text
    - Pillow dependency: added Pillow==10.4.0 to requirements.txt for ImageField support
    - Install scripts: updated install.sh and update.sh to install Pillow system dependencies (libjpeg-dev, libpng-dev, zlib1g-dev)

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.48-beta.23
  - Summary:
    - Login card: centered content horizontally and vertically using flexbox; removed fixed min-height for dynamic sizing
    - Sign in button: replaced rotating conic-gradient spinner with subtle pulsing border animation (box-shadow pulse)
    - Login page footer: added copyright notice on left side ("Copyright © [year] 5echo.io. All rights reserved.")
    - Sign in button: added loading spinner indicator (rotating border) when form is submitted
    - django.po: added "All rights reserved." / "Alle rettigheter reservert." translation

- 2026-02-06 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.47-beta.22
  - Summary:
    - Files button: added to topbar navigation after Facility with "under development" tooltip
    - Login/register card: fixed min-height (400px login, 500px register) to prevent resizing when filling forms
    - Register page: added footer with version and language selector (matches login page layout)
    - Login/register transitions: fade out animation (300ms) when clicking links; register page expands height and fades in on load
    - django.po: added "Files" / "Filer" translation
    - Fixed: LANGUAGE_SESSION_KEY error (using 'django_language' string directly)
    - Fixed: LanguagePreferenceMiddleware moved after AuthenticationMiddleware

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.46-beta.21
  - Summary:
    - Login page footer: moved version and language selector to right side together
    - Customer dropdown menu: active customer shown as disabled div (non-clickable) with checkmark; only other customers selectable
    - Login page language dropdown: uses other_languages context (excludes current language) to match avatar menu behavior
    - Language preference sync: custom set_language_custom view saves preference to session; LanguagePreferenceMiddleware applies it; login_view restores preferred language on login
    - Projects button: added to topbar navigation between Dashboard and Facility with "under development" tooltip
    - django.po: added "Projects" / "Prosjekter" translation

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.45-beta.20
  - Summary:
    - Footer "View Changelog": added document icon to match "About this portal" styling
    - Footer buttons: unified styling for "About this portal" and "View Changelog" (merged CSS classes, consistent hover and layout)
    - Login page footer: further reduced margin-top from 16px to 8px to bring version and language selector much closer to login box

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.44-beta.19
  - Summary:
    - Customer dropdown menu: rebuilt positioning (removed align-self center from wrapper, changed menu positioning to top: 100% with margin-top: 4px, improved transform animation from -8px to 0)
    - Footer buttons: removed padding (8px 12px → 0) and margin-top to match left side text spacing; hover now only changes color instead of background
    - Login page footer: reduced margin-top from 24px to 16px to bring version and language selector closer to login box

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.43-beta.18
  - Summary:
    - Tooltip position: moved below buttons (Facility and Service desk) instead of above
    - Customer dropdown menu: improved vertical positioning (reduced top offset from 2px to 4px, transform from -10px to -4px)
    - Footer "About this portal": added book icon back
    - Footer buttons: improved styling with better padding (8px 12px) and hover background effect
    - Footer layout: "View Changelog" moved under "About this portal" in right section
    - Fixed JavaScript linter errors in customer menu onclick handler (using dataset instead of template variable)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.42-beta.17
  - Summary:
    - Service desk button: added to topbar-right (before avatar) with message icon; shows "under development" tooltip on hover
    - Custom tooltip component: created for Facility and Service desk buttons (styled to match site design, appears on hover)
    - About this portal: moved from avatar menu to footer (right side)
    - Footer layout: changed from grid to flex with space-between for left/right sections
    - django.po: added "Service desk" translation

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.41-beta.16
  - Summary:
    - About modal: added "Head developer: Kevin Jung Park" in developer section
    - About button: renamed to "About this portal" (EN) / "Om portalen" (NO); icon changed to book/document icon
    - django.po: added "Head developer" / "Hovedutvikler" translation

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.40-beta.15
  - Summary:
    - About modal: accessible from avatar menu (all users); shows version, 5echo.io info, developer credits
    - About modal: update check for admins (GitHub main branch comparison); update badge in avatar menu when available
    - Facility: Norwegian translation "Fasilitet" → "Anlegg"
    - portal/views.py: check_updates endpoint for AJAX version check
    - portal/context_processors.py: about_info processor checks GitHub for updates (cached 1h, admin only)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.39-beta.14
  - Summary:
    - Norwegian flag: correct SVG (red field, white-outlined blue cross, 22:16)
    - Login page: language selector is a dropdown (all languages, current marked); closes on outside click / mouse leave
    - CHANGELOG: only full releases get version sections; pre-releases stay under Unreleased
    - Sign in button: short pulse border in loop (narrow wedge), no solid glow; dampened hover (brightness 1.08)
    - django.po: "Select language" for login dropdown aria-label

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.38-beta.13
  - Summary:
    - install.sh: add gettext to apt-get install so msgfmt is available for compilemessages
    - update.sh: if msgfmt missing, install gettext so compilemessages succeeds on existing servers
    - docs/I18N.md: note that gettext is installed by install/update scripts

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.37-beta.12
  - Summary:
    - update.sh + install.sh: run compilemessages so Norsk works after pull and on fresh install
    - update.sh: comment documents update command (cd /opt/pmg-portal && sudo git pull origin dev && sudo bash scripts/update.sh)
    - SETUP_GUIDE.md: "Updating the app" section with exact command

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 1.17.36-beta.11
  - Summary:
    - Norwegian (Norsk) added: Django i18n (LocaleMiddleware, LOCALE_PATHS, set_language), locale/nb/LC_MESSAGES/django.po with translations
    - Avatar menu: language dropdown shows Norsk and English (with flags); current language not listed in submenu; switch via POST to /i18n/setlang/
    - Login page footer (right): current language + link to switch to other language
    - All portal/accounts templates use {% trans %}/{% blocktrans %}; site_footer and changelog modal translated
    - docs/I18N.md: guide for adding and translating strings (Norsk + English) when building further

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.36-beta.10
  - Summary:
    - Topbar: "Portal" renamed to "Dashboard"
    - Avatar menu: Language submenu on click (not hover), close on mouse leave; current language hidden in submenu
    - Login page: version below card (left), language (English + flag) below card (right)
    - Sign in: single moving pulse animation around button when ready; MINOR/PATCH from changelog (0.15.36)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.22-beta.9
  - Summary:
    - Login Sign in: animated circulating green stripe around button when ready
    - Customer dropdown: active customer indicated with checkmark icon
    - Topbar: Facility button (disabled, tooltip "This feature is under development")
    - Avatar menu: Language (English) with UK flag; hover submenu to select English

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.22-beta.8
  - Summary:
    - Login: Create account link less bold and centered; Sign in button disabled until email+password filled, green border when ready
    - Register: removed "This creates a user."; Back to login less bold and centered
    - Customer dropdown: more padding on items, no gap between items; dropdown 2px below trigger; topbar align with avatar

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.22-beta.7
  - Summary:
    - Admin users: SEARCH label, narrow Search button, Add user 36px, wider search field; user form: checkbox layout, Save/Cancel height, narrow Save
    - Admin roles/customers/access: same toolbar layout (SEARCH, aligned search+button, Add on right); RoleForm for roles add (fix 500); CustomerForm queryset for customers add
    - Admin customer access add: form centered

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.22-beta.6
  - Summary:
    - Changelog modal: state-based toggle (data-changelog-view) and setTimeout(220) for panel swap so Hide Full / View Full and reopen work
    - Changelog intro text shortened to "All pre-release builds (alpha, beta, rc) are shown as Unreleased"
    - CHANGELOG Previous changes (pre-0.3.0): one Added, one Changed, one Fixed (no duplicate lists per section)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.22-beta.5
  - Summary:
    - Changelog Unreleased: only one section shown; parse stops at next ## heading (no duplicate Added/Changed/Fixed from Previous changes)
    - Changelog modal: animation on View Full / Hide Full Changelog button (pulse on toggle)
    - BUILDLOG: all changes listed for each build

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.22-beta.4
  - Summary:
    - Changelog: all pre-release builds (alpha, beta, rc) = Unreleased until plain MAJOR.MINOR.PATCH; one consolidated [Unreleased], no duplicates
    - Context: rc treated as Unreleased; changelog cleaned and deduplicated

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.15.19-beta.3
  - Summary:
    - Customer dropdown: reduced vertical spacing between list items (min-height 0, padding 4px 12px, line-height 1.25)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.3.0-beta.2
  - Summary:
    - Added: Changelog modal "View Full Changelog" / "Hide Full Changelog" toggle
    - Added: Profile Account Information edit (pencil) button for email, first name, last name
    - Added: Panel footer on Account Information for "Joined [date]" and future account metadata
    - Added: Migration accounts.0001_sync_username_from_email (User.username from User.email)
    - Changed: Changelog in footer beta versions show version section
    - Changed: Avatar initial: first letter of first name, then last name, then email
    - Changed: Customer dropdown tighter row spacing (min-height 28px, padding 0 12px); wrapper align-self center
    - Changed: Login field labeled "Email"; accepts email or username; login with email preferred
    - Changed: Registration username hidden and set from email; new users username = email
    - Changed: Profile delete account confirm with email instead of username
    - Changed: Install wizard first admin created with username = email; prompt DEFAULT_ADMIN_EMAIL
    - Fixed: Changelog footer not showing latest beta section
    - Fixed: Profile modal Cancel/Escape restoring Account Information tab (including Escape key)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.3.0-beta.1
  - Summary:
    - Added: Portal at site root (/) with HTMX for no-refresh navigation
    - Added: Custom admin app at /admin/ (User management, Customers & access, Portal management)
    - Added: Customer dropdown in header (avatar-style with search when >4 customers)
    - Added: Superusers can switch to any customer; redirect to / after customer switch
    - Added: Wider layout (1280px) aligned with topbar and footer
    - Added: Admin list filters Staff/Active labels, single-row toolbar, outlined Search button
    - Added: Admin forms card layout, two-column rows (e.g. username|email), aligned Save/Cancel
    - Added: Profile modals Cancel restores active tab to Account Information
    - Changed: Version scheme to beta
    - Changed: Buttons smaller (36px height), vertically centered, Search button outlined
    - Changed: Footer max-width 1280px, responsive padding
    - Changed: Customer dropdown reduced row spacing (min-height 32px, padding 2px 12px)
    - Changed: Topbar customer picker height/alignment for consistent vertical center
    - Changed: Edit (table) button higher contrast hover (blue background)
    - Fixed: Footer width now matches main content (1280px)
    - Fixed: Profile Change password / Delete account Cancel returns to Account Information tab
    - Fixed: Form button vertical alignment across admin forms

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.34
  - Summary:
    - Simplified admin layout CSS and removed conflicting width overrides
    - Standardized admin container flex layout to keep footer at bottom
    - Removed admin nav sidebar toggle and forced sidebar visible
    - Added deeper backend logging (view info, templates, db time, slow queries)
    - Added frontend fetch/XHR logging for portal and admin
    - Expanded debug page with view/template columns and system/Django info

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.33
  - Summary:
    - Removed injected dashboard JS/CSS overrides and relied on shared layout
    - Standardized admin layout containers to flex structure matching portal
    - Unified footer styling and positioning without DOM moves or calc hacks
    - Removed admin nav sidebar toggle and forced sidebar visible

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.27
  - Summary:
    - Completely rebuilt admin dashboard page (index.html) to fix persistent width issue
    - Removed breadcrumbs block to prevent duplicate "Administration" title
    - Added dashboard class to body for targeted CSS styling
    - Enhanced JavaScript to hide breadcrumbs and duplicate h1 titles
    - Added CSS rules to hide breadcrumbs and duplicate titles on dashboard page
    - Dashboard now uses full browser width with centered content-wrapper (max-width: 980px)
    - Fixed duplicate title issue - only one "Administration" heading now displays

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.21
  - Summary:
    - Removed "Change Password" link from avatar dropdown menu (available in profile settings)
    - Password change now opens as a modal popup instead of navigating to a new page
    - Updated profile_view to handle password change form submission
    - Improved user experience with modal-based password change workflow
    - Form submission handled via POST to same profile page

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.20
  - Summary:
    - Added auto-dismiss functionality to toast notifications (5 seconds)
    - Toast notifications now fade out smoothly before removal
    - Avatar dropdown now displays full name (first_name + last_name) instead of username
    - Falls back to username if full name is not set
    - Password change page buttons now match in height (40px)
    - Buttons aligned to the right side of the form
    - Created form-btn and form-btn-primary/secondary CSS classes for consistent button styling
    - Improved user experience with better visual feedback

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.19
  - Summary:
    - Ensured footer is identical on portal and admin pages
    - Fixed avatar dropdown vertical alignment issue
    - Fixed Recent Actions modal button functionality on admin page
    - Added password change and profile settings pages
    - Added Profile Settings and Change Password links to avatar dropdown
    - Improved avatar dropdown close behavior (properly closes on outside click)
    - Enhanced active page highlight with better contrast (blue background, border, shadow)
    - Created profile.html and password_change.html templates
    - Added CustomPasswordChangeForm for styled password change
    - Improved JavaScript event handling for modals and dropdowns

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.18
  - Summary:
    - Fixed footer to always stay at bottom of screen using flexbox sticky footer layout
    - Unified admin and portal UI: admin pages now use same topbar as portal
    - Hidden customer dropdown in admin pages (only visible in portal)
    - Fixed Recent Actions modal button functionality
    - Added toast notifications to portal pages (previously only in admin)
    - Moved toast notifications to bottom right corner
    - Added active page highlighting in topbar menu (Portal/Admin buttons)
    - Created admin base.html template with portal-style topbar
    - Added footer to admin pages matching portal footer
    - Improved CSS for consistent experience across admin and portal

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.17
  - Summary:
    - Fixed 500 error when accessing admin panel
    - Added missing {% load i18n %} tag in admin index.html template
    - Template was using {% blocktrans %} and {% trans %} without loading i18n library
    - Fixed topbar layout: improved flexbox to ensure menu buttons stay on same line as brand
    - Enhanced topbar CSS with flex-shrink and proper spacing
    - Improved user avatar dropdown menu styling

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.16
  - Summary:
    - Redesigned portal topbar layout for better UX
    - Moved menu buttons (Portal, Admin) to left side next to brand name
    - Created user avatar component with dropdown menu
    - Avatar dropdown includes user info, admin panel link (if superuser), and logout
    - Customer dropdown positioned in middle-right of topbar
    - Removed "Your customers" section from portal page (redundant with header dropdown)
    - Improved topbar visual hierarchy and spacing
    - Added smooth animations for avatar dropdown menu
    - Fixed Admin button functionality in topbar

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.15
  - Summary:
    - Fixed Recent Actions sidebar removal (properly overrode sidebar block in index.html)
    - Added customer dropdown selector in admin header for filtering by customer
    - Added customer dropdown selector in portal header for switching between customers
    - Implemented customer switching functionality with session-based storage
    - Created user_customers context processor for template access to customer memberships
    - Updated portal_home view to use session-stored active customer
    - Added switch_customer view with POST handling and session management
    - Styled customer switcher dropdowns in both admin and portal interfaces
    - Created IMPROVEMENTS.md with comprehensive list of improvement ideas and future features
    - Improved user experience for multi-customer users

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.15
  - Summary:
    - Deep dive admin UI/UX redesign: modernized tables, layout, and icons
    - Removed Recent Actions section from admin dashboard
    - Added Recent Actions modal accessible via clock icon in admin header
    - Implemented modern minimalist SVG icons throughout admin (Lucide-inspired)
    - Redesigned tables with zebra striping, improved spacing, and visual hierarchy
    - Enhanced table styling with better borders, shadows, and hover effects
    - Added icon buttons for view, edit, and delete actions in tables
    - Improved modal design with backdrop blur and modern card styling
    - Better icon integration with consistent sizing and spacing

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.14
  - Summary:
    - Complete admin UI/UX redesign with modern minimalist approach
    - Improved navigation, buttons, spacing, and visual hierarchy
    - Better contrast and readability (proper text colors on all backgrounds)
    - Moved changelog button to footer under copyright information
    - Inspired by Django Unfold and modern admin best practices

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.13
  - Summary:
    - Fixed CustomerMembership save error (proper form instance handling)
    - Redesigned admin interface to match Interheart style exactly
    - Compact fonts (12px, 13px, 14px) matching Interheart
    - Clean, subtle design with proper rgba colors
    - Better spacing and visual hierarchy

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.12
  - Summary:
    - Fixed 500 error when saving CustomerMembership (added save_m2m method)
    - Complete redesign of admin interface with modern, clean dark theme
    - Improved spacing, shadows, and visual hierarchy
    - Better button styles with hover effects
    - Enhanced table and form styling

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.11
  - Summary:
    - Completely redesigned admin CSS for better text contrast and visibility
    - Matched admin design to portal color palette exactly
    - Fixed all text color issues (text now visible on all backgrounds)
    - Improved form elements, buttons, tables, and all admin components

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.10
  - Summary:
    - Fixed 500 error in CustomerMembership changelist (removed bulk_add URL reference)
    - Modernized Django admin interface with dark theme CSS
    - Created custom admin base template for styling
    - Admin now matches portal design aesthetic

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.9
  - Summary:
    - Fixed 500 error when adding CustomerMembership (form fields configuration)
    - Fixed form to properly handle add vs edit modes with dynamic fields

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.8
  - Summary:
    - Merged bulk add into regular CustomerMembership add form with multi-select
    - Added customer admin permissions to manage memberships for their customer
    - Updated registration text to reflect PMG and Customer admin access assignment
    - Removed separate bulk add page and templates

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.7
  - Summary:
    - Improved UI/UX: better topbar button styling, admin visibility controls
    - Added bulk add CustomerMemberships feature
    - Simplified footer design
    - Made 5echo.io clickable link
    - Enhanced README.md with detailed installation/update instructions
    - Enhanced README.md with detailed installation/update instructions

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.6
  - Summary:
    - Created initial migrations for portal models (fixes missing database tables)
    - Fixed admin 500 errors with improved error handling
    - Improved changelog modal to show version-specific sections
    - Removed changelog preview text from footer, only button remains
    - Added dark mode scrollbar styling
    - Added logging configuration for better debugging
    - Improved topbar design with better button styling
    - Admin button only visible to superusers
    - Removed Admin link from login page
    - Added bulk add CustomerMemberships feature
    - Made 5echo.io clickable in footer
    - Simplified footer (removed Quick Links)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.5
  - Summary:
    - Fixed installer interactive mode detection (auto-defaults to update when piped)
    - Improved non-interactive installation experience
    - Added footer with copyright, version, and changelog preview
    - Added changelog modal dialog for viewing full changelog
    - Fixed 500 error when saving Customer in admin (context processor now skips admin pages)
    - Improved admin queryset handling to avoid errors during save operations
    - Fixed context processor file reading errors causing admin save failures
    - Improved portal_home view error handling and query optimization
    - Comprehensive fix for admin 500 errors: improved get_queryset URL detection, added try/except blocks
    - Added logging configuration for better debugging

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.4
  - Summary:
    - Added standalone installer (install.sh) for curl-based installation
    - Installer detects existing installation and offers update/uninstall
    - Update mode preserves database and .env configuration
    - Fixed interactive prompts in non-interactive mode (defaults to update)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.4
  - Summary:
    - Changed default APP_BIND to 0.0.0.0:8097 for reverse proxy compatibility
    - Fixed static files not loading: added WhiteNoise middleware for production
    - Updated templates to use Django static tag
    - Fixed 500 errors after login and "View site" button
    - Whitelabeled admin site (PMG Portal branding)
    - Improved admin interface with descriptions and counts
    - Added setup guide documentation
    - Fixed 500 error when adding Customer (member_count/link_count methods)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.3
  - Summary:
    - Set default bind port to 8097
    - Fixed local Postgres bootstrap in install wizard

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.2
  - Summary:
    - Added interactive install wizard with .env prompts
    - Bootstrapped local Postgres during install when applicable
    - Updated default admin credentials to admin/admin and superuser check

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.26
  - Summary:
    - FIXED: Removed MutationObserver that was causing infinite loop
    - JavaScript now removes .colMS class directly (root cause of width: 464px)
    - Adds .colMS-override class instead to maintain styling without width constraint
    - Changed cssText to use assignment (=) instead of append (+=) to avoid conflicts
    - Added CSS support for .colMS-override class
    - This should finally fix the width issue by removing the problematic class entirely

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.25
  - Summary:
    - Changed JavaScript to use cssText instead of setProperty for more aggressive style overrides
    - cssText allows appending !important styles directly without property conflicts
    - Added MutationObserver to watch for style changes and automatically re-apply fixes
    - MutationObserver detects when Django admin CSS sets width back to 464px and fixes it immediately
    - Added setTimeout delay up to 1000ms to catch very late-loading CSS
    - This should finally override Django admin's persistent width: 464px constraint

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.24
  - Summary:
    - FIXED: Django admin sets width: 464px on #content.colMS - added min-width: 100% override
    - Enhanced JavaScript to remove and re-set width property to force override Django admin's fixed width
    - Added min-width: 100% to all #content selectors for dashboard pages
    - This should fix the issue where #content had computed width: 464px instead of 100%

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.23
  - Summary:
    - Added dashboard-grid width fixes in JavaScript
    - Added console.log debugging to show computed styles for troubleshooting
    - JavaScript now logs computed width and max-width for #content and .content-wrapper
    - This helps identify what's actually constraining the width in the browser

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.22
  - Summary:
    - Enhanced JavaScript to fix ALL parent containers: #content, .main, #main, #container
    - Removes float constraints from .colMS class dynamically
    - Added window.load event listener for final fix after all resources load
    - Multiple setTimeout delays (50ms, 100ms, 300ms, 500ms) to catch all CSS loading scenarios
    - Simplified CSS overrides - removed redundant selectors, kept only essential ones
    - Added .main and #main width overrides for dashboard pages

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.21
  - Summary:
    - Added JavaScript fallback to dynamically fix #content width constraints
    - JavaScript uses setProperty with 'important' flag to override CSS
    - Sets #content max-width: 100% and width: 100% when content-wrapper is present
    - Ensures content-wrapper has max-width: 980px and centered margins
    - Runs immediately, on DOMContentLoaded, and after 100ms/500ms delays to catch all CSS loading scenarios

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.20
  - Summary:
    - Fixed #content max-width constraint issue by adding :has(.content-wrapper) selector
    - Added specific override for #content.colMS:has(.content-wrapper) to remove max-width: 1200px constraint
    - Ensured #content itself doesn't constrain .content-wrapper by setting max-width: 100% when content-wrapper is present
    - Added multiple selectors to catch all cases: body.admin-page.dashboard #content, body.admin-page #content:has(.content-wrapper)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.19
  - Summary:
    - Completely redesigned admin dashboard to match portal page structure
    - Replaced table-based dashboard with panel-based layout using .content-wrapper, .dashboard-grid, .panel, .list, .list-item
    - Dashboard now uses max-width: 980px centered layout like portal page (not full width)
    - Removed all complex CSS overrides, JavaScript workarounds, and calc() margins
    - Dashboard uses same visual design as portal page with panels and lists
    - Grid layout: 3 columns (desktop), 2 columns (tablet), 1 column (mobile)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.18
  - Summary:
    - Added JavaScript to admin/index.html template to dynamically remove width constraints
    - JavaScript targets #content, #container, #main, and .dashboard elements
    - Sets inline styles with maxWidth: 100%, width: 100%, marginLeft/Right: 0
    - Runs immediately, on DOMContentLoaded, and after 100ms delay to ensure all CSS has loaded
    - This ensures dashboard uses full browser width even if CSS overrides fail

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.17
  - Summary:
    - Added more aggressive CSS overrides targeting #content.colMS specifically to override Django admin's float layout
    - Added body.admin-page.dashboard class targeting (Django adds .dashboard class to body on dashboard page)
    - Increased CSS specificity with multiple selectors: body.admin-page.dashboard #content, body.admin-page #content.colMS:has(.dashboard)
    - Override .colMS float layout specifically for dashboard pages to ensure full width
    - Dashboard now should use full browser width even when Django admin CSS loads first

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.16
  - Summary:
    - Removed problematic inline wrapper div from admin/index.html that was causing dashboard to disappear
    - Reverted to simpler CSS-only solution using :has() selector to detect dashboard and remove #content max-width constraint
    - Dashboard now properly displays using CSS :has() selector to make #content full width when it contains .dashboard
    - Simplified CSS rules - removed calc() margin workarounds that were causing layout issues

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.15
  - Summary:
    - Added inline wrapper div in admin/index.html template with calc() margins to force dashboard to break out of #content container
    - Updated CSS to support new dashboard wrapper structure
    - Fixed footer positioning to use 100vw width with calc() margins (calc(-50vw + 50%)) to ensure full browser width
    - Increased Export button min-width from 120px to 140px and added white-space: nowrap to prevent text wrapping
    - Footer now properly spans full viewport width even when inside #container

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.14
  - Summary:
    - Fixed clipboard function error handling - added event parameter and fallback for older browsers using document.execCommand
    - Fixed button size inconsistency - both Export and Copy buttons now have same height and styling
    - Completely redesigned admin dashboard CSS to remove ALL width constraints
    - Dashboard now uses :has() selector to detect when #content contains dashboard and removes max-width constraint
    - Removed conflicting CSS rules and simplified dashboard width handling
    - Dashboard now properly uses 100% width without any calc() workarounds

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.13
  - Summary:
    - Fixed admin dashboard width by using calc() CSS to break dashboard out of #content's max-width: 1200px constraint
    - Dashboard now uses full viewport width (calc(100vw - 64px)) with proper margins to break out of parent container
    - Added :has() selector fallback for modern browsers, with calc() fallback for older browsers
    - Added "Copy to Clipboard" button to debug view that copies JSON debug data to clipboard
    - Copy button shows visual feedback ("Copied!") when successful

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.12
  - Summary:
    - Fixed admin dashboard width issue by adding more specific CSS selectors (body.admin-page #content .dashboard, etc.)
    - Removed padding and margin constraints from dashboard CSS
    - Created DebugLoggingMiddleware to track all HTTP requests/responses, processing times, database queries, and exceptions
    - Added frontend JavaScript logging to track button clicks, form submissions, page loads, JavaScript errors, and promise rejections
    - Enhanced debug view template to display request logs table, database queries, and frontend logs viewer
    - Added database query logging configuration in settings.py (when DEBUG=True)
    - Frontend logs accessible via window.getPmgDebugLogs() in browser console

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.11
  - Summary:
    - Added Debug link to avatar menu dropdown for superusers
    - Debug link appears after Admin Panel link in both portal and admin base templates
    - Uses info icon (circle with exclamation mark) for visual consistency

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.10
  - Summary:
    - Added viewport width (100vw) CSS overrides for #container to force full browser width
    - Enhanced topbar CSS to ensure it spans full width with explicit margin overrides
    - Added more specific selectors targeting body.admin-page > * and all div wrappers
    - Improved CSS specificity to override Django admin's default width constraints

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.9
  - Summary:
    - Fixed footer_info context processor to work for admin pages (removed admin path skip check)
    - Added more aggressive CSS overrides for admin page width (targeting body > div wrappers)
    - Enhanced footer CSS to handle footer inside or outside #container with viewport width tricks
    - Created debug view at /debug/ for superusers to view system info, database info, file paths, and errors
    - Added debug template with JSON export functionality

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.8
  - Summary:
    - Fixed admin page width issue by setting #container max-width to none (was 100%)
    - Footer now properly spans full width on admin pages with consistent styling
    - Added explicit footer width and margin overrides to ensure it's not constrained
    - Footer positioned at bottom using flexbox layout (margin-top: auto)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.7
  - Summary:
    - Changed admin dashboard from 2 columns to 3 columns layout
    - Added max-width: 1200px to #content with margin: 0 auto for centered layout with safe zones (similar to portal page)
    - Updated responsive breakpoints: 2 columns at 1400px, 1 column at 900px
    - Admin page now has proper width constraints instead of full browser width for better readability

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.6
  - Summary:
    - Fixed Recent Actions button by removing conflicting onclick attribute and improving event listener
    - Fixed customer switcher to redirect to portal when switching from profile settings page
    - Added even more aggressive CSS overrides for admin page width (targeting all divs with class/id containing "col", "content", "container")
    - Added float: none to #content to prevent any float-based layout constraints
    - Improved event listener attachment for Recent Actions button with DOMContentLoaded fallback

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.5
  - Summary:
    - Comprehensive fix for admin page width issue
    - Added CSS overrides for html, body.admin-page, #container, #content, .colMS, .colSM, .main, and all child elements
    - Ensured all admin page elements use 100% width with !important flags to override Django's default admin CSS
    - Added box-sizing: border-box to all admin content elements
    - Targeted both body.admin-page and general selectors to catch all possible width constraints

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.4
  - Summary:
    - Fixed admin dashboard width issue by removing max-width constraint on #container element
    - Changed Add button background from blue to green (success color) for better visual distinction
    - Updated both dashboard and object-tools Add buttons to use green background
    - Ensured #content uses full width with proper box-sizing

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.3
  - Summary:
    - Fixed admin dashboard width issue (removed max-width constraint, now uses full page width)
    - Made Add buttons smaller (28px height, 13px font size, reduced padding)
    - Styled Change buttons as box buttons with edit icon in dashboard
    - Improved button icon contrast (white icons on colored backgrounds)
    - Updated object-tools Add button to match smaller size

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.2
  - Summary:
    - Increased topbar padding (20px top/bottom, 32px left/right) for better spacing around menu
    - Admin dashboard modules now display in 2-column grid layout instead of stacked vertically
    - Admin dashboard box titles (captions) styled with blue background for better contrast
    - Added responsive breakpoint for dashboard (switches to single column on smaller screens)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.2.0-alpha.1
  - Summary:
    - Version bump: 0.1.0-alpha.23 → 0.2.0-alpha.1 (MINOR version increment for new features)
    - Note: CHANGELOG accumulates all changes under [Unreleased] until MAJOR release
    - Major features added: Profile settings redesign, Delete account functionality, Logout confirmation modal
    - Added logout confirmation modal in profile settings sidebar (prevents accidental logout)
    - Delete account modal now resets to Account Information section when closed/cancelled
    - Fixed Recent Actions button vertical alignment in admin topbar (changed to flex with fixed height)
    - Fixed Recent Actions button click functionality (added onclick fallback attribute)
    - Updated admin-icon-btn CSS to use flex instead of inline-flex for better alignment

- 2026-02-05 (Europe/Oslo)
  - Branch: dev
  - Version: 0.1.0-alpha.22
  - Summary:
    - Fixed avatar icon vertical alignment in topbar
    - Increased spacing between website title and menu buttons (gap: 32px)
    - Redesigned profile settings page with left sidebar navigation menu
    - Added sidebar menu items: Account Information, Change Password, Delete Account, Logout
    - Implemented delete account functionality with danger zone modal
    - Delete account requires username confirmation and permanently deletes user
    - Added danger zone styling with warning icons and red color scheme
    - Updated profile_view to handle delete account POST requests

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.1
  - Summary:
    - Created initial Django + Postgres portal foundation
    - Added install/update/reinstall/uninstall scripts
    - Added systemd + optional nginx config
