# Changelog

All notable changes to this project will be documented in this file.
This project follows Semantic Versioning (SemVer).

## [Unreleased]

All pre-release builds (alpha, beta, rc) are shown as Unreleased until release as plain MAJOR.MINOR.PATCH.

Added:
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
- Edit (table) button: higher contrast hover (blue background)
- Changelog: pre-release builds (alpha, beta, rc) always show Unreleased; full release shows all sections for that major
- Changelog modal: no scroll on modal container; only content boxes scroll; fade animation when toggling View Full / Hide Full; button pulse animation on toggle
- Changelog short view: only one Unreleased section (stops at next ## heading; no duplicate Added/Changed/Fixed)
- Avatar initial: first letter of first name, then last name, then email (no longer username)
- Login: field labeled "Email"; accepts email or username; login with email preferred
- Registration: username hidden and set from email; new users get username = email
- Profile delete account: confirm with email instead of username
- Install wizard: first admin created with username = email; prompt "DEFAULT_ADMIN_EMAIL (login email for first admin)"

Fixed:
- Footer width now matches main content (1280px)
- Profile: Change password / Delete account Cancel returns to Account Information tab; modal Cancel/Escape restores tab (including Escape key)
- Form button vertical alignment across admin forms

## Previous changes (pre-0.3.0)
Added:
- Debug view accessible via avatar menu for superusers
- Comprehensive logging middleware for backend request/response tracking
- Frontend logging system for client-side event tracking
- Copy to clipboard functionality for debug data export
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

Changed:
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

## [0.1.0-alpha.1] - Initial foundation
Added:
- Login-first site flow
- Registration page (optional)
- Customer model and membership
- Customer portal landing page
- Admin setup and default admin bootstrap
