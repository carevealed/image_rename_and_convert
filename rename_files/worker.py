import hashlib
import os
import threading
from time import sleep, ctime
import shutil
from PIL import Image, ImageFilter


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


    def run(self):
        # QThread.sleep(100)
        # sleep(2)
        if not self._packet:
            raise WorkerException("Need a job packet")



        # Add a copy of the original to the report
        self.updateStatus.emit(self.status_packet(title="Calculating MD5",
                                                  s_file=os.path.basename(self._packet.old_name),
                                                  d_file=None,
                                                  path=None))
        # checksum = self.get_md5(self._packet.old_name)
        # extension = os.path.splitext(self._packet.old_name)[1]
        # new_packet = self.report_packet(old_name=self._packet.old_name,
        #                                     new_name=self._packet.new_name,
        #                                     object_id=self._packet.object_id,
        #                                     type="Original",
        #                                     md5=checksum,
        #                                     date=None, # TODO change to date Created
        #                                     file_suffix=self._packet.file_suffix,
        #                                     file_extension=extension,
        #                                     notes=None)
        # self.job_completed.emit(new_packet)

        # If needed convert file to new format
        new_path = os.path.join(self._path, self._packet.object_id)
        if not os.path.exists(new_path):
            # Create new directory if doesn't exist
            os.makedirs(new_path)
        new_name = os.path.join(new_path, self._packet.new_name)
        extension = os.path.splitext(self._packet.new_name)[1]

        if self._packet.convert:
            if len(extension) > 5:
                raise ValueError("Extension is too long to be an extension. Got " + str(extension))
            self.updateStatus.emit(self.status_packet(title="Converting new files",
                                                      s_file=self._packet.old_name,
                                                      d_file=self._packet.new_name,
                                                      path=new_path))
            if not self.convert_format(self._packet.old_name, new_name):
                raise WorkerException(self._packet.old_name, " failed to convert.")

            self.updateStatus.emit(self.status_packet(title="Calculating MD5",
                                                      s_file=self._packet.new_name,
                                                      d_file=None,
                                                      path=None))
            checksum = self.get_md5(new_name)
            self._save_as_file(checksum, os.path.join(new_path, self._packet.new_name + ".md5"))
            date = ctime()

            new_packet = self.report_packet(old_name=self._packet.old_name,
                                            new_name=self._packet.new_name,
                                            project_id_prefix=self._packet.project_id_prefix,
                                            project_id_number=self._packet.project_id_number,
                                            object_id_marc=self._packet.object_id_marc,
                                            object_id_number=self._packet.object_id_number,
                                            object_id=self._packet.object_id,
                                            type=self._packet.file_generation,
                                            md5=checksum,
                                            date=date, # TODO change to date Created
                                            file_suffix=self._packet.file_suffix,
                                            file_extension=extension,
                                            notes=None)
            self.job_completed.emit(new_packet)

        # If needed copy the file to the new destination
        if self._packet.copy_file:
            self.updateStatus.emit(self.status_packet(title="Copying Files",
                                                      s_file=self._packet.old_name,
                                                      d_file=self._packet.new_name,
                                                      path=new_path))
            # self.updateStatus.emit('<h3 align="center">Copying files</h3><br>'
            #                        '<table cellpadding="5">'
            #                        '<tr>'
            #                        '<th align="left">From:</th>'
            #                        '<td>{}</td>'
            #                        '</tr>'
            #                        '<tr>'
            #                        '<th align="left">As:</th>'
            #                        '<td>{}</td>'
            #                        '</tr>'
            #                        '<tr>'
            #                        '<th align="left">To:</th>'
            #                        '<td>{}</td>'
            #                        '</tr>'
            #                        # '<p align="left">From:\t{}</p>\n'
            #                        # '<p align="left">As:\t{}</p>\n'
            #                        # '<p align="left">To:\t{}</p>'
            #                        .format(self._packet.old_name, self._packet.new_name, self._path))
            if not self.copy_files(self._packet.old_name, new_name):
                raise WorkerException(self._packet.old_name, " failed to copy.")
            checksum = self.get_md5(new_name)
            Worker2._save_as_file(checksum, os.path.join(new_path, self._packet.new_name + ".md5"))
            date = ctime()
            extension = os.path.splitext(new_name)[1]
            new_packet = self.report_packet(old_name=self._packet.old_name,
                                            new_name=self._packet.new_name,
                                            project_id_prefix=self._packet.project_id_prefix,
                                            project_id_number=self._packet.project_id_number,
                                            object_id_marc=self._packet.object_id_marc,
                                            object_id_number=self._packet.object_id_number,
                                            object_id=self._packet.object_id,
                                            type=self._packet.file_generation,
                                            md5=checksum,
                                            date=date, # TODO change to date Created
                                            file_suffix=self._packet.file_suffix,
                                            file_extension=extension,
                                            notes=None)
            self.job_completed.emit(new_packet)




    def convert_format(self, source, destination):
        print("Converting")
        img = Image.open(source)
        if img.mode == '1':
            # blur the image to make it compress better
            img = img.convert('RGB')
            img = img.filter(ImageFilter.GaussianBlur(3))
        img = img.convert('RGB')



            # raise AmbiguousMode(file['source'])
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
        print("Saving checksum, {}, into {}".format(checksum, file_name))
        with open(file_name, "w") as f:
            f.write(checksum)
            pass
    def copy_files(self, source, destination):
        if not os.path.exists(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        # record.set_Working()
        shutil.copy2(source, destination)
        return True

    @staticmethod
    def get_md5(file_name):

        BUFFER = 8192
        md5 = hashlib.md5()
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(BUFFER), b''):
                md5.update(chunk)
        return md5.hexdigest()

    # def build_report_packet(self):


# class Worker2(object):
#     updateStatus = pyqtSignal(str)
#     reporter = pyqtSignal(NameRecord)
#     reset_progress = pyqtSignal(int)
#     update_progress = pyqtSignal(int)
#     request_report = pyqtSignal()
#     error_reporter = pyqtSignal(str)
#
#     _halt = False
#
#     def __init__(self, job):
#         super(Worker2, self).__init__()
#         self.record = None
#         self.job = job
#
#
#         # def _do_the_renaming(self, record, convert_format=None, print_status=False):
#         if not isinstance(self.job, namedtuple):
#             raise TypeError
#         temp_files = []
#         for part in self.job.parts:
#             if Worker2._halt:
#                 break
#
#             if part.make_copy:
#                 if not os.path.exists(os.path.dirname(part.new_file_name)):
#                     os.makedirs(os.path.dirname(part.new_file_name))
#                 # record.set_Working()
#                 shutil.copy2(part.old_file_name, part.new_file_name)
#
#             if part.convert:
#                 if not os.path.exists(os.path.dirname(part.new_file_name)):
#                     os.makedirs(os.path.dirname(part.new_file_name))
#                 self.convert_format(part.old_file_name, part.new_file_name)
#
#
#                 # # if file.file_status == FileStatus.NEEDS_TO_BE_COPIED:
#                 # #     if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
#                 #         print("Copying {0} to {1}.".format(file.source, file.filename), end="")
#                 #     destination = os.path.join(self.new_path, file.output_filename)
#                 #     shutil.copy2(file.source, destination)
#                 #     if filecmp.cmp(file.source, destination):
#                 #         if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
#                 #             print("  ... Success!")
#                 #
#                 #         new_file.file_status = FileStatus.NEEDS_A_RECORD
#                 #         new_file.file_extension = os.path.splitext(destination)[1]
#                 #         new_file.file_path = os.path.split(destination)[0]
#                 #         new_file.file_suffix = file.file_suffix
#                 #         new_file.file_type = file.file_type
#                 #         new_file.filename = os.path.basename(destination)
#                 #         new_file.md5 = self._calculate_md5(destination)
#
#                     #     record.set_NeedsUpdating()
#                     # else:
#                     #     sys.stderr.write("Failed!\n")
#                     #     raise IOError("File {0} does not match {1]".format(file.source, file.filename))
#     #             elif file.file_status == FileStatus.NEEDS_TO_BE_CREATED:
#     #                 if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
#     #                     print("Converting {0} to {1}.".format(file.source, file.filename), end="")
#     #                 new_file = self.convert_format(file)
#     #
#     #                 if os.path.exists(os.path.join(new_file.file_path, new_file.filename)):
#     #                     if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
#     #                         print("  ... Success!")
#     #                 else:
#     #                     sys.stderr.write("Failed to convert!\n")
#     #                     raise IOError("File {} was not found after being converted from {}".format(new_file.filename, file.source))
#     #             # FIXME!!!
#     #             file.md5 = self._calculate_md5(file.source)
#     #             file.file_suffix = None
#     #             file.file_type = FileTypes.ORIGINAL
#     #             temp_files.append(file)
#     #             temp_files.append(new_file)
#         #             destination = None
#         #         else:
#         #             pass
# 		#
#         # record.parts = temp_files
# 		#
#         # record.set_NeedsUpdating()
#         # return record
#         pass
#
#
    # def convert_format(self, source, destination):
    #         # new_file = copy.copy(file)
	#
    #         # if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
    #         #     print("converting {}".format(file.source))
    #         img = Image.open(source)
    #         if img.mode == '1':
    #             # blur the image to make it compress better
    #             img = img.convert('RGB')
    #             img = img.filter(ImageFilter.GaussianBlur(3))
    #         img = img.convert('RGB')
	#
	#
    #             # raise AmbiguousMode(file['source'])
    #         img.save(destination,
    #                  'jpeg',
    #                  icc_profile=img.info.get("icc_profile"),
    #                  quality=90,
    #                  subsampling=1,
    #                  progressive=True)
    #         img.close()
            # except IOError:
            #     img = Image.open(file['source'])
            #     img.save(os.path.join(self.new_path, file['output_filename']), 'jpeg', icc_profile=img.info.get("icc_profile"), quality=90, subsampling=1, optimize=True)
            #     img.close()
            # if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            #     print("Calculating new checksum")
			#
            # new_file.filename = file.output_filename
            # new_file.md5 = self._calculate_md5(os.path.join(self.new_path, file.output_filename))
            # new_file.file_path = self.new_path
            # new_file.file_suffix = "access"
            # new_file.file_extension = os.path.splitext(file.output_filename)[1]
            # new_file.file_status = FileStatus.DERIVED
            # new_file.file_type = FileTypes.ACCESS
			#
			#
            # return new_file