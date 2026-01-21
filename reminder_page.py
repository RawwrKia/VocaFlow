from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import QHeaderView, QAbstractItemView

from supabase_client import (
    get_reminders, insert_reminder, update_reminder,
    delete_reminder, set_reminder_done
)

class ReminderPage(QWidget):
    def __init__(self, user_id: int, dashboard=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard = dashboard
        self.selected_id = None
        self.loading_table = False

        self.setWindowTitle("Reminder")
        self.setup_ui()
        self.load_data()

        self.resize(950, 650)
        self.setMinimumSize(860, 600)

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
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        top = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setProperty("class", "ghost")
        btn_back.clicked.connect(self.go_back)

        title = QLabel("Reminder")
        title.setObjectName("PageTitle")

        top.addWidget(btn_back)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch()
        layout.addLayout(top)

        self.txt_judul = QLineEdit()
        self.txt_judul.setPlaceholderText("Judul reminder")

        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDate(QDate.currentDate())

        formrow = QHBoxLayout()
        formrow.addWidget(QLabel("Judul"))
        formrow.addWidget(self.txt_judul)
        formrow.addWidget(QLabel("Tanggal"))
        formrow.addWidget(self.date)
        layout.addLayout(formrow)

        btn_add = QPushButton("Tambah")
        btn_update = QPushButton("Update")
        btn_delete = QPushButton("Hapus")

        btn_add.setProperty("class", "primary")
        btn_update.setProperty("class", "secondary")
        btn_delete.setProperty("class", "danger")

        btn_add.clicked.connect(self.add)
        btn_update.clicked.connect(self.update)
        btn_delete.clicked.connect(self.delete)

        action = QHBoxLayout()
        action.addWidget(btn_add)
        action.addWidget(btn_update)
        action.addWidget(btn_delete)
        action.addStretch()
        layout.addLayout(action)

        table_title = QLabel("Daftar Reminder")
        table_title.setObjectName("SectionTitle")
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Tanggal", "Judul", "Selesai"])
        self.table.cellDoubleClicked.connect(self.on_double_click)
        self.table.itemChanged.connect(self.on_item_changed)
        self._setup_table_base(self.table)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        self.loading_table = True
        self.table.setRowCount(0)
        data = get_reminders(self.user_id)

        for row, r in enumerate(data):
            self.table.insertRow(row)

            it_id = QTableWidgetItem(str(r.get("id")))
            it_id.setFlags(it_id.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, it_id)

            tgl = (r.get("tanggal") or "")[:10]
            it_tgl = QTableWidgetItem(tgl)
            it_tgl.setFlags(it_tgl.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, it_tgl)

            it_judul = QTableWidgetItem(r.get("judul") or "")
            it_judul.setFlags(it_judul.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 2, it_judul)

            it_done = QTableWidgetItem("")
            it_done.setFlags((it_done.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsEditable)
            it_done.setCheckState(Qt.Checked if r.get("selesai") else Qt.Unchecked)
            self.table.setItem(row, 3, it_done)

        self.loading_table = False

    def on_double_click(self, row, col):
        self.selected_id = int(self.table.item(row, 0).text())
        self.txt_judul.setText(self.table.item(row, 2).text())

        tgl = self.table.item(row, 1).text().strip()
        if tgl:
            y, m, d = [int(x) for x in tgl.split("-")]
            self.date.setDate(QDate(y, m, d))

    def on_item_changed(self, item: QTableWidgetItem):
        if self.loading_table:
            return
        if item.column() != 3:
            return

        row = item.row()
        rid = int(self.table.item(row, 0).text())
        done = (item.checkState() == Qt.Checked)
        set_reminder_done(rid, done)

    def add(self):
        judul = self.txt_judul.text().strip()
        if not judul:
            QMessageBox.warning(self, "Peringatan", "Judul wajib diisi")
            return
        tgl = self.date.date().toString("yyyy-MM-dd")
        insert_reminder(self.user_id, judul, tgl)
        self.load_data()

    def update(self):
        if self.selected_id is None:
            QMessageBox.warning(self, "Peringatan", "Double click baris dulu untuk edit")
            return

        judul = self.txt_judul.text().strip()
        if not judul:
            QMessageBox.warning(self, "Peringatan", "Judul wajib diisi")
            return
        tgl = self.date.date().toString("yyyy-MM-dd")

        update_reminder(self.selected_id, {"judul": judul, "tanggal": tgl})
        self.load_data()

    def delete(self):
        if self.selected_id is None:
            return
        delete_reminder(self.selected_id)
        self.selected_id = None
        self.load_data()
