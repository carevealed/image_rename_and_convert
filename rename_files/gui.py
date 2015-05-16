import threading
from time import sleep

__author__ = 'California Audio Visual Preservation Project'
from PySide.QtGui import *
from PySide.QtCore import *
from PIL import Image, ImageQt

from rename_files.renaming_model import RenameFactory, ReportFactory, record_bundle, FileTypes, AccessExtensions, \
    NameRecord, RecordStatus
from rename_files.gui_datafiles.report_gui import Ui_dlg_report
from rename_files.worker import Worker
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
    TESTING = 3
MODE = running_mode.NORMAL

if not MODE == running_mode.TESTING:
    from rename_files.gui_datafiles.rename_gui import Ui_Form

if MODE == running_mode.TESTING:
    from rename_files.gui_datafiles.renameTest_gui import Ui_Form


class text_styles:
    INVALID = "QWidget { background-color: rgb(255, 200, 200); }"
    VALID = "QWidget { background-color: rgb(200, 255, 200); }"

class MainDialog(QDialog, Ui_Form):

    def __init__(self, parent=None, folder=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # NON-UI data members
        self.pixmap = QPixmap()
        self.jobNumber = None

        self.showPreview = True
        self._source = ""
        self._destination = None
        self._pid_prefix = ""
        self._pid_startNum = 0
        self._oid_marc = ""
        self._oid_startNum = 0
        self.reporter = ReportFactory(username="asd")  # TODO: add Username input
        self.copyEngine = Worker(self._destination)
        self.reporter.initize_database()

        # setup

        # hide progress bar
        self.progressBar.setVisible(False)


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
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING or MODE == running_mode.TESTING:
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

        self.tree_files.clicked.connect(self._update_preview_window)

        self.checkBox_preview.clicked.connect(self._toggle_preview)

        self.copyEngine.updateStatus.connect(self._update_statusbar)
        self.copyEngine.reset_progress.connect(self._setup_progress_bar)
        self.copyEngine.update_progress.connect(self._update_progress)

        self.copyEngine.reporter.connect(self._add_record)
        self.copyEngine.request_report.connect(self._run_reports)


    def _update_preview_window(self):
        if self.showPreview:
            file_id = int(self.tree_files.selectedItems()[0].text(0))
            filename = self.copyEngine.builder.find_file(file_id)['source']
            # self.pixmap.load(filename)
            newimage = QPixmap(filename)

            scaled_image = newimage.scaledToWidth(self.preview_image.width())

            self.preview_image.setPixmap(scaled_image)
            self.preview_image.setFixedHeight(scaled_image.height())
            self.lbl_filename.setText(os.path.basename(filename))
            # self.lbl_filename

    def _toggle_preview(self):
        if self.showPreview:
            self.showPreview = False
            self.preview_image.setVisible(False)
            self.lbl_filename.setVisible(False)
        else:
            self.showPreview = True
            self.preview_image.setVisible(True)
            self.lbl_filename.setVisible(True)
        print("Turn {}".format(self.showPreview))

    def _test(self):
        # print(self.gridLayout.getItemPosition(self.pushButton_test.))
        self.report = QDialog(self)
        file_id = int(self.tree_files.selectedItems()[0].text(0))

        self._update_data_status()
        # filename = self.builder.find_file(file_id)['old']
        # image = Image.open(filename)
        # thumbnail = ImageQt.ImageQt(filename)
        # pixmap = QPixmap(filename)
        # scale_ratio = pixmap.width()/self.preview_image.maximumWidth()
        # new_y = pixmap.height() / scale_ratio
        # print("starting frame height: {}".format(self.preview_image.maximumHeight()))
        # print("Image Height: {}".format(pixmap.height()))
        # print("Image Width:  {}".format(pixmap.width()))
        # # self.preview_image.setMinimumHeight(new_y)
        # # self.preview_image.setMinimumHeight(new_y)
        # self.preview_image.setFixedHeight(new_y)
        # print("ratio: {}".format(scale_ratio))
        # print("setting hight to {}".format(new_y))
        # self.preview_image.setPixmap(pixmap)
        # print("Frame height: {}".format(self.preview_image.height()))
        # print("Frame width: {}".format(self.preview_image.width()))

        # print(self.builder.find_file(file_id)['old'])
        # self._debug()

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
            print(self.copyEngine.builder.find_file(file_id))

        print("\n****** DATA Queue ******")
        for queue in self.copyEngine.builder.queues:
            print(queue)

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
        # include_report = self.checkBox_IncludeReport.isChecked()
        self.copyEngine.builder.new_path = self._destination
        # self.copyEngine.setup(destination=self._destination, create_report=include_report, reporter=self.reporter)
        self.copyEngine.start()

    def _show_report(self):
        job = self.reporter.current_batch
        # print("showing report")
        report = ReportDialog(job)
        report.exec_()

    def _save_report(self):
        try:
            generate_report(self.reporter, os.path.join(self.copyEngine.builder.new_path, "report.csv"))
        except FileExistsError:
            msg_box = QMessageBox()
            msg_box.setText("The saving location already has a report, do you wish to overwrite it?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            res = msg_box.exec_()
            if res == QMessageBox.Cancel:
                pass
            elif res == QMessageBox.Yes:
                os.remove(os.path.join(self.copyEngine.builder.new_path, "report.csv"))
                generate_report(self.reporter, os.path.join(self.copyEngine.builder.new_path, "report.csv"))

            elif res == QMessageBox.No:
                # Ask user for another name
                save_box = QFileDialog.getSaveFileName(self, 'Save file', self.copyEngine.builder.new_path, "CSV (*.csv);;All Files (*)")

    def _run_reports(self):
        checked = self.checkBox_IncludeReport.isChecked()
        if checked:
            self._save_report()
        # else:
        #     msg_box = QMessageBox()
        #     msg_box.setText("All files have been successfully saved to {}".format(self._destination))
        #     msg_box.exec_()
        self._show_report()

    def _setup_progress_bar(self, total):
        # self.progressBar.
        self.progressBar.setMaximum(total)
        self.progressBar.setProperty("value", 0)

    def _update_progress(self, value):
        self.progressBar.setProperty("value", value)
        if value < self.progressBar.maximum():
           self.progressBar.setVisible(True)
        else:
            self.progressBar.setVisible(False)

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
            # print("Changing {}".format(id))
            current_status = self.copyEngine.builder.find_file(id)['included']
            self.copyEngine.builder.set_file_include(id, not current_status)
        self.update_tree()

    def _add_record(self, record):
        if record.get_status == RecordStatus.NEED_TO_APPEND_RECORD:
            self.reporter._add_access_files(record)
        self.reporter.add_record(record)


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
        # self.copyEngine.builder.
        self.copyEngine.builder.update(obj_marc=self._oid_marc,
                    obj_start_num=self._oid_startNum,
                    proj_prefix=self._pid_prefix,
                    proj_start_num=self._pid_startNum,
                    path=self._destination)
        for queue in self.copyEngine.builder.queues:
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
                    file['filename'] = ""
                if not queue.isSimple:
                    files.append(QTreeWidgetItem(record, ["", "", file["source"], file['filename'], included]))
                old_names += os.path.basename(file['source']) + " "
                new_names += os.path.basename(file['output_filename']) + " "
                file_id = file['id']
            record.setText(0, str(file_id))
            record.setText(3, old_names)
            record.setText(4, new_names)
            record.setText(6, queue.get_status())
            if queue.files:
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
        self.copyEngine.builder.clear_queues()

        for index, jpeg in enumerate(jpegs):
            files_per_record = record_bundle(self._oid_marc, index+self._oid_startNum, path=destination)
            jpeg_name = os.path.splitext(os.path.basename(jpeg))[0]
            found_tiff = False
            # print(jpeg_name)
            for tiff in tiffs:
                if jpeg_name == os.path.splitext(os.path.basename(tiff))[0]:
                    # print("Found one")

                    # files_per_record.add_file(tiff)
                    # files_per_record.add_file2(file_name=tiff, file_type=FileTypes.MASTER)
                    files_per_record.add_file2(file_name=tiff, file_type=FileTypes.ACCESS, new_format=AccessExtensions.JPEG)
                    found_tiff = True
                    break
            if not found_tiff:
                # files_per_record.add_file(jpeg)
                files_per_record.add_file2(file_name=jpeg, file_type=FileTypes.MASTER)
                # files_per_record.add_file2(file_name=jpeg, file_type=FileTypes.ACCESS)

            self.copyEngine.builder.add_queue(files_per_record,
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
            self.copyEngine.builder.update(obj_marc=self._oid_marc,
                                obj_start_num=self._oid_startNum,
                                proj_prefix=self._pid_prefix,
                                proj_start_num=self._pid_startNum,
                                path=self._destination)

            self.update_tree()
            self.buttonRename.setEnabled(True)
            self._update_statusbar("Updated")


class ReportDialog(QDialog, Ui_dlg_report):

    def __init__(self, jobNumber, parent=None):
        super(ReportDialog, self).__init__(parent)
        if not isinstance(jobNumber, int):
            raise TypeError("Only works with int type, received {}".format(type(jobNumber)))
        self.setupUi(self)
        self.job_number = jobNumber
        self.job_record = None

        self.database = ReportFactory()

        self.load_data()



    def load_data(self):
        self.job_record = self.database.get_job(self.job_number)
        # self.tableWidget.setEnabled(False)
        self.tableWidget.setRowCount(len(self.job_record))
        QMessageBox()
        for row, record in enumerate(self.job_record):
            project_id = record['project_id_prefix'] + "_" + str(record['project_id_number']).zfill(6)
            object_id = record['object_id_prefix'] + "_" + str(record['object_id_number']).zfill(6)

            self.tableWidget.setItem(row, 0, QTableWidgetItem(project_id))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(object_id))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(record['file_name']))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(record['destination']))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(record['ia_url']))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(record['md5']))


def start_gui(folder=None):
    app = QApplication(sys.argv)
    if folder and folder != "":
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("Starting GUI with {}".format(folder))
        form = MainDialog(folder=folder)
    else:
        form = MainDialog()

    form.show()
    app.exec_()



if __name__ == '__main__':
    start_gui()