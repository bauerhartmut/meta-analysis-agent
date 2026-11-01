# Legal-First Fulltext Acquisition Pipeline (Prototyp)

Stand: 2026-10-31. Status: funktionierender Prototyp (Analyse → Prototyp →
Test mit 93 DOIs ✓). Bestehende Pipeline-Komponenten wurden **nicht geändert**.

## Architektur

```
DOIs ──► Discovery ──► Rights & License Engine ──► Download Engine ──► data/fulltext_inbox/
         │ (OpenAlex,    │ (Lizenz + Host-Vertrauen;               │ (SHA256, Resume,
         │  Unpaywall,    ▼  kein Verlags-Auto-Download)           ▼  PDF/XML-Validierung)
         │  Crossref)   ┌──────────────┬───────────────┬──────────────────────┐
         ▼              │ DOWNLOAD_    │ LICENSE_      │ MANUAL_REQUIRED/     │
   data/fulltext_      │ ALLOWED      │ UNCLEAR       │ FAILED               │
   metadata/<doi>.json └──────────────┴───────────────┴──────────────────────┘
                                                    │
                                    data/manual_acquisition_queue/
                                    (Titel, DOI, Verlagslink, PMC-Link,
                                     TUfind/EZB/Fernleihe als Zugangswege)
```

Komponenten:

| Datei | Rolle |
|---|---|
| `scripts/fulltext_acquisition.py` | Prototyp-CLI: `--dois FILE [--apply] [--limit N]`; ohne `--apply` reiner Dry-Run (Discovery + Rights-Entscheid) |
| `data/fulltext_inbox/` | heruntergeladene Volltexte (`<doi>.xml` via Europe-PMC-OA-Subset, `.pdf` via Repositorien) |
| `data/fulltext_metadata/` | je Paper ein JSON-Datensatz (siehe unten) |
| `data/fulltext_logs/acquisition.jsonl` | jede Beschaffungsaktion (discovered, manual_queued, downloaded, download_failed, processing_error) |
| `data/fulltext_logs/stats.json` | Dashboard-taugliche Zähler (### unten) |
| `data/manual_acquisition_queue/` | `entries.jsonl` + je Paper ein `.json` mit TU-Zugangsoptionen und Anleitung |
| `scripts/test_dois_small.txt`, `scripts/test_dois_100.txt` | Testmengen (kleiner Set + 93 DOIs via OpenAlex-Themasuche) |

## Rights-Engine: zulässige automatische Downloads

Erlaubt ohne Menschen (Policy, strikt):

1. **PMC/Europe-PMC Volltext-XML** — PMC Open-Access-Subset, ausdrücklich für
   maschinellen Abruf freigegeben (typo: `europepmc_fulltext_xml`).
2. **arXiv-PDF** — explizit für Software-Abgriffe offen.
3. **Repositorien-Kopien** mit einer anerkannten Lizenz
   (`cc0`, `cc-by`, `cc-by-sa`, `cc-by-nc`, `cc-by-nc-sa`) über Unpaywall-OA-Locations.
4. **Vertraute Repositorien** (PMC/arXiv/Zenodo/OSF/…) auch ohne Lizenzzeile.

Nicht automatisch:

* **Verlagsgehostete Kopien** (gold/bronze/hybrid bzw. `host_type=publisher`),
  auch wenn öffentlich erreichbar — die Nutzungsbedingungen wurden für den
  Prototyp nicht verifiziert (`PUBLISHER_ALLOWLIST` ist leer).
* **DOI-Resolver und Verzeichnisse** (`doi.org`, `doaj.org`) — diese URLs lösen
  auf Verlagsseiten auf, die grundsätzlich nicht auto-abgerufen werden.
* **Unbekannte Hosts/Lizenzen** (`LICENSE_UNCLEAR`).
* **Keine offene Kopie** (`MANUAL_REQUIRED`).
* Verboten bleibt: Auto-Downloads über TU-lizenzierte Verlagszugänge, Captcha/
  Cloudflare-Umgehung, Verschleierung von Automatisierung, Campus-IP als
  pauschale Erlaubnis.

## Metadatensatz je Paper (`data/fulltext_metadata/<doi>.json`)

DOI, Titel, Autoren, Jahr, Journal, Abstract (2000 Zeichen), `oa_status`,
`license`, `publisher_url`, `openalex_id`, Status + Grund, `version`
(arxiv-preprint / pmc-final / repository-version), `download_method`,
`fetch_url`, `repository`, `automation` (automatic/none), `checkstatus`
(valid-xml/valid-pdf/failed/pending), bei Download: `download_url`,
`downloaded_at`, `sha256`, `size`, `resumed`, `license_url`.

## Testergebnisse

**Kleiner Test (8 DOIs: 5 aus der laufenden Themendatenbank + 3 Referenzwerke):**
4 × DOWNLOADED (PMC OA subset: Frontiers×2, BMC, BMJ), 2 × FAILED
(PMCID existiert, aber nicht im OA-Subset → in die manuelle Queue mit
PMC-Browser-Link), 2 × MANUAL_REQUIRED (Elsevier JAD; Cochrane CD004366).

**93-DOI-OpenAlex-Test (Thema „exercise + depression + RCT"):**

| Status | n |
|---|---:|
| DOWNLOADED | 18 |
| FAILED (meist: PMCID da, OA-Subset-XML fehlt) | 22 |
| LICENSE_UNCLEAR (grüne/goldene Kopie, ungesicherter Host) | 23 |
| MANUAL_REQUIRED (kein OA, closed) | 30 |

Inbox: 22 Dateien (alles Europe-PMC-XML); Metadaten: 101 Datensätze;
manuelle Queue: 55 Einträge. Kein Verlagszugang wurde angefasst;
keine Captcha-/Botwall-Behandlung; alle Downloads kamen aus explizit
offenen Quellen.

## Abnahmekriterien — Check

- ✅ Quellenrecherche je DOI (OpenAlex + Unpaywall + Crossref + Europe PMC), nachvollziehbar im Log
- ✅ Keine ungeklärten/nicht freigegebenen Volltexte automatisch heruntergeladen
- ✅ OA-Repositorien werden bevorzugt (PMC-XML vor PDF vor Landingpage)
- ✅ Manuelle Beschaffung: Queue mit Titel, DOI, Verlagslink, PMC-Link, TU-Wegen (TUfind, EZB, Fernleihe/subito)
- ✅ Eindeutige Zuordnung: DOI-Dateinamen + Metadaten + SHA256
- ✅ Keine automatisierten Downloads über TU-lizenzierte Verlagszugänge
- ✅ Resume für unterbrochene Downloads; Duplikate via DOI + Hash; kein Überschreiben existierender Dateien

## Konflikte mit bestehenden Modulen (unklär geblieben, kein Code geändert)

1. **Ingest in den Agenten:** Damit die Inbox in den Forschungslauf einfließt,
   muss `orchestrator._ensure_source_text` (bzw. der Volltext-Cache-Pfad in
   `database.fulltext_dir`) Inbox-Dateien nach DOI lesen und — für `.xml` —
   per Tag-Stripping in Klartext konvertieren (derselbe Pipe-Schnitt, den
   `ContentExtractor._pdf_pages` für PDFs beisteuert). Das ist die einzige
   geplante Berührung mit bestehendem Code und muss separat verabredet werden.
2. **Dashboard-Zähler:** `dashboard/server.py` unverändert; `stats.json`
   (discovered/downloaded/manual_required/license_unclear/failed/total_processed)
   kann später in `/api/stats` reingereicht werden.
3. **Polite-pool-E-Mail:** `extractor.py` hält `research@freebuff.ai` hart,
   während `search.py`/`deep_research.py` `OPENALEX_MAILTO` respektieren —
   Vereinheitlichung ist wünschenswert, wurde aber nicht angefasst.
4. **DOI-Kette:** Im laufenden Themencorpus haben nur 5 von 50 Quellen eine
   DOI; vor dem Massen-Prototyp-Lauf lohnt das bestehende
   `scripts/backfill_dois.py` über den Bestand.

## Bekannte Grenzen des Prototyps

- PMC-XML-Vorhandensein ≠ OA-Subset-XML: 22 von 93 DOIs haben eine PMCID,
  aber keine auto-ladbare Volltext-XML → FAILED + manueller Eintrag.
- Institutionelle Repositorien (z. B. `tub.dokumentation.tu-darmstadt.de`,
  Umweltbibliopathy-Depots) sind noch nicht in `REPO_HOSTS` ergänzt — jede
  Aufnahme soll mit verifizierten Terms geschehen.
- Die 93-DOI-Testmenge ist Thema-spezifisch; Wiederholläufe sind idempotent
  (Resume + no-overwrite + Queue-Dedupe) und dürfen frei wiederholt werden.
