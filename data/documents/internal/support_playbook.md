# Support Playbook

This document defines the operational procedures for the support team handling tickets related to the REST API platform. It covers triage, classification, escalation, and resolution workflows.

---

## Ticket Triage Process

### Initial Assessment (First 5 Minutes)

When a ticket arrives, perform the following checks:

1. **Is this a duplicate?** Search for similar tickets by:
   - Error message
   - Affected endpoint
   - Customer account
   - Timestamp proximity

2. **Is this during an active incident?** Check:
   - #incidents Slack channel
   - Status page
   - Recent deployment logs

3. **Is this a security issue?** If yes:
   - Tag as `security`
   - Escalate immediately to on-call SRE
   - Do not request additional details via unencrypted channels

4. **Can this be auto-resolved?** Check if:
   - Customer error (malformed request, expired token)
   - Documented known issue with workaround
   - FAQ-answerable question

### Classification Dimensions

Every ticket should be classified on:

| Dimension | Values |
|-----------|--------|
| Category | authentication, validation, performance, integration, documentation, feature_request, other |
| Severity | P1 (critical), P2 (high), P3 (medium), P4 (low) |
| Issue Type | bug, question, configuration, incident |
| Environment | production, staging, development, unknown |

---

## Severity Classification Philosophy

### P1 - Critical

**Definition**: Complete service outage or security breach affecting production.

**Criteria (any of the following):**
- All API requests failing for a customer
- Authentication system completely non-functional
- Data breach or security vulnerability actively exploited
- Financial transactions failing in production

**Response SLA**: 15 minutes to acknowledge, 1 hour to update
**Escalation**: Immediate page to on-call engineering

**Examples:**
- "All our API calls return 500 since 10:00 UTC"
- "We're seeing unauthorized access to customer data"
- "Payment processing is down"

### P2 - High

**Definition**: Major functionality impaired but workaround exists, or significant portion of customers affected.

**Criteria (any of the following):**
- Specific endpoint failing consistently
- Performance degradation >50% from baseline
- Multiple customers reporting same issue within 1 hour
- Authentication failures for subset of valid credentials

**Response SLA**: 1 hour to acknowledge, 4 hours to update
**Escalation**: Notify on-call, escalate if no progress in 2 hours

**Examples:**
- "POST /users returns 500 for payloads with special characters"
- "API latency is 3x normal"
- "Our staging API key works but production key returns 403"

### P3 - Medium

**Definition**: Functionality impaired but does not block core operations.

**Criteria (any of the following):**
- Non-critical endpoint issue
- Documentation unclear or incorrect
- Edge case validation failures
- Performance issue not affecting majority of requests

**Response SLA**: 4 hours to acknowledge, 24 hours to update
**Escalation**: Include in daily engineering standup if unresolved

**Examples:**
- "OpenAPI docs page shows 500 error"
- "Pagination returns inconsistent results for large offsets"
- "Our SDK is getting 422 on valid-looking requests"

### P4 - Low

**Definition**: Minor issue with easy workaround, feature requests, general questions.

**Criteria (any of the following):**
- Feature request
- General usage question
- Documentation improvement suggestion
- Cosmetic issues

**Response SLA**: 24 hours to acknowledge, 72 hours to update
**Escalation**: None unless customer explicitly requests

**Examples:**
- "Can you add support for X in the API?"
- "How do I implement pagination correctly?"
- "The error message could be clearer"

---

## When to Escalate to Engineering

### Always Escalate

- Consistent 500 errors with reproducible steps
- Multiple customers reporting identical error pattern
- Error in recently deployed code (check deployment log)
- Security-related issues (auth bypass, data leakage)
- Performance degradation detected in metrics
- Silent failures (200 returned when error should occur)
- Any P1 or P2 ticket

### Escalate with Discretion

- Edge case validation failures (check known issues first)
- Version-specific bugs (may have documented workaround)
- Integration issues with third-party libraries
- Intermittent issues without clear reproduction steps

### Do Not Escalate (Handle in Support)

- Customer configuration errors
- Expired or invalid API keys
- Malformed request payloads
- Questions answerable from documentation
- Feature requests (log and close or forward to product)
- Known issues with documented workarounds
- Sporadic non-reproducible errors
- Client disconnect log noise
- Expected behavior misunderstood as bug

---

## When to Request More Information

### Always Request

- Error reports without timestamp
- 500 errors without request ID
- "It doesn't work" without specific error message
- Version-related issues without version numbers
- Intermittent issues without frequency/pattern information

### Information Request Template

> Thank you for reporting this issue. To investigate further, we need:
>
> 1. **Timestamp**: Exact date/time of the error (with timezone)
> 2. **Request ID**: From the `X-Request-Id` response header if available
> 3. **Error Response**: Complete error response body
> 4. **Request Details**: Endpoint, method, and sanitized request body
> 5. **Reproducibility**: Is this consistent or intermittent?
>
> [If version-related suspected:]
> 6. **Versions**: FastAPI, Python, and any relevant library versions

### Do Not Request More Information

- When issue is clearly customer configuration error
- When issue matches known issue exactly
- When you can reproduce the issue yourself
- When the ticket contains sufficient detail to act

---

## When to Close as Configuration / Expected Behavior

### Close as Configuration Error

- API key missing or malformed
- Incorrect Content-Type header
- Request body does not match documented schema
- Rate limit exceeded (unless limits seem incorrect)
- Authentication to wrong environment (staging vs production)

**Template:**
> This appears to be a configuration issue rather than a platform bug. [Specific explanation of what's wrong]. Please review our documentation at [link] and try again. If you continue to experience issues after making these changes, please reopen this ticket with the updated request details.

### Close as Expected Behavior

- Status codes that differ from customer expectation but match HTTP spec
  - 201 for POST creates (not 200)
  - 204 for DELETE (not 200)
  - 403 for existing-but-not-visible resources (not 404)
- Validation rejecting invalid data
- Rate limiting working as documented
- Empty body returning 422 when JSON body required

**Template:**
> This is expected behavior based on our API design. [Explanation of why this is correct]. Our documentation at [link] explains this behavior in detail. If you have concerns about this design decision, please let us know and we can discuss alternatives or raise as a feature request.

### Close as Known Issue / Workaround Available

When issue matches a documented known issue:

**Template:**
> This is a known issue with [component/version]. The recommended workaround is [workaround]. We're tracking this issue and will update you when a fix is available. For reference, this is documented in our internal known issues database.

---

## Ticket Categories Deep Dive

### Authentication Tickets

**Common patterns:**
- 401 intermittent: Check token expiration, clock skew, key rotation
- 401 after copy-paste: Whitespace in API key
- 403 unexpected: Role/permission mismatch, IP restrictions
- "Works in curl, not in code": HTTP client header handling

**Resolution path:**
1. Verify API key is active in dashboard
2. Check key permissions match required scopes
3. Request cURL command that fails for debugging
4. Check for recent password/key rotations

### Validation Tickets

**Common patterns:**
- 422 on valid-looking payload: Check enum case sensitivity, field constraints
- 500 instead of 422: Known validation edge cases (condecimal, AfterValidator)
- Empty body rejected: Need `{}` not empty string
- Type coercion failures: Check documented types vs what customer sends

**Resolution path:**
1. Request exact payload
2. Compare against schema
3. Check for version-specific validation bugs
4. Test in staging if reproducible

### Performance Tickets

**Common patterns:**
- "API is slow": Need baseline comparison, specific endpoints
- Timeout on large requests: Check payload size, pagination needs
- Hangs on second request: Background tasks + middleware interaction

**Resolution path:**
1. Get specific endpoint and timing
2. Check recent deployment or traffic changes
3. Review performance dashboards
4. Escalate if sustained degradation >50%

### Integration Tickets

**Common patterns:**
- Third-party library incompatibility
- SDK version mismatch
- Webhook delivery failures
- OAuth flow issues

**Resolution path:**
1. Verify library versions
2. Check our changelog for breaking changes
3. Request integration code if debugging needed
4. Test with our official SDK if available

---

## Response Time Guidelines

| Severity | First Response | Update Frequency | Resolution Target |
|----------|----------------|------------------|-------------------|
| P1 | 15 minutes | Every 30 minutes | 4 hours |
| P2 | 1 hour | Every 2 hours | 8 hours |
| P3 | 4 hours | Daily | 72 hours |
| P4 | 24 hours | As needed | 1 week |

**Note**: Resolution target means issue resolved OR root cause identified with timeline. Some issues require engineering fixes that take longer—communicate timeline clearly to customer.

---

## Handoff Procedures

### To Engineering

Include in escalation:
1. Ticket ID and link
2. Customer account identifier
3. Reproduction steps (if available)
4. Error messages and logs
5. Timestamps of occurrences
6. Number of affected customers
7. Impact assessment
8. What has already been tried

Use `@engineering-oncall` in Slack #support-escalations

### To Product (Feature Requests)

Log feature request with:
1. Customer segment (tier, industry)
2. Use case description
3. Current workaround (if any)
4. Business impact for customer
5. Similar requests count

Forward to product backlog, close ticket with explanation.

### Between Support Shifts

Daily handoff should include:
1. Open P1/P2 tickets and their status
2. Tickets awaiting customer response >24h
3. Any patterns emerging across tickets
4. Active incidents or known issues

---

## Customer Communication Guidelines

### Tone

- Professional but not robotic
- Acknowledge the customer's frustration if they express it
- Avoid blame language ("you did X wrong")
- Be specific about next steps and timelines
- Do not promise fixes without engineering confirmation

### What Not to Say

- "This is a bug in our code" (until confirmed by engineering)
- "This will be fixed by [date]" (without engineering commitment)
- "This is impossible" (check with engineering first)
- "I don't know" (say "I'll investigate" or "I'll escalate")

### What to Always Include

- Ticket reference number
- Clear next steps (for support or customer)
- Timeline for next update
- Link to relevant documentation if applicable
- Request ID if discussing specific request

---

## AI Agent Integration

When the AI Operations Copilot processes a ticket:

### Accept AI Recommendations When

- Classification matches ticket content clearly
- Suggested response addresses customer's question
- Escalation recommendation aligns with criteria above
- Known issue match is exact (version, error, symptoms)

### Override AI Recommendations When

- Classification seems off based on context
- Response is too generic for specific issue
- Customer sentiment suggests higher priority needed
- Pattern recognition suggests emerging incident

### Required Human Review

- All P1 and P2 tickets
- Any escalation to engineering
- Security-related tickets
- Tickets from enterprise customers
- Compensation or refund discussions

---

## Metrics We Track

### Individual Metrics
- First response time
- Resolution time
- Customer satisfaction score
- Escalation rate
- Reopen rate

### Team Metrics
- Ticket volume by category
- Average resolution time by severity
- Escalation rate trends
- Known issues frequency

### Quality Indicators
- Tickets reopened within 7 days (should be <5%)
- Escalations rejected by engineering (should be <10%)
- Customer satisfaction trend
- Documentation gaps identified

---

## Common Mistakes to Avoid

1. **Escalating too quickly**: Check known issues and documentation first
2. **Escalating too slowly**: P1/P2 should not wait for more information
3. **Generic responses**: Be specific to the customer's issue
4. **Closing without confirmation**: Ensure customer agrees issue is resolved
5. **Missing version information**: Always capture versions for bug reports
6. **Not checking incident status**: Don't troubleshoot during active incident
7. **Promising timelines**: Only engineering can commit to fix timelines
8. **Ignoring patterns**: Multiple similar tickets may indicate incident
