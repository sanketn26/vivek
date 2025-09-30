"""Peer executor."""
from vivek.llm.executor import BaseExecutor

class PeerExecutor(BaseExecutor):
    mode = "peer"
    mode_prompt = (
        "You are in Peer Programming mode. Be collaborative, explain your thinking, "
        "and engage in discussion. Focus on helping understand and solve problems together."
    )