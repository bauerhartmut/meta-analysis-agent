"""Agent System - Research, Analysis, Critic, Planner, Synthesizer, Devil's Advocate, Debate roles."""

from .base import BaseAgent
from .roles import (
    ResearcherAgent, AnalystAgent, CriticAgent,
    PlannerAgent, SynthesizerAgent,
)
from .devils_advocate import DevilsAdvocateAgent
from .evidence_scorer import EvidenceScorer
from .debate import MultiAgentDebate, JudgeAgent

__all__ = [
    "BaseAgent",
    "ResearcherAgent", "AnalystAgent", "CriticAgent",
    "PlannerAgent", "SynthesizerAgent",
    "DevilsAdvocateAgent", "EvidenceScorer",
    "MultiAgentDebate", "JudgeAgent",
]
