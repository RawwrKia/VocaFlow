from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.login_win = None
        self.register_win = None
        self.setup_ui()
        self.resize(520, 420)
        self.setMinimumSize(480, 380)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("VocaFlow")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("PageTitle")
        subtitle = QLabel("Pilih menu untuk masuk:")
        subtitle.setStyleSheet("opacity: 0.85;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        btn_login = QPushButton("Login")
        btn_register = QPushButton("Buat Akun")

        btn_login.setProperty("class", "primary")
        btn_register.setProperty("class", "secondary")

        btn_login.clicked.connect(self.open_login)
        btn_register.clicked.connect(self.open_register)

        layout.addSpacing(10)
        layout.addWidget(btn_login)
        layout.addWidget(btn_register)
        layout.addStretch(1)

        foot = QLabel("Perbanyak Hafalan Kosakata Anda dengan VocaFlow ;D")
        foot.setStyleSheet("opacity: 0.6; font-size: 11px;")
        layout.addWidget(foot)

        self.setLayout(layout)

    def open_login(self):
        from login_window import LoginWindow
        self.login_win = LoginWindow(welcome=self)
        self.login_win.show()
        self.hide()

    def open_register(self):
        from register_window import RegisterWindow
        self.register_win = RegisterWindow(welcome=self)
        self.register_win.show()
        self.hide()
