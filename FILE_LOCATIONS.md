<!--
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: File location index for templates and key project files. Update this file when moving or renaming files.
Path: FILE_LOCATIONS.md
Created: 2026-02-06
Last Modified: 2026-02-06
-->

# File locations

This file is the single reference for where important project files are located. When moving or renaming files, update this file so upgrades and downgrades follow the correct structure.

---

## Admin app (admin_app)

### Python
| File | Path |
|------|------|
| Views | `src/admin_app/views.py` |
| URLs | `src/admin_app/urls.py` |
| Forms | `src/admin_app/forms.py` |
| Templatetags | `src/admin_app/templatetags/admin_extras.py` |
| Backup logic | `src/admin_app/backup_restore.py` |

### Templates – base
| File | Path |
|------|------|
| Base (all admin pages extend) | `src/admin_app/templates/admin_app/base.html` |
| Admin home | `src/admin_app/templates/admin_app/home.html` |

### Templates – device/ (devices, categories, manufacturers, product datasheets)
| File | Path |
|------|------|
| Device landing | `src/admin_app/templates/admin_app/device/device_landing.html` |
| Device list | `src/admin_app/templates/admin_app/device/device_type_list.html` |
| Device detail (product) | `src/admin_app/templates/admin_app/device/device_type_detail.html` |
| Device form (add/edit) | `src/admin_app/templates/admin_app/device/device_type_form.html` |
| Choose facility for instance | `src/admin_app/templates/admin_app/device/device_instance_add_choose_facility.html` |
| Instance form | `src/admin_app/templates/admin_app/device/device_instance_form.html` |
| Instance form (fragment) | `src/admin_app/templates/admin_app/device/device_instance_form_fragment.html` |
| Category list | `src/admin_app/templates/admin_app/device/device_category_list.html` |
| Category form | `src/admin_app/templates/admin_app/device/device_category_form.html` |
| Manufacturer list | `src/admin_app/templates/admin_app/device/manufacturer_list.html` |
| Manufacturer form | `src/admin_app/templates/admin_app/device/manufacturer_form.html` |
| Product datasheet list | `src/admin_app/templates/admin_app/device/product_datasheet_list.html` |
| Product datasheet form | `src/admin_app/templates/admin_app/device/product_datasheet_form.html` |
| Network device list | `src/admin_app/templates/admin_app/device/network_device_list.html` |
| Choose device (add) | `src/admin_app/templates/admin_app/device/network_device_add_choose.html` |
| Network device form | `src/admin_app/templates/admin_app/device/network_device_form.html` |
| Network device form (fragment) | `src/admin_app/templates/admin_app/device/network_device_form_fragment.html` |

### Templates – facility/ (facilities, racks, IP, documents)
| File | Path |
|------|------|
| Facility list | `src/admin_app/templates/admin_app/facility/facility_list.html` |
| Facility form | `src/admin_app/templates/admin_app/facility/facility_form.html` |
| Facility card (detail) | `src/admin_app/templates/admin_app/facility/facility_card.html` |
| Facility customers edit | `src/admin_app/templates/admin_app/facility/facility_customers_edit.html` |
| Facility customers edit (fragment) | `src/admin_app/templates/admin_app/facility/facility_customers_edit_fragment.html` |
| Facility customer add | `src/admin_app/templates/admin_app/facility/facility_customer_add.html` |
| Choose device type (fragment) | `src/admin_app/templates/admin_app/facility/facility_device_choose_type_fragment.html` |
| Document form | `src/admin_app/templates/admin_app/facility/facility_document_form.html` |
| Document form (fragment) | `src/admin_app/templates/admin_app/facility/facility_document_form_fragment.html` |
| Contact form | `src/admin_app/templates/admin_app/facility/facility_contact_form.html` |
| Contact form (fragment) | `src/admin_app/templates/admin_app/facility/facility_contact_form_fragment.html` |
| Rack detail | `src/admin_app/templates/admin_app/facility/rack_detail.html` |
| Rack form | `src/admin_app/templates/admin_app/facility/rack_form.html` |
| Rack form (fragment) | `src/admin_app/templates/admin_app/facility/rack_form_fragment.html` |
| Rack seal form | `src/admin_app/templates/admin_app/facility/rack_seal_form.html` |
| Rack seal remove | `src/admin_app/templates/admin_app/facility/rack_seal_remove_form.html` |
| IP address form | `src/admin_app/templates/admin_app/facility/ip_address_form.html` |
| IP address form (fragment) | `src/admin_app/templates/admin_app/facility/ip_address_form_fragment.html` |
| IP delete button (partial) | `src/admin_app/templates/admin_app/facility/_ip_address_delete_btn.html` |

### Templates – customer/
| File | Path |
|------|------|
| Customer list | `src/admin_app/templates/admin_app/customer/customer_list.html` |
| Customer form | `src/admin_app/templates/admin_app/customer/customer_form.html` |
| Customer card (detail) | `src/admin_app/templates/admin_app/customer/customer_card.html` |
| Customer access list | `src/admin_app/templates/admin_app/customer/customer_access_list.html` |
| Customer access form | `src/admin_app/templates/admin_app/customer/customer_access_form.html` |

### Templates – user/
| File | Path |
|------|------|
| User list | `src/admin_app/templates/admin_app/user/user_list.html` |
| User form | `src/admin_app/templates/admin_app/user/user_form.html` |
| User card (detail) | `src/admin_app/templates/admin_app/user/user_card.html` |
| Role list | `src/admin_app/templates/admin_app/user/role_list.html` |
| Role form | `src/admin_app/templates/admin_app/user/role_form.html` |

### Templates – portal/ (portal management in admin)
| File | Path |
|------|------|
| Portal links list | `src/admin_app/templates/admin_app/portal/portal_link_list.html` |
| Portal link form | `src/admin_app/templates/admin_app/portal/portal_link_form.html` |
| Announcements list | `src/admin_app/templates/admin_app/portal/announcement_list.html` |
| Announcement form | `src/admin_app/templates/admin_app/portal/announcement_form.html` |

### Templates – notifications/
| File | Path |
|------|------|
| Notification list | `src/admin_app/templates/admin_app/notifications/admin_notification_list.html` |

### Templates – backup/
| File | Path |
|------|------|
| Backup and restore | `src/admin_app/templates/admin_app/backup/backup_restore.html` |

---

## Portal (customer portal)

### Python
| File | Path |
|------|------|
| Views | `src/portal/views.py` |
| URLs | `src/portal/urls.py` |
| Models | `src/portal/models.py` |
| Forms | `src/portal/forms.py` |
| Admin (Django admin) | `src/portal/admin.py` |

### Templates
| File | Path |
|------|------|
| Base | `src/portal/templates/portal/base.html` |
| Customer selection | `src/portal/templates/portal/customer_selection.html` |
| No customer | `src/portal/templates/portal/no_customer.html` |
| Customer home | `src/portal/templates/portal/customer_home.html` |
| Facility list | `src/portal/templates/portal/facility_list.html` |
| Facility detail | `src/portal/templates/portal/facility_detail.html` |
| Fragment: customer home | `src/portal/templates/portal/fragments/customer_home_content.html` |
| Fragment: customer selection | `src/portal/templates/portal/fragments/customer_selection_content.html` |
| Fragment: no customer | `src/portal/templates/portal/fragments/no_customer_content.html` |
| Fragment: facility list | `src/portal/templates/portal/fragments/facility_list_content.html` |
| Fragment: facility detail | `src/portal/templates/portal/fragments/facility_detail_content.html` |

### Django admin (portal) overrides
| File | Path |
|------|------|
| CustomerMembership change_list | `src/portal/templates/admin/portal/customermembership/change_list.html` |

---

## Project (pmg_portal)

### Python and configuration
| File | Path |
|------|------|
| Main URLs | `src/pmg_portal/urls.py` |
| Settings | `src/pmg_portal/settings.py` |
| Django admin base_site | `src/pmg_portal/admin_config.py` |
| ASGI | `src/pmg_portal/asgi.py` |
| WSGI | `src/pmg_portal/wsgi.py` |
| Versioning | `src/pmg_portal/versioning.py` |
| Version middleware | `src/pmg_portal/version_middleware.py` |
| Logging middleware | `src/pmg_portal/logging_middleware.py` |

### Templates (global)
| File | Path |
|------|------|
| Django admin base | `src/pmg_portal/templates/admin/base.html` |
| Django admin base_site | `src/pmg_portal/templates/admin/base_site.html` |
| Django admin index | `src/pmg_portal/templates/admin/index.html` |
| Site footer | `src/pmg_portal/templates/includes/site_footer.html` |

---

## Static files

| File | Path |
|------|------|
| Main CSS (portal + admin) | `src/static/app.css` |
| Theme – dark mode (all color variables) | `src/static/css/theme-dark.css` |
| Theme – light mode (all color variables) | `src/static/css/theme-light.css` |
| Admin custom CSS | `src/static/admin_custom.css` |
| Theme documentation (variables and usage) | `docs/THEME_COLORS.md` |

---

## Translations (i18n)

| File | Path |
|------|------|
| Norwegian (Bokmål) | `src/locale/nb/LC_MESSAGES/django.po` |
| Compiled (.mo) | `src/locale/nb/LC_MESSAGES/django.mo` (generated by compilemessages) |

---

## Other apps

| Area | Path (representative) |
|------|----------------------|
| accounts (login, profile) | `src/accounts/` – views.py, urls.py, templates/accounts/ |
| web (debug etc.) | `src/web/` – views.py, urls.py, templates/web/ |

---

## Scripts and deploy

| File | Path |
|------|------|
| Update script | `scripts/update.sh` |
| Install script | `scripts/install.sh` |
| Run manage.py with .env loaded | `scripts/run_manage.sh` |
| Version file | `VERSION` |
| Release notes (popup text for final releases) | `RELEASE_NOTES.json` |

`RELEASE_NOTES.json` is used for the "New update" popup shown on first visit after a final release (no -beta/-alpha/-rc). Add an entry per version, e.g. `"4.8.0": { "nb": "...", "en": "..." }`, with short, readable text about the most important new features and fixes.

---

*Update this file whenever you change template structure or move files.*
