from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox,
    QComboBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QAbstractItemView

from supabase_client import (
    get_notes, insert_note, update_note, delete_note,
    set_note_hafal, get_folders, _folder_name_from_row
)

class NotesPage(QWidget):
    def __init__(self, user_id: int, dashboard=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard = dashboard
        self.selected_id = None
        self.loading_table = False

        self.setWindowTitle("Hafalan Bebas")
        self.setup_ui()
        self.load_folders()
        self.load_data()

        self.resize(1100, 760)
        self.setMinimumSize(1000, 680)

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
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tbl.horizontalHeader().setStretchLastSection(True)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setProperty("class", "ghost")
        btn_back.clicked.connect(self.go_back)

        title = QLabel("Hafalan Bebas")
        title.setObjectName("PageTitle")

        top.addWidget(btn_back)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch()
        layout.addLayout(top)

        # filter bar
        self.cmb_filter_folder = QComboBox()
        self.cmb_filter_status = QComboBox()
        self.cmb_filter_status.addItems(["Semua", "Belum Hafal", "Sudah Hafal"])

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setProperty("class", "secondary")
        btn_refresh.clicked.connect(self.load_data)

        self.cmb_filter_folder.currentIndexChanged.connect(self.load_data)
        self.cmb_filter_status.currentIndexChanged.connect(self.load_data)

        filterbar = QHBoxLayout()
        filterbar.addWidget(QLabel("Folder:"))
        filterbar.addWidget(self.cmb_filter_folder)
        filterbar.addWidget(QLabel("Status:"))
        filterbar.addWidget(self.cmb_filter_status)
        filterbar.addStretch()
        filterbar.addWidget(btn_refresh)
        layout.addLayout(filterbar)

        # form
        self.txt_judul = QLineEdit()
        self.txt_isi = QTextEdit()
        self.txt_isi.setPlaceholderText("Isi hafalan...")

        self.cmb_folder = QComboBox()
        self.chk_hafal_form = QComboBox()
        self.chk_hafal_form.addItems(["Belum Hafal", "Sudah Hafal"])

        form = QFormLayout()
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        sec = QLabel("Input Hafalan")
        sec.setObjectName("SectionTitle")
        form.addRow(sec, QLabel(""))

        form.addRow("Judul", self.txt_judul)
        form.addRow("Isi", self.txt_isi)
        form.addRow("Folder", self.cmb_folder)
        form.addRow("Status", self.chk_hafal_form)

        layout.addLayout(form)

        btn_add = QPushButton("Tambah")
        btn_update = QPushButton("Update")
        btn_delete = QPushButton("Hapus")

        btn_add.setProperty("class", "primary")
        btn_update.setProperty("class", "secondary")
        btn_delete.setProperty("class", "danger")

        btn_add.clicked.connect(self.add)
        btn_update.clicked.connect(self.update)
        btn_delete.clicked.connect(self.delete)

        actions = QHBoxLayout()
        actions.addWidget(btn_add)
        actions.addWidget(btn_update)
        actions.addWidget(btn_delete)
        actions.addStretch()
        layout.addLayout(actions)

        # table
        table_title = QLabel("Daftar Hafalan (double click untuk edit)")
        table_title.setObjectName("SectionTitle")
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "FolderID", "Judul", "Isi", "Hafal", "Created"])
        self.table.cellDoubleClicked.connect(self.on_double_click)
        self.table.itemChanged.connect(self.on_item_changed)

        self._setup_table_base(self.table)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_folders(self):
        self.cmb_folder.clear()
        self.cmb_filter_folder.clear()

        self.cmb_folder.addItem("Tanpa Folder", None)
        self.cmb_filter_folder.addItem("Semua", None)
        self.cmb_filter_folder.addItem("Tanpa Folder", "NO_FOLDER")

        folders = get_folders(self.user_id)
        for f in folders:
            fid = f.get("id")
            name = _folder_name_from_row(f)
            self.cmb_folder.addItem(name, fid)
            self.cmb_filter_folder.addItem(name, fid)

    def _status_to_bool(self, text: str):
        if text == "Belum Hafal":
            return False
        if text == "Sudah Hafal":
            return True
        return None

    def load_data(self):
        folder_filter = self.cmb_filter_folder.currentData()
        status_filter = self._status_to_bool(self.cmb_filter_status.currentText())

        self.loading_table = True
        self.table.setRowCount(0)

        data = get_notes(self.user_id, folder_id=folder_filter, hafal=status_filter)

        for row, n in enumerate(data):
            self.table.insertRow(row)

            it_id = QTableWidgetItem(str(n.get("id")))
            it_id.setFlags(it_id.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, it_id)

            folder_text = "" if n.get("folder_id") is None else str(n.get("folder_id"))
            it_folder = QTableWidgetItem(folder_text)
            it_folder.setFlags(it_folder.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, it_folder)

            it_j = QTableWidgetItem(n.get("judul") or "")
            it_j.setFlags(it_j.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, it_j)

            it_i = QTableWidgetItem(n.get("isi") or "")
            it_i.setFlags(it_i.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, it_i)

            it_h = QTableWidgetItem("")
            it_h.setFlags((it_h.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsEditable)
            it_h.setCheckState(Qt.Checked if n.get("hafal") else Qt.Unchecked)
            self.table.setItem(row, 4, it_h)

            it_c = QTableWidgetItem(n.get("created_at") or "")
            it_c.setFlags(it_c.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 5, it_c)

        self.loading_table = False

    def on_double_click(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.txt_judul.setText(self.table.item(row, 2).text())
        self.txt_isi.setPlainText(self.table.item(row, 3).text())

        hafal_checked = (self.table.item(row, 4).checkState() == Qt.Checked)
        self.chk_hafal_form.setCurrentText("Sudah Hafal" if hafal_checked else "Belum Hafal")

        folder_id_text = self.table.item(row, 1).text().strip()
        folder_id = int(folder_id_text) if folder_id_text else None
        idx = self.cmb_folder.findData(folder_id)
        if idx >= 0:
            self.cmb_folder.setCurrentIndex(idx)
        else:
            self.cmb_folder.setCurrentIndex(0)

    def on_item_changed(self, item: QTableWidgetItem):
        if self.loading_table:
            return
        if item.column() != 4:
            return

        row = item.row()
        note_id = int(self.table.item(row, 0).text())
        new_value = (item.checkState() == Qt.Checked)
        set_note_hafal(note_id, new_value)

    def add(self):
        judul = self.txt_judul.text().strip()
        isi = self.txt_isi.toPlainText().strip()
        if not judul or not isi:
            QMessageBox.warning(self, "Peringatan", "Judul dan isi wajib diisi")
            return

        data = {
            "user_id": self.user_id,
            "judul": judul,
            "isi": isi,
            "folder_id": self.cmb_folder.currentData(),
            "hafal": (self.chk_hafal_form.currentText() == "Sudah Hafal")
        }
        insert_note(data)
        self.load_data()

    def update(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Peringatan", "Double click baris dulu untuk edit")
            return

        data = {
            "judul": self.txt_judul.text().strip(),
            "isi": self.txt_isi.toPlainText().strip(),
            "folder_id": self.cmb_folder.currentData(),
            "hafal": (self.chk_hafal_form.currentText() == "Sudah Hafal")
        }
        update_note(self.selected_id, data)
        self.load_data()

    def delete(self):
        if self.selected_id is None:
            return
        delete_note(self.selected_id)
        self.selected_id = None
        self.load_data()
