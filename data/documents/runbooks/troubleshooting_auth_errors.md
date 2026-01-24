# Troubleshooting: Authentication Errors

This runbook covers common authentication-related issues and their resolutions.

## Issue: Customers Reporting 401 Errors

### Initial Assessment

1. Ask customer for:
   - Full error message
   - Endpoint they're calling
   - When the issue started
   - Any recent changes on their end

2. Check in dashboard:
   - Is their API key active?
   - Are there recent key rotations?
   - Is there unusual traffic from their key?

### Resolution Steps

#### Scenario: Key was revoked

1. Verify key status in admin dashboard
2. If revoked accidentally, contact billing to check for issues
3. Generate new key for customer
4. Provide secure way to share (encrypted email or dashboard)

#### Scenario: Key was never valid

1. Customer may have copy-pasted incorrectly
2. Ask them to regenerate key in their dashboard
3. Verify correct header format: `X-API-Key: <key>`

#### Scenario: Traffic spike triggered rate limit

1. Check rate limit logs for their key
2. Explain current tier limits
3. Suggest upgrade or request patterns optimization
4. Consider temporary limit increase if justified

### Escalation Criteria

Escalate to Engineering if:
- Multiple customers affected simultaneously
- API key validation service appears down
- Authentication logs show anomalies

## Issue: Intermittent 403 Errors

### Common Causes

1. **IP restriction changes**: Check if customer's IPs changed
2. **Role permission updates**: Verify recent permission changes
3. **Rate limit edge cases**: Near-limit traffic causing sporadic failures

### Resolution

1. Review permission audit logs for the customer
2. Compare current vs. expected permissions
3. If rate limit related, check 429 vs 403 response patterns

## Issue: Authentication Working for Some Endpoints Only

This usually indicates permission issues, not authentication issues.

1. Check which endpoints fail vs. succeed
2. Compare required permissions for each
3. Verify API key has appropriate scope
4. Update permissions as needed

## Metrics to Monitor

- Authentication failure rate by error code
- Failed requests by API key
- Rate limit hits by tier
- Average authentication latency

If authentication latency exceeds 100ms, escalate to Engineering.
