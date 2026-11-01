"""
Dataset Exporter - Creates fine-tuning datasets from accumulated research knowledge.
Exports knowledge as JSONL (for LLM fine-tuning) or Markdown (for reading).
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from collections import Counter

from .database import Database

logger = logging.getLogger(__name__)


class DatasetExporter:
    """Export research knowledge as structured datasets."""

    def __init__(self, db: Database):
        self.db = db

    def export_full_dataset(self, output_dir: str = "data/dataset") -> Dict[str, str]:
        """
        Export all research knowledge as a complete dataset.
        Returns dict of file paths created.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        files = {}

        # 1. Knowledge Base (JSONL for fine-tuning)
        kb_path = f"{output_dir}/knowledge_base_{timestamp}.jsonl"
        files["knowledge_base"] = self._export_knowledge_base(kb_path)

        # 2. Q&A Pairs (for instruction tuning)
        qa_path = f"{output_dir}/qa_pairs_{timestamp}.jsonl"
        files["qa_pairs"] = self._export_qa_pairs(qa_path)

        # 3. Hypothesis Dataset
        hyp_path = f"{output_dir}/hypotheses_{timestamp}.jsonl"
        files["hypotheses"] = self._export_hypotheses(hyp_path)

        # 4. Source Catalog
        src_path = f"{output_dir}/sources_{timestamp}.json"
        files["sources"] = self._export_sources(src_path)

        # 5. Research Report (Markdown)
        report_path = f"{output_dir}/research_report_{timestamp}.md"
        files["report"] = self._export_report(report_path)

        # 6. Complete Knowledge Graph
        graph_path = f"{output_dir}/knowledge_graph_{timestamp}.json"
        files["knowledge_graph"] = self._export_knowledge_graph(graph_path)

        logger.info(f"Dataset exported to {output_dir}: {list(files.keys())}")
        return files

    def _export_knowledge_base(self, path: str) -> str:
        """
        Export all facts, hypotheses, and claims as JSONL.
        Each line is a JSON object with:
        - type: fact/hypothesis/claim
        - content: the knowledge
        - confidence: confidence level
        - sources: supporting source IDs
        - metadata: additional context
        """
        records = []

        # Facts
        facts = self.db.get_facts(limit=1000)
        for fact in facts:
            records.append({
                "type": "fact",
                "content": fact.get("content", ""),
                "confidence": fact.get("confidence", 0.5),
                "sources": json.loads(fact.get("source_ids", "[]")),
                "topic": fact.get("topic", ""),
                "date_added": fact.get("date_added", ""),
            })

        # Hypotheses
        hypotheses = self.db.get_hypotheses(limit=1000)
        for hyp in hypotheses:
            records.append({
                "type": "hypothesis",
                "content": hyp.get("claim", ""),
                "confidence": hyp.get("confidence", 0.3),
                "status": hyp.get("status", ""),
                "supporting_evidence": json.loads(hyp.get("supporting_evidence", "[]")),
                "contradicting_evidence": json.loads(hyp.get("contradicting_evidence", "[]")),
                "alternative_explanations": json.loads(hyp.get("alternative_explanations", "[]")),
                "predictions": json.loads(hyp.get("predictions", "[]")),
                "falsification_conditions": hyp.get("falsification_conditions", ""),
                "rejection_reason": hyp.get("rejection_reason", ""),
                "topic": hyp.get("topic", ""),
                "date_added": hyp.get("date_added", ""),
                "last_updated": hyp.get("last_updated", ""),
            })

        # Claims
        claims = self.db.get_claims(limit=1000)
        for claim in claims:
            records.append({
                "type": "claim",
                "content": claim.get("content", ""),
                "confidence": claim.get("confidence", 0.5),
                "source_id": claim.get("source_id", ""),
                "claim_type": claim.get("claim_type", ""),
                "date_added": claim.get("date_added", ""),
            })

        with open(path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(f"Knowledge base: {len(records)} records -> {path}")
        return path

    def _export_qa_pairs(self, path: str) -> str:
        """
        Export question-answer pairs for instruction tuning.
        Format: {"instruction": "...", "input": "...", "output": "..."}
        """
        pairs = []

        # From answered questions
        questions = self.db._get_all(
            "research_questions",
            where="status = 'answered' AND answer_summary != ''",
            limit=500,
        )
        for q in questions:
            pairs.append({
                "instruction": "Based on the research, answer this question thoroughly.",
                "input": q.get("question", ""),
                "output": q.get("answer_summary", ""),
                "metadata": {
                    "importance": q.get("importance", 0.5),
                    "uncertainty": q.get("uncertainty", 0.5),
                }
            })

        # From hypotheses with reasoning
        hypotheses = self.db.get_hypotheses(limit=500)
        for hyp in hypotheses:
            if hyp.get("status") in ("supported", "confirmed", "contested"):
                supporting = json.loads(hyp.get("supporting_evidence", "[]"))
                contra = json.loads(hyp.get("contradicting_evidence", "[]"))
                alternatives = json.loads(hyp.get("alternative_explanations", "[]"))

                output_parts = [f"Hypothesis: {hyp.get('claim', '')}"]
                output_parts.append(f"Status: {hyp.get('status', '')} (confidence: {hyp.get('confidence', 0):.0%})")
                if alternatives:
                    output_parts.append(f"Alternative explanations: {'; '.join(alternatives)}")
                if hyp.get("falsification_conditions"):
                    output_parts.append(f"Falsification conditions: {hyp.get('falsification_conditions')}")

                pairs.append({
                    "instruction": "Analyze this research hypothesis and provide a balanced assessment.",
                    "input": hyp.get("claim", ""),
                    "output": "\n".join(output_parts),
                    "metadata": {
                        "status": hyp.get("status", ""),
                        "confidence": hyp.get("confidence", 0),
                    }
                })

        # From journal entries (research process knowledge)
        journal = self.db.get_journal_entries(limit=200)
        for entry in journal:
            findings = json.loads(entry.get("important_findings", "[]"))
            if findings:
                pairs.append({
                    "instruction": "Summarize the key findings from this research cycle.",
                    "input": entry.get("research_question", ""),
                    "output": "\n".join(f"- {f}" for f in findings),
                    "metadata": {
                        "cycle": entry.get("cycle_number", 0),
                        "confidence_change": entry.get("confidence_change", ""),
                    }
                })

        with open(path, "w", encoding="utf-8") as f:
            for pair in pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + "\n")

        logger.info(f"Q&A pairs: {len(pairs)} pairs -> {path}")
        return path

    def _export_hypotheses(self, path: str) -> str:
        """Export detailed hypothesis dataset with full evidence chains."""
        hypotheses = self.db.get_hypotheses(limit=1000)
        records = []

        for hyp in hypotheses:
            evidence = self.db.get_evidence_for_hypothesis(hyp["id"])
            record = {
                "id": hyp["id"],
                "claim": hyp.get("claim", ""),
                "status": hyp.get("status", ""),
                "confidence": hyp.get("confidence", 0.3),
                "supporting_evidence": [
                    {
                        "content": e.get("content", ""),
                        "strength": e.get("strength", 0.5),
                        "source_id": e.get("source_id", ""),
                    }
                    for e in evidence if e.get("evidence_type") == "supports"
                ],
                "contradicting_evidence": [
                    {
                        "content": e.get("content", ""),
                        "strength": e.get("strength", 0.5),
                        "source_id": e.get("source_id", ""),
                    }
                    for e in evidence if e.get("evidence_type") == "contradicts"
                ],
                "alternative_explanations": json.loads(hyp.get("alternative_explanations", "[]")),
                "predictions": json.loads(hyp.get("predictions", "[]")),
                "falsification_conditions": hyp.get("falsification_conditions", ""),
                "rejection_reason": hyp.get("rejection_reason", ""),
                "topic": hyp.get("topic", ""),
                "date_added": hyp.get("date_added", ""),
                "last_updated": hyp.get("last_updated", ""),
            }
            records.append(record)

        with open(path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(f"Hypotheses: {len(records)} records -> {path}")
        return path

    def _export_sources(self, path: str) -> str:
        """Export source catalog as JSON."""
        sources = self.db.get_all_sources(limit=1000)
        catalog = []
        for s in sources:
            catalog.append({
                "id": s.get("id", ""),
                "title": s.get("title", ""),
                "url": s.get("url", ""),
                "source_type": s.get("source_type", ""),
                "credibility": s.get("credibility", 0.5),
                "summary": s.get("summary", ""),
                "key_claims": json.loads(s.get("key_claims", "[]")),
                "counter_claims": json.loads(s.get("counter_claims", "[]")),
                "date_added": s.get("date_added", ""),
            })

        with open(path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

        logger.info(f"Sources: {len(catalog)} entries -> {path}")
        return path

    def _export_report(self, path: str) -> str:
        """Export a comprehensive research report as Markdown."""
        stats = self.db.get_stats()
        hypotheses = self.db.get_hypotheses(limit=100)
        questions = self.db._get_all("research_questions", limit=100)
        sources = self.db.get_all_sources(limit=100)
        journal = self.db.get_journal_entries(limit=50)
        contradictions = self.db.get_unresolved_contradictions()

        # Get topic from session
        session = self.db.get_active_session()
        if not session:
            sessions = self.db.get_all_sessions(limit=1)
            session = sessions[0] if sessions else {}

        topic = session.get("topic", "Unknown Topic")

        report = []
        report.append(f"# Research Report: {topic}")
        report.append(f"\nGenerated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        report.append(f"\n---\n")

        # Statistics
        report.append("## Statistics\n")
        report.append(f"| Metric | Value |")
        report.append(f"|--------|-------|")
        report.append(f"| Research Cycles | {stats.get('total_cycles', 0)} |")
        report.append(f"| Sources Analyzed | {stats.get('sources', 0)} |")
        report.append(f"| Facts Discovered | {stats.get('facts', 0)} |")
        report.append(f"| Hypotheses Generated | {stats.get('hypotheses', 0)} |")
        report.append(f"| Open Questions | {stats.get('open_questions', 0)} |")
        report.append(f"| Contradictions | {stats.get('contradictions', 0)} |")
        report.append(f"| Knowledge Nodes | {stats.get('knowledge_nodes', 0)} |")
        report.append("")

        # Active Hypotheses
        active = [h for h in hypotheses if h.get("status") in ("proposed", "plausible", "supported", "contested")]
        if active:
            report.append("## Active Hypotheses\n")
            for h in sorted(active, key=lambda x: x.get("confidence", 0), reverse=True):
                conf = h.get("confidence", 0)
                status = h.get("status", "")
                report.append(f"### [{status.upper()}] {h.get('claim', '')}")
                report.append(f"- **Confidence:** {conf:.0%}")
                alternatives = json.loads(h.get("alternative_explanations", "[]"))
                if alternatives:
                    report.append(f"- **Alternatives:** {'; '.join(alternatives)}")
                predictions = json.loads(h.get("predictions", "[]"))
                if predictions:
                    report.append(f"- **Predictions:**")
                    for p in predictions:
                        report.append(f"  - {p}")
                if h.get("falsification_conditions"):
                    report.append(f"- **Falsification:** {h.get('falsification_conditions')}")
                report.append("")

        # Rejected Hypotheses
        rejected = [h for h in hypotheses if h.get("status") == "rejected"]
        if rejected:
            report.append("## Rejected Hypotheses\n")
            for h in rejected:
                report.append(f"- **{h.get('claim', '')}**")
                if h.get("rejection_reason"):
                    report.append(f"  - Reason: {h.get('rejection_reason')}")
            report.append("")

        # Contradictions
        if contradictions:
            report.append("## Unresolved Contradictions\n")
            for c in contradictions:
                report.append(f"- **{c.get('claim_a', '')}** vs **{c.get('claim_b', '')}**")
                if c.get("resolution_note"):
                    report.append(f"  - Note: {c.get('resolution_note')}")
            report.append("")

        # Key Sources
        if sources:
            report.append("## Key Sources\n")
            for s in sorted(sources, key=lambda x: x.get("credibility", 0), reverse=True)[:20]:
                report.append(f"- [{s.get('title', 'Untitled')}]({s.get('url', '')}) (credibility: {s.get('credibility', 0):.1f})")
            report.append("")

        # Research Journal (last 10 entries)
        if journal:
            report.append("## Research Journal (Recent)\n")
            for j in journal[:10]:
                findings = json.loads(j.get("important_findings", "[]"))
                report.append(f"### Cycle {j.get('cycle_number', '?')} - {j.get('timestamp', '')}")
                report.append(f"**Question:** {j.get('research_question', '')}")
                if findings:
                    report.append(f"**Findings:**")
                    for f in findings:
                        report.append(f"  - {f}")
                report.append("")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))

        logger.info(f"Report -> {path}")
        return path

    def _export_knowledge_graph(self, path: str) -> str:
        """Export knowledge graph as JSON."""
        nodes = self.db.get_knowledge_nodes(limit=500)
        all_edges = []
        for node in nodes[:100]:
            edges = self.db.get_edges_for_node(node["id"])
            all_edges.extend(edges)

        graph = {
            "nodes": nodes,
            "edges": all_edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(all_edges),
                "exported": datetime.utcnow().isoformat(),
            }
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        logger.info(f"Knowledge graph: {len(nodes)} nodes, {len(all_edges)} edges -> {path}")
        return path

    def export_for_finetuning(self, output_path: str = "data/dataset/finetune.jsonl") -> str:
        """
        Export dataset specifically formatted for LLM fine-tuning.
        Creates instruction-following pairs from all accumulated knowledge.
        Includes debate pairs (thesis -> counterargument -> refutation).
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        records = []

        # Enhanced system prompt for the specialized model
        system_prompt = (
            "You are a world-class genetics researcher and transhumanist bioethicist "
            "specializing in eugenics, embryo selection, IQ optimization, and hereditary "
            "disease elimination. You provide evidence-based, scientifically rigorous "
            "analysis while acknowledging ethical considerations, limitations, and "
            "uncertainties. You can argue both sides of any genetic enhancement debate."
        )

        # === CATEGORY 1: FACTS (knowledge retrieval pairs) ===
        facts = self.db.get_facts(limit=500)
        for fact in facts:
            confidence = fact.get('confidence', 0.5)
            if confidence < 0.5:
                continue  # Skip low-confidence facts
            records.append({
                "category": "facts",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"What does the scientific evidence say about: {fact.get('topic', 'this topic')}?"},
                    {"role": "assistant", "content": f"Based on peer-reviewed research: {fact.get('content', '')}\n\nConfidence: {confidence:.0%}. This finding is supported by {len(json.loads(fact.get('source_ids', '[]')))} sources."},
                ]
            })

        # === CATEGORY 2: HYPOTHESIS EVALUATIONS (analytical pairs) ===
        hypotheses = self.db.get_hypotheses(limit=500)
        for hyp in hypotheses:
            if hyp.get("status") in ("supported", "confirmed", "contested"):
                supporting = json.loads(hyp.get("supporting_evidence", "[]"))
                contra = json.loads(hyp.get("contradicting_evidence", "[]"))
                alternatives = json.loads(hyp.get("alternative_explanations", "[]"))
                predictions = json.loads(hyp.get("predictions", "[]"))

                # Build rich response
                response_parts = [
                    f"## Hypothesis Analysis\n",
                    f"**Claim:** {hyp.get('claim', '')}",
                    f"**Status:** {hyp.get('status', '')} | **Confidence:** {hyp.get('confidence', 0):.0%}\n",
                ]
                if supporting:
                    response_parts.append(f"**Supporting Evidence ({len(supporting)} items):**")
                    for s in supporting[:3]:
                        if isinstance(s, str):
                            response_parts.append(f"- {s}")
                if contra:
                    response_parts.append(f"\n**Contradicting Evidence ({len(contra)} items):**")
                    for c in contra[:3]:
                        if isinstance(c, str):
                            response_parts.append(f"- {c}")
                if alternatives:
                    response_parts.append(f"\n**Alternative Explanations:**")
                    for a in alternatives:
                        response_parts.append(f"- {a}")
                if predictions:
                    response_parts.append(f"\n**Testable Predictions:**")
                    for p in predictions:
                        response_parts.append(f"- {p}")
                if hyp.get("falsification_conditions"):
                    response_parts.append(f"\n**Falsification Conditions:** {hyp.get('falsification_conditions')}")

                records.append({
                    "category": "hypothesis_evaluations",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Provide a thorough analysis of this hypothesis: {hyp.get('claim', '')}"},
                        {"role": "assistant", "content": "\n".join(response_parts)},
                    ]
                })

        # === CATEGORY 3: DEBATE PAIRS (thesis -> counterargument -> refutation) ===
        # Generate debate pairs for ALL hypotheses with any evidence
        for hyp in hypotheses:
            contra = json.loads(hyp.get("contradicting_evidence", "[]") or '[]')
            supporting = json.loads(hyp.get("supporting_evidence", "[]") or '[]')
            alternatives = json.loads(hyp.get("alternative_explanations", "[]") or '[]')

            # Collect counter-arguments from any available source
            counter_args = []
            if contra:
                counter_args.extend([c for c in contra if isinstance(c, str)])
            if alternatives:
                counter_args.extend([a for a in alternatives if isinstance(a, str)])

            # Skip only if truly no evidence at all
            if not supporting and not counter_args:
                continue

            claim = hyp.get('claim', '')
            confidence = hyp.get('confidence', 0)
            status = hyp.get('status', 'active')

            # Build debate response
            debate_response = [
                f"## Critical Analysis: {claim[:120]}\n",
                f"### Thesis (Confidence: {confidence:.0%}, Status: {status}):\n",
                f"{claim}\n",
            ]

            # Arguments against
            if counter_args:
                debate_response.append(f"### Strongest Counter-Arguments:\n")
                for i, arg in enumerate(counter_args[:5], 1):
                    if isinstance(arg, str) and len(arg) > 10:
                        debate_response.append(f"{i}. {arg}")
            else:
                # Generate generic counter-arguments based on hypothesis content
                generic_counters = []
                claim_lower = claim.lower()
                if 'heritability' in claim_lower or 'genetic' in claim_lower:
                    generic_counters.append("Heritability estimates are population-specific and may not generalize across environments or populations.")
                if 'iq' in claim_lower or 'intelligence' in claim_lower or 'cognitive' in claim_lower:
                    generic_counters.append("IQ measures capture only a narrow slice of cognitive ability and may not reflect real-world outcomes.")
                if 'embryo' in claim_lower or 'selection' in claim_lower or 'pgt' in claim_lower:
                    generic_counters.append("Long-term health and cognitive outcomes of embryo selection remain understudied; current data is limited.")
                if 'flynn' in claim_lower:
                    generic_counters.append("The Flynn Effect plateau may reflect measurement artifacts or socioeconomic stagnation rather than exhausted environmental potential.")
                if 'wilson' in claim_lower:
                    generic_counters.append("The Wilson Effect may be explained by gene-environment correlation rather than pure genetic causation.")
                if 'polygenic' in claim_lower or 'pgs' in claim_lower or 'gwas' in claim_lower:
                    generic_counters.append("Polygenic scores explain only 10-15% of variance; missing heritability and gene-environment interactions limit predictive power.")
                    generic_counters.append("Population stratification and ascertainment bias in GWAS may inflate apparent genetic effects.")
                if not generic_counters:
                    generic_counters.append("The hypothesis may overstate the strength of available evidence while underestimating alternative explanations.")
                    generic_counters.append("Correlation does not imply causation; confounding variables may explain the observed relationships.")
                debate_response.append(f"### Strongest Counter-Arguments:\n")
                for i, arg in enumerate(generic_counters[:3], 1):
                    debate_response.append(f"{i}. {arg}")

            # Responses / supporting evidence
            if supporting:
                debate_response.append(f"\n### Counter-Counterarguments (Responses):\n")
                debate_response.append(f"Despite these criticisms, the hypothesis maintains {confidence:.0%} confidence because:")
                for s in supporting[:3]:
                    if isinstance(s, str) and len(s) > 10:
                        debate_response.append(f"- {s}")
            else:
                debate_response.append(f"\n### Current Defense:\n")
                debate_response.append(f"The hypothesis maintains {confidence:.0%} confidence based on theoretical plausibility and indirect evidence.")
                debate_response.append(f"Direct empirical support is still accumulating.")

            # Balanced assessment
            debate_response.append(f"\n### Balanced Assessment:")
            debate_response.append(f"The hypothesis remains {status} with {confidence:.0%} confidence.")
            if counter_args:
                debate_response.append(f"Key uncertainty: Are the {len(counter_args)} counter-arguments sufficient to significantly revise confidence?")
            else:
                debate_response.append(f"Key uncertainty: Lack of direct contradicting evidence does not equal strong support.")

            records.append({
                "category": "debate_pairs",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide a rigorous scientific debate on this claim: '{claim[:200]}' — present the strongest arguments for and against, then give your balanced assessment."},
                    {"role": "assistant", "content": "\n".join(debate_response)},
                ]
            })

        # === CATEGORY 4: Q&A PAIRS (answered research questions) ===
        questions = self.db._get_all(
            "research_questions",
            where="status = 'answered' AND answer_summary != ''",
            limit=500,
        )
        for q in questions:
            answer = q.get("answer_summary", "")
            if len(answer) < 20:  # Skip trivial answers
                continue
            records.append({
                "category": "qa_pairs",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": q.get("question", "")},
                    {"role": "assistant", "content": answer},
                ]
            })

        # === CATEGORY 5: ETHICAL DEBATE PAIRS (dynamic, per-hypothesis) ===
        # First: 3 general ethical debates (kept for broad coverage)
        general_ethical = [
            {
                "q": "What are the strongest ethical arguments FOR embryo selection for intelligence?",
                "a": (
                    "## Arguments For Embryo Selection for Intelligence\n\n"
                    "1. **Reproductive Autonomy:** Parents have the right to make informed reproductive choices, "
                    "including selecting embryos with favorable genetic profiles, just as they choose "
                    "education, nutrition, and environment.\n\n"
                    "2. **Harm Reduction:** If selection can reduce risk of hereditary cognitive disabilities "
                    "or increase resilience, it aligns with the medical principle of beneficence.\n\n"
                    "3. **Technological Inevitability:** The technology exists and will be used regardless; "
                    "regulation should focus on safety and equity rather than prohibition.\n\n"
                    "4. **Cognitive Enhancement as Public Good:** Higher average cognitive ability could "
                    "accelerate scientific progress, solve global challenges, and improve human welfare.\n\n"
                    "5. **Existing Precedent:** PGD for medical conditions is widely accepted; "
                    "the distinction between medical and enhancement traits is philosophically arbitrary."
                ),
            },
            {
                "q": "What are the strongest ethical arguments AGAINST embryo selection for intelligence?",
                "a": (
                    "## Arguments Against Embryo Selection for Intelligence\n\n"
                    "1. **Historical Eugenics:** The history of eugenics includes forced sterilization, "
                    "genocide, and systematic oppression. Even voluntary programs risk normalizing "
                    "genetic hierarchies.\n\n"
                    "2. **Genetic Determinism:** Overemphasizing genetics ignores the profound role of "
                    "environment, education, nutrition, and social factors in cognitive development.\n\n"
                    "3. **Inequality Amplification:** Only wealthy families could afford selection, "
                    "creating a genetic underclass and exacerbating existing social inequalities.\n\n"
                    "4. **Consent of the Selected:** Future children cannot consent to being genetically "
                    "selected, raising questions about autonomy and instrumentalization.\n\n"
                    "5. **Diversity Reduction:** Genetic selection could reduce human genetic diversity, "
                    "potentially eliminating valuable traits we don't yet understand.\n\n"
                    "6. **Pleiotropic Risks:** Genes affecting intelligence may have trade-offs with "
                    "mental health, creativity, or other valued traits."
                ),
            },
            {
                "q": "How should society regulate embryo genetic selection?",
                "a": (
                    "## Regulatory Framework Recommendations\n\n"
                    "1. **Medical vs. Enhancement Distinction:** Maintain strict separation between "
                    "medical PGD (disease prevention) and enhancement selection. Current evidence "
                    "supports medical use; enhancement requires more research.\n\n"
                    "2. **Equity Requirements:** If enhancement selection becomes available, public "
                    "funding or insurance coverage should prevent it from being wealth-exclusive.\n\n"
                    "3. **Long-term Monitoring:** Mandate longitudinal studies of children born through "
                    "genetic selection to track health, cognitive, and social outcomes.\n\n"
                    "4. **International Coordination:** Prevent regulatory arbitrage by establishing "
                    "international standards through WHO or similar bodies.\n\n"
                    "5. **Public Deliberation:** Any expansion beyond medical PGD should require "
                    "broad public consultation, not just expert or industry input."
                ),
            },
        ]
        for item in general_ethical:
            records.append({
                "category": "ethical_debates",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": item["q"]},
                    {"role": "assistant", "content": item["a"]},
                ]
            })

        # Dynamic: Generate ethical debate for EACH hypothesis
        for hyp in hypotheses:
            claim = hyp.get('claim', '')
            confidence = hyp.get('confidence', 0)
            claim_lower = claim.lower()

            # Determine ethical dimension based on hypothesis content
            ethical_dimensions = []
            if 'embryo' in claim_lower or 'selection' in claim_lower or 'pgt' in claim_lower or 'pgd' in claim_lower:
                ethical_dimensions.append('embryo_selection')
            if 'ai' in claim_lower or 'childci' in claim_lower or 'machine learning' in claim_lower or 'framework' in claim_lower:
                ethical_dimensions.append('ai_prediction')
            if 'eugenics' in claim_lower or 'historical' in claim_lower:
                ethical_dimensions.append('historical_eugenics')
            if 'intelligence' in claim_lower or 'iq' in claim_lower or 'cognitive' in claim_lower:
                ethical_dimensions.append('cognitive_enhancement')
            if 'polygenic' in claim_lower or 'gwas' in claim_lower or 'snp' in claim_lower or 'score' in claim_lower:
                ethical_dimensions.append('genetic_prediction')
            if 'wilson' in claim_lower or 'flynn' in claim_lower or 'heritability' in claim_lower:
                ethical_dimensions.append('heritability_ethics')
            if 'diversity' in claim_lower or 'trade-off' in claim_lower or 'pleiotrop' in claim_lower:
                ethical_dimensions.append('genetic_diversity')
            if 'regulation' in claim_lower or 'society' in claim_lower or 'public' in claim_lower:
                ethical_dimensions.append('regulation')
            if 'multigenerational' in claim_lower or 'epigenetic' in claim_lower:
                ethical_dimensions.append('multigenerational')

            # Default if no specific dimension matched
            if not ethical_dimensions:
                ethical_dimensions = ['genetic_enhancement']

            # Build ethical debate response
            ethical_response = [
                f"## Ethical Analysis: {claim[:120]}\n",
                f"**Hypothesis Confidence:** {confidence:.0%}\n",
                "### Arguments FOR this research direction:\n",
            ]

            # Pro arguments based on ethical dimensions
            pro_args = []
            if 'embryo_selection' in ethical_dimensions:
                pro_args.append("**Reproductive Freedom:** Parents should have access to information about embryo genetics to make informed choices, including selection for health and cognitive potential.")
                pro_args.append("**Medical Precedent:** PGT-A and PGT-M for disease prevention are already widely accepted; extending to cognitive traits follows the same ethical framework.")
            if 'ai_prediction' in ethical_dimensions:
                pro_args.append("**Scientific Advancement:** AI frameworks can identify patterns invisible to human researchers, accelerating our understanding of cognitive development.")
                pro_args.append("**Personalized Medicine:** Accurate prediction models could enable early intervention for children at risk of cognitive difficulties.")
            if 'cognitive_enhancement' in ethical_dimensions:
                pro_args.append("**Human Potential:** If safe and effective, cognitive enhancement could unlock human potential, accelerate scientific progress, and address global challenges.")
                pro_args.append("**Harm Reduction:** Better understanding of cognitive genetics could reduce hereditary cognitive disabilities.")
            if 'genetic_prediction' in ethical_dimensions:
                pro_args.append("**Informed Decision-Making:** Polygenic scores provide additional information for prospective parents, aligning with principles of informed consent and autonomy.")
                pro_args.append("**Research Value:** Even imperfect prediction models advance our understanding of complex traits.")
            if 'heritability_ethics' in ethical_dimensions:
                pro_args.append("**Scientific Accuracy:** Understanding heritability patterns ensures policies are based on evidence rather than ideological assumptions.")
            if 'genetic_diversity' in ethical_dimensions:
                pro_args.append("**Balanced Trade-offs:** Understanding diversity implications allows for informed policy that balances individual choice with collective genetic health.")
            if 'regulation' in ethical_dimensions:
                pro_args.append("**Evidence-Based Policy:** Scientific findings should inform regulatory frameworks to ensure safe, equitable access.")
            if 'multigenerational' in ethical_dimensions:
                pro_args.append("**Long-term Planning:** Understanding multigenerational effects enables responsible policy development for future generations.")
            if 'historical_eugenics' in ethical_dimensions:
                pro_args.append("**Learning from History:** Modern genetic research with informed consent and voluntary participation is fundamentally different from historical forced eugenics programs.")
            if 'genetic_enhancement' in ethical_dimensions:
                pro_args.append("**Technological Progress:** Responsible development of genetic technologies could improve human welfare while respecting individual rights.")

            if not pro_args:
                pro_args.append("**Scientific Value:** Advancing knowledge in this area contributes to our understanding of human biology and development.")

            for i, arg in enumerate(pro_args[:4], 1):
                ethical_response.append(f"{i}. {arg}")

            ethical_response.append(f"\n### Arguments AGAINST this research direction:\n")

            # Con arguments based on ethical dimensions
            con_args = []
            if 'embryo_selection' in ethical_dimensions:
                con_args.append("**Instrumentalization:** Selecting embryos based on predicted cognitive traits risks treating future children as products to be optimized rather than persons with inherent dignity.")
                con_args.append("**Slippery Slope:** Allowing selection for cognitive traits may lead to selection for other non-medical traits, expanding the scope of genetic modification beyond societal consensus.")
            if 'ai_prediction' in ethical_dimensions:
                con_args.append("**Algorithmic Bias:** AI models trained on specific populations may encode and amplify existing biases, leading to unequal outcomes across racial, ethnic, or socioeconomic groups.")
                con_args.append("**Overreliance on Technology:** Delegating cognitive prediction to AI systems risks reducing complex human development to algorithmic scores.")
            if 'cognitive_enhancement' in ethical_dimensions:
                con_args.append("**Inequality Amplification:** If expensive, cognitive enhancement could create a genetic underclass, exacerbating existing social inequalities.")
                con_args.append("**Diversity Reduction:** Genetic selection for specific cognitive profiles may reduce human cognitive diversity, potentially eliminating valuable traits.")
            if 'genetic_prediction' in ethical_dimensions:
                con_args.append("**Premature Application:** Polygenic scores explain only 10-15% of variance; applying them clinically may give false confidence in predictions.")
                con_args.append("**Population Specificity:** Scores developed in one population may not predict well in others, leading to health disparities.")
            if 'heritability_ethics' in ethical_dimensions:
                con_args.append("**Genetic Determinism:** Emphasizing heritability may lead to deterministic thinking that ignores the profound role of environment, education, and social factors.")
            if 'genetic_diversity' in ethical_dimensions:
                con_args.append("**Irreversible Consequences:** Reducing genetic diversity could have unforeseen long-term consequences that cannot be undone.")
            if 'regulation' in ethical_dimensions:
                con_args.append("**Regulatory Lag:** Technology advances faster than regulation, creating gaps that may be exploited before adequate safeguards are in place.")
            if 'multigenerational' in ethical_dimensions:
                con_args.append("**Unknown Long-term Effects:** Epigenetic and multigenerational effects of genetic selection are poorly understood, risking unforeseen consequences.")
            if 'historical_eugenics' in ethical_dimensions:
                con_args.append("**Historical Precedent:** The eugenics movement led to forced sterilization, genocide, and systematic oppression; even voluntary programs risk normalizing genetic hierarchies.")
            if 'genetic_enhancement' in ethical_dimensions:
                con_args.append("**Consent of the Unborn:** Future children cannot consent to being genetically modified, raising fundamental questions about autonomy.")

            if not con_args:
                con_args.append("**Unintended Consequences:** Rapid technological advancement without adequate ethical review may lead to unforeseen harms.")

            for i, arg in enumerate(con_args[:4], 1):
                ethical_response.append(f"{i}. {arg}")

            # Balanced ethical assessment
            ethical_response.append(f"\n### Balanced Ethical Assessment:\n")
            ethical_response.append(f"This research ({confidence:.0%} confidence) sits at the intersection of scientific progress and ethical responsibility. "
                                  f"Key tension: How do we advance knowledge while protecting individual rights, ensuring equity, and preventing historical mistakes from being repeated?")
            ethical_response.append(f"\n**Recommended safeguards:**")
            ethical_response.append(f"- Maintain strict separation between medical and enhancement applications")
            ethical_response.append(f"- Require diverse, representative study populations")
            ethical_response.append(f"- Establish independent ethical oversight boards")
            ethical_response.append(f"- Ensure equitable access if applications become available")
            ethical_response.append(f"- Mandate long-term follow-up studies for any interventions")

            records.append({
                "category": "ethical_debates",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Provide a comprehensive ethical analysis of this research claim: '{claim[:200]}'. Present balanced arguments for and against, identify key ethical tensions, and recommend safeguards."},
                    {"role": "assistant", "content": "\n".join(ethical_response)},
                ]
            })

        # === CATEGORY 6: EVIDENCE SYNTHESIS PAIRS ===
        # For each hypothesis with evidence, create a synthesis pair
        for hyp in hypotheses:
            evidence_records = self.db.get_evidence_for_hypothesis(hyp["id"])
            if len(evidence_records) < 2:
                continue

            evidence_summary = []
            for ev in evidence_records[:10]:
                ev_type = ev.get("evidence_type", "unknown")
                strength = ev.get("strength", 0.5)
                content = ev.get("content", "")[:200]
                evidence_summary.append(f"[{ev_type}] (strength: {strength:.0%}): {content}")

            records.append({
                "category": "evidence_synthesis",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Synthesize all available evidence for or against: {hyp.get('claim', '')[:150]}. Consider the strength and type of each piece of evidence."},
                    {"role": "assistant", "content": (
                        f"## Evidence Synthesis\n\n"
                        f"**Hypothesis:** {hyp.get('claim', '')}\n"
                        f"**Current Confidence:** {hyp.get('confidence', 0):.0%} ({hyp.get('status', 'proposed')})\n\n"
                        f"**Evidence inventory ({len(evidence_records)} pieces):**\n"
                        + "\n".join(evidence_summary)
                        + f"\n\n**Synthesis:** Based on {len(evidence_records)} pieces of evidence, "
                        f"the hypothesis maintains {hyp.get('confidence', 0):.0%} confidence. "
                        f"The evidence base is {'strong' if len(evidence_records) > 5 else 'developing'}. "
                        f"Key uncertainty remains around: {'; '.join(json.loads(hyp.get('alternative_explanations', '[]'))[:2]) or 'methodological limitations'}"
                    )},
                ]
            })

        # === CATEGORY 7: CHAIN-OF-THOUGHT PAIRS (reasoning training) ===
        cot_pairs = [
            {
                "q": "Analyze whether heritability of IQ increases with age (Wilson Effect). Show your reasoning.",
                "a": (
                    "Let me think through this step by step:\n\n"
                    "**Step 1: What is the hypothesis claiming?**\n"
                    "The Wilson Effect claims that heritability of IQ increases from childhood (~40%) to adulthood (~80%).\n\n"
                    "**Step 2: What evidence supports this?**\n"
                    "- Twin studies show MZ twins become more similar in IQ as they age\n"
                    "- DZ twins become less similar with age\n"
                    "- Heritability estimates increase from ~0.4 in childhood to ~0.8 in adulthood\n"
                    "- Multiple longitudinal studies confirm this pattern\n\n"
                    "**Step 3: What are the mechanistic explanations?**\n"
                    "- Gene-environment correlation increases with age\n"
                    "- People select environments matching their genetic predispositions\n"
                    "- Shared environmental influences diminish after leaving home\n"
                    "- Genetic effects accumulate through active gene-environment correlation\n\n"
                    "**Step 4: What are the counterarguments?**\n"
                    "- Equal environments assumption in twin studies may be violated\n"
                    "- Gene-environment interaction could explain the pattern\n"
                    "- Selection effects in longitudinal studies\n\n"
                    "**Step 5: What is my conclusion?**\n"
                    "The Wilson Effect is well-supported by multiple independent studies. The evidence is STRONG for the claim that heritability increases with age.\n\n"
                    "**Classification: SUPPORTS the hypothesis** (strength: 0.85)"
                ),
            },
            {
                "q": "Evaluate this evidence: 'A study found no significant difference in IQ between children conceived via IVF and naturally conceived children.' Does this support or contradict the hypothesis that embryo selection improves cognitive outcomes?",
                "a": (
                    "Let me analyze this evidence step by step:\n\n"
                    "**Step 1: What is the hypothesis claiming?**\n"
                    "Embryo selection (like PGT-A) improves cognitive outcomes in children.\n\n"
                    "**Step 2: What does the evidence actually say?**\n"
                    "The study found NO significant IQ difference between IVF and naturally conceived children.\n\n"
                    "**Step 3: Does this support the hypothesis?**\n"
                    "Not directly. The hypothesis is about SELECTIVE embryo selection, not just IVF in general.\n\n"
                    "**Step 4: Does this contradict the hypothesis?**\n"
                    "Partially. It suggests IVF itself doesn't improve IQ, but doesn't test SELECTIVE selection.\n\n"
                    "**Step 5: What is the overall relationship?**\n"
                    "This evidence is NEUTRAL to the specific hypothesis about embryo selection. It addresses a related but different question (IVF vs natural conception, not selected vs unselected embryos).\n\n"
                    "**Classification: NEUTRAL** (strength: 0.4) - The evidence is about IVF in general, not selective embryo selection."
                ),
            },
            {
                "q": "A meta-analysis of 50 studies shows polygenic scores explain only 10-15% of IQ variance. Analyze this evidence step by step.",
                "a": (
                    "Let me analyze this evidence step by step:\n\n"
                    "**Step 1: What is the evidence?**\n"
                    "Meta-analysis of 50 studies: PGS explains 10-15% of IQ variance.\n\n"
                    "**Step 2: How strong is this evidence?**\n"
                    "Very strong - meta-analyses are the gold standard. 50 studies provide robust evidence.\n\n"
                    "**Step 3: Does this support or contradict the hypothesis that PGS can predict intelligence?**\n"
                    "It PARTIALLY supports - PGS DOES predict IQ, but only explains a small portion.\n"
                    "It PARTIALLY contradicts - the prediction is weaker than many claim.\n\n"
                    "**Step 4: What are the implications?**\n"
                    "- PGS has predictive value but is limited\n"
                    "- 85-90% of variance is NOT captured by current PGS\n"
                    "- Missing heritability remains a major challenge\n"
                    "- Population specificity limits generalizability\n\n"
                    "**Step 5: Classification?**\n"
                    "This is COMPLEX - it supports the EXISTENCE of genetic prediction but contradicts claims that PGS is HIGHLY predictive.\n\n"
                    "**Classification: MIXED** (supports partial prediction, contradicts strong claims)"
                ),
            },
        ]
        for pair in cot_pairs:
            records.append({
                "category": "chain_of_thought",
                "messages": [
                    {"role": "system", "content": system_prompt + "\n\nIMPORTANT: Always show your step-by-step reasoning before giving conclusions."},
                    {"role": "user", "content": pair["q"]},
                    {"role": "assistant", "content": pair["a"]},
                ]
            })

        # Generate CoT pairs for existing hypotheses
        for hyp in hypotheses:
            if hyp.get("status") in ("supported", "contested"):
                supporting = json.loads(hyp.get("supporting_evidence", "[]") or '[]')
                contra = json.loads(hyp.get("contradicting_evidence", "[]") or '[]')
                claim = hyp.get('claim', '')
                confidence = hyp.get('confidence', 0)

                # Build CoT response
                cot_response = [
                    f"Let me analyze this hypothesis step by step:\n\n",
                    f"**Step 1: What is the hypothesis claiming?**\n{claim}\n\n",
                    f"**Step 2: What evidence supports this?**\n",
                ]
                if supporting:
                    for s in supporting[:3]:
                        if isinstance(s, str):
                            cot_response.append(f"- {s}\n")
                else:
                    cot_response.append("- (No direct supporting evidence found)\n")

                cot_response.append(f"\n**Step 3: What evidence contradicts this?**\n")
                if contra:
                    for c in contra[:3]:
                        if isinstance(c, str):
                            cot_response.append(f"- {c}\n")
                else:
                    cot_response.append("- (No direct contradicting evidence found)\n")

                cot_response.append(f"\n**Step 4: What are the key uncertainties?**\n")
                alternatives = json.loads(hyp.get("alternative_explanations", "[]") or '[]')
                if alternatives:
                    for a in alternatives[:2]:
                        if isinstance(a, str):
                            cot_response.append(f"- {a}\n")
                else:
                    cot_response.append("- Alternative explanations not yet explored\n")

                cot_response.append(f"\n**Step 5: What is my conclusion?**\n")
                cot_response.append(f"Based on {len(supporting)} supporting and {len(contra)} contradicting evidence items, ")
                cot_response.append(f"the hypothesis has {confidence:.0%} confidence. ")
                if confidence > 0.6:
                    cot_response.append("The evidence generally supports this hypothesis, though uncertainties remain.")
                elif confidence > 0.4:
                    cot_response.append("The evidence is mixed, with roughly equal support and contradiction.")
                else:
                    cot_response.append("The evidence currently does not strongly support this hypothesis.")

                records.append({
                    "category": "chain_of_thought",
                    "messages": [
                        {"role": "system", "content": system_prompt + "\n\nIMPORTANT: Always show your step-by-step reasoning before giving conclusions."},
                        {"role": "user", "content": f"Analyze this hypothesis step by step: {claim}"},
                        {"role": "assistant", "content": "".join(cot_response)},
                    ]
                })

        # === CATEGORY 8: SELF-CONSISTENCY PAIRS (multiple valid perspectives) ===
        sc_pairs = [
            {
                "q": "What is the most likely outcome of embryo selection for intelligence over the next 20 years?",
                "perspectives": [
                    {
                        "label": "Optimistic View",
                        "reasoning": "Based on rapid advances in polygenic scoring (PGS accuracy improving ~2% per year), decreasing IVF costs, and growing acceptance in countries like Israel and Denmark, embryo selection for cognitive traits could become mainstream within 15-20 years. The theoretical IQ gain of 3-7 points per generation is meaningful.",
                        "conclusion": "Mainstream adoption by 2045 with significant cognitive gains in early-adopter populations."
                    },
                    {
                        "label": "Conservative View",
                        "reasoning": "Regulatory barriers, ethical concerns, and the limitation of PGS to only 10-15% variance explained suggest slow progress. Most countries will restrict enhancement applications. The technology exists but societal adoption will be minimal.",
                        "conclusion": "Limited adoption in a few permissive countries; most of the world maintains restrictions."
                    },
                    {
                        "label": "Technical View",
                        "reasoning": "The key bottleneck is PGS accuracy, not the selection technology itself. Current PGS explains 10-15% of IQ variance. For meaningful selection, we need 30%+. This requires GWAS sample sizes of millions, which won't be available until ~2035. Then clinical validation takes another 10 years.",
                        "conclusion": "Technically feasible by 2045-2050, but clinical adoption depends on validation studies."
                    },
                ],
                "synthesis": "All three perspectives agree on the technical timeline (2045-2050) but differ on adoption speed. The most balanced prediction: limited adoption in 2-3 permissive countries by 2035, broader availability by 2050, pending regulatory and ethical resolution."
            },
            {
                "q": "Is the Wilson Effect evidence for genetic determinism?",
                "perspectives": [
                    {
                        "label": "Pro-Genetic View",
                        "reasoning": "The Wilson Effect shows heritability increases from 40% to 80% with age. This means genetic factors become increasingly dominant as environmental constraints relax. If anything, the environment plays a DECREASING role over time.",
                        "conclusion": "Supports the primacy of genetics in determining cognitive outcomes."
                    },
                    {
                        "label": "Pro-Environmental View",
                        "reasoning": "The Wilson Effect actually shows GENE-ENVIRONMENT CORRELATION, not genetic determinism. People actively select environments that match their genetic predispositions. The environment is still crucial - it's just that people choose their own environments based on genetic tendencies.",
                        "conclusion": "Demonstrates gene-environment interplay, not genetic determinism."
                    },
                    {
                        "label": "Methodological View",
 "reasoning": "The Wilson Effect relies on twin studies which assume equal environments for MZ and DZ twins. If this assumption is violated (MZ twins treated more similarly), heritability estimates are inflated. The 'true' heritability increase may be smaller than reported.",
                        "conclusion": "The effect size may be overestimated due to methodological limitations."
                    },
                ],
                "synthesis": "The Wilson Effect does NOT support genetic determinism - it demonstrates gene-environment correlation. However, it does show that genetic factors become increasingly important over the lifespan, which has implications for intervention timing and strategy."
            },
        ]
        for pair in sc_pairs:
            # Create one record per perspective
            for perspective in pair["perspectives"]:
                records.append({
                    "category": "self_consistency",
                    "messages": [
                        {"role": "system", "content": system_prompt + "\n\nYou will be asked to provide ONE perspective on a question. Present a clear, well-reasoned argument from that specific viewpoint."},
                        {"role": "user", "content": f"Question: {pair['q']}\n\nProvide your answer from the {perspective['label']} perspective."},
                        {"role": "assistant", "content": f"**{perspective['label']}:**\n\n{perspective['reasoning']}\n\n**Conclusion:** {perspective['conclusion']}"},
                    ]
                })
            # Create synthesis record
            records.append({
                "category": "self_consistency",
                "messages": [
                    {"role": "system", "content": system_prompt + "\n\nYou will be given multiple perspectives on a question. Synthesize them into a balanced conclusion."},
                    {"role": "user", "content": f"Question: {pair['q']}\n\nPerspectives:\n" + "\n".join(f"- {p['label']}: {p['conclusion']}" for p in pair['perspectives']) + f"\n\nSynthesize these perspectives into a balanced conclusion."},
                    {"role": "assistant", "content": pair["synthesis"]},
                ]
            })

        # === CATEGORY 9: EXTENDED CONCEPT EXPLANATION PAIRS ===
        concept_pairs = [
            {
                "q": "Explain the Wilson Effect and its significance for intelligence research.",
                "a": (
                    "The Wilson Effect describes how the heritability of IQ increases from approximately "
                    "40% in childhood to 80% in adulthood. This occurs because: (1) As individuals mature, "
                    "they increasingly select and modify their own environments based on genetic predispositions "
                    "(gene-environment correlation); (2) Shared environmental influences diminish as people leave "
                    "the family home; (3) Genetic effects accumulate through active gene-environment correlation. "
                    "Significance: It suggests that genetic factors become increasingly dominant in determining "
                    "cognitive ability over the lifespan, supporting the case for genetic approaches to "
                    "cognitive enhancement. However, critics note this does not mean intelligence is "
                    "immutable - it means the genetic contribution becomes more expressed as environmental "
                    "constraints relax."
                ),
            },
            {
                "q": "What are polygenic scores and how do they relate to embryo selection?",
                "a": (
                    "Polygenic scores (PGS) aggregate the effects of thousands of genetic variants (SNPs) "
                    "across the genome into a single score that predicts a trait. For intelligence: (1) GWAS "
                    "studies have identified hundreds of loci associated with cognitive ability; (2) Current PGS "
                    "for education/IQ explain about 10-15% of variance in independent samples; (3) For embryo "
                    "selection, PGS allow ranking of embryos by predicted cognitive potential. Limitations: "
                    "Population specificity (PGS trained on Europeans may not predict well in other groups), "
                    "missing heritability, gene-environment interactions, and the small effect sizes of "
                    "individual variants. The theoretical IQ gain from selecting the best embryo from a batch "
                    "of 10 is estimated at 3-7 IQ points per generation."
                ),
            },
            {
                "q": "What is PGT-A and PGT-M and how are they used in embryo selection?",
                "a": (
                    "PGT-A (Preimplantation Genetic Testing for Aneuploidy) screens embryos for chromosomal "
                    "abnormalities (too many or too few chromosomes), which are a major cause of implantation "
                    "failure and miscarriage. PGT-M (for Monogenic disorders) tests for specific single-gene "
                    "diseases like cystic fibrosis, Huntington's, or BRCA mutations. Current usage: (1) PGT-A "
                    "is widely used in IVF to improve pregnancy rates; (2) PGT-M is used when parents carry "
                    "known genetic mutations; (3) Neither currently screens for intelligence-related genes, "
                    "though the technology could theoretically be extended. The cognitive and health outcomes "
                    "of children born through PGT-A/PGT-M appear comparable to naturally conceived children "
                    "in available studies, though long-term data is limited."
                ),
            },
            {
                "q": "Explain the Flynn Effect and its implications for genetic vs environmental influences on IQ.",
                "a": (
                    "The Flynn Effect refers to the observed increase in IQ scores over generations - "
                    "approximately 3 points per decade in developed countries during the 20th century. This "
                    "dramatic improvement occurred too quickly to be genetic, demonstrating that environmental "
                    "factors (better nutrition, education, healthcare, reduced disease burden) can substantially "
                    "raise population IQ. However, the Flynn Effect has plateaued or reversed in some "
                    "developed nations since the 1990s, which transhumanists argue suggests: (1) Environmental "
                    "optimization has reached its limits; (2) Further IQ gains may require genetic approaches; "
                    "(3) The genetic component, now relatively more important, becomes the frontier for "
                    "enhancement. Critics counter that the plateau may reflect measurement artifacts, "
                    "socioeconomic stagnation, or that new environmental interventions (digital technology, "
                    "better pedagogy) could produce further gains."
                ),
            },
        ]
        for pair in concept_pairs:
            records.append({
                "category": "concept_explanations",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": pair["q"]},
                    {"role": "assistant", "content": pair["a"]},
                ]
            })

        with open(output_path, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

        # Count by category for logging
        _cat_counts = Counter(r.get('category', 'unknown') for r in records)
        logger.info(f"Fine-tuning dataset: {len(records)} records -> {output_path}")
        for _cat, _cnt in _cat_counts.most_common():
            logger.info(f"  {_cat}: {_cnt}")
        return output_path
