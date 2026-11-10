# Working rules for CD-Tower-defence

This is a 2-week school project: a tower defence game themed around České dráhy (Czech Railways), built by two students as a pair. Each student works with their own Claude. This file is shared, so both Claudes follow the same rules.

## Goal and requirements

- A working game, delivered as a Windows `.exe` (Python + pygame, packaged with PyInstaller, built on a Windows machine).
- Written documentation of a few pages: what the game is about and what it does.
- A private GitHub repo that both students commit to, so each person's contribution is visible.
- A personal corrections log per student (see below).

## Who you are working for

At the start of a session, confirm which student you are working for. Use their identity for commits:

| Student | Name | GitHub | Commit email |
|---|---|---|---|
| Robin | Robin Loebe | rloebe | 194109139+rloebe@users.noreply.github.com |
| Partner | _partner fills in_ | _username_ | _their GitHub noreply email_ |

Never commit under the other student's identity.

## Workflow: plan, branch, build, fix, merge

1. **Plan first.** Before writing code for a feature, agree the plan with the student you're working for. Ask clarifying questions and confirm your understanding before building. Flag tradeoffs honestly and push back when something is a bad idea.
2. **Branch.** Never commit to `main`. Work on a branch named `<firstname>/<short-feature>` (e.g. `robin/enemy-path`). Pull `main` before creating it.
3. **Build and push the branch.** Commit in small, meaningful steps and push the branch.
4. **Test and fix.** The student tests it. Fixes happen on the same branch.
5. **Merge into `main`.** The student does this themself in the terminal:
   ```
   git checkout main
   git pull
   git merge --no-ff <branch-name>
   git push
   ```
   Don't merge into `main` for them.
6. The other student pulls `main` before they start their next session.

Split work by file or feature so both students don't edit the same file at the same time.

## Commits

- Author is the student you're working for (their name and noreply email from the table above). Committer is Claude.
- Keep the `Co-Authored-By: Claude ...` line at the end of every commit message. Don't remove it.
- Example:
  ```
  GIT_AUTHOR_NAME="Robin Loebe" GIT_AUTHOR_EMAIL="194109139+rloebe@users.noreply.github.com" \
  GIT_COMMITTER_NAME="Claude" GIT_COMMITTER_EMAIL="noreply@anthropic.com" \
  git commit -m "Add enemy path following"
  ```
- Short, clear messages in English.

## Corrections log

Each student has their own file: `CORRECTIONS-<firstname>.md`. Whenever the student corrects something you wrote, because it didn't work or wasn't what they wanted, add a row to **that student's** file in the same commit as the fix: date, file or feature, what you produced, what was wrong, how it was fixed, and who fixed it. Be honest in the "what was wrong" column. If the student's file doesn't exist yet, create it from `CORRECTIONS-TEMPLATE.md`.

## Tech notes

- Python + pygame, dependencies in `requirements.txt`.
- Code lives in `src/`, images/sounds/fonts in `assets/`, documentation in `docs/`.
- Test the PyInstaller `.exe` build early (well before the deadline), since packaging problems show up late.
