from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QMessageBox,
    QComboBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QAbstractItemView

from supabase_client import (
    LANGS,
    get_folders, _folder_name_from_row,
    get_vocabularies, insert_vocabulary, update_vocabulary, delete_vocabulary,
    get_translations, upsert_translation, delete_translation,
    set_vocab_hafal, find_translation
)

class VocabularyPage(QWidget):
    def __init__(self, user_id: int, dashboard=None):
        super().__init__()
        self.user_id = user_id
        self.dashboard = dashboard

        self.selected_vocab_id = None
        self.selected_translation_id = None
        self.loading_table = False

        self.setWindowTitle("Kosakata Multibahasa")
        self.setup_ui()
        self.load_folders()
        self.load_data()

        self.resize(1100, 780)
        self.setMinimumSize(1000, 700)

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

        # header
        top = QHBoxLayout()
        btn_back = QPushButton("← Kembali")
        btn_back.setProperty("class", "ghost")
        btn_back.clicked.connect(self.go_back)

        title = QLabel("Kosakata Multibahasa")
        title.setObjectName("PageTitle")

        top.addWidget(btn_back)
        top.addSpacing(6)
        top.addWidget(title)
        top.addStretch()
        layout.addLayout(top)

        # filter
        self.cmb_filter_folder = QComboBox()
        self.cmb_filter_status = QComboBox()
        self.cmb_filter_status.addItems(["Semua", "Belum Hafal", "Sudah Hafal"])
        self.cmb_filter_folder.currentIndexChanged.connect(self.load_data)
        self.cmb_filter_status.currentIndexChanged.connect(self.load_data)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setProperty("class", "secondary")
        btn_refresh.clicked.connect(self.load_data)

        filterbar = QHBoxLayout()
        filterbar.addWidget(QLabel("Folder:"))
        filterbar.addWidget(self.cmb_filter_folder)
        filterbar.addWidget(QLabel("Status:"))
        filterbar.addWidget(self.cmb_filter_status)
        filterbar.addStretch()
        filterbar.addWidget(btn_refresh)
        layout.addLayout(filterbar)

        # form concept
        self.cmb_folder = QComboBox()
        self.txt_catatan = QTextEdit()
        self.txt_catatan.setPlaceholderText("Catatan konsep kosakata (opsional)")

        # form translation
        self.cmb_bahasa = QComboBox()
        self.cmb_bahasa.addItems(LANGS)
        self.cmb_bahasa.currentTextChanged.connect(self.load_detail_for_selected_language)

        self.txt_kosakata = QLineEdit()
        self.txt_pengucapan = QLineEdit()
        self.txt_arti = QLineEdit()

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignTop)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        sec1 = QLabel("Konsep")
        sec1.setObjectName("SectionTitle")
        form.addRow(sec1, QLabel(""))

        form.addRow("Folder", self.cmb_folder)
        form.addRow("Catatan (konsep)", self.txt_catatan)

        sec2 = QLabel("Detail Bahasa")
        sec2.setObjectName("SectionTitle")
        form.addRow(sec2, QLabel(""))

        form.addRow("Bahasa", self.cmb_bahasa)
        form.addRow("Kosakata", self.txt_kosakata)
        form.addRow("Pengucapan", self.txt_pengucapan)
        form.addRow("Arti", self.txt_arti)

        layout.addLayout(form)

        # actions
        btn_new = QPushButton("Buat Kosakata Baru")
        btn_save_lang = QPushButton("Simpan / Update Bahasa")
        btn_del_lang = QPushButton("Hapus Bahasa Ini")
        btn_del_vocab = QPushButton("Hapus Kosakata (Semua Bahasa)")
        btn_mark_hafal = QPushButton("Tandai Sudah Hafal")

        btn_new.setProperty("class", "secondary")
        btn_save_lang.setProperty("class", "primary")
        btn_del_lang.setProperty("class", "danger")
        btn_del_vocab.setProperty("class", "danger")
        btn_mark_hafal.setProperty("class", "primary")

        btn_new.clicked.connect(self.create_new_vocab)
        btn_save_lang.clicked.connect(self.save_language)
        btn_del_lang.clicked.connect(self.delete_language)
        btn_del_vocab.clicked.connect(self.delete_vocab_all)
        btn_mark_hafal.clicked.connect(self.mark_hafal)

        actions = QHBoxLayout()
        actions.addWidget(btn_new)
        actions.addWidget(btn_save_lang)
        actions.addWidget(btn_del_lang)
        actions.addWidget(btn_del_vocab)
        actions.addStretch()
        actions.addWidget(btn_mark_hafal)
        layout.addLayout(actions)

        # table
        table_title = QLabel("Ringkasan (double click untuk edit)")
        table_title.setObjectName("SectionTitle")
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "FolderID", "Hafal", "Indonesia", "Inggris", "Mandarin/Jepang"])
        self.table.cellDoubleClicked.connect(self.on_double_click)
        self.table.itemChanged.connect(self.on_item_changed_hafal)
        self._setup_table_base(self.table)

        # tetap allow checkbox column
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

        vocabs = get_vocabularies(self.user_id, folder_id=folder_filter, sudah_hafal=status_filter)

        for row, v in enumerate(vocabs):
            self.table.insertRow(row)

            it_id = QTableWidgetItem(str(v["id"]))
            it_id.setFlags(it_id.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, it_id)

            folder_text = "" if v.get("folder_id") is None else str(v.get("folder_id"))
            it_fid = QTableWidgetItem(folder_text)
            it_fid.setFlags(it_fid.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, it_fid)

            it_h = QTableWidgetItem("")
            it_h.setFlags((it_h.flags() | Qt.ItemIsUserCheckable) & ~Qt.ItemIsEditable)
            it_h.setCheckState(Qt.Checked if v.get("sudah_hafal") else Qt.Unchecked)
            self.table.setItem(row, 2, it_h)

            trans = get_translations(v["id"])
            m = {t.get("bahasa"): t.get("kosakata") for t in trans}

            self.table.setItem(row, 3, QTableWidgetItem(m.get("Indonesia", "")))
            self.table.setItem(row, 4, QTableWidgetItem(m.get("Inggris", "")))

            mj = []
            if m.get("Mandarin"):
                mj.append(f"Mandarin: {m.get('Mandarin')}")
            if m.get("Jepang"):
                mj.append(f"Jepang: {m.get('Jepang')}")
            self.table.setItem(row, 5, QTableWidgetItem(" | ".join(mj)))

        self.loading_table = False

        if self.selected_vocab_id is not None:
            self.load_detail_for_selected_language(self.cmb_bahasa.currentText())

    def on_double_click(self, row, col):
        self.selected_vocab_id = int(self.table.item(row, 0).text())

        folder_id_text = self.table.item(row, 1).text().strip()
        folder_id = int(folder_id_text) if folder_id_text else None
        idx = self.cmb_folder.findData(folder_id)
        if idx >= 0:
            self.cmb_folder.setCurrentIndex(idx)
        else:
            self.cmb_folder.setCurrentIndex(0)

        vocabs = get_vocabularies(self.user_id)
        found = [x for x in vocabs if int(x["id"]) == int(self.selected_vocab_id)]
        self.txt_catatan.setPlainText(found[0].get("catatan") or "" if found else "")

        self.load_detail_for_selected_language(self.cmb_bahasa.currentText())

    def on_item_changed_hafal(self, item: QTableWidgetItem):
        if self.loading_table:
            return
        if item.column() != 2:
            return

        row = item.row()
        vocab_id = int(self.table.item(row, 0).text())
        hafal = (item.checkState() == Qt.Checked)
        set_vocab_hafal(vocab_id, hafal)

    def create_new_vocab(self):
        self.selected_vocab_id = None
        self.selected_translation_id = None
        self.txt_catatan.clear()
        self.txt_kosakata.clear()
        self.txt_pengucapan.clear()
        self.txt_arti.clear()
        QMessageBox.information(self, "Info", "Mode: buat kosakata baru.\nIsi catatan (opsional), pilih bahasa, lalu Simpan/Update Bahasa.")

    def save_language(self):
        kosakata = self.txt_kosakata.text().strip()
        if not kosakata:
            QMessageBox.warning(self, "Peringatan", "Kosakata wajib diisi")
            return

        bahasa = self.cmb_bahasa.currentText()
        pengucapan = self.txt_pengucapan.text().strip()
        arti = self.txt_arti.text().strip()
        folder_id = self.cmb_folder.currentData()
        catatan = self.txt_catatan.toPlainText().strip()

        if self.selected_vocab_id is None:
            created = insert_vocabulary(self.user_id, catatan=catatan, folder_id=folder_id)
            if not created:
                QMessageBox.critical(self, "Gagal", "Gagal membuat vocabulary. Cek RLS/DB.")
                return
            self.selected_vocab_id = created[0]["id"]
        else:
            update_vocabulary(self.selected_vocab_id, {"catatan": catatan, "folder_id": folder_id})

        upsert_translation(self.selected_vocab_id, bahasa, kosakata, pengucapan, arti)
        self.load_data()

    def load_detail_for_selected_language(self, bahasa: str):
        if self.selected_vocab_id is None:
            self.selected_translation_id = None
            self.txt_kosakata.clear()
            self.txt_pengucapan.clear()
            self.txt_arti.clear()
            return

        tid = find_translation(self.selected_vocab_id, bahasa)
        self.selected_translation_id = tid

        if tid is None:
            self.txt_kosakata.clear()
            self.txt_pengucapan.clear()
            self.txt_arti.clear()
            return

        trans = get_translations(self.selected_vocab_id)
        for t in trans:
            if t.get("bahasa") == bahasa:
                self.txt_kosakata.setText(t.get("kosakata") or "")
                self.txt_pengucapan.setText(t.get("pengucapan") or "")
                self.txt_arti.setText(t.get("arti") or "")
                return

    def delete_language(self):
        if self.selected_translation_id is None:
            QMessageBox.information(self, "Info", "Tidak ada bahasa ini pada kosakata terpilih.")
            return
        delete_translation(self.selected_translation_id)
        self.selected_translation_id = None
        self.load_data()

    def delete_vocab_all(self):
        if self.selected_vocab_id is None:
            return
        delete_vocabulary(self.selected_vocab_id)
        self.selected_vocab_id = None
        self.selected_translation_id = None
        self.load_data()

    def mark_hafal(self):
        if self.selected_vocab_id is None:
            QMessageBox.warning(self, "Peringatan", "Pilih kosakata dulu (double click baris)")
            return
        set_vocab_hafal(self.selected_vocab_id, True)
        self.load_data()
