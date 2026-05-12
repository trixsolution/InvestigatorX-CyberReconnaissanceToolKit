"""
modules/domain_lookup.py
WHOIS, DNS record lookup, IP resolution, and subdomain brute-force.
"""

import socket
import concurrent.futures
from datetime import datetime, timezone
from typing import Callable, Optional


# Common subdomain wordlist
SUBDOMAIN_WORDLIST = [
    "www", "mail", "ftp", "smtp", "pop", "imap", "webmail",
    "admin", "portal", "vpn", "api", "dev", "staging", "test",
    "blog", "shop", "store", "cdn", "media", "images", "static",
    "mobile", "m", "app", "secure", "login", "auth", "sso",
    "remote", "git", "svn", "jira", "wiki", "docs", "support",
    "help", "kb", "status", "monitor", "mx", "ns1", "ns2",
]


class DomainLookup:
    """
    Comprehensive domain intelligence:
    - WHOIS info & domain age
    - DNS records (A, MX, NS, TXT)
    - IP resolution
    - Subdomain brute-force
    """

    def __init__(self, domain: str):
        self.domain = domain.strip().lower()
        # Remove http/https if accidentally passed
        for prefix in ("https://", "http://", "www."):
            if self.domain.startswith(prefix):
                self.domain = self.domain[len(prefix):]

    def run(
        self,
        do_subdomain: bool = True,
        log_cb: Callable[[str], None] = print,
        progress_cb: Optional[Callable[[int], None]] = None,
    ) -> dict:
        result = {
            "domain": self.domain,
            "whois": {},
            "dns": {},
            "ip": None,
            "subdomains": [],
            "errors": [],
        }

        log_cb(f"[DOMAIN] Starting intelligence gathering for: {self.domain}")

        # ── 1. IP Resolution ──────────────────────────────────────────
        log_cb("[DNS] Resolving IP address…")
        result["ip"] = self._resolve_ip(log_cb)
        if progress_cb:
            progress_cb(15)

        # ── 2. WHOIS ──────────────────────────────────────────────────
        log_cb("[WHOIS] Fetching WHOIS data…")
        result["whois"] = self._get_whois(log_cb)
        if progress_cb:
            progress_cb(40)

        # ── 3. DNS Records ────────────────────────────────────────────
        log_cb("[DNS] Querying DNS records (A, MX, NS, TXT)…")
        result["dns"] = self._get_dns_records(log_cb)
        if progress_cb:
            progress_cb(65)

        # ── 4. Subdomain Scan ─────────────────────────────────────────
        if do_subdomain:
            log_cb(f"[SUBDOMAIN] Brute-forcing {len(SUBDOMAIN_WORDLIST)} common subdomains…")
            result["subdomains"] = self._bruteforce_subdomains(log_cb, progress_cb)
        else:
            if progress_cb:
                progress_cb(95)

        if progress_cb:
            progress_cb(100)
        log_cb(f"[DOMAIN] Intelligence complete for: {self.domain}")
        return result

    # ------------------------------------------------------------------ #
    # IP Resolution
    # ------------------------------------------------------------------ #
    def _resolve_ip(self, log_cb: Callable) -> Optional[str]:
        try:
            ip = socket.gethostbyname(self.domain)
            log_cb(f"  [IP] {self.domain} → {ip}")
            return ip
        except socket.gaierror as e:
            log_cb(f"  [ERR] IP resolution failed: {e}")
            return None

    # ------------------------------------------------------------------ #
    # WHOIS
    # ------------------------------------------------------------------ #
    def _get_whois(self, log_cb: Callable) -> dict:
        try:
            import whois as whois_lib
            w = whois_lib.whois(self.domain)
            info = {
                "registrar": str(w.registrar or "N/A"),
                "creation_date": self._format_date(w.creation_date),
                "expiration_date": self._format_date(w.expiration_date),
                "updated_date": self._format_date(w.updated_date),
                "name_servers": self._to_list(w.name_servers),
                "status": self._to_list(w.status),
                "country": str(w.country or "N/A"),
                "org": str(w.org or "N/A"),
                "domain_age_days": self._calc_age(w.creation_date),
            }
            log_cb(f"  [WHOIS] Registrar: {info['registrar']}")
            log_cb(f"  [WHOIS] Created: {info['creation_date']}")
            log_cb(f"  [WHOIS] Domain age: {info['domain_age_days']} days")
            return info
        except ImportError:
            log_cb("  [WARN] python-whois not installed. Skipping WHOIS.")
            return {"error": "python-whois not installed"}
        except Exception as e:
            log_cb(f"  [ERR] WHOIS lookup failed: {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------------ #
    # DNS Records
    # ------------------------------------------------------------------ #
    def _get_dns_records(self, log_cb: Callable) -> dict:
        records = {}
        try:
            import dns.resolver
        except ImportError:
            log_cb("  [WARN] dnspython not installed. Skipping DNS.")
            return {"error": "dnspython not installed"}

        for rtype in ("A", "MX", "NS", "TXT"):
            try:
                answers = dns.resolver.resolve(self.domain, rtype, lifetime=5)
                records[rtype] = [str(r) for r in answers]
                log_cb(f"  [DNS] {rtype}: {', '.join(records[rtype][:3])}")
            except Exception as e:
                records[rtype] = []
                log_cb(f"  [DNS] {rtype}: no record ({e})")

        return records

    # ------------------------------------------------------------------ #
    # Subdomain Brute-force
    # ------------------------------------------------------------------ #
    def _bruteforce_subdomains(
        self,
        log_cb: Callable,
        progress_cb: Optional[Callable],
    ) -> list[str]:
        found = []
        total = len(SUBDOMAIN_WORDLIST)

        def check(word):
            sub = f"{word}.{self.domain}"
            try:
                ip = socket.gethostbyname(sub)
                return (sub, ip)
            except Exception:
                return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(check, w): i for i, w in enumerate(SUBDOMAIN_WORDLIST)}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                res = future.result()
                if res:
                    sub, ip = res
                    found.append({"subdomain": sub, "ip": ip})
                    log_cb(f"  [FOUND] {sub} → {ip}")
                if progress_cb:
                    pct = 65 + int((i + 1) / total * 30)
                    progress_cb(min(pct, 95))

        log_cb(f"  [SUBDOMAIN] Found {len(found)} active subdomains.")
        return found

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _format_date(date_value) -> str:
        if date_value is None:
            return "N/A"
        if isinstance(date_value, list):
            date_value = date_value[0]
        try:
            if hasattr(date_value, "strftime"):
                return date_value.strftime("%Y-%m-%d")
            return str(date_value)
        except Exception:
            return str(date_value)

    @staticmethod
    def _calc_age(creation_date) -> int:
        if creation_date is None:
            return -1
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        try:
            now = datetime.now()
            if hasattr(creation_date, "tzinfo") and creation_date.tzinfo:
                now = datetime.now(timezone.utc)
            delta = now - creation_date
            return delta.days
        except Exception:
            return -1

    @staticmethod
    def _to_list(value) -> list:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v) for v in value]
        return [str(value)]
