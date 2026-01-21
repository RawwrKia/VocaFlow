from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
from PySide6.QtCore import Qt
from supabase_client import insert_user

class RegisterWindow(QWidget):
    def __init__(self, welcome=None):
        super().__init__()
        self.setWindowTitle("Buat Akun")
        self.welcome = welcome
        self.setup_ui()
        self.resize(520, 390)
        self.setMinimumSize(480, 340)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Registrasi")
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

        btn_register = QPushButton("Daftar")
        btn_back = QPushButton("← Kembali")

        btn_register.setProperty("class", "primary")
        btn_back.setProperty("class", "ghost")

        btn_register.clicked.connect(self.register)
        btn_back.clicked.connect(self.go_back)

        row = QHBoxLayout()
        row.addWidget(btn_back)
        row.addStretch(1)
        row.addWidget(btn_register)

        layout.addSpacing(6)
        layout.addLayout(row)
        layout.addStretch(1)

        self.setLayout(layout)

    def go_back(self):
        if self.welcome is not None:
            self.welcome.show()
        self.close()

    def register(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Peringatan", "Semua field wajib diisi")
            return

        resp = insert_user(username, password)
        if not resp.get("ok"):
            if resp.get("error") == "USERNAME_TAKEN":
                QMessageBox.warning(self, "Gagal", "Username sudah dipakai.")
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal register.\n{resp.get('error')}")
            return

        QMessageBox.information(self, "Sukses", "Akun dibuat. Silakan login.")
        if self.welcome is not None:
            self.welcome.show()
        self.close()

    def closeEvent(self, event):
        if self.welcome is not None and self.welcome.isHidden():
            self.welcome.show()
        event.accept()
