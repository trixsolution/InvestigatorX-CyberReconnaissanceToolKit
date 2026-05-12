"""
modules/url_checker.py
Heuristic URL risk analysis.
"""

import re
import urllib.parse
from typing import Callable


SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "free", "update", "account",
    "banking", "confirm", "password", "signin", "credential",
    "paypal", "apple", "microsoft", "amazon", "support",
    "winner", "prize", "urgent", "suspended", "validate",
]

IP_IN_URL_PATTERN = re.compile(
    r"https?://(?:\d{1,3}\.){3}\d{1,3}"
)

HOMOGRAPH_CHARS = set("аеіоурсукх")  # Cyrillic lookalikes

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "buff.ly", "adf.ly", "is.gd", "rb.gy", "cutt.ly",
}


class URLChecker:
    """
    Analyses a URL for phishing / malicious indicators.

    Risk levels: LOW (0-30) | MEDIUM (31-60) | HIGH (61+)
    """

    def __init__(self, url: str):
        self.url = url.strip()
        self.parsed = None
        self.score = 0
        self.flags: list[dict] = []

    def analyze(self) -> dict:
        """Run all checks. Returns a result dict."""
        self._parse_url()

        if self.parsed is None:
            return {
                "url": self.url,
                "valid": False,
                "risk_score": 0,
                "risk_level": "UNKNOWN",
                "flags": [{"label": "Invalid URL", "severity": "high"}],
                "details": {},
            }

        self._check_https()
        self._check_url_length()
        self._check_suspicious_keywords()
        self._check_ip_in_host()
        self._check_subdomain_depth()
        self._check_special_chars()
        self._check_shortener()
        self._check_port()
        self._check_homograph()

        level = self._score_to_level()

        return {
            "url": self.url,
            "valid": True,
            "risk_score": self.score,
            "risk_level": level,
            "flags": self.flags,
            "details": {
                "scheme": self.parsed.scheme,
                "host": self.parsed.netloc,
                "path": self.parsed.path,
                "query": self.parsed.query,
                "url_length": len(self.url),
                "https": self.parsed.scheme == "https",
            },
        }

    # ------------------------------------------------------------------ #
    # Checks
    # ------------------------------------------------------------------ #
    def _parse_url(self):
        try:
            parsed = urllib.parse.urlparse(self.url)
            # If no scheme given, assume http so we can at least get the host
            if not parsed.scheme:
                parsed = urllib.parse.urlparse("http://" + self.url)
            # Require a valid scheme (http/https) AND a non-empty host
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                self.parsed = None
            else:
                self.parsed = parsed
        except Exception:
            self.parsed = None

    def _check_https(self):
        if self.parsed.scheme != "https":
            self._add_flag("No HTTPS (unencrypted)", "medium", 20)
        else:
            self._add_flag("HTTPS present", "low", 0)

    def _check_url_length(self):
        l = len(self.url)
        if l > 100:
            self._add_flag(f"Very long URL ({l} chars)", "high", 25)
        elif l > 54:
            self._add_flag(f"Long URL ({l} chars)", "medium", 10)
        else:
            self._add_flag(f"Normal URL length ({l} chars)", "low", 0)

    def _check_suspicious_keywords(self):
        url_lower = self.url.lower()
        found = [kw for kw in SUSPICIOUS_KEYWORDS if kw in url_lower]
        if found:
            pts = min(len(found) * 10, 30)
            self._add_flag(
                f"Suspicious keywords: {', '.join(found)}", "high", pts
            )
        else:
            self._add_flag("No suspicious keywords", "low", 0)

    def _check_ip_in_host(self):
        if IP_IN_URL_PATTERN.match(self.url):
            self._add_flag("IP address used instead of domain", "high", 20)

    def _check_subdomain_depth(self):
        host = self.parsed.netloc.split(":")[0]
        parts = host.split(".")
        if len(parts) > 4:
            self._add_flag(f"Deep subdomain nesting ({len(parts)} levels)", "medium", 10)

    def _check_special_chars(self):
        suspicious = ["@", "//", "%20", "%00", ".."]
        found = [c for c in suspicious if c in self.url]
        if found:
            self._add_flag(
                f"Special characters found: {', '.join(found)}", "high", 15
            )

    def _check_shortener(self):
        host = self.parsed.netloc.split(":")[0].lower()
        if host in SHORTENERS:
            self._add_flag("URL shortener detected (hides real destination)", "medium", 10)

    def _check_port(self):
        if ":" in self.parsed.netloc:
            port_str = self.parsed.netloc.split(":")[-1]
            if port_str.isdigit():
                port = int(port_str)
                if port not in (80, 443, 8080, 8443):
                    self._add_flag(f"Unusual port in URL: {port}", "medium", 10)

    def _check_homograph(self):
        host = self.parsed.netloc.lower()
        suspicious = [c for c in host if c in HOMOGRAPH_CHARS]
        if suspicious:
            self._add_flag("Possible homograph/IDN attack detected", "high", 20)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _add_flag(self, label: str, severity: str, points: int):
        self.flags.append({"label": label, "severity": severity, "points": points})
        self.score += points

    def _score_to_level(self) -> str:
        if self.score >= 55:
            return "HIGH"
        elif self.score >= 25:
            return "MEDIUM"
        return "LOW"
