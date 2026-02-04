"""
Workflow management stubs for MPART grant tracking.

Placeholder for future workflow automation (approvals, task routing).
"""

import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class WorkflowManager:
    """Stub workflow manager."""

    def __init__(self):
        self.enabled = False

    def trigger(self, grant_id: str, action: str, context: Dict[str, Any] | None = None) -> bool:
        """Placeholder for workflow triggers."""
        logger.info("Workflow manager not configured. Skipping trigger.")
        return False
