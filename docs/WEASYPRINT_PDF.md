# WeasyPrint / PDF (servicerapport)

Servicerapport-PDF og andre dokumenter fra **Document templates** bruker [WeasyPrint](https://weasyprint.org/). WeasyPrint trenger systembiblioteker (Pango, Cairo, GdkPixbuf) som må installeres med apt.

## Feil: «cannot load library 'pango-1.0-0'»

Hvis PDF-nedlasting gir 500-feil og journalctl viser:

```text
OSError: cannot load library 'pango-1.0-0': ... No such file or directory
```

mangler WeasyPrint sine systemavhengigheter på serveren.

### Løsning

Kjør på serveren (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2
sudo systemctl restart pmg-portal
```

Eller kjør en full oppdatering slik at `scripts/update.sh` installerer avhengighetene:

```bash
curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/dev/scripts/install.sh | sudo bash
```

(Velg «Update Production» hvis installasjonen allerede finnes.)

## Document templates

Malene administreres under **Admin → Document templates**. Standard mal for servicerapport kan lastes inn med «Load default servicerapport». HTML og CSS redigeres der; variabler som `service_log`, `facility` og `customer` er tilgjengelige i malen.
