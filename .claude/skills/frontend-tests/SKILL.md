---
name: frontend-tests
description: Write and run unit tests for the React/TypeScript frontend.
---

- Put tests next to the source as `X.test.tsx` / `X.test.ts`, following the style of existing tests and the test runner already configured in `frontend/package.json`.
- Use React Testing Library: query by role/text, simulate user events, mock network calls. Test behavior, not implementation details. Cover render, interaction, loading/error states.
- Run from the repo root:
```
  npm test --prefix frontend -- --run
  npm run test:coverage --prefix frontend
```
- Report coverage for the changed files.