import datetime
import time
import threading
from time import sleep

__author__ = 'California Audio Visual Preservation Project'
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PIL import Image

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
import traceback

COLOR_MODES = dict({"1": "1-bit pixels, black and white, stored with one pixel per byte",
                    "L": "8-bit pixels, black and white",
                    "P": "8-bit pixels, mapped to any other mode using a color palette",
                    "RGB": "3x8-bit pixels, true color",
                    "RGBA": "4x8-bit pixels, true color with transparency mask",
                    "CMYK": "4x8-bit pixels, color separation",
                    "YCbCr": "3x8-bit pixels, color video format",
                    "LAB": "3x8-bit pixels, the L*a*b color space",
                    "HSV": "3x8-bit pixels, Hue, Saturation, Value color space",
                    "I": "32-bit signed integer pixels",
                    "F": "32-bit floating point pixels"})

class running_mode(Enum):
    NORMAL = 0
    DEBUG = 1
    BUIDING = 2
    TESTING = 3

MODE = running_mode.NORMAL
datafile = None


if not MODE == running_mode.TESTING:
    from rename_files.gui_datafiles.rename_gui import Ui_Form

if MODE == running_mode.TESTING:
    from rename_files.gui_datafiles.renameTest_gui import Ui_Form


class text_styles:
    INVALID = "QWidget { background-color: rgb(255, 200, 200); }"
    VALID = "QWidget { background-color: rgb(200, 255, 200); }"

class MainDialog(QDialog, Ui_Form):
    halt_worker = pyqtSignal()
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
        self.reporter = ReportFactory(database=datafile, username="asd")  # TODO: add Username input
        self.copyEngine = Worker(self._destination)
        self.reporter.initize_database()

        # setup

        # hide progress bar
        self.progressBar.setVisible(False)

        # hide metadata stats

        # self.le_resolution.setVisible(False)
        # self.lbl_resolution.setVisible(False)
        # self.lbl_fileSize.setVisible(False)
        # self.le_fileSize.setVisible(False)
        # self.lbl_colorDepth.setVisible(False)
        # self.le_colorDepth.setVisible(False)

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
            self.tree_files.hideColumn(1)
            self.tree_files.hideColumn(2)

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
        self.pushButton_load_filles.clicked.connect(self._load_files_click)
        self.pushButton_update.clicked.connect(self.update_click)

        self.pushButton_group.clicked.connect(self._group_selected)

        self.buttonRename.clicked.connect(self._copy_files)

        self.tree_files.clicked.connect(self._update_preview_window)

        self.checkBox_preview.clicked.connect(self._toggle_preview)

        self.copyEngine.updateStatus.connect(self._update_statusbar)
        self.copyEngine.reset_progress.connect(self._setup_progress_bar)
        self.copyEngine.update_progress.connect(self._update_progress)

        self.copyEngine.reporter.connect(self._add_record)
        self.copyEngine.request_report.connect(self._run_reports)
        self.copyEngine.error_reporter.connect(self._display_error)


    def _update_preview_window(self):
        if self.showPreview:
            # dummy = self.tree_files.selectedItems()[0].parent()
            if self.tree_files.selectedItems()[0].parent():
                item = self.tree_files.selectedItems()[0].parent()
            else:
                item = self.tree_files.selectedItems()[0]
            file_id = int(item.text(2))
            # file_id
            filename = self.copyEngine.builder.find_file(file_id).source
            # self.pixmap.load(filename)

            newimage = QPixmap(filename)
            imageMetadata = Image.open(filename)


            self.le_color.setText(COLOR_MODES[imageMetadata.mode])
            # scaled_image = newimage.scaledToWidth(self.preview_image.width())
            top_size = self.frame_preview.height() - self.frame_7.height() - 20
            scaled_image = newimage.scaledToHeight(top_size)
            # print(scaled_image.height())
            # print()
            self.le_fileSize.setText((str(int(os.path.getsize(filename)/1024)) + " Kb"))
            self.preview_image.setPixmap(scaled_image)
            # self.preview_image.setMinimumWidth(scaled_image.width())
            self.preview_image.setMinimumHeight(scaled_image.height())
            self.le_fileName.setText(os.path.basename(filename))
            resolution = str(newimage.width()) + " x " + str(newimage.height())

            self.le_resolution.setText(resolution)



    def _toggle_preview(self):
        if self.showPreview:
            self.frame_preview.setVisible(False)
            self.showPreview = False
            # self.preview_image.setVisible(False)
            # self.lbl_filename.setVisible(False)
            # self.frame_7.setVisible(False)
        else:
            self.frame_preview.setVisible(True)
            self.showPreview = True
            # self.preview_image.setVisible(True)
            # self.lbl_filename.setVisible(True)
            # self.frame_7.setVisible(True)
        print("Turn {}".format(self.showPreview))
    def _display_error(self, message):
        # error_message = QErrorMessage(self)
        QMessageBox.critical(self,"Converting Error", message)
        # error_message.showMessage(message)
        self.copyEngine.resume()

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
        if self.cb_searchType.currentIndex() == 0:
            smart = True
        else:
            smart = False
        self.load_files(source=self.lineEdit_source.text(), destination=self._destination, smart_sorting=smart)

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
            hasParent =item.parent()
            if hasParent:
                id = int(item.parent().text(1))
            # parent = item.parent()
            else:
                id = int(item.text(1))
            current_status = self.copyEngine.builder.find_queue(id).included
            self.copyEngine.builder.set_file_include(id, not current_status)
        self.update_tree()

    def _add_record(self, record):
        # print(record.get_status())
        # if record._status == RecordStatus.NEED_TO_APPEND_RECORD:
        #     self.reporter._add_access_files(record)
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

    def _group_selected(self):
        print("Making selection a complex object.")
        to_group = []
        for item in self.tree_files.selectedItems():
            hasParent =item.parent()
            if hasParent:
                id = int(item.parent().text(1))
            # parent = item.parent()
            else:
                id = int(item.text(1))
            to_group.append(id)
        print(to_group)
        self.update_tree()

    def update_tree(self):
        records = []
        self.tree_files.clear()
        self.copyEngine.builder.update2(self._pid_prefix, self._pid_startNum, self._oid_marc, self._oid_startNum, self._destination)
        # self.copyEngine.builder.update(obj_marc=self._oid_marc,
        #             obj_start_num=self._oid_startNum,
        #             proj_prefix=self._pid_prefix,
        #             proj_start_num=self._pid_startNum,
        #             path=self._destination)
        for queue in self.copyEngine.builder.queues:
            simple = "Simple"
            old_names = ""
            new_names = ""
            files = []
            queue_id = ""

            if not queue.isSimple:
                simple = "Complex"
            if queue.included:
                project_id = queue.project_id
            else:
                project_id = ""

            record = QTreeWidgetItem(self.tree_files, ["", "", str(queue.parts[0][0].id), project_id, simple])
            queue_id = str(queue.queue)
            for part in queue.parts:
                for file in part:
                    included = "Included"
                    if not file.included:
                        included = "Excluded"
                        # file['filename'] = ""
                    if not queue.isSimple:
                        files.append(QTreeWidgetItem(record, ["", "", str(file.id), file.source, file.filename, included]))
                    old_names = os.path.basename(file.source) + " "
                    if file.included:
                        new_name = os.path.basename(file.filename) + " "
                        dummy = QTreeWidgetItem(record, ["", queue_id, str(file.id), '','', '', new_name])

                        record.addChild(dummy)
            record.setText(1, queue_id)
            record.setText(5, old_names)
            record.setText(8, queue.get_status())
            if queue.parts:
                if queue.isSimple:
                    included = "Included"
                    if not queue.included:
                        included = "Excluded"
                    record.setText(7, included)
                # TODO add logic for complex files
            records.append(record)
        self.tree_files.addTopLevelItems(records)

    def load_files(self, source, destination=None, smart_sorting=True):
        tiffs = []
        jpegs = []

        NameRecord.reset_fileID(self)
        # destination = "/Volumes/CAVPPTestDrive/"

        newfile = ""

        self.tree_files.clear()
        # get all the files that match either tif or jpg
        self.copyEngine.builder.clear_queues()
        for root, subdirs, files in os.walk(source):
            for index, file in enumerate(files):
                if file.startswith('.'):
                    continue
                files_per_part = record_bundle(self._oid_marc, index+self._oid_startNum, path=destination)
                if os.path.splitext(file)[1].lower() == '.tif':
                    newfile = os.path.join(root, file)
                    if smart_sorting:
                        tiffs.append(newfile)
                    else:
                        files_per_part.add_file2(file_name=newfile, file_type_to_create=FileTypes.MASTER)
                        files_per_part.add_file2(file_name=newfile, file_type_to_create=FileTypes.ACCESS, new_format=AccessExtensions.JPEG.value)
                elif os.path.splitext(file)[1].lower() == '.jpg':
                    newfile = os.path.join(root, file)
                    if smart_sorting:
                        jpegs.append(newfile)
                    else:
                        files_per_part.add_file2(file_name=newfile, file_type_to_create=FileTypes.MASTER)
                if not smart_sorting:
                    self.copyEngine.builder.add_queue([files_per_part],
                                      obj_id_prefix=self._oid_marc,
                                      obj_id_num=index + self._oid_startNum,
                                      proj_id_prefix=self._pid_prefix,
                                      proj_id_num=index + self._pid_startNum)

        if smart_sorting:
            for index, jpeg in enumerate(jpegs):
                files_per_part = record_bundle(self._oid_marc, index+self._oid_startNum, path=destination)
                jpeg_name = os.path.splitext(os.path.basename(jpeg))[0]
                found_tiff = False
                for tiff in tiffs:
                    if jpeg_name == os.path.splitext(os.path.basename(tiff))[0]:

                        files_per_part.add_file2(file_name=tiff, file_type_to_create=FileTypes.MASTER)
                        files_per_part.add_file2(file_name=tiff, file_type_to_create=FileTypes.ACCESS, new_format=AccessExtensions.JPEG.value)

                        found_tiff = True
                        break
                if not found_tiff:
                    # files_per_part.add_file(jpeg)
                    files_per_part.add_file2(file_name=jpeg, file_type_to_create=FileTypes.MASTER)
                    # files_per_part.add_file2(file_name=jpeg, file_type=FileTypes.ACCESS)

                self.copyEngine.builder.add_queue([files_per_part],
                                                  obj_id_prefix=self._oid_marc,
                                                  obj_id_num=index + self._oid_startNum,
                                                  proj_id_prefix=self._pid_prefix,
                                                  proj_id_num=index + self._pid_startNum)

        self.buttonRename.setEnabled(True)
        self.pushButton_group.setEnabled(True)
        self.pushButton_include.setEnabled(True)
        self.update_tree()

    def update_click(self):
        if os.path.isdir(self.lineEdit_source.text()):
            if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
                print("Updating tree")
            self._update_statusbar("Updating")
            self.copyEngine.builder.update2(obj_marc=self._oid_marc,
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

        self.database = ReportFactory(database=datafile)

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
            self.tableWidget.setItem(row, 2, QTableWidgetItem(record['original_name']))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(record['new_name']))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(record['new_md5']))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(record['ia_url']))


def start_gui(database, folder=None):
    global datafile

    datafile = database
    # sys.excepthook = excepthook
    app = QApplication(sys.argv)
    # error = QErrorMessage()
    # error.showMessage("error")
    # error.setText("afdssad")
    # error.exec_()
    if folder and folder != "":
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("Starting GUI with {}".format(folder))
        form = MainDialog(folder=folder)
    else:
        form = MainDialog()

    form.show()
    app.exec_()


def excepthook(excType, excValue, tracebackobj):

    Worker.abort()
    date = datetime.date.today()

    time_ = time.localtime()
    # error = QErrorMessage()
    error = QMessageBox()
    error.setWindowTitle("Critical Error")
    # error.setIcon()
    error.setText("Error{}: {}".format(excType.__name__, str(excValue)))
    error.addButton(QPushButton("Close"), QMessageBox.NoRole)
    error.addButton(QPushButton("Save"), QMessageBox.YesRole)
    error.setInformativeText("Do you wish to save the error details for debugging?")
    error.setDetailedText(str(traceback.format_tb(tracebackobj)))
    ret = error.exec_()

    if ret == 1:

        save_file = QFileDialog.getSaveFileName(None,
                                                "Save file",
                                                "Image_Error_{}{}{}-{}{}.log".format(date.year,
                                                                                     date.month,
                                                                                     date.day,
                                                                                     time_.tm_hour,
                                                                                     time_.tm_min,
                                                                                     "Log File (*.log)"))
        if save_file:
            try:
                with open(save_file, 'w') as f:
                    f.writelines("Time: {}\n".format(time.ctime()))
                    f.writelines("Platform: {}\n".format(sys.platform))
                    f.writelines("Version: {}\n".format(sys.version_info))

                    f.writelines("\n")
                    traceback.print_tb(tracebackobj, None, f)
                    print("Saving")
            except IOError:
                print("Error saving file")
    QApplication.quit()

    # if error.clickedButton() == save:

    # if save_error == QMessageBox.YesRole:

    # QMessageBox.about(QMessageBox, "error")

if __name__ == '__main__':

    sys.stderr.write("Not a runnable script. Run batch_renamer.py instead.\n")
    pass