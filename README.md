# 12 Angry AI Agents - Multi-Agent Deliberation Framework

This repository contains the core logic for simulating the "12 Angry Men" jury deliberation using LLM agents. It is designed to be a lightweight framework for testing multi-agent decision-making, anchoring, and persuasion dynamics.

## Structure

- `agents/`: Contains juror persona definitions and the factory for creating AutoGen agents.
- `deliberation/`: The core engine, speaker selection logic, and vote tracking.
- `evidence/`: The case file and evidence knowledge base.
- `config.py`: Configuration for LLM providers (OpenAI, OpenRouter, Ollama).
- `requirements.txt`: Python dependencies.

## Key Features

- **Persona-Driven Agents**: 12 movie-accurate personas with distinct biases and speaking styles.
- **Custom Speaker Selection**: A deterministic yet flexible speaker selection logic that handles jury turn-taking.
- **Vote Tracking**: Automated extraction and tracking of votes during deliberation.
- **Ablation Support**: Built-in support for different experimental conditions (Baseline, No Initial Vote, Open-Minded).

## Research Highlights

A fascinating new paper, **"12 Angry AI Agents,"** tests multi-agent LLM decision-making by putting AI in the jury box. The results expose a massive blind spot in current AI systems regarding how they collaborate and change their minds:

- 🔒 **The Anchoring Effect is Real**: Out of 18 deliberation runs, 17 ended in a "hung jury". LLMs stubbornly anchor to their initial positions.
- ⚖️ **Alignment Makes AIs Rigid**: GPT-4o (highly aligned) was incredibly inflexible, averaging just 1.0 vote change per run.
- 🏆 **The Only Verdict**: Llama-4-Scout was the only model capable of reaching a unanimous "Not Guilty" verdict in specific scenarios.
- 📉 **Bigger Isn't Always Better**: Flexibility, not raw capability, is what mimics human persuasion. Heavy RLHF can make AI a rigid collaborator.
- 🗣️ **Parallel Monologues**: Agents often talk past each other without true social mechanisms for mind-changing.

## Usage

This framework is built on [AutoGen](https://github.com/microsoft/autogen). To run a deliberation, you'll need to initialize the agents using the `JurorFactory` and pass them to the `DeliberationEngine`.

```python
from src.agents.juror_factory import create_all_jurors
from src.deliberation.engine import DeliberationEngine

# Setup your model client and config...
# engine = DeliberationEngine(agents, config)
# results = await engine.run()
```

## Explore More

- **Project Page**: [https://ahmetbersoz.github.io/12-angry-ai-agents/](https://ahmetbersoz.github.io/12-angry-ai-agents/)
- **Paper**: [Read the paper here](https://arxiv.org/abs/2605.01986)
- **Experiment Transcripts**: [Explore all 18 transcripts here](https://ahmetbersoz.github.io/12-angry-ai-agents/transcripts.html)


## Citation

If you use this framework or the paper's findings in your research, please cite:

```bibtex
@article{ersoz2026,
  title={12 Angry AI Agents: Evaluating Multi-Agent LLM Decision-Making Through Cinematic Jury Deliberation},
  author={Ersoz, Ahmet Bahaddin},
  journal={arXiv preprint arXiv:2605.01986},
  year={2026},
  url={https://doi.org/10.48550/arXiv.2605.01986}
}
```
