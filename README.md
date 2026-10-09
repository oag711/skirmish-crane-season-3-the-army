# Skirmish at Crane Reach agent

Edit `agent.py` to build one unit's behavior for Skirmish at Crane Reach. Every unit on a side runs a separate instance of the same `Agent` class, so they do not share state or variables. `sandbox/` is provided code: do not edit it.

Start with the [Getting Started guide](https://vox-deorum.github.io/game-sandbox/students/getting-started/). Then run these commands from this folder as you work:

```console
python -m sandbox play   # command a side yourself in your browser
python -m sandbox watch  # watch your agent take on Naive
python -m sandbox test   # run the provided checks
python -m sandbox eval   # compare your agent with Naive
```

**Naive** is a simple built-in opponent. It holds the other side in `watch` and `eval`, and `eval` reports your side's average score over repeatable matches. The [`environment.md`](environment.md) guide explains rivals, presets, and the other command options.

## Files you will use

| Path | Purpose |
| --- | --- |
| `agent.py` | Your `Agent` implementation and the first TODO locations. |
| `environment.md` | Crane rules, starter walkthrough, helpers, observations, and settings. |
| `manifest.json` | Names the agent class for a submission. |
| `season.json` | Optional local season settings downloaded from My Submissions. |
| `tests/` | Checks your submission should pass. |
| `sandbox/` | Local game, commands, helper package, and observation types. Do not edit it. |
| `requirements.txt` | Exact Python package versions used by the server. |
| `requirements-dev.txt` | Test dependencies. |
| `.env.example` | Example local LLM settings. |

The starter returns Crane orders with `action.move()` and `action.stay()` from `sandbox.crane`. Its `act(observation)` receives the current observation and action mask. Before changing the strategy, read [`environment.md`](environment.md). It starts with a small archer improvement you can copy, then explains when an order is legal.

Leave `sandbox/`, `requirements.in`, and `requirements.txt` unchanged. The pinned packages match the server. Ask your instructor before adding a package.

When your agent is ready, follow the shared [submitting guide](https://vox-deorum.github.io/game-sandbox/students/submitting/). For the optional `learn` and `chat` hooks, see the shared [agent interface](https://vox-deorum.github.io/game-sandbox/students/agent-interface/). Crane messaging begins in Season 3.

## Optional LLM API

If your instructor enables model calls, follow [Using the LLM API](llm.md). Copy `.env.example` to `.env`, add the endpoint and key, and never commit either secret.

Test the connection with:

```console
python -m sandbox llm
```

Design Goal

The goal of my agent is to control an army of footmen, archers, and cavalry by giving each unit a role that supports the rest of the army. Footmen are intended to form the frontline and support nearby allied footmen. Archers are designed to attack enemies from a distance while avoiding dangerous melee units. Cavalry are intended to move quickly, use their charge bonus, and pressure vulnerable enemy archers. When enemies are not visible, units move toward the center of the map to help the army find the opposing team.

Design Reflection

My design uses a scoring system to choose targets and movement paths. The target-selection system considers distance, enemy health, and unit type. The movement system evaluates legal paths and rewards positions that help each unit perform its role. For example, footmen receive a bonus for staying near allied footmen, cavalry receive a bonus for moving far enough to charge, and archers prefer positions that keep enemies within shooting range while avoiding nearby melee threats.

Testing showed that the agent can perform well in some matches, but its performance is inconsistent. In five test seeds, the scores were 70.94, 0.00, 77.97, 0.00, and 86.41, resulting in an average score of 47.06. The zero scores indicate that the current strategy has important weaknesses that need further investigation. The agent may not respond effectively to every map layout or enemy strategy, and its units do not explicitly coordinate their decisions with one another. My next step is to investigate the failed matches, improve how units choose their positions and targets, and test whether those changes make the results more consistent across different seeds.

AI-Use Disclosure and Reflection

I used ChatGPT as a programming assistant to help develop and review the agent's target-selection and movement strategies. The assistance included discussing how different unit types could use their strengths, how to evaluate legal movement paths, and how to organize the agent's decision-making code. I reviewed the suggested code and used the sandbox's match results to evaluate its performance.

Using AI helped me explore strategies and identify possible improvements more quickly, but it did not guarantee that the agent would perform well in every match. The inconsistent test results showed me that code that appears reasonable can still have weaknesses when tested in a game environment. I learned that evaluating an agent across multiple seeds is important, and that failed matches should be investigated rather than relying only on the best scores. I will continue using test results to guide revisions and make sure I understand the behavior of the code I submit.