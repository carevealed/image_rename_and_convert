import hashlib
import os
import threading
from time import sleep, ctime, time
import shutil
from PIL import Image, ImageFilter

from rename_files import file_metadata_builder
from rename_files.nonAV import NonAVModel
# from rename_files.nonAV import file_metadata_builder

__author__ = 'California Audio Visual Preservation Project'

# from PySide.QtGui import *
# from PySide.QtCore import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *
# from PIL import Image, ImageQt
from rename_files.renaming_model import RenameFactory, NameRecord
from collections import namedtuple

class WorkerException(Exception):
    def __init__(self, message, errors):
        super(WorkerException, self).__init__(message)
        self.errors = errors

@DeprecationWarning
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

# job_packet
#   parts job_parts

# job_parts
#   old_file_name
#   new_file_name
#   make_copy Bool
#   convert Bool


class Worker2(QThread):
    report_packet = namedtuple('report_packet', ['old_name',
                                                 'new_name',
                                                 'project_id_prefix',
                                                 'project_id_number',
                                                 'object_id_marc',
                                                 'object_id_number',
                                                 'part_number',
                                                 'object_id',
                                                 'type',
                                                 'md5',
                                                 'date',
                                                 'file_suffix',
                                                 'file_extension',
                                                 'notes'])
    status_packet = namedtuple('status_packet', ['title', 's_file', 'd_file', 'path'])
    updateStatus = pyqtSignal(status_packet)
    job_completed = pyqtSignal(report_packet)

    def __init__(self, path=None, packet=None):
        QThread.__init__(self)
        print("Worker initiated")
        self._packet = packet
        self._path = path
        self.notes = []

    def run(self):
        # QThread.sleep(100)
        # sleep(2)
        checksum = None
        new_name = None
        extension = None
        date = None
        self.new_path = os.path.join(self._path, self._packet.object_id)
        instances = NonAVModel.Instantiations()
        instances.relationship = "page " + str(self._packet.part_number)


        if not self._packet:
            raise WorkerException("Need a job packet")

        # Add a copy of the original to the report
        self.updateStatus.emit(self.status_packet(title="Calculating MD5",
                                                  s_file=os.path.basename(self._packet.old_name),
                                                  d_file=None,
                                                  path=None))


        # If needed convert file to new format

        if not os.path.exists(self.new_path):
            # Create new directory if doesn't exist
            os.makedirs(self.new_path)
        new_name = os.path.join(self.new_path, self._packet.new_name)
        extension = os.path.splitext(self._packet.new_name)[1]

        if self._packet.convert:
            if len(extension) > 5:
                raise ValueError("Extension is too long to be an extension. Got " + str(extension))
            self.updateStatus.emit(self.status_packet(title="Converting new files",
                                                      s_file=self._packet.old_name,
                                                      d_file=self._packet.new_name,
                                                      path=self.new_path))
            if not self.convert_format(self._packet.old_name, new_name):
                raise WorkerException(self._packet.old_name, " failed to convert.")

            self.updateStatus.emit(self.status_packet(title="Calculating MD5",
                                                      s_file=self._packet.new_name,
                                                      d_file=None,
                                                      path=None))
            checksum = self.get_md5(new_name)
            self._save_as_file(checksum, os.path.join(self.new_path, self._packet.new_name + ".md5"))
            date = ctime()

            new_packet = self.report_packet(old_name=self._packet.old_name,
                                            new_name=self._packet.new_name,
                                            project_id_prefix=self._packet.project_id_prefix,
                                            project_id_number=self._packet.project_id_number,
                                            object_id_marc=self._packet.object_id_marc,
                                            object_id_number=self._packet.object_id_number,
                                            part_number=self._packet.part_number,
                                            object_id=self._packet.object_id,
                                            type=self._packet.file_generation,
                                            md5=checksum,
                                            date=date, # TODO change to date Created
                                            file_suffix=self._packet.file_suffix,
                                            file_extension=extension,
                                            notes=self.notes)
            converted_file_metadata = file_metadata_builder.file_metadata_builder(os.path.join(self.new_path,self._packet.new_name),
                                                  generation=self._packet.file_generation,
                                                  derived_from=os.path.basename(self._packet.old_name),
                                                  checksum=checksum,
                                                  checksum_type="md5",
                                                  processing_notes="; ".join(self.notes))
            instances.add_instantiation(converted_file_metadata.xml)
            self.job_completed.emit(new_packet)

        # If needed copy the file to the new destination
        if self._packet.copy_file:
            self.updateStatus.emit(self.status_packet(title="Copying Files",
                                                      s_file=self._packet.old_name,
                                                      d_file=self._packet.new_name,
                                                      path=self.new_path))

            if not self.copy_files(self._packet.old_name, new_name):
                raise WorkerException(self._packet.old_name, " failed to copy.")
            checksum = self.get_md5(new_name)
            Worker2._save_as_file(checksum, os.path.join(self.new_path, self._packet.new_name + ".md5"))
            date = ctime()
            extension = os.path.splitext(new_name)[1]

            new_packet = self.report_packet(old_name=self._packet.old_name,
                                            new_name=self._packet.new_name,
                                            project_id_prefix=self._packet.project_id_prefix,
                                            project_id_number=self._packet.project_id_number,
                                            object_id_marc=self._packet.object_id_marc,
                                            object_id_number=self._packet.object_id_number,
                                            part_number=self._packet.part_number,
                                            object_id=self._packet.object_id,
                                            type=self._packet.file_generation,
                                            md5=checksum,
                                            date=date, # TODO change to date Created
                                            file_suffix=self._packet.file_suffix,
                                            file_extension=extension,
                                            notes=self.notes)
            self.job_completed.emit(new_packet)

        # build an xml


            tiff_file_metadata = file_metadata_builder.file_metadata_builder(os.path.join(self.new_path,self._packet.new_name),
                                                              generation=self._packet.file_generation,
                                                              derived_from="Physical",
                                                              checksum=checksum,
                                                              checksum_type="md5",
                                                              processing_notes="; ".join(self.notes))
            instances.add_instantiation(tiff_file_metadata.xml)
        self.xml = instances
        new_file = self._packet.new_name + ".xml"

        # print(xml)
        # with open(os.path.join(new_path, new_file), 'w') as f:
        #     f.write(xml.__str__())

    def convert_format(self, source, destination):
        print("Converting")
        self.notes.append("{}: Read the original file headers.".format(ctime()))
        img = Image.open(source)
        if img.mode == '1':
            self.notes.append("{}: Determined that the file is 1 bit so extra processing is required.".format(ctime()))

            # blur the image to make it compress better
            self.notes.append("{}: File converted to RGB colorspace.".format(ctime()))
            img = img.convert('RGB')
            self.notes.append("{}: Added gaussian blur of 3 pixels to help.".format(ctime()))
            img = img.filter(ImageFilter.GaussianBlur(3))
        else:
            img = img.convert('RGB')
            self.notes.append("{}: File converted to RGB colorspace.".format(ctime()))
        self.notes.append(("{}: Saved converted image as jpeg.".format(ctime())))
        img.save(destination,
                 'jpeg',
                 icc_profile=img.info.get("icc_profile"),
                 quality=90,
                 subsampling=1,
                 progressive=True)
        img.close()

        return True

    @staticmethod
    def _save_as_file(checksum, file_name):
        # print("Saving checksum, {}, into {}".format(checksum, file_name))
        with open(file_name, "w") as f:
            f.write(checksum)
            pass
    def copy_files(self, source, destination):
        if not os.path.exists(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        # record.set_Working()
        shutil.copy2(source, destination)
        self.notes.append("{}: Copied file with file metadata using Python's shutil.copy2() operation.".format(ctime()))
        return True

    @staticmethod
    def get_md5(file_name):

        BUFFER = 8192
        md5 = hashlib.md5()
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(BUFFER), b''):
                md5.update(chunk)
        return md5.hexdigest()
