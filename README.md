# Meta-Analysis Agent

Ein autonomer Metaanalyse-Agent: Er recherchiert zu einer Frage selbstständig im
Web, liest wissenschaftliche Volltexte (PDF), extrahiert Effektmaße **Wort für
Wort aus der Quelle** (Verbatim-Kontrakt), liest unlesbare Tabellenbilder doppelt
mit einem Vision-Modell (Abweichung → `disputed`, nie Mittelung), bildet
Hypothesen, prüft sie adversarial (Devil's Advocate), poolt statistisch
(Hartung-Knapp-Sidak, LLM-frei, reproduzierbar) und erzeugt einen zitierfähigen
Bericht. Läuft lokal, lange, mit Run-Resume nach Neustart.

> **Zitatregel des Projekts:** Jede zitierte Zahl/Satzpassage ist exakt aus der
> Quelle übernommen und in der Datenbank gegen den Quelltext geprüft. Statistische
> Verarbeitung (`meta/`) ist LLM-frei — Zahlen werden nie von einem Sprachmodell
> errechnet.

## Was öffentlich ist — und was nicht

- **Öffentlich:** Der komplette Agent-Code (Orchestrator, Agents, Statistik,
  Dashboard), Tests, Goldstandard-Fixtures unter `data/golden_tables/`,
  Benchmark-Baseline unter `data/baseline/`.
- **Bewusst nicht im Repository:** Kern-Konfiguration (`research_agent/config.py`
  u. a. Kernbausteine sind per `.gitignore` geschützt; ihre Beschreibungen stehen
  je als `*_PRIVAT.md` daneben), API-Keys (nur `.env`), Lauf-DBs unter
  `data/*.db`. Beschreibungen der geschützten Module liegen offen als
  `*_PRIVAT.md`-Dateien — Code selbst nicht.

## Setup

Voraussetzung: Python 3.10+ (Windows ok, Bash für Shell-Kommandos).

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env      # dann ausfüllen: LLM-Zugang (TUDaGPT) etc.
```

Erster Lauf ( eines Themas):

```bash
python run.py --topic "Does green tea consumption affect short-term memory?"
```

Dashboard (Port 8080, nur localhost):

```bash
python research_agent/dashboard/standalone_server.py
```

Tests:

```bash
export PYTHONIOENCODING=utf-8
python -m pytest research_agent/tests -q
```

## Struktur

```
research_agent/
├── orchestrator.py        # Autonome Läufe, Phasen Planning … Updating
├── agents/                # Debate, Devil's Advocate, Evidence-Scoring
├── meta/                  # Pooling + Metaregression (LLM-frei)
├── research/              # PDF-Layout-Extraktion + Vision-Tabellenlesung
├── llm/                   # Multi-LLM-Engine (TUDaGPT)
├── dashboard/             # WebUI (Standalone + Live-Server)
└── tests/                 # pytest-Suite
scripts/                   # Werkzeug-Skripte (Notebook-Bau, Reparatur-Tools)
docs/internal/             # Arbeitsnotizen, alte README-Fassung
```

## Grenzen

- Englischsprachige Quellen dominiert; PDF-Lesung ist layoutabhängig (Vision-Lesung
  springt bei unlesbaren Text-Layouts ein, meldet Abweichungen als `disputed`).
- Kein Desktop-GUI; Bedienung über CLI + Web-Dashboard auf localhost.
- Kein Multi-User-Betrieb: Das Dashboard hat **keine Authentifizierung** und
  bindet standardmäßig nur auf `127.0.0.1`.

## Lizenz

MIT — siehe `LICENSE`.
