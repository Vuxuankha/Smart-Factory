# Smart Factory developer notes - V16.0.14

## Integration boundary

`app.Application.open_factory()` reuses one `factory_ui.FactoryWindow`. It passes the current `auth_local.AuthStore` and `Session`; no mailbox identity is passed. The new service revalidates current session/role on access and plant/domain grants on each data transaction. Legacy permissions and repositories remain separate.

`factory_catalog.py`: original source names/numbers/requirements, explicit implementation scope in English and Vietnamese. The word "integration_required" means NOT IMPLEMENTED, not a connector that only needs a password. No HTTP or industrial protocol service is exposed.

`factory_schema.py`: 27 whitelisted record schemas, types, same-plant references, admin-only and immutable constraints. `factory_core.py`: transactions, posting, formulas, reports, backup verification. `factory_ui.py`: dark Tkinter UI with main-thread widgets, worker queue, busy guard, pagination and reports. `demo_factory_data.py`: optional deterministic synthetic fixtures only; never invoked by production startup.

## Data and safety boundaries

The new DB has meta, plants, grants, records, postings, audit and preferences tables. Schema version 1 is distinct from the application version. Future schemas are rejected. Fixed offsets are stored per plant; timestamps normalize to UTC. Dates remain business-local dates. DST and currency conversion are not implemented.

SQLite writes use explicit BEGIN IMMEDIATE with busy timeout, rollback and connection close. Optimistic record revisions detect lost updates. Stock quantities are validated Decimal strings with at most six decimal places; no unit conversion or automatic rounding of inventory. Released orders retain a leaf BOM snapshot. Idempotency keys are plant-scoped: repeat identical payload returns the original result; conflicting reuse is rejected. Issue/return/output and audit share a transaction. Returns are full-issue, once only, before output. Output requires material issued for good output, not a full manufacturing scrap-cost/backflush engine.

A visible UI does not confer rights. Admin manages grants; employees start with no plant access; auditor is read-only. Some sensitive masters stay admin-write-only even with a group grant. Audit-chain hashes are not externally anchored or cryptographically signed. Files are not encrypted. A local OS administrator remains a trusted actor.

Snapshot uses SQLite online backup to a temporary file, checksum, ZIP manifest and integrity check, not copying a live DB file. Restore writes a new file exclusively; it never swaps active data. The archive does not contain app accounts, email data or old PMC. It has a 512 MB expanded DB bound and rejects extra members. Only restore trusted self-produced snapshots; a checksum is not authenticity proof.

## Model limitations

- MRP: one product, quantity and need date; up to ten BOM edges; netting at intermediate MAKE levels. No time-phased shared order reservations, ERP/MES sync or automatic goods receipt from inbound PO.
- FEFO: expiry date is exclusive; a lot is unusable on its expiry date. Holds/blocked/future receipt dates are excluded. No arbitrary backdating of issue to bypass expiry.
- Capacity allocation/scheduling: entered capacity weights and one selected machine. Draft only, no global optimum, tooling optimizer, production release to hardware or remote cancellation.
- State/sensor/topology/shift/energy data: manually entered or imported. No live PLC, RFID, biometric or meter feed.
- Energy: interval consumption, entered tariff and explicit CO2 factor/source/date. Missing factor remains UNKNOWN. No official emissions database or financial/ESG certification.
- Cross-system responsibilities: legacy PMC is still its own ledger; migration/reconciliation must be designed before treating this as a production system of record.

## Engineering references (implementation, not user feature requirements)

Python Tkinter threading model: https://docs.python.org/3.12/library/tkinter.html#threading-model
Python sqlite3 transaction control and backup: https://docs.python.org/3.12/library/sqlite3.html
SQLite transactions: https://sqlite.org/lang_transaction.html

These primary sources guide mechanics, not proof of a deployment's safety or certification. Tests use temp folders, mocks or local loopback only. No live scan, device command, mail login, outside API, or new cloud dependency is run to validate Smart Factory.
