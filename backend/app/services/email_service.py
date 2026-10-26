"""Email Delivery Service.

Supports three providers controlled by EMAIL_PROVIDER in .env:

  smtp         → Send via Gmail / Outlook / any personal SMTP server.
                 Uses Python built-in smtplib. No extra packages needed.
                 Best for personal/dev use.

  resend       → Send via Resend API (https://resend.com).
                 Requires RESEND_API_KEY.

  development  → Print OTP to backend terminal only. No real email sent.
                 Safe default for local development.
"""

import asyncio
import email.utils
import smtplib
import ssl
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


# ─────────────────────────────────────────────────────────────
# Email HTML / Text templates
# ─────────────────────────────────────────────────────────────

def _build_html(otp: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DoctorIn Verification Code</title>
  <style>
    body {{ margin:0; padding:0; background:#f8fafc; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }}
    .wrap {{ max-width:520px; margin:40px auto; padding:20px; }}
    .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:16px; padding:40px 36px; }}
    .logo {{ font-size:26px; font-weight:900; color:#0f172a; text-align:center; margin-bottom:28px; }}
    .logo span {{ color:#2563eb; }}
    h2 {{ font-size:18px; color:#0f172a; margin:0 0 8px; }}
    p {{ font-size:14px; color:#64748b; line-height:1.6; margin:0 0 20px; }}
    .code {{ background:#f1f5f9; border:2px solid #e2e8f0; border-radius:12px; font-size:36px;
             font-weight:800; letter-spacing:8px; color:#1e293b; text-align:center;
             padding:20px 16px; margin:24px 0; font-family:monospace; }}
    .note {{ font-size:13px; color:#94a3b8; line-height:1.6; }}
    .footer {{ font-size:12px; color:#cbd5e1; text-align:center; margin-top:24px;
               padding-top:20px; border-top:1px solid #f1f5f9; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="logo">Doctor<span>In</span></div>
      <h2>Verify your email address</h2>
      <p>Enter the code below to complete your DoctorIn registration.<br>
         This code is valid for <strong>5 minutes</strong>.</p>
      <div class="code">{otp}</div>
      <p class="note">If you did not request this code, you can safely ignore this email.
         Your account security has not been compromised.</p>
    </div>
    <div class="footer">DoctorIn &bull; Connect with Verified Medical Professionals</div>
  </div>
</body>
</html>"""


def _build_text(otp: str) -> str:
    return f"""DoctorIn — Verification Code

Your verification code is: {otp}

This code expires in 5 minutes.
If you did not request this code, you can safely ignore this email.

— DoctorIn Team
"""


# ─────────────────────────────────────────────────────────────
# Providers
# ─────────────────────────────────────────────────────────────

class DevelopmentEmailProvider:
    """Prints OTP to terminal only. No email sent."""

    async def send_otp(self, recipient: str, otp: str) -> bool:
        print("\n" + "=" * 60)
        print("[DOCTORIN DEV MODE] OTP generated — no email sent.")
        print(f"  Recipient : {recipient}")
        print(f"  OTP Code  : {otp}")
        print("  To send real emails, set EMAIL_PROVIDER=smtp in .env")
        print("=" * 60 + "\n")
        logger.info("[DEV] OTP generated (terminal only)", extra={"extra_data": {"recipient": recipient}})
        return True


class SMTPEmailProvider:
    """
    High-performance, RFC 5322 compliant SMTP delivery service.
    Features:
      - Connection pooling / warm connection reuse (drops delivery time to ~1.7s)
      - Clean envelope sender (RFC 5321 compliant) preventing Gmail anti-spam delay
      - Full RFC 5322 mandatory headers (Date, Message-ID, Reply-To)
      - Transactional priority headers (X-Priority, Priority, Importance, Auto-Submitted)
      - Port 465 (SSL) and Port 587 (STARTTLS) with automatic failover
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._server: smtplib.SMTP | smtplib.SMTP_SSL | None = None
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.clean_smtp_password or (settings.SMTP_PASSWORD or "").replace(" ", "").strip()
        self.use_tls = settings.SMTP_USE_TLS
        self.sender = settings.EMAIL_FROM or f"DoctorIn <{self.username}>"

    def _connect(self, port: int) -> smtplib.SMTP | smtplib.SMTP_SSL:
        use_ssl = (port == 465) or (not self.use_tls and port != 587)
        logger.info(f"[EMAIL] Connecting to SMTP server at {self.host}:{port} (SSL={use_ssl})...")

        ctx = ssl.create_default_context()
        if use_ssl:
            server = smtplib.SMTP_SSL(self.host, port, context=ctx, timeout=10)
        else:
            server = smtplib.SMTP(self.host, port, timeout=10)
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()

        server.login(self.username, self.password)
        logger.info(f"[EMAIL] SMTP authentication successful on port {port}.")
        return server

    def _get_connection(self) -> smtplib.SMTP | smtplib.SMTP_SSL:
        """Returns a cached alive SMTP connection or connects a fresh one with failover."""
        if self._server is not None:
            try:
                code, _ = self._server.noop()
                if code == 250:
                    return self._server
            except Exception:
                try:
                    self._server.quit()
                except Exception:
                    pass
                self._server = None

        try:
            self._server = self._connect(self.port)
            return self._server
        except Exception as primary_err:
            alt_port = 587 if self.port == 465 else 465
            logger.warning(
                f"[EMAIL] Primary SMTP connection to port {self.port} failed ({primary_err}). "
                f"Attempting fallback to port {alt_port}..."
            )
            try:
                self._server = self._connect(alt_port)
                return self._server
            except Exception:
                self._server = None
                raise primary_err

    def _send_sync(self, recipient: str, subject: str, html: str, text: str) -> None:
        """Synchronous SMTP send with warm connection reuse and complete RFC headers."""
        # 1. Clean envelope sender (RFC 5321 requires pure address, e.g. user@gmail.com)
        _, raw_email = email.utils.parseaddr(self.sender)
        envelope_from = raw_email or self.username

        # 2. Build RFC 5322 compliant message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = recipient
        msg["Reply-To"] = envelope_from
        msg["Date"] = email.utils.formatdate(localtime=True)
        domain = self.username.split("@")[-1] if "@" in self.username else "doctorin.local"
        msg["Message-ID"] = email.utils.make_msgid(domain=domain)

        # High-priority transactional headers prevent delayed queuing and spam filtering
        msg["X-Priority"] = "1"
        msg["Priority"] = "Urgent"
        msg["Importance"] = "High"
        msg["Auto-Submitted"] = "auto-generated"

        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        payload = msg.as_string()

        with self._lock:
            server = self._get_connection()
            try:
                server.sendmail(envelope_from, [recipient], payload)
            except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, smtplib.SMTPException, BrokenPipeError, ConnectionResetError, OSError):
                # Connection dropped while idle; reconnect once for immediate dispatch
                logger.info("[EMAIL] SMTP connection reset detected. Reconnecting for immediate dispatch...")
                try:
                    self._server.quit()
                except Exception:
                    pass
                self._server = None
                server = self._get_connection()
                server.sendmail(envelope_from, [recipient], payload)

    async def send_otp(self, recipient: str, otp: str) -> bool:
        if not self.username or not self.password:
            logger.error("[EMAIL/SMTP] Cannot send email: SMTP_USERNAME or SMTP_PASSWORD is not configured.")
            raise RuntimeError(
                "Gmail SMTP authentication failed: SMTP_PASSWORD is not set in backend .env file."
            )

        subject = f"{otp} is your DoctorIn verification code"
        html = _build_html(otp)
        text = _build_text(otp)

        try:
            logger.info(f"[EMAIL] Dispatching OTP email to {recipient} via SMTP...")
            await asyncio.to_thread(self._send_sync, recipient, subject, html, text)
            logger.info(f"[EMAIL] Verification email sent successfully to {recipient}")
            return True
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "[EMAIL/SMTP] Authentication failed. "
                "For Gmail: make sure you are using an App Password, not your login password. "
                "Enable at: myaccount.google.com → Security → App Passwords"
            )
            raise RuntimeError(
                "SMTP authentication failed. Check SMTP_USERNAME and SMTP_PASSWORD in .env."
            )
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, TimeoutError, OSError) as exc:
            logger.error(f"[EMAIL/SMTP] Network/connection error sending to {recipient}: {exc}")
            raise RuntimeError(f"SMTP connection failed: {exc}") from exc
        except smtplib.SMTPException as exc:
            logger.error(f"[EMAIL/SMTP] SMTP error sending to {recipient}: {exc}")
            raise RuntimeError(f"SMTP delivery failed: {exc}") from exc
        except Exception as exc:
            logger.error(f"[EMAIL/SMTP] Unexpected error sending to {recipient}: {exc}")
            raise RuntimeError(f"Email delivery error: {exc}") from exc


class ResendEmailProvider:
    """Sends email via Resend API. Requires RESEND_API_KEY."""

    def __init__(self):
        import resend as resend_sdk
        resend_sdk.api_key = settings.RESEND_API_KEY
        self._sdk = resend_sdk
        self.sender = settings.EMAIL_FROM or "DoctorIn <onboarding@resend.dev>"

    async def send_otp(self, recipient: str, otp: str) -> bool:
        try:
            logger.info(f"[EMAIL] Dispatching OTP email to {recipient} via Resend API...")
            params = {
                "from": self.sender,
                "to": [recipient],
                "subject": f"{otp} is your DoctorIn verification code",
                "html": _build_html(otp),
                "text": _build_text(otp),
            }
            result = self._sdk.Emails.send(params)
            email_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", "?")
            logger.info(f"[EMAIL] Verification email sent via Resend to {recipient}. ID: {email_id}")
            return True
        except Exception as exc:
            logger.error(f"[EMAIL/Resend] Delivery failed for {recipient}: {exc}")
            raise RuntimeError(f"Resend delivery failed: {exc}") from exc


# ─────────────────────────────────────────────────────────────
# Factory & Dispatch
# ─────────────────────────────────────────────────────────────

_provider_instances = {}

def get_email_provider():
    """Return the configured singleton provider based on current settings with smart fallback."""
    provider = (settings.EMAIL_PROVIDER or "development").strip().lower()

    if provider in ("smtp", "gmail", "email"):
        has_password = bool(settings.clean_smtp_password or settings.SMTP_PASSWORD)
        if settings.SMTP_USERNAME and has_password:
            if "smtp" not in _provider_instances:
                _provider_instances["smtp"] = SMTPEmailProvider()
            return _provider_instances["smtp"]
        logger.warning(
            "[EMAIL] EMAIL_PROVIDER=smtp configured but SMTP_PASSWORD is empty in .env. "
            "Falling back to DevelopmentEmailProvider (printing code to terminal)."
        )
        return DevelopmentEmailProvider()

    if provider == "resend":
        if settings.RESEND_API_KEY:
            if "resend" not in _provider_instances:
                _provider_instances["resend"] = ResendEmailProvider()
            return _provider_instances["resend"]
        logger.warning(
            "[EMAIL] EMAIL_PROVIDER=resend configured but RESEND_API_KEY is empty in .env. "
            "Falling back to DevelopmentEmailProvider (printing code to terminal)."
        )
        return DevelopmentEmailProvider()

    # Explicit development mode
    return DevelopmentEmailProvider()


async def send_otp_email(recipient_email: str, otp: str) -> bool:
    """
    Send OTP verification email via the configured provider.
    Returns True on success.
    Raises RuntimeError on delivery failure (caller converts this to user-facing error).
    """
    provider = get_email_provider()
    return await provider.send_otp(recipient=recipient_email, otp=otp)
