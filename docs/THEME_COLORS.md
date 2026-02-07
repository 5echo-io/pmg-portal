# Theme colors (light and dark mode)

Portal colors are controlled by two dedicated CSS files. Everything that uses color references variables from these files, so you can change the look in one place.

## File reference

| Mode   | File | Usage |
|--------|-----|------|
| **Dark** | `src/static/css/theme-dark.css`  | Default (`:root`). All variables for dark mode. |
| **Light**  | `src/static/css/theme-light.css` | Activated when `<html>` has `class="theme-light"`. |

Change the **color codes** in these two files to adjust dark and light mode respectively. The rest of the page (e.g. `app.css`) only uses `var(--variablename)` and gets values from here.

## Variables (both themes)

### Backgrounds
| Variable       | Description |
|----------------|-------------|
| `--bg`         | Main background (page) |
| `--card`       | Cards, boxes, modals |
| `--topbar-bg`  | Main menu (topbar) |
| `--footer-bg`  | Footer |
| `--input-bg`   | Input fields, text areas, search field |

### Text
| Variable | Description |
|----------|-------------|
| `--text` | Main text |
| `--muted`| Muted text (secondary, helper text) |

### Lines and borders
| Variable | Description |
|----------|-------------|
| `--line` | Border lines, frames, dividers |

### Buttons (neutral)
| Variable     | Description |
|--------------|-------------|
| `--btn`      | Button background (default) |
| `--btnHover` | Button background (hover) |

### Primary/accent (links, active menu, focus)
| Variable        | Description |
|-----------------|-------------|
| `--accent`      | Primary color (links, active button) |
| `--accent-hover`| Hover for accent |
| `--accent-light`| Lighter accent (e.g. table row hover) |
| `--accent-rgb`  | Same as accent, but as "R, G, B" for use in `rgba(var(--accent-rgb), 0.2)` |
| `--on-accent`   | Text color on accent background (e.g. white) |

### Danger (Delete, error, warning)
| Variable        | Description |
|-----------------|-------------|
| `--danger`      | Danger buttons, error messages |
| `--danger-hover`| Hover for danger |
| `--danger-rgb`  | As above, for `rgba(var(--danger-rgb), 0.1)` |
| `--on-danger`   | Text on danger buttons (e.g. white) |

### Success (confirmation, status)
| Variable         | Description |
|------------------|-------------|
| `--success`      | Success messages, checkmarks |
| `--success-light`| Lighter success (e.g. status indicator) |
| `--success-rgb`  | For use in `rgba(var(--success-rgb), 0.1)` |

### Shadows and overlay
| Variable         | Description |
|------------------|-------------|
| `--shadow`       | Light shadow (tooltips, small boxes) |
| `--shadow-strong`| Stronger shadow (modals, dropdown) |
| `--overlay`      | Background behind modals (dark overlay) |
| `--focus-ring`   | Focus ring (keyboard navigation) |

### Avatar
| Variable                 | Description |
|--------------------------|-------------|
| `--avatar-gradient-start`| Start of gradient on user avatar |
| `--avatar-gradient-end`  | End of gradient |

### Toast/status (notifications)
| Variable | Description |
|----------|-------------|
| `--toast-success-border` / `--toast-success-bg` | Success toast |
| `--toast-error-border` / `--toast-error-bg`     | Error toast |
| `--toast-warning-border` / `--toast-warning-bg`| Warning toast |
| `--toast-info-border` / `--toast-info-bg`      | Info toast |

### Warning
| Variable       | Description |
|----------------|-------------|
| `--warning-rgb`| RGB value for warning (e.g. toast, badges). Use: `rgba(var(--warning-rgb), 0.2)` |

## How it is loaded

- **Portal (base.html)** and all pages that include `app.css` get the themes automatically: `app.css` imports at the top `css/theme-dark.css` and `css/theme-light.css`.
- **Dark mode** is the default (`:root` in `theme-dark.css`).
- **Light mode** is activated when `<html>` gets the class `theme-light` (set by the theme script in the portal).
- Admin and other apps that use `app.css` use the same variables; they get dark as default unless the theme class is set.

## Changing colors

### Option 1: Admin (recommended for production)

Superusers can override theme variables without editing code:

1. Go to **Admin** → **Server management** → **System customization**.
2. Adjust **Dark theme** and **Light theme** variables (e.g. accent, buttons, backgrounds).
3. Click **Save changes**. Overrides are stored in the database and apply site-wide. Empty fields use the default from the theme CSS files.
4. Use **Reset dark theme** / **Reset light theme** / **Reset all to default** to clear customizations.

Customizations are stored in `portal.SystemInfo` (key `theme_customizations`) and are included in Backup & Restore, so they survive updates and migrations.

### Option 2: Edit CSS files

1. Open **`src/static/css/theme-dark.css`** for dark mode or **`src/static/css/theme-light.css`** for light mode.
2. Change the hex codes (e.g. `#0b1220` → `#0d1525`) or rgba values for the variables you want to adjust.
3. Save. On next load the whole page will use the new values.

You do not need to touch `app.css` or other files to change colors; just edit the two theme files. Admin overrides (if any) are applied on top of these defaults.
