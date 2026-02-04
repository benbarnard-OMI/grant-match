"""
REST API for MPART grant system.

Provides programmatic access to matches, decisions, and analytics.
"""

from .server import create_api
from .routes import api_routes

__all__ = ['create_api', 'api_routes']
