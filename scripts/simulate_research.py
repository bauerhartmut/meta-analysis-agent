#!/usr/bin/env python3
"""
External Research Simulation - Re-analyze all collected data with fresh LLM context.
Takes all sources, evidence, and hypotheses from the DB and runs a fresh analysis.
"""

import asyncio
import sqlite3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from research_agent.llm.engine import LLMEngine

DB_PATH = Path(__file__).parent / "data" / "research.db"


def load_research_data():
    """Load all research data from the database."""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # Sources with content
    c.execute("""
        SELECT id, title, author, url, source_type, summary, key_claims, counter_claims, content
        FROM sources
        WHERE length(content) > 100
        ORDER BY relevance DESC
    """)
    sources = []
    for row in c.fetchall():
        sources.append({
            "id": row[0], "title": row[1], "author": row[2], "url": row[3],
            "source_type": row[4], "summary": row[5],
            "key_claims": row[6], "counter_claims": row[7], "content": row[8]
        })

    # All hypotheses
    c.execute("""
        SELECT id, claim, confidence, status, supporting_evidence,
               contradicting_evidence, alternative_explanations, predictions,
               falsification_conditions
        FROM hypotheses
        ORDER BY confidence DESC
    """)
    hypotheses = []
    for row in c.fetchall():
        hypotheses.append({
            "id": row[0], "claim": row[1], "confidence": row[2], "status": row[3],
            "supporting_evidence": row[4], "contradicting_evidence": row[5],
            "alternative_explanations": row[6], "predictions": row[7],
            "falsification_conditions": row[8]
        })

    # All evidence
    c.execute("""
        SELECT e.evidence_type, e.content, e.strength,
               s.title as source_title, h.claim as hypothesis_claim
        FROM evidence e
        LEFT JOIN sources s ON e.source_id = s.id
        LEFT JOIN hypotheses h ON e.hypothesis_id = h.id
        WHERE e.evidence_type IN ('supports', 'contradicts')
        ORDER BY e.strength DESC
    """)
    evidence = []
    for row in c.fetchall():
        evidence.append({
            "type": row[0], "content": row[1], "strength": row[2],
            "source_title": row[3], "hypothesis_claim": row[4]
        })

    # Facts
    c.execute("SELECT content, source_ids, confidence FROM facts ORDER BY confidence DESC")
    facts = []
    for row in c.fetchall():
        facts.append({"content": row[0], "source_id": row[1], "confidence": row[2]})

    # Research questions
    c.execute("SELECT question, priority_score, status FROM research_questions ORDER BY priority_score DESC")
    questions = []
    for row in c.fetchall():
        questions.append({"question": row[0], "priority": row[1], "status": row[2]})

    conn.close()
    return {
        "sources": sources,
        "hypotheses": hypotheses,
        "evidence": evidence,
        "facts": facts,
        "research_questions": questions,
    }


def build_simulation_prompt(data):
    """Build a comprehensive prompt for external simulation."""

    # Compile source summaries (compact)
    source_text = ""
    for i, s in enumerate(data["sources"][:25], 1):
        claims = s.get("key_claims", "[]")
        counter = s.get("counter_claims", "[]")
        source_text += f"{i}. {s['title']}\n"
        source_text += f"   Claims: {claims[:200]}\n"
        source_text += f"   Counter: {counter[:200]}\n\n"

    # Compile evidence (compact)
    evidence_text = ""
    supports = [e for e in data["evidence"] if e["type"] == "supports"]
    contradicts = [e for e in data["evidence"] if e["type"] == "contradicts"]

    evidence_text += f"SUPPORTS ({len(supports)}):\n"
    for e in supports[:15]:
        evidence_text += f"  [{e['strength']:.2f}] {e['content'][:150]}\n"

    evidence_text += f"\nCONTRADICTS ({len(contradicts)}):\n"
    for e in contradicts[:15]:
        evidence_text += f"  [{e['strength']:.2f}] {e['content'][:150]}\n"

    # Compile hypotheses (top 20 only)
    hyp_text = ""
    for h in data["hypotheses"][:20]:
        hyp_text += f"  [{h['confidence']:.2f}] {h['claim'][:120]}\n"

    # Compile facts (compact, top 15)
    facts_text = ""
    for f in data["facts"][:15]:
        facts_text += f"  [{f['confidence']:.2f}] {f['content'][:120]}\n"

    prompt = f"""You are an expert research analyst. A research agent has collected {len(data['sources'])} sources, {len(data['evidence'])} evidence entries, {len(data['hypotheses'])} hypotheses, and {len(data['facts'])} facts on the topic:

**RESEARCH QUESTION:** Eugenik: Embryonenselektion und selektive Reproduktion fuer IQ-Optimierung und Eliminierung von Erbkrankheiten - Transhumanistische Genetik

Your task: Based on ALL the collected data below, produce a comprehensive external simulation / meta-analysis. 

**FORMAT YOUR RESPONSE AS VALID JSON** with these keys:

{{
  "executive_summary": "2-3 paragraph summary of what the research found",
  "research_quality_assessment": {{
    "source_count": <number>,
    "source_quality": "excellent/good/fair/poor",
    "evidence_balance": "description of supports vs contradicts",
    "methodological_concerns": ["list of concerns"],
    "coverage_gaps": ["list of gaps in coverage"]
  }},
  "key_findings": [
    {{
      "claim": "the finding",
      "confidence": 0.0-1.0,
      "supports_count": <n>,
      "contradicts_count": <n>,
      "assessment": "strong/moderate/weak/contested",
      "evidence_quality": "excellent/good/fair/poor",
      "sources_used": ["list of source titles"]
    }}
  ],
  "contested_topics": [
    {{
      "topic": "topic name",
      "proArguments": ["supporting arguments"],
      "conArguments": ["contradicting arguments"],
      "verdict": "which side is stronger and why"
    }}
  ],
  "knowledge_gaps": ["What questions remain unanswered"],
  "recommended_next_steps": ["What research should be done next"],
  "overall_verdict": "The final assessment: Is embryo selection for IQ scientifically viable, ethically justified, or both?"
}}

--- COLLECTED DATA ---

{source_text}

--- EVIDENCE DATABASE ---
{evidence_text}

--- HYPOTHESES ---
{hyp_text}

--- KEY FACTS ---
{facts_text}

Produce a thorough, nuanced, evidence-based analysis. Be critical. Identify contradictions. Don't shy away from uncomfortable conclusions."""

    return prompt


async def run_simulation():
    """Run the external simulation."""
    print("Loading research data from database...")
    data = load_research_data()

    print(f"Loaded: {len(data['sources'])} sources, {len(data['evidence'])} evidence, "
          f"{len(data['hypotheses'])} hypotheses, {len(data['facts'])} facts, "
          f"{len(data['research_questions'])} research questions")

    print("Building simulation prompt...")
    prompt = build_simulation_prompt(data)
    print(f"Prompt length: {len(prompt)} chars (~{len(prompt)//4} tokens)")

    print("\nInitializing LLM...")
    llm = LLMEngine()

    print("Running simulation (this may take 1-2 minutes)...")
    result = await llm.chat(
        messages=[
            {"role": "system", "content": "You are an expert research analyst. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    # Try to parse JSON from response
    try:
        # Find JSON in response (might be wrapped in markdown)
        text = result.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        parsed = json.loads(text)
        
        # Save to file
        output_path = Path(__file__).parent / "data" / "simulation_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print("SIMULATION COMPLETE - Results saved to data/simulation_result.json")
        print(f"{'='*80}")
        
        # Print summary
        print(f"\n--- EXECUTIVE SUMMARY ---\n{parsed.get('executive_summary', 'N/A')}")
        
        print(f"\n--- RESEARCH QUALITY ---")
        qa = parsed.get("research_quality_assessment", {})
        for k, v in qa.items():
            print(f"  {k}: {v}")
        
        print(f"\n--- KEY FINDINGS ---")
        for f in parsed.get("key_findings", []):
            print(f"  [{f.get('confidence', 0):.0%}] {f.get('assessment', '?')}: {f.get('claim', '?')}")
            print(f"    Supports: {f.get('supports_count', 0)} | Contradicts: {f.get('contradicts_count', 0)}")
        
        print(f"\n--- CONTESTED TOPICS ---")
        for t in parsed.get("contested_topics", []):
            print(f"  {t.get('topic', '?')}: {t.get('verdict', '?')}")
        
        print(f"\n--- KNOWLEDGE GAPS ---")
        for g in parsed.get("knowledge_gaps", []):
            print(f"  - {g}")
        
        print(f"\n--- OVERALL VERDICT ---")
        print(f"  {parsed.get('overall_verdict', 'N/A')}")

    except json.JSONDecodeError as e:
        print(f"\nFailed to parse JSON: {e}")
        print("\nRaw response:")
        print(result[:3000])
        
        # Save raw response
        output_path = Path(__file__).parent / "data" / "simulation_raw.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\nRaw response saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(run_simulation())
