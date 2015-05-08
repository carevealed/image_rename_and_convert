# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lpsdesk/PycharmProjects/rename_files/rename_files/gui_datafiles/report.ui'
#
# Created: Fri May  8 16:06:27 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_dlg_report(object):
    def setupUi(self, dlg_report):
        dlg_report.setObjectName("dlg_report")
        dlg_report.resize(650, 250)
        dlg_report.setMinimumSize(QtCore.QSize(650, 250))
        self.verticalLayout = QtGui.QVBoxLayout(dlg_report)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtGui.QTableWidget(dlg_report)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        self.verticalLayout.addWidget(self.tableWidget)
        self.pushButton = QtGui.QPushButton(dlg_report)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(dlg_report)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL("clicked()"), dlg_report.close)
        QtCore.QMetaObject.connectSlotsByName(dlg_report)

    def retranslateUi(self, dlg_report):
        dlg_report.setWindowTitle(QtGui.QApplication.translate("dlg_report", "Report", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("dlg_report", "Project ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("dlg_report", "Object ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(2).setText(QtGui.QApplication.translate("dlg_report", "Old Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(3).setText(QtGui.QApplication.translate("dlg_report", "New Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(4).setText(QtGui.QApplication.translate("dlg_report", "Internet Archive URL", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(5).setText(QtGui.QApplication.translate("dlg_report", "MD5", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.horizontalHeaderItem(6).setText(QtGui.QApplication.translate("dlg_report", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("dlg_report", "Close", None, QtGui.QApplication.UnicodeUTF8))

