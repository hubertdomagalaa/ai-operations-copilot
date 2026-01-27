# Error Handling Guide

This document defines how the platform interprets, classifies, and responds to HTTP errors. It is intended for support engineers, backend engineers, and AI agents processing support tickets.

---

## HTTP Status Code Philosophy

### 4xx Client Errors

Client errors indicate the caller made a mistake. The platform is functioning correctly; the request is malformed or unauthorized.

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Malformed JSON, invalid content-type, unparseable body |
| 401 | Unauthorized | Missing or expired token, invalid API key |
| 403 | Forbidden | Valid credentials but insufficient permissions for resource |
| 404 | Not Found | Resource does not exist or caller lacks visibility |
| 409 | Conflict | Resource state conflict (email already exists, cannot delete active resource) |
| 422 | Unprocessable Entity | Valid JSON but failed Pydantic validation |
| 429 | Too Many Requests | Rate limit exceeded |

**Key distinction**: 401 means "we don't know who you are"; 403 means "we know who you are but you can't do this."

**Important**: A 404 may be returned when a resource exists but the caller lacks visibility. This is intentional—we do not leak existence information.

### 5xx Server Errors

Server errors indicate the platform failed to process a valid request. These are always our responsibility.

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 500 | Internal Server Error | Unhandled exception, bug in application code |
| 502 | Bad Gateway | Upstream service failure (database, external API) |
| 503 | Service Unavailable | Overload, maintenance, dependency down |
| 504 | Gateway Timeout | Upstream service did not respond in time |

---

## Error Classification Guidelines

### When 500 Is a Bug vs. Expected Behavior

**It is a bug if:**
- A validation error returns 500 instead of 422
  - Common with `condecimal` constraint violations
  - Occurs when `allow_inf_nan=False` is set but inf/nan values reach the handler
  - Happens with complex type hints like `Annotated` with `AfterValidator`
- The traceback shows `TypeError` or `AttributeError` in application code
- The error occurs during normal request processing, not cleanup
- Pydantic validation should have caught the input but did not
- The error message contains `UnboundLocalError` in OpenAPI generation
- Customer receives inconsistent behavior between sync and async code paths

**It is expected behavior if:**
- The error occurs during dependency cleanup after response was already sent (return code was already 200)
- The error is a `RuntimeError` from ASGI message timing during client disconnect
- Logs show "No response returned" but the client received a valid response
- Error is `EndOfStream` from AnyIO during client disconnect
- Error appears in logs as part of GraphQL integration noise with starlette-graphene3

### When 422 Is Correct vs. Misclassified

**Correct 422:**
- Request body fails Pydantic model validation
- Query/path parameters fail type coercion
- Required field is missing
- Field value exceeds constraints (max_length, gt, lt, etc.)

**Misclassified as 422 (actually a bug):**
- Customer reports 422 but the payload matches documented schema
- 422 returned for valid enum values due to case sensitivity not documented
- 422 returned because server state is inconsistent (e.g., referencing deleted resource)
- Empty body returns 422 when all model fields are optional (should accept empty body)

**Misclassified as something else (should be 422):**
- 500 returned when validation constraint is violated (e.g., `condecimal`, `AfterValidator`)
- 200 returned when validator raises `ValueError` but is silently ignored

---

## Common Customer Misclassifications

The following patterns appear frequently in support tickets where customers report issues that are not bugs:

### "500 error on my request"

**Questions to ask:**
1. Is this reproducible with the same request?
2. What is the exact timestamp? (Check for deployment or incident windows)
3. Is this a sporadic 500 or consistent for this payload?
4. What OS is the customer running? (Some issues are Windows-specific)

**Resolution path:**
- If sporadic and not reproducible: likely transient infrastructure issue, close with explanation
- If consistent: request full payload and check validation edge cases
- If Windows + async subprocess: check for event loop compatibility issues

### "API returning wrong status code"

**Common causes:**
- Customer expects 200 but receives 201 for POST (correct behavior)
- Customer expects 404 but receives 403 (correct; resource exists but not visible)
- Customer expects 422 but receives 400 (malformed JSON before validation)
- Customer expects 500 to include full traceback (tracebacks are suppressed in production)

### "Getting 401 intermittently"

**Check first:**
1. Token expiration timing
2. Clock skew on customer's servers
3. Multiple API keys with different permissions in rotation
4. Copy-paste errors with whitespace in API key

### "Request works from curl but not from my application"

**Check first:**
1. HTTP client header configuration
2. Content-Type header presence and correctness
3. API key encoding issues in different HTTP clients
4. Framework-specific header handling

### "DELETE returns 204 but logs show errors"

**This is known behavior.** When returning 204 No Content:
- The response is sent to the client successfully
- Logs may show `RuntimeError: Response content longer than Content-Length`
- This is a uvicorn/Starlette interaction, not customer-impacting
- Do not escalate unless customer reports actual failed deletions

---

## Error Response Structure

All errors return a consistent JSON structure:

```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "field": "optional_field_name"
}
```

For validation errors (422), the structure is:

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

---

## Known Error Handling Edge Cases

Based on historical ticket patterns:

### Validation Errors That Surface as 500

1. **condecimal constraint violations**: Pydantic raises `ValidationError` but FastAPI may not catch it correctly in older versions. Check FastAPI version.

2. **allow_inf_nan=False on Query parameters**: Constraint not enforced, inf/nan values reach handler and cause assertion errors. This is a known limitation.

3. **JSONResponse as return type hint**: Causes `FastAPIError` at decoration time in some versions (notably 0.89.0), not at request time. Platform-specific (works on Windows, fails on Linux in some cases).

4. **Annotated with AfterValidator**: In FastAPI 0.115.10, validators raising `ValueError` may be silently ignored, returning 200 instead of 422. Fixed in later versions.

### Errors During Dependency Cleanup

Yield dependencies that fail during cleanup may log errors after response is sent:

- Response code will be 200 (already sent to client)
- Error appears in logs as 500 but client sees success
- Sync vs async yield dependencies have different traceback behavior
- When dependency is declared on `APIRouter` vs path function, scope interpretation differs

**Support guidance**: If customer reports seeing 200 but logs show 500, this is cleanup-phase error. Not customer-impacting but should be investigated if frequent.

### Client Disconnect Errors

When clients disconnect mid-request:

- "No response returned" `RuntimeError` may spam logs
- AnyIO `EndOfStream` propagates as `RuntimeError`
- This is noisy but not indicative of a bug
- Occurs more frequently with db session middleware + exception handler middleware combinations

**Do not escalate** client disconnect log spam unless volume is unusually high (>1% of requests).

### UploadFile Lifecycle Issues

In FastAPI 0.106.0+:
- `UploadFile` objects may be closed before `StreamingResponse` generator executes
- Workaround: copy file contents before returning streaming response
- Pin to 0.105.0 if streaming upload handling is critical

### Form Handling Regressions

In FastAPI 0.115.x:
- Default values broken for `x-form-urlencoded` and multipart forms
- Empty string submitted returns `''` instead of `None` default
- Regression from PRs #12134 and #12117
- Workaround: explicit None coercion in handler or pin to 0.112.4

### OpenAPI Generation Failures

- FastAPI 0.99.0: `extra='forbid'` on Pydantic models breaks OpenAPI generation
  - Error: `additionalProperties value is not a valid dict`
  - Workaround: remove `extra='forbid'` or upgrade
- Status code parameter issues: `UnboundLocalError` when `status_code_param.default` is not an integer

---

## Environment-Specific Issues

### Windows

- `asyncio.create_subprocess_exec` raises `NotImplementedError` under uvicorn
- Root cause: Windows `SelectorEventLoop` does not support subprocess
- Workaround: use synchronous subprocess or configure `ProactorEventLoop`
- This is a platform limitation, not a bug

### Python 3.11+

- Sync yield dependency tracebacks may be incomplete
- Error location not shown in traceback for sync context managers
- Async versions work correctly

---

## Middleware-Related Errors

### GZipMiddleware + StreamingResponse

- GZipMiddleware does not compress StreamingResponse
- Works correctly with FileResponse
- Known limitation, not a bug

### Background Tasks + Middleware

- Long-running `async sleep` in BackgroundTasks can block subsequent requests when middleware is present
- Workaround: use threaded background tasks or reduce async sleep duration
- Known interaction pattern

### Timeout Middleware

- Some implementations require double `@app.middleware` decoration to function
- Verify middleware registration pattern if timeouts not triggering

---

## Support Response Templates

### For Customer Reporting Sporadic 500

> Thank you for reporting this. Sporadic 500 errors can occur during transient infrastructure events. Could you please provide:
> 1. The exact timestamp of the error (with timezone)
> 2. The request ID if available in response headers
> 3. Whether this is still occurring
>
> If this was a one-time occurrence and is no longer happening, it was likely a transient issue that has resolved.

### For Customer Reporting 422 Validation Error

> The 422 status code indicates your request body did not pass validation. The response body contains details about which field failed validation and why.
>
> Please check:
> 1. All required fields are present
> 2. Field types match the documented schema
> 3. Field values are within documented constraints
> 4. If sending empty body, ensure it is `{}` not an empty string
>
> If you believe your request matches the documented schema exactly, please share the full request body (with sensitive data redacted) and we will investigate.

### For Customer Reporting 401/403

> For 401 (Unauthorized): Please verify your API key is correctly included in the `X-API-Key` header and has not expired. Check for extra whitespace that may have been introduced during copy-paste.
>
> For 403 (Forbidden): Your credentials are valid but lack permission for this operation. Please verify your API key has the required scopes for this endpoint in the dashboard.

### For Customer Reporting Log Errors Despite Successful Response

> If your client is receiving successful responses (200, 201, 204) but you're seeing errors in logs, this typically indicates a post-response cleanup issue rather than a customer-impacting bug. The response was delivered successfully.
>
> We monitor these patterns internally. If you're seeing a high volume of such log entries, please let us know the timeframe and we can investigate further.

---

## Escalation Criteria

**Escalate to engineering if:**
- Consistent 500 errors reproducible with specific payload
- Error message contains stack trace referencing application code (not validation)
- Multiple customers report same error pattern
- Error occurs on an endpoint that was recently deployed
- Validation returning 200 instead of 422 (silent validator failures)
- OpenAPI/docs endpoint returning 500

**Do not escalate:**
- Client disconnect log noise
- Sporadic non-reproducible 500s
- 4xx errors where customer payload does not match schema
- Expected cleanup-phase errors
- Known version-specific issues with documented workarounds
- DELETE 204 log errors when customer confirms success

---

## Version-Specific Notes

Some errors are version-specific. Always capture:

- FastAPI version
- Pydantic version  
- Python version
- Uvicorn version (if applicable)
- Operating system (especially for async issues)

Known version-specific issues:

| Versions | Issue |
|----------|-------|
| FastAPI 0.89.0 | JSONResponse type hint causes FastAPIError |
| FastAPI 0.99.0 | OpenAPI schema generation fails with extra='forbid' |
| FastAPI 0.106.0+ | UploadFile closed before StreamingResponse executes |
| FastAPI 0.115.10 | AfterValidator with Annotated silently ignored |
| FastAPI 0.115.x | Form field default value regressions |
| FastAPI + Python 3.11 | Sync yield dependency traceback issues |
| FastAPI + Windows | Async subprocess NotImplementedError |
| TestClient + httpx | 'extensions' argument TypeError in PUT methods |

---

## AI Agent Guidance

When processing tickets about errors:

1. **Extract status code** from ticket text
2. **Identify if reproducible** from customer description
3. **Check for version mentions** and cross-reference known issues
4. **Check for environment** (Windows, specific Python version)
5. **Classify as**:
   - Customer error (4xx, payload issue)
   - Known issue (see known_issues.md)
   - Potential bug (consistent 500, needs engineering)
   - Transient (sporadic, non-reproducible)
   - Environment-specific (Windows subprocess, Python 3.11 tracebacks)

Do not recommend escalation for:
- 4xx errors without evidence of platform bug
- Sporadic errors without reproduction steps
- Known version-specific issues with documented workarounds
- Log errors where customer confirms successful response delivery

**Priority signals for escalation:**
- Customer provides reproducible code example
- Multiple tickets with same error signature
- Recent deployment correlation
- Security-related errors (auth bypass, data leakage)
- Silent failures (200 returned when error expected)
