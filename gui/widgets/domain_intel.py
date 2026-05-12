"""
gui/widgets/domain_intel.py
Domain Intelligence panel – WHOIS, DNS, IP resolution, subdomain scan.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QCheckBox, QTabWidget, QTextEdit,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSplitter, QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QBrush

from utils.workers import DomainLookupWorker
from utils.logger import session_logger
from utils.exporter import export_json, export_txt


class DomainIntelWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: DomainLookupWorker | None = None
        self._last_result: dict = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("Domain Intelligence")
        title.setObjectName("sectionHeader")
        root.addWidget(title)

        # ── Config ────────────────────────────────────────────────────
        config = QGroupBox("Target Domain")
        cfg_layout = QVBoxLayout(config)

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        lbl = QLabel("Domain:")
        lbl.setObjectName("fieldLabel")
        lbl.setFixedWidth(80)
        self._domain_input = QLineEdit()
        self._domain_input.setPlaceholderText("e.g.  example.com")
        self._domain_input.returnPressed.connect(self._start_lookup)

        self._chk_subdomain = QCheckBox("Subdomain scan")
        self._chk_subdomain.setChecked(True)

        self._btn_lookup = QPushButton("▶  Lookup")
        self._btn_lookup.setObjectName("primaryButton")
        self._btn_lookup.setFixedHeight(36)
        self._btn_lookup.setFixedWidth(120)
        self._btn_lookup.clicked.connect(self._start_lookup)

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

        row1.addWidget(lbl)
        row1.addWidget(self._domain_input, 1)
        row1.addWidget(self._chk_subdomain)
        row1.addWidget(self._btn_lookup)
        row1.addWidget(self._btn_clear)
        row1.addWidget(btn_export_json)
        row1.addWidget(btn_export_txt)
        cfg_layout.addLayout(row1)
        root.addWidget(config)

        # ── Progress ──────────────────────────────────────────────────
        self._progress = QProgressBar()
        self._progress.setValue(0)
        root.addWidget(self._progress)

        # ── Tabs ──────────────────────────────────────────────────────
        tabs = QTabWidget()

        # WHOIS tab
        self._whois_text = QTextEdit()
        self._whois_text.setObjectName("terminalOutput")
        self._whois_text.setReadOnly(True)
        tabs.addTab(self._whois_text, "WHOIS")

        # DNS tab
        self._dns_text = QTextEdit()
        self._dns_text.setObjectName("terminalOutput")
        self._dns_text.setReadOnly(True)
        tabs.addTab(self._dns_text, "DNS Records")

        # Subdomains tab
        self._subdomain_table = QTableWidget(0, 2)
        self._subdomain_table.setHorizontalHeaderLabels(["Subdomain", "IP Address"])
        self._subdomain_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._subdomain_table.verticalHeader().setVisible(False)
        self._subdomain_table.setAlternatingRowColors(True)
        self._subdomain_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabs.addTab(self._subdomain_table, "Subdomains")

        # Terminal log tab
        self._log_text = QTextEdit()
        self._log_text.setObjectName("terminalOutput")
        self._log_text.setReadOnly(True)
        tabs.addTab(self._log_text, "Log")

        root.addWidget(tabs, 1)

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def _start_lookup(self):
        domain = self._domain_input.text().strip()
        if not domain:
            return

        self._clear_results()
        self._btn_lookup.setEnabled(False)
        self._progress.setValue(0)

        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Analyzing…")

        self._worker = DomainLookupWorker(
            domain=domain,
            do_subdomain=self._chk_subdomain.isChecked(),
        )
        self._worker.log_message.connect(self._log)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.result_ready.connect(self._show_results)
        self._worker.error.connect(lambda e: self._log(
            f"<span style='color:#ff4d4d'>[ERR] {e}</span>"
        ))
        self._worker.finished.connect(self._on_done)
        self._worker.start()
        session_logger.info(f"Domain lookup started: {domain}")

    def _clear(self):
        self._domain_input.clear()
        self._clear_results()
        self._progress.setValue(0)

    def _clear_results(self):
        self._whois_text.clear()
        self._dns_text.clear()
        self._log_text.clear()
        self._subdomain_table.setRowCount(0)
        self._last_result = {}

    @pyqtSlot(dict)
    def _show_results(self, result: dict):
        self._last_result = result

        # WHOIS
        whois = result.get("whois", {})
        self._whois_text.clear()
        if "error" in whois:
            self._whois_text.append(
                f"<span style='color:#ff4d4d'>[ERR] {whois['error']}</span>"
            )
        else:
            age = whois.get("domain_age_days", -1)
            age_str = f"{age} days" if age >= 0 else "N/A"
            age_color = "#ff4d4d" if 0 <= age < 30 else "#00ff9f"

            fields = [
                ("Domain",       result.get("domain", "N/A"), "#00e5ff"),
                ("IP Address",   result.get("ip", "N/A"),     "#00e5ff"),
                ("Registrar",    whois.get("registrar", "N/A"),    "#c9d1d9"),
                ("Country",      whois.get("country", "N/A"),      "#c9d1d9"),
                ("Organization", whois.get("org", "N/A"),          "#c9d1d9"),
                ("Created",      whois.get("creation_date", "N/A"), "#c9d1d9"),
                ("Expires",      whois.get("expiration_date", "N/A"), "#c9d1d9"),
                ("Domain Age",   age_str, age_color),
                ("Status",       ", ".join(whois.get("status", [])[:2]) or "N/A", "#c9d1d9"),
            ]
            for field, value, color in fields:
                self._whois_text.append(
                    f"<span style='color:#8b949e'>{field:<15}</span>"
                    f"<span style='color:{color}'>{value}</span>"
                )

        # DNS
        dns = result.get("dns", {})
        self._dns_text.clear()
        if "error" in dns:
            self._dns_text.append(
                f"<span style='color:#ff4d4d'>[ERR] {dns['error']}</span>"
            )
        else:
            for rtype, records in dns.items():
                self._dns_text.append(
                    f"<span style='color:#00e5ff; font-weight:bold'>[{rtype}]</span>"
                )
                if records:
                    for rec in records:
                        self._dns_text.append(
                            f"  <span style='color:#00ff9f'>  {rec}</span>"
                        )
                else:
                    self._dns_text.append(
                        "  <span style='color:#484f58'>  (no records)</span>"
                    )
                self._dns_text.append("")

        # Subdomains
        subdomains = result.get("subdomains", [])
        self._subdomain_table.setRowCount(0)
        for sub in subdomains:
            row = self._subdomain_table.rowCount()
            self._subdomain_table.insertRow(row)
            sub_item = QTableWidgetItem(sub.get("subdomain", ""))
            sub_item.setForeground(QBrush(QColor("#00e5ff")))
            ip_item = QTableWidgetItem(sub.get("ip", ""))
            ip_item.setForeground(QBrush(QColor("#00ff9f")))
            self._subdomain_table.setItem(row, 0, sub_item)
            self._subdomain_table.setItem(row, 1, ip_item)

    @pyqtSlot()
    def _on_done(self):
        self._btn_lookup.setEnabled(True)
        self._progress.setValue(100)
        main_win = self.parent()
        if main_win and hasattr(main_win, "set_status"):
            main_win.set_status("Complete")
        session_logger.info("Domain lookup completed.")

    @pyqtSlot(str)
    def _log(self, msg: str):
        clean = msg.replace("\n", "<br>")
        if "<span" not in clean:
            if "[ERR]" in clean:
                clean = f"<span style='color:#ff4d4d'>{clean}</span>"
            elif "[OK]" in clean or "[FOUND]" in clean:
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
        path = export_json(self._last_result, "domain_intel")
        self._log(f"<span style='color:#00e5ff'>[EXPORT] JSON saved: {path}</span>")

    def _export_txt(self):
        if not self._last_result:
            return
        r = self._last_result
        whois = r.get("whois", {})
        lines = [
            f"Domain     : {r.get('domain')}",
            f"IP         : {r.get('ip', 'N/A')}",
            f"Registrar  : {whois.get('registrar', 'N/A')}",
            f"Created    : {whois.get('creation_date', 'N/A')}",
            f"Age (days) : {whois.get('domain_age_days', 'N/A')}",
            "",
            "DNS Records:",
        ]
        for rtype, recs in r.get("dns", {}).items():
            lines.append(f"  [{rtype}] {', '.join(recs) if recs else 'none'}")
        lines.append("")
        lines.append("Subdomains Found:")
        for sub in r.get("subdomains", []):
            lines.append(f"  {sub.get('subdomain')} → {sub.get('ip')}")
        path = export_txt(lines, "domain_intel")
        self._log(f"<span style='color:#00e5ff'>[EXPORT] TXT saved: {path}</span>")
