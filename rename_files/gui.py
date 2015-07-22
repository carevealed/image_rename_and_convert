import datetime
import queue
import time
import threading
from time import sleep
import types
from rename_files.jobModel import jobTreeNode, jobTreeModel, ObjectNode, PageNode, PageSideNode, NewFileNode, FileTypeCodes, \
    DataRows

__author__ = 'California Audio Visual Preservation Project'
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PIL import Image

from rename_files.renaming_model import RenameFactory, ReportFactory, record_bundle, FileTypes, AccessExtensions, \
    NameRecord, RecordStatus
from rename_files.gui_datafiles.report_gui import Ui_dlg_report
from rename_files.worker import Worker, Worker2
from enum import Enum
import sys
import argparse
from enum import Enum
import os
from rename_files.renaming_controller import generate_report
import traceback
from queue import Queue

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

MODE = running_mode.DEBUG
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
        self.report_packets = []
        self.showPreview = True
        self._source = ""
        self._destination = None
        self._pid_prefix = ""
        self._pid_startNum = 0
        self._oid_marc = ""
        self._oid_startNum = 0
        self.reporter = ReportFactory(database=datafile, username="CAPS")  # TODO: add Username input
        # self.copyEngine = Worker(self._destination)
        # self.copyEngine = Worker(self._destination)
        self.reporter.initize_database()
        self.tree_files.setVisible(False)
        self.status = None
        self.report_queues = Queue()

        # setup

        # set up the model view for the files view
        self.items = []

        self.jobs_data_root = jobTreeNode("Root", self._pid_startNum, self._oid_marc, self._oid_startNum)
        # ------------- Test --------------
        # newObject = ObjectNode("cusb_000001")
        # new_page = PageNode(33, newObject)
        # new_page_side = PageSideNode("a", new_page, "dyyee.tif")
        # new_file_master = NewFileNodes("dfd_000001_master.tif", "Master", new_page_side)
        # new_file_access = NewFileNodes("dfd_000001_access.jpg", "Access", new_page_side)
        # self.jobs_data_root.insertChild(0, newObject)
        # ------------- Test --------------

        # child = jobTreeNode("dd", parent=self.jobs_data_root)
        # child1 = jobTreeNode("ddd")
        # child.insertChild(0, child1)
        # self.jobs_data_root.insertChild(1, child1)
        # s.addChild(jobTreeNode("ddd", s))
        # self.items.append(s)
        # self.items[-1].addChild()
        self.data = jobTreeModel(self.jobs_data_root)

        # newObject = ObjectNode("cusb_000001")
        # new_page = PageNode(33, newObject)
        # new_page_side = PageSideNode("a", new_page, "dyyee.tif")
        # new_file_master = NewFileNode("dfd_000001_master.tif", FileType.MASTER, new_page_side)
        # new_file_access = NewFileNode("dfd_000001_access.jpg", FileType.ACCESS, new_page_side)
        # self.data.add_object(newObject)
        # self.data.add_object(ObjectNode("dffddfd"))
        # self.data.add_object(ObjectNode("dfdwefd"))
        self.tree_filesView.setModel(self.data)
        # child2 = jobTreeNode("round2")
        # child1.insertChild(0, child2)
        # child1.insertChild(0, child2)


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
        self.tree_filesView.clicked.connect(self._update_preview_window)
        self.checkBox_preview.clicked.connect(self._toggle_preview)


        # self.copyEngine.updateStatus.connect(self._update_statusbar)
        # self.copyEngine.reset_progress.connect(self._setup_progress_bar)
        # self.copyEngine.update_progress.connect(self._update_progress)
		#
		# self.copyEngine.reporter.connect(self._add_record)
		# self.copyEngine.request_report.connect(self._run_reports)
		# self.copyEngine.error_reporter.connect(self._display_error)

    def _add_report_packet(self, packet):
        print(str(packet))
        self.report_packets.append(packet)
        # self.report_queues.put(packet)

    def _update_preview_window(self):
        if self.showPreview:
            index = self.tree_filesView.selectedIndexes()[0]
            item = self.data.getNode(index)
            filename = item.get_data().original_name
            if filename is None:
                return None
            # dummy = self.tree_files.selectedItems()[0].parent()
            # if self.tree_files.selectedItems()[0].parent():
            #     item = self.tree_files.selectedItems()[0].parent()
            # else:
            #     item = self.tree_files.selectedItems()[0]
            # file_id = int(item.text(2))
            # # file_id
            # filename = self.copyEngine.builder.find_file(file_id).source
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

    def update_status_message(self, packet):
        print(packet)
        self.status = '<h3 align="left">\tProcessing Images</h3><br>' \
                      '<table cellpadding="5">' \
                      '<tr>' \
                      '<th align="left">Process:</th>' \
                      '<td>{}</td>' \
                      '</tr>'.format(packet.title)

        if not packet.d_file is None:
            self.status += '<tr>' \
                           '<th align="left">From:</th>' \
                           '<td>{}</td>' \
                           '</tr>' \
                           '<tr>' \
                           '<th align="left">As:</th>' \
                           '<td>{}</td>' \
                           '</tr>' \
                           '<tr>' \
                           '<th align="left">To:</th>' \
                           '<td>{}</td>' \
                           '</tr>'.format(packet.s_file, packet.d_file, packet.path)
        else:
            self.status += '<tr>' \
                           '<th align="left">File:</th>' \
                           '<td>{}</td>' \
                           '</tr>'.format(packet.s_file)
        # self.status = packet

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
        print("testing")
        ReportDialog(2)
        # queues = self.tree_filesView.model().get_active_jobs()
        # for queue in queues:
        #     print(queue)


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
        include_report = self.checkBox_IncludeReport.isChecked()
        jobs = self.tree_filesView.model().get_active_jobs()
        q = Queue()
        for j in jobs:
            q.put(j)
        progress = QProgressDialog("Processing images", "Abort", 0, q.qsize())
        # progress = QProgressDialog("Processing images", "Abort", 0, len(jobs))
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        i = 0
        status = ""
        worker = Worker2()


        # self.connect(worker.updateStatus, status)
        while q.unfinished_tasks:
            if not worker.isRunning():
                job = q.get()
                worker = Worker2(self._destination, packet=job)
                worker.updateStatus.connect(self.update_status_message)
                worker.job_completed.connect(self._add_report_packet)
                worker.run()
            new_message = QLabel()
            new_message.setText(self.status)
            new_message.setMargin(20)
            progress.setLabel(new_message)
            # progress.setLabelText(self.status.ljust(3))
            progress.setValue(i)
            if progress.wasCanceled():
                break

            # print(i)q
            # print(self.status)
            if not worker.isRunning():
                i += 1

                q.task_done()
                continue

            sleep(.01)
        report_queues = self._sort_reports()
        progress = QProgressDialog("Writing report. Please wait", "Abort", 0, len(report_queues))
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        sleep(.5)
        i = 0
        assert(isinstance(report_queues, tuple))
        for i, record in enumerate(report_queues):
            assert(isinstance(record, tuple))
            # job = report_queues.get()
            new_message = QLabel()
            new_message.setText(self._generate_report_message(record))
            new_message.setMargin(20)
            # for i, packet in enumerate(job):
            #     print(i, str(packet))
            # QThread.sleep(100)
            progress.setLabel(new_message)
            self.reporter.add_record2(record)
            progress.setValue(i)
            # i += 1
            # print(str(job))
            # report_queues.task_done()

        if include_report:
            print("Opening report")
            self._run_reports()



        # for i, job in enumerate(jobs):
        #     progress.setValue(i)
        #     progress.setLabelText(str(job))
        #     current_job = Worker2(job)
        #     current_job.run()
        #     while current_job.isRunning():
        #         print("Sleeping")
        #         # QThread.sleep(1)
        #     # if i == 50:
        #     # print(str(job))

        #     sleep(0.05)
        #
        # self.copyEngine.builder.new_path = self._destination
        # self.copyEngine.setup(destination=self._destination, create_report=include_report, reporter=self.reporter)
        # self.copyEngine.start()
    def _generate_report_message(self, record):
        message = '<h3 align="center">Saving Record of Image</h3><br>' \
                  '<table cellpadding="5">' \
                  '<tr>' \
                  '<th align="left">Object ID:</th>' \
                  '<td>{}</td>' \
                  '</tr>' \
                  '</table>' \
                  .format(record[0].object_id)
                  # '<tr>' \
                  # '<th align="left">New Name:</th>' \
                  # '<td>{}</td>' \
                  # '</tr>' \

        return message

    def _sort_reports(self):
        reports = []
        object_ids = []
        # find all unique object ids
        for packet in self.report_packets:
            if not packet.object_id in object_ids:
                object_ids.append(packet.object_id)

        for id in object_ids:
            object_packets = []
            # find all packets with that unique ID
            for packet in self.report_packets:
                # create queue of tuples of packet ids
                if packet.object_id == id:
                    object_packets.append(packet)
            original = Worker2.report_packet(old_name=object_packets[0].old_name,
                                             new_name=None,
                                             project_id_prefix=object_packets[0].project_id_prefix,
                                             project_id_number=object_packets[0].project_id_number,
                                             object_id_marc=object_packets[0].object_id_marc,
                                             object_id_number=object_packets[0].object_id_number,
                                             object_id=object_packets[0].object_id,
                                             type="Original",
                                             md5=Worker2.get_md5(object_packets[0].old_name),
                                             date=None,
                                             file_suffix=None,
                                             file_extension=os.path.splitext(object_packets[0].old_name)[1],
                                             notes=None)
            object_packets.insert(0, original)

            reports.append(tuple(object_packets))

        # return that queue
        return tuple(reports)

    def _show_report(self):
        job = self.reporter.current_batch
        report = ReportDialog(job)
        report.exec_()

    def _save_report(self):
        assert(isinstance(self._destination, str))
        try:
            generate_report(self.reporter, os.path.join(self._destination, "report.csv"))
            # generate_report(self.reporter, os.path.join(self.copyEngine.builder.new_path, "report.csv"))
        except FileExistsError:
            msg_box = QMessageBox()
            msg_box.setText("The saving location already has a report, do you wish to overwrite it?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            res = msg_box.exec_()
            if res == QMessageBox.Cancel:
                pass
            elif res == QMessageBox.Yes:
                os.remove(os.path.join(self._destination, "report.csv"))
                generate_report(self.reporter, os.path.join(self._destination, "report.csv"))

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
        jobTreeNode.pid_prefix = self._pid_prefix
        self._update_data_status()
        self.data.update_object_numbers()

    def _update_pid_startNum(self, new_number):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("updating PID: {}".format(new_number))
        try:
            self._pid_startNum = int(new_number)
            self.lineEdit_PID_startNum.setStyleSheet(text_styles.VALID)
            jobTreeNode.pid_start_num = self._pid_startNum
            self.data.update_object_numbers()
        except ValueError:
            self.lineEdit_PID_startNum.setStyleSheet(text_styles.INVALID)
            self._pid_startNum = None
        self._update_data_status()

    def _update_oid_marc(self, new_marc):
        self._oid_marc = new_marc
        jobTreeNode.oid_marc = self._oid_marc
        self._update_data_status()
        self.data.update_object_numbers()


    def _update_oid_startNum(self, new_number):

        if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
            print("updating OID: {}".format(new_number))
        try:
            self._oid_startNum = int(new_number)
            self.lineEdit_OID_startNum.setStyleSheet(text_styles.VALID)
            jobTreeNode.oid_start_num = self._oid_startNum
            self.data.update_object_numbers()
        except ValueError:
            self.lineEdit_OID_startNum.setStyleSheet(text_styles.INVALID)
            self._oid_startNum = None
        self._update_data_status()



    def _update_data_status(self):
        if self.data.rowCount() > 0:
            start_index = self.data.index(0,0)

            # start_index = self.tree_filesView.selectedIndexes()[0]
            # start_index = self.tree_filesView.selectedIndexes()[0]
            # end_index = self.tree_filesView.selectedIndexes()[-1]
            end_index = self.data.index(self.data.rowCount()-1, self.data.columnCount(parent=self.data._root))
        else:
            start_index = QModelIndex()
            end_index = QModelIndex()
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
            self.buttonRename.setEnabled(True)
            self.pushButton_update.setEnabled(True)
        else:
            self.lineEdit_validStatus.insert("Not Valid")
            self.lineEdit_validStatus.setStyleSheet(text_styles.INVALID)
            self.pushButton_load_filles.setEnabled(False)
            self.buttonRename.setEnabled(False)
            self.pushButton_update.setEnabled(False)
        if start_index.isValid() and end_index.isValid():
            self.tree_filesView.dataChanged(start_index, end_index)

    def _include_selection(self):
        start_index = self.tree_filesView.selectedIndexes()[0]
        end_index = self.tree_filesView.selectedIndexes()[-1]
        for index in self.tree_filesView.selectedIndexes():
            if index.column() != 0:
                continue
            item = self.data.getNode(index)
            # print(item.get_data())
            included = not item.get_data().included
            item.set_included(included)
            # print(current_node)
        self.data.update_object_numbers()
        if start_index.isValid() and end_index.isValid():
            self.tree_filesView.dataChanged(start_index, end_index)
        else:
            raise Exception("Not valid index")


        # for item in self.tree_files.selectedItems():
        #     hasParent =item.parent()
        #     if hasParent:
        #         id = int(item.parent().text(1))
        #     # parent = item.parent()
        #     else:
        #         id = int(item.text(1))
        #     current_status = self.copyEngine.builder.find_queue(id).included
        #     self.copyEngine.builder.set_file_include(id, not current_status)
        # self.update_tree()

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
        if self.data.rowCount() > 0:
            self.data.removeRows(0, self.data.rowCount())
        jobTreeNode.total_active = 0
        # get all the files that match either tif or jpg
        # self.copyEngine.builder.clear_queues()
        for root, subdirs, files in os.walk(source):
            index = 0
            for file in files:
                if file.startswith('.'):
                    continue
                if not file.lower().endswith('.jpg') and not file.lower().endswith('.tif'):
                    print("Skipping {}.".format(file))
                    continue
                files_per_part = record_bundle(self._oid_marc, index+self._oid_startNum, path=destination)
                newObject = ObjectNode(self._pid_prefix,
                                       self._oid_marc)
                # new_page = PageNode(1, newObject)
                if os.path.splitext(file)[1].lower() == '.tif':
                    # new_side = PageSideNode(page_side="", original_filename=newfile, parent=new_page)

                    newfile = os.path.join(root, file)
                    if smart_sorting:
                        tiffs.append(newfile)
                    else:
                        newObject = ObjectNode(self._pid_prefix, self._oid_marc)
                        new_page = PageNode(1, newObject)
                        new_side = PageSideNode(page_side="", original_filename=newfile, parent=new_page)
                        new_master = NewFileNode(FileTypeCodes.MASTER, copy=True, convert=False, parent=new_side)
                        new_access = NewFileNode(FileTypeCodes.ACCESS, copy=False, convert=True, parent=new_side)
                        self.data.add_object(newObject)

                        files_per_part.add_file2(file_name=newfile, file_type_to_create=FileTypes.MASTER)
                        files_per_part.add_file2(file_name=newfile, file_type_to_create=FileTypes.ACCESS, new_format=AccessExtensions.JPEG.value)
                elif os.path.splitext(file)[1].lower() == '.jpg':
                    newfile = os.path.join(root, file)
                    if smart_sorting:
                        jpegs.append(newfile)
                    else:
                        # new_master = NewFileNode(FileType.MASTER, convert=False, parent=new_side)
                        files_per_part.add_file2(file_name=newfile, file_type_to_create=FileTypes.MASTER)
                        newObject = ObjectNode(self._pid_prefix, self._oid_marc)
                        new_page = PageNode(1, newObject)
                        new_side = PageSideNode(page_side="", original_filename=newfile, parent=new_page)
                        new_master = NewFileNode(FileTypeCodes.MASTER, copy=True, convert=False, parent=new_side)
                        self.data.add_object(newObject)
                else:
                    continue
                if not smart_sorting:
                    pass
                    # self.data.add_object(newObject)
                    # self.copyEngine.builder.add_queue([files_per_part],
                    #                   obj_id_prefix=self._oid_marc,
                    #                   obj_id_num=index + self._oid_startNum,
                    #                   proj_id_prefix=self._pid_prefix,
                    #                   proj_id_num=index + self._pid_startNum)
                # if newObject:
                #     self.data.add_object(newObject)
                index += 1
        if smart_sorting:
            index = 0
            for index, jpeg in enumerate(jpegs):
                # files_per_part = record_bundle(self._oid_marc, index+self._oid_startNum, path=destination)
                jpeg_name = os.path.splitext(os.path.basename(jpeg))[0]
                found_tiff = False
                newObject = ObjectNode(self._pid_prefix,
                                       self._oid_marc)

                new_page = None
                new_side = None
                # new_master = None
                # new_access = None
                for tiff in tiffs:
                    if jpeg_name == os.path.splitext(os.path.basename(tiff))[0]:
                        new_page = PageNode(1, newObject)
                        new_side = PageSideNode(page_side="", original_filename=tiff, parent=new_page)
                        new_master = NewFileNode(FileTypeCodes.MASTER, copy=True, convert=False, parent=new_side)
                        new_access = NewFileNode(FileTypeCodes.ACCESS, copy=False, convert=True, parent=new_side)


                        files_per_part.add_file2(file_name=tiff, file_type_to_create=FileTypes.MASTER)
                        files_per_part.add_file2(file_name=tiff,
                                                 file_type_to_create=FileTypes.ACCESS,
                                                 new_format=AccessExtensions.JPEG.value)

                        found_tiff = True
                        # self.data.add_object(newObject)
                        break

                if not found_tiff:
                    # files_per_part.add_file(jpeg)
                    new_page = PageNode(1, newObject)
                    new_side = PageSideNode(page_side="", original_filename=jpeg, parent=new_page)
                    new_master = NewFileNode(FileTypeCodes.MASTER, copy=True, convert=False, parent=new_side)
                    files_per_part.add_file2(file_name=jpeg, file_type_to_create=FileTypes.MASTER)
                    # files_per_part.add_file2(file_name=jpeg, file_type=FileTypes.ACCESS)
                self.data.add_object(newObject)
                # self.copyEngine.builder.add_queue([files_per_part],
                #                                   obj_id_prefix=self._oid_marc,
                #                                   obj_id_num=index + self._oid_startNum,
                #                                   proj_id_prefix=self._pid_prefix,
                #                                   proj_id_num=index + self._pid_startNum)


        # new_page = PageNode(33, newObject)
        # newObject.addChild(new_page)
        # new_page_side = PageSideNode("a", new_page, "dyyee.tif")

        # new_file_master = None
        # new_file_access = None

        self.buttonRename.setEnabled(True)
        self.pushButton_group.setEnabled(True)
        self.pushButton_include.setEnabled(True)
        self.data.update_object_numbers()
        # self.update_tree()

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


# class Supervisor(threading):
#     MAX_WORKERS = 1
#
#     def __init__(self, model):
#         super(Supervisor, self).__init__(model)
#         assert(isinstance(model, jobTreeModel))
#         self.q = Queue(maxsize=1)
#         self.model = model
#         self.workers = []
#
#     def add_worker(self, worker):
#         assert(isinstance(worker, Worker2))
#         if len(self.workers) <= Supervisor.MAX_WORKERS:
#             self.workers.append(worker)
#         pass
#
#     def run(self):
#         print("Running")
#         # for worker in self.workers:
#         #     assert(isinstance(worker, Worker2))
#         #     if worker.is_alive():
#         #         sleep(1)
#         #         continue
#         #     # start_job = self.workers.
# 		#
#         #     if worker.is_done():
#         #         self



if __name__ == '__main__':

    sys.stderr.write("Not a runnable script. Run batch_renamer.py instead.\n")
    pass