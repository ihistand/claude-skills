# How a Mac app behaves

Read this when a change adds a command, a shortcut, a menu, a destructive action, a panel or a
permission, in SwiftUI or AppKit.

## Menus and commands

- **Every command is in the menu bar,** including the ones that also have a toolbar button or a
  key handler. People find commands there and see their shortcuts.
  - SwiftUI: `.commands`, with `CommandGroup` and `CommandMenu`.
  - AppKit: build the items with a nil target, so the action goes through the responder chain to
    whatever has focus.
- **A toggle is a menu item with a checkmark** showing its current state:
  - SwiftUI: a `Toggle` inside the commands;
  - AppKit: `state = .on` or `.off`, set in `validateMenuItem`.
- **Items that cannot run right now are disabled, not hidden.** For example, "Go Up" at the top
  of the tree is disabled.
  - SwiftUI: `.disabled` together with `focusedValue` / `@FocusedValue`.
  - AppKit: one `validateUserInterfaceItem` method.
- **Leave out an item only when its target cannot exist on this Mac or in this build,** such as
  iCloud Drive when iCloud is off.
- **Commands work with no window open:** the app, not the window, answers them.
- **A setting can be both a Settings control and a checked menu item.** Then it stays reachable
  from the keyboard.

## Shortcuts

- **Use Apple's name and shortcut when one exists.** For example, "Paste and Match Style" is
  ⌥⇧⌘V, through the standard `pasteAsPlainText:` action, not an invented "Paste as Plain Text".
  Text fields and web views already answer the standard actions.
- **Copy the system apps' shortcuts for the same job** (Finder's Go menu, Mail's message
  commands). When one clashes with yours, move yours.
- **Check a shortcut is free before you bind it,** in your own menus and in the text system.
  Never take a text view's own editing keys (⇧⌘↑, ⌥⌘↑, ⌥←…).
- **A shortcut includes ⌘ or ⌃.** A plain key or an ⌥ combination types a character (⌥P types
  π).
- **A shortcut the user sets is refused on a clash, with the name of the item that already has
  it.** Say in its help that System Settings ▸ Keyboard ▸ App Shortcuts can override any menu item
  by its title.

## Context menus

- **Build the menu for the row that was clicked,** and show only the items that apply to it (a
  folder-only item does not appear on a file).
  - AppKit: `menuNeedsUpdate` with `clickedRow`.
  - SwiftUI: `contextMenu(forSelectionType:)`.
- **The context menu repeats the menu-bar commands for that item.** It holds nothing new.

## Destructive and reversible actions

- **Confirm only what cannot be undone.** Anything the app can undo is undone with ⌘Z
  (`UndoManager`, with the action's name in Edit ▸ Undo) and asks nothing first.
- **Deleting a file is Move to Trash (⌘⌫).** When the app registers its undo, which puts the
  file back as Finder does, it asks nothing, as in Finder. When the app cannot undo it, confirm
  first, with a warning alert: "Move to Trash" and "Cancel", and the line "You can restore it from
  the Trash."
- **A delete that skips the Trash always confirms,** with a warning alert that names the item and
  says it cannot be undone. Examples: Delete Immediately (⌥⌘⌫), or a volume with no Trash.
- **Never overwrite silently.** A name clash is an error, shown to the user.
- **A view that blocks on Accept or Reject treats closing it as Reject,** so its result always
  arrives exactly once.

## Panels, sheets and small prompts

- **Use the system's own panels before building one:**
  - `NSOpenPanel` / `.fileImporter`, with a prompt such as "Move Here";
  - `NSWorkspace` for Reveal in Finder and Open With;
  - `NSPopover` / `.popover` for Get Info on an item.
- **A one-line prompt (rename, new name)** is an alert with a text field. The field has focus when
  it opens, and a rename starts with the current name, its base name selected.
- **A floating panel handles its keys at the window level,** so they work whichever view has
  focus:
  - Return, Esc and ↑/↓ are handled by the panel;
  - after a click in a list, focus goes back to the field;
  - Return confirms an input method's text while it is composing;
  - number shortcuts follow the key's position, so they work on non-QWERTY layouts.
- **A panel that looks borderless is a titled panel with a transparent title bar,** so its edges
  can still be dragged to resize it.

## Sandbox, App Store and permissions

- **Don't show a control that cannot work in this build.** A sandboxed or App Store build hides a
  feature the sandbox blocks, so it never offers a switch that does nothing.
- **File access in the sandbox comes from the user, through a panel.** Keep it across launches with
  a security-scoped bookmark. To reach a hidden folder, ask for a broader parent folder.
- **Privacy-sensitive background features are off by default,** and honour the system's own
  signals (concealed and transient pasteboard types, `NSPasteboard.accessBehavior`). Never raise a
  system prompt from a timer.
- **The Accessibility permission belongs to one copy of the app.** When it is on for another copy
  (an older download, a Debug build), say how to remove the app with − and add it again.

## Launch, state, settings and alternative views

- **No splash or launch screen** unless the owner asks for one (SKILL.md step 0). When startup feels slow, show the main window sooner by deferring
  work (restoring the session, scanning files, starting helpers) until after it appears.
- **Prefer an explicit command to a clever heuristic.** When the app can't tell two cases apart
  reliably, give the user a one-click command and keep the simple default. One example is an
  automatic title change the user wants to keep: offer "Keep Current Title" instead of guessing
  which titles to keep. A heuristic that guesses wrong reads as a bug.
- **Never lose the user's state.** When part of a saved session can't be restored (a file is
  missing or unreadable), keep it in the saved session and offer Try Again or Forget. Never
  write back the shorter list.
- **Closing a Settings window commits the value being edited.** AppKit: `makeFirstResponder(nil)`
  in `windowWillClose`, so a half-typed number is saved rather than dropped.
- **Defaults that follow another platform's habits ship off.** Terminal copy-on-select is one
  example.
- **Offer another way to view content (a table for a CSV, a preview for Markdown) with a small
  hint. Never switch to it automatically.** The plain view stays the default when the other view
  would rewrite the file.
- **Keep one source of truth.** Other views read it, and only one surface edits it at a time.

## Custom AppKit views: accessibility and appearance

- **A plain `NSView` is not an accessibility element** until it has a role. A custom tab strip is
  a tab group of radio-button tabs, with a "Close Tab" custom action.
- **An element reports itself dimmed unless `setAccessibilityEnabled(true)`.**
- **A label inside a custom button can answer the accessibility hit test through its cell,**
  even with `setAccessibilityElement(false)`. Make the button's `hitTest` return the button.
- **Route appearance changes through one place.** Every view that draws its own colours
  re-styles when light or dark changes. A reusable view never sets `NSApp.appearance` itself.

## Checking it

- **Keep logic in types with no UI, and unit-test them.** Compiling and green unit tests prove
  little about layout, though: launch the app and take screenshots, in light and in dark.
- **Run the checks in each build that ships.** A sandboxed debug build (Debug settings with the
  App Store entitlements, signed ad hoc) shows sandbox-only bugs before TestFlight.
- **Tests use their own pasteboard and their own defaults suite,** never the user's real ones.
- **A refactor's bar is "no visible change":** its UI tests pass unchanged.
- **Measure a layout or drawing bug before you explain it.**
  - Build the view in a real `NSWindow` in a throwaway test, let layout settle, and print the real
    geometry and control state before proposing a cause.
  - A view that sets `translatesAutoresizingMaskIntoConstraints = false` stays zero-sized when
    you assign `.frame`, and every geometry assertion then passes silently. Host it with
    constraints.
  - Settle with several `layoutSubtreeIfNeeded()` and short run-loop passes; one is often not
    enough.
  - `xcodebuild test` (as of Xcode 26) does not pass your environment to the test runner, so a debug print gated
    on an environment variable never fires.
- **Some "bugs" are the system's own behaviour.** With System Settings ▸ Appearance ▸ Show scroll
  bars on Automatic and no mouse attached, scroll bars are overlay bars. They appear only while
  scrolling in their direction, and macOS 26 does not reveal them on hover (re-check on a newer macOS). Check the setting
  before changing the app.
- **AppKit facts measured on macOS 26** (re-check on a newer macOS before you rely on one):
  - An `NSScrollView` with legacy scrollers reserves no space for them: content draws under the
    bars.
  - An `NSScroller` fixes its orientation from the aspect ratio of the frame it was created with;
    created at `.zero`, it is vertical.
  - A disabled `NSScroller` draws nothing.
  - `needsLayout = true` set inside `layout()` is ignored; set it on the next run-loop turn.
