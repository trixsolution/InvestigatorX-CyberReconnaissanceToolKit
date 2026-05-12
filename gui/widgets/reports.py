"""
gui/widgets/reports.py
Reports panel – browse saved reports, preview content, open files.
"""

import os
import json

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QGroupBox, QSplitter, QAbstractItemView, QFileDialog,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QColor, QBrush

from utils.exporter import list_reports, REPORTS_DIR
from utils.logger import session_logger


class ReportsWidget(QWidget):

    HEADERS = ["Filename", "Size", "Last Modified"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)

        title = QLabel("Reports")
        title.setObjectName("sectionHeader")
        root.addWidget(title)

        # ── Toolbar ───────────────────────────────────────────────────
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self._btn_refresh = QPushButton("↻  Refresh")
        self._btn_refresh.setFixedHeight(34)
        self._btn_refresh.clicked.connect(self._refresh_list)

        self._btn_open_dir = QPushButton("📁  Open Reports Folder")
        self._btn_open_dir.setObjectName("exportButton")
        self._btn_open_dir.setFixedHeight(34)
        self._btn_open_dir.clicked.connect(self._open_reports_dir)

        self._btn_delete = QPushButton("🗑  Delete Selected")
        self._btn_delete.setObjectName("dangerButton")
        self._btn_delete.setFixedHeight(34)
        self._btn_delete.clicked.connect(self._delete_selected)

        info_lbl = QLabel(f"Reports saved to: {REPORTS_DIR}")
        info_lbl.setStyleSheet("color: #6e7681; font-size: 8pt;")

        toolbar.addWidget(self._btn_refresh)
        toolbar.addWidget(self._btn_open_dir)
        toolbar.addWidget(self._btn_delete)
        toolbar.addStretch()
        toolbar.addWidget(info_lbl)
        root.addLayout(toolbar)

        # ── Splitter: file list + preview ─────────────────────────────
        splitter = QSplitter(Qt.Vertical)

        # File list
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(self.HEADERS)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.itemSelectionChanged.connect(self._on_selection_change)
        self._table.setMinimumHeight(200)
        splitter.addWidget(self._table)

        # Preview
        preview_frame = QFrame()
        preview_frame.setObjectName("panel")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(8, 8, 8, 8)
        preview_layout.setSpacing(4)

        preview_hdr = QHBoxLayout()
        preview_title = QLabel("File Preview")
        preview_title.setStyleSheet("color: #00e5ff; font-size: 9pt; font-weight: bold;")
        preview_hdr.addWidget(preview_title)
        preview_hdr.addStretch()
        preview_layout.addLayout(preview_hdr)

        self._preview = QTextEdit()
        self._preview.setObjectName("terminalOutput")
        self._preview.setReadOnly(True)
        preview_layout.addWidget(self._preview)
        splitter.addWidget(preview_frame)

        splitter.setSizes([300, 300])
        root.addWidget(splitter, 1)

        # ── Session log ───────────────────────────────────────────────
        log_group = QGroupBox("Session Log")
        log_layout = QVBoxLayout(log_group)

        log_hdr = QHBoxLayout()
        self._btn_view_log = QPushButton("View Current Session Log")
        self._btn_view_log.setObjectName("exportButton")
        self._btn_view_log.setFixedHeight(28)
        self._btn_view_log.clicked.connect(self._view_session_log)
        log_hdr.addStretch()
        log_hdr.addWidget(self._btn_view_log)
        log_layout.addLayout(log_hdr)

        self._log_text = QTextEdit()
        self._log_text.setObjectName("terminalOutput")
        self._log_text.setReadOnly(True)
        self._log_text.setMaximumHeight(120)
        log_layout.addWidget(self._log_text)
        root.addWidget(log_group)

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def _refresh_list(self):
        self._table.setRowCount(0)
        reports = list_reports()

        if not reports:
            self._table.insertRow(0)
            item = QTableWidgetItem("No reports found. Run a scan to generate one.")
            item.setForeground(QBrush(QColor("#484f58")))
            self._table.setItem(0, 0, item)
            return

        for report in reports:
            row = self._table.rowCount()
            self._table.insertRow(row)

            name_item = QTableWidgetItem(report["name"])
            size_item = QTableWidgetItem(self._fmt_size(report["size"]))
            date_item = QTableWidgetItem(report["modified"])

            if report["name"].endswith(".json"):
                name_item.setForeground(QBrush(QColor("#00e5ff")))
            else:
                name_item.setForeground(QBrush(QColor("#ffa500")))

            name_item.setData(Qt.UserRole, report["path"])

            self._table.setItem(row, 0, name_item)
            self._table.setItem(row, 1, size_item)
            self._table.setItem(row, 2, date_item)

    def _on_selection_change(self):
        rows = self._table.selectedItems()
        if not rows:
            return
        path = self._table.item(self._table.currentRow(), 0).data(Qt.UserRole)
        if not path or not os.path.isfile(path):
            return
        self._preview_file(path)

    def _preview_file(self, path: str):
        self._preview.clear()
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(8192)  # preview first 8 KB

            if path.endswith(".json"):
                try:
                    parsed = json.loads(content)
                    pretty = json.dumps(parsed, indent=2, default=str)
                    # Syntax-highlight JSON keys
                    for line in pretty.splitlines():
                        if '":' in line:
                            key, _, rest = line.partition('":')
                            self._preview.append(
                                f"<span style='color:#00e5ff'>{key}\":</span>"
                                f"<span style='color:#c9d1d9'>{rest}</span>"
                            )
                        else:
                            self._preview.append(
                                f"<span style='color:#c9d1d9'>{line}</span>"
                            )
                except json.JSONDecodeError:
                    self._preview.setPlainText(content)
            else:
                for line in content.splitlines():
                    color = "#00ff9f" if line.startswith("  [") else "#c9d1d9"
                    self._preview.append(
                        f"<span style='color:{color}'>{line}</span>"
                    )

        except Exception as e:
            self._preview.append(
                f"<span style='color:#ff4d4d'>[ERR] Cannot read file: {e}</span>"
            )

    def _open_reports_dir(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)
        os.startfile(REPORTS_DIR)

    def _delete_selected(self):
        row = self._table.currentRow()
        if row < 0:
            return
        path_item = self._table.item(row, 0)
        if not path_item:
            return
        path = path_item.data(Qt.UserRole)
        if path and os.path.isfile(path):
            try:
                os.remove(path)
                session_logger.info(f"Deleted report: {path}")
            except Exception as e:
                session_logger.error(f"Delete failed: {e}")
        self._refresh_list()
        self._preview.clear()

    def _view_session_log(self):
        log_path = session_logger.get_log_path()
        if os.path.isfile(log_path):
            self._preview_file(log_path)
            self._log_text.clear()
            entries = session_logger.get_entries()
            for entry in entries[-50:]:  # last 50 entries
                color = (
                    "#ff4d4d" if "[ERR ]" in entry
                    else "#ffa500" if "[WARN]" in entry
                    else "#00ff9f"
                )
                self._log_text.append(
                    f"<span style='color:{color}'>{entry}</span>"
                )

    @staticmethod
    def _fmt_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.1f} MB"
