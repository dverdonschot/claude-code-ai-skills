# Ask Questions About Dutch Statistics and Get Instant Analysis: Building the CBS Analyzer Skill

## The Problem I Wanted to Solve

I wanted to ask Claude simple questions like "When did renewable energy overtake coal in the Netherlands?" and get real answers with data, charts, and statistical analysis. Not vague responses. Not "I don't have access to that data." Real, verified numbers from official sources.

The problem? Netherlands' national statistics (CBS - Centraal Bureau voor de Statistiek) has **thousands** of free datasets going back to 1946. Everything from energy usage to sickness absence to housing prices. All available via their open API at [opendata.cbs.nl](https://opendata.cbs.nl).

But using it meant:
- Reading API documentation
- Writing code to fetch data
- Understanding their dimension system
- Parsing responses
- Loading into pandas
- Then finally analyzing

That's 30 minutes of work before I can even ask my question.

## What If Claude Just... Knew How?

That's what I built. Watch this:

**Me**: "Download dataset 83140NED and tell me when oil overtook coal as the primary energy source in the Netherlands"

**Claude** (using the skill):
- Checks if data is cached locally
- Downloads 5,609 rows spanning 1946-2024
- Explores energy carrier dimensions
- Writes analysis script
- Returns answer: **1960**
  - 1959: Coal = 426.0 PJ, Oil = 371.0 PJ
  - 1960: Coal = 439.6 PJ, Oil = 445.7 PJ

**Next question**: "What about natural gas overtaking oil?"

**Claude**: Already has the data, just analyzes:
- **1974** (the oil crisis year)
  - 1973: Oil = 1,247.1 PJ, Gas = 1,193.5 PJ
  - 1974: Oil = 1,095.1 PJ, Gas = 1,281.2 PJ

**Next**: "When did renewables overtake coal?"

**Claude**: **2020**
- 2019: Coal = 268.9 PJ, Renewables = 227.8 PJ
- 2020: Coal = 172.0 PJ, Renewables = 283.5 PJ
- (Dramatic 36% drop in coal, likely COVID + climate policy)

Three complex data analysis questions. Total time: **under 2 minutes**. All answers backed by official government statistics.

## How This Works: Claude Skills

This is powered by what I call **Claude Skills** - a way to give Claude specialized knowledge without burning your context window.

Here's the key insight: **MCP servers load ALL their tools into EVERY conversation**. Whether you use them or not, they're consuming tokens. It's like carrying every tool in your garage in your pocket, just in case.

Skills are different: **they only load when you invoke them**.

Think of it like this:
- **MCP Server**: "Here are 47 tools you might need" (15KB of context, every conversation)
- **Skill**: "Need CBS data analysis? Here's how" (2KB of context, only when asked)

## The CBS Analyzer Skill in Action

Let me show you exactly what this looks like. I'll walk through a real conversation.

### Question 1: Sickness Absence Analysis

**Me**: "Download dataset 83130NED and analyze if sickness absence significantly changed between 2014 and 2023"

**What happens behind the scenes:**

1. **Skill activates** (loads ~2KB of instructions on how to work with CBS data)

2. **Claude checks for cached data**
   ```bash
   ls data/83130NED/
   # Not found, needs to download
   ```

3. **Gets dataset info**
   ```
   Dataset: Sickness absence of employees; industry, establishment size (2014-2023)
   Total observations: 1,260
   ```

4. **Downloads the data**
   ```bash
   opencbs save 83130NED
   # Saves to: data/83130NED/data.parquet
   ```

5. **Explores the structure**
   - 126 rows per year (different industries and company sizes)
   - Key column: `AandeelWerknemersDatHeeftVerzuimd_1` (Share of employees absent)

6. **Writes analysis script**
   ```python
   # Filters 2014 vs 2023
   # Runs t-test for statistical significance
   # Calculates effect size (Cohen's d)
   ```

7. **Returns comprehensive answer**:
   - **2014**: 42.24% average absence
   - **2023**: 48.75% average absence
   - **Change**: +6.51 percentage points (+15.4% increase)
   - **p-value**: < 0.000001 (highly significant)
   - **Effect size**: Cohen's d = -1.15 (large)

Plus bonus insights:
- Average frequency: 1.00 → 1.33 times per year (+33%)
- Average duration: 6.19 → 8.06 days (+30%)
- Surprisingly, employees attribute LESS to work-related causes in 2023

This is a complete statistical analysis with significance testing. From a simple question.

### Question 2: Energy Transition Timeline

**Me**: "Analyze energy sources over time - when did major transitions happen?"

**Claude**: Already has the skill loaded, downloads different dataset (83140NED)

**Result**: Complete historical timeline
- **1960**: Oil overtook coal (post-war industrialization)
- **1968**: Natural gas overtook coal (Groningen gas field discovery)
- **1974**: Natural gas overtook oil (1973 oil crisis impact)
- **2020**: Renewables overtook coal (climate policy + COVID)
- **2022**: Oil temporarily overtook gas again (Ukraine energy crisis)

Plus a detailed table showing dominant energy source by decade:

```
Year    Coal    Oil      Gas      Renewable    Dominant Source
1946    305.0   57.0     0.0      -            Coal
1960    439.6   445.7    11.9     -            Oil
1975    98.4    998.9    1315.0   -            Natural Gas
2020    172.0   1096.0   1316.8   283.5        Natural Gas
2024    173.4   1041.6   941.2    408.3        Oil
```

All from: "When did energy sources change?"

## The Token Efficiency Story

Here's what makes this powerful. After running both analyses above, I checked my context usage with `/context`:

```
Context Usage: 97k/200k tokens (49%)

⛁ System prompt:     2.5k  (1.3%)
⛁ System tools:     13.7k  (6.9%)
⛁ Messages:         36.0k (18.0%)
⛶ Free space:      103k  (51.4%)
```

**Less than half my context window used** after:
- Downloading two datasets (6,869 total rows)
- Running statistical analysis with scipy
- Creating multiple Python scripts
- Generating detailed reports
- Having a multi-turn conversation

Compare this to an MCP server approach:
- All tool definitions loaded upfront: ~15-20KB
- Every conversation, whether you use them or not
- Multiple tools for each operation

The skill? **2KB, only when invoked.**

## What CBS Data Is Available

CBS (Statistics Netherlands) provides incredible data, all free:

### Energy & Environment
- **83140NED**: Energy supply 1946-2024 (what I used above)
- Renewable energy production by source
- CO2 emissions by sector
- Waste management and recycling

### Labor & Economy
- **83130NED**: Sickness absence by industry (what I used above)
- Employment statistics
- Wages and income
- Business demographics

### Demographics
- Population by age, region, migration background
- Births, deaths, life expectancy
- Households and families

### Housing & Living
- House prices and sales
- Rental prices
- Energy consumption
- Municipal statistics

**Thousands of datasets. 70+ years of history. All free.**

The problem was access. The solution is this skill.

## How the Skill Works Technically

The CBS Analyzer skill is actually a complete application packaged as a "skill":

```
.claude/skills/cbs-analyzer/
├── SKILL.md                # Instructions for Claude
├── scripts/
│   ├── cli.py             # Command-line interface (359 lines)
│   └── client.py          # CBS API client (337 lines)
├── data/
│   ├── 83140NED/          # Cached datasets
│   │   ├── data.parquet
│   │   └── metadata.json
│   └── cache/cache.db     # API response cache
```

**SKILL.md** tells Claude:
- When to use this skill
- How to check for cached data
- Commands available (`opencbs info`, `opencbs save`, etc.)
- How to analyze with pandas
- What format CBS uses for dates (2020JJ00 = year 2020)
- Common pitfalls and solutions

**scripts/cli.py** provides commands:
```bash
opencbs info 83140NED           # Get dataset metadata
opencbs data 83140NED --count   # Count rows
opencbs dimension 83140NED Perioden  # View time periods
opencbs save 83140NED           # Download and cache
```

**scripts/client.py** handles:
- REST API calls to opendata.cbs.nl
- Response caching (24-hour expiry)
- Converting JSON to pandas DataFrames
- Saving to efficient Parquet format

**The brilliance**: Claude reads SKILL.md (2KB), understands the system, uses the tools correctly. No hardcoded logic. Just instructions.

## Setting This Up Yourself

Want this? Here's how:

### Step 1: Clone the Repository

```bash
git clone https://github.com/ewoudtm/ai-skills ~/ai-skills
```

### Step 2: Link to Your Project

```bash
cd ~/your-project
~/ai-skills/setup-skills.sh .
```

The setup script creates symlinks:

```
Setting up skills in: ~/your-project

Creating symlinks in .claude/skills...
  + cbs-analyzer/
  + docs-manager.md
  + honest-feedback.md
  + session-memory.md

✓ 4 skills installed (4 new)
```

### Step 3: Start Using It

Just ask Claude questions:

```
"Use the cbs-analyzer skill to find out if renewable
energy is growing in the Netherlands"
```

Claude will:
1. Load the skill instructions
2. Figure out which dataset to use
3. Download if needed
4. Analyze
5. Answer your question

**That's it.** Three steps. Under 2 minutes.

## Why Symlinks Are Genius

The repository uses symlinks instead of copying files. This means:

**One central repository:**
```
~/ai-skills/.claude/skills/cbs-analyzer/
```

**Many projects link to it:**
```
~/project1/.claude/skills/cbs-analyzer/ → ~/ai-skills/.claude/skills/cbs-analyzer/
~/project2/.claude/skills/cbs-analyzer/ → ~/ai-skills/.claude/skills/cbs-analyzer/
~/project3/.claude/skills/cbs-analyzer/ → ~/ai-skills/.claude/skills/cbs-analyzer/
```

**When I improve the skill:**
```bash
cd ~/ai-skills
git pull origin main
# All projects immediately get the update
```

No npm install. No version management. No copy-paste. Just update once, works everywhere.

## Other Skills in the Repository

The repo includes three more skills:

### docs-manager
Maintains your `docs/` folder. When you make code changes, it:
- Updates relevant documentation
- Creates diagrams with Mermaid
- Prevents duplication through cross-references
- Enforces 200-line maximum per file

**Use when**: You've made significant changes and need docs updated.

### honest-feedback
Gives you direct technical assessment without sugarcoating:
- "This approach has problems: [specific issues]"
- "I don't have enough information to answer confidently"
- "These requirements conflict: [details]"

**Use when**: You need objective code review or architecture evaluation.

### session-memory
Documents your work in concise session logs:
```
memories/sessions/2025-11/energy-analysis.md

## Summary
Analyzed Dutch energy transitions using CBS data

## Changes
- Created: analyze_energy_simple.py
- Modified: scripts/client.py:127 - Added caching

## Decisions
- Use Parquet for storage (more efficient than CSV)

## Tags
#cbs #energy #analysis
```

**Use when**: You want continuity across sessions or project history tracking.

## Creating Your Own Skills

Want to create a custom skill? Here's the template:

```markdown
---
name: my-skill
description: What this does
---

# My Skill

## Context
When to use this skill:
- Situation 1
- Situation 2

## Process
1. First, do this
2. Then, do this
3. Finally, return this

## Guidelines
- Important rule 1
- Important rule 2

## Output
What the user gets
```

Save it in the central repo:
```bash
echo "[content]" > ~/ai-skills/.claude/skills/my-skill.md
```

All your linked projects get it instantly.

### Skill Complexity Levels

**Simple** (just markdown):
```
honest-feedback.md          # Pure instructions
```

**Medium** (markdown + helpers):
```
session-memory.md           # Instructions + file templates
```

**Complex** (full application):
```
cbs-analyzer/
├── SKILL.md               # Instructions
├── scripts/               # Python tools
└── data/                  # Cache storage
```

Scale to your needs.

## Real Results: What I've Learned

Since building this, I've analyzed:

**Energy data**:
- Confirmed Netherlands went coal → oil (1960) → gas (1974)
- Found renewables finally overtook coal in 2020
- Discovered 2022 energy crisis reversed 50 years of oil decline

**Labor data**:
- Sickness absence increased 15% (2014-2023)
- Employees absent more frequently AND longer
- Work-related attribution actually decreased (surprising)

**All from casual questions.** No documentation reading. No manual data wrangling.

The skill handles:
- Finding the right dataset
- Downloading efficiently
- Understanding CBS's dimension system
- Date format quirks (2020JJ00 = year)
- Statistical analysis
- Clear reporting

I just ask questions.

## When to Use Skills vs MCP

Both have their place:

### Use MCP When:
- You need real-time services (web search, APIs)
- Tools are used constantly
- It's fundamental infrastructure
- You're providing it to others

### Use Skills When:
- Specialized domain knowledge
- Used occasionally, not constantly
- Want zero cost until needed
- Share across multiple projects
- Need version control of behavior

### Use Both:
Skills can invoke MCP tools! A skill provides the workflow, MCP provides the capabilities.

## The Philosophy

Traditional approach: "Let me find an API, read the docs, write some code..."

Skills approach: "Just ask the question."

The knowledge about CBS data - how to access it, how to structure it, how to analyze it - is encoded once. In markdown. Then available everywhere, forever.

New dataset? Update the skill. All projects benefit.

Better analysis approach? Update the skill. Everyone gets it.

Found a bug? Fix once. Works everywhere.

This is how we should extend LLMs: **specialized knowledge, on-demand, automatically distributed.**

## Try It Yourself

Ready to analyze Dutch statistics with natural language?

```bash
# 1. Clone
git clone https://github.com/ewoudtm/ai-skills ~/ai-skills

# 2. Setup
cd ~/your-project
~/ai-skills/setup-skills.sh .

# 3. Ask Claude
"Use cbs-analyzer to show me population growth trends"
"Analyze renewable energy adoption rates"
"Compare house prices between regions"
```

The data is there. The tools are there. The skill makes it accessible.

## What's Next

I'm building more skills:

**Financial data**: CBS also has economic indicators, GDP, trade statistics
**Visualizations**: Automatic chart generation for trends
**Comparisons**: Multi-dataset analysis (compare energy vs economy)
**Regional**: Provincial and municipal breakdowns

And you can too. Fork the repo. Add your domain. Share it back.

The repository is open: **[github.com/ewoudtm/ai-skills](https://github.com/ewoudtm/ai-skills)**

## Bottom Line

I wanted to ask Claude questions about Dutch statistics and get real answers. Not "I don't have that data." Not "Let me help you write code to fetch that."

Just: **question → answer.**

The CBS Analyzer skill does this. For thousands of datasets. Going back 70+ years. All free government data.

And it costs almost nothing in tokens because it only loads when needed.

That's the power of skills. That's why I built this.

Try it. You'll wonder how you lived without it.

---

## Resources

- **Repository**: [github.com/ewoudtm/ai-skills](https://github.com/ewoudtm/ai-skills)
- **CBS Open Data**: [opendata.cbs.nl](https://opendata.cbs.nl)
- **Full Docs**: See `docs/` in the repository
- **Questions?**: Open an issue on GitHub

---

*All statistics in this article are real results from the CBS Analyzer skill. The energy transition dates, sickness absence rates, and context usage are from actual Claude Code sessions. Nothing is simulated.*
