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
- **Experiment Transcripts**: [Explore all 18 transcripts here](https://ahmetbersoz.github.io/12-angry-ai-agents/transcripts.html)

## Citation

If you use this framework or the paper's findings in your research, please cite:

```bibtex
@article{ersoz2024twelveangry,
  title={12 Angry AI Agents: Evaluating Multi-Agent LLM Decision-Making Through Cinematic Jury Deliberation},
  author={Ersoz, Ahmet},
  journal={arXiv preprint arXiv:2405.xxxxx},
  year={2024},
  url={https://github.com/ahmetbersoz/12-angry-ai-agents}
}
```
