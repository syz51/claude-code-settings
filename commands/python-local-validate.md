if not in python project, alert the user. If in python project,
check the package manager, and use that to run ruff to fix 
both linting and formatting issues.
use `pyright` CLI (checks all files, not just open ones)
run tests with coverage report if available and analyse the results.
