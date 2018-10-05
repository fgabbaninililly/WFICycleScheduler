# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addcyclepanel.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(562, 240)
        Dialog.setAutoFillBackground(False)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(380, 200, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 541, 181))
        self.groupBox.setObjectName("groupBox")
        self.lblCycle = QtWidgets.QLabel(self.groupBox)
        self.lblCycle.setGeometry(QtCore.QRect(20, 60, 26, 20))
        self.lblCycle.setObjectName("lblCycle")
        self.lblEnd = QtWidgets.QLabel(self.groupBox)
        self.lblEnd.setGeometry(QtCore.QRect(20, 150, 141, 20))
        self.lblEnd.setObjectName("lblEnd")
        self.lblStart = QtWidgets.QLabel(self.groupBox)
        self.lblStart.setGeometry(QtCore.QRect(20, 125, 141, 16))
        self.lblStart.setObjectName("lblStart")
        self.lblComponent = QtWidgets.QLabel(self.groupBox)
        self.lblComponent.setGeometry(QtCore.QRect(20, 30, 84, 20))
        self.lblComponent.setObjectName("lblComponent")
        self.cmbCycleName = QtWidgets.QComboBox(self.groupBox)
        self.cmbCycleName.setGeometry(QtCore.QRect(200, 60, 331, 20))
        self.cmbCycleName.setObjectName("cmbCycleName")
        self.dtEditStart = QtWidgets.QDateTimeEdit(self.groupBox)
        self.dtEditStart.setGeometry(QtCore.QRect(200, 120, 161, 20))
        self.dtEditStart.setObjectName("dtEditStart")
        self.dtEditEnd = QtWidgets.QDateTimeEdit(self.groupBox)
        self.dtEditEnd.setGeometry(QtCore.QRect(200, 150, 161, 20))
        self.dtEditEnd.setObjectName("dtEditEnd")
        self.cmbComponentName = QtWidgets.QComboBox(self.groupBox)
        self.cmbComponentName.setGeometry(QtCore.QRect(200, 30, 331, 20))
        self.cmbComponentName.setObjectName("cmbComponentName")
        self.lblSubPhase = QtWidgets.QLabel(self.groupBox)
        self.lblSubPhase.setGeometry(QtCore.QRect(20, 90, 61, 20))
        self.lblSubPhase.setObjectName("lblSubPhase")
        self.cmbSubPhase = QtWidgets.QComboBox(self.groupBox)
        self.cmbSubPhase.setGeometry(QtCore.QRect(200, 90, 331, 20))
        self.cmbSubPhase.setObjectName("cmbSubPhase")

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add a Cycle"))
        self.groupBox.setTitle(_translate("Dialog", "Add a new cycle"))
        self.lblCycle.setText(_translate("Dialog", "Cycle"))
        self.lblEnd.setText(_translate("Dialog", "Do not end after this time"))
        self.lblStart.setText(_translate("Dialog", "Do not start before this time"))
        self.lblComponent.setText(_translate("Dialog", "Component"))
        self.lblSubPhase.setText(_translate("Dialog", "Sub Phase"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

