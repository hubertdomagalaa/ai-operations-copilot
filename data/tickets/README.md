# Data Directory — Tickets

This directory contains support ticket data.

## Purpose
- Store raw ingested tickets
- Store processed ticket results
- Maintain ticket history for evaluation

## Structure (when implemented)
- `raw/` — Original ticket JSON files
- `processed/` — Tickets with agent outputs
- `archived/` — Old tickets for training/evaluation

## Note
In production, this would be replaced by a database.
Local files are for development and testing only.
