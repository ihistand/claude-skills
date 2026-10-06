# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **skills development repository** for creating and testing Claude Code superpowers skills. Skills are reusable process documentation that carry hard-won practices, and the reasons for them, across different domains.

**Skills in this repo**:
- `sqlanvil-engineering-fundamentals` — **MOVED 2026-07-16** to the public canonical repo [SQLAnvil/agent-skills](https://github.com/SQLAnvil/agent-skills) (`npx skills add SQLAnvil/agent-skills`; local checkout `~/projects-ivan/sqlanvil/agent-skills`; Ivan loads it through the `sqlanvil-toolkit` plugin since 2026-10-05). The directory here is a pointer stub only.
- `dataform-engineering-fundamentals` — **REMOVED 2026-09-15**; the canonical copy lives in the acuantia-gcp-dataform repo.
- `stl-generator` — 3D-printable woodworking jigs and measured replacement parts (threaded light globe, 2026-10-05) via build123d (moved off CadQuery 2026-10-04). Scripts are verified by measuring the built solids, not just by running: the CadQuery versions ran cleanly and built broken parts.
- `acuantia-dataform` — **REMOVED 2026-08-22**: client-specific, so it doesn't belong in a public repo. It now ships in the acuantia-dataform plugin (the production repo dropped its in-repo copy 2026-09-20).

**Note**: this is the ONLY checkout of `ihistand/claude-skills` (consolidated 2026-07-04 at `~/projects-ivan/claude-skills`; gitignored inside the projects-ivan monorepo with its own git history). Commit/push skills here.

**Related Ecosystem**: This repository is part of the broader superpowers framework (https://github.com/obra/superpowers), which provides skills for Claude Code and other AI assistants.

## Repository Structure

```
claude-skills/
├── CLAUDE.md / GEMINI.md / README.md
├── sqlanvil-engineering-fundamentals/README.md  # pointer stub; moved to SQLAnvil/agent-skills
└── stl-generator/                               # build123d jig generator (SKILL.md + references/ + scripts/)
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

[Instructions with their reasons, patterns, and examples; red flags only for failures seen in testing]
```

**Key Principles**:
- Skills change behavior, not just provide information: each one targets failures observed without it
- Give each rule its reason: current models follow a rule they understand and over-apply one that is only emphasized
- Add a red flags section only for failures you saw in testing, each with the reason it matters
- Document common mistakes and correct patterns side-by-side
- Reference related skills for workflow chains

**Working with Claude Code Features**: When developing skills that integrate with Claude Code's CLI, plugins, hooks, MCP servers, or configuration, use the `claude-code-guide` agent for the official documentation.

### Testing Skills

Test skills with subagents before deploying:

1. **RED Phase**: Test scenarios without the skill to capture baseline failures
2. **GREEN Phase**: Write skill addressing observed failures
3. **REFACTOR Phase**: Test same scenarios with the skill to verify effectiveness

**For detailed guidance**: Use the `skill-creator` skill when creating new skills or editing existing ones.

### File Naming Conventions

- Skill directory: `kebab-case-name/`
- Skill definition: `SKILL.md` (required)
- PR documentation: `PR_DESCRIPTION.md` (optional but recommended)

## Related Documentation

- **Main superpowers repo**: https://github.com/obra/superpowers
- **Skill writing guide**: Use the `skill-creator` skill
- **Skill testing guide**: The subagent RED-GREEN-REFACTOR cycle under "Testing Skills" above
- **Claude Code and plugin development**: Use the `claude-code-guide` agent for the official documentation on the CLI, plugins, hooks, MCP servers, skills, and configuration; `claude plugin validate <dir>` checks a plugin or marketplace

## Key Commands

```bash
# View skill content
cat <skill-name>/SKILL.md

# Edit skill
$EDITOR <skill-name>/SKILL.md

# Word count check (skills should be as concise as possible while remaining effective)
wc -w <skill-name>/SKILL.md

# Create new skill directory
mkdir -p new-skill-name && cd new-skill-name
touch SKILL.md PR_DESCRIPTION.md
```

## Important Notes

### Skill Development Philosophy

Skills are **process documentation**, not reference documentation. A good skill:

1. **Explains its rules**: says why each practice matters, so the agent applies it correctly in cases the skill didn't anticipate and can tell when a real exception applies
2. **Holds up under pressure**: still guides correctly when the task is urgent; test this rather than assume it
3. **Catches known failures**: red flags name specific mistakes seen in testing, not every conceivable deviation
4. **Show impact**: Use time math and real-world scenarios to demonstrate value
5. **Chain workflows**: Reference related skills for comprehensive coverage

## Git Workflow

**Author**: Ivan Histand <ivan@badgeretl.com>
**Remote**: Use `origin` (not `github`)

### Standard Commit Pattern

```bash
git add <skill-name>/SKILL.md
git commit -m "feat: enhance <skill-name> with [specific improvement]"
git push origin main
```

## Common Tasks

### Adding a New Skill

1. Create skill directory: `mkdir -p new-skill-name`
2. Create SKILL.md with proper frontmatter
3. Test with subagents (RED-GREEN-REFACTOR, see "Testing Skills" above)
4. Iterate until the with-skill runs fix the failures the baseline showed
5. Document testing approach in PR_DESCRIPTION.md

### Editing Existing Skills

1. Use the `skill-creator` skill for guidance
2. Make changes to SKILL.md
3. Re-run the test scenarios, including the pressure ones, to check the change didn't undo earlier fixes
4. Update PR_DESCRIPTION.md if testing revealed new insights

### Validating Skill Effectiveness

Run Claude Code agents through pressure scenarios:
- Time pressure (urgent deadline)
- Authority pressure (stakeholder waiting)
- Exhaustion (working late at night)

Check that the skill still leads to the right behavior in each scenario, and that it doesn't cause over-correction elsewhere, such as refusing a legitimate exception.
