# Working rules for CD-Tower-defence

School project: a tower defence game themed around České dráhy (Czech Railways), built by two students as a pair. Each student works with their own Claude. This file is shared, so both Claudes follow the same rules.

**Game name: Výluka** (working title, not final yet). **Deadline: 24 Nov 2026.** Finishing beats adding features.

## The assignment

The teacher's original assignment (Czech) is in `docs/zadani.md`. Read it. Summary:

The game counts as done when:
- It runs on someone else's computer by following the README.
- The README has: game description, controls, how to run it, technologies used.
- There are some automated tests and/or a manual test scenario (we have both: `tests/` and `docs/testovaci-scenar.md`).
- Git history is clean and readable, and each student has commits under their own name.

Required outputs:
- Design document: `docs/design-dokument.md` (+ the visual design in `docs/vizualni-design.md`)
- Repo with commits from each student
- README
- AI failure diary (*Deník selhání AI*), one per student, at least 3 real cases
- Short individual retrospective, one per student
- There is an **individual oral defence**, so each student must be able to explain the code they committed. Keep code simple and readable, and explain what you build.

No `.exe` is required. Don't spend time on PyInstaller.

## Before every task: check GitHub and build around it

Always `git fetch` first and look at `main` and every remote branch (log + files) so you know what's done, what's in progress and what the other student changed. Tell your student what you found. Then build **on top of** what's there so both halves fit together: use the existing names, files and interfaces, don't duplicate something that already exists, and don't rewrite the other student's files. If something you need is missing from the other side, tell your student instead of inventing your own version.

## What the game must look like

The look is decided. Follow `docs/vizualni-design.md`: low-poly/voxel style like the game Unrailed, the camera angle and projection formulas, the map layout, all screens (loading, menu, game HUD, tower picker, station delay panel, coin popups, end screen), the colours and the animations. The exact shapes, coordinates and colours are in the design prototype sources in `docs/design-prototyp/` (`Sprite.dc.html` has every character as polygon lists you can port to `pygame.draw.polygon` directly). Don't invent a different look.

## Language

- Everything a player or the teacher reads is in **Czech**: in-game text, README, docs, diaries, retrospectives.
- Code identifiers in English; code comments in Czech.
- Commit messages: short, in English.

## Comments in the code (required)

The defence is individual, so the code must explain itself. In every file you write or change:
- A module docstring at the top: what the file is for and how it fits into the game.
- A docstring for every class and function: what it does, what the parameters mean (with units: tiles, pixels, seconds) and what it returns.
- A comment above every non-obvious block or line: **why** it's done this way, not just what it does (e.g. why we sort by depth, why `dt` is capped, why the map is pre-rendered).
- Plain, simple Czech that a student can read out and explain. No clever one-liners without a comment.

## Who you are working for

At the start of a session, confirm which student you are working for. Use their identity for commits:

| Student | Name | GitHub | Commit email |
|---|---|---|---|
| Robin | Robin Loebe | rloebe | 194109139+rloebe@users.noreply.github.com |
| Partner | Matěj Volf | VolfM | 194108824+VolfM@users.noreply.github.com |

Never commit under the other student's identity.

## Work split

| Area | Owner | Files |
|---|---|---|
| Game core: loop, game states, world/projection, map layout and drawing, track, enemies, waves | Robin | `src/main.py`, `src/game.py`, `src/settings.py`, `src/iso.py`, `src/world.py`, `src/scenery.py`, `src/track.py`, `src/enemies.py`, `src/waves.py` |
| Character drawing + animation for all 7 sprites (ported from `docs/design-prototyp/Sprite.dc.html`) | Robin | `src/sprites.py` |
| All screens and UI: loading screen, menu, HUD, tower picker, build-spot highlight, ghost tower under the mouse, station delay panel, coin popups, end screen | Robin (Matěj can take it back if he starts before Robin gets to it) | `src/ui.py` |
| Tests, README, test scenario | Robin | `tests/`, `README.md`, `docs/testovaci-scenar.md` |
| **Towers: types, building with the mouse, shooting, slowing, spending money** | **Matěj** | `src/towers.py` |
| **Ambient life: passing trains on the bottom line, cars, tractor, grazing cows, chimney smoke** | **Matěj** | `src/ambient.py` |
| Design doc | both | `docs/design-dokument.md`, `docs/vizualni-design.md` |
| Own diary + retrospective | each | `CORRECTIONS-<name>.md`, `RETROSPEKTIVA-<name>.md` |

Don't edit the other person's files. If you need a change there, tell your student so they can ask the other person, or keep it to a small, clearly described change.

## Plan for 23 Nov evening (updated: Matěj starts later, so Robin took over sprites and UI)

1. **Robin:** the isometric core on `robin/iso-core`: `iso.py`, `world.py` (map layout, `BUILDABLE`), track and enemies in tiles, new game states and fields, `sprites.py`, temporary keyboard-only `ui.py`, tests. Then the full map drawing (`scenery.py`) and the full `ui.py`.
2. **Matěj, as soon as he starts:** `src/towers.py` on top of `main` (after `robin/iso-core` is merged). Everything he needs is in the interface below. The tower sprites already exist in `sprites.py` (`"worker"`, `"draisine"`, `"dispatcher"`), so towers only need logic + calling `draw_sprite`.
3. Merge both, test together with `docs/testovaci-scenar.md`, fix bugs (each fix → diary entry).
4. Diaries (3+ real cases each), retrospectives, final README check, run it on another PC.
5. **Matěj, after the towers:** ambient life in `src/ambient.py`, exactly as described in `docs/vizualni-design.md` (section "Okolní život") – the same behaviour as in the design prototype.

## Interface between core and towers/UI

World coordinates are in **tiles** (floats), not pixels. Only drawing converts to the screen.

`src/iso.py` (Robin):
- `to_screen(x, y, z=0) -> (sx, sy)`, `to_tile(sx, sy) -> (col, row)`, `depth(x, y)` for draw order. Formulas are in `docs/vizualni-design.md`.

`src/main.py` calls these. Keep the signatures so the two halves stay compatible:
- `towers.TowerManager()` with `reset()`, `handle_event(event, game)`, `update(dt, game)`, `draw(surface, game)`. `handle_event` only receives events that `ui.handle_event` didn't turn into an action.
- `ui.handle_event(event, game)` returns `"start"`, `"restart"`, `"menu"`, `"next_wave"`, `"pause"`, `"speed"`, `"skip_loading"`, `"quit"`, `"ui"` (handled by the UI itself, e.g. a click on the picker; ignore it) or `None` (the event belongs to the towers, e.g. a click on grass = build)
- `ui.draw(surface, game)` draws the right screen for the game state (it calls `draw_loading`, `draw_menu`, `draw_hud`, `draw_end_screen`)
- `sprites.draw_sprite(surface, kind, center, size, phase=0.0, action=0.0, flip=False)` where `kind` is `"cow" | "signal" | "tree" | "closure" | "worker" | "draisine" | "dispatcher"`; `center` in real screen pixels (from `iso.to_screen`), `size` in logical pixels

Screen and sizes:
- The game runs **fullscreen** at the monitor's resolution (`python src/main.py --okno` = 960 × 640 window for debugging). Everything is designed for a logical 960 × 640 area, scaled by `settings.SCALE` and centred by `settings.OFFSET_X/Y`.
- Positions on screen always come from `iso.to_screen(...)` (already scaled). Pixel sizes you choose yourself (line widths, sprite size, offsets) are logical: convert with `iso.px(value)`.

Towers (what `towers.py` must provide and use):
- Tower stats are shared in `settings.TOWER_TYPES` (`name`, `price`, `range` in tiles, `damage`, `rate` in seconds, `slow`, `slow_time`) and `settings.TOWER_ORDER`. The picker in `ui.py` shows them; `towers.py` uses the same values.
- `game.selected_tower`: which tower the player picked in the picker (`"worker" | "draisine" | "dispatcher"`), set by `ui.py`. Build that one on click.
- `TowerManager.towers`: list of built towers; each tower has `col`, `row` (tile) and `kind`. `ui.py` reads them to show ranges and hide occupied build spots.
- Building: on a left click that `ui.handle_event` returned `None` for, take the tile from `iso.to_tile(*event.pos)`, check `track.can_build(col, row)`, that the tile is free and `game.money >= price`, then subtract the price.
- Drawing: `sprites.draw_sprite(surface, tower.kind, (sx, sy - iso.px(54) * 16 / 60), 54, phase=game.time, action=...)` where `(sx, sy) = iso.to_screen(col + 0.5, row + 0.5)`. `action` 0–1 = how much it's "working" right after a shot (worker swings, dispatcher raises the paddle).

Ambient life (`src/ambient.py`, Matěj) – `main.py` already loads it automatically when the file exists:
- `ambient.Ambient()` – created after the screen is set up (sizes are known).
- `update(dt)` – called every frame, always (loading, menu, game, pause); `dt` in seconds.
- `drawables()` – returns a list of `(depth, draw_function)`; `scenery.draw` sorts them together with map objects and enemies, so a train is correctly hidden behind a house. `depth = iso.depth(x, y)` of the object's centre; `draw_function(surface)` draws it.
- `draw_overlay(surface)` – things above everything on the map (chimney smoke).
- Use `iso.to_screen` for positions and `iso.px` for pixel sizes; reuse `scenery.box`, `scenery.tri` and `sprites.draw_sprite` (cows) instead of copying them. For speed, pre-draw each vehicle once (like `scenery.bake`) and only move it.

Game state (`src/game.py`, class `Game`):
- `state`: `"loading" | "menu" | "playing" | "won" | "lost"`; `load_progress` 0–1 while loading
- `money`, `delay`, `max_delay`, `kills`, `paused`, `speed` (1 or 2), `time` (seconds, for animations)
- `enemies`, `waves` (`.current`, `.total`), `wave_in_progress`, `path` (tile points), `tower_manager`
- `popups`: list of dicts `{"text", "x", "y", "coin": bool, "t"}` added by the core when an enemy dies (`+10` with coin, at the enemy) or reaches Praha (`+5 min`, no position); UI draws and the core removes them after ~1 s
- `track.can_build(col, row)` → True on free grass only (Robin); towers must use it
- `enemy.x`, `enemy.y` (tiles), `enemy.radius`, `enemy.progress` (distance along the track: target the highest one), `enemy.alive`, `enemy.take_damage(amount)`, `enemy.apply_slow(factor, duration)`
- `game.py` gives the reward, counts the kill and adds the popup when `enemy.alive` turns False, so towers only call `take_damage`.

## Workflow: plan, branch, build, fix, merge

1. **Plan first.** Before writing code for a feature, agree the plan with the student. Ask clarifying questions and confirm your understanding before building. Flag tradeoffs honestly and push back when something is a bad idea.
2. **Branch.** Never commit to `main`. Branch from an up-to-date `main`, named `<firstname>/<short-feature>` (e.g. `matej/ui`).
3. **Build and push the branch.** One commit per bigger change (see Commits), then push the branch.
4. **Test and fix.** The student runs it. Fixes happen on the same branch.
5. **Merge into `main`.** The student does this themself in the terminal:
   ```
   git checkout main
   git pull
   git merge --no-ff <branch-name> -m "Merge branch '<branch-name>'"
   git push
   ```
   Don't merge into `main` for them.
6. The other student pulls `main` before they start their next session.

## Commits

- Author is the student you're working for (their name and noreply email from the table above). Committer is Claude.
- Keep the `Co-Authored-By: Claude ...` line at the end of every commit message. Don't remove it.
- **One commit per bigger, meaningful change** (a feature, a screen, a fix of a real problem). No separate commits for tiny tweaks like a colour change; group them with the change they belong to. Never rewrite history that is already on `main`.
- Example:
  ```
  GIT_AUTHOR_NAME="Robin Loebe" GIT_AUTHOR_EMAIL="194109139+rloebe@users.noreply.github.com" \
  GIT_COMMITTER_NAME="Claude" GIT_COMMITTER_EMAIL="noreply@anthropic.com" \
  git commit -m "Add enemy path following"
  ```

## AI failure diary (Deník selhání AI)

Each student has their own file, `CORRECTIONS-<firstname>.md`, in the format of `CORRECTIONS-TEMPLATE.md`. The teacher requires, for each case: **what I wanted, what the AI did wrong, how I noticed, how I fixed it.** At least 3 cases per student.

Whenever the student corrects something you did, because it didn't work or wasn't what they wanted, add a case to **that student's** file in the same commit as the fix. Only real cases; never invent or embellish one. Be honest in "what the AI did wrong". If the student's file is still in the old table format, convert it to the template format first.

## Tech notes

- Python 3.12+ with **pygame-ce** (not plain `pygame`: it has no wheels for Python 3.14, so `pip install` fails on a fresh PC). The code still does `import pygame`.
- Run: `python src/main.py`. Tests: `python -m pytest`.
- Code in `src/`, tests in `tests/`, docs in `docs/`, font in `assets/fonts/`. Graphics are drawn with code (polygons), no image files.
- Don't draw the real ČD logo or other brand marks; colours and names are fine.
- Game logic must not need an open window, so tests can run without a display.
- Pre-render the static map (terrain, track, buildings) once into a `Surface` and blit it every frame; only moving things are drawn per frame.
