"""Custom speaker selection logic for vote rounds."""

from __future__ import annotations

from typing import Sequence

from autogen_agentchat.base import ChatAgent
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage

from deliberation.vote_tracker import VoteTracker


def create_selector_func(
    agents: list[ChatAgent],
    vote_tracker: VoteTracker,
    turns_between_votes: int,
) -> callable:
    """Return a selector_func for SelectorGroupChat.

    Normal turns: return None so the LLM picks the next speaker.
    Every *turns_between_votes* turns: cycle through all 12 jurors for a vote
    round (Juror_1 first so the Foreman calls the vote).
    """
    agent_names = [a.name for a in agents]
    # Sort jurors numerically (Juror_1, Juror_2, ..., Juror_12)
    sorted_names = sorted(agent_names, key=lambda n: int(n.split("_")[1]) if "_" in n else 999)

    vote_queue: list[str] = []

    def selector_func(
        messages: Sequence[BaseAgentEvent | BaseChatMessage],
    ) -> str | None:
        # If the queue is empty, start a new 12-person round starting with Juror_1
        if not vote_queue:
            vote_queue.extend(sorted_names)

        return vote_queue.pop(0)

    return selector_func
