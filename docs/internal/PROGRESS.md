# Research Agent - Stand 26.08.2026 (Nachts)

## Was fertig ist

### Agent-System (funktioniert)
- **Autonomer Research-Agent** läuft mit Ollama qwen3:14b
- **Dashboard** auf http://localhost:8080 mit Knowledge Graph (D3.js)
- **5 Such-Provider**: OpenAlex, PubMed, Semantic Scholar, arXiv, DuckDuckGo
- **Domain-Filter** gegen irrelevante Papers (100+ Patterns für Physik, Chemie, Engineering)
- **Topic Context Injection** - Such-Queries bekommen Themen-Kontext hinzu
- **Fact-Extraktion** funktioniert (111 Facts aus 78 Quellen)
- **Seed-Fragen-System** mit 10 strategischen Fragen

### Fine-Tuning Umgebung (fertig, auf WSL)
- **WSL Ubuntu** auf D:\AIResearch\finetune\
- **PyTorch 2.13+cu126**, PEFT, TRL, Transformers installiert
- **RTX 3060 12GB** verfügbar
- **QLoRA Config** für qwen3 erstellt
- **Pipeline-Script** `run_pipeline.py` - Export → Convert → Train

### DB Cleanup (fertig)
- 62 Wilson Effect Duplikate entfernt (65 → 7 Hypothesen)
- 54 Wilson Effect Fragen als "answered" markiert
- Agent rotiert jetzt sauber durch alle Seed-Topics

## Forschungsstand (DB)

### Stats
- 78 Quellen | 111 Facts | 8 Hypothesen | 65 Fragen (2 offen) | 257 Embeddings
- 128 Zyklen | Läuft seit ~2h

### Hypothesen (8)
1. **[90%] S:18 C:0** - Wilson Effect: IQ-Erblichkeit steigt von 40% (Kindheit) auf 80% (Erwachsenenalter)
2. **[65%]** - IQ-Selektion könnte pleiotrope Effekte haben (Trade-offs)
3. **[65%]** - Flynn Effect Plateau → Umwelt-Interventionen erschöpft
4. **[65%]** - Flynn Effect bestätigt genetischen Ansatz
5. **[60%]** - Gene für Kognition haben pleiotrope Effekte
6. **[60%]** - PGT-A/PGT-M Kinder haben bessere Outcomes
7. **[60%]** - Quantitative Modelle unterschätzen non-shared environment
8. **[60%]** - Polygenic Scores korrelieren mit realen Outcomes

### Beantwortete Seed-Fragen
- ✅ GWAS Results
- ✅ PGT-A/PGT-M Outcomes
- ✅ Cost-Benefit Analysis
- ✅ Countries practicing embryo selection
- ✅ Response to Selection
- ✅ Polygenic Scores
- ✅ Flynn Effect Plateau
- ✅ Maximum IQ Gain
- ⏳ Counterarguments to Wilson Effect (läuft noch)
- ⏳ Ethical Frameworks

## NÄCHSTER SCHRITT: Fine-Tuning Dataset erstellen

Das ist die wichtigste Aufgabe für morgen!

### Was zu tun ist
1. **Fine-Tuning Dataset aus DB exportieren** (JSONL Format)
   - Conversation-Pairs: System Prompt + User Question + Assistant Answer
   - Jede beantwortete Seed-Frage → 1 Conversation-Pair
   - Hypothesen mit Evidence → Conversation-Pairs
   - Facts → Knowledge-Pairs
   - Gegenargumente + Entkräftung → Debate-Pairs

2. **Dataset-Qualität prüfen**
   - Mindestens 50-100 hochwertige Conversation-Pairs
   - Pro Topic (GWAS, PGT-A, Cost-Benefit, etc.) mindestens 5-10 Paare
   - Konkrete Zahlen (h²=0.80, IQ-Punkte, Kosten)

3. **Auf WSL kopieren**
   - `cp finetune/data/train.jsonl /mnt/d/AIResearch/finetune/data/`
   - Fine-Tuning starten mit `python3 scripts/run_pipeline.py`

### Dataset-Format (JSONL)
```json
{
  "messages": [
    {"role": "system", "content": "Du bist ein Top-Eugeniker und Transhumanist..."},
    {"role": "user", "content": "Was ist der Wilson Effect und was bedeutet er für Embryonenselektion?"},
    {"role": "assistant", "content": "Der Wilson Effect zeigt, dass die Erblichkeit von IQ..."}
  ]
}
```

### Fine-Tuning Config (bereits erstellt)
- Modell: qwen3 (QLoRA, 4-bit)
- LoRA: r=64, alpha=128
- Epochs: 3
- Batch: 4 (RTX 3060 12GB)
- Config: `finetune/configs/qwen3_qlora.yaml`

## Wichtige Dateien
- `research_agent/data/research.db` - Hauptdatenbank
- `research_agent/orchestrator.py` - Agent-Logik (Seed-Fragen, Dedup, Domain-Filter)
- `research_agent/agents/roles.py` - LLM-Prompts (Planner, Researcher, Critic)
- `research_agent/research/search.py` - Such-Provider + Domain-Filter
- `research_agent/dashboard/server.py` - Web-Dashboard + Knowledge Graph API
- `research_agent/dashboard/templates/index.html` - D3.js Graph-Visualisierung
- `finetune/` - Fine-Tuning Umgebung auf WSL

## Server starten
```bash
source /tmp/research-agent-env/bin/activate
cd research_agent
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
PYTHONPATH=$(pwd)/.. python3 -c "
import research_agent.main as m
import sys
sys.argv = ['main', '--port', '8080']
m.main()
"
```
