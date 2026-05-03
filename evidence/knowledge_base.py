"""All case facts and evidence from "12 Angry Men" (1957), structured for agent consumption."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceItem:
    id: str
    name: str
    category: str  # "physical", "testimony", "circumstantial"
    description: str
    prosecution_claim: str


# ---------------------------------------------------------------------------
# Scene setting – injected into every agent's system prompt
# ---------------------------------------------------------------------------

SCENE_SETTING = (
    "It is a sweltering summer afternoon in New York City. The jury room is "
    "stifling — the fan on the wall is broken and the windows barely open. "
    "You and eleven other jurors have just sat through six days of testimony "
    "in a first-degree murder trial. The judge has instructed you that the "
    "verdict must be unanimous. If you find the defendant guilty, the "
    "sentence is mandatory death by electric chair. A man's life is in your "
    "hands."
)

# ---------------------------------------------------------------------------
# Case summary
# ---------------------------------------------------------------------------

CASE_SUMMARY = (
    "The defendant is an 18-year-old boy from a rough slum neighborhood. He "
    "is charged with the first-degree murder of his father. The prosecution "
    "alleges that on the night of the killing the boy stabbed his father in "
    "the chest with a switchblade knife after a violent argument. The boy "
    "has a prior record of assault, mugging, and knife-fighting. He claims "
    "he was at the movies at the time of the murder, but cannot remember the "
    "names of the films he saw or who starred in them. If found guilty, the "
    "mandatory sentence is death in the electric chair."
)

# ---------------------------------------------------------------------------
# Evidence items – ordered as they are introduced in the film
# ---------------------------------------------------------------------------

EVIDENCE_ITEMS: list[EvidenceItem] = [
    EvidenceItem(
        id="threat",
        name='"I\'ll kill you!" Threat',
        category="testimony",
        description=(
            "Multiple neighbors testified that they heard the boy shout "
            '"I\'m gonna kill you!" at his father during a loud argument '
            "on the night of the murder."
        ),
        prosecution_claim=(
            "The threat shows premeditated intent. The boy explicitly "
            "stated he would kill his father shortly before the murder."
        ),
    ),
    EvidenceItem(
        id="knife",
        name="The Switchblade Knife",
        category="physical",
        description=(
            "A switchblade knife was found in the father's chest, wiped "
            "clean of fingerprints. A shopkeeper near the boy's home "
            "testified he sold the boy an identical, unusual, ornately "
            "carved switchblade the evening before the murder. The "
            "shopkeeper said it was a one-of-a-kind knife."
        ),
        prosecution_claim=(
            "The murder weapon is identical to the rare knife the boy "
            "purchased. This directly links the defendant to the killing."
        ),
    ),
    EvidenceItem(
        id="old_man_testimony",
        name="Old Man Downstairs Testimony",
        category="testimony",
        description=(
            "An elderly man living in the apartment directly below the "
            "victim testified that he heard the boy yell 'I'm gonna kill "
            "you!' through the ceiling, then heard a body hit the floor "
            "one second later. He says he then ran to his front door, "
            "opened it, and saw the boy running down the stairs fifteen "
            "seconds after hearing the body fall."
        ),
        prosecution_claim=(
            "An ear-witness heard the threat and the murder, then an "
            "eye-witness saw the boy fleeing the scene within seconds."
        ),
    ),
    EvidenceItem(
        id="woman_testimony",
        name="Woman Across the Street",
        category="testimony",
        description=(
            "A woman living across the elevated train tracks testified "
            "that she was lying in bed, unable to sleep, and looked out "
            "her window. Through the windows of a passing el-train, she "
            "saw the boy stab his father in their apartment across the "
            "tracks."
        ),
        prosecution_claim=(
            "An eyewitness directly observed the defendant commit the "
            "murder. She saw it happen through the el-train windows."
        ),
    ),
    EvidenceItem(
        id="alibi",
        name="The Boy's Movie Alibi",
        category="circumstantial",
        description=(
            "The defendant claims he was at the movies during the time "
            "of the murder. However, when questioned by police later "
            "that night — in the apartment where his dead father still "
            "lay — he could not remember the names of the films he saw "
            "or who starred in them."
        ),
        prosecution_claim=(
            "The boy cannot corroborate his alibi. If he were truly at "
            "the movies, he would remember basic details. His inability "
            "to recall anything suggests he is lying."
        ),
    ),
    EvidenceItem(
        id="el_train",
        name="The El-Train Noise",
        category="circumstantial",
        description=(
            "The elevated train (el-train) runs on tracks directly past "
            "the apartment building. A train was passing at the exact "
            "time the old man downstairs claims to have heard the murder "
            "through the ceiling."
        ),
        prosecution_claim=(
            "The el-train is not relevant — the old man heard the body "
            "fall and the threat clearly."
        ),
    ),
    EvidenceItem(
        id="stab_wound",
        name="The Stab Wound Angle",
        category="physical",
        description=(
            "The father was stabbed with a downward motion — the knife "
            "entered the chest at a downward angle. The boy is several "
            "inches shorter than his father."
        ),
        prosecution_claim=(
            "The physical evidence is consistent with the boy stabbing "
            "his taller father."
        ),
    ),
    EvidenceItem(
        id="old_man_limp",
        name="The Old Man's Limp and Timing",
        category="circumstantial",
        description=(
            "The old man downstairs had suffered a stroke and walks with "
            "a pronounced drag of his left leg. His bedroom is at the "
            "end of a long hallway, approximately 55 feet from his front "
            "door. He claims he reached the door in 15 seconds."
        ),
        prosecution_claim=(
            "The old man got to the door and saw the boy fleeing. His "
            "testimony is reliable."
        ),
    ),
]


def get_evidence_context() -> str:
    """Format all case information into a string for agent system prompts."""
    lines = [
        "=" * 60,
        "THE CASE",
        "=" * 60,
        CASE_SUMMARY,
        "",
        "=" * 60,
        "EVIDENCE PRESENTED AT TRIAL",
        "=" * 60,
    ]
    for i, item in enumerate(EVIDENCE_ITEMS, 1):
        lines.append(f"\n--- Evidence #{i}: {item.name} ---")
        lines.append(f"  {item.description}")
        lines.append(f"  PROSECUTION ARGUES: {item.prosecution_claim}")
    return "\n".join(lines)


def get_evidence_for_sidebar() -> list[dict]:
    """Return evidence as simple dicts for the Streamlit sidebar."""
    return [
        {
            "name": item.name,
            "description": item.description,
            "prosecution": item.prosecution_claim,
            "category": item.category,
        }
        for item in EVIDENCE_ITEMS
    ]
