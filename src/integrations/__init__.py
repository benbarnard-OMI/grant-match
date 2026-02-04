"""
Third-party integrations for MPART grant system.

Includes calendar, CRM, and other integrations.
"""

from .calendar import CalendarIntegration, DeadlineManager
from .crm import CRMIntegration

__all__ = ['CalendarIntegration', 'DeadlineManager', 'CRMIntegration']
