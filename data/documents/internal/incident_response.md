# Incident Response Guide

This document defines procedures for detecting, managing, communicating, and learning from production incidents. It applies to all engineering and support personnel involved in incident response.

---

## What Qualifies as an Incident

### Incident Criteria

An incident is declared when ANY of the following occur:

| Threshold | Description |
|-----------|-------------|
| Availability | Error rate >5% for any critical endpoint for >5 minutes |
| Latency | P95 latency >3x baseline for >5 minutes |
| Data | Any suspected data corruption or unauthorized access |
| Security | Active exploit or vulnerability disclosure affecting us |
| Dependency | Critical upstream service (database, auth provider) down |
| Customer Impact | Multiple enterprise customers report same issue simultaneously |

### What Is NOT an Incident

- Single customer experiencing issues due to their configuration
- Sporadic 500 errors without pattern (<0.1% of requests)
- Known issues with documented workarounds
- Planned maintenance (unless it exceeds window)
- Performance degradation within acceptable bounds

### Incident Severity Levels

| Level | Name | Criteria | Example |
|-------|------|----------|---------|
| SEV1 | Critical | Complete outage or data breach | All API requests failing, auth system compromised |
| SEV2 | Major | Significant functionality impaired | One critical endpoint down, >10% error rate |
| SEV3 | Minor | Limited impact with workaround | Non-critical feature degraded, specific edge case |

---

## Incident Lifecycle

```
Detection → Declaration → Response → Resolution → Post-Incident
```

### 1. Detection

Incidents are detected through:

- **Automated monitoring**: PagerDuty alerts on error rate, latency, availability
- **Customer reports**: Multiple tickets with same pattern within 30 minutes
- **Internal discovery**: Engineer notices issue during deployment or testing
- **External notification**: Security researcher, vendor, or partner report

**Response time by detection source:**
- Automated alert: Acknowledge within 5 minutes
- Customer reports: Correlate within 15 minutes
- Internal discovery: Declare immediately if criteria met

### 2. Declaration

**Who can declare an incident:**
- Any on-call engineer
- Any support lead
- Any engineering manager

**Declaration checklist:**
1. Confirm incident criteria are met
2. Assign initial severity level
3. Create incident channel: `#incident-YYYY-MM-DD-brief-name`
4. Page on-call if not already engaged
5. Post initial status to status page
6. Notify stakeholders via `@incident-notify` Slack group

**Declaration message template:**
```
INCIDENT DECLARED - SEV[X]
Issue: [Brief description]
Impact: [What's broken, who's affected]
Detection: [How we found out]
Current status: [Investigation/Mitigation/etc.]
Incident commander: [@name]
```

### 3. Response

#### Roles During Incident

| Role | Responsibility |
|------|----------------|
| Incident Commander (IC) | Owns resolution, coordinates efforts, makes decisions |
| Technical Lead | Drives investigation and implementation of fixes |
| Communications Lead | Updates status page, stakeholders, and customers |
| Scribe | Documents timeline, decisions, and actions in incident channel |

**For SEV3**: IC may handle all roles
**For SEV2**: Minimum IC + Technical Lead
**For SEV1**: All roles should be filled

#### Response Priorities

1. **Mitigate** - Stop the bleeding (rollback, disable feature, scale up)
2. **Communicate** - Keep stakeholders informed
3. **Investigate** - Find root cause
4. **Fix** - Implement proper solution
5. **Verify** - Confirm resolution

**Do NOT:**
- Skip mitigation to find root cause
- Make changes without documenting
- Go dark on communication
- Blame individuals

#### Decision Framework

When deciding between options:

| Factor | Consideration |
|--------|---------------|
| Speed | Which option restores service fastest? |
| Risk | What could go wrong with each option? |
| Reversibility | Can we undo this if it doesn't work? |
| Data | Are we risking data loss or corruption? |

**When in doubt**: Choose the safest reversible option that stops customer impact.

### 4. Resolution

**Resolution is declared when:**
- Service metrics return to normal thresholds
- Customer-impacting symptoms have stopped
- No new error reports for 15 minutes (SEV1/2) or 30 minutes (SEV3)

**Resolution checklist:**
1. Confirm metrics are stable
2. Communicate resolution to stakeholders
3. Update status page to "Resolved"
4. Close incident channel (archive after 24h)
5. Schedule post-incident review

**Resolution message template:**
```
INCIDENT RESOLVED - SEV[X]
Duration: [Start time] to [End time] ([total minutes])
Root cause: [Brief description]
Fix applied: [What we did]
Customer impact: [Scope of impact]
Follow-up: [Any remaining work, post-incident scheduled for X]
```

### 5. Post-Incident

Required for all SEV1 and SEV2 incidents. Optional for SEV3.

**Timeline:**
- Post-incident review: Within 3 business days
- Post-incident document: Within 5 business days
- Action items tracked: Until completion

---

## Communication Guidelines

### Internal Communication

**Frequency by severity:**
- SEV1: Every 15 minutes minimum
- SEV2: Every 30 minutes minimum
- SEV3: Every hour or at significant changes

**Update template:**
```
[TIME] Update #[N]
Status: [Investigating/Identified/Mitigating/Resolved]
What we know: [Current understanding]
What we're doing: [Current action]
Next update: [Time]
```

**Stakeholders to notify:**

| Severity | Notify |
|----------|--------|
| SEV1 | All engineering, support, leadership, customer success |
| SEV2 | On-call team, support lead, affected team lead |
| SEV3 | On-call team, relevant squad |

### External Communication

**Status page updates:**
- First update: Within 10 minutes of declaration
- Subsequent updates: Match internal frequency
- Final update: When resolved, with summary

**Customer communication:**
- Enterprise customers: Direct email for SEV1/2 affecting them
- All customers: Status page for any SEV1
- Specific customers: Direct outreach if we know impact scope

**What to communicate externally:**
- That we are aware of the issue
- What functionality is affected
- Workarounds if available
- Expected time to next update

**What NOT to communicate externally:**
- Technical implementation details
- Blame or speculation
- Specific fix timelines until confident
- Internal URLs or system names

---

## Common Incident Scenarios

### Scenario: Error Rate Spike

**Symptoms:** 
- 5xx error rate increases suddenly
- PagerDuty alert fires

**Immediate actions:**
1. Check recent deployments (last 2 hours)
2. Check dependency status (database, external APIs)
3. Check for traffic anomaly (DDoS, traffic spike)
4. Review error logs for pattern

**Common causes:**
- Bad deployment (rollback candidate)
- Database connection exhaustion
- Upstream service failure
- Rate limiting misconfiguration

### Scenario: Authentication Failures

**Symptoms:**
- 401/403 spike
- Customer reports of login failures

**Immediate actions:**
1. Check auth service health
2. Verify token validation is functioning
3. Check for recent auth config changes
4. Verify API key store is accessible

**Common causes:**
- Token signing key rotation issue
- Cache invalidation problem
- Auth service overloaded
- DNS issue affecting auth endpoints

### Scenario: Performance Degradation

**Symptoms:**
- P95 latency increasing
- Timeouts reported by customers

**Immediate actions:**
1. Check database query performance
2. Check for connection pool exhaustion
3. Review recent code changes for N+1 queries
4. Check for resource contention (CPU, memory)

**Common causes:**
- Slow database query introduced
- Missing index on new query pattern
- Memory leak causing GC pressure
- Background task consuming resources

### Scenario: Dependency Failure

**Symptoms:**
- Specific functionality broken
- 502/503 errors
- Timeouts on specific operations

**Immediate actions:**
1. Identify affected dependency
2. Check dependency status page
3. Verify circuit breaker status
4. Assess impact scope

**Common causes:**
- Third-party service outage
- Network connectivity issue
- Certificate expiration
- Rate limiting by dependency

---

## Runbooks for Specific Systems

### API Gateway

**Health check:** `GET /health` returns 200
**Metrics:** Check `api_gateway_error_rate` and `api_gateway_latency_p95`
**Restart procedure:** Rolling restart via deployment pipeline
**Rollback:** Revert to previous container image tag

### Database

**Health check:** Connection test via monitoring endpoint
**Metrics:** Check `db_connection_pool_utilization` and `db_query_latency_p95`
**Emergency:** Failover to read replica (requires IC approval)
**Restart procedure:** Coordinate with DBA on-call

### Background Workers

**Health check:** Queue depth and worker count
**Metrics:** Check `queue_depth` and `job_failure_rate`
**Restart procedure:** Scale down and up via orchestration platform
**Emergency:** Pause job processing if corrupting data

---

## On-Call Responsibilities

### Before Incident

- Ensure PagerDuty profile is current
- Have laptop and internet access available
- Know how to access runbooks and dashboards
- Be familiar with recent deployments

### During Incident

- Acknowledge pages within 5 minutes
- Declare incident if criteria met
- Assume IC role until handed off
- Follow escalation path if unable to resolve

### After Incident

- Participate in post-incident review
- Complete assigned action items
- Update runbooks if gaps found
- Hand off context at shift change

### Escalation Path

```
On-call Engineer (5 min)
    ↓
On-call Lead (15 min)
    ↓
Engineering Manager (30 min)
    ↓
VP Engineering (SEV1 only)
```

---

## Post-Incident Review Process

### Goals

- Understand what happened and why
- Identify improvements to prevent recurrence
- Share learnings across team
- NO blame, only learning

### Format

**Duration:** 30-60 minutes
**Attendees:** IC, Technical Lead, relevant engineers, support if involved
**Facilitator:** Rotating, not someone involved in incident

### Agenda

1. **Timeline reconstruction** (10 min)
2. **Root cause analysis** (15 min)
3. **What went well** (5 min)
4. **What could be improved** (10 min)
5. **Action items** (10 min)

### Post-Incident Document

Required sections:

```markdown
# Incident Report: [Brief Title]

## Summary
[1-2 sentence summary]

## Impact
- Duration: [time]
- Customers affected: [count/scope]
- Errors generated: [count]
- Revenue impact: [if applicable]

## Timeline
[Detailed timeline with timestamps]

## Root Cause
[Technical explanation]

## Resolution
[What we did to fix it]

## Lessons Learned
- What went well
- What could be improved

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
```

---

## Tools and Access

### Required Access for On-Call

- PagerDuty account with on-call rotation
- Slack with access to incident channels
- Dashboard access (Grafana, Datadog, etc.)
- Production read-only access
- Deployment pipeline access
- Status page admin access

### Key Dashboards

| Dashboard | Purpose |
|-----------|---------|
| API Overview | Error rates, latency, throughput |
| Database Health | Connections, query performance |
| Dependencies | External service status |
| Recent Deployments | What shipped recently |

### Communication Channels

| Channel | Purpose |
|---------|---------|
| #incidents | Active incident coordination |
| #support-escalations | Support team escalations |
| #deployments | Deployment notifications |
| #oncall-handoff | Shift change notes |

---

## Metrics and Thresholds

### Alerting Thresholds

| Metric | Warning | Critical (Page) |
|--------|---------|-----------------|
| Error rate | >1% | >5% |
| P95 latency | >2x baseline | >3x baseline |
| Availability | <99.5% | <99% |
| Database connections | >70% pool | >90% pool |

### SLOs

| Service | Target | Measurement Window |
|---------|--------|-------------------|
| API Availability | 99.9% | Monthly |
| API Latency P95 | <500ms | Weekly |
| Error Rate | <0.1% | Daily |

---

## Quarterly Review

Every quarter, review:

1. Incident count by severity
2. Mean time to detect (MTTD)
3. Mean time to resolve (MTTR)
4. Repeat incidents (same root cause)
5. Action item completion rate
6. On-call burden distribution

Use findings to improve processes and tooling.
