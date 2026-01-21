from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QTabWidget, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QAbstractItemView

from supabase_client import (
    get_folders, insert_folder, update_folder, delete_folder,
    get_notes, get_vocabularies, get_translations, _folder_name_from_row
)

class FolderPage(QWidget):
    def __init__(self, user_id: int, dashboard=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard = dashboard

        self.selected_folder_id = None
        self.selected_folder_row_id = None
        self.loading = False

        self.setWindowTitle("Kategori")
        self.setup_ui()
        self.load_folders()

        self.resize(1050, 720)
        self.setMinimumSize(980, 650)

    def go_back(self):
        if self.dashboard is not None:
            self.dashboard.show()
        self.close()

    def closeEvent(self, event):
        if self.dashboard is not None:
            self.dashboard.show()
        event.accept()

    def _setup_table_base(self, tbl: QTableWidget):
        tbl.setAlternatingRowColors(True)
        tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # header
        top = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setProperty("class", "ghost")
        btn_back.clicked.connect(self.go_back)

        title = QLabel("Kategori")
        title.setObjectName("PageTitle")

        top.addWidget(btn_back)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch()
        layout.addLayout(top)

        # form
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nama kategori/folder")

        btn_add = QPushButton("Tambah")
        btn_update = QPushButton("Update")
        btn_delete = QPushButton("Hapus")

        btn_add.setProperty("class", "primary")
        btn_update.setProperty("class", "secondary")
        btn_delete.setProperty("class", "danger")

        btn_add.clicked.connect(self.add_folder)
        btn_update.clicked.connect(self.update_folder)
        btn_delete.clicked.connect(self.delete_folder)

        actions = QHBoxLayout()
        actions.addWidget(btn_add)
        actions.addWidget(btn_update)
        actions.addWidget(btn_delete)
        actions.addStretch()

        layout.addWidget(QLabel("Nama folder").setObjectName("SectionTitle") or QLabel())  # dummy to keep structure
        sec = QLabel("Nama folder")
        sec.setObjectName("SectionTitle")
        layout.addWidget(sec)
        layout.addWidget(self.txt_name)
        layout.addLayout(actions)

        # folders table
        folders_title = QLabel("Daftar folder (klik untuk lihat isi)")
        folders_title.setObjectName("SectionTitle")
        layout.addWidget(folders_title)

        self.tbl_folders = QTableWidget()
        self.tbl_folders.setColumnCount(2)
        self.tbl_folders.setHorizontalHeaderLabels(["ID", "Nama"])
        self.tbl_folders.cellClicked.connect(self.on_select_folder)
        self._setup_table_base(self.tbl_folders)

        layout.addWidget(self.tbl_folders)

        # filter status
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Semua", "Belum Hafal", "Sudah Hafal"])
        self.cmb_status.currentIndexChanged.connect(self.load_contents)

        statusbar = QHBoxLayout()
        statusbar.addWidget(QLabel("Filter status isi:"))
        statusbar.addWidget(self.cmb_status)
        statusbar.addStretch()
        layout.addLayout(statusbar)

        # tabs
        self.tabs = QTabWidget()

        self.tbl_notes = QTableWidget()
        self.tbl_notes.setColumnCount(3)
        self.tbl_notes.setHorizontalHeaderLabels(["ID", "Judul", "Hafal"])
        self._setup_table_base(self.tbl_notes)
        self.tabs.addTab(self.tbl_notes, "Hafalan Bebas")

        self.tbl_vocab = QTableWidget()
        self.tbl_vocab.setColumnCount(4)
        self.tbl_vocab.setHorizontalHeaderLabels(["ID", "Indonesia", "Inggris", "Hafal"])
        self._setup_table_base(self.tbl_vocab)
        self.tabs.addTab(self.tbl_vocab, "Kosakata")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def load_folders(self):
        self.tbl_folders.setRowCount(0)
        folders = get_folders(self.user_id)
        for row, f in enumerate(folders):
            self.tbl_folders.insertRow(row)
            self.tbl_folders.setItem(row, 0, QTableWidgetItem(str(f.get("id"))))
            self.tbl_folders.setItem(row, 1, QTableWidgetItem(_folder_name_from_row(f)))

    def on_select_folder(self, row, col):
        self.selected_folder_id = int(self.tbl_folders.item(row, 0).text())
        self.selected_folder_row_id = self.selected_folder_id
        self.txt_name.setText(self.tbl_folders.item(row, 1).text())
        self.load_contents()

    def _status_bool(self):
        t = self.cmb_status.currentText()
        if t == "Belum Hafal":
            return False
        if t == "Sudah Hafal":
            return True
        return None

    def load_contents(self):
        if self.selected_folder_id is None:
            self.tbl_notes.setRowCount(0)
            self.tbl_vocab.setRowCount(0)
            return

        st = self._status_bool()

        notes = get_notes(self.user_id, folder_id=self.selected_folder_id, hafal=st)
        self.tbl_notes.setRowCount(0)
        for r, n in enumerate(notes):
            self.tbl_notes.insertRow(r)
            self.tbl_notes.setItem(r, 0, QTableWidgetItem(str(n.get("id"))))
            self.tbl_notes.setItem(r, 1, QTableWidgetItem(n.get("judul") or ""))
            self.tbl_notes.setItem(r, 2, QTableWidgetItem("✓" if n.get("hafal") else ""))

        vocabs = get_vocabularies(self.user_id, folder_id=self.selected_folder_id, sudah_hafal=st)
        self.tbl_vocab.setRowCount(0)
        for r, v in enumerate(vocabs):
            self.tbl_vocab.insertRow(r)
            self.tbl_vocab.setItem(r, 0, QTableWidgetItem(str(v.get("id"))))

            trans = get_translations(v.get("id"))
            m = {t.get("bahasa"): t.get("kosakata") for t in trans}
            self.tbl_vocab.setItem(r, 1, QTableWidgetItem(m.get("Indonesia", "")))
            self.tbl_vocab.setItem(r, 2, QTableWidgetItem(m.get("Inggris", "")))
            self.tbl_vocab.setItem(r, 3, QTableWidgetItem("✓" if v.get("sudah_hafal") else ""))

    def add_folder(self):
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Peringatan", "Nama folder wajib diisi")
            return
        resp = insert_folder(self.user_id, name)
        if not resp.get("ok"):
            QMessageBox.critical(self, "Gagal", f"Gagal insert folder.\n{resp.get('error')}")
            return
        self.load_folders()

    def update_folder(self):
        if self.selected_folder_row_id is None:
            QMessageBox.warning(self, "Peringatan", "Klik folder dulu untuk edit")
            return
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Peringatan", "Nama folder wajib diisi")
            return
        resp = update_folder(self.selected_folder_row_id, name)
        if not resp.get("ok"):
            QMessageBox.critical(self, "Gagal", f"Gagal update folder.\n{resp.get('error')}")
            return
        self.load_folders()

    def delete_folder(self):
        if self.selected_folder_row_id is None:
            return
        delete_folder(self.selected_folder_row_id)
        self.selected_folder_row_id = None
        self.selected_folder_id = None
        self.txt_name.clear()
        self.load_folders()
        self.load_contents()
