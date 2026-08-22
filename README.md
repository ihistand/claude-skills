# claude-skills

[Agent Skills](https://agentskills.io) by Ivan Histand for Claude Code and other coding agents.
Each skill is a `SKILL.md` that loads when its domain comes up and keeps the agent on a
disciplined workflow — tests first, safe commands, no shortcuts under time pressure.

## Install

With the [`skills`](https://skills.sh) CLI (works for Claude Code, Cursor, Codex, and others):

```bash
npx skills add ihistand/claude-skills                 # pick from the list
npx skills add ihistand/claude-skills -s dataform-engineering-fundamentals
```

Or by hand — Claude Code reads skills from `~/.claude/skills/<name>/SKILL.md` (user-wide) or
`.claude/skills/<name>/SKILL.md` (one project):

```bash
git clone https://github.com/ihistand/claude-skills
ln -s "$PWD/claude-skills/dataform-engineering-fundamentals" ~/.claude/skills/
```

## Skills

| Skill | Use it when |
|-------|-------------|
| [dataform-engineering-fundamentals](dataform-engineering-fundamentals/) | Writing or troubleshooting BigQuery Dataform: SQLX models, source declarations, assertions. Enforces TDD (assertions before implementation), `--schema-suffix dev` + `--dry-run` before anything touches production, `${ref()}` over hardcoded table paths, mandatory `columns: {}` documentation, and layered architecture. Cross-links to the SQLAnvil skill for Postgres/Supabase work. |
| [stl-generator](stl-generator/) | Designing 3D-printable woodworking jigs and fixtures (circle-cutting guides, angle wedges, spacing blocks, alignment fixtures) with CadQuery. Ships reference patterns and ready scripts; tuned for an Elegoo Neptune 4 Pro. |

Working with SQLAnvil instead of Dataform? That skill lives in its own repo:
`npx skills add SQLAnvil/agent-skills` ([SQLAnvil/agent-skills](https://github.com/SQLAnvil/agent-skills)).
The `sqlanvil-engineering-fundamentals/` folder here is only a pointer to it.

The Dataform skill is also bundled in the
[dataform-toolkit](https://github.com/ihistand/claude-plugins) Claude Code plugin, together with
`/dataform-test`, `/dataform-deploy`, `/dataform-new-table`, and `/dataform-etl` slash commands.

## How these skills are written

They follow the [superpowers](https://github.com/obra/superpowers) approach: a skill is process
documentation that enforces discipline, not a reference page. Each one carries explicit counters to
"just this once" rationalizations, a red-flags section that catches an agent about to deviate,
wrong-vs-right examples, and a time-pressure protocol. Skills are tested RED-GREEN-REFACTOR with
subagents — scenarios run without the skill to capture the failures, then with it to confirm they
stop. See [CLAUDE.md](CLAUDE.md) for the development workflow.

## Author

Ivan Histand — [ivan@histand.net](mailto:ivan@histand.net) · [github.com/ihistand](https://github.com/ihistand) · [histand.net](https://histand.net)
