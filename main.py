import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from welcome_window import WelcomeWindow

# ==================================================
# QSS
# ==================================================
APP_STYLE = """
/* Base */
QWidget {
    background: #F6F0D7;
    color: #2F352B;
    font-size: 12px;
}
QLabel#PageTitle {
    font-size: 18px;
    font-weight: 700;
    color: #2F352B;
    padding: 6px 2px;
}
QLabel#SectionTitle {
    font-size: 13px;
    font-weight: 700;
    color: #2F352B;
    padding: 6px 2px;
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(137,152,109,0.65);
    border-radius: 10px;
    padding: 8px 10px;
    selection-background-color: rgba(156,171,132,0.6);
}
QTextEdit {
    min-height: 90px;
}
QComboBox::drop-down {
    border: 0px;
    width: 24px;
}
QComboBox QAbstractItemView {
    background: #F6F0D7;
    border: 1px solid rgba(137,152,109,0.65);
    selection-background-color: rgba(197,216,157,0.9);
}

/* Buttons */
QPushButton {
    background: rgba(255,255,255,0.65);
    border: 1px solid rgba(137,152,109,0.65);
    border-radius: 12px;
    padding: 9px 12px;
    font-weight: 600;
}
QPushButton:hover {
    background: rgba(197,216,157,0.55);
}
QPushButton:pressed {
    background: rgba(156,171,132,0.55);
}
QPushButton[class="primary"] {
    background: #89986D;
    border: 1px solid #89986D;
    color: #F6F0D7;
}
QPushButton[class="primary"]:hover { background: #7C8A61; }
QPushButton[class="secondary"] {
    background: #C5D89D;
    border: 1px solid #9CAB84;
    color: #2F352B;
}
QPushButton[class="danger"] {
    background: #8A4E4E;
    border: 1px solid #8A4E4E;
    color: #F6F0D7;
}
QPushButton[class="ghost"] {
    background: transparent;
    border: 1px solid rgba(137,152,109,0.55);
    color: #2F352B;
}

/* Tables */
QTableWidget {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(137,152,109,0.65);
    border-radius: 12px;
    gridline-color: rgba(137,152,109,0.35);
    selection-background-color: rgba(197,216,157,0.75);
    selection-color: #2F352B;
}
QHeaderView::section {
    background: rgba(156,171,132,0.55);
    border: 0px;
    padding: 8px 10px;
    font-weight: 700;
    color: #2F352B;
}
QTableCornerButton::section {
    background: rgba(156,171,132,0.55);
    border: 0px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid rgba(137,152,109,0.65);
    border-radius: 12px;
    top: -1px;
    background: rgba(255,255,255,0.35);
}
QTabBar::tab {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(137,152,109,0.55);
    border-bottom: 0px;
    padding: 8px 12px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 6px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: rgba(197,216,157,0.75);
    border-color: rgba(137,152,109,0.65);
}
"""

def main():
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(APP_STYLE)

    w = WelcomeWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
