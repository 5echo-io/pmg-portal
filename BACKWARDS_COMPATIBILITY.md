# Backwards compatibility – PMG Portal

Dette dokumentet beskriver hvordan vi sikrer at appen kan **oppgradere og nedgradere** mellom versjoner uten at servere havner i inkonsistent tilstand, og at **backup/restore** og **install wizard** fungerer på tvers av versjoner.

## Oversikt

- **Versjon lagres i databasen** etter hver vellykket migrering. Ved oppstart sjekker appen om kodeversjonen er **nyere** eller **samme** som DB-versjonen. Hvis DB er nyere (du har nedgradert kode), **blokkeres forespørsler** med 503 og en tydelig melding inntil du har kjørt migreringer bakover.
- **Backup-format** er versjonert. Alle formatversjoner vi støtter (f.eks. `"1"`) kan gjenopprettes av nåværende og fremtidige appversjoner. Backup-filer inneholder også `app_version` (hvem som laget backupen).
- **Install/update-skript** kjører alltid `set_stored_version` etter `migrate`, slik at lagret versjon alltid stemmer med siste kjøring.

## Komponenter

### 1. Lagret appversjon (database)

- **Modell:** `portal.SystemInfo` (nøkkel `app_version`, verdi = streng fra `VERSION`-filen).
- **Settes av:** `manage.py set_stored_version` (kjøres automatisk etter `migrate` i `scripts/update.sh` og `scripts/install.sh`).
- **Brukes av:** `VersionCompatibilityMiddleware` og `pmg_portal.versioning.check_version_compatibility()`.

### 2. Versjonssjekk ved oppstart

- **Middleware:** `pmg_portal.version_middleware.VersionCompatibilityMiddleware`.
- **Logikk:** Hvis **lagret versjon > nåværende kodeversjon** (nedgradering uten tilpasset migreringstilstand), returneres **503** med forklarende HTML.
- **Løsning for bruker:** Kjør migreringer bakover til målgruppeversjonen (se under), deretter start appen på nytt.

### 3. Backup / Restore

- **Manifest:** `manifest.json` i hver backup inneholder:
  - `version` – backup-**format**versjon (f.eks. `"1"`). Endres bare når backup-formatet endres (ny struktur, ikke bare appversjon).
  - `app_version` – appversjon som **laget** backupen (fra `VERSION`).
- **Støttede formatversjoner:** `admin_app.backup_restore.SUPPORTED_BACKUP_FORMAT_VERSIONS` (i dag `["1"]`). Alle listerte format kan gjenopprettes av nåværende app.
- **Oppgradering:** Backup fra v2.0.0 kan gjenopprettes på v5.0.0. Etter restore har DB schema og data fra backupen; lagret `app_version` i DB vil være den fra backupen. Det er OK – appen behandler det som en «oppgradering» (kode nyere enn eller lik DB) og kjører ikke blokkering.
- **Nedgradering:** For å gå tilbake til f.eks. v2.0.0: installer v2.0.0, gjenopprett en backup tatt på v2 (eller kjør migreringer bakover til v2s migreringspunkt), start appen. Ikke gjenopprett en backup fra v5 på en v2-installasjon med mindre du vet at format og schema er kompatible.

### 4. Install wizard og .env

- Nye .env-nøkler bør ha **standardverdier** i `settings.py` (f.eks. `env("NY_NØKKEL", "default")`), slik at eldre installasjoner ikke må oppdatere .env for å starte.
- Install/update-skriptene endrer ikke .env ved oppdatering; de beholder eksisterende .env. Unntak: manuell endring eller dokumentert migrering av konfigurasjon.

## Oppgradering (f.eks. v2.0.0 → v5.0.0)

1. Deploy ny kode (v5.0.0).
2. Kjør som vanlig:  
   `sudo bash scripts/update.sh`  
   eller  
   `sudo bash scripts/install.sh`  
   (velg Update).
3. Script kjører `migrate`, deretter `set_stored_version`. DB lagrer nå v5.0.0.
4. Appen starter; middleware ser at kodeversjon >= lagret versjon → ingen blokkering.

## Nedgradering (f.eks. v5.0.0 → v2.0.0)

1. **Stopp tjenesten.**
2. **Deploy gammel kode** (v2.0.0).
3. Kjør migreringer **bakover** til det migreringspunktet v2.0.0 forventer, f.eks.:
   ```bash
   cd /opt/pmg-portal/src
   sudo -E .venv/bin/python manage.py migrate portal 0006_device_type_and_product_fk   # eksempel – sjekk v2 sin siste migrering
   sudo -E .venv/bin/python manage.py migrate admin_app 0001_add_admin_notifications   # om nødvendig
   ```
4. Sett lagret versjon til nåværende (v2), slik at middleware ikke blokkerer:
   ```bash
   sudo -E .venv/bin/python manage.py set_stored_version
   ```
5. Start tjenesten.

Hvis du **ikke** kjører migreringer bakover og starter v2-kode mot en DB som har v5-migreringer, vil appen enten feile (manglende tabeller/kolonner) eller middleware vil returnere 503 fordi lagret versjon (v5) er nyere enn kode (v2). Da må du enten kjøre migreringer bakover som over, eller gjenopprette en backup tatt før oppgradering.

## Funksjoner og filer (flyttet / slettet / lagt til)

For at appen skal **forbli funksjonell uansett versjon** når filer flyttes, slettes eller legges til:

- **Én kodeversjon per deploy:** Ved oppgradering deployer du ny kode (med nye filer/URLer/views); ved nedgradering deployer du gammel kode (med gammel filstruktur). Appen som kjører har alltid den filstrukturen som hører til den versjonen – så lenge migreringer og lagret versjon er tilpasset (se over).
- **Nye filer/views/URLer:** Når du legger til en ny funksjon (ny template, ny view, ny URL), påvirker det ikke eldre versjoner – de har ikke den koden. Etter nedgradering bruker du gammel kode som ikke refererer til de nye filene.
- **Flytting/sletting av filer:** Gjør det i **nye** commits/versjoner. Eldre versjoner har fortsatt de gamle stiene. Unngå at **samme** versjon av koden refererer til en fil som er slettet eller flyttet i samme release (dvs. refaktorer flytt/slett i én konsistent endring).
- **Templates som kan mangle:** Hvis en view brukes på tvers av versjoner men template kan variere, vurder `get_template()` med fallback eller try/except rundt `render` og returner en enkel melding (f.eks. 404 eller «Ikke tilgjengelig i denne versjonen») i stedet for å la TemplateDoesNotExist krasje hele forespørselen.
- **URL-er:** Unngå at en URL i en eldre versjon peker på en view som ikke lenger finnes i den versjonen (typisk unngått ved at hele urlconf er del av samme kodeversjon).

Kort sagt: **Appen opprettholdes funksjonell per versjon fordi hver deploy er én kodeversjon med tilhørende filer; migreringer + set_stored_version sikrer at DB og kode er i sync ved opp- og nedgradering.**

## Regler for utviklere

1. **Migreringer:** Skriv **reversible** migreringer der det er mulig (`RunPython` med `reverse_code`, `AlterField` som kan rulles tilbake). Dette gjør nedgradering tryggere.
2. **Backup-format:** Når du endrer **struktur** på backup (nye filer i arkivet, annen manifest-struktur), øk `BACKUP_FORMAT_VERSION` og legg den **gamle** versjonen i `SUPPORTED_BACKUP_FORMAT_VERSIONS` slik at eldre backup-filer fortsatt kan gjenopprettes.
3. **VERSION-fil:** Hold `VERSION` oppdatert ved release. Den brukes både for visning og for versjonssjekk.
4. **Nye innstillinger:** Bruk `env("NAVN", "default")` for nye .env-variabler slik at eksisterende installasjoner ikke brekker.
5. **Nye filer/funksjoner:** Ved å legge til eller fjerne filer/views/URLer, gjør det i én konsistent versjon; ved nedgradering deployes koden som ikke refererer til de nye filene.

## Korte svar på vanlige spørsmål

- **Kan jeg gjenopprette en backup fra v2 på v5?** Ja, hvis backup-formatet er støttet (i dag format "1").
- **Kan jeg gjenopprette en backup fra v5 på v2?** Kun hvis backup-formatet er det samme og schema i backupen er kompatibelt med v2 (typisk backup tatt på v2).
- **Hvorfor får jeg 503 etter nedgradering?** Fordi DB fortsatt har «nyere» lagret versjon. Kjør migreringer bakover og deretter `set_stored_version`, så forsvinner blokkeringen.
- **Må jeg gjøre noe etter restore?** Nei. Restore erstatter DB (og media); lagret versjon i DB kommer fra backupen. Appen vil ikke blokkere fordi kodeversjon er >= den lagrede etter restore (oppgradering eller lik versjon).
