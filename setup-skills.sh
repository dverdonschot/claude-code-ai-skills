#!/bin/bash

# setup-skills.sh
# Symlinks AI skills to a target project directory

set -e

SKILLS_SOURCE="/var/home/ewt/claude-code-ai-skills/.claude/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 [target_directory]"
    echo ""
    echo "Symlinks AI skills from this repository to a target project."
    echo ""
    echo "Arguments:"
    echo "  target_directory    Path to project (defaults to current directory)"
    echo ""
    echo "Examples:"
    echo "  $0                          # Setup in current directory"
    echo "  $0 ~/projects/my-app        # Setup in specific project"
    echo "  $0 .                        # Setup in current directory (explicit)"
}

# Parse arguments
TARGET_DIR="${1:-.}"

if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    print_usage
    exit 0
fi

# Resolve to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
    echo -e "${RED}Error: Directory '$1' does not exist${NC}"
    exit 1
}

SKILLS_DIR="$TARGET_DIR/.claude/skills"
SKILL_CATALOG="$SCRIPT_DIR/SKILL.md"

echo -e "${BLUE}=== AI Skills Setup ===${NC}"
echo -e "Source: ${GREEN}$SKILLS_SOURCE${NC}"
echo -e "Target: ${GREEN}$TARGET_DIR${NC}"
echo ""

# Check if source exists
if [[ ! -d "$SKILLS_SOURCE" ]]; then
    echo -e "${RED}Error: Skills source directory not found: $SKILLS_SOURCE${NC}"
    echo "Make sure you're running this from the ai-skills repository"
    exit 1
fi

# Create .claude/skills directory
echo -e "${BLUE}Creating .claude/skills directory...${NC}"
mkdir -p "$SKILLS_DIR"

# Count existing symlinks
EXISTING_COUNT=0
NEW_COUNT=0
UPDATED_COUNT=0

# Symlink each skill
for skill_dir in "$SKILLS_SOURCE"/*/; do
    if [[ -d "$skill_dir" ]]; then
        skill_name="$(basename "$skill_dir")"
        target_link="$SKILLS_DIR/$skill_name"

        if [[ -L "$target_link" ]]; then
            # Symlink exists
            current_target="$(readlink "$target_link")"
            if [[ "$current_target" == "$skill_dir" ]]; then
                echo -e "  ${GREEN}✓${NC} $skill_name (already linked)"
                EXISTING_COUNT=$((EXISTING_COUNT + 1))
            else
                # Update symlink
                rm "$target_link"
                ln -s "$skill_dir" "$target_link"
                echo -e "  ${YELLOW}↻${NC} $skill_name (updated)"
                UPDATED_COUNT=$((UPDATED_COUNT + 1))
            fi
        elif [[ -e "$target_link" ]]; then
            # File/directory exists but not a symlink
            echo -e "  ${YELLOW}⚠${NC}  $skill_name (file exists, skipping)"
        else
            # Create new symlink
            ln -s "$skill_dir" "$target_link"
            echo -e "  ${GREEN}+${NC} $skill_name (linked)"
            NEW_COUNT=$((NEW_COUNT + 1))
        fi
    fi
done

echo ""

# Symlink SKILL.md catalog to .claude directory
SKILL_CATALOG_LINK="$TARGET_DIR/.claude/SKILL.md"
if [[ ! -e "$SKILL_CATALOG_LINK" ]]; then
    ln -s "$SKILL_CATALOG" "$SKILL_CATALOG_LINK"
    echo -e "${BLUE}Linking skill catalog...${NC}"
    echo -e "  ${GREEN}+${NC} SKILL.md (linked)"
elif [[ -L "$SKILL_CATALOG_LINK" ]]; then
    echo -e "${BLUE}Skill catalog already linked${NC}"
    echo -e "  ${GREEN}✓${NC} SKILL.md"
fi

echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo -e "  New symlinks:      $NEW_COUNT"
echo -e "  Already linked:    $EXISTING_COUNT"
echo -e "  Updated:           $UPDATED_COUNT"
echo ""
echo -e "${BLUE}Available skills in $TARGET_DIR:${NC}"
ls -1 "$SKILLS_DIR" | sed 's/^/  - /'
echo ""
echo -e "${YELLOW}Note:${NC} Skills are symlinked. Updates to skills in $SCRIPT_DIR"
echo "      will automatically reflect in this project."
echo ""
echo -e "${GREEN}Ready to use!${NC} Invoke skills in Claude Code with:"
echo -e "  ${BLUE}Skill: docs-manager${NC}"
