# UI/UX-forbedringsforslag – PMG Portal

## Allerede implementert
- **«Legg til enhet» på anlegg**: Først velg enhetstype, deretter fyll ut instans (serienummer, anlegg forhåndsvalgt). Modal med to steg: 1) Velg enhetstype, 2) Skjema for instans.

---

## Admin / Anlegg

### 1. **Breadcrumbs og navigasjon**
- Klikkbare breadcrumbs på alle nivåer (Anlegg → [Anleggsnavn] → Racks → [Rack]).
- «Tilbake til anlegg»-lenke tydelig på rack- og enhetsider.
- Siste besøkte anlegg/rack huskes (f.eks. i session) og tilbys som snarvei.

### 2. **Tabeller og lister**
- Sorterbare kolonner (klikk på kolonneheader).
- Kolonnevis synlighet (velg hvilke kolonner som vises).
- Eksport til CSV/Excel på lister (enheter, anlegg, kunder).
- Sticky table header ved scrolling på lange lister.
- Empty state med tydelig CTA: «Ingen enheter – legg til en» med lenke til riktig handling.

### 3. **Søk og filtre**
- Ett samlet søkefelt med forslag (anlegg, enheter, kunder).
- Lagrede filtre (f.eks. «Mine anlegg», «Enheter uten serienummer»).
- Hurtigfiltrering med chips/tags (aktiv/inaktiv, kategori, anlegg).
- Søk med delvis treff i flere felt (navn, serienummer, merke, modell).

### 4. **Modaler og skjemaer**
- «Rediger enhet» i modal: Last inn kun skjema-fragment (som andre modaler), ikke hele siden.
- For store skjemaer: stegindikator (Steg 1 av 3) og «Lagre utkast».
- Validering i sanntid (felter valideres ved blur/tab, ikke bare ved submit).
- Tydelig «Lukke uten å lagre» med bekreftelse hvis bruker har endret noe.
- Fokus på første felt når modal åpnes; Escape lukker modal.

### 5. **Enheter (Devices)**
- På device type-detalj: rediger produkt (navn, kategori, spec) uten å forlate siden (inline eller egen modal).
- Spec-editor per kategori: for Nettverk – porter, PoE, hastighet; for PC – CPU, RAM, disk (strukturert UI, ikke bare JSON).
- Port-visualizer for nettverksenheter (antall porter, PoE-indikator, hastighet per port).
- Hurtig «Legg til instans» direkte fra device type-listen (ikon/knapp per rad).
- Filter på instansliste: per anlegg, per rack, «uten serienummer», «uten anlegg».

### 6. **Anleggskort (facility card)**
- Dashboard-widget: sist endrede anlegg, antall enheter per anlegg.
- Tabs med tellere som oppdateres uten full reload (HTMX eller fetch).
- «Du er her»-indikator i sidemeny (aktiv tab tydelig).
- Hurtighandlinger på kort: «Legg til rack», «Legg til enhet» uten å åpne full liste.

### 7. **Tilgjengelighet og responsivitet**
- Fokusrekkefølge og tab-navigasjon i modaler (trap focus, lukk med Escape).
- ARIA-labels på ikoner og knapper.
- Brukervennlig tabell på mobil (kort per rad eller horisontal scroll med sticky kolonner).
- Større touch-targets på mobil for «Legg til» og handlinger.

### 8. **Tilbakemeldinger og status**
- Toast/snackbar ved «Lagret», «Slettet», «Feil» i stedet for kun meldingsboks eller redirect.
- Loading-state på knapper («Lagrer…», spinner) under submit.
- Tydelig feilmelding ved validering (under feltet, rød ramme, ikon).
- Bekreftelse før destruktive handlinger (slett enhet, fjern fra anlegg) med kort forklaring.

### 9. **Kunder og tilgang**
- «Administrer tilgang»: grupper kunder (f.eks. alfabetisk eller etter org.nr.) og søk som filtrerer listen.
- Vis antall anlegg per kunde i kundelisten.
- Massehandlinger: «Gi tilgang til alle valgte» / «Fjern tilgang for valgte».

### 10. **Dokumenter og IP**
- Forhåndsvisning av dokument (PDF/ bilde) i modal før nedlasting.
- IP-liste: kopier-ikon for IP-adresse og «Kopier hele blokk».
- Statusindikator: «Tildelt enhet» vs «Ledig» på IP-adresser.

---

## Kundeportal (/facilities/, /facility/…)

### 11. **Anleggsliste**
- Kortvisning vs listevisning (toggle).
- Sortering: navn, sted, sist oppdatert.
- Favoritter / «Mine anlegg» (stjernemarkering, sortert øverst).

### 12. **Anleggsdetalj**
- Kart eller adressevisning for anlegg med koordinater/adresse.
- «Del denne siden» (lenke som beholder kontekst).
- Tydelig «Ingen enheter» / «Ingen dokumenter» med forklaring.
- Nedlast alle dokumenter som ZIP.

### 13. **Generelt**
- Mørk modus (theme-toggle).
- Språkvelger tydelig (norsk/engelsk).
- Kort «Sist innlogget» / «Profil» i header.
- Pålogging: «Husk meg», glemt passord med tydelig flyt.

---

## Teknisk støtte for UX

- **HTMX**: Mer innhold lastet inline (færre full page reloads).
- **Keyboard shortcuts**: f.eks. `N` for «Ny enhet», `S` for søk.
- **Session/state**: Husk valgt anlegg, filter og sortering på tvers av sidene.
- **Performance**: Lazy-load tabeller (pagination eller infinite scroll), defer ikke-kritisk JS.

---

*Dette dokumentet kan oppdateres når nye forbedringer prioriteres.*
