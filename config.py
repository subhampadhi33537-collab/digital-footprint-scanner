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
    All modules import configuration from here.
    """

    # --------------------------------------------------
    # FLASK CORE SETTINGS
    # --------------------------------------------------
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

    # --------------------------------------------------
    # GROQ AI SETTINGS
    # --------------------------------------------------
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", 512))  # Reduced for speed
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", 0.3))  # Lower for consistency

    # --------------------------------------------------
    # FREE EMAIL OSINT / VALIDATION API
    # --------------------------------------------------
    ABSTRACT_API_KEY = os.getenv("ABSTRACT_API_KEY")
    ABSTRACT_EMAIL_API_KEY = os.getenv("ABSTRACT_EMAIL_API_KEY") or os.getenv("ABSTRACT_API_KEY")
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
    # RISK SCORING THRESHOLDS (exposure counts)
    # --------------------------------------------------
    RISK_THRESHOLDS = {
        "LOW": 2,
        "MEDIUM": 5,
        "HIGH": 10
    }

    # --------------------------------------------------
    # GOOGLE OAUTH SETTINGS
    # --------------------------------------------------
    GOOGLE_CLIENT_SECRETS_FILE = BASE_DIR / "client_secret.json"
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/gmail.readonly"
    ]
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/callback"
    )

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
        if not cls.GROQ_API_KEY:
            errors.append("[ERROR] GROQ_API_KEY is missing in .env")

        # Logical validation
        if cls.SCAN_TIMEOUT <= 0:
            errors.append("[ERROR] SCAN_TIMEOUT must be greater than 0")

        if cls.MAX_PLATFORMS <= 0:
            errors.append("[ERROR] MAX_PLATFORMS must be greater than 0")

        # Optional API warning (NOT fatal)
        if not cls.ABSTRACT_EMAIL_API_KEY and not cls.ABSTRACT_API_KEY:
            print("[WARNING] ABSTRACT_EMAIL_API_KEY / ABSTRACT_API_KEY not set — email API scan will be limited")

        if not cls.GOOGLE_CLIENT_SECRETS_FILE.exists():
            errors.append(f"[ERROR] Google client_secrets file not found at {cls.GOOGLE_CLIENT_SECRETS_FILE}")

        # Stop app only if fatal errors exist
        if errors:
            for error in errors:
                print(error)
            raise EnvironmentError("Configuration validation failed. Fix the .env file or missing files.")

        # Ensure required directories exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.SCAN_DIR.mkdir(exist_ok=True)
        cls.TEMP_DIR.mkdir(exist_ok=True)

        print("[OK] Configuration loaded and validated successfully")


# ==================================================
# EXPORT SINGLE CONFIG OBJECT
# ==================================================
config = Config
