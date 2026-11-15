---
name: macos-app-design
description: Use when designing, restyling or polishing the UI of a native macOS app in SwiftUI or AppKit - a new window, screen, sheet, inspector or settings pane, or a request to make an existing Mac screen look better, cleaner, less cluttered or more modern.
---

# Designing macOS apps

## Overview

**A Mac app looks great by looking like the Mac.** People judge a Mac app against Finder, Mail,
Xcode and System Settings, not against websites. Its character comes from what it shows and how it
orders it, through hierarchy, density and the right container, never from custom chrome.

The usual failure is web styling: chips, cards with shadows, tinted lanes, hover lifts and a
custom colour per category. Each one makes a SwiftUI screen look like a dashboard in a browser.

## When to use

- Building a new Mac window, screen, sheet, popover, inspector or Settings pane.
- "Make it look better", "it looks plain or cluttered", "modernise this view" on a Mac app.
- Reviewing a Mac screen's design.

Not for iOS or iPadOS, whose idioms differ (large titles, cards, tab bars), and not for web
pages; use frontend-design there.

## The recipe

Work through these in order and write the answer to each down before you write code.

0. **Check the request against Mac convention.** For each requested behaviour that differs from
   what Apple's own apps do, write one line with three parts: the convention, which Apple app shows
   it, and the Mac-native alternative. Common cases:
   - a splash screen;
   - Return to open, or F2 to rename;
   - Ctrl in place of ⌘;
   - closing the window quits the app;
   - copy on select;
   - a heuristic that acts for the user.

   The owner decides each one. Then:
   - **When you can ask the owner** (you are talking to them), put those lines to them and wait
     for an answer before building the items that depend on it. Build the rest meanwhile.
   - **When you cannot ask** (a subagent, a headless run), build the Mac-native version. Make the
     requested version a single setting or constant away. List each deviation at the top of your
     report, with that line and where to change it.
   - **Either way, never add behaviour the request didn't ask for** to make up for a deviation, such
     as a silent save on quit. Propose it in the same list instead.

1. **Name the closest system app** that does the same job, and take its structure:
   - a list of records with details: Mail, Reminders;
   - files or a hierarchy: Finder;
   - documents with an inspector: Pages, Xcode;
   - preferences: System Settings;
   - a dashboard: Activity Monitor.
2. **Pick the window structure:**
   - `NavigationSplitView` for a sidebar, content and detail;
   - `.inspector` for properties of the selection;
   - `.toolbar` for the window's commands;
   - a `Settings` scene for preferences;
   - `.sheet` for a short task that blocks the window.
3. **Pick the content containers.** Each kind of content has its own:

   | Content | Container |
   |---|---|
   | Records with several fields (ID, state, date) | `Table`, with sortable columns |
   | A list to pick from, or a sidebar | `List` with selection |
   | Properties, or settings | `Form` with `.formStyle(.grouped)`, `LabeledContent` |
   | Aligned label and value pairs | `Grid` or `LabeledContent` |
   | A bordered group inside a pane | `GroupBox` |
   | A tree | `OutlineGroup`, or a `List` with children |
   | Nothing to show | one `ContentUnavailableView` for the whole area |

4. **Make the hierarchy with type and space, not boxes:**
   - Use system text styles only: `.title2`, `.title3` or `.headline` for headings, `.body` (13 pt)
     for text, `.callout` and `.caption` for detail.
   - Use `.secondary` and `.tertiary` foreground styles for what matters less.
   - Use SwiftUI's default padding and spacing. Mac layouts are denser than web: rows of 22–28 pt,
     and 16–20 pt margins, not 32.
5. **Use colour only for meaning:**
   - The accent colour marks selection and the primary action.
   - Red, orange and green mean error, warning and success, each paired with an SF Symbol so colour
     is never the only signal.
   - Give categories a colour only when the category is the point of the screen.
   - Never tint a background as decoration.
   - Take materials from the system containers (sidebar, toolbar, popover, sheet). Never hand-build
     blur or glass.
6. **Make it behave like a Mac:**
   - Selection with a highlight, and Return or double-click to open the selected item.
   - Arrow keys and Tab move between items.
   - Every toolbar action is also a menu-bar command, with a shortcut where it is frequent
     (`.commands`, `.keyboardShortcut`).
   - A context menu on every row.
   - Undo for anything reversible.
   - Hover changes only what the system changes (toolbar buttons, links), never a lift or a glow.

   **Read `references/behaviour.md` first when the change does any of these:**
   - adds a command, a shortcut, a menu, a destructive action, a panel or a permission;
   - touches launch, saved state or Settings;
   - builds a custom AppKit control;
   - chases a layout or drawing bug.

   It covers:
   - checkmarked toggles, disabled items, and Apple's standard names and shortcuts;
   - shortcut clashes and context menus;
   - undo and Move to Trash;
   - prompts and focus, and the sandbox;
   - launch and session state;
   - accessibility of custom views;
   - measuring layout bugs.
7. **Look at it before you call it done.** A clean build and green unit tests prove little about
   layout.
   - Render it as an Xcode preview (with the xcode plugin's preview tool), or build it and capture the
     window with `screencapture -l <windowid>` or an XCUITest screenshot.
   - Check light and dark, the narrowest and the widest window, Increase Contrast, and VoiceOver on
     one row.
   - Put the screenshot beside the system app from step 1. Remove anything that system app would not
     have.

## Web habit → Mac equivalent

| Web habit | On the Mac |
|---|---|
| Metadata as icon-and-capsule chips | Secondary text, or label and value rows in a `Form` or `Grid` |
| Cards with shadows and rounded fills | `List` rows, `Form` sections or `GroupBox`; the system draws the edges |
| A hover lift, shadow or coloured border | Selection highlight and a context menu |
| A tinted lane or panel per column | A section header with its count, on the window's own background |
| A custom colour per status or category | The status in words, with a symbol where it helps; accent only for selection |
| A coloured banner box per alert | A row in a list of issues, or one standard banner |
| A dashed placeholder in each empty column | Nothing, or "None" in secondary text; `ContentUnavailableView` when the whole view is empty |
| A custom `Layout` to wrap tags | Text that wraps, or a `Table` column |
| A segmented filter inside the sidebar | `.searchScopes`, or a toolbar `Picker` |
| An icon on every label | Icons where Mac apps put them: sidebar rows, toolbar buttons, menu items |
| A click on a card navigates away | Click selects; Return or double-click opens; the detail follows the selection |
| Fixed columns at any width | Content that reflows, or a `Table` the user can resize |

## Red flags: stop and go back to the recipe

Stop when you notice yourself doing any of these:
- writing `.shadow(`, `cornerRadius:` or `.opacity(0.1)` fills on content views;
- writing a `Color` per category, or a `switch` that maps statuses to colours;
- writing `onHover` with an animation;
- writing a custom `Layout`;
- changing an item's visible words (capitalising a status, renaming a heading) to make it look nicer;
- skipping the screenshot because "it should look right".

## Related

When installed, the Xcode plugin's `swiftui-specialist` (data flow, identity, performance) and the
accessibility skills (VoiceOver, Dynamic Type, contrast) cover correctness. This skill covers how
the app looks and behaves as a Mac app.
