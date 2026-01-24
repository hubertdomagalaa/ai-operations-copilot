# Data Directory — Logs

This directory contains operational logs.

## Purpose
- Store workflow execution logs
- Capture agent inputs and outputs
- Record performance metrics
- Maintain audit trail

## Log Categories
- `workflow/` — Workflow execution traces
- `agents/` — Individual agent logs
- `api/` — API request logs
- `errors/` — Error logs for debugging

## Log Format
Logs should be structured JSON for easy parsing:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "component": "triage_agent",
  "ticket_id": "ticket-123",
  "trace_id": "trace-abc",
  "message": "Classification complete",
  "data": {...}
}
```

## Retention
- Development: Keep all logs
- Production: Rotate after 30 days, archive to cold storage

## Note
In production, use a proper logging infrastructure (ELK, CloudWatch, etc.).
Local files are for development only.
