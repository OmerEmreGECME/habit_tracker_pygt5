from PyQt5 import QtWidgets, QtCore, QtGui
import datetime
from dialogs import HabitEditDialog
import sqlite3

class MainWindow(QtWidgets.QMainWindow):
    LEVEL_NAMES = ["Başlangıç", "Çaylak", "Usta", "Ustalaşmış", "Usta++"]

    def __init__(self, db, user_row):
        super().__init__()
        self.db = db
        self.user = user_row
        self.setWindowTitle(f"Habit Tracker - {self.user['username']}")
        self.resize(900, 600)
        self.selected_habit_id = None
        self.setup_ui()
        self.refresh_habits()
        self.update_profile_panel()

    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout()
        central.setLayout(main_layout)

        # Top bar
        top_bar = QtWidgets.QHBoxLayout()
        self.user_label = QtWidgets.QLabel(f"Kullanıcı: {self.user['username']}")
        self.points_label = QtWidgets.QLabel()
        self.level_label = QtWidgets.QLabel()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximum(10)
        top_bar.addWidget(self.user_label)
        top_bar.addStretch()
        top_bar.addWidget(self.points_label)
        top_bar.addWidget(self.level_label)
        top_bar.addWidget(QtWidgets.QLabel("Seviye ilerlemesi:"))
        top_bar.addWidget(self.progress_bar)
        main_layout.addLayout(top_bar)

        # Middle layout
        middle = QtWidgets.QHBoxLayout()
        main_layout.addLayout(middle)

        # Left: Habits table + controls
        left_layout = QtWidgets.QVBoxLayout()
        self.habits_table = QtWidgets.QTableWidget(0, 4)
        self.habits_table.setHorizontalHeaderLabels(["ID", "Alışkanlık", "Kategori", "Sıklık"])
        self.habits_table.horizontalHeader().setStretchLastSection(True)
        self.habits_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.habits_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.habits_table.hideColumn(0)
        left_layout.addWidget(self.habits_table)

        controls = QtWidgets.QHBoxLayout()
        self.add_btn = QtWidgets.QPushButton("Ekle")
        self.edit_btn = QtWidgets.QPushButton("Düzenle")
        self.delete_btn = QtWidgets.QPushButton("Sil")
        self.mark_btn = QtWidgets.QPushButton("Bugün Tamamla / Geri Al")
        controls.addWidget(self.add_btn)
        controls.addWidget(self.edit_btn)
        controls.addWidget(self.delete_btn)
        controls.addWidget(self.mark_btn)
        left_layout.addLayout(controls)

        middle.addLayout(left_layout, 2)

        # Right: Details, Calendar, Badges
        right_layout = QtWidgets.QVBoxLayout()
        self.details_group = QtWidgets.QGroupBox("Alışkanlık Detayı")
        d_layout = QtWidgets.QVBoxLayout()
        self.detail_name = QtWidgets.QLabel("-")
        self.detail_category = QtWidgets.QLabel("-")
        self.detail_frequency = QtWidgets.QLabel("-")
        d_layout.addWidget(QtWidgets.QLabel("Ad:")); d_layout.addWidget(self.detail_name)
        d_layout.addWidget(QtWidgets.QLabel("Kategori:")); d_layout.addWidget(self.detail_category)
        d_layout.addWidget(QtWidgets.QLabel("Sıklık:")); d_layout.addWidget(self.detail_frequency)
        self.details_group.setLayout(d_layout)
        right_layout.addWidget(self.details_group)

        self.calendar = QtWidgets.QCalendarWidget()
        right_layout.addWidget(QtWidgets.QLabel("Tamamlanma Takvimi (seçili alışkanlık)"))
        right_layout.addWidget(self.calendar)

        badges_box = QtWidgets.QGroupBox("Rozetler")
        b_layout = QtWidgets.QVBoxLayout()
        self.badges_list = QtWidgets.QLabel("-")
        b_layout.addWidget(self.badges_list)
        badges_box.setLayout(b_layout)
        right_layout.addWidget(badges_box)

        self.logout_btn = QtWidgets.QPushButton("Çıkış Yap")
        right_layout.addWidget(self.logout_btn)

        middle.addLayout(right_layout, 1)

        # Signals
        self.add_btn.clicked.connect(self.add_habit)
        self.edit_btn.clicked.connect(self.edit_habit)
        self.delete_btn.clicked.connect(self.delete_habit)
        self.mark_btn.clicked.connect(self.toggle_completion_today)
        self.habits_table.itemSelectionChanged.connect(self.on_habit_selected)
        self.logout_btn.clicked.connect(self.on_logout)
        self.calendar.clicked.connect(self.on_calendar_date_clicked)
        self.calendar.setLocale(QtCore.QLocale(
            QtCore.QLocale.Turkish,
            QtCore.QLocale.Turkey
))

    # ---------------------------
    # Habits CRUD & Details
    # ---------------------------
    def refresh_habits(self):
        self.habits = self.db.list_habits(self.user["id"])
        self.habits_table.setRowCount(0)
        for h in self.habits:
            row = self.habits_table.rowCount()
            self.habits_table.insertRow(row)
            self.habits_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(h["id"])))
            self.habits_table.setItem(row, 1, QtWidgets.QTableWidgetItem(h["name"]))
            self.habits_table.setItem(row, 2, QtWidgets.QTableWidgetItem(h["category"]))
            self.habits_table.setItem(row, 3, QtWidgets.QTableWidgetItem(h["frequency"]))
        self.clear_details()

    def clear_details(self):
        self.selected_habit_id = None
        self.detail_name.setText("-")
        self.detail_category.setText("-")
        self.detail_frequency.setText("-")
        self.calendar.setSelectedDate(QtCore.QDate.currentDate())
        self.calendar.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())
        self.badges_list.setText("-")

    def on_habit_selected(self):
        selected_rows = self.habits_table.selectionModel().selectedRows()
        if not selected_rows:
            self.clear_details()
            return
        row = selected_rows[0].row()
        habit_id_item = self.habits_table.item(row, 0)
        if not habit_id_item:
            self.clear_details()
            return
        habit_id = int(habit_id_item.text())
        habit = self.db.get_habit(habit_id)
        if not habit:
            self.clear_details()
            return
        self.selected_habit_id = habit_id
        self.detail_name.setText(habit["name"])
        self.detail_category.setText(habit["category"])
        self.detail_frequency.setText(habit["frequency"])
        self.refresh_calendar_for_habit(habit_id)
        self.update_badges_for_habit(habit_id)

    # ---------------------------
    # Calendar & Completion
    # ---------------------------
    def refresh_calendar_for_habit(self, habit_id):
        # 🔄 Tüm formatları temizle
        self.calendar.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())

        dates = self.db.completions_for_habit(habit_id)

        fmt = QtGui.QTextCharFormat()
        fmt.setBackground(QtGui.QBrush(QtGui.QColor("#8fbc8f")))
        fmt.setForeground(QtGui.QBrush(QtGui.QColor("black")))

        for d in dates:
            if isinstance(d, str):
                d = datetime.date.fromisoformat(d)

            qd = QtCore.QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(qd, fmt)


    def toggle_completion_today(self):
        if not self.selected_habit_id:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Lütfen bir alışkanlık seçin.")
            return

        # 🔴 BUGÜN DEĞİL → TAKVİMDE SEÇİLİ TARİH
        qdate = self.calendar.selectedDate()
        selected_date = datetime.date( qdate.year(), qdate.month(), qdate.day() )

        if self.db.is_completed(self.selected_habit_id, selected_date):
            # 🔁 GERİ AL
            self.db.unmark_completed(self.selected_habit_id, selected_date)
            self.db.add_points(self.user["id"], -1)

            QtWidgets.QMessageBox.information(
                self,
                "Bilgi",
                f"{selected_date.strftime('%d.%m.%Y')} tarihi için tamamlama geri alındı. (-1 puan)"
            )

        else:
            # ✅ TAMAMLA
            ok = self.db.mark_completed(self.selected_habit_id, selected_date)
            if ok:
                self.db.add_points(self.user["id"], 1)
                QtWidgets.QMessageBox.information(
                    self,
                    "Tebrikler",
                    f"{selected_date.strftime('%d.%m.%Y')} tarihi için alışkanlık tamamlandı! (+1 puan)"
                )
            else:
                QtWidgets.QMessageBox.information(
                    self,
                    "Bilgi",
                    "Bu tarih zaten tamamlanmış."
                )
        self.calendar.setSelectedDate(
            QtCore.QDate(selected_date.year, selected_date.month, selected_date.day)
        )
        self.refresh_calendar_for_habit(self.selected_habit_id)
        self.update_profile_panel()
        self.update_badges_for_habit(self.selected_habit_id)



    def on_calendar_date_clicked(self, qdate):
        if not self.selected_habit_id:
            return

        d = datetime.date(qdate.year(),qdate.month(), qdate.day())

        if self.db.is_completed(self.selected_habit_id, d):
            self.mark_btn.setText("Geri Al")
        else:
            self.mark_btn.setText("Tamamla")


    # ---------------------------
    # CRUD
    # ---------------------------
    def add_habit(self):
        dlg = HabitEditDialog(parent=self)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            name, category, frequency = dlg.get_values()

            # Boş isim kontrolü
            if not name.strip():
                QtWidgets.QMessageBox.warning(
                self,
                    "Uyarı",
                    "Alışkanlık adı boş olamaz."
                )
                return

            # Aynı isim (BÜYÜK/küçük harf duyarsız) kontrolü
            existing = [
                h["name"].lower()
                for h in self.db.list_habits(self.user["id"])
            ]

            if name.lower() in existing:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Uyarı",
                    "Bu isimde bir alışkanlık zaten mevcut."
                )
                return

            # Veritabanına ekle
            self.db.add_habit(
                self.user["id"],
                name.strip(),
                category,
                frequency
            )

            # Listeyi yenile
            self.refresh_habits()

    def update_habit(self, habit_id, name, category, frequency):
        name = name.strip()

        cur = self.conn.cursor()
        try:
            cur.execute(
                "UPDATE habits SET name = ?, category = ?, frequency = ? WHERE id = ?",
                (name, category, frequency, habit_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


    def edit_habit(self):
        if self.selected_habit_id is None:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir alışkanlık seçin.")
            return
        habit = self.db.get_habit(self.selected_habit_id)
        if not habit:
            QtWidgets.QMessageBox.warning(self, "Hata", "Seçili alışkanlık bulunamadı.")
            self.refresh_habits()
            return
        dlg = HabitEditDialog(parent=self,
                              name=habit["name"],
                              category=habit["category"],
                              frequency=habit["frequency"])
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            name, category, frequency = dlg.get_values()
            if not name:
                QtWidgets.QMessageBox.warning(self, "Uyarı", "Alışkanlık adı boş olamaz.")
                return
            self.db.update_habit(self.selected_habit_id, name, category, frequency)
            self.refresh_habits()

    def delete_habit(self):
        if not self.selected_habit_id:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir alışkanlık seçin.")
            return

        confirm = QtWidgets.QMessageBox.question(
            self,
            "Onay",
            "Seçili alışkanlığı silmek istiyor musunuz?\n"
            "Bu alışkanlıktan kazanılan puanlar da silinecek.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, # Butonları netleştirelim
            QtWidgets.QMessageBox.No # Varsayılan buton No olsun
        )

        # 🔴 EĞER CEVAP 'YES' DEĞİLSE METODU BURADA DURDUR (Kapatmayı önler)
        if confirm != QtWidgets.QMessageBox.Yes:
            return 

        # ✅ BURADAN AŞAĞISI SADECE 'YES' DENİRSE ÇALIŞIR
        habit_id = self.selected_habit_id

        # Silmeden önce puanları düş
        completed_count = self.db.completion_count_for_habit(habit_id)
        if completed_count > 0:
            self.db.add_points(self.user["id"], -completed_count)

        # Veritabanından sil
        self.db.delete_habit(habit_id)

        # Arayüzü güncelle
        self.refresh_habits()
        self.update_profile_panel()
        QtWidgets.QMessageBox.information(self, "Bilgi", "Alışkanlık başarıyla silindi.")

        if confirm == QtWidgets.QMessageBox.Yes:
            habit_id = self.selected_habit_id

            # 🔴 MUTLAKA SİLMEDEN ÖNCE!
            completed_count = self.db.completion_count_for_habit(habit_id)
            print("DEBUG completion_count:", completed_count)  # test için

            if completed_count > 0:
                self.db.add_points(self.user["id"], -completed_count)

        # 🔽 ŞİMDİ SİL
        self.db.delete_habit(habit_id)

        self.refresh_habits()
        self.update_profile_panel()

    # ---------------------------
    # Profile & Badges
    # ---------------------------
    def update_profile_panel(self):
        pts = self.db.total_points(self.user["id"])
        self.points_label.setText(f"Puan: {pts}")
        lvl = pts // 10
        lvl_name = self.LEVEL_NAMES[min(lvl, len(self.LEVEL_NAMES)-1)]
        self.level_label.setText(f"Seviye: {lvl_name} ({lvl})")
        self.progress_bar.setValue(pts % 10)

    def update_badges_for_habit(self, habit_id):
        if not habit_id:
            self.badges_list.setText("-")
            return
        dates = [d if isinstance(d, datetime.date) else datetime.date.fromisoformat(d)
                 for d in self.db.completions_for_habit(habit_id)]
        badges = []
        today = datetime.date.today()
        streak = 0
        for i in range(7):
            day = today - datetime.timedelta(days=i)
            if day in dates:
                streak += 1
            else:
                break
        if streak >= 7:
            badges.append("Seri Katılım (7 gün)")
        total_pts = self.db.total_points(self.user["id"])
        if total_pts >= 30:
            badges.append("İstikrar Ustası (30+ puan)")
        self.badges_list.setText("\n".join(badges) if badges else "Henüz rozet yok.")

    # ---------------------------
    # Logout
    # ---------------------------
    def on_logout(self):
        confirm = QtWidgets.QMessageBox.question(self, "Çıkış", "Oturumdan çıkmak istiyor musunuz?")
        if confirm == QtWidgets.QMessageBox.Yes:
            self.close()
