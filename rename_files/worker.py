import os
import threading
from time import sleep

__author__ = 'California Audio Visual Preservation Project'

# from PySide.QtGui import *
# from PySide.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
# from PIL import Image, ImageQt
from rename_files.renaming_model import RenameFactory, NameRecord



class Worker(QThread):
    updateStatus = Signal(str)
    reporter = Signal(NameRecord)
    reset_progress = Signal(int)
    update_progress = Signal(int)
    request_report = Signal()
    error_reporter = Signal(str)



    def __init__(self, path):
        QThread.__init__(self)
        self._idle = True
        # self.builder = None
        # self.reporter = None
        self.builder = RenameFactory(path)

    # @builder.setter
    # def builder(self, value):
    #     # self.builder = value

    def pause(self):
        self._idle = True

    def resume(self):
        self._idle = False

    @property
    def idle(self):
        return self._idle

    def setup(self, destination):
        pass

    def run(self):
        success = True
        self._idle = False
        if self.builder.new_path == "":
            raise ValueError("PAth can't be empty")
        self.reset_progress.emit(len(self.builder.queues))
        for index, i in enumerate(self.builder.queues):
            while self._idle:
                sleep(1)

            if i.included:
                self.updateStatus.emit("Saving {}".format(i.get_dict()['project id']))
                try:
                    record = self.builder.execute_rename_from_queue_by_record(i)
                    self.reporter.emit(record)
                except IOError as ie:
                    self._idle = True
                    error_message = "Problem with: {}. ({})".format(i.get_dict()['project id'], ie)
                    self.updateStatus.emit(error_message)
                    self.error_reporter.emit(error_message)

                # self.reporter.add_record(record)
            self.update_progress.emit(index+1)
        self.request_report.emit()
        self._idle = True
        self.updateStatus.emit("Done")


