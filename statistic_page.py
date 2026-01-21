from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt

from supabase_client import (
    count_folders,
    count_notes, count_notes_hafal,
    count_vocab, count_vocab_hafal,
    count_vocab_translations,
    count_reminders, count_reminders_done,
    count_vocab_by_language
)

class StatisticPage(QWidget):
    def __init__(self, user_id: int, dashboard=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard = dashboard

        self.setWindowTitle("Statistik")
        self.setup_ui()
        self.refresh()

        self.resize(760, 520)
        self.setMinimumSize(700, 480)

    def go_back(self):
        if self.dashboard is not None:
            self.dashboard.show()
        self.close()

    def closeEvent(self, event):
        if self.dashboard is not None:
            self.dashboard.show()
        event.accept()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setProperty("class", "ghost")
        btn_back.clicked.connect(self.go_back)

        title = QLabel("Statistik")
        title.setObjectName("PageTitle")

        top.addWidget(btn_back)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch()

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setProperty("class", "secondary")
        btn_refresh.clicked.connect(self.refresh)

        layout.addLayout(top)
        layout.addWidget(btn_refresh)

        self.lbl = QLabel("-")
        self.lbl.setWordWrap(True)
        self.lbl.setStyleSheet("background: rgba(255,255,255,0.45); border: 1px solid rgba(137,152,109,0.55); border-radius: 12px; padding: 12px;")
        layout.addWidget(self.lbl)
        layout.addStretch()

        self.setLayout(layout)

    def refresh(self):
        folders = count_folders(self.user_id)

        notes_total = count_notes(self.user_id)
        notes_hafal = count_notes_hafal(self.user_id)

        vocab_total = count_vocab(self.user_id)
        vocab_hafal = count_vocab_hafal(self.user_id)
        trans_total = count_vocab_translations(self.user_id)
        by_lang = count_vocab_by_language(self.user_id)

        rem_total = count_reminders(self.user_id)
        rem_done = count_reminders_done(self.user_id)

        text = []
        text.append(f"Folder: {folders}")
        text.append("")
        text.append(f"Hafalan Bebas: {notes_total} total | {notes_hafal} sudah hafal | {notes_total-notes_hafal} belum")
        text.append(f"Kosakata (konsep): {vocab_total} total | {vocab_hafal} sudah hafal | {vocab_total-vocab_hafal} belum")
        text.append(f"Jumlah translation (semua bahasa): {trans_total}")
        text.append("Rincian translation per bahasa:")
        for k, v in by_lang.items():
            text.append(f"- {k}: {v}")
        text.append("")
        text.append(f"Reminder: {rem_total} total | {rem_done} selesai | {rem_total-rem_done} belum")

        self.lbl.setText("\n".join(text))
