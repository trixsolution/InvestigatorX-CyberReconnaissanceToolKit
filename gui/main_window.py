"""
gui/main_window.py
Main application window: header, sidebar navigation, stacked pages, status bar.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QStackedWidget, QPushButton,
    QStatusBar, QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

from gui.widgets.dashboard import DashboardWidget
from gui.widgets.network_scanner import NetworkScannerWidget
from gui.widgets.url_analyzer import URLAnalyzerWidget
from gui.widgets.domain_intel import DomainIntelWidget
from gui.widgets.email_intel import EmailIntelWidget
from gui.widgets.reports import ReportsWidget


NAV_ITEMS = [
    ("⬡  Dashboard",          "dashboard"),
    ("◈  Network Scanner",     "network"),
    ("⊕  URL Analyzer",        "url"),
    ("◎  Domain Intelligence", "domain"),
    ("✉  Email Intelligence",  "email"),
    ("▤  Reports",             "reports"),
]


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Investigator X – Cyber Recon Toolkit")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 680)

        self._active_nav = "dashboard"
        self._nav_buttons: dict[str, QPushButton] = {}

        self._build_ui()

    # ------------------------------------------------------------------ #
    # Build
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────
        root.addWidget(self._build_header())

        # ── Body (sidebar + main content) ─────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addWidget(self._build_sidebar())

        self._stack = QStackedWidget()
        self._stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body.addWidget(self._stack)

        # Pages
        self._pages: dict[str, QWidget] = {
            "dashboard": DashboardWidget(self),
            "network":   NetworkScannerWidget(self),
            "url":       URLAnalyzerWidget(self),
            "domain":    DomainIntelWidget(self),
            "email":     EmailIntelWidget(self),
            "reports":   ReportsWidget(self),
        }
        for widget in self._pages.values():
            self._stack.addWidget(widget)

        body_widget = QWidget()
        body_widget.setLayout(body)
        body_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(body_widget)

        # ── Status bar ────────────────────────────────────────────────
        self._status_label = QLabel("  ●  Ready")
        self._status_label.setObjectName("statusReady")
        sb = QStatusBar()
        sb.addWidget(self._status_label)
        self.setStatusBar(sb)

        # Navigate to default page
        self._navigate("dashboard")

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("header")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)

        # Logo placeholder (ASCII hex shield)
        logo_lbl = QLabel("⬡")
        logo_lbl.setStyleSheet(
            "color: #00ff9f; font-size: 28pt; font-weight: bold;"
        )

        title_col = QVBoxLayout()
        title_col.setSpacing(0)

        title = QLabel("INVESTIGATOR X")
        title.setObjectName("titleLabel")

        subtitle = QLabel("Cyber Recon Toolkit")
        subtitle.setObjectName("subtitleLabel")

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        layout.addWidget(logo_lbl)
        layout.addLayout(title_col)
        layout.addStretch()

        disclaimer = QLabel("⚠  For educational and authorized use only")
        disclaimer.setObjectName("disclaimerLabel")
        layout.addWidget(disclaimer)

        return header

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(2)

        nav_label = QLabel("  NAVIGATION")
        nav_label.setStyleSheet(
            "color: #484f58; font-size: 7pt; letter-spacing: 2px; "
            "padding: 8px 16px 4px 16px;"
        )
        layout.addWidget(nav_label)

        for label, key in NAV_ITEMS:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(False)
            btn.setFixedHeight(44)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            layout.addWidget(btn)
            self._nav_buttons[key] = btn

        layout.addStretch()

        # Version label
        ver = QLabel("  v1.0.0  |  2025")
        ver.setStyleSheet("color: #30363d; font-size: 7pt; padding: 4px 16px;")
        layout.addWidget(ver)

        return sidebar

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def _navigate(self, key: str):
        # Reset all nav buttons
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.setObjectName("navButtonActive")
            else:
                btn.setObjectName("navButton")
            # Force style refresh
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self._active_nav = key
        self._stack.setCurrentWidget(self._pages[key])

    # ------------------------------------------------------------------ #
    # Status bar helpers (called by child widgets)
    # ------------------------------------------------------------------ #
    @pyqtSlot(str)
    def set_status(self, text: str):
        color_map = {
            "ready":     ("#00ff9f", "statusReady"),
            "scanning":  ("#ffa500", "statusBusy"),
            "analyzing": ("#ffa500", "statusBusy"),
            "complete":  ("#00e5ff", "statusDone"),
            "error":     ("#ff4d4d", "statusBusy"),
        }
        key = text.lower().split()[0] if text else "ready"
        color, obj = color_map.get(key, ("#c9d1d9", "statusReady"))
        self._status_label.setObjectName(obj)
        self._status_label.setText(f"  ●  {text}")
        self._status_label.setStyleSheet(f"color: {color}; font-size: 8pt;")
