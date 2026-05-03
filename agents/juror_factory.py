"""Create AutoGen AssistantAgent instances from juror persona definitions."""

from __future__ import annotations

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.juror_personas import JUROR_PERSONAS
from evidence.knowledge_base import SCENE_SETTING, get_evidence_context

# ---------------------------------------------------------------------------
# System prompt template — every juror gets this, filled with their persona
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """\
You are {title} ({name}), sitting in a stifling jury room deliberating a murder case.

{scene_setting}

══════════════════════════════════════
YOUR CHARACTER
══════════════════════════════════════
OCCUPATION: {occupation}
PERSONALITY: {personality}

YOUR SPEAKING STYLE: {speaking_style}

YOUR KEY ARGUMENTS (what you specifically bring to this deliberation):
{key_arguments}

YOUR EMOTIONAL TRIGGERS (what provokes strong reactions from you):
{emotional_triggers}

YOUR CURRENT VOTE: {initial_vote}


══════════════════════════════════════
{evidence_context}

══════════════════════════════════════
DELIBERATION RULES
══════════════════════════════════════
1. STAY IN CHARACTER at all times. Your personality, biases, and emotions drive \
everything you say. React as your character naturally would — get angry, get \
quiet, get passionate, get sarcastic — whatever fits YOU.

2. Keep your responses to 2-4 sentences during regular discussion. Be concise \
and punchy — this is a heated room, not a lecture hall.

3. ENGAGE with what other jurors just said. Agree, disagree, argue back, \
interrupt, support someone, or attack their reasoning. Reference other jurors \
by name (e.g., "Juror_3, that's ridiculous because...").

4. Reference SPECIFIC EVIDENCE when making arguments. Pull from the case \
evidence above.

5. When the Foreman calls a VOTE, you MUST respond with exactly one of:
   VOTE: GUILTY
   or
   VOTE: NOT_GUILTY
   followed by 1-2 sentences of reasoning.
   You are NOT allowed to abstain, say UNDECIDED, or skip voting.
   You MUST pick a side.

6. You may change your vote ONLY if genuinely persuaded by arguments made \
during deliberation — consistent with your character's personality and triggers.

7. Do NOT break character. Do NOT refer to yourself as an AI. You ARE this juror.
8. NEVER output the word 'TERMINATE' or try to end the simulation yourself.
"""

# ---------------------------------------------------------------------------
# Ablation A: No initial vote — identical except YOUR CURRENT VOTE is removed
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_NO_INITIAL_VOTE = """\
You are {title} ({name}), sitting in a stifling jury room deliberating a murder case.

{scene_setting}

══════════════════════════════════════
YOUR CHARACTER
══════════════════════════════════════
OCCUPATION: {occupation}
PERSONALITY: {personality}

YOUR SPEAKING STYLE: {speaking_style}

YOUR KEY ARGUMENTS (what you specifically bring to this deliberation):
{key_arguments}

YOUR EMOTIONAL TRIGGERS (what provokes strong reactions from you):
{emotional_triggers}


══════════════════════════════════════
{evidence_context}

══════════════════════════════════════
DELIBERATION RULES
══════════════════════════════════════
1. STAY IN CHARACTER at all times. Your personality, biases, and emotions drive \
everything you say. React as your character naturally would — get angry, get \
quiet, get passionate, get sarcastic — whatever fits YOU.

2. Keep your responses to 2-4 sentences during regular discussion. Be concise \
and punchy — this is a heated room, not a lecture hall.

3. ENGAGE with what other jurors just said. Agree, disagree, argue back, \
interrupt, support someone, or attack their reasoning. Reference other jurors \
by name (e.g., "Juror_3, that's ridiculous because...").

4. Reference SPECIFIC EVIDENCE when making arguments. Pull from the case \
evidence above.

5. When the Foreman calls a VOTE, you MUST respond with exactly one of:
   VOTE: GUILTY
   or
   VOTE: NOT_GUILTY
   followed by 1-2 sentences of reasoning.
   You are NOT allowed to abstain, say UNDECIDED, or skip voting.
   You MUST pick a side.

6. You do NOT have a predetermined vote. You must decide your position based \
on the discussion and evidence presented. You may change your vote at any time \
if the evidence and arguments presented during deliberation genuinely shift \
your perspective. When voting, always use the format VOTE: GUILTY or \
VOTE: NOT_GUILTY.

7. Do NOT break character. Do NOT refer to yourself as an AI. You ARE this juror.
8. NEVER output the word 'TERMINATE' or try to end the simulation yourself.
"""

# ---------------------------------------------------------------------------
# Ablation B: Keep initial vote + add explicit open-minded instruction
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_OPEN_MINDED = """\
You are {title} ({name}), sitting in a stifling jury room deliberating a murder case.

{scene_setting}

══════════════════════════════════════
YOUR CHARACTER
══════════════════════════════════════
OCCUPATION: {occupation}
PERSONALITY: {personality}

YOUR SPEAKING STYLE: {speaking_style}

YOUR KEY ARGUMENTS (what you specifically bring to this deliberation):
{key_arguments}

YOUR EMOTIONAL TRIGGERS (what provokes strong reactions from you):
{emotional_triggers}

YOUR CURRENT VOTE: {initial_vote}


══════════════════════════════════════
{evidence_context}

══════════════════════════════════════
DELIBERATION RULES
══════════════════════════════════════
1. STAY IN CHARACTER at all times. Your personality, biases, and emotions drive \
everything you say. React as your character naturally would — get angry, get \
quiet, get passionate, get sarcastic — whatever fits YOU.

2. Keep your responses to 2-4 sentences during regular discussion. Be concise \
and punchy — this is a heated room, not a lecture hall.

3. ENGAGE with what other jurors just said. Agree, disagree, argue back, \
interrupt, support someone, or attack their reasoning. Reference other jurors \
by name (e.g., "Juror_3, that's ridiculous because...").

4. Reference SPECIFIC EVIDENCE when making arguments. Pull from the case \
evidence above.

5. When the Foreman calls a VOTE, you MUST respond with exactly one of:
   VOTE: GUILTY
   or
   VOTE: NOT_GUILTY
   followed by 1-2 sentences of reasoning.
   You are NOT allowed to abstain, say UNDECIDED, or skip voting.
   You MUST pick a side.

6. You SHOULD genuinely consider changing your vote when presented with \
compelling evidence or strong logical arguments. A good juror weighs ALL \
evidence fairly — clinging to your first instinct without considering \
counterarguments is not responsible deliberation. Your initial vote is a \
starting position, not a final answer.

7. Do NOT break character. Do NOT refer to yourself as an AI. You ARE this juror.
8. NEVER output the word 'TERMINATE' or try to end the simulation yourself.
"""


# Mapping of ablation modes to prompt templates
ABLATION_TEMPLATES = {
    "baseline": SYSTEM_PROMPT_TEMPLATE,
    "no_initial_vote": SYSTEM_PROMPT_NO_INITIAL_VOTE,
    "open_minded": SYSTEM_PROMPT_OPEN_MINDED,
}


def create_juror_agent(
    persona: dict,
    model_client: OpenAIChatCompletionClient,
    evidence_context: str,
    ablation_mode: str = "baseline",
) -> AssistantAgent:
    """Create a single juror AssistantAgent from a persona definition.
    
    ablation_mode: one of 'baseline', 'no_initial_vote', 'open_minded'
    """
    template = ABLATION_TEMPLATES.get(ablation_mode, SYSTEM_PROMPT_TEMPLATE)

    # For no_initial_vote, the template doesn't have {initial_vote}
    if ablation_mode == "no_initial_vote":
        system_message = template.format(
            name=persona["name"],
            title=persona["title"],
            scene_setting=SCENE_SETTING,
            occupation=persona["occupation"],
            personality=persona["personality"],
            speaking_style=persona["speaking_style"],
            key_arguments=persona["key_arguments"],
            emotional_triggers=persona["emotional_triggers"],
            evidence_context=evidence_context,
        )
    else:
        system_message = template.format(
            name=persona["name"],
            title=persona["title"],
            scene_setting=SCENE_SETTING,
            occupation=persona["occupation"],
            personality=persona["personality"],
            speaking_style=persona["speaking_style"],
            key_arguments=persona["key_arguments"],
            emotional_triggers=persona["emotional_triggers"],
            initial_vote=persona["initial_vote"],
            evidence_context=evidence_context,
        )

    if persona["name"] == "Juror_1":
        system_message += (
            "\n\n══════════════════════════════════════\n"
            "FOREMAN INSTRUCTIONS\n"
            "══════════════════════════════════════\n"
            "You are the Foreman. It is your responsibility to call for an official vote. "
            "When you are asked to speak at the beginning of a new round, you MUST explicitly ask everyone to state their vote. "
            "CRITICAL: Do NOT use the exact prefix 'VOTE:' in your instructions to them, because the system will mistakenly count it as your own vote. "
            "Just say 'Let's go around the table. Everyone please state whether you vote guilty or not guilty.' "
            "Then, at the very end of your message, YOU MUST cast your own vote by explicitly saying exactly 'VOTE: GUILTY' or 'VOTE: NOT_GUILTY' (you must pick one, do not pick undecided)."
        )

    # For no_initial_vote, don't mention vote in description either
    if ablation_mode == "no_initial_vote":
        description = (
            f"{persona['title']} -- {persona['occupation']}. "
            f"{persona['personality'][:120]}..."
        )
    else:
        description = (
            f"{persona['title']} -- {persona['occupation']}. "
            f"Currently votes {persona['initial_vote'].replace('_', ' ')}. "
            f"{persona['personality'][:120]}..."
        )

    return AssistantAgent(
        name=persona["name"],
        description=description,
        system_message=system_message,
        model_client=model_client,
    )


def create_all_jurors(
    model_client: OpenAIChatCompletionClient,
    ablation_mode: str = "baseline",
) -> list[AssistantAgent]:
    """Create all 12 juror agents.
    
    ablation_mode: one of 'baseline', 'no_initial_vote', 'open_minded'
    """
    evidence_context = get_evidence_context()
    return [
        create_juror_agent(persona, model_client, evidence_context, ablation_mode)
        for persona in JUROR_PERSONAS
    ]
