# claude-skills

[Agent Skills](https://agentskills.io) by Ivan Histand for Claude Code and other coding agents.
Each skill is a `SKILL.md` that loads when its domain comes up and keeps the agent on a
disciplined workflow — tests first, safe commands, no shortcuts under time pressure.

## Install

With the [`skills`](https://skills.sh) CLI (works for Claude Code, Cursor, Codex, and others):

```bash
npx skills add ihistand/claude-skills -s stl-generator
```

Or by hand — Claude Code reads skills from `~/.claude/skills/<name>/SKILL.md` (user-wide) or
`.claude/skills/<name>/SKILL.md` (one project):

```bash
git clone https://github.com/ihistand/claude-skills
ln -s "$PWD/claude-skills/stl-generator" ~/.claude/skills/
```

## Skills

| Skill | Use it when |
|-------|-------------|
| [stl-generator](stl-generator/) | Designing 3D-printable woodworking jigs and fixtures (circle-cutting trammels, angle wedges, spacing blocks, drilling guides, alignment fixtures) with [build123d](https://github.com/gumyr/build123d). Ships tested ready scripts and a print-readiness check that refuses STLs that would misprint. Defaults to an Elegoo Neptune 4 Pro's bed; `--bed` sets any other. Needs Python with build123d (`uv run --with build123d` works with no setup). |

### Elsewhere

- **sqlanvil-engineering-fundamentals** lives in its own public repo:
  `npx skills add SQLAnvil/agent-skills` ([SQLAnvil/agent-skills](https://github.com/SQLAnvil/agent-skills)).
  The `sqlanvil-engineering-fundamentals/` folder here is only a pointer to it.
- **dataform-engineering-fundamentals** was retired from this repo and from the
  [ihistand/claude-plugins](https://github.com/ihistand/claude-plugins) marketplace in
  September 2026, and is no longer published.
- **stl-generator** is also packaged as the `stl-generator-toolkit` plugin in
  [ihistand/claude-plugins](https://github.com/ihistand/claude-plugins), with
  `/stl-circle-jig`, `/stl-angle-wedge`, `/stl-spacing-block`, and `/stl-generate` commands.

## How these skills are written

They follow the [superpowers](https://github.com/obra/superpowers) approach: a skill is process
documentation that enforces discipline, not a reference page. Each one carries explicit counters to
"just this once" rationalizations, a red-flags section that catches an agent about to deviate,
wrong-vs-right examples, and a time-pressure protocol. Skills are tested RED-GREEN-REFACTOR with
subagents — scenarios run without the skill to capture the failures, then with it to confirm they
stop. See [CLAUDE.md](CLAUDE.md) for the development workflow.

## Author

Ivan Histand — [ivan@histand.net](mailto:ivan@histand.net) · [github.com/ihistand](https://github.com/ihistand) · [histand.net](https://histand.net)
