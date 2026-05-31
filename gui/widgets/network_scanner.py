"""
gui/widgets/network_scanner.py
Network Scanner panel – ping sweep + port scanning UI.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QGroupBox, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QProgressBar, QSplitter, QSizePolicy, QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSlot, QThread
from html import escape as html_escape
from PyQt5.QtGui import QColor, QBrush, QFont

from utils.workers import NetworkScanWorker
from utils.logger import session_logger
from utils.exporter import export_json, export_txt


class NetworkScannerWidget(QWidget):

    TABLE_HEADERS = ["IP Address", "Status", "Open Ports", "Services"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: NetworkScanWorker | None = None
        self._results: list[dict] = []
        self._build_ui()

    # ------------------------------------------------------------------ #
    # Build
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        # Title
        title = QLabel("Network Scanner")
        title.setObjectName("sectionHeader")
        root.addWidget(title)

        # ── Config panel ──────────────────────────────────────────────
        config = QGroupBox("Scan Configuration")
        config_layout = QVBoxLayout(config)
        config_layout.setSpacing(10)

        # Target input row
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        lbl_target = QLabel("Target (IP / CIDR):")
        lbl_target.setObjectName("fieldLabel")
        lbl_target.setFixedWidth(160)
        self._target_input = QLineEdit()
        self._target_input.setPlaceholderText("e.g.  192.168.1.1  or  192.168.1.0/24")
        row1.addWidget(lbl_target)
        row1.addWidget(self._target_input)
        config_layout.addLayout(row1)

        # Port mode row
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        lbl_port = QLabel("Port Scan Mode:")
        lbl_port.setObjectName("fieldLabel")
        lbl_port.setFixedWidth(160)
        self._port_mode = QComboBox()
        self._port_mode.addItems(["Top 20 Ports", "Custom Range", "Full (1-65535)"])
        self._port_mode.setFixedWidth(180)
        self._port_mode.currentIndexChanged.connect(self._on_port_mode_change)

        lbl_start = QLabel("Start:")
        lbl_start.setObjectName("fieldLabel")
        self._port_start = QSpinBox()
        self._port_start.setRange(1, 65535)
        self._port_start.setValue(1)
        self._port_start.setFixedWidth(90)
        self._port_start.setEnabled(False)

        lbl_end = QLabel("End:")
        lbl_end.setObjectName("fieldLabel")
        self._port_end = QSpinBox()
        self._port_end.setRange(1, 65535)
        self._port_end.setValue(1024)
        self._port_end.setFixedWidth(90)
        self._port_end.setEnabled(False)

        row2.addWidget(lbl_port)
        row2.addWidget(self._port_mode)
        row2.addSpacing(16)
        row2.addWidget(lbl_start)
        row2.addWidget(self._port_start)
        row2.addWidget(lbl_end)
        row2.addWidget(self._port_end)
        row2.addStretch()
        config_layout.addLayout(row2)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._btn_scan = QPushButton("▶  Start Scan")
        self._btn_scan.setObjectName("primaryButton")
        self._btn_scan.setFixedHeight(36)
        self._btn_scan.clicked.connect(self._start_scan)

        self._btn_stop = QPushButton("■  Stop")
        self._btn_stop.setObjectName("dangerButton")
        self._btn_stop.setFixedHeight(36)
        self._btn_stop.setEnabled(False)
        self._btn_stop.clicked.connect(self._stop_scan)

        self._btn_clear = QPushButton("⊘  Clear")
        self._btn_clear.setFixedHeight(36)
        self._btn_clear.clicked.connect(self._clear_results)

        btn_row.addWidget(self._btn_scan)
        btn_row.addWidget(self._btn_stop)
        btn_row.addWidget(self._btn_clear)
        btn_row.addStretch()
        config_layout.addLayout(btn_row)

        root.addWidget(config)

        # ── Progress bar ──────────────────────────────────────────────
        self._progress = QProgressBar()
        self._progress.setValue(0)
        self._progress.setTextVisible(True)
        root.addWidget(self._progress)

        # ── Splitter: results table + terminal ────────────────────────
        splitter = QSplitter(Qt.Vertical)

        # Results table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(self.TABLE_HEADERS)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSortingEnabled(True)
        splitter.addWidget(self._table)

        # Terminal output
        term_frame = QFrame()
        term_frame.setObjectName("panel")
        term_layout = QVBoxLayout(term_frame)
        term_layout.setContentsMargins(8, 8, 8, 8)
        term_layout.setSpacing(4)

        term_hdr = QHBoxLayout()
        term_title = QLabel("Terminal Output")
        term_title.setStyleSheet("color: #00e5ff; font-size: 8pt; font-weight: bold;")
        btn_export_json = QPushButton("Export JSON")
        btn_export_json.setObjectName("exportButton")
        btn_export_json.setFixedHeight(28)
        btn_export_json.clicked.connect(self._export_json)

        btn_export_txt = QPushButton("Export TXT")
        btn_export_txt.setObjectName("exportButton")
        btn_export_txt.setFixedHeight(28)
        btn_export_txt.clicked.connect(self._export_txt)

        term_hdr.addWidget(term_title)
        term_hdr.addStretch()
        term_hdr.addWidget(btn_export_json)
        term_hdr.addWidget(btn_export_txt)
        term_layout.addLayout(term_hdr)

        self._terminal = QTextEdit()
        self._terminal.setObjectName("terminalOutput")
        self._terminal.setReadOnly(True)
        self._terminal.setMinimumHeight(150)
        term_layout.addWidget(self._terminal)
        splitter.addWidget(term_frame)

        splitter.setSizes([350, 200])
        root.addWidget(splitter)

    # ------------------------------------------------------------------ #
    # Slots
    # ------------------------------------------------------------------ #
    @pyqtSlot(int)
    def _on_port_mode_change(self, idx: int):
        is_custom = idx == 1
        self._port_start.setEnabled(is_custom)
        self._port_end.setEnabled(is_custom)

    def _start_scan(self):
        target = self._target_input.text().strip()
        if not target:
            self._log("<span style='color:#ff4d4d'>[ERR] Please enter a target IP or CIDR.</span>")
            return

        mode_map = {0: "top", 1: "custom", 2: "full"}
        port_mode = mode_map[self._port_mode.currentIndex()]

        self._table.setRowCount(0)
        self._terminal.clear()
        self._results.clear()
        self._progress.setValue(0)
        self._btn_scan.setEnabled(False)
        self._btn_stop.setEnabled(True)

        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Scanning…")

        self._worker = NetworkScanWorker(
            target=target,
            port_mode=port_mode,
            custom_start=self._port_start.value(),
            custom_end=self._port_end.value(),
        )
        self._worker.log_message.connect(self._log)
        self._worker.host_found.connect(self._add_table_row)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.scan_complete.connect(self._on_scan_complete)
        self._worker.error.connect(lambda e: self._log(f"<span style='color:#ff4d4d'>[ERR] {e}</span>"))
        self._worker.finished.connect(self._on_worker_done)
        self._worker.start()

        session_logger.info(f"Network scan started: {target} / {port_mode}")

    def _stop_scan(self):
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._log("<span style='color:#ffa500'>[SCAN] Stop requested…</span>")

    def _clear_results(self):
        self._table.setRowCount(0)
        self._terminal.clear()
        self._results.clear()
        self._progress.setValue(0)

    @pyqtSlot(str, str, list, object)
    def _add_table_row(self, ip: str, status: str, ports: list, services):
        """Add one host result row to the table."""
        row = self._table.rowCount()
        self._table.insertRow(row)

        port_str = ", ".join(str(p) for p in ports) if ports else "—"
        service_str = ""
        if isinstance(services, dict):
            service_str = ", ".join(f"{p}/{s.split('[')[0].strip()}" for p, s in services.items())
        if not service_str:
            service_str = "—"

        ip_item = QTableWidgetItem(ip)
        status_item = QTableWidgetItem(status)
        ports_item = QTableWidgetItem(port_str)
        svc_item = QTableWidgetItem(service_str)

        if status == "UP":
            status_item.setForeground(QBrush(QColor("#00ff9f")))
        else:
            status_item.setForeground(QBrush(QColor("#ff4d4d")))

        if ports:
            ports_item.setForeground(QBrush(QColor("#ffa500")))

        for item in (ip_item, status_item, ports_item, svc_item):
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self._table.setItem(row, 0, ip_item)
        self._table.setItem(row, 1, status_item)
        self._table.setItem(row, 2, ports_item)
        self._table.setItem(row, 3, svc_item)

    @pyqtSlot(list)
    def _on_scan_complete(self, results: list):
        self._results = results

    @pyqtSlot()
    def _on_worker_done(self):
        self._btn_scan.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._progress.setValue(100)
        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Complete")
        session_logger.info("Network scan completed.")

    @pyqtSlot(str)
    def _log(self, msg: str):
        """Append a plain-text message to the terminal with colour coding.

        This method always receives PLAIN TEXT from the worker.  It HTML-escapes
        the content before inserting so that banners containing <, > or & never
        corrupt the Qt rich-text renderer.
        """
        escaped = html_escape(msg).replace("\n", "<br>")
        # colour by content (check the raw msg so tags don't interfere)
        if "[OPEN]" in msg:
            line = f"<span style='color:#00ff9f'>{escaped}</span>"
        elif "[ERR]" in msg or "DOWN" in msg:
            line = f"<span style='color:#ff4d4d'>{escaped}</span>"
        elif "[SCAN]" in msg or "[HOST]" in msg:
            line = f"<span style='color:#00e5ff'>{escaped}</span>"
        else:
            line = f"<span style='color:#c9d1d9'>{escaped}</span>"

        self._terminal.append(line)
        sb = self._terminal.verticalScrollBar()
        sb.setValue(sb.maximum())
        session_logger.info(msg)

    def _log_html(self, html: str):
        """Append a pre-built HTML snippet directly (used internally for export messages)."""
        self._terminal.append(html)
        sb = self._terminal.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _export_json(self):
        if not self._results:
            self._log_html("<span style='color:#ffa500'>[WARN] No results to export.</span>")
            return
        path = export_json(self._results, "network_scanner")
        self._log_html(f"<span style='color:#00e5ff'>[EXPORT] JSON saved: {html_escape(path)}</span>")
        session_logger.info(f"[EXPORT] JSON saved: {path}")

    def _export_txt(self):
        if not self._results:
            self._log_html("<span style='color:#ffa500'>[WARN] No results to export.</span>")
            return
        lines = []
        for r in self._results:
            lines.append(f"IP: {r['ip']}  |  Status: {r['status']}")
            if r["open_ports"]:
                lines.append(f"  Open Ports: {', '.join(str(p) for p in r['open_ports'])}")
                for port, svc in r.get("services", {}).items():
                    lines.append(f"    [{port}] {svc}")
            lines.append("")
        path = export_txt(lines, "network_scanner")
        self._log_html(f"<span style='color:#00e5ff'>[EXPORT] TXT saved: {html_escape(path)}</span>")
        session_logger.info(f"[EXPORT] TXT saved: {path}")
