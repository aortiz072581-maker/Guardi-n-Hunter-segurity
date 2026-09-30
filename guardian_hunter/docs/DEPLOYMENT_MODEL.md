# Guardian Hunter — Deployment Model

## Evaluation deployment

Guardian Hunter can be evaluated in an isolated development or
test environment.

## Integration boundary

External systems may provide data to defensive analysis interfaces
and consume structured results.

## Safety boundary

Detection and analysis do not automatically authorize remediation.

The product remains:

- READ_ONLY
- DRY_RUN
- REAL_EXECUTION_BLOCKED
- HUMAN_REVIEW_REQUIRED
- RESPONSE_LOCKED

## Production consideration

Any future production deployment requiring actions outside the
current defensive boundary must undergo separate security review,
authorization design, testing, and human approval.
