from PySide6.QtCore import QTimer, QDate
from PySide6.QtWidgets import QMessageBox
from supabase_client import get_reminders

class ReminderService:
    """
    Alarm ringan:
    - cek reminders yang tanggalnya <= hari ini dan belum selesai
    - munculkan popup (sekali per reminder per sesi aplikasi)
    """
    def __init__(self, user_id: int, parent_widget=None):
        self.user_id = user_id
        self.parent_widget = parent_widget
        self.timer = QTimer()
        self.timer.setInterval(30_000)  # 30 detik
        self.timer.timeout.connect(self.check_due)
        self.shown_ids = set()

    def start(self):
        self.check_due()
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def check_due(self):
        try:
            data = get_reminders(self.user_id)
        except Exception:
            return

        today = QDate.currentDate().toString("yyyy-MM-dd")
        due = []
        for r in data:
            if r.get("selesai") is True:
                continue
            rid = r.get("id")
            tgl = (r.get("tanggal") or "").split("T")[0]
            if not rid or not tgl:
                continue
            if rid in self.shown_ids:
                continue
            if tgl <= today:
                due.append(r)

        if due:
            for r in due:
                self.shown_ids.add(r["id"])

            msg = "Reminder jatuh tempo:\n\n" + "\n".join([f"- {x.get('judul','(tanpa judul)')} ({(x.get('tanggal') or '')[:10]})" for x in due])
            QMessageBox.information(self.parent_widget, "Reminder", msg)
