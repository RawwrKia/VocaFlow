from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt

from supabase_client import (
    get_quiz_vocab_questions, set_vocab_hafal
)

class QuizPage(QWidget):
    def __init__(self, user_id: int, dashboard=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard = dashboard

        self.questions = []
        self.index = 0
        self.current = None
        self.score = 0
        self.total = 0

        self.setWindowTitle("Quiz Kosakata")
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

        title = QLabel("Quiz Kosakata")
        title.setObjectName("PageTitle")

        top.addWidget(btn_back)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch()
        layout.addLayout(top)

        self.cmb_from = QComboBox()
        self.cmb_to = QComboBox()
        langs = ["Acak", "Indonesia", "Inggris", "Mandarin", "Jepang"]
        self.cmb_from.addItems(langs)
        self.cmb_to.addItems(langs)

        btn_start = QPushButton("Mulai / Ulang")
        btn_start.setProperty("class", "primary")
        btn_start.clicked.connect(self.load_questions)

        pick = QHBoxLayout()
        pick.addWidget(QLabel("Dari"))
        pick.addWidget(self.cmb_from)
        pick.addWidget(QLabel("Ke"))
        pick.addWidget(self.cmb_to)
        pick.addStretch()
        pick.addWidget(btn_start)
        layout.addLayout(pick)

        self.lbl_info = QLabel("-")
        self.lbl_info.setStyleSheet("opacity: 0.85; font-weight: 600;")

        self.lbl_q = QLabel("Klik Mulai untuk mulai.")
        self.lbl_q.setWordWrap(True)
        self.lbl_q.setStyleSheet("font-size: 15px; font-weight: 700;")

        self.txt_answer = QLineEdit()
        self.txt_answer.setPlaceholderText("Ketik jawaban...")

        btn_submit = QPushButton("Jawab")
        btn_submit.setProperty("class", "primary")
        btn_submit.clicked.connect(self.check)

        btn_skip = QPushButton("Skip")
        btn_skip.setProperty("class", "secondary")
        btn_skip.clicked.connect(self.next_question)

        btns = QHBoxLayout()
        btns.addWidget(btn_submit)
        btns.addWidget(btn_skip)
        btns.addStretch()

        self.lbl_score = QLabel("Skor: 0 / 0")
        self.lbl_score.setStyleSheet("opacity: 0.85; font-weight: 700;")

        layout.addWidget(self.lbl_info)
        layout.addWidget(self.lbl_q)
        layout.addWidget(self.txt_answer)
        layout.addLayout(btns)
        layout.addWidget(self.lbl_score)
        layout.addStretch()

        self.setLayout(layout)

    def load_questions(self):
        f = self.cmb_from.currentText()
        t = self.cmb_to.currentText()
        if f != "Acak" and t != "Acak" and f == t:
            QMessageBox.warning(self, "Peringatan", "Bahasa Dari dan Ke tidak boleh sama.")
            return

        self.questions = get_quiz_vocab_questions(self.user_id, from_lang=f, to_lang=t, limit=40, include_hafal=False)
        if not self.questions:
            QMessageBox.information(self, "Info", "Tidak ada soal.\nPastikan ada kosakata minimal 2 bahasa dan belum hafal.")
            return

        self.index = 0
        self.score = 0
        self.total = 0
        self.lbl_score.setText("Skor: 0 / 0")
        self.next_question()

    def next_question(self):
        if self.index >= len(self.questions):
            QMessageBox.information(self, "Selesai", f"Quiz selesai!\nSkor akhir: {self.score} / {self.total}")
            return

        self.current = self.questions[self.index]
        self.index += 1

        self.lbl_info.setText(f"{self.current['from_lang']} → {self.current['to_lang']}")
        self.lbl_q.setText(f"Terjemahkan: {self.current['prompt']}")
        self.txt_answer.clear()
        self.txt_answer.setFocus()

    def norm(self, s: str) -> str:
        return (s or "").strip().casefold()

    def check(self):
        if not self.current:
            return

        user_ans = self.norm(self.txt_answer.text())
        correct = self.norm(self.current["answer"])

        self.total += 1
        if user_ans == correct:
            self.score += 1
            set_vocab_hafal(int(self.current["vocab_id"]), True)
            QMessageBox.information(self, "Benar", "Jawaban benar! Ditandai sudah hafal.")
        else:
            QMessageBox.warning(self, "Salah", f"Salah.\nJawaban: {self.current['answer']}")

        self.lbl_score.setText(f"Skor: {self.score} / {self.total}")
        self.next_question()
