# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **skills development repository** for creating and testing Claude Code superpowers skills. Skills are reusable process documentation that enforce discipline and best practices across different domains.

**Skills in this repo**:
- `sqlanvil-engineering-fundamentals` — **MOVED 2026-07-16** to the public canonical repo [SQLAnvil/agent-skills](https://github.com/SQLAnvil/agent-skills) (`npx skills add SQLAnvil/agent-skills`; local checkout `~/projects-ivan/sqlanvil-agent-skills`, symlink retargeted there). The directory here is a pointer stub only.
- `dataform-engineering-fundamentals` — BigQuery Dataform TDD/safety/documentation discipline (the original skill here).
- `acuantia-dataform`, `stl-generator` — project-specific skills.

**Note**: this is the ONLY checkout of `ihistand/claude-skills` (consolidated 2026-07-04 at `~/projects-ivan/claude-skills`; gitignored inside the projects-ivan monorepo with its own git history). Commit/push skills here.

**Related Ecosystem**: This repository is part of the broader superpowers framework (https://github.com/obra/superpowers), which provides skills for Claude Code and other AI assistants.

## Repository Structure

```
claude-skills/
├── CLAUDE.md / GEMINI.md / README.md
├── sqlanvil-engineering-fundamentals/SKILL.md   # sqlanvil delta guide (synced per engine release)
├── dataform-engineering-fundamentals/SKILL.md   # BigQuery Dataform TDD discipline (original skill)
├── acuantia-dataform/                           # project-specific
└── stl-generator/                               # project-specific
```

## Skill Development Workflow

### Understanding Superpowers Skills

Skills are markdown files that provide specialized instructions to Claude Code agents. They follow a specific structure:

```markdown
---
name: skill-name
description: Brief description used by skill selection system
---

# Skill Title

[Comprehensive instructions, patterns, red flags, and examples]
```

**Key Principles**:
- Skills enforce discipline, not just provide information
- Must be bulletproof against rationalization ("just this once", "too urgent")
- Include red flags section to catch agents about to deviate
- Document common mistakes and correct patterns side-by-side
- Reference related skills for workflow chains

**Working with Claude Code Features**: When developing skills that integrate with Claude Code's CLI, plugins, hooks, MCP servers, or configuration, use `superpowers-developing-for-claude-code:working-with-claude-code` for comprehensive official documentation.

### Testing Skills (Critical)

Skills MUST be tested before deployment using the `superpowers:testing-skills-with-subagents` workflow:

1. **RED Phase**: Test scenarios WITHOUT the skill to capture baseline failures
2. **GREEN Phase**: Write skill addressing observed failures
3. **REFACTOR Phase**: Test same scenarios WITH skill to verify effectiveness

**For detailed testing guidance**: Use the `superpowers:writing-skills` skill when creating new skills or editing existing ones.

### File Naming Conventions

- Skill directory: `kebab-case-name/`
- Skill definition: `SKILL.md` (required)
- PR documentation: `PR_DESCRIPTION.md` (optional but recommended)

## Working with dataform-engineering-fundamentals

### Skill Purpose

Domain-specific adaptation of TDD principles for Google Cloud Dataform (BigQuery data transformation pipelines). Enforces:
- Test-driven development for data transformations
- Safety practices (`--schema-suffix dev`, `--dry-run`)
- Dependency management (ALWAYS `${ref()}`, NEVER hardcoded table paths)
- Comprehensive documentation (`columns: {}` blocks mandatory)
- Proper architecture (layered structure, file naming, schema configuration)

### Key Files

**SKILL.md** (~356 lines; last substantive overhaul 2026-06-06 — cut redundancy, fixed uniqueKey/ref(), added incremental internals): non-negotiable safety practices (6), architecture patterns (layering, incremental internals, assertions, .sqlx declarations), TDD workflow, documentation standards (`columns: {}`), quick-reference commands, rationalization table, red flags, time-pressure protocol, troubleshooting. Cross-links to `sqlanvil-engineering-fundamentals` for Postgres/Supabase work.

**PR_DESCRIPTION.md**: not currently present — write it if/when contributing the skill upstream (documents testing approach and results).

### Editing the Skill

When modifying `SKILL.md`:

1. **Understand the domain**: This skill targets Dataform/BigQuery developers who face time pressure to skip best practices
2. **Maintain rigor**: Don't soften the discipline-enforcing language (red flags, "non-negotiable", rationalization counters)
3. **Test changes**: Use `superpowers:testing-skills-with-subagents` to verify modifications don't introduce loopholes
4. **Preserve cross-references**: Skill integrates with `superpowers:test-driven-development`, `superpowers:brainstorming`, `superpowers:systematic-debugging`, and `superpowers:root-cause-tracing`

## Contributing Skills Upstream

When ready to contribute `dataform-engineering-fundamentals` (or other skills) to the main superpowers repository:

### Prerequisites

1. Skill has been thoroughly tested with subagents
2. PR_DESCRIPTION.md documents testing approach and results
3. Skill follows superpowers conventions (structure, tone, rigor)

### Contribution Process

```bash
# Navigate to superpowers cache
cd ~/.claude/plugins/cache/superpowers

# Create pull request
gh pr create \
  --repo obra/superpowers \
  --title "Add dataform-engineering-fundamentals skill" \
  --body-file ~/projects-ivan/claude-skills/dataform-engineering-fundamentals/PR_DESCRIPTION.md
```

**Alternative**: Manually create PR at https://github.com/obra/superpowers/pull/new/[branch-name]

### Skill Quality Checklist

Before submitting:
- ☐ Tested with RED-GREEN-REFACTOR cycle
- ☐ No new rationalizations emerged during testing
- ☐ Cross-reference integration verified
- ☐ Common mistakes section includes corrections
- ☐ Red flags section catches deviation attempts
- ☐ Rationalization table addresses common excuses
- ☐ Time pressure protocol provides clear guidance
- ☐ Description in frontmatter accurately summarizes enforcement areas

## Related Documentation

- **Main superpowers repo**: https://github.com/obra/superpowers
- **Superpowers installation**: See `../.codex_INSTALL.md` for Codex setup instructions
- **Skill writing guide**: Use `superpowers:writing-skills` skill
- **Skill testing guide**: Use `superpowers:testing-skills-with-subagents` skill
- **Claude Code development**: Use `superpowers-developing-for-claude-code:working-with-claude-code` for comprehensive documentation on Claude Code CLI, plugins, hooks, MCP servers, skills, and configuration
- **Plugin development**: Use `superpowers-developing-for-claude-code:developing-claude-code-plugins` when creating, modifying, testing, or releasing Claude Code plugins

## Key Commands

```bash
# View skill content
cat dataform-engineering-fundamentals/SKILL.md

# Edit skill
$EDITOR dataform-engineering-fundamentals/SKILL.md

# Word count check (skills should be as concise as possible while remaining effective)
wc -w dataform-engineering-fundamentals/SKILL.md

# Create new skill directory
mkdir -p new-skill-name && cd new-skill-name
touch SKILL.md PR_DESCRIPTION.md
```

## Important Notes

### Skill Development Philosophy

Skills are **process documentation that enforces discipline**, not reference documentation. They must:

1. **Resist rationalization**: Include explicit counters to "just this once" thinking
2. **Be bulletproof under pressure**: Work especially when tired, stressed, or rushed
3. **Fail fast**: Catch deviations immediately with red flags sections
4. **Show impact**: Use time math and real-world scenarios to demonstrate value
5. **Chain workflows**: Reference related skills for comprehensive coverage

### Integration with Acuantia Projects

The `dataform-engineering-fundamentals` skill was developed against the real-world `acuantia-gcp-dataform` project (see parent directory `CLAUDE.md` for Acuantia project documentation). This ensures the skill addresses actual production challenges, not theoretical best practices.

**Testing context**: The skill was validated by testing Claude Code agents working on Dataform pipelines under realistic time pressure scenarios.

## Git Workflow

**Author**: Ivan Histand <ivan@badgeretl.com>
**Remote**: Use `origin` (not `github`)

### Standard Commit Pattern

```bash
git add dataform-engineering-fundamentals/SKILL.md
git commit -m "feat: enhance dataform skill with [specific improvement]"
git push origin main
```

## Common Tasks

### Adding a New Skill

1. Create skill directory: `mkdir -p new-skill-name`
2. Create SKILL.md with proper frontmatter
3. Test with `superpowers:testing-skills-with-subagents`
4. Iterate until bulletproof against rationalization
5. Document testing approach in PR_DESCRIPTION.md
6. Contribute upstream when ready

### Editing Existing Skills

1. Use `superpowers:writing-skills` skill for guidance
2. Make changes to SKILL.md
3. Re-test with pressure scenarios to verify no loopholes introduced
4. Update PR_DESCRIPTION.md if testing revealed new insights

### Validating Skill Effectiveness

Run Claude Code agents through pressure scenarios:
- Time pressure (urgent deadline)
- Authority pressure (stakeholder waiting)
- Exhaustion (working late at night)

Skills must enforce discipline in ALL scenarios.
