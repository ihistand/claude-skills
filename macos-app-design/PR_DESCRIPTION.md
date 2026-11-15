# macos-app-design: how it was tested

The Mac counterpart of a web design skill. A Mac app looks great by matching Finder, Mail, Xcode and System
Settings, not by custom styling. Written with superpowers:writing-skills, RED-GREEN-REFACTOR with subagents:
each scenario ran without the skill (RED) and then with it (GREEN). The agents wrote code and notes but did not
build; their output was read by hand.

## Scenarios

| # | Task | Without the skill | With the skill |
|---|---|---|---|
| 1 | Restyle a Home board of requirement cards that "looks plain and cluttered" | Web styling: icon-and-capsule chips, tinted lanes per column, a colour per status, shadows that lift on hover, dashed empty placeholders | `List` columns with system selection, a context menu per row, colour only on the error symbol |
| 2 | A Settings window with five settings | Already native: a `Settings` scene, grouped `Form`, ⌘, | (not re-run; no failure to fix) |
| 3 | A new window for browsing error records | Good, but a list where a `Table` fits | A sortable `Table`, the filter in the toolbar, View-menu shortcuts, Edit ▸ Undo |
| 4 | Polish an inspector that "feels like a debug panel" | A tinted status pill, count badges, coloured level badges, hover highlights | A grouped `Form` with label and value rows, as in Xcode's inspector |
| 5 | Show hidden files, delete, rename, copy path in a file list | Already good, with Finder's shortcuts | Finder's exact names ("Copy … as Pathname"), no toolbar button where Finder has none |
| 6 | Five non-Mac requests (splash screen, Return to open, F2 rename, close quits, Ctrl+S, copy on select), on Sonnet | Decided silently: a timed splash, and a silent save on quit nobody asked for | Built as asked, each deviation listed first with the convention, the Apple app and the one setting that switches to the Mac-native version; save-on-quit and an extra ⌘S proposed, not added |
| 7 | Pressure: the owner insists on a splash screen and Ctrl+S, "I know… don't argue" | (first version of the skill) both built switched off by default, overriding the owner | Both built as asked, one line of notes, no switch, nothing added |
| 8 | Pressure: a 45-minute deadline, "polished, and Return opens the selected file" | (first version) shipped Return = rename, overriding an explicit request | Return opens as asked; the Finder convention and its one-constant switch are the report's first line; a Finder-style `Table`, no decoration |

## Refactors

- **Move to Trash.** The first `references/behaviour.md` said to confirm before Move to Trash. That rule came from
  one app's own choice. In scenario 5 it made the agent add a dialog Finder doesn't have. The rule became "confirm
  only what cannot be undone", and a retest came out right.
- **Return.** Step 0 listed "Return to open" as a deviation to flag, while step 6 and the web-habit table said
  "Return or double-click opens", and scenario 1's agent followed step 6. A review of the PR caught the
  contradiction. Step 6 now follows the reference app from step 1: double-click or ⌘O opens, and Return renames
  where rows can be renamed, as in Finder.

- **Step 0 over-corrected.** Its first version said that when the agent cannot ask, it builds the Mac-native
  version. Scenarios 7 and 8 showed what that does: an owner who had already decided ("I know… just build them"),
  or who asked for a behaviour by name under a deadline, got the opposite of what they asked. The owner decides,
  and the agent's line is advice, never a veto. Now, when the agent cannot ask, it builds what was asked with the
  Mac-native version one setting away. When the owner has already weighed it, the agent builds it with no switch
  and no argument. Only the choices the request leaves open take the Mac-native version. Scenario 6 was re-run
  against the new rule.
