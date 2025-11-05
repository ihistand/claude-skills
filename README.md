# Claude Skills Development

A repository for developing and testing [Claude Code](https://claude.com/claude-code) superpowers skills.

## What are Skills?

Skills are reusable process documentation that enforce discipline and best practices across different domains. They provide specialized instructions to Claude Code agents, ensuring consistent workflows even under time pressure or exhaustion.

**Key Characteristics**:
- Discipline-enforcing, not just informational
- Bulletproof against rationalization ("just this once", "too urgent")
- Include red flags to catch deviations before they happen
- Tested against pressure scenarios (deadlines, authority, exhaustion)

## Repository Contents

### dataform-engineering-fundamentals

A comprehensive skill for BigQuery Dataform development that adapts TDD principles to data transformation pipelines.

**Enforces**:
- ✅ Test-driven development (write assertions before implementation)
- ✅ Safety practices (`--schema-suffix dev`, `--dry-run`, validation queries)
- ✅ Dependency management (ALWAYS `${ref()}`, NEVER hardcoded table paths)
- ✅ Documentation standards (mandatory `columns: {}` blocks)
- ✅ Proper architecture (layered structure, file naming conventions)
- ✅ Looker integration patterns

**Size**: ~3,200 words of discipline-enforcing guidance

**Testing**: Validated using RED-GREEN-REFACTOR methodology with pressure scenarios

## Project Structure

```
claude-skills/
├── README.md                                  # This file
├── CLAUDE.md                                  # Development guide for Claude Code
├── dataform-engineering-fundamentals/
│   ├── SKILL.md                              # Complete skill definition
│   └── PR_DESCRIPTION.md                     # Pull request documentation
```

## Development Workflow

### Creating New Skills

1. **Create skill directory**:
   ```bash
   mkdir -p new-skill-name
   cd new-skill-name
   ```

2. **Create SKILL.md with frontmatter**:
   ```markdown
   ---
   name: new-skill-name
   description: Brief description for skill selection system
   ---

   # Skill Title

   [Comprehensive instructions...]
   ```

3. **Test thoroughly** using `superpowers:testing-skills-with-subagents`:
   - RED phase: Test WITHOUT skill to capture failures
   - GREEN phase: Write skill addressing failures
   - REFACTOR phase: Test WITH skill to verify effectiveness

4. **Document testing** in PR_DESCRIPTION.md

### Contributing Upstream

When ready to contribute to the main [superpowers repository](https://github.com/obra/superpowers):

```bash
cd ~/.claude/plugins/cache/superpowers

gh pr create \
  --repo obra/superpowers \
  --title "Add [skill-name] skill" \
  --body-file ~/path/to/PR_DESCRIPTION.md
```

## Skill Development Principles

### Must-Haves

- **Bulletproof against rationalization**: Counter common excuses explicitly
- **Red flags section**: Catch agents about to deviate from the process
- **Common mistakes**: Show wrong vs. correct patterns side-by-side
- **Time pressure protocol**: Work especially when tired/rushed
- **Real-world validation**: Test against actual production scenarios

### Quality Checklist

Before submitting:
- ☐ Tested with RED-GREEN-REFACTOR cycle
- ☐ No new rationalizations emerged during testing
- ☐ Cross-reference integration verified (related skills work together)
- ☐ Common mistakes section includes corrections
- ☐ Red flags section catches deviation attempts
- ☐ Rationalization table addresses common excuses
- ☐ Description accurately summarizes enforcement areas

## Related Resources

- **Main superpowers repo**: https://github.com/obra/superpowers
- **Claude Code**: https://claude.com/claude-code
- **Development guide**: See [CLAUDE.md](CLAUDE.md) for detailed instructions

## Skills in This Repository

| Skill | Description | Status |
|-------|-------------|--------|
| [dataform-engineering-fundamentals](dataform-engineering-fundamentals/) | Generic BigQuery Dataform TDD workflow enforcement (suitable for upstream contribution) | ✅ Complete |
| [acuantia-dataform](acuantia-dataform/) | Acuantia-specific Dataform patterns (extends dataform-engineering-fundamentals with ODS, Looker integration, dataset conventions) | ✅ Complete |

## Author

**Ivan Histand** - Sr Data Architect

- GitHub: [@ihistand](https://github.com/ihistand)
- Email: ihistand@rotoplas.com

## License

Skills are intended for contribution to the [obra/superpowers](https://github.com/obra/superpowers) repository, which uses its own license terms.
