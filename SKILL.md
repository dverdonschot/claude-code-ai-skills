# AI Skills Project

This project contains reusable skills for Claude Code to help maintain consistent, high-quality documentation and development practices.

## What are Skills?

Skills are specialized prompts that Claude Code can invoke to perform specific tasks with domain expertise. They help automate repetitive tasks and enforce best practices across your codebase.

## Available Skills

### Documentation Management (`docs-manager`)
**Location**: `.claude/skills/docs-manager.md`

Maintains structured, concise documentation in the `docs/` folder. This skill:
- Ensures documentation stays up-to-date after code changes
- Prevents duplication and maintains clear structure
- Keeps content focused on getting started and understanding components
- Creates visualizations and diagrams where helpful
- Excludes README.md (kept in project root)

**When to use**: After making significant code changes, adding features, or refactoring components.

### CBS Dataset Analyzer (`cbs-analyzer`)
**Location**: `.claude/skills/cbs-analyzer/SKILL.md`

Download and analyze CBS Open Data datasets. This skill:
- Downloads datasets using the opencbs CLI
- Checks for cached data before re-downloading
- Explores dimensions and dataset structure
- Analyzes data with pandas
- Answers questions about Dutch statistics

**When to use**: When analyzing CBS datasets, exploring trends in Dutch statistics, or querying CBS Open Data by dataset ID.

**📝 Read more**: [Building an AI Skill to Analyze Datasets on CBS Open Data](https://dverdonschot.github.io/blog/2025-11-22-ai-skill-opencbs.html)

### Kubernetes Cluster Metrics (`k8s-metrics`)
**Location**: `.claude/skills/k8s-metrics/SKILL.md`

Generate comprehensive Kubernetes cluster health and resource usage reports. This skill:
- Checks cluster connectivity and gathers pod/node status
- Identifies failed containers, crash loops, and resource issues
- Analyzes resource distribution across namespaces
- Generates human-readable summary reports
- Outputs detailed JSON with specific resource names for AI investigation
- Provides actionable recommendations

**When to use**: When checking Kubernetes cluster health, investigating pod failures, analyzing resource usage, or needing quick cluster status overview.

### Container Sandboxes (`container-sandboxes`)
**Location**: `.claude/skills/container-sandboxes/SKILL.md`

Create isolated container environments for safe code execution using Docker or Podman. This skill:
- Provides local sandboxes without API keys or external services
- Supports both Docker and Podman with auto-detection
- Includes Python, Node, and full-stack container templates
- Executes commands safely in isolated environments
- Manages files and processes within sandboxes
- Perfect for testing untrusted code or running experiments locally

**When to use**: When you need to run code in isolation, test packages safely, execute untrusted code, or work in clean environments without affecting the host system.

## Skill Structure

Each skill is defined in `.claude/skills/[skill-name].md` with:

```markdown
# [Skill Name]

[Brief description of what this skill does]

## Context

[When this skill should be used]

## Process

1. [Step-by-step process]
2. [The skill should follow]
3. [To complete its task]

## Guidelines

- [Specific rules]
- [And constraints]
- [For this skill]

## Output

[What the skill produces]
```

## Using Skills in Your Projects

### Quick Setup

Run the setup script from any project directory:

```bash
/var/home/ewt/ai-skills/setup-skills.sh
```

Or specify a target:

```bash
/var/home/ewt/ai-skills/setup-skills.sh ~/projects/my-app
```

This creates:
- `.claude/skills/` with symlinks to central skills
- `memories/` directory for session tracking
- `memory-status.md` index file

See [Setup Guide](docs/guides/setup-project.md) for details.

### How Symlinks Work

Skills are symlinked, not copied. Updates to skills in this repository automatically reflect in all projects using them.

**Central location**: `/var/home/ewt/ai-skills/.claude/skills/`
**Project links**: Each project's `.claude/skills/` contains symlinks

## Creating New Skills

1. Create a new file in `.claude/skills/[skill-name].md`
2. Follow the structure above
3. Update this SKILL.md file to list the new skill
4. Test the skill in Claude Code
5. Skills automatically available in all symlinked projects

## Best Practices

- Keep skills focused on a single responsibility
- Make skills reusable across different projects
- Include clear examples in skill documentation
- Test skills thoroughly before relying on them
- Update central repository; changes propagate via symlinks
