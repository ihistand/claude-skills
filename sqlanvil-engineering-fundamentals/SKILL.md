---
name: sqlanvil-engineering-fundamentals
description: Use when writing or editing a sqlanvil data project (.sqlx models, workflow_settings.yaml, .df-credentials.json) targeting PostgreSQL or Supabase - corrects Dataform/BigQuery priors that produce wrong config blocks, credentials, DDL, separators, and CLI commands in the sqlanvil fork
---

# sqlanvil Engineering Fundamentals

## Overview

**sqlanvil is a fork of Dataform repositioned for PostgreSQL and Supabase.** Your Dataform/BigQuery instincts are *mostly* right — `.sqlx` files, `config {}` blocks, `${ref()}`, `${self()}`, declarations, assertions, tags, incremental tables, `pre_operations`/`post_operations` all work the same. **This skill is the delta**: the specific places where assuming Dataform/BigQuery produces broken sqlanvil code.

**Core principle:** When the warehouse is Postgres/Supabase, reach for the **`postgres: {}` config block** and idiomatic Postgres — never BigQuery options or hand-rolled DDL workarounds.

**REQUIRED FOUNDATION:** TDD applies — see superpowers:test-driven-development. For warehouse-agnostic architecture, layering, `${ref()}` discipline, and `columns:{}` documentation standards, the rules in **dataform-engineering-fundamentals** carry over unchanged (just swap BigQuery specifics for the deltas below).

**Authoritative config reference:** `protos/configs.proto` in the sqlanvil repo (`PostgresOptions`, `PostgresConnection`, `ConnectionConfig`, `TableConfig`, `IncrementalTableConfig`, `ViewConfig`, `DeclarationConfig`). When unsure of a field, read the proto — it is the source of truth.

## When to Use

- Writing any `.sqlx` model, `workflow_settings.yaml`, or `.df-credentials.json` for a sqlanvil project on Postgres/Supabase
- Adding indexes, partitioning, storage options, materialized views, or stored procedures
- Reading a source table from **another warehouse** (BigQuery, or a second Postgres) — named connections + `introspect`
- Translating an existing Dataform/BigQuery project to sqlanvil/Postgres
- Any time you're about to write `bigquery: {}`, `partitionBy`, `dataform.json`, `method: "btree"`, or `;` between statements — STOP and check the deltas

## The Deltas That Bite (read before writing anything)

### 1. Project config: `workflow_settings.yaml`, warehouse is Postgres
```yaml
warehouse: postgres            # flat string ("postgres" or "supabase") — NOT nested
defaultDataset: public         # the Postgres SCHEMA
defaultAssertionDataset: sqlanvil_assertions
sqlanvilCoreVersion: 1.1.1     # sqlanvil's OWN SemVer line (NOT dataformCoreVersion); 1.1.1+ for named connections
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
Emits `CREATE MATERIALIZED VIEW`. Default = **drop + recreate every run** (which also picks up definition changes). Set Postgres options directly in the view config via `postgres: {}`:
```sqlx
config {
  type: "view",
  materialized: true,
  postgres: {
    refreshPolicy: "on_dependency_change",   // in-place REFRESH instead of drop+recreate
    noData: true,                            // CREATE ... WITH NO DATA (empty until first refresh)
    indexes: [{ name: "idx_mv_id", columns: ["id"], unique: true }]
  }
}
```
`refreshPolicy: "on_dependency_change"` runs `REFRESH MATERIALIZED VIEW` in place instead of drop+recreate — but in-place refresh does **not** pick up definition (SQL) changes; omit `refreshPolicy` for the safe drop+recreate default.

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

### 9. Primary keys / one-time DDL on incrementals → wrap in `when(!incremental())`
An **unwrapped** `pre_operations`/`post_operations` block runs on **every** run of an incremental — the initial create *and* every append (the block is compiled into both the create-path ops and the incremental-path ops). So a bare `ALTER TABLE ... ADD PRIMARY KEY` errors on the second run (`multiple primary keys ... not allowed`). Wrap one-time DDL so it only runs on create + `--full-refresh`:
```sqlx
post_operations {
  ${when(!incremental(), `ALTER TABLE ${self()} ADD PRIMARY KEY (order_date)`)}
}
```
(The PK also gives the incremental upsert its `ON CONFLICT` target.) Matview post-ops also re-run every build — keep them idempotent (matviews can't have PKs anyway).

### 10. Metadata + assertions (same surface as Dataform, works on PG)
- `description:` (table comment) + `columns: { col: "..." }` (per-column comments) → `COMMENT ON TABLE|VIEW|MATERIALIZED VIEW|COLUMN`. Document every table.
- `assertions: { uniqueKey, uniqueKeys: [["a","b"],["c"]], nonNull: [...], rowConditions: [...] }`. Standalone assertion = `type: "assertion"` whose `SELECT` returns offending rows (passes iff zero rows).

### 11. No BigQuery-isms, ever
Don't emit `bigquery: {}`, `partitionBy`, `clusterBy`, `OPTIONS(...)`, `bigqueryPolicyTags`, backticked `` `project.dataset.table` ``, or `CREATE ... NOT ENFORCED`. Use the `postgres:` equivalents and standard double-quoted identifiers.

### 12. CLI: `sqlanvil <verb>` (the installed CLI — no global `dataform`, no `npm run`)
```bash
sqlanvil init    <projectDir> --warehouse postgres   # or supabase — scaffolds workflow_settings.yaml + .df-credentials.json template (BigQuery is the default and needs a GCP project + location)
sqlanvil compile <projectDir>
sqlanvil run     <projectDir> --credentials <projectDir>/.df-credentials.json
sqlanvil run     <projectDir> --credentials ... --full-refresh
sqlanvil run     <projectDir> --credentials ... --actions <name> --include-deps
sqlanvil test    <projectDir> --credentials ...
```
Install with `npm i -g @sqlanvil/cli`. (Working from a sqlanvil repo checkout instead of the installed CLI? Use `./scripts/run <verb>` in place of `sqlanvil <verb>`.) Note: `--dry-run` only validates BigQuery today; on Postgres it does **not** EXPLAIN-validate SQL (known gap).

### 13. Supabase extras (`warehouse: supabase`)
`supabase: {}` block adds `enableRls`, `publishToRealtime`, `ownerRole`, `vectors: [{ column, dimensions, indexType }]`. Dedicated action types: `rlsPolicy`, `realtimePublication`, `wrapper`, `vectorIndex`. `enableRls` only flips RLS on — declare actual policies via the `rlsPolicy` action.

### 14. Declaring external sources: `type: "declaration"`
Reference a pre-existing (externally-managed) table so `${ref()}` resolves and the DAG tracks it. Two equivalent forms:
```sqlx
-- one declaration per .sqlx file
config { type: "declaration", schema: "raw", name: "orders" }
```
```js
// many declarations in one .js file
declare({ schema: "raw", name: "orders" });
declare({ schema: "raw", name: "customers" });
```
**Declarations are exempt from `--schema-suffix` / `tablePrefix` / `datasetSuffix` — intentionally.** They point at fixed external tables, so the suffix is *not* applied to a declaration's own target, and `${ref()}` to a declared source resolves to the real (unsuffixed) table even under `--schema-suffix dev`. So a dev run reads true sources while writing to suffixed output schemas. Don't try to "fix" a declaration that lacks a suffix — that's correct.

### 15. Cross-warehouse sources: named connections + the auto-generated FDW bridge (≥ 1.1.1)

To read a table that lives in **BigQuery** from a Postgres/Supabase project, declare it as a **named connection** — do **not** hand-roll a foreign-data-wrapper. sqlanvil generates the whole FDW bridge for you. (**BigQuery sources are the supported path today.** A `platform: postgres`/`supabase` source compiles but is **not yet runnable** — the `postgres_fdw` user mapping isn't emitted, so it has no credentials at run time. Don't use Postgres sources yet.)

**Step 1 — declare the connection** in `workflow_settings.yaml`:
```yaml
warehouse: supabase              # the ONE warehouse sqlanvil writes to
connections:
  bigquery_public:
    platform: bigquery           # BigQuery sources are the supported path
    project: bigquery-public-data
    dataset: geo_us_boundaries
    saKeyId: "<vault-secret-id>" # NON-secret Vault pointer; the SA key lives in Supabase Vault, not here
```
The read (write) warehouse must be **`postgres` or `supabase`** — the bridge is a Postgres FDW; reading a connection from a `warehouse: bigquery` project errors. Connections are **read-only sources**: one R/W warehouse, everything else is a source you pull *from* (no write-back).

**Step 2 — tag a declaration with the connection.** It **requires `columnTypes`** (the FDW needs them to build the foreign table), expressed in **Postgres** types (the foreign table is a Postgres object):
```sqlx
config {
  type: "declaration",
  connection: "bigquery_public",
  name: "zip_codes",
  columnTypes: { zip_code: "text", internal_point_lat: "float8", internal_point_lon: "float8" }
}
```
A connection-tagged declaration with no `columnTypes` is a **compile error** — don't omit them.

**Step 3 — generate that declaration instead of hand-writing it** (preferred):
```bash
sqlanvil introspect <connection> <schema.table> --output definitions/sources/<name>.sqlx
# e.g. sqlanvil introspect bigquery_public geo_us_boundaries.zip_codes --output definitions/sources/zip_codes.sqlx
```
`introspect` reads the live source schema and writes the declaration with each source column mapped to a Postgres type (`--output` writes the file; otherwise it prints to stdout). It connects from your machine at build time, so it needs **read creds for the source** in `.df-credentials.json` under a `connections` map — `{ "connections": { "<name>": { ...source creds... } } }` (BigQuery: `{ "credentials": <SA key JSON> }`; Postgres: `host`/`port`/`database`/`user`/`password`/`sslMode`). This sits alongside the flat write-warehouse creds; `run` ignores the `connections` map.

**What `compile` auto-generates** (you never write these): a foreign server **`<connection>_srv`** and a ref-able foreign table in schema **`<connection>_ext`** — e.g. `bigquery_public_ext.zip_codes`. Downstream models just `${ref("zip_codes")}` it like any other source; multiple declarations on one connection share the server. **Don't** hand-write a `wrapper`/foreign-table action to read a source — named connections replace that manual path.

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
| in-place matview refresh | `postgres: { refreshPolicy: "on_dependency_change" }` in the view config (else drop+recreate) |
| `dataform run` / `npm run` | `sqlanvil run ... --credentials` |
| hand-written FDW / foreign table to read another warehouse | named connection (`connections:` + `connection:`-tagged declaration), generated via `sqlanvil introspect` |
| `dataformCoreVersion:` | `sqlanvilCoreVersion:` (sqlanvil's own SemVer line) |

## Common Mistakes (observed in real agent baselines)

1. Hand-rolling indexes/fillfactor in `post_operations` → use the `postgres: {}` block.
2. `method: "btree"` string → numeric enum (`0`).
3. Nesting credentials under `"postgres"` or using `username`/`databaseName`/`ssl` → flat `PostgresConnection`.
4. Leaving `bigquery: {}`, `defaultProject`, `clusterBy`, `bigqueryPolicyTags` in → remove all of it.
5. `;` separators in operations → `---` (and trust `$$...$$` bodies).
6. For a materialized view, set `postgres: { refreshPolicy, noData, indexes }` in the view config (the view's `postgres:` block IS supported).
7. Assuming a `dataform` CLI → it is `sqlanvil` (or `./scripts/run` in a repo checkout).
8. Confusing incremental `uniqueKey` (merge key) with `assertions.uniqueKey` (quality check).
9. `opclass: ["..."]` as an array → `opclass` is a single string applied to every indexed column.
10. Bare `ADD PRIMARY KEY`/`ADD CONSTRAINT` in an incremental's `post_operations` → wrap in `when(!incremental())`, or it re-runs on every append and errors.

## Red Flags — STOP and check the deltas

If you're about to type any of these in a Postgres/Supabase sqlanvil project, you're reverting to BigQuery priors:
- `dataform.json`, `defaultProject`, `defaultLocation`
- `bigquery: {`, `partitionBy`, `clusterBy`, `OPTIONS(`
- `method: "` (string) inside an index
- `CREATE INDEX` / `SET (fillfactor` inside `post_operations`
- `;` to separate statements in an operation
- `ADD PRIMARY KEY`/`ADD CONSTRAINT` in an incremental's `post_operations` without `when(!incremental())`
- a bare `dataform` or `npm run` command
- `dataformCoreVersion:` in `workflow_settings.yaml` (the field is `sqlanvilCoreVersion:`)
- a `connection:`-tagged declaration with **no** `columnTypes`, or hand-writing a foreign table instead of using a named connection
- reading a connection from a `warehouse: bigquery` project (the read side must be `postgres`/`supabase`)

When unsure of a `postgres:` field name or enum value, read `protos/configs.proto`.
