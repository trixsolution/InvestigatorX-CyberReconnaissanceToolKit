"""
modules/email_checker.py
Email intelligence: format validation, domain extraction,
MX record lookup, and domain existence check.
"""

import re
import socket
from typing import Callable, Optional

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com",
    "throwaway.email", "yopmail.com", "10minutemail.com",
    "trashmail.com", "sharklasers.com", "guerrillamailblock.com",
    "grr.la", "guerrillamail.info", "spam4.me", "maildrop.cc",
}


class EmailChecker:
    """
    Analyses an email address for:
    - Format validity
    - Domain extraction
    - MX record presence
    - Domain DNS existence
    - Disposable email detection
    """

    def __init__(self, email: str):
        self.email = email.strip()
        self.username = ""
        self.domain = ""

    def analyze(self, log_cb: Callable[[str], None] = print) -> dict:
        result = {
            "email": self.email,
            "valid_format": False,
            "username": "",
            "domain": "",
            "mx_records": [],
            "domain_resolves": False,
            "is_disposable": False,
            "issues": [],
            "score": "UNKNOWN",
        }

        log_cb(f"[EMAIL] Analysing: {self.email}")

        # ── Format check ──────────────────────────────────────────────
        if not EMAIL_REGEX.match(self.email):
            result["issues"].append("Invalid email format")
            result["score"] = "INVALID"
            log_cb("  [ERR] Invalid email format")
            return result

        result["valid_format"] = True
        parts = self.email.split("@", 1)
        self.username = parts[0]
        self.domain = parts[1].lower()
        result["username"] = self.username
        result["domain"] = self.domain
        log_cb(f"  [OK] Format valid. User='{self.username}', Domain='{self.domain}'")

        # ── Disposable check ──────────────────────────────────────────
        if self.domain in DISPOSABLE_DOMAINS:
            result["is_disposable"] = True
            result["issues"].append("Disposable / throwaway email domain")
            log_cb(f"  [WARN] Disposable domain detected: {self.domain}")

        # ── Domain resolution ─────────────────────────────────────────
        log_cb(f"  [DNS] Checking if domain resolves…")
        result["domain_resolves"] = self._check_domain_resolves(log_cb)

        if not result["domain_resolves"]:
            result["issues"].append("Domain does not resolve (DNS failure)")
            log_cb(f"  [ERR] Domain '{self.domain}' does not resolve")

        # ── MX records ────────────────────────────────────────────────
        log_cb(f"  [MX] Looking up MX records for {self.domain}…")
        result["mx_records"] = self._get_mx_records(log_cb)

        if not result["mx_records"]:
            result["issues"].append("No MX records found – domain cannot receive email")
            log_cb(f"  [ERR] No MX records for {self.domain}")

        # ── Overall score ─────────────────────────────────────────────
        result["score"] = self._calculate_score(result)
        log_cb(f"  [SCORE] Email score: {result['score']}")

        return result

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _check_domain_resolves(self, log_cb: Callable) -> bool:
        try:
            socket.gethostbyname(self.domain)
            log_cb(f"  [OK] Domain resolves.")
            return True
        except socket.gaierror:
            return False

    def _get_mx_records(self, log_cb: Callable) -> list[str]:
        try:
            import dns.resolver
            answers = dns.resolver.resolve(self.domain, "MX", lifetime=5)
            records = sorted(
                [(r.preference, str(r.exchange).rstrip(".")) for r in answers]
            )
            for pref, mx in records:
                log_cb(f"  [MX] Priority {pref}: {mx}")
            return [mx for _, mx in records]
        except ImportError:
            log_cb("  [WARN] dnspython not installed.")
            return self._fallback_mx(log_cb)
        except Exception as e:
            log_cb(f"  [ERR] MX lookup failed: {e}")
            return []

    def _fallback_mx(self, log_cb: Callable) -> list[str]:
        """Fallback: attempt socket connection to common mail ports."""
        for port in (25, 587, 465):
            try:
                s = socket.socket()
                s.settimeout(2)
                s.connect((self.domain, port))
                s.close()
                log_cb(f"  [MX-FALLBACK] Mail port {port} reachable on {self.domain}")
                return [self.domain]
            except Exception:
                pass
        return []

    @staticmethod
    def _calculate_score(result: dict) -> str:
        if not result["valid_format"]:
            return "INVALID"
        issues = len(result["issues"])
        if result["domain_resolves"] and result["mx_records"] and issues == 0:
            return "VALID"
        elif result["domain_resolves"] and issues <= 1:
            return "SUSPICIOUS"
        return "INVALID"
