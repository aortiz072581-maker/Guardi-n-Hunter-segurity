# Guardian Hunter Architecture

## High-level flow

INPUT
  ↓
ANALYSIS
  ↓
EVIDENCE
  ↓
RISK STATE
  ↓
DEFENSIVE RESPONSE
  ↓
SAFETY GATE
  ↓
HUMAN REVIEW
  ↓
LOCKED RESULT

## Execution boundary

The product intentionally maintains:

READ_ONLY=True
DRY_RUN=True
REAL_EXECUTION_BLOCKED=True

The architecture does not treat detection as authorization for execution.

## Integration model

External systems may consume defensive results through documented
interfaces without granting Guardian Hunter permission to perform
real-world actions.
