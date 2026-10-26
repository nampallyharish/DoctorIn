"""Input Sanitization, XSS Prevention, and PII Data Masking Utilities."""

import html
import re


class Sanitizer:
    """Security utility for input scrubbing, XSS prevention, and PII masking."""

    # Regex patterns for stripping dangerous tags and protocols
    SCRIPT_TAG_PATTERN = re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)
    HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
    JAVASCRIPT_URI_PATTERN = re.compile(r"javascript\s*:", re.IGNORECASE)

    @staticmethod
    def sanitize_text(text: str | None) -> str | None:
        """
        Strip script tags, escape special HTML entities, and remove javascript: URIs
        to protect against Cross-Site Scripting (XSS).
        """
        if not text or not isinstance(text, str):
            return text

        # 1. Remove explicit <script> tags
        cleaned = Sanitizer.SCRIPT_TAG_PATTERN.sub("", text)

        # 2. Remove javascript: pseudo-protocols
        cleaned = Sanitizer.JAVASCRIPT_URI_PATTERN.sub("", cleaned)

        # 3. HTML entity escape to prevent tag execution in raw HTML contexts
        return html.escape(cleaned.strip())

    @staticmethod
    def mask_email(email: str | None) -> str | None:
        """
        Mask email for secure logging / UI presentation.
        Example: doctor.johnson@hospital.org -> d***n@hospital.org
        """
        if not email or "@" not in email:
            return email

        user, domain = email.split("@", 1)
        if len(user) <= 2:
            masked_user = user[0] + "*"
        else:
            masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
        return f"{masked_user}@{domain}"

    @staticmethod
    def mask_phone(phone: str | None) -> str | None:
        """
        Mask phone number for secure logging.
        Example: +919876543210 -> +91******3210
        """
        if not phone or len(phone) < 6:
            return phone
        return phone[:3] + "*" * (len(phone) - 7) + phone[-4:]

    @staticmethod
    def mask_token(token: str | None) -> str | None:
        """
        Mask JWT / Auth token for safe logging.
        Example: eyJhbGciOiJIUzI1NiIsIn... -> eyJhb...[REDACTED]
        """
        if not token or len(token) < 10:
            return "[REDACTED]"
        return token[:6] + "...[REDACTED]"
