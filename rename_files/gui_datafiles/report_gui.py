# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lpsdesk/PycharmProjects/rename_files/rename_files/gui_datafiles/report.ui'
#
# Created: Mon Aug 31 11:49:36 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dlg_report(object):
    def setupUi(self, dlg_report):
        dlg_report.setObjectName(_fromUtf8("dlg_report"))
        dlg_report.resize(900, 371)
        dlg_report.setMinimumSize(QtCore.QSize(650, 250))
        self.verticalLayout = QtGui.QVBoxLayout(dlg_report)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tableWidget = QtGui.QTableWidget(dlg_report)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(6)
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
        self.verticalLayout.addWidget(self.tableWidget)
        self.pushButton = QtGui.QPushButton(dlg_report)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(dlg_report)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), dlg_report.close)
        QtCore.QMetaObject.connectSlotsByName(dlg_report)

    def retranslateUi(self, dlg_report):
        dlg_report.setWindowTitle(_translate("dlg_report", "Report", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("dlg_report", "Object ID", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("dlg_report", "Old Name", None))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("dlg_report", "New Name", None))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("dlg_report", "MD5", None))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("dlg_report", "Internet Archive URL", None))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("dlg_report", "Technical Notes", None))
        self.pushButton.setText(_translate("dlg_report", "Close", None))

