"""
modules/scanner.py
Network scanning: ping sweep, port scanning, banner grabbing.
Uses threading for speed; safe and modular.
"""

import socket
import concurrent.futures
import ipaddress
import subprocess
import platform
from typing import Callable, Optional

# Top 20 most common ports for quick scan
TOP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
    143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080,
]

# Common service names
SERVICE_NAMES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    111: "RPC",
    135: "MSRPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    993: "IMAPS",
    995: "POP3S",
    1723: "PPTP",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Alt",
}


class NetworkScanner:
    """
    Performs ping sweep + port scanning with optional banner grabbing.

    Parameters
    ----------
    target: str
        Single IP (e.g. '192.168.1.1') or CIDR (e.g. '192.168.1.0/24')
    port_mode: str
        'top'    – scan TOP_PORTS
        'custom' – scan custom_start..custom_end
        'full'   – scan 1-65535
    """

    MAX_WORKERS = 50
    TIMEOUT = 1.0  # seconds

    def __init__(
        self,
        target: str,
        port_mode: str = "top",
        custom_start: int = 1,
        custom_end: int = 1024,
    ):
        self.target = target.strip()
        self.port_mode = port_mode
        self.custom_start = custom_start
        self.custom_end = custom_end

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def run(
        self,
        log_cb: Callable[[str], None] = print,
        host_cb: Optional[Callable] = None,
        progress_cb: Optional[Callable[[int], None]] = None,
        stop_flag: Callable[[], bool] = lambda: False,
    ) -> list[dict]:
        """
        Main entry point. Returns list of result dicts:
            { ip, status, open_ports: [], services: {} }
        """
        hosts = self._parse_targets()
        results = []
        total = len(hosts)

        log_cb(f"[SCAN] Starting scan on {self.target} ({total} host(s))")
        log_cb(f"[SCAN] Port mode: {self.port_mode}")

        for idx, ip in enumerate(hosts):
            if stop_flag():
                log_cb("[SCAN] Scan aborted by user.")
                break

            is_up = self._ping(ip)
            status = "UP" if is_up else "DOWN"
            open_ports = []
            services = {}

            if is_up:
                log_cb(f"[HOST] {ip} is UP – scanning ports…")
                ports_to_scan = self._get_ports()
                open_ports, services = self._scan_ports(ip, ports_to_scan, log_cb, stop_flag)
            else:
                log_cb(f"[HOST] {ip} is DOWN (no response)")

            result = {
                "ip": ip,
                "status": status,
                "open_ports": open_ports,
                "services": services,
            }
            results.append(result)

            if host_cb:
                host_cb(ip, status, open_ports, services)

            if progress_cb:
                pct = int((idx + 1) / total * 100)
                progress_cb(pct)

        log_cb(f"[SCAN] Complete. {len([r for r in results if r['status']=='UP'])} host(s) up.")
        return results

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _parse_targets(self) -> list[str]:
        """Expand CIDR or return single IP list."""
        try:
            network = ipaddress.ip_network(self.target, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError:
            return [self.target]

    def _ping(self, ip: str) -> bool:
        """Send ICMP ping; returns True if host responds."""
        system = platform.system().lower()
        flag = "-n" if system == "windows" else "-c"
        timeout_flag = "-w" if system == "windows" else "-W"
        timeout_val = "500" if system == "windows" else "1"

        try:
            result = subprocess.run(
                ["ping", flag, "1", timeout_flag, timeout_val, ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=3,
            )
            return result.returncode == 0
        except Exception:
            return self._tcp_probe(ip)

    def _tcp_probe(self, ip: str) -> bool:
        """Fallback: try TCP connect to port 80 or 443."""
        for port in (80, 443, 22):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self.TIMEOUT)
                s.connect((ip, port))
                s.close()
                return True
            except Exception:
                pass
        return False

    def _get_ports(self) -> list[int]:
        if self.port_mode == "top":
            return TOP_PORTS
        elif self.port_mode == "full":
            return list(range(1, 65536))
        else:  # custom
            return list(range(self.custom_start, self.custom_end + 1))

    def _scan_ports(
        self,
        ip: str,
        ports: list[int],
        log_cb: Callable,
        stop_flag: Callable[[], bool],
    ) -> tuple[list[int], dict[int, str]]:
        """Threaded port scan returning (open_ports, {port: service})."""
        open_ports = []
        services = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            future_map = {
                executor.submit(self._check_port, ip, port): port
                for port in ports
            }
            for future in concurrent.futures.as_completed(future_map):
                if stop_flag():
                    executor.shutdown(wait=False)
                    break
                port = future_map[future]
                try:
                    is_open, banner = future.result()
                    if is_open:
                        open_ports.append(port)
                        service = SERVICE_NAMES.get(port, "Unknown")
                        if banner:
                            service = f"{service} [{banner[:40]}]"
                        services[port] = service
                        log_cb(f"  [OPEN] {ip}:{port}  {service}")
                except Exception:
                    pass

        open_ports.sort()
        return open_ports, services

    def _check_port(self, ip: str, port: int) -> tuple[bool, str]:
        """Attempt TCP connect and optional banner grab."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.TIMEOUT)
            s.connect((ip, port))
            # Banner grab
            banner = ""
            try:
                s.settimeout(0.5)
                data = s.recv(256)
                banner = data.decode("utf-8", errors="ignore").strip()
            except Exception:
                pass
            s.close()
            return True, banner
        except Exception:
            return False, ""
