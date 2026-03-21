---
description: Critical rules for Test-Driven Development and running tests in this repository
---

# Critical Testing Rules for Agents

## 1. Test Environment Execution
When running tests in this project, you **MUST** use the project's virtual environment and Python path.
**Command to execute:**
```bash
PYTHONPATH=. .venv/bin/pytest
```
*Do not* attempt to run the global `pytest` binary blindly, as it will fail module imports and give inaccurate results.

## 2. Mandatory Communication Upon Failure
If the testing framework hangs, throws unrelated environment errors, or outright fails to execute:
- **YOU MUST NOT KEEP SILENT.**
- Immediately halt any assumptions about the codebase.
- Explicitly notify the user that tests are currently un-runnable and explain the exact output of the failure.

## 3. Strict Adherence to Red/Green TDD
- Skipping test verification or moving forward while tests are hanging/failing because of environment setup violates the Red/Green loop.
- Never "fake" a successful execution loop or assume code changes work correctly without witnessing the actual output of a green test suite.
- Lying or proceeding under false assumptions risks the entire project integrity. Stop and fix the test environment first.
