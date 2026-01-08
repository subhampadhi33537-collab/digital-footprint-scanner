import os
from dotenv import load_dotenv  # type: ignore
from pathlib import Path


# ==================================================
# LOAD .env FILE
# ==================================================

# Resolve project root directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env from project root
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)


# ==================================================
# CONFIGURATION CLASS
# ==================================================

class Config:
    """
    Central configuration class for the
    AI-Powered Digital Footprint Scanner.

    All modules must import configuration from here.
    """

    # --------------------------------------------------
    # FLASK CORE SETTINGS
    # --------------------------------------------------
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

    # --------------------------------------------------
    # GOOGLE GEMINI AI SETTINGS
    # --------------------------------------------------
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", 1024))
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", 0.6))

    # --------------------------------------------------
    # FREE EMAIL OSINT / VALIDATION API
    # --------------------------------------------------
    ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY")
    ABSTRACT_API_URL = "https://emailvalidation.abstractapi.com/v1/"

    # --------------------------------------------------
    # OSINT SCAN LIMITS (ETHICAL)
    # --------------------------------------------------
    SCAN_TIMEOUT = int(os.getenv("SCAN_TIMEOUT", 15))
    MAX_PLATFORMS = int(os.getenv("MAX_PLATFORMS", 25))

    # --------------------------------------------------
    # DATA HANDLING & STORAGE
    # --------------------------------------------------
    STORE_SCAN_DATA = os.getenv("STORE_SCAN_DATA", "False").lower() == "true"

    DATA_DIR = BASE_DIR / "data"
    SCAN_DIR = DATA_DIR / "scans"
    TEMP_DIR = DATA_DIR / "temp"

    # --------------------------------------------------
    # SUPPORTED PLATFORM LIST (ETHICAL OSINT)
    # --------------------------------------------------
    SUPPORTED_PLATFORMS = [
        "github",
        "twitter",
        "linkedin",
        "instagram",
        "facebook",
        "reddit",
        "medium",
        "stackoverflow",
        "devto",
        "pinterest"
    ]

    # --------------------------------------------------
    # RISK SCORING THRESHOLDS
    # --------------------------------------------------
    RISK_THRESHOLDS = {
        "LOW": 0,
        "MEDIUM": 40,
        "HIGH": 70
    }

    # --------------------------------------------------
    # VALIDATION ON STARTUP
    # --------------------------------------------------
    @classmethod
    def validate(cls):
        """
        Validate critical configuration values.
        Called once during app startup.
        """

        errors = []

        # Mandatory keys
        if not cls.GEMINI_API_KEY:
            errors.append("❌ GEMINI_API_KEY is missing in .env")

        # Logical validation
        if cls.SCAN_TIMEOUT <= 0:
            errors.append("❌ SCAN_TIMEOUT must be greater than 0")

        if cls.MAX_PLATFORMS <= 0:
            errors.append("❌ MAX_PLATFORMS must be greater than 0")

        # Optional API warning (NOT fatal)
        if not cls.ABSTRACT_API_KEY:
            print("⚠️ ABSTRACT_API_KEY not set — email API scan will be limited")

        # Stop app only if fatal errors exist
        if errors:
            for error in errors:
                print(error)
            raise EnvironmentError(
                "Configuration validation failed. Fix the .env file."
            )

        # Ensure required directories exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.SCAN_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)

        print("✅ Configuration loaded and validated successfully")


# ==================================================
# EXPORT SINGLE CONFIG OBJECT
# ==================================================

config = Config
