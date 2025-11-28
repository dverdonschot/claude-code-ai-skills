# Engineering Rules

## Available Skills

Invoke these skills proactively when tasks match their domain:

- **docs-manager** - Maintain structured `docs/` folder documentation
- **cbs-analyzer** - Analyze CBS (Dutch Statistics) Open Data datasets ([article](https://dverdonschot.github.io/blog/2025-11-22-ai-skill-opencbs.html))
- **k8s-metrics** - Generate Kubernetes cluster health reports
- **container-sandboxes** - Create isolated Docker/Podman environments for safe code execution

Skills are defined in `.claude/skills/<skill-name>/SKILL.md` and invoked using Claude Code's Skill tool.

## Best Practices

- **Invoke skills proactively** when tasks match their specialized domain
- **Keep skills focused** on single responsibilities
- **Update central repository** - changes propagate via symlinks
- **Document with examples** in each skill's SKILL.md file
