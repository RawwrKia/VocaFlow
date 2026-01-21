from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt

from reminder_service import ReminderService

class DashboardWindow(QWidget):
    def __init__(self, user_id: int, welcome=None):
        super().__init__()
        self.user_id = user_id
        self.welcome = welcome

        self.setWindowTitle("Menu")
        self.setup_ui()
        self.resize(560, 640)
        self.setMinimumSize(520, 600)

        self.reminder_service = ReminderService(self.user_id, parent_widget=self)
        self.reminder_service.start()

    def setup_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("Mau Apa Hari Ini?")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("PageTitle")

        root.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        btn_kategori = QPushButton("Kategori")
        btn_vocab = QPushButton("Kosakata")
        btn_notes = QPushButton("Hafalan Bebas")
        btn_quiz_vocab = QPushButton("Quiz Kosakata")
        btn_quiz_notes = QPushButton("Quiz Hafalan Bebas")
        btn_reminder = QPushButton("Reminder")
        btn_stat = QPushButton("Statistik")
        btn_logout = QPushButton("Logout")

        # classes
        for b in [btn_kategori, btn_vocab, btn_notes, btn_quiz_vocab, btn_quiz_notes, btn_reminder, btn_stat]:
            b.setProperty("class", "secondary")
        btn_logout.setProperty("class", "danger")

        btn_kategori.clicked.connect(self.open_kategori)
        btn_vocab.clicked.connect(self.open_vocab)
        btn_notes.clicked.connect(self.open_notes)
        btn_quiz_vocab.clicked.connect(self.open_quiz_vocab)
        btn_quiz_notes.clicked.connect(self.open_quiz_notes)
        btn_reminder.clicked.connect(self.open_reminder)
        btn_stat.clicked.connect(self.open_stat)
        btn_logout.clicked.connect(self.logout)

        # layout as tiles
        grid.addWidget(btn_kategori, 0, 0)
        grid.addWidget(btn_vocab, 0, 1)
        grid.addWidget(btn_notes, 1, 0)
        grid.addWidget(btn_reminder, 1, 1)
        grid.addWidget(btn_quiz_vocab, 2, 0)
        grid.addWidget(btn_quiz_notes, 2, 1)
        grid.addWidget(btn_stat, 3, 0)
        grid.addWidget(btn_logout, 3, 1)

        root.addSpacing(6)
        root.addLayout(grid)
        root.addStretch(1)

        self.setLayout(root)

    def open_kategori(self):
        from folder_page import FolderPage
        self.hide()
        self.page = FolderPage(self.user_id, dashboard=self)
        self.page.show()

    def open_vocab(self):
        from vocabulary_page import VocabularyPage
        self.hide()
        self.page = VocabularyPage(self.user_id, dashboard=self)
        self.page.show()

    def open_notes(self):
        from notes_page import NotesPage
        self.hide()
        self.page = NotesPage(self.user_id, dashboard=self)
        self.page.show()

    def open_quiz_vocab(self):
        from quiz_page import QuizPage
        self.hide()
        self.page = QuizPage(self.user_id, dashboard=self)
        self.page.show()

    def open_quiz_notes(self):
        from notes_quiz_page import NotesQuizPage
        self.hide()
        self.page = NotesQuizPage(self.user_id, dashboard=self)
        self.page.show()

    def open_reminder(self):
        from reminder_page import ReminderPage
        self.hide()
        self.page = ReminderPage(self.user_id, dashboard=self)
        self.page.show()

    def open_stat(self):
        from statistic_page import StatisticPage
        self.hide()
        self.page = StatisticPage(self.user_id, dashboard=self)
        self.page.show()

    def logout(self):
        try:
            self.reminder_service.stop()
        except Exception:
            pass

        if self.welcome is not None:
            self.welcome.show()
        self.close()
