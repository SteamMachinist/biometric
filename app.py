from threading import Thread

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow
from database_utils import DatabaseUtil


def run_app():
    app = QApplication([])
    window = MainWindow(DatabaseUtil())
    window.show()
    app.exec()


if __name__ == '__main__':
    gui_thread = Thread(target=run_app)
    gui_thread.start()
    gui_thread.join()
