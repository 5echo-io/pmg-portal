# ServiceDesk Plus (ManageEngine) – integration

The PMG portal has fields to link the service log to external tickets:

- **external_id** on each service log: use the ticket ID from ServiceDesk Plus (or another system) here.
- **SLA fields**: `sla_deadline`, `sla_met` for simple SLA tracking.

## Future API integration

ManageEngine provides a REST API for [ServiceDesk Plus Cloud](https://www.manageengine.com/products/service-desk/sdpod-v3-api/SDPOD-V3-API.html). Possible extensions:

1. **Synchronization**: Fetch tickets (Requests) from the API and display/update status in the portal.
2. **Create tickets**: When a planned visit is created, create a Request in ServiceDesk Plus and store the ID in `external_id`.
3. **SLA fetching**: Use the API to fetch SLA status and update `sla_met` / `sla_deadline`.

API documentation and help:

- [SDPOD V3 API](https://www.manageengine.com/products/service-desk/sdpod-v3-api/SDPOD-V3-API.html)
- [ServiceDesk Plus Cloud Help](https://help.sdpondemand.com/home)

For OAuth 2.0 and API keys, see the ManageEngine documentation. Configuration (base URL, client id/secret) should be stored in environment variables or settings, not in code.
