---
name: dataform-engineering-fundamentals
description: Use when developing BigQuery Dataform transformations, SQLX files, source declarations, or troubleshooting pipelines - enforces TDD workflow (tests first), ALWAYS use ${ref()} never hardcoded table paths, comprehensive columns:{} documentation, safety practices (--schema-suffix dev, --dry-run), proper ref() syntax, .sqlx for new declarations, no schema config in operations/tests, and architecture patterns that prevent technical debt under time pressure
---

# Dataform Engineering Fundamentals

## Overview

**Core principle**: Safety practices and proper architecture are NEVER optional in Dataform development, regardless of time pressure or business urgency. The time "saved" by shortcuts gets multiplied into hours of debugging, broken dependencies, and production issues.

**REQUIRED FOUNDATION:** This skill builds upon superpowers:test-driven-development. All TDD principles from that skill apply here; this skill adapts them for BigQuery Dataform SQLX files.

**For PostgreSQL / Supabase:** use **sqlanvil-engineering-fundamentals** instead (or alongside) — the architecture, `${ref()}`, TDD, and `columns:{}` rules below carry over unchanged; that skill covers the Postgres/Supabase deltas (config blocks, credentials, DDL, named connections).

**Official docs:** syntax/config/API at https://cloud.google.com/dataform/docs · repository structure & naming at https://cloud.google.com/dataform/docs/best-practices-repositories

## When to Use

Use this skill for ANY Dataform work — new SQLX transformations, modifying tables, adding sources, troubleshooting pipelines, and "quick" reports or ad-hoc analysis.

**Especially** when under time pressure, stakeholders are waiting, you're working late and exhausted, or you're tempted to "just make it work" — discipline matters most exactly when it's tempting to skip.

**Related skills:**
- **superpowers:brainstorming** — refine rough requirements into clear designs *before* writing code
- **superpowers:systematic-debugging** — structured problem-solving for pipeline failures
- **superpowers:root-cause-tracing** — trace cascading errors back to their source
- **elements-of-style:writing-clearly-and-concisely** — for column descriptions, commit messages, any prose

## Non-Negotiable Safety Practices

ALWAYS required. No exceptions for deadlines, urgency, or "simple" tasks.

### 1. Always Use `--schema-suffix dev` for Testing

```bash
# WRONG: testing in production
dataform run --actions my_table

# CORRECT: test in dev first
dataform run --schema-suffix dev --actions my_table
```

Writes to `schema_dev.my_table` instead of production, so you can test without touching real data or dashboards.

### 2. Always Use `--dry-run` Before Execution

```bash
dataform compile                                              # check compilation
dataform run --schema-suffix dev --dry-run --actions my_table # validate SQL, estimate cost
dataform run --schema-suffix dev --actions my_table           # only then execute
```

Catches SQL errors, missing dependencies, and cost surprises before using BigQuery slots.

### 3. Source Declarations Before `ref()`

Declare external tables before querying them, so dependency tracking works.

```sql
-- definitions/sources/external_system/table_name.sqlx
config {
  type: "declaration",
  database: "project_id",
  schema: "external_schema",
  name: "table_name"
}
```

Then reference with `FROM ${ref("table_name")}` — never `FROM \`project.external_schema.table_name\``.

### 4. ALWAYS Use `${ref()}` — NEVER Hardcoded Table Paths

```sql
-- WRONG
FROM `project.reporting_schema.customer_metrics`
SELECT * FROM project.source_schema.customers

-- CORRECT (after declaring the source)
FROM ${ref("customer_metrics")}
SELECT * FROM ${ref("customers")}
```

`${ref()}` builds the dependency graph automatically, makes `--schema-suffix` work, and keeps refactoring safe. Hardcoded paths break all three. **Exception: none.** There is no valid reason to hardcode a table path in a SQLX file.

### 5. `ref()` Syntax: Single-Argument by Default

Prefer single-argument `ref()` — Dataform resolves the full path from the source declaration:

```sql
FROM ${ref("sales_order")}
```

Use **two-argument** `ref()` to disambiguate when a table name isn't unique across schemas, or when you need explicit schema/source control (e.g. ODS layers with repeated table names across datasets):

```sql
FROM ${ref("external_schema", "sales_order")}
```

Both are valid. Reach for single-arg first; two-arg is the right tool when you must pin the schema — not an error.

### 6. Basic Validation Queries

Always verify output — catches silent failures (empty tables, nulls, bad joins) immediately:

```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`project.schema_dev.my_table\`"
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) FROM \`project.schema_dev.my_table\` WHERE key_field IS NULL"
```

## Architecture Patterns (Not Optional)

Even for "quick" work. (Repository structure & naming: https://cloud.google.com/dataform/docs/best-practices-repositories)

### Layered Structure

```
definitions/
  sources/          # external data declarations
  intermediate/     # transformations and business logic
  output/
    reports/        # reporting tables
    marts/          # data marts for specific use cases
```

Don't build monolithic queries in the output layer — break them into intermediate steps for reuse and testing. Each table should do ONE transformation clearly.

### Incremental vs Full Refresh

```sql
config {
  type: "incremental",
  uniqueKey: ["order_id"],
  bigquery: {
    partitionBy: "DATE(order_date)",
    clusterBy: ["customer_id", "product_id"]
  }
}
```

`uniqueKey` is an array (it merges rows instead of appending). **Incremental** for tables that grow daily (events, transactions, logs); **full refresh** for small dimensions and aggregations with lookback windows.

### Incremental Internals

Use the `incremental()` context function to write only new rows on incremental runs, and `${self()}` to reference the table being built:

```sql
config {
  type: "incremental",
  uniqueKey: ["order_id"],
  bigquery: { partitionBy: "DATE(order_date)" }
}

SELECT order_id, order_date, amount
FROM ${ref("orders")}
${when(incremental(), `WHERE order_date > (SELECT MAX(order_date) FROM ${self()})`)}
```

- `incremental()` is true only on incremental runs (false on first build and `--full-refresh`).
- `${self()}` resolves to this table — use it in the incremental `WHERE` to read the high-water mark.
- `pre_operations { ... }` / `post_operations { ... }` run DDL around the build (grants, etc.). Wrap one-time DDL in `${when(!incremental(), ...)}` so it runs only on create/full-refresh, not on every append.

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

Catches data-quality issues automatically during pipeline runs.

### Source Declarations: Prefer `.sqlx` Files

ALL NEW source declarations MUST be `.sqlx` files (they support column docs, are more maintainable, and integrate with dependency tracking):

```sql
-- definitions/sources/external_system/table_name.sqlx
config {
  type: "declaration",
  database: "project_id",
  schema: "external_schema",
  name: "table_name",
  columns: { id: "Unique identifier for records" }
}
```

Existing `.js` `declare()` files can remain, but migrate them to `.sqlx` when you next modify them.

### Schema Configuration Rules

Files in `definitions/operations/` and `definitions/test/` must NOT include a `schema:` config. Operations live in the default `dataform` schema and assertions in `dataform_assertions` (set in `workflow_settings.yaml`); specifying schema explicitly causes conflicts.

```sql
-- CORRECT
config { type: "operations", tags: ["daily"] }

-- WRONG
config { type: "operations", schema: "dataform", tags: ["daily"] }
```

## Documentation Standards (Non-Negotiable)

Every table with `type: "table"` MUST include a comprehensive `columns: {}` block. (Use elements-of-style:writing-clearly-and-concisely for the descriptions.)

```sql
-- WRONG: no column documentation
config { type: "table", schema: "reporting" }

-- CORRECT
config {
  type: "table",
  schema: "reporting",
  columns: {
    customer_id: "Unique customer identifier from source system",
    total_revenue: "Sum of all order amounts in USD, excluding refunds"
  }
}
```

**Where descriptions come from:** upstream source declarations, third-party/API docs (CRM, ERP, analytics), business logic for calculated fields, and BI-tool context analysts need.

Source declarations should document columns too — downstream tables inherit and extend these descriptions, keeping documentation consistent across the pipeline:

```sql
config {
  type: "declaration",
  database: "project_id",
  schema: "external_api",
  name: "events",
  description: "Event records from external API",
  columns: {
    event_id: "Unique event identifier from API",
    user_id: "User who triggered the event",
    event_type: "Type of event (click, view, purchase, etc.)",
    timestamp: "UTC timestamp when the event occurred"
  }
}
```

## Test-Driven Development (TDD) Workflow

**REQUIRED BACKGROUND:** follow superpowers:test-driven-development. For NEW features with unclear requirements, use superpowers:brainstorming FIRST to refine the design, then start TDD.

The cycle for Dataform tables:

1. **RED** — write data-quality assertions / unit tests first; run them and watch them FAIL (table doesn't exist yet).
2. **GREEN** — write the minimal SQLX to make them pass.
3. **REFACTOR** — clean up while keeping tests passing.

Tests-first *defines what should happen*; tests-after merely *checks what does happen* — and "after" usually means never.

### Example

**Step 1 — assertion first** (`definitions/assertions/assert_customer_metrics.sqlx`):
```sql
config { type: "assertion", description: "Customer metrics must have valid data" }

SELECT 'Duplicate customer_id' AS test
FROM ${ref("customer_metrics")}
GROUP BY customer_id HAVING COUNT(*) > 1
UNION ALL
SELECT 'Negative lifetime value' AS test
FROM ${ref("customer_metrics")}
WHERE lifetime_value < 0
```

**Step 2 — run, watch it fail:**
```bash
dataform run --schema-suffix dev --run-tests --actions assert_customer_metrics
# ERROR: Table customer_metrics does not exist ✓ EXPECTED
```

**Step 3 — minimal implementation** (`definitions/output/reports/customer_metrics.sqlx`):
```sql
config {
  type: "table",
  schema: "reporting",
  columns: {
    customer_id: "Unique customer identifier",
    lifetime_value: "Total revenue from customer in USD"
  }
}

SELECT customer_id, SUM(order_total) AS lifetime_value
FROM ${ref("orders")}
GROUP BY customer_id
```

**Step 4 — run, watch it pass:**
```bash
dataform run --schema-suffix dev --actions customer_metrics
dataform run --schema-suffix dev --run-tests --actions assert_customer_metrics
# No rows returned ✓ TESTS PASS
```

## Quick Reference

| Task | Command |
|------|---------|
| Compile only | `dataform compile` |
| Dry run | `dataform run --schema-suffix dev --dry-run --actions table_name` |
| Test in dev | `dataform run --schema-suffix dev --actions table_name` |
| Run with dependencies | `dataform run --schema-suffix dev --include-deps --actions table_name` |
| Run by tag | `dataform run --schema-suffix dev --tags looker` |
| Production deploy | `dataform run --actions table_name` (only after dev testing succeeds) |

## Common Rationalizations (And Why They're Wrong)

| Excuse | Reality | Fix |
|--------|---------|-----|
| "Too urgent to test in dev" | Production failures waste MORE time than dev testing | 3 minutes testing saves 60 minutes debugging |
| "It's just a quick report" | "Quick" reports become permanent tables | Use proper architecture from the start |
| "Business is waiting" | Broken output wastes stakeholder time | Correct results 10 minutes later > wrong results now |
| "Hardcoding the path is faster than `${ref()}`" | Breaks dependency tracking and `--schema-suffix` | Declare the source, use `${ref()}` (30 seconds) |
| "I'll refactor / add tests / add docs later" | Later = never; technical debt rarely gets fixed | Do it right the first time (tests FIRST, `columns:{}` immediately) |
| "Tests after achieve the same result" | Tests-after checks behavior; tests-first defines it | TDD catches design flaws early |
| "Column docs are optional for internal tables" | Internal tables become external eventually | Document everything, always |
| "Working late, just need it working" | Exhaustion causes mistakes | Discipline matters MORE when tired |
| "This is different because [business reason]" | The rules exist precisely for the exceptions | Follow the non-negotiable practices |

## Red Flags — STOP Immediately

If you catch yourself thinking any of these, stop and follow the skill:

- "I'll skip `--schema-suffix dev` / `--dry-run` this once"
- "I'll just hardcode the path / use backticks instead of `${ref()}`"
- "I'll create one big file instead of intermediate layers"
- "Tests are optional here / I'll write them after"
- "This table doesn't need a `columns: {}` block / I'll document later"
- "I'll use a `.js` file for this new declaration"
- "I'll add `schema:` to this operation/test file"
- "I'll fix the technical debt later"

## Time Pressure Protocol

Under extreme pressure (board meeting in 2 hours, production down), the non-negotiables above STILL apply — dev testing, `--dry-run`, source declarations, `columns:{}`, tests-first, and basic validation each cost minutes and save hours.

**You may skip** (and only with a `technical_debt`-tagged TODO documenting the follow-up): extensive standalone documentation files, peer review, and performance optimization. Nothing else.

## Troubleshooting

For ANY bug, test failure, or unexpected behavior, use superpowers:systematic-debugging before attempting fixes; for cascading failures use superpowers:root-cause-tracing. Dataform-specific errors: https://cloud.google.com/dataform/docs

- **"Table not found"** — check the source declaration exists, verify `ref()` syntax (single-arg if the source is declared), confirm schema/database match, run `dataform compile` to see resolved SQL.
- **Dependency cycle** — use `${ref()}` (not direct references), look for circular chains (A → B → A), review the dependency graph in the Dataform UI.
- **Timeouts** — add partitioning/clustering, switch full refresh to incremental, break large transformations into smaller intermediate tables.

**Discipline is faster than shortcuts.**
