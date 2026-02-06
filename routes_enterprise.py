"""
Enterprise-Grade Features & Extensions
======================================
Advanced features for production deployment:
- Data export (PDF, CSV, JSON)
- API rate limiting
- Audit logging
- Result history/tracking
- Admin dashboard
"""

import json
import csv
import os
from datetime import datetime
from functools import wraps
import logging

from flask import request, jsonify, send_file
from io import StringIO, BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================
# RATE LIMITING
# ==============================
class RateLimiter:
    """Simple in-memory rate limiter"""
    def __init__(self, max_requests=100, window_seconds=3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, identifier):
        """Check if request is allowed"""
        now = datetime.now().timestamp()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(now)
            return True
        return False

rate_limiter = RateLimiter()

def rate_limit(max_requests=100, window_seconds=3600):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as identifier
            identifier = request.remote_addr
            
            if not rate_limiter.is_allowed(identifier):
                return jsonify({
                    "status": "error",
                    "message": f"Rate limit exceeded. Max {max_requests} requests per {window_seconds}s"
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==============================
# AUDIT LOGGING
# ==============================
class AuditLogger:
    """Centralized audit logging"""
    def __init__(self, log_file="logs/audit.log"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
    
    def log(self, action: str, user: str, details: dict, status: str = "success"):
        """Log an action"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user": user,
            "ip": request.remote_addr if request else "unknown",
            "status": status,
            "details": details
        }
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Audit log error: {e}")

audit_logger = AuditLogger()

# ==============================
# DATA EXPORT FUNCTIONS
# ==============================
def export_to_json(scan_results: dict) -> dict:
    """Export scan results as JSON"""
    return {
        "format": "json",
        "data": scan_results,
        "exported_at": datetime.now().isoformat()
    }

def export_to_csv(scan_results: dict) -> str:
    """Export scan results as CSV"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "User Input",
        "Platforms Found",
        "Risk Level",
        "ML Risk Score",
        "Timestamp",
    ])
    
    # Data row
    writer.writerow([
        scan_results.get("user_input", ""),
        len(scan_results.get("platforms_found", [])),
        scan_results.get("risk_level", ""),
        scan_results.get("ml_analysis", {}).get("ml_risk_score", ""),
        datetime.now().isoformat(),
    ])
    
    return output.getvalue()

def export_to_pdf(scan_results: dict) -> bytes:
    """Export scan results as PDF (requires reportlab)"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        pdf_file = BytesIO()
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"Digital Footprint Scan Report", styles['Heading1'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * 1))
        
        # Summary section
        summary_data = [
            ["Report Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["User Input", scan_results.get("user_input", "N/A")],
            ["Platforms Found", str(len(scan_results.get("platforms_found", [])))],
            ["Risk Level", scan_results.get("risk_level", "N/A")],
            ["ML Risk Score", f"{scan_results.get('ml_analysis', {}).get('ml_risk_score', 'N/A'):.1f}%"],
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        
        # Build PDF
        doc.build(elements)
        return pdf_file.getvalue()
        
    except ImportError:
        logger.warning("reportlab not installed. Returning JSON as fallback.")
        return json.dumps({
            "format": "pdf_fallback",
            "message": "PDF export requires reportlab installation",
            "data": export_to_json(scan_results)
        }).encode()

# ==============================
# RESULT HISTORY
# ==============================
class ResultHistory:
    """Manage scan result history"""
    def __init__(self, history_file="data/scan_history.jsonl"):
        self.history_file = history_file
        os.makedirs(os.path.dirname(history_file) or ".", exist_ok=True)
    
    def save(self, scan_results: dict, scan_id: str = None):
        """Save scan results to history"""
        if scan_id is None:
            scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        entry = {
            "scan_id": scan_id,
            "timestamp": datetime.now().isoformat(),
            "data": scan_results
        }
        
        try:
            with open(self.history_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
            return scan_id
        except Exception as e:
            logger.error(f"History save error: {e}")
            return None
    
    def get_history(self, limit: int = 100) -> list:
        """Retrieve recent scans"""
        scans = []
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r") as f:
                    for line in f:
                        if line.strip():
                            scans.append(json.loads(line))
            return scans[-limit:]  # Return last N scans
        except Exception as e:
            logger.error(f"History retrieval error: {e}")
            return []
    
    def get_by_id(self, scan_id: str) -> dict:
        """Retrieve specific scan"""
        for scan in self.get_history(limit=1000):
            if scan.get("scan_id") == scan_id:
                return scan.get("data")
        return None

result_history = ResultHistory()

# ==============================
# ANALYTICS & METRICS
# ==============================
class Analytics:
    """Track usage analytics"""
    def __init__(self):
        self.stats = {
            "total_scans": 0,
            "avg_risk_score": 0,
            "risk_distribution": {
                "LOW": 0,
                "MEDIUM": 0,
                "HIGH": 0,
                "CRITICAL": 0
            },
            "platforms_coverage": {}
        }
    
    def record_scan(self, scan_results: dict):
        """Record scan for analytics"""
        self.stats["total_scans"] += 1
        
        # Update average risk
        risk_score = scan_results.get("ml_analysis", {}).get("ml_risk_score", 50)
        n = self.stats["total_scans"]
        avg = self.stats["avg_risk_score"]
        self.stats["avg_risk_score"] = (avg * (n - 1) + risk_score) / n
        
        # Update distribution
        risk_level = scan_results.get("risk_level", "MEDIUM")
        if risk_level in self.stats["risk_distribution"]:
            self.stats["risk_distribution"][risk_level] += 1
        
        # Update platform coverage
        for platform in scan_results.get("platforms_found", []):
            if platform not in self.stats["platforms_coverage"]:
                self.stats["platforms_coverage"][platform] = 0
            self.stats["platforms_coverage"][platform] += 1
    
    def get_stats(self) -> dict:
        """Get current analytics"""
        return self.stats

analytics = Analytics()

# ==============================
# SECURITY HEADERS
# ==============================
def add_security_headers(response):
    """Add security headers to responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

# ==============================
# HEALTH CHECK & STATUS
# ==============================
def get_system_status() -> dict:
    """Get system status and metrics"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0-enterprise",
        "endpoints": {
            "scanning": "/api/scan",
            "chatbot": "/api/chat-with-ai",
            "ml": "/api/ml/predict/risk",
            "export": "/api/export",
            "analytics": "/api/analytics"
        },
        "analytics": analytics.get_stats()
    }
