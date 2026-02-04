"""
CRM integration stubs for MPART grant system.

Placeholder for future CRM connectors (Salesforce, HubSpot, etc.).
"""

import logging
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class CRMIntegration:
    """Stub CRM integration class."""

    def __init__(self, provider: str = "stub"):
        self.provider = provider

    def push_matches(self, matches: List[Dict[str, Any]]) -> bool:
        """Placeholder for pushing matches to a CRM."""
        logger.info("CRM integration not configured. Skipping push.")
        return False
