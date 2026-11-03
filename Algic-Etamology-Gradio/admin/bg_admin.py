# Admin/bg_admin.py
import smtplib
import threading
import json
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis

# Configure system audit logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("🚨 EMERGENCY-BG-ADMIN")

class BackgroundAdminMonitor:
    """Manages system alerts and sends background SMTP notifications for emergency events."""
    
    def __init__(self, flask_app=None):
        self.app = flask_app
        self.redis_client = None
        
        if self.app:
            if self.app.config.get("USE_REDIS_CACHE", True):
                self.redis_client = redis.Redis.from_url(self.app.config.get("REDIS_URI", "redis://localhost:6379/0"))

    def trigger_break_glass_alert(self, operator_ip, timestamp=None):
        """Dispatches immediate notification emails using an isolated background thread."""
        ts = timestamp or time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
        
        # 1. Update the Redis cache structure for real-time monitoring
        if self.redis_client:
            event_log = {"status": "COMPROMISED", "operator_ip": operator_ip, "timestamp": ts}
            self.redis_client.set("sys:status:break_glass", json.dumps(event_log))
            self.redis_client.incr("sys:metrics:security_alerts")
            
        # 2. Extract configurations from the app context
        smtp_cfg = {
            "host": self.app.config.get("SMTP_HOST"),
            "port": self.app.config.get("SMTP_PORT"),
            "user": self.app.config.get("SMTP_USERNAME"),
            "pass": self.app.config.get("SMTP_PASSWORD"),
            "from": self.app.config.get("SMTP_FROM_EMAIL"),
            "dev_mode": self.app.config.get("USE_TERMINAL_EMAIL", True)
        }

        # 3. Spin up an isolated execution thread to prevent network latency from blocking users
        email_thread = threading.Thread(
            target=self._execute_smtp_payload,
            args=(smtp_cfg, operator_ip, ts)
        )
        email_thread.daemon = True
        email_thread.start()

    def _execute_smtp_payload(self, cfg, operator_ip, timestamp):
        """Assembles the security notification email and dispatches it over SMTP."""
        subject = "🚨 CRITICAL SYSTEM ALERT: Algic Platform Break-Glass Activated"
        body = f"""
        ===================================================================
        CRITICAL SECURITY OVERRIDE NOTIFICATION
        ===================================================================
        The system break-glass emergency account has been successfully accessed.
        
        Event Details:
        - Timestamp: {timestamp}
        - Source IP Address: {operator_ip}
        - Authentication Path: Local Memory Hash Override
        
        Action Required:
        Verify the status of your university Active Directory network node.
        Ensure this access was authorized by a system administrator.
        ===================================================================
        """
        
        # Dev Mode Check: Print directly to stdout instead of calling external relays
        if cfg["dev_mode"]:
            logger.warning("\n[DEV MODE - SMTP TERMINAL PRINTOUT]%s\nTo: %s\nSubject: %s\n%s", "═"*30, cfg["from"], subject, body)
            return

        # Production Execution Loop
        try:
            msg = MIMEMultipart()
            msg['From'] = cfg["from"]
            msg['To'] = cfg["from"]  # Routes notifications back to the administrative mailbox
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Open secure SMTP connection tunnel
            server = smtplib.SMTP(cfg["host"], cfg["port"])
            server.starttls()  # Enforce TLS encryption handshake properties
            server.login(cfg["user"], cfg["pass"])
            server.sendmail(cfg["from"], cfg["from"], msg.as_string())
            server.quit()
            logger.info("Successfully dispatched security alert email to system administrators.")
            
        except Exception as e:
            logger.error("Failed to route emergency notification over SMTP: %s", str(e))
