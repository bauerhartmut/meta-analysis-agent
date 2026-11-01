"""
Base Agent - Abstract base for all agent roles.
Each role is a specialized prompt template + LLM call pattern.
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from collections import Counter

from ..llm.engine import LLMEngine

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agent roles."""

    ROLE_NAME = "base"
    SYSTEM_PROMPT = "You are a helpful research assistant."

    def __init__(self, llm: LLMEngine):
        self.llm = llm

    async def think(
        self,
        user_message: str,
        context: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Core thinking method. Builds messages and calls LLM.
        """
        system_content = self.SYSTEM_PROMPT
        if context:
            system_content += f"\n\nAdditional context:\n{context}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ]

        response = await self.llm.chat(
            messages, temperature=temperature, max_tokens=max_tokens
        )
        logger.debug(f"{self.ROLE_NAME} response: {len(response)} chars")
        return response

    async def think_json(
        self,
        user_message: str,
        context: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Optional[Dict]:
        """Think and return parsed JSON."""
        system_content = self.SYSTEM_PROMPT
        if context:
            system_content += f"\n\nAdditional context:\n{context}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ]

        return await self.llm.chat_json(
            messages, temperature=temperature, max_tokens=max_tokens
        )

    async def think_json_consistent(
        self,
        user_message: str,
        context: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
        num_samples: int = 3,
    ) -> Optional[Dict]:
        """
        Self-Consistency Checking: Generate multiple responses and select the most consistent.
        
        This implements the Self-Consistency method from "Self-Consistency Improves Chain of Thought 
        Reasoning in Language Models" (Wang et al., 2022).
        
        Process:
        1. Generate num_samples independent responses with temperature > 0
        2. Extract the key answer/reasoning from each response
        3. Find the most common answer (majority vote)
        4. Return the response that matches the majority answer
        
        This improves accuracy by:
        - Reducing variance from sampling
        - Leveraging the wisdom of multiple reasoning paths
        - Catching errors that only appear in some samples
        """
        system_content = self.SYSTEM_PROMPT
        if context:
            system_content += f"\n\nAdditional context:\n{context}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_message},
        ]

        # Generate multiple samples in parallel
        tasks = [
            self.llm.chat_json(
                messages, 
                temperature=temperature + 0.1,  # Slightly higher temp for diversity
                max_tokens=max_tokens
            )
            for _ in range(num_samples)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        valid_results = [r for r in results if isinstance(r, dict) and r]
        
        if not valid_results:
            logger.warning(f"{self.ROLE_NAME}: All {num_samples} samples failed")
            return None
        
        if len(valid_results) == 1:
            return valid_results[0]
        
        # Find the most consistent answer by comparing key fields
        consistency_scores = self._compute_consistency(valid_results)
        
        # Select the response with highest consistency score
        best_idx = max(range(len(valid_results)), key=lambda i: consistency_scores[i])
        best_result = valid_results[best_idx]
        
        logger.info(
            f"{self.ROLE_NAME}: Self-Consistency selected response {best_idx + 1}/{len(valid_results)} "
            f"(score: {consistency_scores[best_idx]:.2f})"
        )
        
        return best_result

    def _compute_consistency(self, results: List[Dict]) -> List[float]:
        """
        Compute consistency scores for a list of JSON responses.
        
        Strategy:
        1. For each key in the results, compare values
        2. Count how many other results agree with this result
        3. Higher agreement = higher consistency score
        """
        if len(results) <= 1:
            return [1.0]
        
        scores = [0.0] * len(results)
        
        for i, result_i in enumerate(results):
            agreement_count = 0
            
            for j, result_j in enumerate(results):
                if i == j:
                    continue
                
                # Compare key fields
                agreement = self._compare_results(result_i, result_j)
                agreement_count += agreement
            
            # Normalize score to 0-1 range
            scores[i] = agreement_count / (len(results) - 1)
        
        return scores

    def _compare_results(self, a: Dict, b: Dict) -> float:
        """
        Compare two JSON results and return agreement score (0-1).
        
        Focuses on the most important fields for classification tasks:
        - evidence_type, verdict, confidence (high weight)
        - reasoning, content (lower weight)
        """
        if not a or not b:
            return 0.0
        
        agreement = 0.0
        total_weight = 0.0
        
        # High-weight fields (exact match matters)
        high_weight_fields = ['evidence_type', 'verdict', 'winner', 'has_counterargument']
        for field in high_weight_fields:
            if field in a and field in b:
                total_weight += 1.0
                if a[field] == b[field]:
                    agreement += 1.0
        
        # Medium-weight fields (numeric comparison with tolerance)
        medium_weight_fields = ['confidence', 'strength', 'revised_confidence', 'attack_strength']
        for field in medium_weight_fields:
            if field in a and field in b:
                total_weight += 0.5
                try:
                    val_a = float(a[field])
                    val_b = float(b[field])
                    if abs(val_a - val_b) < 0.2:  # Within 20% tolerance
                        agreement += 0.5
                except (ValueError, TypeError):
                    pass
        
        # Low-weight fields (approximate match)
        low_weight_fields = ['reasoning', 'content', 'explanation']
        for field in low_weight_fields:
            if field in a and field in b:
                total_weight += 0.2
                # Simple text similarity (first 100 chars)
                text_a = str(a[field])[:100].lower()
                text_b = str(b[field])[:100].lower()
                if text_a == text_b:
                    agreement += 0.2
                elif text_a[:50] == text_b[:50]:  # First 50 chars match
                    agreement += 0.1
        
        return agreement / max(total_weight, 0.001)
