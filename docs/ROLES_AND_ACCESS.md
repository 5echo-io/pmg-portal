# Roller og tilganger (Roles and Access)

## Hierarki (standardroller)

Disse rollene er faste typer og kan ikke slettes som konsept. Brukere kan ikke slette eller tildele roller over eget nivå.

| Nivå | Rolle | Beskrivelse |
|------|--------|-------------|
| 1 | **Platform admin** | `User.is_superuser`. Se og styre alle tenants, overstyre alle roller, opprette/slette tenants, endre globale innstillinger. Synlig **kun** for andre platform admins. Kan ikke slette seg selv. |
| 2 | **Super admin** | `UserProfile.system_role == 'super_admin'`. Nesten som platform admin; kan ikke gjøre kritiske endringer (f.eks. opprette/slette tenants) og kan ikke endre eller slette platform admin. Kan ikke slette seg selv. |
| 3 | **Owner** (per tenant) | Eier tenant (kunde). Kan ikke slettes eller endres av andre enn owner selv. Kan overføre Owner til en annen bruker. |
| 4 | **Administrator** (per tenant) | Kan gjøre det meste (anlegg, rapporter, produktdatablader, slette ting), men ikke systeminnstillinger. Kan ikke slette brukere med høyere rolle. |
| 5 | **User** (per tenant) | Vanlig bruker/kunde. |

## Implementasjon

- **Systemroller**: Platform admin = `User.is_superuser`. Super admin = `portal.UserProfile.system_role == 'super_admin'` (sett i Django admin eller senere i admin-app).
- **Tenant-roller**: Lagres i `CustomerMembership.role`: `owner`, `administrator`, `user`.
- **is_staff avledet**: Feltet «Is staff» vises ikke i brukerskjemaer. `User.is_staff` settes automatisk: `True` hvis brukeren er Platform admin, Super admin, eller har minst én tenant-rolle Owner eller Administrator. Se `portal.roles.compute_is_staff` og `sync_user_is_staff`; signal på `CustomerMembership` oppdaterer brukeren ved lagring/sletting av medlemskap.
- **Sjekker**: `portal.roles` – `can_see_user`, `can_edit_user`, `can_delete_user`, `can_edit_owner_membership`, `get_assignable_tenant_roles`, `can_create_delete_tenants`, `can_access_system_settings`.

## Tildeling av roller

- Ved **redigering av brukertilgang** (Customer access): Kun roller som er på eller under aktørens eget nivå vises i nedtrekksmenyen (f.eks. en Administrator kan bare tildele Administrator eller User).
- Ved **endring av brukers rolle**: Samme begrensning – brukeren kan bare angi roller opp til sitt eget nivå.

## Planlagt utvidelse: egendefinerte roller

- **Egendefinerte roller**: Mulighet til å opprette nye roller med konfigurerbare rettigheter for alle funksjoner i applikasjonen.
- **Begrensning**: Man kan bare gi rettigheter så langt som man selv er i hierarkiet (en Administrator kan ikke gi Owner-nivå).
- Dette bygges videre på dagens hierarki og `get_assignable_tenant_roles` / tillatelsesmatrise.
