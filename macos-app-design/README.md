# macos-app-design

An [Agent Skill](https://agentskills.io) for designing native macOS apps in SwiftUI or AppKit. It is the Mac
counterpart of a web design skill: a web page wants a look of its own, while a Mac app looks great by looking like
the Mac.

Claude loads it when you design, restyle or polish a Mac window, screen, sheet, inspector or Settings pane. It also
loads when you ask for an existing Mac screen to look better, cleaner or more modern.

## What it does

- **Checks the request against Mac convention first.** Before building something Apple's apps don't do (a splash
  screen, Return to open, Ctrl in place of ⌘), it tells you the convention and the Mac-native alternative. You
  decide. When it can't ask, it builds what you asked for, with the Mac-native version one setting away.
- **Takes its structure from the closest system app** (Finder, Mail, Xcode, System Settings).
- **Uses the Mac's own containers** (`Table`, `List`, grouped `Form`, `Grid`, `GroupBox`, `.inspector`, a `Settings`
  scene) in place of web styling: chips, shadowed cards, tinted lanes, hover lifts, a colour per status.
- **Keeps colour for meaning,** and makes the screen behave like a Mac: selection, menu-bar commands with shortcuts,
  context menus and undo.
- **Looks at a screenshot of the running app,** in light and dark, before calling a screen done.

`references/behaviour.md` is read when a change touches commands, shortcuts, menus, destructive actions, panels,
permissions, launch, saved state, Settings or custom AppKit controls, or when a layout bug needs chasing.

## Install

With the [`skills`](https://skills.sh) CLI (Claude Code, Cursor, Codex and others):

```bash
npx skills add ihistand/claude-skills -s macos-app-design
```

Or as a Claude Code plugin, from the [ihistand/claude-plugins](https://github.com/ihistand/claude-plugins)
marketplace:

```
/plugin marketplace add ihistand/claude-plugins
/plugin install macos-app-toolkit@ihistand
```

## Works well with

Xcode's own plugin (`/plugin install xcode@claude-plugins-official`, which needs an Xcode with agent support) adds
SwiftUI previews and Apple's `swiftui-specialist` and accessibility skills. Those cover code correctness; this skill
covers how the app looks and behaves.

## Files

| File | What it holds |
|---|---|
| `SKILL.md` | The recipe, the web-habit-to-Mac table and the red flags |
| `references/behaviour.md` | Menus and shortcuts, context menus, undo and Move to Trash, panels and focus, the sandbox, launch and state, custom-view accessibility, measuring layout bugs |
| `PR_DESCRIPTION.md` | How the skill was tested: each scenario without and with it, and what changed after |
