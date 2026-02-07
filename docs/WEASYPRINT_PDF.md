# WeasyPrint / PDF (service report)

Service report PDF and other documents from **Document templates** use [WeasyPrint](https://weasyprint.org/). WeasyPrint requires system libraries (Pango, Cairo, GdkPixbuf) that must be installed with apt.

**Install wizard:** When you run `scripts/install.sh` (new installation or update), the script automatically installs these dependencies and the correct weasyprint version, so that document template PDFs work without manual steps.

## Error: "cannot load library 'pango-1.0-0'"

If PDF download returns a 500 error and journalctl shows:

```text
OSError: cannot load library 'pango-1.0-0': ... No such file or directory
```

WeasyPrint's system dependencies are missing on the server.

### Solution

On the server (Ubuntu/Debian), run:

```bash
sudo apt-get update
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2
sudo systemctl restart pmg-portal
```

Or run a full update so that `scripts/update.sh` installs the dependencies:

```bash
curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/dev/scripts/install.sh | sudo bash
```

(Choose "Update Production" if the installation already exists.)

## Document templates

Templates are managed under **Admin → Document templates**. The default service report template can be loaded with "Load default service report". HTML and CSS are edited there; variables such as `service_log`, `facility` and `customer` are available in the template.
