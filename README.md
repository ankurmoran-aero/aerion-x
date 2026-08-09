# Aerion-X

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![OpenRouter](https://img.shields.io/badge/AI-OpenRouter-6366f1?style=for-the-badge)](https://openrouter.ai)
[![Status](https://img.shields.io/badge/Status-Active-22c55e?style=for-the-badge)]()

**Aerion-X** is an autonomous, terminal-based AI agent that orchestrates complex engineering workflows through a unified, intelligent interface. It handles file operations, software architecture planning, terminal execution, and auto-dependency resolution — all within a rich, animated CLI experience.

---

## Features

- **Architect Mode** — Collaborative project blueprinting with GPT-4o / Claude before writing a single line of code
- **Autonomous Sandboxing** — All generated code is isolated into a secure `Workspace` directory automatically
- **Integrated Shell** — Drop into an interactive sub-shell with `/shell` without losing AI context
- **Auto-Dependency Resolution** — Detects and installs missing Python/Node.js packages on the fly
- **Rich Terminal UI** — Animated interface with Markdown rendering and syntax highlighting

---

## Installation

```bash
pip install git+https://github.com/ankurmoran-aero/aerion-x.git
```

## Quick Start

```bash
aerion-x
```

### Core Commands

| Command | Description |
|---------|-------------|
| `/cd <path>` | Navigate the AI's active workspace |
| `/shell` | Launch an interactive sub-shell |
| `clear` | Reset the terminal view |
| `exit` | Gracefully shut down the agent |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| AI Engine | OpenRouter / GPT-4o / Claude-3.5-Sonnet |
| UI Framework | `rich`, `prompt_toolkit` |

---

## Project Structure

```
aerion-x/
├── main.py              # Entry point & agent loop
├── config.py            # Configuration & API keys
├── tools/               # Modular tool implementations
│   ├── file_tool.py     # File system operations
│   ├── git_tool.py      # Git integration
│   ├── shell_tool.py    # Shell execution
│   ├── plan_tool.py     # Architecture planning
│   └── web_tool.py      # Web requests
├── requirements.txt
└── setup.py
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
