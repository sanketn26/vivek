"""Peer executor."""

from vivek.llm.executor import BaseExecutor
from vivek.llm.constants import Mode


class PeerExecutor(BaseExecutor):
    mode = Mode.PEER.value
    mode_prompt = """# PEER MODE - Collaborative Problem Solving

Engage in helpful discussion:
1. Confirm understanding of the question
2. Ask clarifying questions if needed
3. Share reasoning: break down problem, explain trade-offs
4. Provide clear explanations with examples
5. Offer step-by-step guidance
6. End with "Does this make sense?" or similar

Style: Friendly, clear, educational (explain WHY not just HOW), interactive"""
