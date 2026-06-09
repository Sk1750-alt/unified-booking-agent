"""
Configuration settings for the Unified Booking Agent.

This module centralizes all configuration options for easy management
and environment-specific customization.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

APP_NAME = "Unified Booking Agent"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "MCP-Powered Multi-Platform Accommodation Search"

# =============================================================================
# SERVER SETTINGS
# =============================================================================

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# =============================================================================
# API SETTINGS
# =============================================================================

# RapidAPI Configuration (for Booking.com integration)
RAPIDAPI_KEY: Optional[str] = os.getenv("RAPIDAPI_KEY", None)
RAPIDAPI_HOST = "booking-com15.p.rapidapi.com"

# Gemini API Key (for LLM-powered chatbot)
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)


# API Timeout Settings (in seconds)
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 10))

# =============================================================================
# DATA SETTINGS
# =============================================================================

# Path to mock data files
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
MOCK_LISTINGS_FILE = os.path.join(DATA_DIR, "mock_listings.json")

# =============================================================================
# CURRENCY SETTINGS
# =============================================================================

DEFAULT_CURRENCY = "INR"
CURRENCY_SYMBOL = "Rs."

# =============================================================================
# SELECTION STRATEGIES
# =============================================================================

AVAILABLE_STRATEGIES = [
    "cheapest",
    "highest_rating", 
    "best_value",
    "flexible_cancellation"
]

DEFAULT_STRATEGY = "best_value"

# =============================================================================
# PLATFORM SETTINGS
# =============================================================================

# Enabled platforms for search
ENABLED_PLATFORMS = [
    "MockAirbnb",
    "MockBooking",
    "Booking.com"  # Real API integration
]

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
