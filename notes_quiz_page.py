from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

from supabase_client import get_quiz_notes_questions, set_note_hafal

class NotesQuizPage(QWidget):
    def __init__(self, user_id: int, dashboard=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard = dashboard

        self.notes = []
        self.idx = 0
        self.current = None
        self.answer_visible = False

        self.setWindowTitle("Quiz Hafalan Bebas")
        self.setup_ui()

        self.resize(900, 560)
        self.setMinimumSize(820, 520)

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

        title = QLabel("Quiz Hafalan Bebas")
        title.setObjectName("PageTitle")

        top.addWidget(btn_back)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch()
        layout.addLayout(top)

        btn_start = QPushButton("Mulai / Ulang")
        btn_start.setProperty("class", "primary")
        btn_start.clicked.connect(self.start_quiz)
        layout.addWidget(btn_start)

        self.lbl_title = QLabel("Klik Mulai untuk mulai.")
        self.lbl_title.setWordWrap(True)
        self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700;")

        self.lbl_answer = QLabel("")
        self.lbl_answer.setWordWrap(True)

        btn_show = QPushButton("Tampilkan Jawaban")
        btn_show.setProperty("class", "secondary")
        btn_show.clicked.connect(self.toggle_answer)

        btn_correct = QPushButton("Saya Benar (Hafal)")
        btn_wrong = QPushButton("Saya Salah")
        btn_next = QPushButton("Soal Berikutnya")

        btn_correct.setProperty("class", "primary")
        btn_wrong.setProperty("class", "secondary")
        btn_next.setProperty("class", "secondary")

        btn_correct.clicked.connect(self.mark_correct)
        btn_wrong.clicked.connect(self.mark_wrong)
        btn_next.clicked.connect(self.next_note)

        actions = QHBoxLayout()
        actions.addWidget(btn_show)
        actions.addStretch()
        actions.addWidget(btn_wrong)
        actions.addWidget(btn_correct)
        actions.addWidget(btn_next)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_answer)
        layout.addLayout(actions)
        layout.addStretch()

        self.setLayout(layout)

    def start_quiz(self):
        self.notes = get_quiz_notes_questions(self.user_id, limit=40, include_hafal=False)
        self.idx = 0
        self.current = None
        self.answer_visible = False

        if not self.notes:
            self.lbl_title.setText("Tidak ada hafalan (atau semuanya sudah hafal).")
            self.lbl_answer.setText("")
            return

        self.show_current()

    def show_current(self):
        if self.idx >= len(self.notes):
            self.lbl_title.setText("Selesai! Tidak ada soal lagi.")
            self.lbl_answer.setText("")
            self.current = None
            return

        self.current = self.notes[self.idx]
        self.answer_visible = False
        self.lbl_title.setText(f"[{self.idx+1}/{len(self.notes)}] Judul: {self.current.get('judul','')}")
        self.lbl_answer.setText("Jawaban disembunyikan. Klik 'Tampilkan Jawaban'.")

    def toggle_answer(self):
        if not self.current:
            return
        if not self.answer_visible:
            self.lbl_answer.setText(self.current.get("isi", ""))
            self.answer_visible = True
        else:
            self.lbl_answer.setText("Jawaban disembunyikan. Klik 'Tampilkan Jawaban'.")
            self.answer_visible = False

    def mark_correct(self):
        if not self.current:
            return
        set_note_hafal(int(self.current["id"]), True)
        QMessageBox.information(self, "OK", "Ditandai sudah hafal.")
        self.next_note()

    def mark_wrong(self):
        QMessageBox.information(self, "Info", "Tidak apa-apa. Lanjut soal berikutnya.")
        self.next_note()

    def next_note(self):
        if not self.notes:
            return
        self.idx += 1
        self.show_current()
