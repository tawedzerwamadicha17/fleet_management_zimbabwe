# Fleet Management Zimbabwe

Standalone App. It contains only the fleet/transport module (Vehicle Trip, Transport Request/Assignment, Fuel Request, inspections, routes, reports) plus the supporting masters it depends on (Files, Import, Export, Cargo Type, Port, Requested Payments, Bond and related). It does not depend on CSF TZ or the Tanzanian modules.

## Zimbabwe localisation
- ZWG/USD instead of TZS; Zimbabwe default country on trips.
- `ZIMRA Fleet Settings`: TIN/BP number, VAT number, VAT rate (default 15.5%, Finance Act No. 7 of 2025), FDMS device and tax IDs, document rules.
- Seeded on install/migrate: Zimbabwe vehicle document types (ZINARA licence, VID Certificate of Fitness, Operator's Licence, insurance, COMESA Yellow Card, carbon tax, cross-border road access) and border posts (Beitbridge, Chirundu, Kazungula, Plumtree, Forbes, Nyamapanda, Victoria Falls...).
- Custom fields: Vehicle (number plate, fuel consumption, status, documents), Customer (VAT no), Sales Invoice (fiscal status, receipt, verification link), Vehicle Trip (transit declaration, carbon tax, Yellow Card, cross-border permit).
- Vehicle Trip: plate-format warning; blocks when mandatory documents are expired or missing.
- Sales Invoice: ZIMRA buyer-detail checks, "Fiscalise with ZIMRA" button, queued submission on submit.
- Daily email of documents expired or expiring soon.

## Install
   email me tawedzerwamadicha@gmail.com

## Dashboard
Open **Fleet Management** from the desktop Apps screen (or `/app/fleet-management`). The workspace shows number cards (active trips, available vehicles, requests awaiting assignment, expired / expiring documents, fuel requests awaiting approval), charts (trips per month, trips by status, fleet status, request and fuel status), quick shortcuts and grouped links to all masters and reports. The same cards/charts are also available as a standard Dashboard: `/app/dashboard-view/Fleet Management`. Run `bench --site <site> migrate` to load it.

## Before relying on it for ZIMRA compliance
1. Receipt signing is not implemented. Register a function at hook `zimra_receipt_signer` that implements ZIMRA's hash chain and device signature for your registered device. Until then, submission is refused.
2. Validate the payload and endpoints against ZIMRA's Fiscal Device Gateway spec in the test environment.
3. Copy the standard/zero/exempt tax IDs from your device configuration.
4. Confirm zero-rating of international transport and currency handling with your tax advisor.
5. Untested on a live bench. Run on a test site first. The bundled Clearing & Forwarding doctypes (Port, Terminal, ICD, Shipping Line) are inherited from the original app and still carry its sea-freight, East Africa orientation; prune or adapt them for Zimbabwe.
