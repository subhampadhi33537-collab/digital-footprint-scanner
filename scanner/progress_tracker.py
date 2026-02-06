"""
Real-Time Scan Progress Tracking
==================================
Provides real-time scan progress updates to frontend
"""

import logging
import threading
from datetime import datetime
from typing import Dict, List
from queue import Queue

logger = logging.getLogger(__name__)

# Enable immediate flushing of log output to terminal
import sys
import io
class ImmediateFlushHandler(logging.StreamHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()
        sys.stdout.flush()
        sys.stderr.flush()

if not logger.handlers:
    handler = ImmediateFlushHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [PROGRESS] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class ScanProgress:
    """Track scanning progress in real-time"""
    
    def __init__(self):
        self.current_scan = None
        self.platforms_checked = 0
        self.platforms_found = 0
        self.current_platform = None
        self.start_time = None
        self.status = "idle"
        self.results = []
        self.lock = threading.Lock()
    
    def start_scan(self, user_input: str, total_platforms: int):
        """Start tracking a new scan"""
        with self.lock:
            self.current_scan = user_input
            self.platforms_checked = 0
            self.platforms_found = 0
            self.current_platform = None
            self.start_time = datetime.now()
            self.status = "scanning"
            self.results = []
            logger.info(f"[SCAN STARTED] {user_input}")
            logger.info(f"[PLATFORMS] Scanning {total_platforms} platforms...")
    
    def update_platform(self, platform: str, status: str, found: bool = False):
        """Update progress for current platform"""
        with self.lock:
            self.current_platform = platform
            self.platforms_checked += 1
            if found:
                self.platforms_found += 1
            
            # Console output
            status_icon = "[OK]" if found else "[NO]" if status == "not_found" else "[TO]" if status == "timeout" else "[ER]"
            status_text = "FOUND" if found else status.upper() if status.upper() != "NOT_FOUND" else "NOT FOUND"
            
            progress_pct = int((self.platforms_checked / self.total_platforms) * 100) if hasattr(self, 'total_platforms') else 0
            
            logger.info(f"{status_icon} [{self.platforms_checked}] {platform.upper()}: {status_text}")
            
            # Immediate flush to terminal
            import sys
            sys.stdout.flush()
            sys.stderr.flush()
            
            self.results.append({
                "platform": platform,
                "status": status,
                "found": found,
                "timestamp": datetime.now().isoformat()
            })
    
    def finish_scan(self):
        """Mark scan as complete"""
        with self.lock:
            self.status = "complete"
            elapsed = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"[SCAN DONE] Found {self.platforms_found}/{self.platforms_checked} accounts in {elapsed:.1f}s")
            logger.info("="*60)
    
    def get_progress(self) -> Dict:
        """Get current scan progress"""
        with self.lock:
            elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            
            return {
                "status": self.status,
                "user_input": self.current_scan,
                "platforms_checked": self.platforms_checked,
                "platforms_found": self.platforms_found,
                "current_platform": self.current_platform,
                "elapsed_seconds": elapsed,
                "results": self.results
            }
    
    def is_scanning(self) -> bool:
        """Check if scan is in progress"""
        with self.lock:
            return self.status == "scanning"

# Global progress tracker
scan_progress = ScanProgress()

def log_platform_result(platform: str, status: str, found: bool = False):
    """Log platform result with progress tracking"""
    scan_progress.update_platform(platform, status, found)

def start_scan_logging(user_input: str, total_platforms: int):
    """Initialize scan logging"""
    scan_progress.total_platforms = total_platforms
    scan_progress.start_scan(user_input, total_platforms)

def finish_scan_logging():
    """Finalize scan logging"""
    scan_progress.finish_scan()
