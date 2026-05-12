"""
gui/widgets/dashboard.py
Dashboard home panel with stat cards and quick-start instructions.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QSpacerItem, QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


STAT_CARDS = [
    ("⬡", "Network Scanner", "Ping sweep, port scan\n& banner grabbing"),
    ("⊕", "URL Analyzer",    "Phishing risk scoring\n& keyword detection"),
    ("◎", "Domain Intel",    "WHOIS, DNS records\n& subdomain discovery"),
    ("✉", "Email Intel",     "MX lookup, format\nvalidation & checks"),
]

FEATURE_BULLETS = [
    "✔  Multithreaded network scanning (no GUI freeze)",
    "✔  Heuristic URL phishing risk score",
    "✔  WHOIS & full DNS record lookup",
    "✔  Subdomain brute-force (40+ wordlist)",
    "✔  Email MX & domain existence check",
    "✔  Color-coded terminal output",
    "✔  Export reports as JSON / TXT",
]


class StatCard(QFrame):
    def __init__(self, icon: str, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setMinimumSize(220, 120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("statIcon")
        icon_lbl.setAlignment(Qt.AlignLeft)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "color: #00e5ff; font-size: 10pt; font-weight: bold;"
        )

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("color: #8b949e; font-size: 8pt;")
        desc_lbl.setWordWrap(True)

        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)
        layout.addStretch()


class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(24)

        # ── Page title ────────────────────────────────────────────────
        title = QLabel("Dashboard")
        title.setObjectName("sectionHeader")

        root.addWidget(title)

        # ── Welcome banner ────────────────────────────────────────────
        banner = QFrame()
        banner.setObjectName("panel")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(24, 20, 24, 20)
        banner_layout.setSpacing(6)

        welcome = QLabel("Welcome to Investigator X")
        welcome.setStyleSheet(
            "color: #00ff9f; font-size: 16pt; font-weight: bold; letter-spacing: 1px;"
        )

        tagline = QLabel(
            "A professional Python-based Cyber Recon Toolkit for authorized security assessments."
        )
        tagline.setStyleSheet("color: #8b949e; font-size: 10pt;")
        tagline.setWordWrap(True)

        banner_layout.addWidget(welcome)
        banner_layout.addWidget(tagline)
        root.addWidget(banner)

        # ── Module cards ──────────────────────────────────────────────
        cards_label = QLabel("Modules")
        cards_label.setStyleSheet("color: #8b949e; font-size: 8pt; letter-spacing: 1px;")
        root.addWidget(cards_label)

        grid = QGridLayout()
        grid.setSpacing(12)
        for i, (icon, title_text, desc) in enumerate(STAT_CARDS):
            card = StatCard(icon, title_text, desc)
            grid.addWidget(card, i // 2, i % 2)
        root.addLayout(grid)

        # ── Feature list ──────────────────────────────────────────────
        features_frame = QFrame()
        features_frame.setObjectName("panel")
        feat_layout = QVBoxLayout(features_frame)
        feat_layout.setContentsMargins(20, 16, 20, 16)
        feat_layout.setSpacing(6)

        feat_title = QLabel("Capabilities")
        feat_title.setStyleSheet(
            "color: #00e5ff; font-size: 10pt; font-weight: bold;"
        )
        feat_layout.addWidget(feat_title)

        for bullet in FEATURE_BULLETS:
            lbl = QLabel(bullet)
            lbl.setStyleSheet("color: #c9d1d9; font-size: 9pt;")
            feat_layout.addWidget(lbl)

        root.addWidget(features_frame)

        # ── Disclaimer ────────────────────────────────────────────────
        disclaimer = QLabel(
            "⚠  All scans must be performed on networks and systems you own or have explicit written permission to test. "
            "Unauthorized scanning is illegal and unethical."
        )
        disclaimer.setStyleSheet(
            "color: #6e7681; font-size: 8pt; font-style: italic;"
        )
        disclaimer.setWordWrap(True)
        root.addWidget(disclaimer)

        root.addStretch()
