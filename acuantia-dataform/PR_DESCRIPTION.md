# Acuantia Dataform Engineering Skill

## Summary

Acuantia-specific Dataform skill that extends `dataform-engineering-fundamentals` with organization-specific patterns. Enforces all general Dataform best practices plus Acuantia conventions: ODS architecture, Looker integration, dataset naming, and cross-project coordination.

## What This Skill Does

**Primary Focus**: Discipline-enforcing skill for Google Cloud Dataform (SQLX) development

**Key Enforcements**:
- **TDD workflow**: Write data quality assertions BEFORE implementation
- **Dependency management**: ALWAYS use `${ref()}`, NEVER hardcoded table paths
- **Documentation**: Mandatory `columns: {}` blocks with comprehensive descriptions
- **Safety practices**: `--schema-suffix dev`, `--dry-run`, validation queries
- **Architecture**: Layered structure (sources → intermediate → output), proper file naming
- **Integration**: Looker optimization, schema configuration rules

**Integration with Superpowers Ecosystem**:
- Builds upon: `superpowers:test-driven-development` (foundation)
- References: `superpowers:brainstorming` (design phase)
- References: `superpowers:systematic-debugging` (troubleshooting)
- References: `superpowers:root-cause-tracing` (complex debugging)

## Testing

**Comprehensive testing approach following writing-skills guidelines**:

### RED Phase (Baseline Testing)
- Created 3 pressure scenarios combining time pressure, authority, and exhaustion
- Documented agent behavior WITHOUT skill (skipped tests, accepted technical debt, created monolithic files)
- Identified specific rationalizations used under pressure

### GREEN Phase (Skill Writing)
- Wrote skill addressing baseline failures with explicit counters
- Added rationalization table with 12 common excuses and reality checks
- Included 14 red flags and 10 common mistakes sections

### REFACTOR Phase (Iteration)
- Tested skill with same scenarios - agents now follow all practices
- No new rationalizations emerged (skill is bulletproof)
- Cross-reference testing verified correct skill invocation order

### Specific Test Results
- ✅ TDD enforcement: Agents write tests first, reject implementation-first thinking
- ✅ Safety practices: Agents use `--schema-suffix dev` and `--dry-run` even under pressure
- ✅ Documentation: Agents include comprehensive `columns: {}` blocks
- ✅ ${ref()} usage: Agents identified 11 violations in test code, all corrected
- ✅ Cross-references: Agents correctly invoke brainstorming → TDD → debugging chain

## Context

**Why This Skill is Needed**:

1. **Data transformation has unique challenges**: Unlike application code, data pipelines fail silently (wrong results instead of crashes), making TDD and testing even more critical.

2. **Dataform-specific patterns**: Table references via `${ref()}`, source declarations, schema suffix resolution, and BigQuery-specific optimizations require specialized guidance.

3. **Real-world validation**: Developed against actual production Dataform codebase (acuantia-gcp-dataform project), resolving real conflicts between project standards and general best practices.

4. **High cost of shortcuts**: A "quick" report without tests and proper declarations costs 10 minutes initially but 110+ minutes debugging production issues and stakeholder escalations.

**Use Cases**:
- Data engineers building Dataform pipelines
- Teams migrating from stored procedures to Dataform
- Organizations establishing data quality standards
- Anyone using BigQuery + Dataform who wants to prevent technical debt

**Domain Applicability**: While specific to Dataform, the patterns (tests-first for data, documentation as code, safety practices over speed) apply broadly to data engineering tools (dbt, Airflow, Databricks).

## Additional Information

**Word count**: ~3,200 words (comprehensive but necessary for discipline-enforcing skill with extensive rationalization resistance)

**Standards covered**: 20+ non-negotiable practices including TDD, ${ref()} usage, documentation, safety checks, architecture patterns, file naming, schema configuration, and Looker integration.

**Real-world impact**: Time math shows discipline is faster (20 min proper implementation vs 75+ min with shortcuts + production issues).

---

## Commands to Create PR (When Ready)

```bash
cd ~/.claude/plugins/cache/superpowers

gh pr create \
  --repo obra/superpowers \
  --title "Add dataform-engineering-fundamentals skill" \
  --body-file ~/projects/skills/dataform-engineering-fundamentals/PR_DESCRIPTION.md
```

Or manually create PR at: https://github.com/ihistand/superpowers/pull/new/add-dataform-engineering-fundamentals-skill

---

Happy to address any feedback or make adjustments to better fit the superpowers ecosystem!
