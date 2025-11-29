# Setup Skills in a Project

This guide shows how to add AI skills to any Claude Code project.

## Quick Setup

From any project directory:

```bash
/var/home/ewt/ai-skills/setup-skills.sh
```

Or specify a target directory:

```bash
/var/home/ewt/ai-skills/setup-skills.sh ~/projects/my-app
```

## What It Does

The setup script:

1. Creates `.claude/skills/` directory
2. Symlinks all skills from ai-skills repository
3. Links `SKILL.md` catalog to `.claude/` directory

## Result

After running, your project has:

```
your-project/
├── .claude/
│   ├── SKILL.md -> /var/home/ewt/claude-code-ai-skills/SKILL.md
│   └── skills/              # Symlinks to central skills
│       ├── cbs-analyzer/
│       ├── container-sandboxes/
│       ├── docs-manager/
│       └── k8s-metrics/
```

## Usage

In Claude Code, invoke skills:

```
Skill: docs-manager
Skill: cbs-analyzer
Skill: k8s-metrics
Skill: container-sandboxes
```

Skills are invoked using Claude Code's Skill tool and will automatically execute their specialized tasks.

## Updating Skills

Since skills are symlinked, updates to the central ai-skills repository automatically reflect in all projects.

To update:

```bash
cd /var/home/ewt/ai-skills
# Make changes to .claude/skills/*.md
# All projects using symlinks see updates immediately
```

## Per-Project Customization

If a project needs custom skills:

1. Symlink common skills (via setup script)
2. Add project-specific skills directly to `.claude/skills/`

Example:

```bash
# After running setup-skills.sh
cd your-project/.claude/skills
# Create project-specific skill directory
mkdir -p custom-skill
cat > custom-skill/SKILL.md << 'EOF'
# Custom Skill
[Your custom skill content]
EOF
```

## Manual Setup

If you prefer manual setup:

```bash
cd your-project
mkdir -p .claude/skills
cd .claude

# Symlink skill catalog
ln -s /var/home/ewt/claude-code-ai-skills/SKILL.md .

# Symlink skills
cd skills
ln -s /var/home/ewt/claude-code-ai-skills/.claude/skills/docs-manager .
ln -s /var/home/ewt/claude-code-ai-skills/.claude/skills/cbs-analyzer .
ln -s /var/home/ewt/claude-code-ai-skills/.claude/skills/k8s-metrics .
ln -s /var/home/ewt/claude-code-ai-skills/.claude/skills/container-sandboxes .
```

## Troubleshooting

### Symlinks not working

Check if symlinks are enabled on your filesystem. On Windows, you may need administrator privileges or WSL.

### Skills source not found

The script expects skills at `/var/home/ewt/ai-skills/.claude/skills/`. If you moved the repository, update `SKILLS_SOURCE` in `setup-skills.sh:6`.

### Script won't execute

Make it executable:

```bash
chmod +x /var/home/ewt/ai-skills/setup-skills.sh
```
