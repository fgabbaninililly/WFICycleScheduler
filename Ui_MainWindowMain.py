from PyQt5 import QtWidgets

from Ui_MainWindowSub import Ui_MainWindowSub

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindowSub()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())