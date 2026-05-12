"""
Global QSS Stylesheet for Investigator X
Dark cyber theme with neon green/cyan accents
"""

GLOBAL_STYLESHEET = """
/* ============================================================
   BASE & WINDOW
   ============================================================ */
QMainWindow, QDialog {
    background-color: #0d1117;
    color: #c9d1d9;
}

QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
}

/* ============================================================
   STACKED / PANEL WIDGETS
   ============================================================ */
QStackedWidget {
    background-color: #0d1117;
}

QFrame#panel {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
}

/* ============================================================
   SIDEBAR
   ============================================================ */
QFrame#sidebar {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
    min-width: 200px;
    max-width: 200px;
}

QPushButton#navButton {
    background-color: transparent;
    color: #8b949e;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    text-align: left;
    padding: 12px 16px;
    font-size: 10pt;
    font-family: 'Consolas', 'Courier New', monospace;
    font-weight: normal;
}

QPushButton#navButton:hover {
    background-color: #161b22;
    color: #00e5ff;
    border-left: 3px solid #00e5ff;
}

QPushButton#navButtonActive {
    background-color: #161b22;
    color: #00ff9f;
    border: none;
    border-left: 3px solid #00ff9f;
    border-radius: 0px;
    text-align: left;
    padding: 12px 16px;
    font-size: 10pt;
    font-family: 'Consolas', 'Courier New', monospace;
    font-weight: bold;
}

/* ============================================================
   HEADER
   ============================================================ */
QFrame#header {
    background-color: #161b22;
    border-bottom: 1px solid #21262d;
    min-height: 70px;
    max-height: 70px;
}

QLabel#titleLabel {
    color: #00ff9f;
    font-size: 20pt;
    font-weight: bold;
    font-family: 'Consolas', 'Courier New', monospace;
    letter-spacing: 2px;
}

QLabel#subtitleLabel {
    color: #00e5ff;
    font-size: 9pt;
    font-family: 'Consolas', 'Courier New', monospace;
    letter-spacing: 1px;
}

QLabel#disclaimerLabel {
    color: #6e7681;
    font-size: 8pt;
    font-style: italic;
}

/* ============================================================
   BUTTONS
   ============================================================ */
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 20px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
}

QPushButton:hover {
    background-color: #2d333b;
    border: 1px solid #00e5ff;
    color: #00e5ff;
}

QPushButton:pressed {
    background-color: #161b22;
    border: 1px solid #00ff9f;
    color: #00ff9f;
}

QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border: 1px solid #21262d;
}

QPushButton#primaryButton {
    background-color: #003d2b;
    color: #00ff9f;
    border: 1px solid #00ff9f;
    border-radius: 6px;
    padding: 8px 24px;
    font-weight: bold;
    font-size: 10pt;
}

QPushButton#primaryButton:hover {
    background-color: #00ff9f;
    color: #0d1117;
    border: 1px solid #00ff9f;
}

QPushButton#primaryButton:pressed {
    background-color: #00cc7a;
    color: #0d1117;
}

QPushButton#primaryButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border: 1px solid #21262d;
}

QPushButton#dangerButton {
    background-color: #3d0000;
    color: #ff4d4d;
    border: 1px solid #ff4d4d;
    border-radius: 6px;
    padding: 8px 24px;
    font-weight: bold;
}

QPushButton#dangerButton:hover {
    background-color: #ff4d4d;
    color: #0d1117;
}

QPushButton#exportButton {
    background-color: #00214d;
    color: #00e5ff;
    border: 1px solid #00e5ff;
    border-radius: 6px;
    padding: 8px 20px;
}

QPushButton#exportButton:hover {
    background-color: #00e5ff;
    color: #0d1117;
}

/* ============================================================
   LINE EDITS / INPUTS
   ============================================================ */
QLineEdit {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 10pt;
    selection-background-color: #00ff9f;
    selection-color: #0d1117;
}

QLineEdit:focus {
    border: 1px solid #00e5ff;
    background-color: #1c2128;
}

QLineEdit:disabled {
    color: #484f58;
    background-color: #161b22;
}

/* ============================================================
   COMBO BOX
   ============================================================ */
QComboBox {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 12px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QComboBox:hover {
    border: 1px solid #00e5ff;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    selection-background-color: #21262d;
    selection-color: #00ff9f;
}

/* ============================================================
   SPIN BOX
   ============================================================ */
QSpinBox {
    background-color: #161b22;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    font-family: 'Consolas', 'Courier New', monospace;
}

QSpinBox:focus {
    border: 1px solid #00e5ff;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #21262d;
    border: none;
    width: 18px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #30363d;
}

/* ============================================================
   TEXT EDIT (TERMINAL OUTPUT)
   ============================================================ */
QTextEdit {
    background-color: #0a0e14;
    color: #00ff9f;
    border: 1px solid #21262d;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    padding: 8px;
    selection-background-color: #21262d;
}

QTextEdit#terminalOutput {
    background-color: #080c10;
    color: #00ff9f;
    border: 1px solid #1a4a3a;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    line-height: 1.4;
}

/* ============================================================
   TABLE WIDGET
   ============================================================ */
QTableWidget {
    background-color: #161b22;
    color: #c9d1d9;
    gridline-color: #21262d;
    border: 1px solid #21262d;
    border-radius: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
    alternate-background-color: #1c2128;
}

QTableWidget::item {
    padding: 6px 10px;
    border: none;
}

QTableWidget::item:selected {
    background-color: #21262d;
    color: #00e5ff;
}

QHeaderView::section {
    background-color: #21262d;
    color: #00ff9f;
    border: none;
    border-right: 1px solid #30363d;
    border-bottom: 1px solid #30363d;
    padding: 8px 10px;
    font-weight: bold;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
}

QHeaderView::section:hover {
    background-color: #2d333b;
}

/* ============================================================
   SCROLL BAR
   ============================================================ */
QScrollBar:vertical {
    background-color: #0d1117;
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00e5ff;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
}

QScrollBar:horizontal {
    background-color: #0d1117;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00e5ff;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

/* ============================================================
   PROGRESS BAR
   ============================================================ */
QProgressBar {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 4px;
    text-align: center;
    color: #c9d1d9;
    font-size: 8pt;
    min-height: 16px;
    max-height: 16px;
}

QProgressBar::chunk {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #00664d, stop:1 #00ff9f
    );
    border-radius: 3px;
}

/* ============================================================
   STATUS BAR
   ============================================================ */
QStatusBar {
    background-color: #161b22;
    color: #6e7681;
    border-top: 1px solid #21262d;
    font-size: 8pt;
}

QStatusBar::item {
    border: none;
}

QLabel#statusReady {
    color: #00ff9f;
    font-size: 8pt;
}

QLabel#statusBusy {
    color: #ffa500;
    font-size: 8pt;
}

QLabel#statusDone {
    color: #00e5ff;
    font-size: 8pt;
}

/* ============================================================
   LABELS
   ============================================================ */
QLabel#sectionHeader {
    color: #00ff9f;
    font-size: 13pt;
    font-weight: bold;
    border-bottom: 1px solid #21262d;
    padding-bottom: 6px;
}

QLabel#fieldLabel {
    color: #8b949e;
    font-size: 9pt;
}

QLabel#riskLow {
    color: #00ff9f;
    font-weight: bold;
    font-size: 11pt;
}

QLabel#riskMedium {
    color: #ffa500;
    font-weight: bold;
    font-size: 11pt;
}

QLabel#riskHigh {
    color: #ff4d4d;
    font-weight: bold;
    font-size: 11pt;
}

/* ============================================================
   GROUP BOX
   ============================================================ */
QGroupBox {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-top: 12px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    color: #8b949e;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    color: #00e5ff;
    font-size: 9pt;
    font-weight: bold;
}

/* ============================================================
   CHECKBOX
   ============================================================ */
QCheckBox {
    color: #c9d1d9;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #30363d;
    border-radius: 3px;
    background-color: #161b22;
}

QCheckBox::indicator:checked {
    background-color: #00ff9f;
    border: 1px solid #00ff9f;
}

QCheckBox::indicator:hover {
    border: 1px solid #00e5ff;
}

/* ============================================================
   SPLITTER
   ============================================================ */
QSplitter::handle {
    background-color: #21262d;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

/* ============================================================
   TAB WIDGET
   ============================================================ */
QTabWidget::pane {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 0 6px 6px 6px;
}

QTabBar::tab {
    background-color: #0d1117;
    color: #8b949e;
    border: 1px solid #21262d;
    border-bottom: none;
    padding: 8px 16px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 9pt;
}

QTabBar::tab:selected {
    background-color: #161b22;
    color: #00ff9f;
    border-top: 2px solid #00ff9f;
}

QTabBar::tab:hover {
    color: #00e5ff;
    background-color: #1c2128;
}

/* ============================================================
   TOOLTIP
   ============================================================ */
QToolTip {
    background-color: #1c2128;
    color: #c9d1d9;
    border: 1px solid #30363d;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 8pt;
    padding: 4px 8px;
}

/* ============================================================
   DASHBOARD STAT CARDS
   ============================================================ */
QFrame#statCard {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
}

QFrame#statCard:hover {
    border: 1px solid #00e5ff;
}

QLabel#statValue {
    color: #00ff9f;
    font-size: 22pt;
    font-weight: bold;
}

QLabel#statTitle {
    color: #8b949e;
    font-size: 8pt;
    letter-spacing: 1px;
}

QLabel#statIcon {
    color: #00e5ff;
    font-size: 20pt;
}
"""
