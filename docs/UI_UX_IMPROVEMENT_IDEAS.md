<!--
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: UI/UX improvement ideas and backlog
Path: docs/UI_UX_IMPROVEMENT_IDEAS.md
Created: 2026-02-05
Last Modified: 2026-02-06
-->

# UI/UX improvement ideas – PMG Portal

## Already implemented
- **“Add device” on facility**: First choose device type, then fill in instance (serial number, facility pre-selected). Modal with two steps: 1) Choose device type, 2) Instance form.

---

## Admin / Facilities

### 1. **Breadcrumbs and navigation**
- Clickable breadcrumbs at all levels (Facilities → [Facility name] → Racks → [Rack]).
- Clear “Back to facility” link on rack and device pages.
- Last visited facility/rack remembered (e.g. in session) and offered as shortcut.

### 2. **Tables and lists**
- Sortable columns (click column header).
- Column visibility (choose which columns to show).
- Export to CSV/Excel on lists (devices, facilities, customers).
- Sticky table header when scrolling long lists.
- Empty state with clear CTA: “No devices – add one” with link to the right action.

### 3. **Search and filters**
- Single search field with suggestions (facilities, devices, customers).
- Saved filters (e.g. “My facilities”, “Devices without serial number”).
- Quick filtering with chips/tags (active/inactive, category, facility).
- Search with partial match across multiple fields (name, serial number, brand, model).

### 4. **Modals and forms**
- “Edit device” in modal: Load only form fragment (like other modals), not full page.
- For large forms: step indicator (Step 1 of 3) and “Save draft”.
- Real-time validation (fields validated on blur/tab, not only on submit).
- Clear “Close without saving” with confirmation if user has changed anything.
- Focus on first field when modal opens; Escape closes modal.

### 5. **Devices**
- On device type detail: edit product (name, category, spec) without leaving the page (inline or separate modal).
- Spec editor per category: for Network – ports, PoE, speed; for PC – CPU, RAM, disk (structured UI, not just JSON).
- Port visualizer for network devices (number of ports, PoE indicator, speed per port).
- Quick “Add instance” directly from device type list (icon/button per row).
- Filter on instance list: per facility, per rack, “without serial number”, “without facility”.

### 6. **Facility card**
- Dashboard widget: recently updated facilities, device count per facility.
- Tabs with counts that update without full reload (HTMX or fetch).
- “You are here” indicator in side menu (active tab clear).
- Quick actions on card: “Add rack”, “Add device” without opening full list.

### 7. **Accessibility and responsiveness**
- Focus order and tab navigation in modals (trap focus, close with Escape).
- ARIA labels on icons and buttons.
- Mobile-friendly table (card per row or horizontal scroll with sticky columns).
- Larger touch targets on mobile for “Add” and actions.

### 8. **Feedback and status**
- Toast/snackbar on “Saved”, “Deleted”, “Error” instead of only message box or redirect.
- Loading state on buttons (“Saving…”, spinner) during submit.
- Clear validation error (under field, red border, icon).
- Confirmation before destructive actions (delete device, remove from facility) with short explanation.

### 9. **Customers and access**
- “Manage access”: group customers (e.g. alphabetically or by org number) and search that filters the list.
- Show facility count per customer in customer list.
- Bulk actions: “Grant access to all selected” / “Revoke access for selected”.

### 10. **Documents and IP**
- Document preview (PDF/image) in modal before download.
- IP list: copy icon for IP address and “Copy entire block”.
- Status indicator: “Assigned to device” vs “Available” on IP addresses.

---

## Customer portal (/facilities/, /facility/…)

### 11. **Facility list**
- Card view vs list view (toggle).
- Sort by: name, location, last updated.
- Favourites / “My facilities” (star, sorted to top).

### 12. **Facility detail**
- Map or address display for facility with coordinates/address.
- “Share this page” (link that preserves context).
- Clear “No devices” / “No documents” with explanation.
- Download all documents as ZIP.

### 13. **General**
- Dark mode (theme toggle).
- Clear language switcher (Norwegian/English).
- Short “Last login” / “Profile” in header.
- Login: “Remember me”, forgot password with clear flow.

---

## Technical support for UX

- **HTMX**: More content loaded inline (fewer full page reloads).
- **Keyboard shortcuts**: e.g. `N` for “New device”, `S` for search.
- **Session/state**: Remember selected facility, filter and sort across pages.
- **Performance**: Lazy-load tables (pagination or infinite scroll), defer non-critical JS.

---

*This document may be updated when new improvements are prioritised.*
