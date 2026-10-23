# Solution: PR Test Agent

A GitHub Actions workflow runs a custom Claude Code agent (`test-writer`) on every pull request. The agent reads the PR diff, decides whether tests are needed, writes or updates unit tests for the backend (pytest) and frontend (Vitest/Jest + React Testing Library) using reusable skills, runs them, pushes passing tests to the PR branch, and posts a summary comment on the PR.

## Files

| Path | Purpose |
|---|---|
| `.github/workflows/pr-tests.yml` | Trigger, environment setup, runs the agent |
| `.claude/agents/test-writer.md` | The custom agent: the decision logic and the procedure |
| `.claude/skills/backend-tests/SKILL.md` | Skill: how to write and run backend tests |
| `.claude/skills/frontend-tests/SKILL.md` | Skill: how to write and run frontend tests |

## Main technical decisions

- **`anthropics/claude-code-action` as the agent runtime.** It is the smallest GitHub-native way to run an agent. It handles checkout context, tool permissions, and the model loop, so no custom orchestration code is needed.
- **Agent and skills are plain Markdown files in `.claude/`.** The agent holds the decision logic (analyze diff, decide, verify, report). The skills hold stack-specific knowledge (where tests live, which libraries, which commands). Splitting them means a new stack, such as a second service, only needs a new skill.
- **The agent runs the real test commands, not a simulation.** Dependencies are installed before the agent starts, so it can iterate on failures (max 3 attempts). Tests are only pushed if the suite passes.
- **Commits go to the PR branch; the report goes in a PR comment.** Both are visible in the PR context without extra tooling.
- **The agent never edits non-test source code.** A failing test caused by an apparent source bug is reported, not worked around. This keeps the agent from masking defects.
- **`GITHUB_TOKEN` rather than a PAT.** It needs no extra setup and is scoped to the job. It also prevents workflow loops, because commits it pushes do not re-trigger workflows.

## How to run the PR workflow

### Prerequisites

1. Repo secret `ANTHROPIC_API_KEY` (Settings → Secrets and variables → Actions). It must come from the Anthropic API Console, with billing credits added.
2. Settings → Actions → General → Workflow permissions: **Read and write**, and enable **Allow GitHub Actions to create and approve pull requests**.
3. The Claude GitHub app installed on the repo: https://github.com/apps/claude
4. The four files above merged into `main`. For a PR already open, push a new commit after updating the workflow so the run picks up the change.

### Running it

Open or update a PR that touches `backend/**` or `frontend/**`. The workflow starts automatically.

## Limitations

- **Non-deterministic output.** Test quality depends on the model. Tests can pass but assert weak or trivially true behavior. Humans should still review them.
- **Forked PRs are skipped**, because secrets are unavailable to them.
- **No CI re-run on the agent's commit.** Commits pushed with `GITHUB_TOKEN` do not trigger other workflows, so other required checks will not re-run on the agent's push unless a PAT or GitHub App token is used.
- **Coverage is reported, not enforced.** There is no threshold or gate.
- **Unit tests only.** There are no integration or end-to-end tests, and no snapshot or visual testing.
- **Large PRs** may exceed the agent's context or turn budget, leaving partial coverage.
- **Each run costs API credits**, and there is no cost cap besides the limit set in the Anthropic Console.

## What I would change for production

- Use a GitHub App token or PAT for pushes so downstream CI runs on the agent's commits, and make that CI a required check.
- Enforce coverage on changed lines (e.g. `diff-cover`) as a status check, instead of relying on the agent's self-report.
- Set explicit turn and cost limits on the action, and a monthly spend cap on the API key.
- Add a Postgres (or other) service container so tests that need real dependencies work.