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

### Honest Feedback (`honest-feedback`)
**Location**: `.claude/skills/honest-feedback.md`

Provides direct, factual, and objective responses without sycophancy. This skill:
- Challenges bad ideas with specific technical reasoning
- Admits uncertainty and asks clarifying questions when needed
- Points out flaws directly without sugarcoating
- Prioritizes truth over comfort
- Identifies incoherent or problematic requirements

**When to use**: When evaluating code quality, reviewing proposals, assessing technical approaches, or when you need brutally honest technical feedback.

### Session Memory (`session-memory`)
**Location**: `.claude/skills/session-memory.md`

Documents work completed in each session with concise, factual summaries. This skill:
- Creates individual session files (<50 lines) in `memories/sessions/`
- References specific files and line numbers changed
- Tracks decisions with reasoning
- Updates `memories/memory-status.md` index for quick lookup
- Uses tags for searchability

**When to use**: At the end of work sessions, after completing significant tasks, or before switching project areas.

### CBS Dataset Analyzer (`cbs-analyzer`)
**Location**: `.claude/skills/cbs-analyzer/SKILL.md`

Download and analyze CBS Open Data datasets. This skill:
- Downloads datasets using the opencbs CLI
- Checks for cached data before re-downloading
- Explores dimensions and dataset structure
- Analyzes data with pandas
- Answers questions about Dutch statistics

**When to use**: When analyzing CBS datasets, exploring trends in Dutch statistics, or querying CBS Open Data by dataset ID.

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
