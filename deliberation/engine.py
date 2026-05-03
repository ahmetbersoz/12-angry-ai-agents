"""Core deliberation engine — creates the AutoGen team and streams messages."""

from __future__ import annotations

from typing import AsyncGenerator

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, ExternalTermination
from autogen_agentchat.messages import BaseAgentEvent, BaseChatMessage, TextMessage, ChatMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.base import TaskResult, ChatAgent, Response
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken

from agents.juror_factory import create_all_jurors
from agents.juror_personas import JUROR_PERSONAS
from evidence.knowledge_base import get_evidence_context
from config import Config, GENERIC_MODEL_INFO, OPENROUTER_DEFAULT_BASE_URL
from deliberation.speaker_selection import create_selector_func
from deliberation.vote_tracker import VoteTracker

# ---------------------------------------------------------------------------
# Custom selector prompt — tells the LLM how to pick the next speaker
# ---------------------------------------------------------------------------

SELECTOR_PROMPT = """\
You are the invisible moderator of a heated jury deliberation room.
The following jurors are present:
{roles}

Read the conversation above carefully and select the NEXT juror to speak.

Guidelines for selection:
1. Pick someone who would naturally REACT to the last statement — agreement, \
disagreement, outrage, or support.
2. If Juror_3 just attacked someone, let the target respond or let Juror_8 \
calmly counter.
3. Allow heated back-and-forth exchanges (2-3 turns) before letting someone \
new jump in.
4. If someone has been quiet for a while, give them a chance — especially \
Juror_9 or Juror_5 who have important observations.
5. Don't let Juror_7 dominate — he mostly complains about wanting to leave.
6. Let Juror_1 (Foreman) intervene when things get chaotic to restore order.
7. After a vote round, let Juror_8 or Juror_3 react first to the results.

Return ONLY the name of the next juror (e.g., "Juror_8"). Nothing else.
"""

# ---------------------------------------------------------------------------
# Opening task message — sets the scene exactly as the movie begins
# ---------------------------------------------------------------------------

OPENING_TASK = """\
The jury files into the hot, cramped deliberation room. It's a sweltering \
summer afternoon in New York City. The fan on the wall is broken. The windows \
barely open. You've all just sat through six grueling days of testimony in a \
first-degree murder trial.

An 18-year-old boy from a slum neighborhood stands accused of stabbing his \
father to death with a switchblade knife. Two eyewitnesses — an old man \
living downstairs and a woman across the el-train tracks — have testified \
against him. A shopkeeper identified the murder weapon as a knife he sold \
the boy. The boy claims he was at the movies but cannot name the films.

The judge has told you: the verdict must be UNANIMOUS. If you find the \
defendant guilty, the sentence is mandatory death by electric chair.

A man's life is in your hands.

Foreman — please organize the room, explain the procedure, and initiate the first round of voting and discussion.
"""


class DeliberationEngine:
    """Orchestrates the 12-agent jury deliberation."""

    def __init__(self, config: Config, ablation_mode: str = "baseline") -> None:
        self.config = config
        self.ablation_mode = ablation_mode
        self.model_client: OpenAIChatCompletionClient | None = None
        self.juror_agents: list = []
        self.team: SelectorGroupChat | None = None
        self.vote_tracker = VoteTracker()
        self.is_running = False
        self.external_termination = ExternalTermination()

    async def initialize(self) -> None:
        """Create model client, agents, and the group chat team."""
        provider = self.config.provider

        if provider == "openrouter":
            api_key = self.config.openrouter_api_key
            base_url = self.config.base_url or OPENROUTER_DEFAULT_BASE_URL
        elif provider == "ollama":
            api_key = self.config.api_key or "ollama"
            base_url = self.config.base_url
        else:
            api_key = self.config.api_key
            base_url = self.config.base_url

        client_kwargs: dict = {
            "model": self.config.model_name,
            "api_key": api_key,
            "temperature": self.config.temperature,
        }
        if base_url:
            client_kwargs["base_url"] = base_url

        if provider in ("ollama", "openrouter"):
            client_kwargs["model_info"] = GENERIC_MODEL_INFO

        self.model_client = OpenAIChatCompletionClient(**client_kwargs)
        self.juror_agents = create_all_jurors(self.model_client, self.ablation_mode)

        # Seed vote tracker with initial votes from personas
        # (skip for no_initial_vote ablation — votes are unknown at start)
        if self.ablation_mode != "no_initial_vote":
            for persona in JUROR_PERSONAS:
                self.vote_tracker.record_vote(persona["name"], persona["initial_vote"])

        # Build selector func for periodic vote rounds
        selector_func = create_selector_func(
            self.juror_agents,
            self.vote_tracker,
            self.config.turns_between_votes,
        )

        # Termination: unanimous verdict OR max messages
        max_term = MaxMessageTermination(self.config.max_turns)
        termination = max_term | self.external_termination

        self.team = SelectorGroupChat(
            participants=self.juror_agents,
            model_client=self.model_client,
            termination_condition=termination,
            selector_prompt=SELECTOR_PROMPT,
            selector_func=selector_func,
            allow_repeated_speaker=False,
        )

    async def run(self) -> AsyncGenerator[dict, None]:
        """Stream deliberation messages as they occur.

        Yields dicts of the form:
            {"type": "message", "source": str, "content": str}
            {"type": "vote_round", "round": int, "tally": (int, int)}
        """
        if self.team is None:
            raise RuntimeError("Call initialize() first")

        self.is_running = True
        vote_round_jurors: set[str] = set()
        
        evidence = get_evidence_context()
        opening_task_with_evidence = OPENING_TASK + "\n\n══════════════════════════════════════\nCASE EVIDENCE\n══════════════════════════════════════\n" + evidence

        async for event in self.team.run_stream(task=opening_task_with_evidence):
            if isinstance(event, TaskResult):
                # Take final snapshot
                if self.vote_tracker.current_votes:
                    self.vote_tracker.take_snapshot()
                self.is_running = False
                yield {"type": "result", "data": event}
                return

            # Extract content from various message types
            content = ""
            source = ""
            if hasattr(event, "content") and hasattr(event, "source"):
                content = str(event.content) if event.content else ""
                source = str(event.source) if event.source else ""

            if not content or not source:
                continue

            # Check for votes in the message
            vote = self.vote_tracker.parse_vote(content)
            if vote and source:
                self.vote_tracker.record_vote(source, vote)
                vote_round_jurors.add(source)

                # If all 12 jurors have voted in this round, snapshot
                if len(vote_round_jurors) >= 12:
                    snap = self.vote_tracker.take_snapshot()
                    tally = self.vote_tracker.get_tally()
                    yield {
                        "type": "vote_round",
                        "round": snap.round_num,
                        "tally": tally,
                    }
                    vote_round_jurors.clear()

                    # Check for unanimous verdict
                    if self.vote_tracker.is_unanimous():
                        self.is_running = False

            yield {
                "type": "message",
                "source": source,
                "content": content,
            }

    async def reset(self) -> None:
        """Reset all state for a fresh run."""
        if self.team:
            await self.team.reset()
        self.vote_tracker = VoteTracker()
        if self.ablation_mode != "no_initial_vote":
            for persona in JUROR_PERSONAS:
                self.vote_tracker.record_vote(persona["name"], persona["initial_vote"])
        self.is_running = False
        self.external_termination = ExternalTermination()
