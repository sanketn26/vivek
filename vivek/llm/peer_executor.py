"""Peer executor."""

from vivek.llm.executor import BaseExecutor


class PeerExecutor(BaseExecutor):
    mode = "peer"
    mode_prompt = "Peer Mode: Collaborate, explain thinking, engage in discussion, and help solve problems together."
