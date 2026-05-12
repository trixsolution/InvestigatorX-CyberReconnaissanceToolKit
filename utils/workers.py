"""
utils/workers.py
QThread-based worker classes for non-blocking GUI operations.
Each module gets its own Worker with signals for progress and results.
"""

from PyQt5.QtCore import QThread, pyqtSignal
from typing import Callable, Any


class BaseWorker(QThread):
    """Base worker with common signals."""

    log_message = pyqtSignal(str)           # Terminal output line
    progress = pyqtSignal(int)              # 0-100
    status_changed = pyqtSignal(str)        # Status bar text
    finished = pyqtSignal()                 # Work done
    error = pyqtSignal(str)                 # Error message


class NetworkScanWorker(BaseWorker):
    """Worker for network scanning operations."""

    host_found = pyqtSignal(str, str, list, str)  # ip, status, ports, services
    scan_complete = pyqtSignal(list)               # list of result dicts

    def __init__(self, target: str, port_mode: str,
                 custom_start: int = 1, custom_end: int = 1024,
                 parent=None):
        super().__init__(parent)
        self.target = target
        self.port_mode = port_mode
        self.custom_start = custom_start
        self.custom_end = custom_end
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        from modules.scanner import NetworkScanner
        scanner = NetworkScanner(
            target=self.target,
            port_mode=self.port_mode,
            custom_start=self.custom_start,
            custom_end=self.custom_end,
        )

        def on_log(msg):
            self.log_message.emit(msg)

        def on_host(ip, status, ports, services):
            self.host_found.emit(ip, status, ports, services)

        def on_progress(val):
            self.progress.emit(val)

        try:
            results = scanner.run(
                log_cb=on_log,
                host_cb=on_host,
                progress_cb=on_progress,
                stop_flag=lambda: self._stop,
            )
            self.scan_complete.emit(results)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class URLAnalyzeWorker(BaseWorker):
    """Worker for URL analysis."""

    result_ready = pyqtSignal(dict)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        from modules.url_checker import URLChecker
        try:
            checker = URLChecker(self.url)
            result = checker.analyze()
            self.log_message.emit(f"[URL] Analysis complete for: {self.url}")
            self.result_ready.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class DomainLookupWorker(BaseWorker):
    """Worker for domain intelligence."""

    result_ready = pyqtSignal(dict)

    def __init__(self, domain: str, do_subdomain: bool, parent=None):
        super().__init__(parent)
        self.domain = domain
        self.do_subdomain = do_subdomain

    def run(self):
        from modules.domain_lookup import DomainLookup
        try:
            lookup = DomainLookup(self.domain)

            def on_log(msg):
                self.log_message.emit(msg)

            def on_progress(val):
                self.progress.emit(val)

            result = lookup.run(
                do_subdomain=self.do_subdomain,
                log_cb=on_log,
                progress_cb=on_progress,
            )
            self.result_ready.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()


class EmailCheckWorker(BaseWorker):
    """Worker for email intelligence."""

    result_ready = pyqtSignal(dict)

    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email

    def run(self):
        from modules.email_checker import EmailChecker
        try:
            checker = EmailChecker(self.email)

            def on_log(msg):
                self.log_message.emit(msg)

            result = checker.analyze(log_cb=on_log)
            self.result_ready.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
