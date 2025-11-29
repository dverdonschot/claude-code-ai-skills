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

- **cbs-analyzer**: Download and analyze CBS (Dutch Statistics) Open Data datasets
  - Query specific dataset IDs
  - Explore energy/population/economic trends
  - Analyze Netherlands statistics

- **k8s-metrics**: Generate Kubernetes cluster health reports
  - Shows pod status and resource distribution
  - Displays failed containers and node health
  - Provides cluster utilization metrics

- **container-sandboxes**: Operate local container sandboxes
  - Run code in isolation using Docker or Podman
  - Test packages safely
  - Execute commands in isolated environments

## Project Structure

```
claude-code-ai-skills/
├── SKILL.md                    # Skill catalog and overview
├── .claude/skills/             # Skill definitions
│   ├── cbs-analyzer/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── container-sandboxes/
│   │   └── SKILL.md
│   ├── docs-manager/
│   │   └── SKILL.md
│   └── k8s-metrics/
│       ├── SKILL.md
│       └── scripts/
├── docs/                       # Project documentation
│   ├── getting-started.md      # This file
│   ├── architecture/           # System design docs
│   ├── guides/                 # Feature guides
│   └── reference/              # API and config reference
└── setup-skills.sh             # Setup script for projects
```

## Next Steps

- Read [SKILL.md](../SKILL.md) to understand how skills work
- Explore the [architecture](./architecture/overview.md) documentation
- Create your own custom skills in `.claude/skills/`

## Need Help?

- Check skill documentation in `.claude/skills/`
- Review examples in this `docs/` folder
- Ask Claude Code to explain any skill
