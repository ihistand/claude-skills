# Gemini Context: claude-skills

This file provides context to the Gemini CLI agent when working in this repository.

## Project Overview

This is a **skills development repository** for creating and testing Claude Code superpowers skills. Skills are reusable process documentation that enforce discipline and best practices across different domains.

**Skills in this repo**: `sqlanvil-engineering-fundamentals` (delta guide for sqlanvil data projects on Postgres/Supabase/MySQL — synced to each sqlanvil release, currently 1.19.0), `dataform-engineering-fundamentals` (BigQuery Dataform TDD discipline), plus `acuantia-dataform` and `stl-generator`. See [`CLAUDE.md`](./CLAUDE.md) for conventions (testing workflow, contribution process).

**Related Ecosystem**: This repository is part of the broader superpowers framework (https://github.com/obra/superpowers), which provides skills for Claude Code and other AI assistants.

## Key Concepts

- **Skills**: Markdown files that provide specialized instructions to Claude Code agents. They enforce discipline and are designed to be "bulletproof against rationalization".
- **Superpowers Framework**: A framework for creating and using skills with AI assistants.
- **Testing**: Skills are tested using a RED-GREEN-REFACTOR workflow.

## dataform-engineering-fundamentals

This is the main skill in this repository. It is a domain-specific adaptation of TDD principles for Google Cloud Dataform.
