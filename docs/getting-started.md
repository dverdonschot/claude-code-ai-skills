# Getting Started

Welcome to the AI Skills project! This guide will help you start using Claude Code skills in minutes.

## Quick Start

1. **Install Claude Code** (if not already installed)
   ```bash
   npm install -g @anthropics/claude-code
   ```

2. **Navigate to this project**
   ```bash
   cd /path/to/ai-skills
   ```

3. **Invoke a skill**
   Within Claude Code, use the Skill tool to invoke any skill:
   ```
   Skill: docs-manager
   ```

## Available Skills

- **docs-manager**: Maintains structured documentation in `docs/` folder
  - Use after code changes
  - Keeps docs concise and up-to-date
  - Creates helpful visualizations

- **honest-feedback**: Provides direct, factual feedback without sycophancy
  - Challenges bad ideas with technical reasoning
  - Admits uncertainty when needed
  - No sugarcoating

- **session-memory**: Documents work done in each session
  - Creates concise summaries (<50 lines)
  - Tracks file changes and decisions
  - Updates searchable index

## Project Structure

```
ai-skills/
├── SKILL.md                    # Skill catalog and overview
├── .claude/skills/             # Skill definitions
│   ├── docs-manager.md
│   ├── honest-feedback.md
│   └── session-memory.md
├── docs/                       # Project documentation
│   ├── getting-started.md      # This file
│   ├── architecture/           # System design docs
│   ├── guides/                 # Feature guides
│   └── reference/              # API and config reference
└── memories/                   # Session work logs
    ├── memory-status.md        # Quick lookup index
    └── sessions/               # Individual session files
        └── YYYY-MM/
```

## Next Steps

- Read [SKILL.md](../SKILL.md) to understand how skills work
- Explore the [architecture](./architecture/overview.md) documentation
- Create your own custom skills in `.claude/skills/`

## Need Help?

- Check skill documentation in `.claude/skills/`
- Review examples in this `docs/` folder
- Ask Claude Code to explain any skill
