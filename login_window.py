from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
from PySide6.QtCore import Qt
from supabase_client import select_user

class LoginWindow(QWidget):
    def __init__(self, welcome=None):
        super().__init__()
        self.setWindowTitle("Login")
        self.welcome = welcome
        self.dashboard = None
        self.setup_ui()
        self.resize(520, 360)
        self.setMinimumSize(480, 320)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Login")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Username")

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Password")
        self.txt_password.setEchoMode(QLineEdit.Password)

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.txt_username)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.txt_password)

        btn_login = QPushButton("Login")
        btn_back = QPushButton("← Kembali")

        btn_login.setProperty("class", "primary")
        btn_back.setProperty("class", "ghost")

        btn_login.clicked.connect(self.do_login)
        btn_back.clicked.connect(self.go_back)

        row = QHBoxLayout()
        row.addWidget(btn_back)
        row.addStretch(1)
        row.addWidget(btn_login)

        layout.addSpacing(6)
        layout.addLayout(row)
        layout.addStretch(1)

        self.setLayout(layout)

    def go_back(self):
        if self.welcome is not None:
            self.welcome.show()
        self.close()

    def do_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Peringatan", "Username dan password wajib diisi")
            return

        rows = select_user(username, password)
        if not rows:
            QMessageBox.critical(self, "Gagal", "Login gagal. Cek username/password.")
            return

        user_id = rows[0]["id"]

        from dashboard_window import DashboardWindow
        self.dashboard = DashboardWindow(user_id=user_id, welcome=self.welcome)

        if self.welcome is not None:
            self.welcome.hide()

        self.dashboard.show()
        self.close()

    def closeEvent(self, event):
        if self.dashboard is None and self.welcome is not None and self.welcome.isHidden():
            self.welcome.show()
        event.accept()
