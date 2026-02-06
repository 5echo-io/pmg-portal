# Changelog Summary: 0.1.0-alpha.1 → 1.18.0-beta.1

## Major Features Added

### Admin Panel
- **Custom admin app** at `/admin/` with User management, Customers & access, Portal management
- **Customer card page**: Modern detail view with logo upload/delete, member management, and portal links tabs
- **User card page**: User detail page similar to customer card, showing user information, memberships, and details
- **Delete functionality**: Ability to delete customers and users with confirmation modal and 3-second countdown
- **Admin dashboard**: Redesigned with modern minimalist design, panel-based layout
- **Recent Actions modal**: Accessible via clock icon in admin header

### Customer Management
- **Customer logo upload**: ImageField support with preview, automatic file deletion
- **Customer selection flow**: Explicit customer profile selection on login (no auto-select)
- **Customer selection page**: Dedicated page showing all available customer profiles with logos and org numbers
- **Customer switch modal**: Modal accessible from avatar menu for switching between customer profiles
- **Auto-selection**: Automatically selects single customer profile when user has access to only one
- **Search functionality**: Search field on customer selection page when more than 4 customers

### User Experience
- **Profile settings page**: Redesigned with left sidebar navigation menu
- **Password change modal**: Integrated into profile settings
- **Delete account functionality**: With danger zone confirmation modal
- **Logout confirmation modal**: In profile settings sidebar
- **Language preference**: Synchronization across login page and main site
- **Animated transitions**: Between login and register pages

### Internationalization
- **Norwegian (Norsk)**: Full i18n with Django LOCALE_PATHS, locale/nb, and set_language switcher
- **Language switcher**: In avatar dropdown (Norsk/English with flags)
- **All templates translated**: Portal and account templates with {% trans %}/{% blocktrans %}

### UI/UX Improvements
- **Topbar redesign**: Menu buttons on left, customer dropdown in middle-right, user avatar on far right
- **Avatar dropdown**: Shows full name, logout, admin panel access, language switcher
- **Toast notifications**: Unified across portal and admin, positioned bottom right, auto-dismiss after 5 seconds
- **Footer**: Full width with copyright, version, and changelog button
- **Dark mode scrollbar**: Styled to match site design
- **Loading indicators**: Spinner on Sign in button, animated transitions
- **Tooltips**: Custom tooltip component for Facility and Service desk buttons

### Portal Features
- **Portal at site root** (`/`) with HTMX for no-refresh navigation
- **Customer dropdown**: In header (avatar-style with search when >4 customers)
- **Wider layout**: 1280px aligned with topbar and footer
- **Service desk button**: In topbar (right side, before avatar) - under development
- **Projects button**: In topbar navigation - under development
- **Files button**: In topbar navigation - under development

### Developer Tools
- **Debug view**: Accessible via avatar menu for superusers at `/debug/`
- **Comprehensive logging**: Backend request/response tracking, frontend event tracking
- **Copy to clipboard**: Functionality for debug data export
- **About modal**: Shows app version, 5echo.io info, developer credits
- **Update check**: For admins (compares current version with GitHub main branch)

## Major Changes

### Authentication & User Management
- **Login**: Field labeled "Email"; accepts email or username; login with email preferred
- **Registration**: Username hidden and set from email; new users get username = email
- **Profile delete account**: Confirm with email instead of username
- **Migration**: `accounts.0001_sync_username_from_email` syncs User.username from User.email

### Admin Interface
- **Modernized Django admin**: Dark theme matching portal design
- **Admin list filters**: Staff/Active labels, single-row toolbar, outlined Search button
- **Admin forms**: Card layout, two-column rows (e.g. username|email), aligned Save/Cancel
- **Admin tables**: Modern styling, zebra striping, improved spacing
- **SVG icons**: Replaced default Django admin icons with modern minimalist SVG icons

### Layout & Styling
- **Standardized layout**: Consistent structure across all pages (portal and admin)
- **Flexbox layout**: Footer always at bottom, proper spacing
- **Button styling**: Smaller (36px height), vertically centered, consistent widths
- **Customer dropdown**: Reduced vertical spacing, improved positioning
- **Footer width**: Matches main content (1280px → 980px)

### Customer Selection
- **Text updates**: "Select Customer" → "Select Customer Profile" (Norwegian: "Velg kundeprofil")
- **UI improvements**: Compact list layout instead of grid, smaller logos, better spacing
- **Icon updates**: Building/company icon for customer switch
- **Search placeholder**: "Search customer profiles" (Norwegian: "Søk etter kundeprofiler")

### Delete Functionality
- **Delete buttons**: Narrower, darker red (#991b1b) for better danger indication
- **Delete modal**: Updated to match profile settings modal design with centered positioning
- **Button widths**: Standardized View/Edit/Delete buttons (8px 12px padding)

## Bug Fixes

### Critical Fixes
- **Customer logo upload**: Files now properly saved to disk using explicit storage.save()
- **Media file serving**: Django view added to serve media files in production as fallback
- **Logo deletion**: Improved cleanup of old logo files when replacing logos or deleting customers
- **500 errors**: Fixed multiple admin panel errors (Customer save, CustomerMembership, context processor)
- **Database tables**: Created initial migrations for portal models
- **Static files**: Added WhiteNoise middleware for production static file serving

### UI Fixes
- **Customer selection scroll**: Fixed scroll behavior - only customer list scrolls, not entire page
- **Customer name display**: Only shows in topbar when customer profile is actually selected
- **Duplicate divider**: Removed extra divider line before "Switch Customer Profile" button
- **JavaScript syntax errors**: Replaced inline onclick handlers with data attributes and event listeners
- **Delete modal positioning**: Fixed to be centered on screen instead of appearing top-left
- **View button width**: Made consistent with other action buttons
- **Footer positioning**: Fixed to always be at bottom of screen
- **Avatar alignment**: Fixed vertical alignment in topbar
- **Form button alignment**: Fixed vertical alignment across admin forms

### Translation Fixes
- **compilemessages error**: Fixed "Can't find msgfmt" by installing gettext in install scripts
- **Duplicate translations**: Removed duplicate entries in django.po file
- **Norwegian flag**: Corrected to official Norway flag

### Admin Fixes
- **Admin dashboard width**: Completely rebuilt to use full browser width
- **Duplicate titles**: Removed duplicate "Administration" title on admin dashboard
- **Breadcrumbs**: Removed from dashboard page
- **Sidebar**: Admin nav sidebar toggle removed and sidebar forced visible
- **Customer dropdown**: Active customer shown with checkmark icon, disabled state

## Technical Improvements

### Dependencies
- **Pillow**: Added Pillow==10.4.0 for ImageField support
- **System dependencies**: Updated install scripts with libjpeg-dev, libpng-dev, zlib1g-dev
- **gettext**: Added to install.sh/update.sh for translation support

### File Structure
- **Media files**: Nginx configuration updated to serve /media/ files
- **Static files**: WhiteNoise middleware for production static file serving
- **Logging**: Added admin_app logger with INFO level for better debugging

### Code Quality
- **Error handling**: Improved error handling throughout admin panel
- **Logging**: Enhanced logging with file existence checks, directory listings, permissions verification
- **Code organization**: Better separation of concerns, improved template structure

## Documentation

- **SETUP_GUIDE.md**: Detailed installation and update instructions
- **docs/I18N.md**: How to add and translate strings (Norsk + English)
- **docs/ADMIN_LAYOUT.md**: Admin layout documentation
- **README.md**: Improved with detailed installation and update instructions
- **IMPROVEMENTS.md**: Comprehensive improvement ideas and future features

## Version History

- **1.18.0-beta.1** (Current): Delete functionality, user card page, UI improvements
- **1.17.51-beta.1**: Customer selection scroll fixes
- **1.17.50-beta.27**: Customer selection flow, UI improvements, translations
- **1.17.50-beta.26**: Customer card page, logo upload improvements
- **1.17.50-beta.25**: Customer logo display, UI additions
- **0.1.0-alpha.1**: Initial foundation

---

**Total changes**: Hundreds of improvements, bug fixes, and new features across all areas of the application.
