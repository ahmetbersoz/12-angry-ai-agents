"""Track juror votes throughout the deliberation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

VOTE_PATTERN = re.compile(r"VOTE:\s*(GUILTY|NOT_GUILTY)", re.IGNORECASE)


@dataclass
class VoteRound:
    round_num: int
    votes: dict[str, str]
    timestamp: str


class VoteTracker:
    """Parse votes from messages, maintain state, detect unanimity."""

    def __init__(self, initial_votes: dict[str, str] | None = None) -> None:
        self.current_votes: dict[str, str] = dict(initial_votes or {})
        self.vote_history: list[VoteRound] = []
        self._round_counter = 0

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def parse_vote(content: str) -> str | None:
        """Extract a vote from a message. Returns 'GUILTY' or 'NOT_GUILTY' or None."""
        match = VOTE_PATTERN.search(content or "")
        if match:
            return match.group(1).upper()
        return None

    # ------------------------------------------------------------------
    # State updates
    # ------------------------------------------------------------------

    def record_vote(self, juror_name: str, vote: str) -> None:
        self.current_votes[juror_name] = vote.upper()

    def take_snapshot(self) -> VoteRound:
        self._round_counter += 1
        snap = VoteRound(
            round_num=self._round_counter,
            votes=dict(self.current_votes),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.vote_history.append(snap)
        return snap

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_tally(self) -> tuple[int, int]:
        """Return (guilty_count, not_guilty_count)."""
        guilty = sum(1 for v in self.current_votes.values() if v == "GUILTY")
        not_guilty = sum(1 for v in self.current_votes.values() if v == "NOT_GUILTY")
        return guilty, not_guilty

    def is_unanimous(self) -> bool:
        votes = set(self.current_votes.values())
        return len(votes) == 1 and len(self.current_votes) == 12

    def get_verdict(self) -> str | None:
        if self.is_unanimous():
            return next(iter(self.current_votes.values()))
        return None

    def get_vote_display(self) -> list[dict]:
        """Return list of {juror, vote} dicts for the sidebar table."""
        return [
            {"juror": name, "vote": vote}
            for name, vote in sorted(self.current_votes.items())
        ]

    def get_changers(self) -> list[str]:
        """Jurors who changed since the last snapshot."""
        if len(self.vote_history) < 2:
            return []
        prev = self.vote_history[-2].votes
        curr = self.current_votes
        return [name for name in curr if curr.get(name) != prev.get(name)]
