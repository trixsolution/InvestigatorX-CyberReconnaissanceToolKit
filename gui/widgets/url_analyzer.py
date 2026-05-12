"""
gui/widgets/url_analyzer.py
URL Analyzer panel – risk scoring with color-coded flags.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGroupBox, QTextEdit, QProgressBar,
    QScrollArea, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor

from utils.workers import URLAnalyzeWorker
from utils.logger import session_logger
from utils.exporter import export_json, export_txt


class FlagItem(QFrame):
    """A single indicator flag row."""

    SEVERITY_COLORS = {
        "high":   ("#3d0000", "#ff4d4d"),
        "medium": ("#3d2800", "#ffa500"),
        "low":    ("#003d2b", "#00ff9f"),
    }

    def __init__(self, label: str, severity: str, points: int, parent=None):
        super().__init__(parent)
        sev = severity.lower()
        bg, fg = self.SEVERITY_COLORS.get(sev, ("#21262d", "#c9d1d9"))

        self.setStyleSheet(
            f"background-color: {bg}; border: 1px solid {fg}; "
            f"border-radius: 4px; padding: 4px 10px;"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        icon_map = {"high": "✖", "medium": "⚠", "low": "✔"}
        icon = icon_map.get(sev, "•")

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"color: {fg}; font-size: 10pt; background: transparent; border: none;")
        icon_lbl.setFixedWidth(18)

        text_lbl = QLabel(label)
        text_lbl.setStyleSheet(f"color: {fg}; font-size: 9pt; background: transparent; border: none;")
        text_lbl.setWordWrap(True)

        pts_lbl = QLabel(f"+{points}" if points > 0 else "")
        pts_lbl.setStyleSheet(
            f"color: {fg}; font-size: 8pt; background: transparent; border: none; opacity: 0.7;"
        )
        pts_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(icon_lbl)
        layout.addWidget(text_lbl, 1)
        layout.addWidget(pts_lbl)


class URLAnalyzerWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: URLAnalyzeWorker | None = None
        self._last_result: dict = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("URL Analyzer")
        title.setObjectName("sectionHeader")
        root.addWidget(title)

        # ── Input ─────────────────────────────────────────────────────
        config = QGroupBox("Target URL")
        cfg_layout = QVBoxLayout(config)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        lbl = QLabel("URL:")
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(60)
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://example.com/login?redirect=verify")
        self._url_input.returnPressed.connect(self._start_analyze)

        self._btn_analyze = QPushButton("▶  Analyze")
        self._btn_analyze.setObjectName("primaryButton")
        self._btn_analyze.setFixedHeight(36)
        self._btn_analyze.setFixedWidth(120)
        self._btn_analyze.clicked.connect(self._start_analyze)

        self._btn_clear = QPushButton("⊘  Clear")
        self._btn_clear.setFixedHeight(36)
        self._btn_clear.setFixedWidth(100)
        self._btn_clear.clicked.connect(self._clear)

        input_row.addWidget(lbl)
        input_row.addWidget(self._url_input, 1)
        input_row.addWidget(self._btn_analyze)
        input_row.addWidget(self._btn_clear)
        cfg_layout.addLayout(input_row)
        root.addWidget(config)

        # ── Progress ──────────────────────────────────────────────────
        self._progress = QProgressBar()
        self._progress.setValue(0)
        root.addWidget(self._progress)

        # ── Results split ─────────────────────────────────────────────
        results_row = QHBoxLayout()
        results_row.setSpacing(16)

        # Left: Risk score card
        self._score_frame = QFrame()
        self._score_frame.setObjectName("panel")
        self._score_frame.setFixedWidth(200)
        score_layout = QVBoxLayout(self._score_frame)
        score_layout.setContentsMargins(16, 20, 16, 20)
        score_layout.setSpacing(8)
        score_layout.setAlignment(Qt.AlignCenter)

        score_title = QLabel("RISK SCORE")
        score_title.setStyleSheet("color: #8b949e; font-size: 7pt; letter-spacing: 2px;")
        score_title.setAlignment(Qt.AlignCenter)

        self._score_number = QLabel("—")
        self._score_number.setStyleSheet("color: #c9d1d9; font-size: 36pt; font-weight: bold;")
        self._score_number.setAlignment(Qt.AlignCenter)

        self._score_level = QLabel("—")
        self._score_level.setObjectName("riskLow")
        self._score_level.setAlignment(Qt.AlignCenter)

        score_layout.addStretch()
        score_layout.addWidget(score_title)
        score_layout.addWidget(self._score_number)
        score_layout.addWidget(self._score_level)

        self._valid_label = QLabel("")
        self._valid_label.setAlignment(Qt.AlignCenter)
        self._valid_label.setStyleSheet("font-size: 9pt; font-weight: bold;")
        score_layout.addWidget(self._valid_label)

        score_layout.addStretch()
        results_row.addWidget(self._score_frame)

        # Right: Flags list
        flags_outer = QFrame()
        flags_outer.setObjectName("panel")
        flags_outer_layout = QVBoxLayout(flags_outer)
        flags_outer_layout.setContentsMargins(12, 12, 12, 12)
        flags_outer_layout.setSpacing(8)

        flags_hdr = QHBoxLayout()
        flags_hdr_lbl = QLabel("Indicators")
        flags_hdr_lbl.setStyleSheet("color: #00e5ff; font-size: 10pt; font-weight: bold;")

        btn_export_json = QPushButton("Export JSON")
        btn_export_json.setObjectName("exportButton")
        btn_export_json.setFixedHeight(28)
        btn_export_json.clicked.connect(self._export_json)

        btn_export_txt = QPushButton("Export TXT")
        btn_export_txt.setObjectName("exportButton")
        btn_export_txt.setFixedHeight(28)
        btn_export_txt.clicked.connect(self._export_txt)

        flags_hdr.addWidget(flags_hdr_lbl)
        flags_hdr.addStretch()
        flags_hdr.addWidget(btn_export_json)
        flags_hdr.addWidget(btn_export_txt)
        flags_outer_layout.addLayout(flags_hdr)

        # Scrollable flags area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        self._flags_container = QWidget()
        self._flags_container.setStyleSheet("background: transparent;")
        self._flags_layout = QVBoxLayout(self._flags_container)
        self._flags_layout.setSpacing(6)
        self._flags_layout.setAlignment(Qt.AlignTop)

        placeholder = QLabel("Enter a URL above and click Analyze.")
        placeholder.setStyleSheet("color: #484f58; font-size: 9pt;")
        placeholder.setAlignment(Qt.AlignCenter)
        self._flags_layout.addWidget(placeholder)
        self._placeholder = placeholder

        scroll.setWidget(self._flags_container)
        flags_outer_layout.addWidget(scroll)
        results_row.addWidget(flags_outer, 1)

        root.addLayout(results_row)

        # ── Details panel ─────────────────────────────────────────────
        details_group = QGroupBox("URL Details")
        details_layout = QVBoxLayout(details_group)
        self._details_text = QTextEdit()
        self._details_text.setObjectName("terminalOutput")
        self._details_text.setReadOnly(True)
        self._details_text.setMaximumHeight(130)
        details_layout.addWidget(self._details_text)
        root.addWidget(details_group)

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def _start_analyze(self):
        url = self._url_input.text().strip()
        if not url:
            return

        self._btn_analyze.setEnabled(False)
        self._progress.setValue(20)
        self._clear_flags()
        self._details_text.clear()

        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Analyzing…")

        self._worker = URLAnalyzeWorker(url)
        self._worker.result_ready.connect(self._show_results)
        self._worker.error.connect(lambda e: self._show_error(e))
        self._worker.finished.connect(self._on_done)
        self._worker.start()
        session_logger.info(f"URL analysis started: {url}")

    def _clear(self):
        self._url_input.clear()
        self._score_number.setText("—")
        self._score_number.setStyleSheet("color: #c9d1d9; font-size: 36pt; font-weight: bold;")
        self._score_level.setText("—")
        self._score_level.setObjectName("riskLow")
        self._valid_label.setText("")
        self._details_text.clear()
        self._progress.setValue(0)
        self._clear_flags()
        if self._placeholder:
            self._placeholder.show()

    @pyqtSlot(dict)
    def _show_results(self, result: dict):
        self._last_result = result
        self._progress.setValue(100)

        if not result.get("valid"):
            self._show_error("Invalid or unparseable URL.")
            return

        # Score card
        score = result["risk_score"]
        level = result["risk_level"]
        self._score_number.setText(str(score))

        color_map = {
            "LOW":    ("#00ff9f", "36pt"),
            "MEDIUM": ("#ffa500", "36pt"),
            "HIGH":   ("#ff4d4d", "36pt"),
        }
        color, size = color_map.get(level, ("#c9d1d9", "36pt"))
        self._score_number.setStyleSheet(
            f"color: {color}; font-size: {size}; font-weight: bold;"
        )
        self._score_level.setText(f"● {level}")
        self._score_level.setStyleSheet(
            f"color: {color}; font-size: 13pt; font-weight: bold;"
        )
        self._valid_label.setText("VALID ✔")
        self._valid_label.setStyleSheet("color: #00ff9f; font-size: 9pt; font-weight: bold;")

        # Flags — show ALL flags so HTTPS / clean indicators are still visible
        self._clear_flags()
        if self._placeholder:
            self._placeholder.hide()

        for flag in result.get("flags", []):
            item = FlagItem(flag["label"], flag["severity"], flag["points"])
            self._flags_layout.addWidget(item)

        # Details
        details = result.get("details", {})
        lines = [
            f"URL      : {result['url']}",
            f"Scheme   : {details.get('scheme', 'N/A')}",
            f"Host     : {details.get('host', 'N/A')}",
            f"Path     : {details.get('path', '/')}",
            f"Query    : {details.get('query', '') or '(none)'}",
            f"Length   : {details.get('url_length', 0)} chars",
            f"HTTPS    : {'Yes ✔' if details.get('https') else 'No ✖'}",
        ]
        for line in lines:
            col = "#00ff9f" if "✔" in line else "#ff4d4d" if "✖" in line else "#c9d1d9"
            self._details_text.append(
                f"<span style='color:{col}'>{line}</span>"
            )

    def _show_error(self, msg: str):
        self._score_number.setText("!")
        self._score_number.setStyleSheet("color: #ff4d4d; font-size: 36pt; font-weight: bold;")
        self._score_level.setText("ERROR")
        self._score_level.setStyleSheet("color: #ff4d4d; font-size: 13pt; font-weight: bold;")
        self._valid_label.setText("INVALID ✖")
        self._valid_label.setStyleSheet("color: #ff4d4d; font-size: 9pt; font-weight: bold;")
        self._details_text.append(f"<span style='color:#ff4d4d'>[ERR] {msg}</span>")

    @pyqtSlot()
    def _on_done(self):
        self._btn_analyze.setEnabled(True)
        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Complete")
        session_logger.info("URL analysis completed.")

    def _clear_flags(self):
        while self._flags_layout.count():
            item = self._flags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._placeholder = None

    def _export_json(self):
        if not self._last_result:
            return
        path = export_json(self._last_result, "url_analyzer")
        self._details_text.append(
            f"<span style='color:#00e5ff'>[EXPORT] JSON saved: {path}</span>"
        )

    def _export_txt(self):
        if not self._last_result:
            return
        r = self._last_result
        lines = [
            f"URL     : {r.get('url')}",
            f"Risk    : {r.get('risk_level')} (score {r.get('risk_score')})",
            "",
            "Indicators:",
        ]
        for flag in r.get("flags", []):
            if flag["points"] > 0:
                lines.append(f"  [{flag['severity'].upper()}] {flag['label']} (+{flag['points']})")
        path = export_txt(lines, "url_analyzer")
        self._details_text.append(
            f"<span style='color:#00e5ff'>[EXPORT] TXT saved: {path}</span>"
        )
