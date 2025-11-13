---
name: session-memory
description: Document work completed in each session with concise, factual summaries. Track changes, files modified, and key decisions in individual session files, with a central index for quick lookup.
---

# Session Memory

Document work completed in each session with concise, factual summaries. Track changes, files modified, and key decisions in individual session files, with a central index for quick lookup.

## Context

Use this skill:
- At the end of each work session
- After completing significant tasks
- Before switching to a different project area
- When explicitly requested to document work

## Core Principles

### 1. Brevity
- Target: <50 lines per session
- Focus on what changed, not how
- Omit implementation details
- Use bullet points, not paragraphs

### 2. Factual
- Document actual changes made
- Reference specific files and line numbers
- Note decisions with reasons
- No speculation or future plans

### 3. Searchable
- Use consistent formatting
- Include file paths
- Tag key concepts
- Update memory-status.md index

## Process

### 1. Analyze Session Work

Review what was done:
- Files created, modified, or deleted
- Code changes and their purpose
- Configuration updates
- Documentation changes
- Decisions made

### 2. Create Session File

**Filename format**: `YYYY-MM-DD-HHmm-[brief-description].md`

Example: `2025-11-13-1445-setup-skills-system.md`

**Location**: `memories/sessions/YYYY-MM/`

### 3. Document Session

Use this structure:

```markdown
# [Brief Description]

**Date**: YYYY-MM-DD HH:MM
**Duration**: ~X minutes

## Summary
[1-2 sentence overview of what was accomplished]

## Changes

### Created
- `path/to/file.ext` - Purpose

### Modified
- `path/to/file.ext:line` - What changed and why

### Deleted
- `path/to/file.ext` - Why removed

## Decisions
- [Decision made]: [Reason]

## Context
[Any important context for future reference]

## Tags
#tag1 #tag2 #tag3
```

### 4. Update Memory Status

Add entry to `memories/memory-status.md`:

```markdown
- **YYYY-MM-DD HHmm** - [Brief description] - `sessions/YYYY-MM/filename.md` #tags
```

Keep entries in reverse chronological order (newest first).

### 5. Keep It Short

If session file exceeds 50 lines:
- Remove unnecessary details
- Focus on key changes only
- Consolidate similar items
- Use more concise language

## Guidelines

**DO**:
- Reference files with full paths
- Include line numbers for code changes
- Use bullet points
- State facts only
- Tag relevant concepts
- Update memory-status.md
- Keep under 50 lines

**DON'T**:
- Include code snippets
- Write implementation details
- Speculate on future work
- Use verbose language
- Duplicate information
- Skip the index update

## Template

```markdown
# [Session Title]

**Date**: YYYY-MM-DD HH:MM
**Duration**: ~X min

## Summary
[What was accomplished in 1-2 sentences]

## Changes

### Created
- `file/path` - Purpose
- `another/file` - Purpose

### Modified
- `file/path:123` - What and why
- `file/path:456` - What and why

### Deleted
- `old/file` - Reason

## Decisions
- Used X instead of Y because [reason]
- Chose approach Z for [reason]

## Context
[Any important background or constraints]

## Tags
#relevant #tags #here
```

## Memory Status Format

`memories/memory-status.md` contains a quick-lookup index:

```markdown
# Memory Status

Quick index of all sessions for fast reference.

## Recent Sessions

- **2025-11-13 1445** - Setup skills system - `sessions/2025-11/2025-11-13-1445-setup-skills-system.md` #setup #skills
- **2025-11-12 0930** - Fix auth bug - `sessions/2025-11/2025-11-12-0930-fix-auth-bug.md` #bugfix #auth
- **2025-11-12 0815** - Add user dashboard - `sessions/2025-11/2025-11-12-0815-user-dashboard.md` #feature #ui

## Tags Index

### #setup
- 2025-11-13 1445 - Setup skills system

### #bugfix
- 2025-11-12 0930 - Fix auth bug

### #feature
- 2025-11-12 0815 - Add user dashboard

## By Month

### 2025-11
- 3 sessions
- Topics: skills, auth, dashboard

### 2025-10
- 12 sessions
- Topics: initial setup, user system, API
```

## Examples

### Example 1: Feature Work

```markdown
# Add Password Reset Flow

**Date**: 2025-11-13 14:30
**Duration**: ~45 min

## Summary
Implemented password reset with email tokens and expiration.

## Changes

### Created
- `src/auth/reset-password.ts` - Password reset logic
- `src/email/templates/reset.html` - Email template
- `tests/auth/reset-password.test.ts` - Test suite

### Modified
- `src/auth/routes.ts:45` - Added /reset-password endpoint
- `src/db/schema.ts:78` - Added reset_tokens table
- `docs/guides/authentication.md:123` - Documented reset flow

## Decisions
- 1-hour token expiration (security vs UX tradeoff)
- SHA256 for token hashing (sufficient for this use case)
- Email-only reset (no SMS for MVP)

## Context
User reported locked accounts due to forgotten passwords.

## Tags
#feature #auth #email
```

### Example 2: Bug Fix

```markdown
# Fix Race Condition in Cache

**Date**: 2025-11-13 10:15
**Duration**: ~20 min

## Summary
Fixed race condition causing stale cache reads.

## Changes

### Modified
- `src/cache/redis.ts:67` - Added mutex lock
- `src/cache/redis.ts:89` - Wait for lock release

## Decisions
- Used redlock pattern for distributed locking
- 5-second lock timeout (based on max query time)

## Context
Production issue #847 - intermittent stale data. Occurred under high load (>1000 req/s).

## Tags
#bugfix #cache #concurrency
```

### Example 3: Refactoring

```markdown
# Extract Email Service

**Date**: 2025-11-13 16:00
**Duration**: ~30 min

## Summary
Extracted email logic into separate service for reusability.

## Changes

### Created
- `src/services/email.ts` - Email service class
- `src/services/email.test.ts` - Unit tests

### Modified
- `src/auth/reset-password.ts:23` - Use EmailService
- `src/notifications/notify.ts:45` - Use EmailService
- `src/auth/verify.ts:67` - Use EmailService

### Deleted
- `src/utils/send-email.ts` - Replaced by service

## Decisions
- Singleton pattern for service instance (connection pooling)
- Template-based API (easier to maintain)

## Tags
#refactor #email #architecture
```

## Output

After running this skill:
1. New session file in `memories/sessions/YYYY-MM/`
2. Updated `memories/memory-status.md` with new entry
3. Concise, factual record of work completed
4. Easy reference for future sessions
