# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/lpsdesk/PycharmProjects/rename_files/rename_files/gui_datafiles/complex.ui'
#
# Created: Wed Jul 22 15:32:46 2015
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

class Ui_ComplexForm(object):
    def setupUi(self, ComplexForm):
        ComplexForm.setObjectName(_fromUtf8("ComplexForm"))
        ComplexForm.setWindowModality(QtCore.Qt.WindowModal)
        ComplexForm.resize(809, 495)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ComplexForm)
        self.verticalLayout_2.setContentsMargins(5, 1, 1, 1)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.pushButton_add_file = QtGui.QPushButton(ComplexForm)
        self.pushButton_add_file.setObjectName(_fromUtf8("pushButton_add_file"))
        self.gridLayout.addWidget(self.pushButton_add_file, 0, 1, 1, 1)
        self.columnView_files = QtGui.QColumnView(ComplexForm)
        self.columnView_files.setObjectName(_fromUtf8("columnView_files"))
        self.gridLayout.addWidget(self.columnView_files, 0, 0, 2, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.pushButton_remove_file = QtGui.QPushButton(ComplexForm)
        self.pushButton_remove_file.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.pushButton_remove_file.setObjectName(_fromUtf8("pushButton_remove_file"))
        self.gridLayout.addWidget(self.pushButton_remove_file, 2, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton_cancle = QtGui.QPushButton(ComplexForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_cancle.sizePolicy().hasHeightForWidth())
        self.pushButton_cancle.setSizePolicy(sizePolicy)
        self.pushButton_cancle.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_cancle.setObjectName(_fromUtf8("pushButton_cancle"))
        self.horizontalLayout.addWidget(self.pushButton_cancle)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.pushButton_add_object = QtGui.QPushButton(ComplexForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_add_object.sizePolicy().hasHeightForWidth())
        self.pushButton_add_object.setSizePolicy(sizePolicy)
        self.pushButton_add_object.setMinimumSize(QtCore.QSize(100, 0))
        self.pushButton_add_object.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_add_object.setObjectName(_fromUtf8("pushButton_add_object"))
        self.horizontalLayout.addWidget(self.pushButton_add_object)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)
        self.listView_files = QtGui.QListView(ComplexForm)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listView_files.sizePolicy().hasHeightForWidth())
        self.listView_files.setSizePolicy(sizePolicy)
        self.listView_files.setMaximumSize(QtCore.QSize(16777215, 100))
        self.listView_files.setObjectName(_fromUtf8("listView_files"))
        self.gridLayout.addWidget(self.listView_files, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(ComplexForm)
        QtCore.QMetaObject.connectSlotsByName(ComplexForm)

    def retranslateUi(self, ComplexForm):
        ComplexForm.setWindowTitle(_translate("ComplexForm", "Add Complex Object", None))
        self.pushButton_add_file.setText(_translate("ComplexForm", "Add Selected", None))
        self.pushButton_remove_file.setText(_translate("ComplexForm", "Remove Selected", None))
        self.pushButton_cancle.setText(_translate("ComplexForm", "Cancle", None))
        self.pushButton_add_object.setText(_translate("ComplexForm", "Add Object", None))

