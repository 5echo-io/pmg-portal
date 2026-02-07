# ServiceDesk Plus (ManageEngine) – integrasjon

PMG-portalen har felt for å koble servicelogg til eksterne saker:

- **external_id** på hver servicelogg: bruk her sak-ID fra ServiceDesk Plus (eller annet system).
- **SLA-felt**: `sla_deadline`, `sla_met` for enkel sporing av SLA.

## Fremtidig API-integrasjon

ManageEngine tilbyr REST API for [ServiceDesk Plus Cloud](https://www.manageengine.com/products/service-desk/sdpod-v3-api/SDPOD-V3-API.html). Mulige utvidelser:

1. **Synkronisering**: Hente saker (Requests) fra API og vise/oppdatere status i portalen.
2. **Opprette saker**: Når en planlagt tur opprettes, opprette en Request i ServiceDesk Plus og lagre ID i `external_id`.
3. **SLA-henting**: Bruke API for å hente SLA-status og oppdatere `sla_met` / `sla_deadline`.

API-dokumentasjon og hjelp:

- [SDPOD V3 API](https://www.manageengine.com/products/service-desk/sdpod-v3-api/SDPOD-V3-API.html)
- [ServiceDesk Plus Cloud Help](https://help.sdpondemand.com/home)

For OAuth 2.0 og API-nøkler, se ManageEngine-dokumentasjonen. Konfigurasjon (base URL, client id/secret) bør lagres i miljøvariabler eller settings, ikke i kode.
