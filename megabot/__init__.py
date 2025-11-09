"""
MEGA-Bot - A unified AI agent integrating multiple platforms with Agent HQ orchestration
"""

__version__ = "2.0.0"
__author__ = "MEGAGENT Team"

from .core import MegaBot
from .config import Config
from .utils import setup_logging, get_logger, validate_query, validate_topic
from .monetization import MonetizationManager, SubscriptionTier
from .advertising import AdvertisingCore, AdPlacement
from .octogen import Octogen, OctogenMode, OctogenCapability
from .agenthq import (
    AgentHQCoordinator, 
    OctopusBrain, 
    LangChainOrchestrator, 
    LangGraphOrchestrator,
    CloudOctopus,
    EnterpriseCloudOctogent
)

__all__ = [
    "MegaBot", "Config", 
    "setup_logging", "get_logger", "validate_query", "validate_topic",
    "MonetizationManager", "SubscriptionTier",
    "AdvertisingCore", "AdPlacement",
    "Octogen", "OctogenMode", "OctogenCapability",
    "AgentHQCoordinator", "OctopusBrain",
    "LangChainOrchestrator", "LangGraphOrchestrator",
    "CloudOctopus", "EnterpriseCloudOctogent"
]
