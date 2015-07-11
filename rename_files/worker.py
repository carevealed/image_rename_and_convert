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
    updateStatus = pyqtSignal(str)
    reporter = pyqtSignal(NameRecord)
    reset_progress = pyqtSignal(int)
    update_progress = pyqtSignal(int)
    request_report = pyqtSignal()
    error_reporter = pyqtSignal(str)

    _halt = False


    def __init__(self, path):
        QThread.__init__(self)
        self._idle = True
        # self._halt = False

        # self.builder = None
        # self.reporter = None
        self.builder = RenameFactory(path)
        # halt_worker.connect(self._halt)

    # @builder.setter
    # def builder(self, value):
    #     # self.builder = value

    def pause(self):
        self._idle = True

    def resume(self):
        self._idle = False

    @staticmethod
    def abort():
        Worker._halt = True
        RenameFactory.abort()
        print("Halting Worker")

    @property
    def idle(self):
        return self._idle

    def setup(self, destination):
        pass

    def run(self):
        success = True
        self._idle = False
        print("starting conversion")
        if self.builder.new_path == "":
            raise ValueError("PAth can't be empty")
        self.reset_progress.emit(len(self.builder.queues))
        for index, i in enumerate(self.builder.queues):
            while self._idle:
                sleep(1)
            if Worker._halt:
                success = False
                break
            if i.included:
                self.updateStatus.emit("Saving {}".format(i.get_dict()['project id']))
                try:
                    record = self.builder.execute_rename_from_queue_by_record(i)
                    if record == False:
                        success = False
                        break
                    self.reporter.emit(record)
                except IOError as ie:
                    self._idle = True
                    error_message = "Problem with: {}. ({})".format(i.get_dict()['project id'], ie)
                    self.updateStatus.emit(error_message)
                    self.error_reporter.emit(error_message)

                # self.reporter.add_record(record)
            self.update_progress.emit(index+1)
        if success:
            self.request_report.emit()
        self._idle = True
        self.updateStatus.emit("Done")


