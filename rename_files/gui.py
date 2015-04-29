from enum import Enum
import os

__author__ = 'California Audio Visual Preservation Project'
from PySide.QtGui import *
from PySide.QtCore import *
from gui_data import Ui_Form
from enum import Enum
import renaming_model
import sys

class running_mode(Enum):
    NORMAL = 0
    DEBUG = 1
    BUIDING = 2
MODE = running_mode.BUIDING

class MainDialog(QDialog, Ui_Form):

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.setupUi(self)

        # NON-UI data members
        self.builder = renaming_model.RenameFactory()

        # self.pushButton_update.clicked.connect(self.buttonClicked)
        self.pushButton_sourceBrowse.clicked.connect(self.browse_source)
        self.pushButton_destinationBrowse.clicked.connect(self.browse_destination)
        self.pushButton_update.clicked.connect(self.update_click)


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

    def load_files(self, source, destination=None):
        tiffs = []
        jpegs = []
        records = []

        object_id_prefix = "CAS"
        first_object_id = 54
        proj_id_prefix = "caps"
        first_project_id = 43
        destination = "/Volumes/CAVPPTestDrive/"

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


        for index, jpeg in enumerate(jpegs):
            files_per_record = renaming_model.record_bundle(object_id_prefix, index+first_object_id, path=destination)
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
                              obj_id_prefix=object_id_prefix,
                              obj_id_num=index + first_object_id,
                              proj_id_prefix=proj_id_prefix,
                              proj_id_num=index + first_project_id)

        for queue in self.builder.queues:
            simple = "Simple"
            old_names = ""
            new_names = ""
            files = []

            if not queue.isSimple:
                simple = "Complex"
            record = QTreeWidgetItem(self.tree_files, [queue.project_id, simple])
            for file in queue.files:
                included = "Included"
                if not file['included']:
                    included = "Excluded"

                if not queue.isSimple:
                    files.append(QTreeWidgetItem(record, ["", "", file["old"], file['new'], included]))
                old_names += os.path.basename(file['old']) + " "
                new_names += os.path.basename(file['new']) + " "
            record.setText(2, old_names)
            record.setText(3, new_names)
            if queue.isSimple:
                included = "Included"
                if not queue.files[0]['included']:
                    included = "Excluded"
                record.setText(4, included)

            records.append(record)

        self.tree_files.addTopLevelItems(records)

    def update_click(self):
        if os.path.isdir(self.lineEdit_source.text()):
            if MODE == running_mode.DEBUG or MODE == running_mode.BUIDING:
                print("Updating")
            self.load_files(source=self.lineEdit_source.text())


app = QApplication(sys.argv)
form = MainDialog()
form.show()
app.exec_()