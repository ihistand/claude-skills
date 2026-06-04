---
name: sqlanvil-engineering-fundamentals
description: Use when writing or editing a sqlanvil data project (.sqlx models, workflow_settings.yaml, .df-credentials.json) targeting PostgreSQL or Supabase - corrects Dataform/BigQuery priors that produce wrong config blocks, credentials, DDL, separators, and CLI commands in the sqlanvil fork
---

# sqlanvil Engineering Fundamentals

## Overview

**sqlanvil is a fork of Dataform repositioned for PostgreSQL and Supabase.** Your Dataform/BigQuery instincts are *mostly* right — `.sqlx` files, `config {}` blocks, `${ref()}`, `${self()}`, declarations, assertions, tags, incremental tables, `pre_operations`/`post_operations` all work the same. **This skill is the delta**: the specific places where assuming Dataform/BigQuery produces broken sqlanvil code.

**Core principle:** When the warehouse is Postgres/Supabase, reach for the **`postgres: {}` config block** and idiomatic Postgres — never BigQuery options or hand-rolled DDL workarounds.

**REQUIRED FOUNDATION:** TDD applies — see superpowers:test-driven-development. For warehouse-agnostic architecture, layering, `${ref()}` discipline, and `columns:{}` documentation standards, the rules in **dataform-engineering-fundamentals** carry over unchanged (just swap BigQuery specifics for the deltas below).

**Authoritative config reference:** `protos/configs.proto` in the sqlanvil repo (`PostgresOptions`, `PostgresConnection`, `TableConfig`, `IncrementalTableConfig`, `ViewConfig`). When unsure of a field, read the proto — it is the source of truth.

## When to Use

- Writing any `.sqlx` model, `workflow_settings.yaml`, or `.df-credentials.json` for a sqlanvil project on Postgres/Supabase
- Adding indexes, partitioning, storage options, materialized views, or stored procedures
- Translating an existing Dataform/BigQuery project to sqlanvil/Postgres
- Any time you're about to write `bigquery: {}`, `partitionBy`, `dataform.json`, `method: "btree"`, or `;` between statements — STOP and check the deltas

## The Deltas That Bite (read before writing anything)

### 1. Project config: `workflow_settings.yaml`, warehouse is Postgres
```yaml
warehouse: postgres            # flat string ("postgres" or "supabase") — NOT nested
defaultDataset: public         # the Postgres SCHEMA
defaultAssertionDataset: dataform_assertions
dataformCoreVersion: 3.0.x
vars:
  someVar: value
```
**Drop** `defaultProject` and `defaultLocation` — they are BigQuery-only. (`dataform.json` is the legacy upstream name; sqlanvil uses `workflow_settings.yaml`.)

### 2. Connection: `.df-credentials.json` — flat `PostgresConnection`
The filename is literally `.df-credentials.json` (the fork kept upstream's name; it's the default, override with `--credentials`). The JSON is a **flat** `PostgresConnection` — **not** nested under a `"postgres"` key, **not** the BigQuery shape:
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "postgres",
  "user": "postgres",
  "password": "password",
  "sslMode": "require",
  "defaultSchema": "public"
}
```
Field names exactly: `host port database user password sslMode defaultSchema` — **not** `username`/`databaseName`/`ssl`. Gitignore it. Supabase: `host: db.<ref>.supabase.co`, port 5432 (or 6543 pooler), `sslMode: "require"`.

### 3. Storage, indexes, partitioning are FIRST-CLASS — never hand-roll DDL
Use the `postgres: {}` block on `type: "table"` and `type: "incremental"`. **Do not** create indexes or set fillfactor via `post_operations` raw DDL.
```sqlx
config {
  type: "table",
  postgres: {
    fillfactor: 80,
    unlogged: false,
    tablespace: "fast_ssd",
    indexes: [
      { name: "idx_email", columns: ["email"], unique: true },
      { name: "idx_props", columns: ["props"], method: 2, opclass: "jsonb_path_ops" }
    ]
  }
}
```
**Index `method` is a NUMERIC ENUM, not a string:** `BTREE=0, HASH=1, GIN=2, GIST=3, BRIN=4`. `method: "btree"` fails the config type check (the parser uses protobufjs `create()`). Omit `method` for btree (default 0).
Index fields: `name`, `columns[]`(array), `method`(int), `where`(partial predicate), `unique`(bool), `include[]`(array, covering), `opclass`(**single string**, applied to every indexed column — `opclass: "gin_trgm_ops"`, **not** an array).

### 4. Native partitioning via `postgres.partition` (not `partitionBy`/`clusterBy`)
```sqlx
postgres: {
  partition: {
    kind: 0,                                   // RANGE=0, LIST=1, HASH=2 (numeric enum)
    columns: ["order_date"],
    partitions: [
      { name: "y2024", values: "FROM ('2024-01-01') TO ('2025-01-01')" }
    ],
    includeDefault: true
  }
}
```
`values` is the raw `FOR VALUES` body matching `kind`. There is no `clusterBy` — use `indexes` instead.

### 5. Materialized views: `type: "view", materialized: true`
Emits `CREATE MATERIALIZED VIEW`. Default = **drop + recreate every run** (which also picks up definition changes).
**Known limitation:** `ViewConfig` has no `postgres: {}` block, so you **cannot** set `refreshPolicy` or `noData` from a view's `config` today — writing `postgres: {...}` in a view config will not parse. For in-place `REFRESH MATERIALIZED VIEW` instead of drop+recreate, add a separate `type: "operations"` action running `refresh materialized view ${ref("mv_name")}` with a dependency on the matview.

### 6. Statement separator is `---`, never `;`
Three dashes on their own line separate statements in `operations`, `pre_operations`, `post_operations`. sqlanvil never splits on `;`, so PL/pgSQL `$$ ... ; ... $$` bodies survive intact. A `table`/`view` model body is exactly ONE `SELECT` — no `---`.

### 7. Procedures / functions / triggers / extensions / grants → `type: "operations"`
No dedicated action type; the operations generator is dialect-agnostic.
```sqlx
config { type: "operations", hasOutput: false }
CREATE OR REPLACE FUNCTION marts.recalc() RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  -- body; semicolons here are fine
END;
$$
---
CALL marts.recalc()
```

### 8. Two different `uniqueKey`s — do not confuse them
- Top-level `uniqueKey: ["id"]` on an **incremental** = the upsert/merge key (Postgres `INSERT ... ON CONFLICT`). Controls incremental write behavior.
- `assertions: { uniqueKey: ["id"] }` = generates a uniqueness **assertion** action. A data-quality check.

They are independent and can coexist.

### 9. Primary keys / one-time DDL on incrementals → `post_operations`
On Postgres, plain `pre_operations`/`post_operations` run only on **create + `--full-refresh`**; `incrementalPre/PostOps` run on appends. So `ALTER TABLE ${self()} ADD PRIMARY KEY (...)` belongs in `post_operations` — it won't re-run (and error) on every append. Matview post-ops re-run on every build, so keep them idempotent (matviews can't have PKs anyway).

### 10. Metadata + assertions (same surface as Dataform, works on PG)
- `description:` (table comment) + `columns: { col: "..." }` (per-column comments) → `COMMENT ON TABLE|VIEW|MATERIALIZED VIEW|COLUMN`. Document every table.
- `assertions: { uniqueKey, uniqueKeys: [["a","b"],["c"]], nonNull: [...], rowConditions: [...] }`. Standalone assertion = `type: "assertion"` whose `SELECT` returns offending rows (passes iff zero rows).

### 11. No BigQuery-isms, ever
Don't emit `bigquery: {}`, `partitionBy`, `clusterBy`, `OPTIONS(...)`, `bigqueryPolicyTags`, backticked `` `project.dataset.table` ``, or `CREATE ... NOT ENFORCED`. Use the `postgres:` equivalents and standard double-quoted identifiers.

### 12. CLI: `./scripts/run <verb>` (no global `dataform`, no `npm run`)
```bash
./scripts/run compile <projectDir>
./scripts/run run     <projectDir> --credentials <projectDir>/.df-credentials.json
./scripts/run run     <projectDir> --credentials ... --full-refresh
./scripts/run run     <projectDir> --credentials ... --actions <name> --include-deps
./scripts/run test    <projectDir> --credentials ...
```
Boot a local PG with `./tools/postgres/run-postgres-db.sh`. Note: `--dry-run` only validates BigQuery today; on Postgres it does **not** EXPLAIN-validate SQL (known gap).

### 13. Supabase extras (`warehouse: supabase`)
`supabase: {}` block adds `enableRls`, `publishToRealtime`, `ownerRole`, `vectors: [{ column, dimensions, indexType }]`. Dedicated action types: `rlsPolicy`, `realtimePublication`, `wrapper`, `vectorIndex`. `enableRls` only flips RLS on — declare actual policies via the `rlsPolicy` action.

## Quick Reference: Dataform/BigQuery → sqlanvil/Postgres

| You'd reach for (Dataform/BQ) | Use instead (sqlanvil/PG) |
|---|---|
| `dataform.json` | `workflow_settings.yaml`, `warehouse: postgres` |
| `defaultProject` / `defaultLocation` | drop them; `defaultDataset` = schema |
| `bigquery: { partitionBy, clusterBy }` | `postgres: { partition: {...}, indexes: [...] }` |
| `OPTIONS(...)` / table options | `postgres: { fillfactor, unlogged, tablespace }` |
| `CREATE INDEX` in `post_operations` | `postgres: { indexes: [...] }` |
| `method: "btree"` (string) | `method: 0` (numeric enum) |
| `;` between statements | `---` |
| `CREATE PROCEDURE` + run separately | `type: "operations"` |
| creds `{postgres:{username,databaseName,ssl}}` | flat `{host,port,database,user,password,sslMode,defaultSchema}` |
| matview `refreshPolicy` in view config | not supported — use `operations` REFRESH |
| `dataform run` / `npm run` | `./scripts/run run ... --credentials` |

## Common Mistakes (observed in real agent baselines)

1. Hand-rolling indexes/fillfactor in `post_operations` → use the `postgres: {}` block.
2. `method: "btree"` string → numeric enum (`0`).
3. Nesting credentials under `"postgres"` or using `username`/`databaseName`/`ssl` → flat `PostgresConnection`.
4. Leaving `bigquery: {}`, `defaultProject`, `clusterBy`, `bigqueryPolicyTags` in → remove all of it.
5. `;` separators in operations → `---` (and trust `$$...$$` bodies).
6. `postgres: { refreshPolicy }` on a materialized view → won't parse; use an `operations` REFRESH action.
7. Assuming a `dataform` CLI → `./scripts/run`.
8. Confusing incremental `uniqueKey` (merge key) with `assertions.uniqueKey` (quality check).
9. `opclass: ["..."]` as an array → `opclass` is a single string applied to every indexed column.

## Red Flags — STOP and check the deltas

If you're about to type any of these in a Postgres/Supabase sqlanvil project, you're reverting to BigQuery priors:
- `dataform.json`, `defaultProject`, `defaultLocation`
- `bigquery: {`, `partitionBy`, `clusterBy`, `OPTIONS(`
- `method: "` (string) inside an index
- `CREATE INDEX` / `SET (fillfactor` inside `post_operations`
- `;` to separate statements in an operation
- `postgres: {` inside a `type: "view"` config
- a bare `dataform` or `npm run` command

When unsure of a `postgres:` field name or enum value, read `protos/configs.proto`.
