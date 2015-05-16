import os
import threading
from time import sleep

__author__ = 'California Audio Visual Preservation Project'
from PySide.QtGui import *
from PySide.QtCore import *
# from PIL import Image, ImageQt
from rename_files.renaming_model import RenameFactory, NameRecord



class Worker(QThread):
    updateStatus = Signal(str)
    reporter = Signal(NameRecord)
    reset_progress = Signal(int)
    update_progress = Signal(int)
    request_report = Signal()


    def __init__(self, path):
        QThread.__init__(self)
        # self.builder = None
        # self.reporter = None
        self.builder = RenameFactory(path)

    # @builder.setter
    # def builder(self, value):
    #     # self.builder = value


    def setup(self, destination):
        pass

    def run(self):
        success = True
        if self.builder.new_path == "":
            raise ValueError("PAth can't be empty")
        self.reset_progress.emit(len(self.builder.queues))
        for index, i in enumerate(self.builder.queues):
            if i.included:
                record = self.builder.execute_rename_from_queue_by_record(i)
                # print(i.get_dict()['project id'])
                self.updateStatus.emit("Saving {}".format(i.get_dict()['project id']))
                self.reporter.emit(record)
                # self.reporter.add_record(record)
            self.update_progress.emit(index+1)
        self.request_report.emit()
        self.updateStatus.emit("Done")


