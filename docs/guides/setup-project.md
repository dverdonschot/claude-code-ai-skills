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
3. Creates `memories/` directory structure
4. Initializes `memory-status.md` index file

## Result

After running, your project has:

```
your-project/
├── .claude/
│   └── skills/              # Symlinks to central skills
│       ├── docs-manager.md -> /var/home/ewt/ai-skills/.claude/skills/docs-manager.md
│       ├── honest-feedback.md -> /var/home/ewt/ai-skills/.claude/skills/honest-feedback.md
│       └── session-memory.md -> /var/home/ewt/ai-skills/.claude/skills/session-memory.md
└── memories/                # Project-specific session logs
    ├── memory-status.md
    └── sessions/
        └── YYYY-MM/
```

## Usage

In Claude Code, invoke skills:

```
Skill: docs-manager
Skill: honest-feedback
Skill: session-memory
```

Skills are not yet invokable via the Skill tool (feature may be added in future Claude Code versions). For now, you can:

1. **Copy skill content**: Read the skill file and paste into your prompt
2. **Reference in instructions**: "Follow the process in `.claude/skills/docs-manager.md`"
3. **Wait for feature**: Claude Code may add skill support in future updates

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
# Create project-specific skill
cat > custom-skill.md << 'EOF'
# Custom Skill
[Your custom skill content]
EOF
```

## Manual Setup

If you prefer manual setup:

```bash
cd your-project
mkdir -p .claude/skills
cd .claude/skills

# Symlink skills
ln -s /var/home/ewt/ai-skills/.claude/skills/docs-manager.md .
ln -s /var/home/ewt/ai-skills/.claude/skills/honest-feedback.md .
ln -s /var/home/ewt/ai-skills/.claude/skills/session-memory.md .

# Setup memories
cd ../..
mkdir -p memories/sessions/$(date +%Y-%m)
touch memories/memory-status.md
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
