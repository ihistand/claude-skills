---
name: acuantia-dataform
description: Use when working on Acuantia's BigQuery Dataform pipeline (acuantia-gcp-dataform project) - enforces all dataform-engineering-fundamentals practices plus Acuantia-specific patterns: ODS two-arg ref() syntax, looker_ filename prefix for Looker tables, Looker integration context, acuantia dataset conventions, and coordination with looker/callrail_data_export/dialpad_data_integration projects
---

# Acuantia Dataform Engineering

## Overview

**REQUIRED FOUNDATION:** This skill builds upon `dataform-engineering-fundamentals`. All general Dataform best practices from that skill apply here. This skill adds Acuantia-specific patterns and integration context.

**Core principle**: Safety practices and proper architecture are NEVER optional in Dataform development, regardless of time pressure or business urgency.

**TDD Foundation:** Both this skill and `dataform-engineering-fundamentals` build upon superpowers:test-driven-development. All TDD principles from that skill apply to Dataform development.

Time pressure does not justify skipping safety checks or creating technical debt. The time "saved" by shortcuts gets multiplied into hours of debugging, broken dependencies, and production issues.

## When to Use

Use this skill for ANY Dataform work:
- Creating new SQLX transformations
- Modifying existing tables
- Adding data sources
- Troubleshooting pipeline failures
- "Quick" reports or ad-hoc analysis

**Especially** use when:
- Under time pressure or deadlines
- Stakeholders are waiting
- Working late at night (exhausted)
- Tempted to "just make it work"

**Related Skills**:
- **Before designing new features**: Use superpowers:brainstorming to refine requirements into clear designs before writing any code
- **When troubleshooting failures**: Use superpowers:systematic-debugging for structured problem-solving
- **When debugging complex issues**: Use superpowers:root-cause-tracing to trace errors back to their source

## Non-Negotiable Safety Practices

These are ALWAYS required. No exceptions for deadlines, urgency, or "simple" tasks:

### 1. Always Use `--schema-suffix dev` for Testing

```bash
# WRONG: Testing in production
dataform run --actions my_table

# CORRECT: Test in dev first
dataform run --schema-suffix dev --actions my_table
```

**Why**: Writes to `looker_dev.my_table` instead of `looker_prod.my_table`. Allows safe testing without impacting production data or dashboards.

### 2. Always Use `--dry-run` Before Execution

```bash
# Check compilation
dataform compile

# Validate SQL without executing
dataform run --schema-suffix dev --dry-run --actions my_table

# Only then execute
dataform run --schema-suffix dev --actions my_table
```

**Why**: Catches SQL errors, missing dependencies, and cost estimation before using BigQuery slots.

### 3. Source Declarations Before ref()

**WRONG**: Using tables without source declarations
```sql
-- This will break dependency tracking
FROM `acuantia.callrail_api.calls`
```

**CORRECT**: Create source declaration first
```sql
-- definitions/sources/callrail/calls.sqlx
config {
  type: "declaration",
  database: "acuantia",
  schema: "callrail_api",
  name: "calls"
}

-- Then reference it
FROM ${ref("calls")}
```

### 4. ALWAYS Use ${ref()} - NEVER Hardcoded Table Paths

**WRONG**: Hardcoded table paths
```sql
-- NEVER do this
FROM `acuantia.dialpad_api.calls`
FROM `acuantia.looker_prod.customer_metrics`
SELECT * FROM acuantia.ods.sap_customers
```

**CORRECT**: Always use ${ref()}
```sql
-- Create source declaration first, then reference
FROM ${ref("calls")}
FROM ${ref("customer_metrics")}
SELECT * FROM ${ref("sap_customers")}
```

**Why**:
- Dataform tracks dependencies automatically with ref()
- Hardcoded paths break dependency graphs
- ref() enables --schema-suffix to work correctly
- Refactoring is easier when references are managed

**Exception**: None. There is NO valid reason to use hardcoded table paths in SQLX files.

### 5. Proper ref() Syntax

**WRONG**: Including schema in ref() for most tables
```sql
FROM ${ref("magento_rotoplas_me_22_prod", "sales_order")}
```

**CORRECT**: Use single argument when source declared
```sql
FROM ${ref("sales_order")}
```

**SPECIAL CASE - ODS Tables**: Use two-argument ref() for ODS to avoid suffix duplication
```sql
-- Correct for ODS tables
FROM ${ref("ods", "sap_customers")}
-- NOT ${ref("sap_customers")} - this would create ods_dev_dev with --schema-suffix dev
```

**Why**:
- Single-argument ref() works for most tables
- Two-argument ref() needed for ODS architecture (prevents ods_dev_dev)
- ODS is special: `acuantia.ods` is source of truth, `ods_dev`/`ods_prod` are staging

### 6. Basic Validation Queries

Always verify your output:
```bash
# Check row counts
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`acuantia.looker_dev.my_table\`"

# Check for nulls in critical fields
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`acuantia.looker_dev.my_table\`
   WHERE key_field IS NULL"
```

**Why**: Catches silent failures (empty tables, null values, bad joins) immediately.

## Architecture Patterns (Not Optional)

Even for "quick" work, follow these patterns:

### Layered Structure

```
definitions/
  sources/          # External data declarations
  intermediate/     # Transformations and business logic
  output/           # Final tables for consumption
    looker/         # Looker-specific views
    reports/        # Ad-hoc reports
```

**Don't**: Create monolithic queries directly in output layer

**Do**: Break into intermediate steps for reusability and testing

### Incremental vs Full Refresh

```sql
config {
  type: "incremental",
  uniqueKey: "order_id",
  bigquery: {
    partitionBy: "DATE(order_date)",
    clusterBy: ["customer_id", "product_id"]
  }
}
```

**When to use incremental**: Tables that grow daily (events, transactions, logs)

**When to use full refresh**: Small dimension tables, aggregations with lookback windows

### Dataform Assertions

```sql
config {
  type: "table",
  assertions: {
    uniqueKey: ["call_id"],
    nonNull: ["customer_phone_number", "start_time"],
    rowConditions: ["duration >= 0"]
  }
}
```

**Why**: Catches data quality issues automatically during pipeline runs.

### Source Declarations: Prefer .sqlx Files

**STRONGLY PREFER**: .sqlx files for ALL new declarations
```sql
-- definitions/sources/callrail/calls.sqlx
config {
  type: "declaration",
  database: "acuantia",
  schema: "callrail_api",
  name: "calls",
  columns: {
    call_id: "Unique call identifier from Dialpad API",
    // ... more columns
  }
}
```

**ACCEPTABLE (legacy only)**: .js files for existing declarations
```javascript
// definitions/sources/ods_declarations.js (existing file)
declare({
  database: "acuantia",
  schema: "ods",
  name: "sap_customers"
});
```

**Rule**: ALL NEW source declarations MUST be .sqlx files. Existing .js declarations can remain but should be migrated to .sqlx when modifying them.

**Why**: .sqlx files support column documentation, are more maintainable, and integrate better with Dataform's dependency tracking.

### File Naming Conventions

**Looker Tables**: All files in `definitions/output/looker/` MUST be prefixed with `looker_`

```sql
-- CORRECT
definitions/output/looker/looker_customer_metrics.sqlx
definitions/output/looker/looker_sales_summary.sqlx

-- WRONG
definitions/output/looker/customer_metrics.sqlx
definitions/output/looker/sales_summary.sqlx
```

**Why**: Makes it easy to identify Looker-specific tables and prevents naming conflicts.

### Schema Configuration Rules

**Operations**: Files in `definitions/operations/` should NOT include `schema:` config
```sql
-- CORRECT
config {
  type: "operations",
  tags: ["daily"]
}

-- WRONG
config {
  type: "operations",
  schema: "dataform",  // DON'T specify schema
  tags: ["daily"]
}
```

**Tests/Assertions**: Files in `definitions/test/` should NOT include `schema:` config
```sql
-- CORRECT
config {
  type: "assertion",
  description: "Check for duplicates"
}

-- WRONG
config {
  type: "assertion",
  schema: "dataform_assertions",  // DON'T specify schema
  description: "Check for duplicates"
}
```

**Why**: Operations live in the default `dataform` schema and assertions live in `dataform_assertions` schema (configured in `workflow_settings.yaml`). Specifying schema explicitly can cause conflicts.

### Looker Integration Context

Tables in `definitions/output/looker/` are consumed by the Google Looker reporting system.

**Key considerations**:
- Add partitioning/clustering for query performance
- Use descriptive column names (Looker dimension names derive from these)
- Include comprehensive column descriptions (sync to Looker metadata)
- Consider Looker user query patterns when designing schema
- Reference the `looker/` project directory for existing dashboard patterns

**Example Looker-optimized config**:
```sql
config {
  type: "table",
  schema: "looker_prod",
  tags: ["looker", "daily"],
  bigquery: {
    partitionBy: "DATE(order_date)",
    clusterBy: ["customer_id", "region"]
  }
}
```

## Documentation Standards (Non-Negotiable)

All tables with `type: "table"` MUST include comprehensive `columns: {}` documentation in the config block.

### columns: {} Requirement

**WRONG**: Table without column documentation
```sql
config {
  type: "table",
  schema: "looker_prod"
}

SELECT customer_id, total_revenue FROM ${ref("orders")}
```

**CORRECT**: Complete column documentation
```sql
config {
  type: "table",
  schema: "looker_prod",
  columns: {
    customer_id: "Unique customer identifier from SAP (KUNNR field)",
    total_revenue: "Sum of all order amounts in USD, excluding refunds"
  }
}

SELECT customer_id, total_revenue FROM ${ref("orders")}
```

### Where to Get Column Descriptions

Column descriptions should be derived from:

1. **Source Declarations**: Copy descriptions from upstream source tables
2. **Third-party Documentation**:
   - SAP: Use publicly available SAP field documentation (e.g., KUNNR = Customer Number)
   - Dialpad: Use Dialpad API documentation for field definitions
   - HubSpot: Use HubSpot API docs for property descriptions
   - Magento/Adobe Commerce: Use Adobe Commerce schema documentation
3. **Business Logic**: Document calculated fields, transformations, and business rules
4. **Looker Requirements**: Include context that Looker dashboard builders need

**Example with SAP source documentation**:
```sql
config {
  type: "table",
  schema: "looker_prod",
  columns: {
    customer_id: "SAP Customer Number (KUNNR) - unique identifier in SAP ERP",
    customer_name: "Customer name (NAME1 field) - legal business name",
    account_group: "Customer Account Group (KTOKD) - classification code",
    credit_limit: "Credit limit in USD (KLIMK field) - maximum allowed credit"
  }
}
```

### Source Declarations Should Include columns: {}

When applicable, source declarations should also document columns:

```sql
-- definitions/sources/dialpad/calls.sqlx
config {
  type: "declaration",
  database: "acuantia",
  schema: "dialpad_api",
  name: "calls",
  description: "Dialpad call records with transcripts and sentiment analysis",
  columns: {
    call_id: "Unique call identifier from Dialpad API",
    external_number: "Customer phone number that originated or received the call",
    duration: "Call duration in seconds",
    start_time: "UTC timestamp when call started",
    transcript: "Full call transcript from Dialpad AI",
    sentiment: "Overall call sentiment: positive/negative/neutral/mixed",
    sentiment_score: "Sentiment confidence score (0.0 to 1.0)"
  }
}
```

**Why document sources**: Downstream tables inherit and extend these descriptions, creating documentation consistency across the pipeline.

## Test-Driven Development (TDD) Workflow

**REQUIRED BACKGROUND:** You MUST understand and follow superpowers:test-driven-development

**BEFORE TDD:** When creating NEW features with unclear requirements, use superpowers:brainstorming FIRST to refine rough ideas into clear designs. Only start TDD once you have a clear understanding of what needs to be built.

When creating NEW features or tables in Dataform, apply the TDD cycle:

1. **RED**: Write tests first, watch them fail
2. **GREEN**: Write minimal code to make tests pass
3. **REFACTOR**: Clean up while keeping tests passing

The superpowers:test-driven-development skill provides the foundational TDD principles. This section adapts those principles specifically for Dataform tables and SQLX files.

### TDD for Dataform Tables

**WRONG: Implementation-first approach**
```
1. Write SQLX transformation
2. Test manually with bq query
3. "It works, ship it"
```

**CORRECT: Test-first approach**
```
1. Write data quality assertions first
2. Write unit tests for business logic
3. Run tests - they should FAIL (table doesn't exist yet)
4. Write SQLX transformation
5. Run tests - they should PASS
6. Refactor transformation if needed
```

### Example TDD Workflow

**Step 1: Write assertions first** (definitions/assertions/assert_customer_metrics.sqlx)
```sql
config {
  type: "assertion",
  description: "Customer metrics must have valid data"
}

-- This WILL fail initially (table doesn't exist)
SELECT 'Duplicate customer_id' AS test
FROM ${ref("customer_metrics")}
GROUP BY customer_id
HAVING COUNT(*) > 1

UNION ALL

SELECT 'Negative lifetime value' AS test
FROM ${ref("customer_metrics")}
WHERE lifetime_value < 0
```

**Step 2: Run tests - watch them fail**
```bash
dataform run --schema-suffix dev --run-tests --actions assert_customer_metrics
# ERROR: Table customer_metrics does not exist ✓ EXPECTED
```

**Step 3: Write minimal implementation** (definitions/output/looker/customer_metrics.sqlx)
```sql
config {
  type: "table",
  schema: "looker_prod",
  columns: {
    customer_id: "Unique customer identifier",
    lifetime_value: "Total revenue from customer in USD"
  }
}

SELECT
  customer_id,
  SUM(order_total) AS lifetime_value
FROM ${ref("orders")}
GROUP BY customer_id
```

**Step 4: Run tests - watch them pass**
```bash
dataform run --schema-suffix dev --actions customer_metrics
dataform run --schema-suffix dev --run-tests --actions assert_customer_metrics
# No rows returned ✓ TESTS PASS
```

### Why TDD Matters in Dataform

- **Catches bugs before production**: Tests fail when logic is wrong
- **Documents expected behavior**: Tests show what the table should do
- **Prevents regressions**: Future changes won't break existing logic
- **Faster debugging**: Test failures pinpoint exact issues
- **Confidence in refactoring**: Change code safely with test coverage

### TDD Red Flags

If you're thinking:
- "I'll write tests after the implementation" → **NO, write tests FIRST**
- "Tests are overkill for this simple table" → **NO, simple tables break too**
- "I'll test manually with bq query" → **NO, manual tests aren't repeatable**
- "Tests after achieve the same result" → **NO, tests-first catches design flaws**

**All of these mean**: You're skipping TDD. Write tests first, then implementation.

**See also**: The superpowers:test-driven-development skill contains additional TDD rationalizations and red flags that apply universally to all code, including Dataform SQLX files.

## Quick Reference

| Task | Command | Notes |
|------|---------|-------|
| Compile only | `dataform compile` | Check syntax, no BigQuery execution |
| Dry run | `dataform run --schema-suffix dev --dry-run --actions table_name` | Validate SQL, estimate cost |
| Test in dev | `dataform run --schema-suffix dev --actions table_name` | Safe execution in dev environment |
| Run with dependencies | `dataform run --schema-suffix dev --include-deps --actions table_name` | Run upstream dependencies first |
| Run by tag | `dataform run --schema-suffix dev --tags looker` | Run all tables with tag |
| Production deploy | `dataform run --actions table_name` | Only after dev testing succeeds |

## Common Rationalizations (And Why They're Wrong)

| Excuse | Reality | Fix |
|--------|---------|-----|
| "Too urgent to test in dev" | Production failures waste MORE time than dev testing | 3 minutes testing saves 60 minutes debugging |
| "It's just a quick report" | "Quick" reports become permanent tables | Use proper architecture from start |
| "Business is waiting" | Broken output wastes stakeholder time | Correct results delivered 10 minutes later > wrong results now |
| "Hardcoding table path is faster than ${ref()}" | Breaks dependency tracking, creates maintenance nightmare | Create source declaration, use ${ref()} (30 seconds) |
| "I'll refactor it later" | Technical debt rarely gets fixed | Do it right the first time (saves time overall) |
| "Correctness over elegance" | Architecture = maintainability, not elegance | Proper structure IS correctness |
| "I'll add tests after" | After = never | Write tests FIRST (TDD), then implementation |
| "I'll add documentation after" | After = never | Add columns: {} in config block immediately |
| "Looker prefix isn't necessary" | Causes naming conflicts and confusion | Always prefix Looker tables with looker_ |
| "Working late, just need it working" | Exhaustion causes mistakes | Discipline matters MORE when tired |
| "Column docs are optional for internal tables" | All tables become external eventually | Document everything, always |
| "Tests after achieve same result" | Tests-after = checking what it does; tests-first = defining what it should do | TDD catches design flaws early |

## Red Flags - STOP Immediately

If you're thinking any of these thoughts, STOP and follow the skill:

- "I'll skip `--schema-suffix dev` this once"
- "No time for `--dry-run`"
- "I'll just hardcode the table path instead of using ${ref()}"
- "I'll use backticks instead of ${ref()} (it's faster)"
- "I'll just create one file instead of intermediate layers"
- "Tests are optional for ad-hoc work"
- "I'll write tests after the implementation"
- "I'll add column documentation later"
- "This table doesn't need columns: {} block"
- "I'll use a .js file for declarations (faster to write)"
- "I don't need to prefix this Looker table with looker_"
- "I'll add schema: config to this operation/test file"
- "I'll fix the technical debt later"
- "This is different because [business reason]"

**All of these mean**: You're about to create problems. Follow the non-negotiable practices.

## Common Mistakes

### Mistake 1: Using tables before declaring sources

```sql
-- WRONG: Direct table reference
FROM `acuantia.hubspot.contact`

-- CORRECT: Declare source first
FROM ${ref("contact")}
```

**Fix**: Create source declaration in `definitions/sources/` before using in queries.

### Mistake 2: Mixing ref() with manual schema qualification

```sql
-- WRONG: When source exists
FROM ${ref("dataset_name", "table_name")}

-- CORRECT
FROM ${ref("table_name")}
```

**Fix**: Use single-argument `ref()` when source declaration exists. Dataform handles full path resolution.

### Mistake 3: Skipping dev testing under pressure

**Symptom**: "I'll deploy directly to production because it's urgent"

**Fix**: `--schema-suffix dev` takes 30 seconds longer than production deploy. Production failures take hours to fix.

### Mistake 4: Creating monolithic transformations

**Symptom**: 200-line SQLX file with 5 CTEs doing multiple transformations

**Fix**: Break into intermediate tables. Each table should do ONE transformation clearly.

### Mistake 5: Missing columns: {} documentation

**Symptom**: Table config without column descriptions

**Fix**: Add comprehensive `columns: {}` block to EVERY table with `type: "table"`. Get descriptions from source docs, upstream tables, or business logic.

### Mistake 6: Writing implementation before tests

**Symptom**: Creating SQLX file, then adding assertions afterward (or never)

**Fix**: Follow TDD cycle - write assertions first, watch them fail, write implementation, watch tests pass.

### Mistake 7: Using .js files for NEW source declarations

**Symptom**: Creating NEW `definitions/sources/sources.js` files with declare() functions

**Fix**: Create .sqlx files in `definitions/sources/[system]/[table].sqlx` with proper config blocks and column documentation. Existing .js files can remain until they need modification.

### Mistake 8: Hardcoded table paths instead of ${ref()}

**Symptom**: Using backtick-quoted table paths in queries
```sql
FROM `acuantia.dialpad_api.calls`
SELECT * FROM acuantia.ods.sap_customers
```

**Fix**: ALWAYS use ${ref()} after creating source declarations
```sql
FROM ${ref("calls")}
SELECT * FROM ${ref("ods", "sap_customers")}
```

**Why critical**: Hardcoded paths break dependency tracking, prevent --schema-suffix from working, and make refactoring impossible.

### Mistake 9: Missing looker_ prefix for Looker tables

**Symptom**: File in `definitions/output/looker/` without looker_ prefix
```
definitions/output/looker/customer_metrics.sqlx  ❌
```

**Fix**: Add looker_ prefix to filename
```
definitions/output/looker/looker_customer_metrics.sqlx  ✅
```

### Mistake 10: Adding schema: config to operations or tests

**Symptom**: Operations or test files with explicit schema configuration
```sql
config {
  type: "operations",
  schema: "dataform",  // Wrong!
}
```

**Fix**: Remove schema: config - operations and tests use default schemas from workflow_settings.yaml

## Time Pressure Protocol

When under extreme time pressure (board meeting in 2 hours, production down, stakeholder waiting):

1. ✅ **Still use dev testing** - 3 minutes saves 60 minutes debugging
2. ✅ **Still use --dry-run** - Catches errors before wasting BigQuery slots
3. ✅ **Still create source declarations** - Broken dependencies waste MORE time
4. ✅ **Still add columns: {} documentation** - Takes 2 minutes, saves hours explaining to Looker users
5. ✅ **Still write tests first (TDD)** - 5 minutes writing assertions prevents production bugs
6. ✅ **Still do basic validation** - Wrong results are worse than delayed results
7. ⚠️ **Can skip**: Extensive documentation files, peer review, performance optimization
8. ⚠️ **Must document**: Tag as "technical_debt", create TODO with follow-up tasks

**The bottom line**: Safety practices save time. Skipping them wastes time. Even under pressure.

## Troubleshooting Dataform Errors

**RECOMMENDED APPROACH:** When encountering ANY bug, test failure, or unexpected behavior, use superpowers:systematic-debugging before attempting fixes. For errors deep in execution or cascading failures, use superpowers:root-cause-tracing to identify the original trigger.

### "Table not found" errors

**Quick fixes:**
1. Check source declaration exists in `definitions/sources/`
2. Verify ref() syntax (single argument if source exists)
3. Check schema/database match in source config
4. Run `dataform compile` to see resolved SQL

**If issue persists:** Use superpowers:systematic-debugging for structured root cause investigation.

### Dependency cycle errors

**Quick fixes:**
1. Use `${ref("table_name")}` not direct table references
2. Check for circular dependencies (A → B → A)
3. Review dependency graph in Dataform UI

**If issue persists:** Use superpowers:root-cause-tracing to trace the dependency chain back to the source of the cycle.

### Timeout errors

**Quick fixes:**
1. Add partitioning/clustering to config
2. Use incremental updates instead of full refresh
3. Break large transformations into smaller intermediate tables

**If issue persists:** Use superpowers:systematic-debugging to investigate query performance systematically.

## Real-World Impact

**Scenario**: "Quick" report created without source declarations, skipping dev testing.

**Cost**:
- 10 minutes saved initially
- 2 hours debugging "table not found" errors in production
- 3 stakeholder escalations
- 1 broken morning dashboard
- Net loss: 110 minutes

**With proper practices**:
- 13 minutes total (3 extra for dev testing)
- Zero production issues
- Zero escalations
- Net gain: 97 minutes

**Takeaway**: Discipline is faster than shortcuts.
