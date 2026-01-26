# Error Handling Guidelines

## Overview

This document defines how errors are classified, interpreted, and communicated within the platform. It is intended for support engineers, backend engineers, and AI agents processing error-related tickets.

## HTTP Status Code Philosophy

### 4xx Client Errors

These indicate the client made an invalid request. The system is functioning correctly.

| Code | Interpretation | Support Response |
|------|----------------|------------------|
| 400 | Malformed request body or invalid JSON | Request code sample from customer |
| 401 | Missing or invalid authentication token | Verify token configuration, check expiration |
| 403 | Valid auth but insufficient permissions | Check role assignments, not a bug |
| 404 | Resource does not exist | Verify resource ID, check if deleted |
| 405 | HTTP method not allowed on endpoint | Client integration error |
| 409 | Resource conflict (duplicate key, etc.) | Expected behavior, guide customer on uniqueness |
| 422 | Validation failed (Pydantic rejection) | Provide exact field and constraint that failed |
| 429 | Rate limit exceeded | Verify customer tier, explain limits |

**Key principle**: 4xx errors are almost never platform bugs. They indicate the customer needs to change their request.

### 5xx Server Errors

These indicate the platform failed to process a valid request.

| Code | Interpretation | Support Response |
|------|----------------|------------------|
| 500 | Unhandled exception | Always investigate, always escalate |
| 502 | Upstream service unavailable | Check service health, may be transient |
| 503 | Service overloaded or in maintenance | Check deployment status, inform customer |
| 504 | Request timeout | Investigate slow queries, check for deadlocks |

**Key principle**: 5xx errors should be treated as potential bugs until proven otherwise.

## Common Misclassifications

### Customer Reports 500 But It's Actually 422

Frequent pattern: Customer says "getting 500 error" but the actual response is 422 with validation details in the body. Common causes:

- Customer's error handling discards response body
- Customer only logs status code, not message
- Frontend catches all errors as "server error"

**Action**: Always request the complete HTTP response including body and headers.

### Customer Reports Bug But It's Expected Behavior

Patterns observed from historical tickets:

1. **DELETE returning 204 with empty body** — not an error, RFC-compliant behavior
2. **Type validation rejecting values** — Pydantic working as designed
3. **Auth token expiring** — configuration issue, not a bug
4. **Rate limiting enforced** — feature working correctly
5. **Query parameter constraints** — documented API behavior

**Action**: Before escalating, verify against API documentation whether the behavior is by design.

### Actual Bugs Masquerading as Client Errors

Less common but critical to catch:

1. **500 returned for valid input** — validation bug allowing invalid state
2. **422 for valid input** — overly strict validation
3. **Incorrect error message** — misleading the customer about the actual problem
4. **Error in background processing** — request returns 200 but operation fails silently

## Error Response Format

All API errors follow this structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "field": "optional_field_name",
  "context": {}
}
```

For validation errors (422), the format includes field-level details:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Support Response Guidelines

### When Customer Reports an Error

1. **Request full context**: HTTP method, endpoint, request body, response body, headers
2. **Check status code accuracy**: Confirm what code was actually returned
3. **Reproduce if possible**: Use internal tools to replicate the request
4. **Check logs**: Correlate request ID with backend logs

### When Error Is a Bug

1. Document reproduction steps precisely
2. Note customer impact (single customer vs widespread)
3. Record versions: client library, API version, environment
4. Escalate to engineering with priority based on impact

### When Error Is Expected Behavior

1. Explain the behavior with reference to documentation
2. Provide the correct way to achieve the customer's goal
3. If documentation is unclear, file internal ticket to improve docs
4. Close ticket as resolved with explanation

## Known Problematic Patterns

Based on historical ticket analysis:

### Async Operations and Error Visibility

- Errors in background tasks may not surface to the client
- StreamingResponse handlers may fail after headers are sent
- Long-running operations may timeout without clear error

### Middleware Interference

- Custom middleware can swallow or transform errors
- Error handling middleware must be ordered correctly
- Multiple middleware layers can obscure original error

### Serialization Edge Cases

- Non-UTF8 bytes in response body cause encoding errors
- Large response bodies may trigger timeout errors
- JSON serialization of complex types may fail

## Escalation Criteria

Escalate to engineering immediately if:

- 5xx errors affecting multiple customers
- 5xx errors on critical endpoints (auth, payments)
- Error logs indicate data corruption
- Error pattern is new and increasing
- Customer reports data loss

Do not escalate if:

- 4xx error with clear cause
- Known issue with documented workaround
- Single occurrence with no reproduction case
- Customer configuration error

## AI Agent Guidance

When processing error-related tickets:

1. Extract the actual HTTP status code from the ticket
2. Distinguish between customer-reported status and actual status
3. Check if error matches known patterns in this document
4. Recommend information gathering if context is incomplete
5. Flag for human review if error indicates potential data loss
