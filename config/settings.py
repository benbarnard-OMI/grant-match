"""
Configuration settings management.

Supports environment variables, config files, and admin UI.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field


logger = logging.getLogger(__name__)


@dataclass
class KeywordWeights:
    """Keyword weight configuration."""
    medicaid: int = 35
    policy_monitoring: int = 25
    regulatory_analysis: int = 25
    rural_health: int = 15
    health_services_research: int = 30
    health_policy: int = 30
    health_equity: int = 20
    state_policy: int = 25
    
    def to_dict(self):
        return asdict(self)


@dataclass
class NotificationSettings:
    """Notification configuration."""
    enabled: bool = True
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_address: str = "mpart-grants@uis.edu"
    to_addresses: List[str] = field(default_factory=list)
    daily_digest: bool = True
    immediate_alerts: bool = False
    alert_threshold: int = 95


@dataclass
class SourceSettings:
    """Data source configuration."""
    illinois_gata: bool = True
    sam_gov: bool = True
    rwjf: bool = False
    commonwealth_fund: bool = False
    academy_health: bool = False
    shadac: bool = False
    cms_innovation: bool = False
    hrsa: bool = False


@dataclass
class Settings:
    """Complete application settings."""
    organization: str = "MPART @ UIS"
    keywords: KeywordWeights = field(default_factory=KeywordWeights)
    notifications: NotificationSettings = field(default_factory=NotificationSettings)
    sources: SourceSettings = field(default_factory=SourceSettings)
    high_priority_threshold: int = 80
    deep_research_threshold: int = 50
    auto_export: bool = False
    export_format: str = "json"
    
    @classmethod
    def from_file(cls, filepath: str = "config/settings.json") -> 'Settings':
        """Load settings from JSON file."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            # Create default settings file
            settings = cls()
            settings.save(filepath)
            return settings
        
        with open(filepath) as f:
            data = json.load(f)
        
        return cls(
            organization=data.get('organization', 'MPART @ UIS'),
            keywords=KeywordWeights(**data.get('keywords', {})),
            notifications=NotificationSettings(**data.get('notifications', {})),
            sources=SourceSettings(**data.get('sources', {})),
            high_priority_threshold=data.get('high_priority_threshold', 80),
            deep_research_threshold=data.get('deep_research_threshold', 50),
            auto_export=data.get('auto_export', False),
            export_format=data.get('export_format', 'json')
        )
    
    def save(self, filepath: str = "config/settings.json"):
        """Save settings to JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)
        
        logger.info(f"Settings saved to {filepath}")
    
    def update_keywords(self, **kwargs):
        """Update keyword weights."""
        for key, value in kwargs.items():
            if hasattr(self.keywords, key):
                setattr(self.keywords, key, value)
        self.save()
    
    def update_sources(self, **kwargs):
        """Update source settings."""
        for key, value in kwargs.items():
            if hasattr(self.sources, key):
                setattr(self.sources, key, value)
        self.save()


def load_settings() -> Settings:
    """Load settings from file or environment."""
    # First check for settings file
    if Path("config/settings.json").exists():
        return Settings.from_file()
    
    # Otherwise create from environment variables
    settings = Settings()
    
    # Override with env vars if present
    settings.notifications.smtp_host = os.getenv('SMTP_HOST', settings.notifications.smtp_host)
    settings.notifications.smtp_port = int(os.getenv('SMTP_PORT', settings.notifications.smtp_port))
    settings.notifications.smtp_username = os.getenv('SMTP_USERNAME', '')
    settings.notifications.smtp_password = os.getenv('SMTP_PASSWORD', '')
    settings.notifications.from_address = os.getenv('FROM_ADDRESS', settings.notifications.from_address)
    
    if os.getenv('TO_ADDRESSES'):
        settings.notifications.to_addresses = os.getenv('TO_ADDRESSES').split(',')
    
    return settings


if __name__ == '__main__':
    # Test settings
    settings = load_settings()
    print("Current settings:")
    print(json.dumps(asdict(settings), indent=2))
