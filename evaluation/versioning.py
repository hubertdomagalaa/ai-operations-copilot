"""
Version Tracking for Evaluation
===============================

Tracks versions of code, models, prompts, and datasets for reproducibility.

!!! WARNING !!!
This is INFRASTRUCTURE ONLY.
No real version tracking is happening yet.
This file defines HOW versions will be tracked.

WHY THIS FILE EXISTS:
- Reproducibility is critical for AI evaluation
- Need to know which model/prompt/code produced results
- Enables comparison across versions
- Supports regression detection

VERSION TYPES TRACKED:
1. code_version — Git commit hash
2. model_version — LLM model identifier
3. prompt_version — Hash of prompt templates
4. dataset_version — Dataset identifier

WHAT IS INTENTIONALLY MISSING:
- Automatic version detection
- Version comparison logic
- Regression detection
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VersionInfo:
    """
    Version information for a single evaluation run.
    
    This captures the state of all components when evaluation was run.
    """
    
    # Code version
    code_version: Optional[str] = None
    """Git commit hash. Example: 'abc123def'"""
    
    code_branch: Optional[str] = None
    """Git branch. Example: 'main'"""
    
    code_dirty: Optional[bool] = None
    """True if there are uncommitted changes"""
    
    # Model version
    model_provider: Optional[str] = None
    """LLM provider. Example: 'openai'"""
    
    model_name: Optional[str] = None
    """Model identifier. Example: 'gpt-4-0125-preview'"""
    
    model_version: Optional[str] = None
    """Full version string if available"""
    
    # Prompt version
    prompt_version: Optional[str] = None
    """Hash of prompt templates used"""
    
    prompt_templates: Optional[Dict[str, str]] = None
    """Map of template names to their hashes"""
    
    # Dataset version
    dataset_id: Optional[str] = None
    """Dataset identifier"""
    
    dataset_version: Optional[str] = None
    """Dataset version or creation date"""
    
    # Capture timestamp
    captured_at: Optional[str] = None


def capture_version_info() -> VersionInfo:
    """
    Capture current version information.
    
    Should be called at the start of each evaluation run.
    
    TODO: Implement real version capture
    
    Returns:
        VersionInfo with current versions
    """
    info = VersionInfo(captured_at=datetime.utcnow().isoformat())
    
    # TODO: Get git commit hash
    # try:
    #     import subprocess
    #     result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True)
    #     info.code_version = result.stdout.decode().strip()
    # except Exception:
    #     pass
    
    # TODO: Get git branch
    # TODO: Check for uncommitted changes
    # TODO: Get model version from config
    # TODO: Hash prompt templates
    
    return info


def get_code_version() -> Optional[str]:
    """
    Get the current git commit hash.
    
    TODO: Implement git integration
    """
    # TODO: Run 'git rev-parse HEAD'
    return None


def get_model_version() -> Optional[str]:
    """
    Get the current LLM model version from config.
    
    TODO: Read from environment/config
    """
    # TODO: Read OPENAI_MODEL or similar from config
    return None


def hash_prompt_templates() -> Dict[str, str]:
    """
    Hash all prompt templates for version tracking.
    
    TODO: Implement prompt template discovery and hashing
    """
    # TODO: Find all prompt templates
    # TODO: Compute hash for each
    return {}


def versions_match(a: VersionInfo, b: VersionInfo) -> bool:
    """
    Check if two version infos represent the same configuration.
    
    Used to detect if results are comparable.
    
    TODO: Implement comparison logic
    """
    # TODO: Compare code versions
    # TODO: Compare model versions
    # TODO: Compare prompt versions
    return False


def format_version_string(info: VersionInfo) -> str:
    """
    Format version info as a human-readable string.
    """
    parts = []
    
    if info.code_version:
        parts.append(f"code:{info.code_version[:7]}")
    
    if info.model_name:
        parts.append(f"model:{info.model_name}")
    
    if info.prompt_version:
        parts.append(f"prompts:{info.prompt_version[:7]}")
    
    if info.dataset_version:
        parts.append(f"data:{info.dataset_version}")
    
    return " | ".join(parts) if parts else "versions not tracked"
