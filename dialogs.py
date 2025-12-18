from PyQt5 import QtWidgets
from utils import hash_password

class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Kayıt Ol")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        self.resize(400, 220)
        layout = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()
        self.username_edit = QtWidgets.QLineEdit()
        self.email_edit = QtWidgets.QLineEdit()
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_confirm = QtWidgets.QLineEdit()
        self.password_confirm.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Kullanıcı Adı:", self.username_edit)
        form.addRow("E-posta:", self.email_edit)
        form.addRow("Şifre:", self.password_edit)
        form.addRow("Şifre (Tekrar):", self.password_confirm)
        layout.addLayout(form)
        self.msg_label = QtWidgets.QLabel()
        layout.addWidget(self.msg_label)
        btns = QtWidgets.QHBoxLayout()
        self.register_btn = QtWidgets.QPushButton("Kayıt Ol")
        self.cancel_btn = QtWidgets.QPushButton("İptal")
        btns.addWidget(self.register_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.register_btn.clicked.connect(self.on_register)
        self.cancel_btn.clicked.connect(self.reject)

    def on_register(self):
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip().lower()
        pw = self.password_edit.text()
        pw2 = self.password_confirm.text()
        if not username or not email or not pw:
            self.msg_label.setText("Alanlar boş olamaz.")
            return
        if "@" not in email:
            self.msg_label.setText("Geçerli bir e-posta girin.")
            return
        if pw != pw2:
            self.msg_label.setText("Şifreler eşleşmiyor.")
            return
        phash = hash_password(pw)
        user_id = self.db.create_user(username, email, phash)
        if user_id is None:
            self.msg_label.setText("E-posta veya kullanıcı adı zaten kayıtlı.")
        else:
            QtWidgets.QMessageBox.information(self, "Başarılı", "Kayıt tamamlandı. Giriş yapabilirsiniz.")
            self.accept()

class LoginDialog(QtWidgets.QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = None
        self.setWindowTitle("Giriş Yap")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        self.resize(360, 160)
        layout = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()
        self.email_edit = QtWidgets.QLineEdit()
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("E-posta:", self.email_edit)
        form.addRow("Şifre:", self.password_edit)
        layout.addLayout(form)
        self.msg_label = QtWidgets.QLabel()
        layout.addWidget(self.msg_label)
        btns = QtWidgets.QHBoxLayout()
        self.login_btn = QtWidgets.QPushButton("Giriş")
        self.register_btn = QtWidgets.QPushButton("Kayıt Ol")
        btns.addWidget(self.login_btn)
        btns.addWidget(self.register_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        self.login_btn.clicked.connect(self.on_login)
        self.register_btn.clicked.connect(self.on_register)

    def on_register(self):
        from dialogs import RegisterDialog
        dlg = RegisterDialog(self.db, self)
        dlg.exec_()

    def on_login(self):
        email = self.email_edit.text().strip().lower()
        pw = self.password_edit.text()
        if not email or not pw:
            self.msg_label.setText("E-posta ve şifre gerekli.")
            return
        user = self.db.get_user_by_email(email)
        if not user:
            self.msg_label.setText("Kayıtlı kullanıcı bulunamadı.")
            return
        if user["password_hash"] != hash_password(pw):
            self.msg_label.setText("Hatalı şifre.")
            return
        self.user = user
        self.accept()

from PyQt5 import QtWidgets


class HabitEditDialog(QtWidgets.QDialog):
    CATEGORIES = ["Spor", "Sanat", "Müzik", "Hobi", "Sağlık", "İş"]
    FREQUENCIES = ["Günlük", "Haftalık", "Aylık"]

    def __init__(self, parent=None, name="", category="", frequency=""):
        super().__init__(parent)
        self.setWindowTitle("Alışkanlık")
        self.resize(300, 200)

        layout = QtWidgets.QFormLayout(self)

        # 🔹 Alışkanlık adı
        self.name_edit = QtWidgets.QLineEdit(name)
        layout.addRow("Ad:", self.name_edit)

        # 🔹 Kategori (FİLTRELİ)
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(self.CATEGORIES)

        if category in self.CATEGORIES:
            self.category_combo.setCurrentText(category)

        layout.addRow("Kategori:", self.category_combo)

        # 🔹 Sıklık (ZATEN FİLTRELİ)
        self.frequency_combo = QtWidgets.QComboBox()
        self.frequency_combo.addItems(self.FREQUENCIES)

        if frequency in self.FREQUENCIES:
            self.frequency_combo.setCurrentText(frequency)

        layout.addRow("Sıklık:", self.frequency_combo)

        # 🔹 Butonlar
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def get_values(self):
        return (
            self.name_edit.text().strip(),
            self.category_combo.currentText(),
            self.frequency_combo.currentText()
        )
    