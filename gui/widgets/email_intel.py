"""
gui/widgets/email_intel.py
Email Intelligence panel – format validation, MX lookup, domain check.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFrame, QTextEdit, QProgressBar,
    QGridLayout, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor

from utils.workers import EmailCheckWorker
from utils.logger import session_logger
from utils.exporter import export_json, export_txt


class InfoCard(QFrame):
    """A key-value info row card."""

    def __init__(self, label: str, value: str = "—", color: str = "#c9d1d9", parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setStyleSheet(
            "QFrame#panel { background-color: #161b22; border: 1px solid #21262d; border-radius: 6px; }"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #8b949e; font-size: 8pt;")
        lbl.setFixedWidth(130)

        self._val = QLabel(value)
        self._val.setStyleSheet(f"color: {color}; font-size: 9pt; font-weight: bold;")
        self._val.setWordWrap(True)

        layout.addWidget(lbl)
        layout.addWidget(self._val, 1)

    def set_value(self, value: str, color: str = "#c9d1d9"):
        self._val.setText(value)
        self._val.setStyleSheet(f"color: {color}; font-size: 9pt; font-weight: bold;")


class EmailIntelWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: EmailCheckWorker | None = None
        self._last_result: dict = {}
        self._info_cards: dict[str, InfoCard] = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("Email Intelligence")
        title.setObjectName("sectionHeader")
        root.addWidget(title)

        # ── Config ────────────────────────────────────────────────────
        config = QGroupBox("Target Email")
        cfg_layout = QVBoxLayout(config)

        row = QHBoxLayout()
        row.setSpacing(10)
        lbl = QLabel("Email:")
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(60)

        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("user@example.com")
        self._email_input.returnPressed.connect(self._start_check)

        self._btn_check = QPushButton("▶  Analyze")
        self._btn_check.setObjectName("primaryButton")
        self._btn_check.setFixedHeight(36)
        self._btn_check.setFixedWidth(120)
        self._btn_check.clicked.connect(self._start_check)

        self._btn_clear = QPushButton("⊘  Clear")
        self._btn_clear.setFixedHeight(36)
        self._btn_clear.setFixedWidth(100)
        self._btn_clear.clicked.connect(self._clear)

        btn_export_json = QPushButton("Export JSON")
        btn_export_json.setObjectName("exportButton")
        btn_export_json.setFixedHeight(36)
        btn_export_json.clicked.connect(self._export_json)

        btn_export_txt = QPushButton("Export TXT")
        btn_export_txt.setObjectName("exportButton")
        btn_export_txt.setFixedHeight(36)
        btn_export_txt.clicked.connect(self._export_txt)

        row.addWidget(lbl)
        row.addWidget(self._email_input, 1)
        row.addWidget(self._btn_check)
        row.addWidget(self._btn_clear)
        row.addWidget(btn_export_json)
        row.addWidget(btn_export_txt)
        cfg_layout.addLayout(row)
        root.addWidget(config)

        # ── Progress ──────────────────────────────────────────────────
        self._progress = QProgressBar()
        self._progress.setValue(0)
        root.addWidget(self._progress)

        # ── Results ───────────────────────────────────────────────────
        results_row = QHBoxLayout()
        results_row.setSpacing(16)

        # Left: Score card
        self._score_frame = QFrame()
        self._score_frame.setObjectName("panel")
        self._score_frame.setFixedWidth(200)
        score_layout = QVBoxLayout(self._score_frame)
        score_layout.setAlignment(Qt.AlignCenter)
        score_layout.setContentsMargins(16, 20, 16, 20)

        score_title = QLabel("EMAIL STATUS")
        score_title.setStyleSheet("color: #8b949e; font-size: 7pt; letter-spacing: 2px;")
        score_title.setAlignment(Qt.AlignCenter)

        self._score_lbl = QLabel("—")
        self._score_lbl.setStyleSheet("color: #c9d1d9; font-size: 20pt; font-weight: bold;")
        self._score_lbl.setAlignment(Qt.AlignCenter)
        self._score_lbl.setWordWrap(True)

        score_layout.addStretch()
        score_layout.addWidget(score_title)
        score_layout.addWidget(self._score_lbl)
        score_layout.addStretch()
        results_row.addWidget(self._score_frame)

        # Right: Info cards grid
        info_frame = QFrame()
        info_frame.setObjectName("panel")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_layout.setSpacing(8)

        info_title = QLabel("Analysis Details")
        info_title.setStyleSheet("color: #00e5ff; font-size: 10pt; font-weight: bold;")
        info_layout.addWidget(info_title)

        grid = QGridLayout()
        grid.setSpacing(8)

        card_defs = [
            ("format",      "Format Valid",       "—"),
            ("username",    "Username",           "—"),
            ("domain",      "Domain",             "—"),
            ("domain_dns",  "Domain Resolves",    "—"),
            ("mx",          "MX Records",         "—"),
            ("disposable",  "Disposable Email",   "—"),
        ]

        for i, (key, label, default) in enumerate(card_defs):
            card = InfoCard(label, default)
            self._info_cards[key] = card
            grid.addWidget(card, i // 2, i % 2)

        info_layout.addLayout(grid)

        # Issues
        issues_lbl = QLabel("Issues / Warnings")
        issues_lbl.setStyleSheet("color: #00e5ff; font-size: 9pt; font-weight: bold; margin-top: 8px;")
        info_layout.addWidget(issues_lbl)

        self._issues_text = QTextEdit()
        self._issues_text.setObjectName("terminalOutput")
        self._issues_text.setReadOnly(True)
        self._issues_text.setMaximumHeight(100)
        info_layout.addWidget(self._issues_text)

        results_row.addWidget(info_frame, 1)
        root.addLayout(results_row)

        # ── Log ───────────────────────────────────────────────────────
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout(log_group)
        self._log_text = QTextEdit()
        self._log_text.setObjectName("terminalOutput")
        self._log_text.setReadOnly(True)
        self._log_text.setMaximumHeight(130)
        log_layout.addWidget(self._log_text)
        root.addWidget(log_group)

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def _start_check(self):
        email = self._email_input.text().strip()
        if not email:
            return

        self._reset_cards()
        self._issues_text.clear()
        self._log_text.clear()
        self._progress.setValue(20)
        self._btn_check.setEnabled(False)

        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Analyzing…")

        self._worker = EmailCheckWorker(email)
        self._worker.log_message.connect(self._log)
        self._worker.result_ready.connect(self._show_results)
        self._worker.error.connect(lambda e: self._log(
            f"<span style='color:#ff4d4d'>[ERR] {e}</span>"
        ))
        self._worker.finished.connect(self._on_done)
        self._worker.start()
        session_logger.info(f"Email check started: {email}")

    def _clear(self):
        self._email_input.clear()
        self._reset_cards()
        self._issues_text.clear()
        self._log_text.clear()
        self._progress.setValue(0)
        self._score_lbl.setText("—")
        self._score_lbl.setStyleSheet("color: #c9d1d9; font-size: 20pt; font-weight: bold;")

    def _reset_cards(self):
        for card in self._info_cards.values():
            card.set_value("—")

    @pyqtSlot(dict)
    def _show_results(self, result: dict):
        self._last_result = result
        self._progress.setValue(100)

        score = result.get("score", "UNKNOWN")
        color_map = {
            "VALID":      "#00ff9f",
            "SUSPICIOUS": "#ffa500",
            "INVALID":    "#ff4d4d",
            "UNKNOWN":    "#c9d1d9",
        }
        color = color_map.get(score, "#c9d1d9")
        self._score_lbl.setText(score)
        self._score_lbl.setStyleSheet(
            f"color: {color}; font-size: 20pt; font-weight: bold;"
        )

        yes_no = lambda b, good="#00ff9f", bad="#ff4d4d": (
            ("✔ Yes", good) if b else ("✖ No", bad)
        )

        self._info_cards["format"].set_value(
            *yes_no(result.get("valid_format"))
        )
        self._info_cards["username"].set_value(
            result.get("username", "—"), "#c9d1d9"
        )
        self._info_cards["domain"].set_value(
            result.get("domain", "—"), "#00e5ff"
        )
        self._info_cards["domain_dns"].set_value(
            *yes_no(result.get("domain_resolves"))
        )

        mx = result.get("mx_records", [])
        self._info_cards["mx"].set_value(
            f"✔ {len(mx)} record(s)" if mx else "✖ None found",
            "#00ff9f" if mx else "#ff4d4d",
        )

        disp = result.get("is_disposable", False)
        self._info_cards["disposable"].set_value(
            *yes_no(disp, good="#ff4d4d", bad="#00ff9f")
        )

        # Issues
        issues = result.get("issues", [])
        if issues:
            for issue in issues:
                self._issues_text.append(
                    f"<span style='color:#ffa500'>⚠  {issue}</span>"
                )
        else:
            self._issues_text.append(
                "<span style='color:#00ff9f'>✔  No issues detected.</span>"
            )

    @pyqtSlot()
    def _on_done(self):
        self._btn_check.setEnabled(True)
        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Complete")
        session_logger.info("Email check completed.")

    @pyqtSlot(str)
    def _log(self, msg: str):
        clean = msg.replace("\n", "<br>")
        if "<span" not in clean:
            if "[ERR]" in clean:
                clean = f"<span style='color:#ff4d4d'>{clean}</span>"
            elif "[OK]" in clean:
                clean = f"<span style='color:#00ff9f'>{clean}</span>"
            elif "[WARN]" in clean:
                clean = f"<span style='color:#ffa500'>{clean}</span>"
            else:
                clean = f"<span style='color:#8b949e'>{clean}</span>"
        self._log_text.append(clean)
        sb = self._log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _export_json(self):
        if not self._last_result:
            return
        path = export_json(self._last_result, "email_intel")
        self._log(f"<span style='color:#00e5ff'>[EXPORT] JSON saved: {path}</span>")

    def _export_txt(self):
        if not self._last_result:
            return
        r = self._last_result
        lines = [
            f"Email         : {r.get('email')}",
            f"Status        : {r.get('score')}",
            f"Format Valid  : {r.get('valid_format')}",
            f"Username      : {r.get('username', 'N/A')}",
            f"Domain        : {r.get('domain', 'N/A')}",
            f"Domain Resolves: {r.get('domain_resolves')}",
            f"MX Records    : {', '.join(r.get('mx_records', [])) or 'None'}",
            f"Disposable    : {r.get('is_disposable')}",
            "",
            "Issues:",
        ]
        for issue in r.get("issues", ["None"]):
            lines.append(f"  - {issue}")
        path = export_txt(lines, "email_intel")
        self._log(f"<span style='color:#00e5ff'>[EXPORT] TXT saved: {path}</span>")
