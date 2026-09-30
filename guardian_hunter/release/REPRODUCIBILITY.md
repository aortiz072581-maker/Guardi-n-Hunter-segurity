# Guardian Hunter — Reproducibility Contract

A buyer evaluation should be able to reproduce the documented
validation results from a clean project state.

Required evidence:

1. source revision
2. Python version
3. Node.js version
4. dependency inventory
5. test commands
6. test output
7. safety invariant output
8. known limitations

The validation environment must not silently enable real execution.

Required state:

READ_ONLY=True
DRY_RUN=True
REAL_EXECUTION_BLOCKED=True
HUMAN_REVIEW_REQUIRED=True
RESPONSE_LOCKED=True
