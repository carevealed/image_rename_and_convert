# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rename_gui.ui'
#
# Created: Wed Apr 29 14:55:40 2015
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 650)
        Form.setMinimumSize(QtCore.QSize(600, 650))
        self.gridLayout_3 = QtGui.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.frameBackground = QtGui.QFrame(Form)
        self.frameBackground.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameBackground.setFrameShadow(QtGui.QFrame.Raised)
        self.frameBackground.setObjectName("frameBackground")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frameBackground)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frameTitle = QtGui.QFrame(self.frameBackground)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameTitle.sizePolicy().hasHeightForWidth())
        self.frameTitle.setSizePolicy(sizePolicy)
        self.frameTitle.setMinimumSize(QtCore.QSize(0, 50))
        self.frameTitle.setMaximumSize(QtCore.QSize(16777215, 50))
        self.frameTitle.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameTitle.setFrameShadow(QtGui.QFrame.Raised)
        self.frameTitle.setObjectName("frameTitle")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.frameTitle)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_title = QtGui.QLabel(self.frameTitle)
        font = QtGui.QFont()
        font.setPointSize(23)
        font.setWeight(75)
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.verticalLayout_3.addWidget(self.label_title)
        self.verticalLayout_2.addWidget(self.frameTitle)
        self.frameSetup = QtGui.QFrame(self.frameBackground)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameSetup.sizePolicy().hasHeightForWidth())
        self.frameSetup.setSizePolicy(sizePolicy)
        self.frameSetup.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameSetup.setFrameShadow(QtGui.QFrame.Plain)
        self.frameSetup.setObjectName("frameSetup")
        self.gridLayout = QtGui.QGridLayout(self.frameSetup)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_destinationBrowse = QtGui.QPushButton(self.frameSetup)
        self.pushButton_destinationBrowse.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_destinationBrowse.setObjectName("pushButton_destinationBrowse")
        self.gridLayout.addWidget(self.pushButton_destinationBrowse, 1, 4, 1, 1)
        self.pushButton_sourceBrowse = QtGui.QPushButton(self.frameSetup)
        self.pushButton_sourceBrowse.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pushButton_sourceBrowse.setObjectName("pushButton_sourceBrowse")
        self.gridLayout.addWidget(self.pushButton_sourceBrowse, 0, 4, 1, 1)
        self.label_destination = QtGui.QLabel(self.frameSetup)
        self.label_destination.setObjectName("label_destination")
        self.gridLayout.addWidget(self.label_destination, 1, 0, 1, 1)
        self.lineEdit_OID_MARC = QtGui.QLineEdit(self.frameSetup)
        self.lineEdit_OID_MARC.setObjectName("lineEdit_OID_MARC")
        self.gridLayout.addWidget(self.lineEdit_OID_MARC, 4, 1, 1, 1)
        self.label_source = QtGui.QLabel(self.frameSetup)
        self.label_source.setObjectName("label_source")
        self.gridLayout.addWidget(self.label_source, 0, 0, 1, 1)
        self.lineEdit_PID_MARC = QtGui.QLineEdit(self.frameSetup)
        self.lineEdit_PID_MARC.setObjectName("lineEdit_PID_MARC")
        self.gridLayout.addWidget(self.lineEdit_PID_MARC, 3, 1, 1, 1)
        self.label_OID_MARC = QtGui.QLabel(self.frameSetup)
        self.label_OID_MARC.setObjectName("label_OID_MARC")
        self.gridLayout.addWidget(self.label_OID_MARC, 4, 0, 1, 1)
        self.label_OID_startNum = QtGui.QLabel(self.frameSetup)
        self.label_OID_startNum.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_OID_startNum.setObjectName("label_OID_startNum")
        self.gridLayout.addWidget(self.label_OID_startNum, 4, 2, 1, 1)
        self.label_PID_startNum = QtGui.QLabel(self.frameSetup)
        self.label_PID_startNum.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_PID_startNum.setObjectName("label_PID_startNum")
        self.gridLayout.addWidget(self.label_PID_startNum, 3, 2, 1, 2)
        self.label_PID_MARC = QtGui.QLabel(self.frameSetup)
        self.label_PID_MARC.setObjectName("label_PID_MARC")
        self.gridLayout.addWidget(self.label_PID_MARC, 3, 0, 1, 1)
        self.lineEdit_OID_startNum = QtGui.QLineEdit(self.frameSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_OID_startNum.sizePolicy().hasHeightForWidth())
        self.lineEdit_OID_startNum.setSizePolicy(sizePolicy)
        self.lineEdit_OID_startNum.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_OID_startNum.setObjectName("lineEdit_OID_startNum")
        self.gridLayout.addWidget(self.lineEdit_OID_startNum, 4, 4, 1, 1)
        self.lineEdit_PID_startNum = QtGui.QLineEdit(self.frameSetup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_PID_startNum.sizePolicy().hasHeightForWidth())
        self.lineEdit_PID_startNum.setSizePolicy(sizePolicy)
        self.lineEdit_PID_startNum.setMaximumSize(QtCore.QSize(100, 16777215))
        self.lineEdit_PID_startNum.setObjectName("lineEdit_PID_startNum")
        self.gridLayout.addWidget(self.lineEdit_PID_startNum, 3, 4, 1, 1)
        self.lineEdit_destination = QtGui.QLineEdit(self.frameSetup)
        self.lineEdit_destination.setObjectName("lineEdit_destination")
        self.gridLayout.addWidget(self.lineEdit_destination, 1, 1, 1, 3)
        self.lineEdit_source = QtGui.QLineEdit(self.frameSetup)
        self.lineEdit_source.setObjectName("lineEdit_source")
        self.gridLayout.addWidget(self.lineEdit_source, 0, 1, 1, 3)
        self.verticalLayout_2.addWidget(self.frameSetup)
        self.frameFiles = QtGui.QFrame(self.frameBackground)
        self.frameFiles.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameFiles.setFrameShadow(QtGui.QFrame.Raised)
        self.frameFiles.setObjectName("frameFiles")
        self.verticalLayout = QtGui.QVBoxLayout(self.frameFiles)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tree_files = QtGui.QTreeWidget(self.frameFiles)
        self.tree_files.setObjectName("tree_files")
        item_0 = QtGui.QTreeWidgetItem(self.tree_files)
        item_0 = QtGui.QTreeWidgetItem(self.tree_files)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        item_1 = QtGui.QTreeWidgetItem(item_0)
        self.verticalLayout.addWidget(self.tree_files)
        self.frame = QtGui.QFrame(self.frameFiles)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.pushButton_update = QtGui.QPushButton(self.frame)
        self.pushButton_update.setObjectName("pushButton_update")
        self.gridLayout_2.addWidget(self.pushButton_update, 2, 1, 1, 2)
        self.pushButton_include = QtGui.QPushButton(self.frame)
        self.pushButton_include.setObjectName("pushButton_include")
        self.gridLayout_2.addWidget(self.pushButton_include, 1, 2, 1, 1)
        self.pushButton_group = QtGui.QPushButton(self.frame)
        self.pushButton_group.setAutoFillBackground(False)
        self.pushButton_group.setFlat(False)
        self.pushButton_group.setObjectName("pushButton_group")
        self.gridLayout_2.addWidget(self.pushButton_group, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.verticalLayout_2.addWidget(self.frameFiles)
        self.frameActions = QtGui.QFrame(self.frameBackground)
        self.frameActions.setMaximumSize(QtCore.QSize(16777215, 50))
        self.frameActions.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameActions.setFrameShadow(QtGui.QFrame.Plain)
        self.frameActions.setObjectName("frameActions")
        self.horizontalLayout = QtGui.QHBoxLayout(self.frameActions)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.checkBoxIncludeReport = QtGui.QCheckBox(self.frameActions)
        self.checkBoxIncludeReport.setEnabled(True)
        self.checkBoxIncludeReport.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.checkBoxIncludeReport.setChecked(True)
        self.checkBoxIncludeReport.setObjectName("checkBoxIncludeReport")
        self.horizontalLayout.addWidget(self.checkBoxIncludeReport)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.buttonRename = QtGui.QPushButton(self.frameActions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonRename.sizePolicy().hasHeightForWidth())
        self.buttonRename.setSizePolicy(sizePolicy)
        self.buttonRename.setMinimumSize(QtCore.QSize(150, 0))
        self.buttonRename.setMaximumSize(QtCore.QSize(400, 16777215))
        self.buttonRename.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.buttonRename.setObjectName("buttonRename")
        self.horizontalLayout.addWidget(self.buttonRename)
        self.verticalLayout_2.addWidget(self.frameActions)
        self.gridLayout_3.addWidget(self.frameBackground, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "CAPS Renaming Script", None, QtGui.QApplication.UnicodeUTF8))
        self.label_title.setText(QtGui.QApplication.translate("Form", "CAPS Renaming Script", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_destinationBrowse.setText(QtGui.QApplication.translate("Form", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_sourceBrowse.setText(QtGui.QApplication.translate("Form", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_destination.setText(QtGui.QApplication.translate("Form", "Destination:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_source.setText(QtGui.QApplication.translate("Form", "Source:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_OID_MARC.setText(QtGui.QApplication.translate("Form", "Object ID MARC:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_OID_startNum.setText(QtGui.QApplication.translate("Form", "Start Number:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_PID_startNum.setText(QtGui.QApplication.translate("Form", "Start Number:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_PID_MARC.setText(QtGui.QApplication.translate("Form", "Project ID MARC:", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.headerItem().setText(0, QtGui.QApplication.translate("Form", "Project ID", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.headerItem().setText(1, QtGui.QApplication.translate("Form", "Simple/Complex", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.headerItem().setText(2, QtGui.QApplication.translate("Form", "Original Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.headerItem().setText(3, QtGui.QApplication.translate("Form", "New Name", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.headerItem().setText(4, QtGui.QApplication.translate("Form", "Included/Excluded", None, QtGui.QApplication.UnicodeUTF8))
        __sortingEnabled = self.tree_files.isSortingEnabled()
        self.tree_files.setSortingEnabled(False)
        self.tree_files.topLevelItem(0).setText(0, QtGui.QApplication.translate("Form", "CAPS1010", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(0).setText(1, QtGui.QApplication.translate("Form", "Simple", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(0).setText(2, QtGui.QApplication.translate("Form", "ana109.tif", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(0).setText(3, QtGui.QApplication.translate("Form", "ANA_00181_prsv.jpg", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(0).setText(4, QtGui.QApplication.translate("Form", "Included", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).setText(0, QtGui.QApplication.translate("Form", "CAPS1011", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).setText(1, QtGui.QApplication.translate("Form", "Complex", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).setText(2, QtGui.QApplication.translate("Form", "ana110.tif .. ana113.tif", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).setText(3, QtGui.QApplication.translate("Form", "ANA_00182_001_prsv.jpg .. ANA_00182_004_prsv.jpg", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).setText(4, QtGui.QApplication.translate("Form", "Included", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(0).setText(2, QtGui.QApplication.translate("Form", "ana110.tif", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(0).setText(3, QtGui.QApplication.translate("Form", "ANA_00182_001_prsv.jpg", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(0).setText(4, QtGui.QApplication.translate("Form", "Included", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(1).setText(2, QtGui.QApplication.translate("Form", "ana111.tif", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(1).setText(3, QtGui.QApplication.translate("Form", "ANA_00182_002_prsv.jpg", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(1).setText(4, QtGui.QApplication.translate("Form", "Included", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(2).setText(2, QtGui.QApplication.translate("Form", "ana112.tif", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(2).setText(3, QtGui.QApplication.translate("Form", "ANA_00182_003_prsv.jpg", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(2).setText(4, QtGui.QApplication.translate("Form", "Included", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(3).setText(2, QtGui.QApplication.translate("Form", "ana113.tif", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(3).setText(3, QtGui.QApplication.translate("Form", "ANA_00182_004_prsv.jpg", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.topLevelItem(1).child(3).setText(4, QtGui.QApplication.translate("Form", "Included", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_files.setSortingEnabled(__sortingEnabled)
        self.pushButton_update.setText(QtGui.QApplication.translate("Form", "Update", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_include.setText(QtGui.QApplication.translate("Form", "Include/Exclude", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_group.setText(QtGui.QApplication.translate("Form", "Group/Ungroup", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxIncludeReport.setText(QtGui.QApplication.translate("Form", "Include Report", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRename.setText(QtGui.QApplication.translate("Form", "Rename", None, QtGui.QApplication.UnicodeUTF8))

