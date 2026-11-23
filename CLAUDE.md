# Working rules for CD-Tower-defence

School project: a tower defence game themed around České dráhy (Czech Railways), built by two students as a pair. Each student works with their own Claude. This file is shared, so both Claudes follow the same rules.

**Deadline: 24 Nov 2026.** Scope is deliberately small. Finishing beats adding features.

## The assignment (teacher's definition of done)

The game counts as done when:
- It runs on someone else's computer by following the README.
- The README has: game description, controls, how to run it, technologies used.
- There are some automated tests and/or a manual test scenario (we have both: `tests/` and `docs/testovaci-scenar.md`).
- Git history is clean and readable, and each student has commits under their own name.

Required outputs:
- Design document: `docs/design-dokument.md`
- Repo with commits from each student
- README
- AI failure diary (*Deník selhání AI*), one per student, at least 3 real cases
- Short individual retrospective, one per student
- There is an **individual oral defence**, so each student must be able to explain the code they committed. Keep code simple and readable, and explain what you build.

No `.exe` is required. Don't spend time on PyInstaller.

## Language

- Everything a player or the teacher reads is in **Czech**: in-game text, README, docs, diaries, retrospectives.
- Code identifiers in English; short code comments in Czech.
- Commit messages: short, in English.

## Who you are working for

At the start of a session, confirm which student you are working for. Use their identity for commits:

| Student | Name | GitHub | Commit email |
|---|---|---|---|
| Robin | Robin Loebe | rloebe | 194109139+rloebe@users.noreply.github.com |
| Partner | Matěj Volf | VolfM | 194108824+VolfM@users.noreply.github.com |

Never commit under the other student's identity.

## Before every task: check GitHub

Run `git fetch` and look at the remote branches and `main` (log + files) so you know what's done and what isn't before planning anything. Tell the student what you found.

## Work split

| Area | Owner | Files |
|---|---|---|
| Game core: loop, states, map/track, enemies, waves | Robin | `src/main.py`, `src/game.py`, `src/settings.py`, `src/map.py`, `src/enemies.py`, `src/waves.py` |
| Tests, README, test scenario | Robin | `tests/`, `README.md`, `docs/testovaci-scenar.md` |
| Towers, shooting, buying/placing, money spending | Matěj | `src/towers.py` |
| Menu, HUD, end screens, buttons | Matěj | `src/ui.py` |
| Design doc | both | `docs/design-dokument.md` |
| Own diary + retrospective | each | `CORRECTIONS-<name>.md`, `RETROSPEKTIVA-<name>.md` |

Don't edit the other person's files. If you need a change there (e.g. a new attribute on the game state), tell your student so they can ask the other person, or keep it to a small, clearly described change.

### Interface between core and towers/UI

`src/main.py` calls these. Keep their signatures so the two halves stay compatible:
- `towers.TowerManager()` with `handle_event(event, game)`, `update(dt, game)`, `draw(surface, game)`
- `ui.handle_event(event, game)` returns `"start"`, `"restart"`, `"next_wave"`, `"quit"` or `None`
- `ui.draw_menu(surface)`, `ui.draw_hud(surface, game)`, `ui.draw_end_screen(surface, game)`

The game state (`src/game.py`, class `Game`) exposes: `state` (`"menu" | "playing" | "won" | "lost"`), `money`, `delay`, `max_delay`, `enemies`, `waves` (WaveManager), `path` (list of points), `tower_manager`, and helpers `map.is_on_path(pos, path, margin)`, `enemy.take_damage(amount)`, `enemy.progress` (distance along the track, for targeting the furthest enemy).

## Workflow: plan, branch, build, fix, merge

1. **Plan first.** Before writing code for a feature, agree the plan with the student. Ask clarifying questions and confirm your understanding before building. Flag tradeoffs honestly and push back when something is a bad idea.
2. **Branch.** Never commit to `main`. Branch from an up-to-date `main`, named `<firstname>/<short-feature>` (e.g. `robin/enemy-path`).
3. **Build and push the branch.** Commit in small, meaningful steps and push the branch.
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
- Code in `src/`, tests in `tests/`, docs in `docs/`. Graphics are drawn with code (shapes and text), no image files needed.
- Don't draw the real ČD logo or other brand marks; colours and names are fine.
- Game logic must not need an open window, so tests can run without a display.
