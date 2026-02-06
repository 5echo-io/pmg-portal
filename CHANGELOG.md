# Changelog

All notable changes to this project will be documented in this file.
This project follows Semantic Versioning (SemVer).

## [Unreleased]

Pre-release builds (alpha, beta, rc) are listed here. Only full releases (no build suffix) get a dedicated version section below.

### Fixed
- **compilemessages**: Removed duplicate msgid entries in locale nb django.po so msgfmt succeeds on update; update.sh shows clearer error when compilemessages fails.

### Changed
- **Backup & Restore**: UI and logic improvements; admin base layout and footer tweaks
- **Facility card & Rack detail**: Layout and template refinements; portal facility list and base template updates
- **Styling**: app.css and site_footer adjustments
- **Rack detail**: Template refactor and layout updates; IP address form, site footer, portal base and app.css tweaks
- **IP address form & views**: Small template and view tweaks
- **Admin views**: View logic updates and refinements; small view tweak
- **IP address form**: Delete button extracted to partial _ip_address_delete_btn.html

### Added
- **Admin – Network device list**: Dedicated network device list page (template + view + URL); admin home link

#### Facility Management (Anlegg)
- **Facility Model**: New Facility model with comprehensive fields (name, slug, description, address, city, postal code, country, contact information)
- **Customer-Facility Relationship**: Many-to-many relationship allowing customers to have access to multiple facilities
- **Admin Panel - Facilities**:
  - Facility list page with search and filtering (active/inactive)
  - Facility add/edit form with customer assignment
  - Facility detail card page with tabs for customers, racks, network devices, IP addresses, documents, and information
  - Facility delete functionality with confirmation modal
  - Added to Portal management section in admin home
- **Portal - Facilities**:
  - Facility list page showing all facilities the active customer has access to
  - Facility detail page with comprehensive information
  - Overview tab with statistics (racks, network devices, IP addresses, documents)
  - Tabs for Racks, Network Devices, IP Addresses, Documents, and Information
  - Facility button in topbar (active when customer profile is selected)
- **Related Models**:
  - `FacilityDocument`: Document uploads for facilities (manuals, diagrams, certificates, reports)
  - `Rack`: Rack management within facilities (name, location, height in U, serial number)
  - `NetworkDevice`: Network equipment tracking (switches, routers, firewalls, servers, etc.)
  - `IPAddress`: IP address reservation and tracking
  - `RackSeal`: Security seal tracking for racks with installation/removal history
- **Context Processor**: Updated to include `user_facilities` based on active customer
- **Rack Management**:
  - Rack CRUD operations in admin panel (add, edit, delete, detail view)
  - Rack detail page with interactive U-position visualization
  - Rack serial number field for asset tracking
  - Rack seal management: install and remove security seals with tracking
  - Seal removal tracking with reason and notes
  - Active seal validation to prevent duplicate seal IDs
  - Rack name uniqueness validation within facility
- **Network Device Management**:
  - Network device CRUD operations in admin panel (add, edit)
  - NetworkDeviceForm with facility and rack filtering
  - Add device directly from rack detail view with pre-selected rack and position
  - Add device at specific U-position from rack visualization
  - Remove device from rack (clears rack assignment while keeping device in facility)
  - Edit device with automatic redirect back to rack if assigned
  - Device links in facility and rack views showing rack name and U-position
- **Facility Customer Access**: Add or remove customers from a facility's access list; batch edit via "Manage access" (facility_customers_edit with checkboxes) or remove per customer
- **IP Address Management**: CRUD for IP addresses within a facility (add, edit, delete) with optional device assignment
- **Facility Document Management**: Upload and delete documents for facilities (title, description, file, category)
- **Backup & Restore**: Full backup (PostgreSQL + media) and restore from single .tar.gz; superuser-only; linked from admin home under "Server management"

### Changed
- **Removed Dev Feature Protection**: Removed `ENABLE_DEV_FEATURES` and `DEV_ACCESS_USERS` feature flags - Facility features are now directly available
- **Simplified Access Control**: Facility views use standard `@staff_required` decorator (admin) and `@login_required` (portal) instead of `@dev_required`
- **Context Processor**: Simplified to directly return `user_facilities` without dev feature checks
- **Templates**: Removed conditional dev feature checks - Facility button shows when customer profile is selected
- **Install Script**: Updated rsync to use `--delete` flag to ensure all template files are properly synced
- **Facility Templates**: Facility templates are now production-ready and kept in main branch (no longer removed during main branch cleanup)
- **HTMX Navigation**: Added HTMX support to Facility list and detail views for seamless navigation without full page reloads
- **URL Structure**: Changed Facility URLs from primary key (`pk`) to slug-based (`slug`) for better SEO and user-friendly URLs (BREAKING CHANGE)
- **Facility Detail UI**: Added breadcrumb navigation and back button for better user experience
- **Network Tab**: Combined Network Devices and IP Addresses into a single Network tab with combined statistics
- **Breadcrumb Styling**: Unified breadcrumb styling to use admin-breadcrumb class for consistent design across admin and portal
- **Customer Switch**: Customer switch now redirects back to referring page instead of always redirecting to portal home
- **Card Header Redesign**: Edit and Delete actions moved to card header as icon buttons for better space utilization and cleaner layout
- **Admin Content Width**: Increased admin content width from 980px to 1280px for consistency with portal layout
- **Tab Styling**: Improved tab styling with hover states, active state highlighting, and better spacing
- **Breadcrumb Navigation**: Added contextual back button (←) on all admin pages for quicker navigation to list or parent
- **Card Title Block**: Customer and facility cards show slug below name; facility card shows country flag, active/inactive badge, and created/updated dates in header
- **Information Tab Removed**: Customer and facility card information moved to header/summary; Information tab removed
- **Smart Cancel**: Form Cancel buttons use context-based cancel_url (e.g. back to rack or facility)
- **Country Flag Filter**: New admin_extras template tag `country_flag` for facility country display
- **List and Table Styling**: Unified Add button styling and admin-table-actions column class
- **Admin Toolbar Layout**: Search and filter use label-above-control layout (admin-search-group, admin-filter-group); Search button aligned at end
- **Rack Detail Header**: Rack detail page uses card-style header matching facility/customer cards (icon, title block, badge, Edit/Add Seal, meta)
- **Breadcrumb Back Button**: Styled as pill button with border and hover state
- **Table Action Buttons**: View/non-danger buttons use minimal outline style; danger button uses red tint and clear hover
- **Rack Detail Layout**: Two-column layout with left sidebar (visualization, info card, side menu) and right main content; Edit Rack opens in modal (iframe) with close/refresh on save
- **Rack Edit Modal**: rack_edit view supports ?modal=1 and redirects with ?modal_close=1 for parent to close modal and refresh
- **Danger Button Hover**: Softer hover styles (rgba) for form-btn-danger, admin-btn-danger, and admin-btn-sm.admin-btn-danger
- **Rack Detail Width**: Container constrained to max-width 1280px (aligned with dashboard)
- **Facility Edit and Customer Access Modals**: Edit facility and "Manage access" open in iframe modals; postMessage to close and refresh on save
- **Facility Card**: Delete rack button in Racks tab; Remove customer button per row; Norwegian (i18n) for tab and table labels
- **Rack Detail**: Grid layout with Front/Rear view tabs; device cells and empty units open device add/edit modal (openDeviceModal)
- **Modal Support**: facility_edit, facility_customers_edit, network_device_add, network_device_edit support ?modal=1 and redirect with ?modal_close=1 for parent close/refresh
- **IP Address and Document Forms**: Templates and URLs for ip_address add/edit/delete and facility_document upload; facility_customer_add template and URL restored for optional add-one flow
- **Shared Footer**: New site_footer.html include with version, About, Changelog, and language dropdown; used across portal and admin
- **Install Scripts**: Comment that postgresql-client provides pg_dump/psql for Admin Backup & Restore

### Fixed
- **Context Processor**: Added missing Facility model import to fix 500 error when accessing Facility features
- **Template Sync**: Fixed install.sh to ensure Facility template files are properly copied to server
- **Migration Handling**: Improved migration error handling in update.sh with better migration name detection using multiple patterns and fallback to Django showmigrations command
- **Migration Fake Command**: Fixed Django migrate --fake command syntax to use separate app label and migration name arguments instead of combined format
- **Norwegian Translations**: Added comprehensive Norwegian translations for Facility management features (159 new translation strings)

## [3.0.0-alpha.1] - 2026-02-06

### Added

#### Facility Management (Anlegg)
- **Facility Model**: New Facility model with comprehensive fields (name, slug, description, address, city, postal code, country, contact information)
- **Customer-Facility Relationship**: Many-to-many relationship allowing customers to have access to multiple facilities
- **Admin Panel - Facilities**:
  - Facility list page with search and filtering (active/inactive)
  - Facility add/edit form with customer assignment
  - Facility detail card page with tabs for customers, racks, network devices, IP addresses, documents, and information
  - Facility delete functionality with confirmation modal
  - Added to Portal management section in admin home
- **Portal - Facilities**:
  - Facility list page showing all facilities the active customer has access to
  - Facility detail page with comprehensive information
  - Overview tab with statistics (racks, network devices, IP addresses, documents)
  - Tabs for Racks, Network Devices, IP Addresses, Documents, and Information
  - Facility button in topbar (active when customer profile is selected)
- **Related Models**:
  - `FacilityDocument`: Document uploads for facilities (manuals, diagrams, certificates, reports)
  - `Rack`: Rack management within facilities (name, location, height in U)
  - `NetworkDevice`: Network equipment tracking (switches, routers, firewalls, servers, etc.)
  - `IPAddress`: IP address reservation and tracking
- **Context Processor**: Updated to include `user_facilities` based on active customer

### Changed
- **Removed Dev Feature Protection**: Removed `ENABLE_DEV_FEATURES` and `DEV_ACCESS_USERS` feature flags - Facility features are now directly available
- **Simplified Access Control**: Facility views use standard `@staff_required` decorator (admin) and `@login_required` (portal) instead of `@dev_required`
- **Context Processor**: Simplified to directly return `user_facilities` without dev feature checks
- **Templates**: Removed conditional dev feature checks - Facility button shows when customer profile is selected
- **Install Script**: Updated rsync to use `--delete` flag to ensure all template files are properly synced

### Fixed
- **Context Processor**: Added missing Facility model import to fix 500 error when accessing Facility features
- **Template Sync**: Fixed install.sh to ensure Facility template files are properly copied to server

#### UI/UX
- Facility card grid layout with modern design
- Facility detail page with tabbed interface
- Responsive facility list and detail views
- Empty state handling for facilities
- Facility iconography and visual hierarchy

### Technical
- Database migrations prepared for Facility, FacilityDocument, Rack, NetworkDevice, and IPAddress models
- URL routing for facility list and detail pages
- Template fragments for HTMX support
- CSS styling for facility components

## [2.0.0] - 2026-02-06

### Added

#### Admin Panel
- Custom admin app at `/admin/` with User management, Customers & access, Portal management
- Customer card page: Modern detail view with logo upload/delete, member management, and portal links tabs
- User card page: User detail page similar to customer card, showing user information, memberships, and details
- Delete functionality: Ability to delete customers and users with confirmation modal and 3-second countdown
- Admin dashboard: Redesigned with modern minimalist design, panel-based layout
- Recent Actions modal: Accessible via clock icon in admin header
- View button: Added View button to user list for accessing user card page

#### Customer Management
- Customer logo upload: ImageField support with preview, automatic file deletion
- Customer selection flow: Explicit customer profile selection on login (no auto-select for multiple customers)
- Customer selection page: Dedicated page showing all available customer profiles with logos and org numbers
- Customer switch modal: Modal accessible from avatar menu for switching between customer profiles
- Auto-selection: Automatically selects single customer profile when user has access to only one
- Search functionality: Search field on customer selection page when more than 4 customers

#### User Experience
- Profile settings page: Redesigned with left sidebar navigation menu
- Password change modal: Integrated into profile settings
- Delete account functionality: With danger zone confirmation modal
- Logout confirmation modal: In profile settings sidebar
- Language preference synchronization: User's language choice persists across login page and main site
- Animated transitions: Between login and register pages (fade out/in, card height expansion)
- Loading spinner indicator: On Sign in button when form is submitted

#### Internationalization
- Norwegian (Norsk): Full i18n with Django LOCALE_PATHS, locale/nb, and set_language switcher
- Language switcher: In avatar dropdown (Norsk/English with flags; current language hidden from submenu)
- Login page footer: Language dropdown listing all languages
- All portal and account templates translated: Using {% trans %}/{% blocktrans %} with Norwegian translations
- Documentation: docs/I18N.md guide for adding and translating strings

#### Portal Features
- Portal at site root (`/`) with HTMX for no-refresh navigation
- Customer dropdown: In header (avatar-style with search when >4 customers)
- Wider layout: 1280px aligned with topbar and footer
- Service desk button: In topbar (right side, before avatar) - under development
- Projects button: In topbar navigation - under development
- Files button: In topbar navigation - under development

#### UI/UX Components
- Topbar redesign: Menu buttons on left, customer dropdown in middle-right, user avatar on far right
- Avatar dropdown: Shows full name, logout, admin panel access, language switcher
- Toast notifications: Unified across portal and admin, positioned bottom right, auto-dismiss after 5 seconds
- Footer: Full width with copyright, version, and changelog button
- Dark mode scrollbar: Styled to match site design
- Custom tooltip component: For Facility and Service desk buttons (styled to match site design)
- About modal: Accessible from avatar menu (all users); shows app version, 5echo.io info, developer credits
- About modal update check: For admins (compares current version with GitHub main branch); update notification badge in avatar menu

#### Developer Tools
- Debug view: Accessible via avatar menu for superusers at `/debug/`
- Comprehensive logging: Backend request/response tracking, frontend event tracking
- Copy to clipboard: Functionality for debug data export
- File storage debugging: Enhanced logging with file existence checks, directory listings, and permissions verification

#### Documentation
- SETUP_GUIDE.md: Detailed installation and update instructions
- docs/I18N.md: How to add and translate strings (Norsk + English)
- docs/ADMIN_LAYOUT.md: Admin layout documentation
- README.md: Improved with detailed installation and update instructions
- IMPROVEMENTS.md: Comprehensive improvement ideas and future features

### Changed

#### Authentication & User Management
- Login: Field labeled "Email"; accepts email or username; login with email preferred
- Registration: Username hidden and set from email; new users get username = email
- Profile delete account: Confirm with email instead of username
- Migration: `accounts.0001_sync_username_from_email` syncs User.username from User.email for existing users

#### Admin Interface
- Modernized Django admin: Dark theme matching portal design
- Admin list filters: Staff/Active labels, single-row toolbar, outlined Search button
- Admin forms: Card layout, two-column rows (e.g. username|email), aligned Save/Cancel
- Admin tables: Modern styling, zebra striping, improved spacing
- SVG icons: Replaced default Django admin icons with modern minimalist SVG icons
- Customer management: Redirect to modern customer card page instead of edit form after add/edit operations

#### Layout & Styling
- Standardized layout: Consistent structure across all pages (portal and admin)
- Flexbox layout: Footer always at bottom, proper spacing
- Button styling: Smaller (36px height), vertically centered, consistent widths
- Customer dropdown: Reduced vertical spacing, improved positioning
- Footer width: Matches main content (1280px → 980px)
- Customer selection width: Increased from 600px to 800px, then to 1000px for better visibility
- Customer card width: Changed to use full width (100%) instead of fixed 1280px max-width

#### Customer Selection
- Text updates: "Select Customer" → "Select Customer Profile" (Norwegian: "Velg kundeprofil")
- Customer switching: "Switch Customer" → "Switch Customer Profile" (Norwegian: "Bytt kundeprofil")
- UI improvements: Compact list layout instead of grid, smaller logos, better spacing
- Icon updates: Building/company icon for customer switch
- Search placeholder: "Search customer profiles" (Norwegian: "Søk etter kundeprofiler")

#### Delete Functionality
- Delete buttons: Narrower, darker red (#991b1b) for better danger indication
- Delete modal design: Updated to match profile settings modal design with centered positioning and danger zone styling
- Button widths: Standardized View/Edit/Delete buttons (8px 12px padding, auto width)

#### Logo Management
- Logo upload: AJAX-based upload with client-side preview and cache-busting for immediate display
- Logo deletion: Improved cleanup of old logo files when replacing logos or deleting customers
- Logging: Added admin_app logger with INFO level for better debugging of file operations

### Fixed

#### Critical Fixes
- Customer logo upload: Files now properly saved to disk using explicit storage.save() before model assignment
- Media file serving: Django view added to serve media files in production as fallback when nginx is not configured
- Logo deletion: Improved cleanup of old logo files when replacing logos or deleting customers
- File storage: Ensure customer_logos directory exists before saving files
- URL routing: Fixed duplicate import in urls.py
- 500 errors: Fixed multiple admin panel errors (Customer save, CustomerMembership, context processor)
- Database tables: Created initial migrations for portal models
- Static files: Added WhiteNoise middleware for production static file serving

#### UI Fixes
- Customer selection scroll: Fixed scroll behavior - only customer list scrolls, not entire page
- Customer name display: Only shows in topbar when customer profile is actually selected
- Duplicate divider: Removed extra divider line before "Switch Customer Profile" button
- JavaScript syntax errors: Replaced inline onclick handlers with data attributes and event listeners
- Delete modal positioning: Fixed to be centered on screen instead of appearing top-left
- View button width: Made consistent with other action buttons
- Footer positioning: Fixed to always be at bottom of screen
- Avatar alignment: Fixed vertical alignment in topbar
- Form button alignment: Fixed vertical alignment across admin forms
- CSS layout: Improved flexbox layout for customer selection container and main content area to properly constrain scrolling

#### Translation Fixes
- compilemessages error: Fixed "Can't find msgfmt" by installing gettext in install scripts
- Duplicate translations: Removed duplicate entries in django.po file
- Norwegian flag: Corrected to official Norway flag

#### Admin Fixes
- Admin dashboard width: Completely rebuilt to use full browser width
- Duplicate titles: Removed duplicate "Administration" title on admin dashboard
- Breadcrumbs: Removed from dashboard page
- Sidebar: Admin nav sidebar toggle removed and sidebar forced visible
- Customer dropdown: Active customer shown with checkmark icon, disabled state

### Technical Improvements

#### Dependencies
- Pillow: Added Pillow==10.4.0 for ImageField support
- System dependencies: Updated install scripts with libjpeg-dev, libpng-dev, zlib1g-dev
- gettext: Added to install.sh/update.sh for translation support

#### File Structure
- Media files: Nginx configuration updated to serve /media/ files; Django serves media files as fallback
- Static files: WhiteNoise middleware for production static file serving
- Logging: Added admin_app logger with INFO level for better debugging

#### Code Quality
- Error handling: Improved error handling throughout admin panel
- Logging: Enhanced logging with file existence checks, directory listings, permissions verification
- Code organization: Better separation of concerns, improved template structure

---

## Previous Beta Releases (Merged into 2.0.0)

### [1.18.0-beta.1] - 2026-02-06

Added:
- Delete functionality: added ability to delete customers and users from admin panel with confirmation modal
- User card page: created user detail page similar to customer card, showing user information, memberships, and details in tabs
- Delete confirmation modal: warning modal with 3-second countdown before delete button is enabled to prevent accidental deletions
- View button: added View button to user list for accessing user card page

Changed:
- Customer selection width: increased customer selection container width from 600px to 800px, then to 1000px for better visibility
- Customer card width: changed customer card container to use full width (100%) instead of fixed 1280px max-width
- Delete button styling: made delete buttons narrower (matching View button width) and darker red (#991b1b) for better danger indication
- Delete modal design: updated delete confirmation modal to match profile settings modal design with centered positioning and danger zone styling
- Button widths: standardized View and Edit button widths to match Delete button (8px 12px padding, auto width)

Fixed:
- Customer selection page scroll: fixed scroll behavior to prevent entire page from scrolling - only customer list scrolls when content exceeds container height
- CSS layout: improved flexbox layout for customer selection container and main content area to properly constrain scrolling
- Delete modal positioning: fixed delete modal to be centered on screen instead of appearing top-left
- View button width: made View button consistent width with other action buttons

### [1.17.51-beta.1] - 2026-02-06

Fixed:
- Customer selection page scroll: fixed scroll behavior to prevent entire page from scrolling - only customer list scrolls when content exceeds container height
- CSS layout: improved flexbox layout for customer selection container and main content area to properly constrain scrolling

### [1.17.50-beta.27] - 2026-02-06

Fixed:
- Customer selection page: fixed scroll behavior - only customer list scrolls, not entire page
- Customer name display: ensure customer name only shows in topbar when customer profile is actually selected
- Duplicate divider: removed extra divider line before "Switch Customer Profile" button in avatar menu
- JavaScript syntax errors: replaced inline onclick handlers with data attributes and event listeners

Changed:
- Customer selection: changed text from "Select Customer" to "Select Customer Profile" (Norwegian: "Velg kundeprofil")
- Customer switching: changed text from "Switch Customer" to "Switch Customer Profile" (Norwegian: "Bytt kundeprofil")
- Customer selection UI: made cards more compact and less overwhelming (reduced padding, smaller logos, list layout instead of grid)
- Customer switch icon: changed from pencil icon to building/company icon
- Search placeholder: updated from "Search customers" to "Search customer profiles" (Norwegian: "Søk etter kundeprofiler")
- Customer selection scroll: container uses flexbox with overflow hidden, only list scrolls when needed

Added:
- Customer selection flow: no automatic customer selection on login - users must explicitly choose a customer profile
- Customer selection page: dedicated page showing all available customer profiles with logos and org numbers
- Customer switch modal: modal accessible from avatar menu for switching between customer profiles
- Search field: added search functionality to customer selection page when more than 4 customers available
- Auto-selection: automatically select and hide switch option when user has access to only one customer profile
- Customer switch button: added to avatar menu below user name/email for switching customer profiles

### [1.17.50-beta.26] - 2026-02-06

Fixed:
- Customer logo upload: files now properly saved to disk using explicit storage.save() before model assignment
- Media file serving: Django view added to serve media files in production as fallback when nginx is not configured
- Logo deletion: improved cleanup of old logo files when replacing logos or deleting customers
- File storage: ensure customer_logos directory exists before saving files
- URL routing: fixed duplicate import in urls.py

Changed:
- Customer management: redirect to modern customer card page instead of edit form after add/edit operations
- Logo upload: AJAX-based upload with client-side preview and cache-busting for immediate display
- Logging: added admin_app logger with INFO level for better debugging of file operations

Added:
- Customer card page: modern detail view with logo upload/delete, member management, and portal links tabs
- File storage debugging: enhanced logging with file existence checks, directory listings, and permissions verification

### [1.17.50-beta.25] - 2026-02-06

Fixed:
- Customer logo display: fixed layout with logo on left (120x120px), customer name and description text on right
- Media files: updated nginx config to serve /media/ files; Django serves media files as fallback

Changed:
- CSS: improved customer-header layout with flexbox for better alignment

Added:
- Service desk button in topbar (right side, before avatar) with icon; shows "under development" tooltip on hover
- Custom tooltip component for Facility and Service desk buttons (styled to match site design, appears on hover)
- Projects button in topbar navigation (between Dashboard and Facility); shows "under development" tooltip on hover
- Files button in topbar navigation (after Facility); shows "under development" tooltip on hover
- Language preference synchronization: user's language choice persists across login page and main site; preferred language stored in session and applied automatically on login
- Animated transitions between login and register pages (fade out/in, card height expansion)
- Loading spinner indicator on Sign in button when form is submitted
- Copyright notice in login page footer (left side)
- Customer logo upload: ImageField added to Customer model; logo upload in admin customer form with preview; logo displayed next to customer name on dashboard; automatic logo file deletion when customer is deleted
- Customer logo display: improved layout with larger logo (120x120px) on left, customer name and description text on right
- Media files: nginx configuration updated to serve /media/ files; Django serves media files as fallback
- Pillow dependency: added Pillow==10.4.0 for ImageField support; install scripts updated with system dependencies
- About modal: accessible from avatar menu (all users); shows app version, 5echo.io info, developer credits (Head developer: Kevin Jung Park)
- About modal: update check for admins (compares current version with GitHub main branch); update notification badge in avatar menu when update available
- Norwegian (Norsk) as second language: full i18n with Django LOCALE_PATHS, locale/nb, and set_language switcher
- Language switcher in avatar dropdown (Norsk/English with flags; current language hidden from submenu; open on click, close on mouse leave)
- Login page footer (right): language dropdown listing all languages
- All portal and account templates translated ({% trans %}/{% blocktrans %}); Norwegian translations in locale/nb/LC_MESSAGES/django.po
- docs/I18N.md: how to add and translate strings (Norsk + English) when building the site further
- Portal at site root (/) with HTMX for no-refresh navigation
- Custom admin app at /admin/ (User management, Customers & access, Portal management)
- Customer dropdown in header (avatar-style with search when >4 customers)
- Superusers can switch to any customer; redirect to / after customer switch
- Wider layout (1280px) aligned with topbar and footer
- Admin list filters: Staff/Active labels, single-row toolbar, outlined Search button
- Admin forms: card layout, two-column rows (e.g. username|email), aligned Save/Cancel
- Profile modals: Cancel restores active tab to Account Information
- Changelog modal with "View Full Changelog" / "Hide Full Changelog" toggle
- Profile Account Information: edit (pencil) button to edit email, first name, last name
- Panel footer on Account Information for "Joined [date]" and future account metadata
- Migration `accounts.0001_sync_username_from_email`: syncs User.username from User.email for existing users

Changed:
- Version scheme to beta
- Buttons: smaller (36px height), vertically centered, Search button outlined
- Footer: max-width 1280px, responsive padding
- Customer dropdown: reduced vertical spacing (min-height 0, padding 4px 12px, line-height 1.25); wrapper align-self center
- Topbar: customer picker height/alignment for consistent vertical center
- Tooltip position: moved below buttons (Facility and Service desk) instead of above
- Customer dropdown menu: rebuilt positioning system (removed align-self center, changed to top: 100% with margin-top, improved transform animation)
- Footer buttons: removed padding/margin to match left side text spacing; hover now only changes color
- Footer "View Changelog": added document icon to match "About this portal" styling
- Footer buttons: unified styling for "About this portal" and "View Changelog" (consistent hover and layout)
- Login page footer: further reduced margin-top from 16px to 8px to bring version and language selector much closer to login box
- Login page footer: moved version and language selector to right side (together)
- Customer dropdown menu: active customer now shown as disabled (non-clickable) with checkmark; only other customers can be selected
- Login page language dropdown: only shows other languages (not current language), matching avatar menu behavior
- Language preference: custom set_language view saves preference to session; middleware applies it for authenticated users; login view restores preferred language
- Login/register card: fixed size (min-height 400px for login, 500px for register) to prevent resizing when filling forms
- Register page: added footer with version and language selector (matches login page)
- Login/register transitions: fade out animation (300ms) when navigating between pages; register page expands height and fades in on load
- Login card: centered content horizontally and vertically; dynamic height based on content (removed fixed min-height)
- Sign in button: replaced rotating spinner with subtle pulsing border animation
- Login page footer: added copyright notice on left side ("Copyright © [year] 5echo.io. All rights reserved.")
- Edit (table) button: higher contrast hover (blue background)
- Changelog: pre-release builds (alpha, beta, rc) always show Unreleased; full release shows all sections for that major
- Changelog modal: no scroll on modal container; only content boxes scroll; fade animation when toggling View Full / Hide Full; button pulse animation on toggle
- Changelog short view: only one Unreleased section (stops at next ## heading; no duplicate Added/Changed/Fixed)
- Changelog modal: state-based toggle (data-changelog-view); setTimeout for swap so View Full / Hide Full and reopen work
- Changelog intro text: "All pre-release builds (alpha, beta, rc) are shown as Unreleased"
- Previous changes (pre-0.3.0): one Added, one Changed, one Fixed (no duplicate lists per section)
- Avatar initial: first letter of first name, then last name, then email (no longer username)
- Login: field labeled "Email"; accepts email or username; login with email preferred
- Registration: username hidden and set from email; new users get username = email
- Profile delete account: confirm with email instead of username
- Install wizard: first admin created with username = email; prompt "DEFAULT_ADMIN_EMAIL (login email for first admin)"
- Admin users/roles/customers/access lists: SEARCH label above field; narrower Search button; Add button 36px height; wider search input; single-row toolbar with aligned search and Add button
- Admin user add/edit: checkbox layout for Staff/Active/Superuser; Save and Cancel same height; narrow Save button
- About this portal: moved from avatar menu to footer (right side)
- Footer layout: changed from grid to flex with space-between for left/right sections
- Admin role and customer add/edit: narrow Save button
- Admin customer access add form: centered layout
- RoleForm (name only) for roles add/edit to fix 500; CustomerForm primary_contact queryset in __init__ for customers add
- Login: "Create account" link less bold and centered; Sign in button disabled until email and password filled, then green border/glow when ready
- Register: removed "This creates a user." text; "Back to login" less bold and centered
- Customer dropdown: more padding on menu items; no vertical gap between items; dropdown closer to trigger (2px); topbar alignment with avatar
- Login Sign in: animated green stripe circulating around button when ready (conic-gradient rotation)
- Customer dropdown: active customer shown with checkmark icon in list
- Topbar: Facility button (grayed out, tooltip "This feature is under development")
- Avatar menu: Language (English) with UK flag icon; hover shows submenu with English option
- Topbar: "Portal" renamed to "Dashboard"
- Avatar menu: Language submenu opens on click (not hover), closes when mouse leaves; current language not shown in submenu
- Login page: version below card (left), language selector below card (right)
- Sign in button: single moving pulse animation around button when ready (narrow green wedge)
- Norwegian flag: correct SVG (red field, white-outlined blue cross per 22:16 proportions)
- Changelog: only full releases (no -beta/-alpha/-rc) get version sections; pre-releases stay under Unreleased
- Sign in button: short pulse border animation in loop around button only (no fill); dampened hover brightness
- Facility: Norwegian translation changed from "Fasilitet" to "Anlegg"
- About button: renamed to "About this portal" (EN) / "Om portalen" (NO); icon changed to book/document icon (different from Debug)

Fixed:
- Norwegian flag was wrong (corrected to official Norway flag)
- Footer width now matches main content (1280px)
- Profile: Change password / Delete account Cancel returns to Account Information tab; modal Cancel/Escape restores tab (including Escape key)
- Form button vertical alignment across admin forms
- compilemessages failing with "Can't find msgfmt": install.sh and update.sh install gettext when needed

## Previous changes (pre-0.3.0)
Added:
- Debug view accessible via avatar menu for superusers
- Comprehensive logging middleware for backend request/response tracking
- Frontend logging system for client-side event tracking
- Copy to clipboard functionality for debug data export

Changed:
- Default admin password to "admin" and skip creation if any superuser exists
- Default app bind port to 8097
- Default APP_BIND to 0.0.0.0:8097 (was 127.0.0.1:8097) for reverse proxy compatibility
- Improved install wizard DJANGO_ALLOWED_HOSTS prompt with example
- Enhanced admin interface for Customers, CustomerMemberships, and Portal Links
- Improved topbar design with better button styling and username separation
- Admin button only visible to superusers (removed from login page)
- Footer simplified (removed Quick Links section)
- Changelog button styled to match other footer links
- Made 5echo.io clickable link in footer
- Registration text updated to reflect PMG and Customer admin access assignment
- CustomerMembership admin: multi-select customers when adding, single select when editing
- Moved changelog button to footer under copyright information
- Removed Recent Actions section from admin dashboard (now accessible via modal)
- Redesigned admin tables with modern styling, zebra striping, and improved spacing
- Replaced default Django admin icons with modern minimalist SVG icons
- Improved admin visual hierarchy with better contrast and readability
- Portal now uses session-based customer selection instead of always showing first customer
- Redesigned portal topbar layout: menu buttons (Portal, Admin) moved to left side next to brand
- User avatar with dropdown menu replaces separate logout/admin buttons
- Removed "Your customers" section from portal page (replaced by dropdown in header)
- Footer now always stays at bottom of screen (sticky footer with flexbox layout)
- Admin pages now use same topbar design as portal pages for consistent experience
- Customer dropdown hidden in admin pages (only visible in portal)
- Recent Actions modal button fixed and working properly
- Toast notifications now show in both portal and admin pages, positioned at bottom right
- Active page highlighted in topbar menu (Portal/Admin buttons show active state)
- Footer now identical on portal and admin pages
- Avatar dropdown vertical alignment fixed
- Recent Actions modal button fixed and working properly
- Added password change and profile settings to avatar dropdown menu
- Improved avatar dropdown close behavior (closes on outside click)
- Enhanced active page highlight with better contrast and visual design
- Toast notifications now auto-dismiss after 5 seconds
- Avatar dropdown now shows full name instead of username (falls back to username if no name set)
- Password change page buttons now match in height and are aligned to the right
- Removed "Change Password" link from avatar dropdown menu
- Password change now opens as a modal popup in profile settings page
- Profile settings page redesigned with left sidebar navigation menu
- Delete account functionality with danger zone confirmation modal
- Logout confirmation modal in profile settings sidebar
- Account information section in profile settings
- Password change modal integrated into profile settings
- Increased spacing between website title and menu buttons in topbar (gap: 32px)
- Delete account modal now resets to Account Information section when closed/cancelled
- Increased topbar padding (20px top/bottom, 32px left/right) for better spacing
- Admin dashboard modules now display in 2 columns side by side instead of stacked
- Admin dashboard box titles (captions) now have blue background for better contrast
- Admin dashboard now uses full page width (removed max-width constraint on #container and #content)
- Add buttons in admin dashboard made smaller (28px height, 13px font)
- Change buttons in admin dashboard styled as box buttons with edit icon
- Button icons improved for better contrast
- Add button background changed from blue to green (success color) for better visual distinction
- Comprehensive CSS overrides added to ensure admin page uses full browser width (targeting html, body, #container, #content, .colMS, .colSM, .main, and all child elements)
- Customer switcher now redirects to portal page when switching customer from profile settings page
- Admin dashboard now displays 3 columns instead of 2
- Admin page content now has max-width: 1200px with centered margins (similar to portal page) for better readability
- Fixed admin page width constraint by removing max-width from #container (set to none)
- Footer now properly spans full width and is positioned at bottom on admin pages
- Fixed footer_info context processor to work for admin pages (removed skip check)
- Added debug view at /debug/ for system information, database info, and file paths (superuser only)
- Added even more aggressive CSS overrides using viewport width (100vw) for #container and topbar
- Enhanced topbar CSS to ensure it spans full browser width
- Added Debug link to avatar menu dropdown for superusers (accessible from both portal and admin pages)
- Fixed admin dashboard width by adding more specific CSS selectors and removing padding/margin constraints
- Added comprehensive debug logging middleware to track all requests, responses, database queries, and processing times
- Added frontend JavaScript logging to track button clicks, form submissions, page loads, and JavaScript errors
- Enhanced debug view to display request logs, database queries, and frontend logs
- Fixed admin dashboard width issue by using calc() to break out of #content max-width constraint (dashboard now uses full viewport width)
- Added "Copy to Clipboard" button to debug view for easy sharing of debug data
- Fixed clipboard function error handling and fallback for older browsers
- Fixed button size inconsistency in debug view export section
- Completely redesigned admin dashboard CSS to remove all width constraints and ensure full browser width
- Dashboard now properly breaks out of #content max-width constraint using :has() selector
- Added inline wrapper div in admin/index.html template to force dashboard to break out of #content container using calc() margins
- Fixed footer positioning to use 100vw width with calc() margins to ensure it spans full browser width
- Increased Export button min-width to 140px and added white-space: nowrap to prevent text wrapping
- Removed problematic inline wrapper div that was causing dashboard to disappear - reverted to simpler CSS-only solution using :has() selector
- Added more aggressive CSS overrides targeting #content.colMS specifically to override Django admin's float layout
- Added body.admin-page.dashboard class targeting for dashboard pages
- Increased CSS specificity to ensure dashboard width overrides work even when Django admin CSS loads first
- Added JavaScript to dynamically remove width constraints from #content, #container, and .dashboard elements on dashboard page
- JavaScript runs immediately, on DOMContentLoaded, and after 100ms delay to ensure all CSS has loaded
- Completely redesigned admin dashboard to use same structure as portal page (content-wrapper with max-width: 980px)
- Replaced table-based dashboard layout with panel-based layout matching portal design
- Dashboard now uses .content-wrapper, .dashboard-grid, .panel, .list, and .list-item classes like portal page
- Removed all complex CSS overrides and JavaScript workarounds in favor of simple portal-style structure
- Fixed #content max-width constraint by adding :has(.content-wrapper) selector to remove max-width: 1200px when content-wrapper is present
- Added specific overrides for #content.colMS to ensure it doesn't constrain content-wrapper width
- Added JavaScript fallback to dynamically set #content max-width: 100% when content-wrapper is present
- JavaScript runs immediately, on DOMContentLoaded, and after delays to ensure CSS has loaded
- Enhanced JavaScript to also fix .main, #main, and #container width constraints
- Added window.load event listener to ensure fixes apply after all resources load
- Removed all max-width constraints from #content when dashboard class is present on body
- Added dashboard-grid width fixes in JavaScript
- Added console.log debugging to show computed styles for troubleshooting
- Fixed Django admin's default width: 464px on #content.colMS by adding min-width: 100% override
- Enhanced JavaScript to remove and re-set width property to override Django admin's fixed width
- Changed JavaScript to use cssText instead of setProperty for more aggressive style overrides
- Added MutationObserver to watch for style changes and re-apply fixes if Django admin CSS overwrites them
- Added multiple setTimeout delays up to 1000ms to catch late-loading CSS
- Fixed infinite loop in MutationObserver by removing it and instead removing .colMS class directly
- JavaScript now removes .colMS class and adds .colMS-override class to break Django admin's width: 464px constraint
- Added CSS support for .colMS-override class

Fixed:
- Admin dashboard width issue - completely rebuilt dashboard page to use full browser width
- Duplicate "Administration" title on admin dashboard page
- Breadcrumbs removed from dashboard page to prevent duplicate titles
- Injected CSS directly into template to ensure it loads last and overrides all Django admin styles
- Added JavaScript to hide sidebars and filters that constrain content width
- Force viewport width (100vw) on all container elements to break out of constraints
- Fixed footer width issue - footer now spans full browser width using 100vw and calc() margins
- Fixed footer positioning - footer now sticks to bottom of page using flexbox (matches portal)
- Fixed footer content width - changed from 1200px to 980px to match portal and eliminate right gap
- Footer styling now matches portal exactly (same grid layout, padding, and max-width)
- Footer now moved outside all containers using JavaScript to ensure full width
- Footer uses 100vw with calc() margins to break out of any container constraints
- Admin changelist filter sidebar (#changelist-filter) is now static and cannot be hidden
- Sidebar toggle/collapse buttons are hidden to prevent collapsing
- Standardized layout structure across all pages (portal and admin)
- Footer now consistently positioned at bottom using flexbox (margin-top: auto)
- Footer styling unified - full width background with centered content (max-width: 980px)
- Topbar height and styling standardized across all pages
- All pages now use same flexbox structure: html > body (flex column) > header + main (flex: 1) + footer (margin-top: auto)
- Removed injected "nuclear" JS/CSS from admin dashboard and rely on shared layout
- Standardized Django admin container layout to match portal flex structure
- Footer now uses shared layout rules only (no DOM moves or calc hacks)
- Admin nav sidebar toggle removed and sidebar forced visible
- Simplified admin layout CSS to remove conflicting width overrides
- Admin container now uses flex layout to keep footer at bottom
- Added detailed request logging (view, templates, db time, slow queries)
- Added fetch/XHR logging for frontend (portal + admin)
- Debug page now shows view/template columns and extra Django/system info
- Interactive install wizard to collect .env values and bootstrap local Postgres
- Improved admin interface with helpful descriptions and member/link counts
- Setup guide documentation (SETUP_GUIDE.md)
- Standalone installer script (install.sh) that can be run via curl from GitHub
- Installer detects existing installation and offers update/uninstall options
- Footer with copyright, version, and changelog button
- Changelog modal dialog showing version-specific changes (unreleased or major release)
- Dark mode scrollbar styling
- Initial database migrations for portal models
- Bulk add CustomerMemberships feature integrated into regular add form (multi-select customers)
- Customer admins can now manage memberships for their own customer
- Improved README.md with detailed installation and update instructions
- Modernized Django admin interface with dark theme matching portal design
- Recent Actions modal accessible via clock icon in admin header
- Modern minimalist SVG icons throughout admin interface (Lucide-inspired)
- Customer dropdown selector in admin header for filtering by customer
- Customer dropdown selector in portal header for switching between customers
- Customer switching functionality with session-based active customer storage
- IMPROVEMENTS.md document with comprehensive improvement ideas and future features
- Redesigned topbar with menu buttons on left, customer dropdown in middle-right, user avatar on far right
- User avatar dropdown menu with logout and admin panel access
- Recent Actions button click handler improved (removed conflicting onclick, improved event listener attachment)
- Admin page width constraints further overridden with more aggressive CSS selectors (targeting all divs with class/id containing "col", "content", "container")
- Avatar icon vertical alignment in topbar
- Recent Actions button vertical alignment in admin topbar
- Recent Actions button click functionality (added onclick fallback)
- Local Postgres bootstrap in installer (role/db creation)
- Static files not loading (added WhiteNoise middleware for production static file serving)
- 500 error after login redirect (improved error handling in portal_home view)
- "View site" button redirect error (fixed landing view to check authentication)
- Whitelabeled admin site (removed "Django administration" branding)
- 500 error when adding Customer (fixed member_count/link_count methods to handle new objects)
- Installer interactive prompts when piped from curl (defaults to update mode in non-interactive)
- 500 error when saving Customer in admin (optimized queryset and fixed admin_order_field)
- 500 error in admin save and portal links (fixed context processor file reading, improved error handling)
- 500 error when saving in admin (context processor now skips admin pages, improved admin queryset handling)
- 500 errors on admin changelist and save operations (improved get_queryset URL detection, added comprehensive error handling)
- Database tables missing error (created initial migrations for portal models)
- 500 error when adding CustomerMembership (fixed form fields configuration for add/edit modes)
- 500 error when accessing CustomerMembership changelist (removed bulk_add URL reference)
- 500 error when saving CustomerMembership (fixed form save logic and save_m2m method)
- Complete redesign of Django admin interface with modern minimalist design
- Improved navigation, buttons, and visual hierarchy
- Better contrast and readability throughout admin interface
- 500 error when accessing admin panel (added missing {% load i18n %} in admin index.html template)
- Footer positioning fixed to always be at bottom of screen
- Admin and portal pages now have consistent UI/UX with same topbar design
- Toast notifications unified across portal and admin, positioned bottom right
- Active page indication added to topbar navigation buttons

## [0.1.0-alpha.1] - 2026-01-XX - Initial foundation

### Added
- Login-first site flow
- Registration page (optional)
- Customer model and membership
- Customer portal landing page
- Admin setup and default admin bootstrap
