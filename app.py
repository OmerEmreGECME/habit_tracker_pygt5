import sys
from PyQt5 import QtWidgets
from database import Database
from dialogs import LoginDialog
from main_window import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    db = Database()

    login = LoginDialog(db)
    if login.exec_() == QtWidgets.QDialog.Accepted:
        user = db.get_user_by_id(login.user["id"])
        win = MainWindow(db, user)
        win.show()
        app.exec_()
    else:
        print("Kullanıcı oturumu açmadı. Uygulama kapatılıyor.")

if __name__ == "__main__":
    main()
