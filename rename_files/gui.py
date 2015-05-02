__author__ = 'California Audio Visual Preservation Project'
from PySide.QtGui import *
from PySide.QtCore import *
# from rename_files.gui_datafiles import Ui_Form
from rename_files.gui_datafiles.gui_view import Ui_Form
from rename_files.renaming_model import RenameFactory, ReportFactory, record_bundle
from enum import Enum
import sys
import argparse
from enum import Enum
import os
from rename_files.renaming_controller import generate_report


class running_mode(Enum):
    NORMAL = 0
    DEBUG = 1
    BUIDING = 2
MODE = running_mode.BUIDING


class text_styles:
    INVALID = "QWidget { background-color: rgb(255, 200, 200); }"
    VALID = "QWidget { background-color: rgb(200, 255, 200); }"

class MainDialog(QDialog, Ui_Form):

    def __init__(self, parent=None, folder=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # NON-UI data members
        self.builder = RenameFactory()
        self._source = ""
        self._destination = ""
        self._pid_prefix = ""
        self._pid_startNum = 0
        self._oid_marc = ""
        self._oid_startNum = 0
        self.reporter = ReportFactory(username="asd")  # TODO: add Username input
        self.reporter.initize_database()

        # setup UI

        # include a status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QWidget {border: 1px solid grey; border-radius: 3px; }")
        self.gridLayout_3.addWidget(self.status_bar)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameSetup.sizePolicy().hasHeightForWidth())
        self._update_statusbar("Idle")

        self.status_bar.setSizePolicy(sizePolicy)

        # hide the first column in normal mode
        if MODE == running_mode.NORMAL:
            self.tree_files.hideColumn(0)

        # set a test button if debut or building mode is on
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            self.pushButton_test = QPushButton(self.frameSetup)
            self.pushButton_test.setAutoFillBackground(False)
            self.pushButton_test.setFlat(False)
            self.pushButton_test.setObjectName("pushButton_test")
            self.pushButton_test.setText("Test")
            self.gridLayout.addWidget(self.pushButton_test, 2, 0, 3, 0)
            self.pushButton_test.clicked.connect(self._test)

        if folder:
            self.lineEdit_source.insert(folder)
        if MODE == running_mode.BUIDING:
            self.lineEdit_destination.insert("/Volumes/CAVPPTestDrive/test1")
            self.lineEdit_OID_MARC.insert("c")

        # setup signals and slots
        self.lineEdit_destination.textChanged.connect(self._update_destination)
        self._update_destination(self.lineEdit_destination.text())

        self.lineEdit_source.textChanged.connect(self._update_source)
        self._update_source(self.lineEdit_source.text())

        self.lineEdit_OID_MARC.textChanged.connect(self._update_oid_marc)
        self._update_oid_marc(self.lineEdit_OID_MARC.text())

        self.lineEdit_OID_startNum.textChanged.connect(self._update_oid_startNum)
        self._update_oid_startNum(self.lineEdit_OID_startNum.text())

        self.lineEdit_PID_prefix.textChanged.connect(self._update_pid_prefix)
        self._update_pid_prefix(self.lineEdit_PID_prefix.text())

        self.lineEdit_PID_startNum.textChanged.connect(self._update_pid_startNum)
        self._update_pid_startNum(self.lineEdit_PID_startNum.text())

        self.pushButton_sourceBrowse.clicked.connect(self.browse_source)
        self.pushButton_destinationBrowse.clicked.connect(self.browse_destination)

        self.pushButton_include.clicked.connect(self._include_selection)

        self.pushButton_load_filles.clicked.connect(self._load_files_click)
        self.pushButton_update.clicked.connect(self.update_click)

        self.buttonRename.clicked.connect(self._copy_files)



    def _test(self):
        # print(self.gridLayout.getItemPosition(self.pushButton_test.))

        self._update_data_status()
        self._debug()

    def _debug(self):
        data_members = self.__dict__
        # print(type(data_members))
        # print("\n****** Attributes ******")
        # for key, value in data_members.items():
        #     print("  {:30}: {}".format(key, value), )

        print("\n****** DATA TREE Selected ******")
        for item in self.tree_files.selectedItems():
            file_id = int(item.text(0))
            # print("  {}".format(file_id))
            print(self.builder.find_file(file_id))

        # print("\n****** DATA Queue ******")
        # for queue in self.builder.queues:
        #     print(queue)

    def _load_files_click(self):
        self.load_files(source=self.lineEdit_source.text(), destination=self._destination)

    def _update_statusbar(self, message):
        self.status_bar.showMessage("Status: {}".format(message))

    def _update_source(self, new_source):
        self._source = new_source
        self._update_data_status()

    def _update_destination(self, new_destination):
        self._destination = new_destination
        self._update_data_status()

    def _copy_files(self):
        success = True
        print("Copying the files")

        for i in self.builder.queues:
            record = self.builder.execute_rename_from_queue_by_record(i)
            # print(i.get_dict()['project id'])
            self._update_statusbar("Copying {}".format(i.get_dict()['project id']))
            self.reporter.add_record(record)
        if self.checkBox_IncludeReport.isChecked():
            # print("Generating report")
            report = os.path.join(self._destination, "report.csv")
            generate_report(self.reporter, report)
            self._update_statusbar("Report generated to {}".format(report))
        print(success)
    def _update_pid_prefix(self, new_prefix):
        self._pid_prefix = new_prefix
        self._update_data_status()

    def _update_pid_startNum(self, new_number):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("updating PID: {}".format(new_number))
        try:
            self._pid_startNum = int(new_number)
            self.lineEdit_PID_startNum.setStyleSheet(text_styles.VALID)
        except ValueError:
            self.lineEdit_PID_startNum.setStyleSheet(text_styles.INVALID)
            self._pid_startNum = None
        self._update_data_status()

    def _update_oid_marc(self, new_marc):
        self._oid_marc = new_marc
        self._update_data_status()


    def _update_oid_startNum(self, new_number):
        try:
            self._oid_startNum = int(new_number)
            self.lineEdit_OID_startNum.setStyleSheet(text_styles.VALID)
        except ValueError:
            self.lineEdit_OID_startNum.setStyleSheet(text_styles.INVALID)
            self._oid_startNum = None
        self._update_data_status()


    def _update_data_status(self):

        valid = True

        # source
        if os.path.exists(self._source):
            self.lineEdit_source.setStyleSheet(text_styles.VALID)
        else:
            self.lineEdit_source.setStyleSheet(text_styles.INVALID)
            valid = False

        # destination
        if os.path.exists(self._destination):
            self.lineEdit_destination.setStyleSheet(text_styles.VALID)
        else:
            self.lineEdit_destination.setStyleSheet(text_styles.INVALID)
            valid = False

        # pid prefix
        if self._pid_prefix == "":
            self.lineEdit_PID_prefix.setStyleSheet(text_styles.INVALID)
            valid = False
        else:
            self.lineEdit_PID_prefix.setStyleSheet(text_styles.VALID)

        # OID MARC
        if self._oid_marc == "":
            self.lineEdit_OID_MARC.setStyleSheet(text_styles.INVALID)
            valid = False
        else:
            self.lineEdit_OID_MARC.setStyleSheet(text_styles.VALID)
        if not self._pid_startNum:
            valid = False
        if not self._oid_startNum:
            valid = False

        self.lineEdit_validStatus.clear()
        if valid:
            self.lineEdit_validStatus.insert("Valid")
            self.lineEdit_validStatus.setStyleSheet(text_styles.VALID)
            self.pushButton_load_filles.setEnabled(True)
            self.pushButton_update.setEnabled(True)
        else:
            self.lineEdit_validStatus.insert("Not Valid")
            self.lineEdit_validStatus.setStyleSheet(text_styles.INVALID)
            self.pushButton_load_filles.setEnabled(False)
            self.buttonRename.setEnabled(False)
            self.pushButton_update.setEnabled(False)

    def _include_selection(self):
        for item in self.tree_files.selectedItems():
            id = int(item.text(0))
            print("Changing {}".format(id))
            current_status = self.builder.find_file(id)['included']
            self.builder.set_file_include(id, not current_status)
        self.update_tree()

    def closeEvent(self, *args, **kwargs):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("Closing Database")
        self.reporter.close_database()



    def load_source(self, folder_name):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("Loading {} into source".format(folder_name))
        self.lineEdit_source.clear()
        self.lineEdit_source.insert(folder_name)


    def browse_source(self):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("Browsing source")
        source = QFileDialog.getExistingDirectory(self, 'Source')
        if source:
            self.load_source(source)

    def load_destination(self, folder_name):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("Loading {} into destination".format(folder_name))
        self.lineEdit_destination.clear()
        self.lineEdit_destination.insert(folder_name)

        pass

    def browse_destination(self):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("Browsing Destination")
        destination = QFileDialog.getExistingDirectory(self, 'Destination')
        if destination:
            self.load_destination(destination)

    def update_tree(self):
        records = []
        self.tree_files.clear()
        for queue in self.builder.queues:
            simple = "Simple"
            old_names = ""
            new_names = ""
            files = []
            file_id = ""

            if not queue.isSimple:
                simple = "Complex"
            record = QTreeWidgetItem(self.tree_files, ["", queue.project_id, simple])

            for file in queue.files:
                included = "Included"
                if not file['included']:
                    included = "Excluded"

                if not queue.isSimple:
                    files.append(QTreeWidgetItem(record, ["", "", file["old"], file['new'], included]))
                old_names += os.path.basename(file['old']) + " "
                new_names += os.path.basename(file['new']) + " "
                file_id = file['id']
            record.setText(0, str(file_id))
            record.setText(3, old_names)
            record.setText(4, new_names)
            record.setText(6, queue.get_status())
            if queue.isSimple:
                included = "Included"
                if not queue.files[0]['included']:
                    included = "Excluded"
                record.setText(5, included)

            records.append(record)
        self.tree_files.addTopLevelItems(records)

    def load_files(self, source, destination=None):
        tiffs = []
        jpegs = []


        # destination = "/Volumes/CAVPPTestDrive/"

        newfile = ""

        self.tree_files.clear()
        # get all the files that match either tif or jpg
        for root, subdirs, files in os.walk(source):
            for index, file in enumerate(files):
                if os.path.splitext(file)[1] == '.tif':
                    newfile = os.path.join(root, file)
                    tiffs.append(newfile)
                if os.path.splitext(file)[1] == '.jpg':
                    newfile = os.path.join(root, file)
                    jpegs.append(newfile)
        self.builder.clear_queues()

        for index, jpeg in enumerate(jpegs):
            files_per_record = record_bundle(self._oid_marc, index+self._oid_startNum, path=destination)
            jpeg_name = os.path.splitext(os.path.basename(jpeg))[0]
            found_tiff = False
            # print(jpeg_name)
            for tiff in tiffs:
                if jpeg_name == os.path.splitext(os.path.basename(tiff))[0]:
                    # print("Found one")
                    files_per_record.add_file(tiff)
                    found_tiff = True
                    break
            if not found_tiff:
                files_per_record.add_file(jpeg)
            self.builder.add_queue(files_per_record,
                              obj_id_prefix=self._oid_marc,
                              obj_id_num=index + self._oid_startNum,
                              proj_id_prefix=self._pid_prefix,
                              proj_id_num=index + self._pid_startNum)
        self.buttonRename.setEnabled(True)
        self.update_tree()

    def update_click(self):
        if os.path.isdir(self.lineEdit_source.text()):
            if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
                print("Updating tree")
            self._update_statusbar("Updating")
            self.builder.update(obj_marc=self._oid_marc,
                                obj_start_num=self._oid_startNum,
                                proj_prefix=self._pid_prefix,
                                proj_start_num=self._pid_startNum,
                                path=self._destination)
            # self.load_files(source=self.lineEdit_source.text(), destination=self._destination)
            self.update_tree()
            self.buttonRename.setEnabled(True)
            self._update_statusbar("Updated")

def start_gui(folder=None):
    if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
        print("Starting GUI with {}".format(folder))
    app = QApplication(sys.argv)
    form = MainDialog(folder=folder)
    form.show()
    app.exec_()

if __name__ == '__main__':
    start_gui()