"""
Metrics Collection
==================

Metrics infrastructure for monitoring and evaluation.

WHY THIS FILE EXISTS:
- Track system performance (latency, throughput)
- Monitor AI quality (confidence, accuracy)
- Enable alerting on anomalies
- Support capacity planning

METRIC TYPES:
- Counter: Cumulative counts (requests, errors)
- Gauge: Point-in-time values (queue depth)
- Histogram: Distributions (latency, confidence)

KEY METRICS:
- Workflow execution time
- Agent-specific latency
- Classification confidence distribution
- Human override rate
- Error rate by agent

TODO: Implement with Prometheus client when ready
"""

from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict


class MetricValue:
    """
    A single metric observation.
    """
    
    def __init__(self, value: float, labels: Dict[str, str] = None):
        self.value = value
        self.labels = labels or {}
        self.timestamp = datetime.utcnow()


class Counter:
    """
    Cumulative counter metric.
    
    Only goes up (or resets to zero).
    """
    
    def __init__(self, name: str, description: str, labels: List[str] = None):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._values: Dict[tuple, float] = defaultdict(float)
    
    def inc(self, value: float = 1, labels: Dict[str, str] = None):
        """Increment the counter."""
        label_key = self._label_key(labels)
        self._values[label_key] += value
    
    def get(self, labels: Dict[str, str] = None) -> float:
        """Get current counter value."""
        label_key = self._label_key(labels)
        return self._values[label_key]
    
    def _label_key(self, labels: Dict[str, str] = None) -> tuple:
        """Convert labels to hashable key."""
        if not labels:
            return ()
        return tuple(sorted(labels.items()))


class Gauge:
    """
    Point-in-time gauge metric.
    
    Can go up or down.
    """
    
    def __init__(self, name: str, description: str, labels: List[str] = None):
        self.name = name
        self.description = description
        self.label_names = labels or []
        self._values: Dict[tuple, float] = defaultdict(float)
    
    def set(self, value: float, labels: Dict[str, str] = None):
        """Set the gauge value."""
        label_key = self._label_key(labels)
        self._values[label_key] = value
    
    def inc(self, value: float = 1, labels: Dict[str, str] = None):
        """Increment the gauge."""
        label_key = self._label_key(labels)
        self._values[label_key] += value
    
    def dec(self, value: float = 1, labels: Dict[str, str] = None):
        """Decrement the gauge."""
        label_key = self._label_key(labels)
        self._values[label_key] -= value
    
    def get(self, labels: Dict[str, str] = None) -> float:
        """Get current gauge value."""
        label_key = self._label_key(labels)
        return self._values[label_key]
    
    def _label_key(self, labels: Dict[str, str] = None) -> tuple:
        if not labels:
            return ()
        return tuple(sorted(labels.items()))


class Histogram:
    """
    Distribution metric with buckets.
    
    Tracks count, sum, and bucket distribution.
    """
    
    DEFAULT_BUCKETS = [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    
    def __init__(
        self,
        name: str,
        description: str,
        buckets: List[float] = None,
        labels: List[str] = None,
    ):
        self.name = name
        self.description = description
        self.buckets = sorted(buckets or self.DEFAULT_BUCKETS)
        self.label_names = labels or []
        self._counts: Dict[tuple, Dict[float, int]] = defaultdict(
            lambda: {b: 0 for b in self.buckets + [float("inf")]}
        )
        self._sums: Dict[tuple, float] = defaultdict(float)
        self._totals: Dict[tuple, int] = defaultdict(int)
    
    def observe(self, value: float, labels: Dict[str, str] = None):
        """Record an observation."""
        label_key = self._label_key(labels)
        self._sums[label_key] += value
        self._totals[label_key] += 1
        
        for bucket in self.buckets + [float("inf")]:
            if value <= bucket:
                self._counts[label_key][bucket] += 1
    
    def _label_key(self, labels: Dict[str, str] = None) -> tuple:
        if not labels:
            return ()
        return tuple(sorted(labels.items()))


# === Pre-defined metrics ===

# Workflow metrics
workflow_duration = Histogram(
    name="workflow_duration_seconds",
    description="Time to complete ticket workflow",
    buckets=[0.5, 1, 2, 5, 10, 30, 60, 120],
    labels=["status"],
)

workflow_total = Counter(
    name="workflow_total",
    description="Total workflows executed",
    labels=["status"],
)

# Agent metrics
agent_duration = Histogram(
    name="agent_duration_seconds",
    description="Time for agent to process",
    buckets=[0.1, 0.5, 1, 2, 5, 10],
    labels=["agent_type"],
)

agent_confidence = Histogram(
    name="agent_confidence",
    description="Confidence scores from agents",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    labels=["agent_type"],
)

# Human-in-the-loop metrics
human_review_required = Counter(
    name="human_review_required_total",
    description="Times human review was required",
    labels=["agent_type", "reason"],
)

human_override_total = Counter(
    name="human_override_total",
    description="Times human overrode AI decision",
    labels=["agent_type"],
)

# Error metrics
agent_errors = Counter(
    name="agent_errors_total",
    description="Agent processing errors",
    labels=["agent_type", "error_type"],
)
