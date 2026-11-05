"""
Data models for the Research Agent.
All domain objects as dataclasses.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
import json
import uuid


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# === Enums ===

class SourceType(Enum):
    WEB = "web"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    PDF = "pdf"
    WIKIPEDIA = "wikipedia"
    OTHER = "other"


class HypothesisStatus(Enum):
    PROPOSED = "proposed"
    PLAUSIBLE = "plausible"
    SUPPORTED = "supported"
    CONTESTED = "contested"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"


class EvidenceType(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"


class ResearchPhase(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    ANALYZING = "analyzing"
    HYPOTHESIZING = "hypothesizing"
    CRITIQUING = "critiquing"
    SYNTHESIZING = "synthesizing"
    UPDATING = "updating"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


# === Core Models ===

@dataclass
class Source:
    id: str = field(default_factory=gen_id)
    title: str = ""
    author: str = ""
    publication_date: str = ""
    url: str = ""
    # The study identity a forest-plot row and the duplicate check need. Derived
    # from the URL when the provider gives none, so it is never re-derived on read.
    doi: str = ""
    source_type: str = "web"
    content_hash: str = ""
    credibility: float = 0.5  # 0.0 to 1.0
    relevance: float = 0.0
    relevance_scored: int = 0  # 1 once the analyzer has scored relevance
    relevance_unjudgeable: int = 0  # 1 when there was no full text to judge
    summary: str = ""
    key_claims: str = "[]"  # JSON array
    counter_claims: str = "[]"  # JSON array
    evaluated: int = 0  # 1 once the LLM credibility evaluation has run
    date_added: str = field(default_factory=now_iso)
    content: str = ""
    raw_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Fact:
    id: str = field(default_factory=gen_id)
    content: str = ""
    confidence: float = 0.5
    source_ids: str = "[]"  # JSON array of source IDs
    date_added: str = field(default_factory=now_iso)
    last_verified: str = ""
    topic: str = ""
    # The passage the fact was read from, with its position in the stored text:
    # quote_start/quote_end are -1 when the passage could not be found verbatim.
    quote: str = ""
    quote_start: int = -1
    quote_end: int = -1
    quote_exact: int = 0
    source_text_id: str = ""
    section: str = ""
    page: int = -1

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StudyEffect:
    """One effect size read out of one paper, with the sentence it came from.

    A fact says what a paper claims; this says what it measured. Only a row with
    an effect and a precision (``se``, or a confidence interval to derive it
    from) can be pooled, so a missing standard error stays NULL instead of being
    guessed - a made-up precision is worse than a missing row.
    """
    id: str = field(default_factory=gen_id)
    source_id: str = ""
    hypothesis_id: str = ""
    outcome: str = ""  # exactly as read out of the paper
    # The synthesis target this reading belongs to ("cognitive ability"), or ''
    # when it belongs to none. Pooling groups by this; the wording above stays.
    outcome_key: str = ""
    comparison: str = ""
    # smd|g|r|z|or|rr|hr|beta|mean_diff|heritability|other
    effect_type: str = ""
    effect: Optional[float] = None
    se: Optional[float] = None
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    ci_level: float = 0.95  # as reported, never assumed
    n: Optional[int] = None
    events: Optional[int] = None
    design: str = ""
    population: str = ""
    moderators: str = "{}"  # JSON object
    direction: str = ""  # what "higher" means - without it a sign is unreadable
    unit: str = ""
    # Phase 4 (order §7.1): 0 = unadjusted, 1 = adjusted model, -1 = text says
    # nothing. Pooling refuses to mix these states silently (pooling/2).
    adjusted: int = -1
    # Reported follow-up wording, verbatim; '' = single timepoint not stated.
    time_point: str = ""
    # Study-level link (Phase 2); '' = assignment unknown and unclaimed.
    study_id: str = ""
    # Kohorten-Verbindung (Claude-Vorschlag 6): nur gesetzt, wenn der Text
    # die Zuordnung WOERTLICH belegt (z. B. "UK Biobank cohort A"); '' =
    # unbekannt, nie geschätzt. Zeilen mit derselben kohort_id sind
    # abhängige Schätzungen, auch wenn sie aus verschiedenen DOIs
    # kommen - das Pooling gruppiert und weist die Abhängigkeit aus,
    # statt die Teilnehmer still doppelt zu zählen.
    cohort_id: str = ""
    quote: str = ""
    quote_start: int = -1
    quote_end: int = -1
    source_text_id: str = ""
    section: str = ""
    page: int = -1
    extractor: str = ""
    extraction_pass: int = 1
    # 1 when the two extraction passes disagree; disputed rows are never pooled.
    disputed: int = 0
    rejection_reason: str = ""
    # Evidenzart (Sprint 30): "text_verbatim" = aus dem Textlayer gelsesen,
    # quote/quote_start verifizieren gegen den gespeicherten Text.
    # "vision_read" = aus der gerasterten PDF-Seite doppelgelesen; quote ist
    # dann der Zellstring, quote_start bleibt -1. Pooling nimmt eine
    # vision_read-Zeile nur bei vision_status == "verified" an.
    evidence_kind: str = "text_verbatim"
    # verified | disputed - nur gefuellt bei evidence_kind == "vision_read".
    vision_status: str = ""
    # Belegkette der Bildlesung (JSON): pdf_hash, crop_hash, page, dpi, model,
    # prompt_version, beide Rohlesungen. Kein Feld in vision_meta wird je
    # dazu benutzt, die Zahlen selbst zu pruefen: die Zahlen selbst laufen
    # nur verglichen, nie gemittelt.
    vision_meta: str = "{}"
    created_at: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Claim:
    id: str = field(default_factory=gen_id)
    content: str = ""
    source_id: str = ""
    claim_type: str = "observation"  # observation, conclusion, hypothesis
    confidence: float = 0.5
    supporting_source_ids: str = "[]"
    contradicting_source_ids: str = "[]"
    date_added: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Hypothesis:
    id: str = field(default_factory=gen_id)
    claim: str = ""
    status: str = "proposed"
    confidence: float = 0.3
    supporting_evidence: str = "[]"
    contradicting_evidence: str = "[]"
    alternative_explanations: str = "[]"
    predictions: str = "[]"
    falsification_conditions: str = "[]"
    date_added: str = field(default_factory=now_iso)
    last_updated: str = field(default_factory=now_iso)
    rejection_reason: str = ""
    topic: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Evidence:
    id: str = field(default_factory=gen_id)
    hypothesis_id: str = ""
    source_id: str = ""
    evidence_type: str = "supports"
    content: str = ""
    strength: float = 0.5
    date_added: str = field(default_factory=now_iso)
    # Where a simulated experiment's evidence comes from. A critique or a paper
    # has no experiment, so empty is the normal value.
    experiment_id: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResearchQuestion:
    id: str = field(default_factory=gen_id)
    question: str = ""
    importance: float = 0.5
    uncertainty: float = 0.5
    information_gain: float = 0.5
    researchability: float = 0.5
    novelty: float = 0.5
    contradiction_level: float = 0.0
    status: str = "open"  # open, in_progress, answered, abandoned
    parent_question_id: str = ""
    date_added: str = field(default_factory=now_iso)
    date_answered: str = ""
    answer_summary: str = ""
    priority_score: float = 0.0

    def compute_priority(self) -> float:
        """Compute priority score from component factors."""
        self.priority_score = (
            self.importance * 0.25
            + self.uncertainty * 0.20
            + self.information_gain * 0.25
            + self.researchability * 0.10
            + self.novelty * 0.10
            + self.contradiction_level * 0.10
        )
        return self.priority_score

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ResearchSession:
    id: str = field(default_factory=gen_id)
    topic: str = ""
    start_time: str = field(default_factory=now_iso)
    end_time: str = ""
    cycle_count: int = 0
    sources_found: int = 0
    hypotheses_generated: int = 0
    questions_answered: int = 0
    summary: str = ""
    status: str = "active"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class JournalEntry:
    id: str = field(default_factory=gen_id)
    session_id: str = ""
    cycle_number: int = 0
    timestamp: str = field(default_factory=now_iso)
    research_question: str = ""
    why_selected: str = ""
    sources_investigated: str = "[]"
    important_findings: str = "[]"
    contradictions: str = "[]"
    new_hypotheses: str = "[]"
    rejected_hypotheses: str = "[]"
    updated_beliefs: str = "[]"
    next_question: str = ""
    confidence_change: str = ""
    phase: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Contradiction:
    id: str = field(default_factory=gen_id)
    claim_a: str = ""
    source_a_id: str = ""
    claim_b: str = ""
    source_b_id: str = ""
    resolution: str = "unresolved"
    resolution_note: str = ""
    date_added: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class KnowledgeGraphNode:
    id: str = field(default_factory=gen_id)
    node_type: str = ""  # concept, hypothesis, source, question, evidence
    label: str = ""
    content: str = ""
    date_added: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class KnowledgeGraphEdge:
    id: str = field(default_factory=gen_id)
    source_node_id: str = ""
    target_node_id: str = ""
    relation: str = ""  # supports, contradicts, investigates, derives_from, etc.
    weight: float = 1.0
    date_added: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Embedding:
    id: str = field(default_factory=gen_id)
    entity_type: str = ""  # source, fact, hypothesis, question, etc.
    entity_id: str = ""
    embedding: str = "[]"  # JSON array of floats
    text: str = ""
    date_added: str = field(default_factory=now_iso)

    def to_dict(self) -> dict:
        return asdict(self)
