# Acuantia Dataform Engineering Skill

## Summary

Lean, Acuantia-specific extension skill that requires `dataform-engineering-fundamentals` as a prerequisite. Adds only organization-specific patterns: ODS architecture, Looker integration, dataset naming conventions, and cross-project coordination.

## Architecture

**Skill Hierarchy**:
```
dataform-engineering-fundamentals (generic foundation)
    ↓ REQUIRED PREREQUISITE
acuantia-dataform (thin extension layer)
```

**Reduced from 3,176 to 1,332 words** (58% reduction) by removing all generic Dataform content and focusing exclusively on Acuantia-specific patterns.

## What This Skill Adds

**Organization-Specific Patterns** (not found in generic skill):

### 1. ODS Architecture
- Two-argument ref() syntax for ODS tables: `${ref("ods", "table_name")}`
- Prevents `ods_dev_dev` suffix duplication
- ODS dataset conventions (ods, ods_dev, ods_prod)

### 2. Looker Integration
- `looker_` filename prefix requirement
- Schema configuration: `looker_prod` and `looker_dev`
- Metadata sync via `node scripts/updateLookerDescriptions.js`
- Performance optimization for Looker user query patterns

### 3. Acuantia Dataset Conventions
- `acuantia.callrail_api.*` - CallRail raw data
- `acuantia.dialpad_api.*` - Dialpad raw data
- `acuantia.hubspot.*` - HubSpot CRM (via Fivetran)
- `acuantia.magento_rotoplas_me_22_prod.*` - Adobe Commerce (via Fivetran)
- `acuantia.ods` - Operational Data Store

### 4. Cross-Project Coordination
- Integration with `callrail_data_export` Python pipeline
- Integration with `dialpad_data_integration` Python pipeline
- Coordination with `looker/` project for BI layer
- Schema change protocol across all three layers

### 5. Source System Documentation
- SAP ERP field naming (KUNNR, NAME1, KTOKD)
- Dialpad API patterns (transcripts, sentiment)
- CallRail API patterns (tracking numbers, attribution)
- Business context (Septic, General, Industrial, Chemical verticals)

## What This Skill Does NOT Include

**Defers to `dataform-engineering-fundamentals`**:
- TDD workflow (write tests first)
- Safety practices (--schema-suffix dev, --dry-run)
- ${ref()} enforcement (general cases)
- columns: {} documentation standards
- Architecture patterns (layered structure)
- Schema configuration rules (operations, tests)
- Troubleshooting guidance
- Time pressure protocol

**Why**: Avoids duplication, maintains single source of truth for generic practices, reduces maintenance burden.

## Usage Pattern

When working on Acuantia Dataform projects:

1. **First**: Use `dataform-engineering-fundamentals` skill
   - Apply ALL generic Dataform best practices
   - Follow TDD, safety practices, documentation standards

2. **Then**: Use `acuantia-dataform` skill
   - Add Acuantia-specific patterns on top
   - ODS ref() syntax, Looker conventions, dataset names

The acuantia-dataform skill explicitly states at the top:
> **YOU MUST USE `dataform-engineering-fundamentals` SKILL FIRST.**

## Benefits of This Architecture

1. **Single Source of Truth**: Generic practices live in one place
2. **Easy Maintenance**: Updates to generic patterns don't require updating acuantia-dataform
3. **Clear Separation**: Obvious what's generic vs. organization-specific
4. **Lean and Focused**: 58% smaller, faster to read and process
5. **Reusable Foundation**: dataform-engineering-fundamentals can be contributed upstream

## Related Skills

- **Builds upon**: `dataform-engineering-fundamentals` (REQUIRED)
- **Coordinates with**: Acuantia project documentation in parent CLAUDE.md

## Testing

This skill extension was validated by:
- Ensuring all Acuantia-specific patterns are captured
- Verifying no duplication with generic skill
- Testing that prerequisite relationship is clear
- Confirming skill hierarchy works in practice

---

**Note**: This is an internal Acuantia skill, not intended for upstream contribution. The generic `dataform-engineering-fundamentals` skill is suitable for contribution to the superpowers repository.
