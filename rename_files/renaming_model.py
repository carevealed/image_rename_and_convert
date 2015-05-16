from enum import Enum, unique
import filecmp
import hashlib
import threading
from operator import itemgetter
import os
from os.path import expanduser
import sqlite3
import shutil
import sys
from PIL import Image


@unique
class running_mode(Enum):
    NORMAL = 0
    DEBUG = 1
    BUILD = 2
    INIT = 3

class FileTypes(Enum):
    MASTER = "Master"
    ACCESS = "Access"

class FileStatus(Enum):
    READY = 0
    WORKING = 1
    NEEDS_TO_BE_CREATED = 2
    NEEDS_TO_BE_COPIED = 3
    NEEDS_A_RECORD = 4
    COPIED = 5
    IGNORE = 6


class AccessExtensions(Enum):
    JPEG = '.jpg'

CHECK_CHECKSUMS = True
DEBUG = True
BUILD_MODE = True
MODE = running_mode.NORMAL

@unique
class RecordStatus(Enum):
    pending = 0
    working = 1
    done = 2
    NEED_TO_APPEND_RECORD = 3


class Singleton(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

class NameRecord(object):
    '''
    Contains the information per each file being converted. The files and project information
    '''
    file_local_id = 0
    def __init__(self, files, queue, obj_prefix, obj_num, proj_prefix, proj_num, path=None, make_jpegs_from_tiffs=True, simple=True, included=True):
        self.queue = queue
        self.files = []

        # print("files: {}".format(files))
        # TODO: IF you want to make complex, here is where do it
        for file in files.files:
            # if os.path.splitext(file)[1] == ".tif":
            #     file['make_access'] = True
            file['id'] = self.file_local_id
            if file['file_status'] == FileStatus.IGNORE:
                file['output_filename'] = ""
            else:
                file['output_filename'] = obj_prefix + "_" + str(obj_num).zfill(6) + ".jpg"
            NameRecord.file_local_id += 1
            # file['md5'] = self._calculate_md5(file['old'])

            file['included'] = included

            self.files.append(file)

        self.project_id = proj_prefix + "_" + str(proj_num)
        self.object_id = obj_prefix + "_" + str(obj_num)
        self.project_id_prefix = proj_prefix
        self.project_id_number = proj_num
        self.object_id_prefix = obj_prefix
        self.object_id_number = obj_num
        self.ia_url = "https://archive.org/details/" + obj_prefix + "_" + str(obj_num).zfill(6)
        self.included = included


        # self.md5 = self._calculate_md5(original_name)
        self.isSimple = simple
        self.complex_obj_group = None
        self._status = RecordStatus.pending

    def get_status(self):
        # print(self._status)
        if self._status == RecordStatus.pending:
            return "Ready"
        if self._status == RecordStatus.working:
            return "Working"
        if self._status == RecordStatus.done:
            return "Completed"

    def set_Pending(self):
        self._status = RecordStatus.pending

    def set_Working(self):
        self._status = RecordStatus.working

    def set_Done(self):
        self._status = RecordStatus.done
    def set_NeedsUpdating(self):
        self._status = RecordStatus.NEED_TO_APPEND_RECORD

    def _calculate_md5(self, file_name):
        BUFFER = 8192
        md5 = hashlib.md5()
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(BUFFER), b''):
                md5.update(chunk)
        raise DeprecationWarning
        return md5.hexdigest()

    def __str__(self):
        return "data: " + str(self.get_dict())

    def get_dict(self):
        return {'queue': self.queue,
                'files': self.files,
                # 'original name': self.old_name,
                # 'new name': self.new_name,
                'project id': self.project_id,
                # 'md5': self.md5,
                'simple': self.isSimple,
                'group': self.complex_obj_group,
                'status': self._status}


@unique
class ProgressStatus(Enum):
    idle = 0
    working = 1

class RenameFactory(object):
    def __init__(self, path, project_id=None):
        self._queues = []
        self.names_used = []
        self.new_path = path
        self.current_progress = 0
        self._status = ProgressStatus.idle
        self.project_id = str
        self.object_id = str
        self.object_ids = dict()
        if project_id:
            self.project_id = project_id

    def __len__(self):
        return len(self._queues)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_progress < self.__len__():
            record = self._queues[self.current_progress]
            self.current_progress += 1
            return record
        else:
            raise StopIteration

    @property
    def queues(self):
        return self._queues
    @property
    def status(self):
        return self._status

    def _calculate_md5(self, file_name):
        BUFFER = 8192
        md5 = hashlib.md5()
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(BUFFER), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def update(self, proj_prefix, proj_start_num, obj_marc, obj_start_num, path):
        # print("updating builder")
        # print("proj_prefix: {}, proj_start_num: {}, obj_marc: {}, obj_start_num: {}".format(proj_prefix, proj_start_num, obj_marc, obj_start_num))
        new_queues = []
        # queues = )
        NameRecord.file_local_id = 0
        object_count = 0
        queue_count = 0
        for index, old_queue in enumerate(sorted(self._queues, key=lambda x: x.queue)):
            # print("\nOld: ", end="")
            # print(old_queue)
            included_files = []
            excluded_files = []
            files = record_bundle(object_id_prefix=obj_marc, object_id_number=obj_start_num+object_count, path=path)
            for file in old_queue.files:
                if file['included'] == True:
                    # files.add_file(file['old'])
                    if file['file_type'] == FileTypes.MASTER:
                        files.add_file2(file['source'], file['file_type'])

                    if file['file_type'] == FileTypes.ACCESS:
                        files.add_file2(file['source'], file['file_type'], new_format=file['file_extension'])

                else:
                    excluded_files.append(file['source'])
            # print("Included files:{}".format(included_files))

            if len(files) > 0:
                new_queue = NameRecord(files=files,
                                       queue=queue_count,
                                       obj_prefix=obj_marc,
                                       obj_num=object_count+obj_start_num,
                                       proj_prefix=proj_prefix,
                                       proj_num=proj_start_num+object_count)
                queue_count += 1
                object_count += 1
                new_queues.append(new_queue)
            else:
                # print("excluded files size: {}".format(len(excluded_files)))
                for excluded_file in excluded_files:
                    print(excluded_file)
                    file = record_bundle(path=path)
                    file_format = None
                    # file.add_file(excluded_file)
                    if os.path.splitext(excluded_file)[1] == ".jpg":
                        file_type = FileTypes.MASTER
                        file_format = AccessExtensions.JPEG
                    elif os.path.splitext(excluded_file)[1] == ".tif":
                        file_type = FileTypes.ACCESS
                        file_format = AccessExtensions.JPEG
                    else:
                        raise TypeError("Unsupported file format, {}".format(os.path.splitext(excluded_file)[1]))
                    if file_type == FileTypes.MASTER:
                        file.add_file2(file_name=excluded_file, file_type=file_type, include=False)
                    elif file_type == FileTypes.ACCESS:
                        file.add_file2(file_name=excluded_file, file_type=file_type, include=False, new_format=file_format)




                    new_queue = NameRecord(files=file,
                                           queue=queue_count,
                                           obj_prefix=obj_marc,
                                           obj_num=object_count+obj_start_num,
                                           proj_prefix=proj_prefix,
                                           proj_num=proj_start_num+object_count,
                                           included=False)

                    queue_count += 1
                    new_queues.append(new_queue)


            # print("New: ", end="")
            # print(new_queue)

            # compaire the originals
        self._queues = new_queues
        pass


    def clear_queues(self):
        self._queues = []

    def add_queue(self, files, obj_id_prefix, obj_id_num, proj_id_prefix, proj_id_num):
        if obj_id_prefix in self.object_ids:
            # print("found one")
            pass
        else:
            self.object_ids[obj_id_prefix] = obj_id_num


        new_queue = NameRecord(files, len(self._queues), obj_prefix=obj_id_prefix, obj_num=obj_id_num, proj_prefix=proj_id_prefix, proj_num=proj_id_num)
        self._queues.append(new_queue)

    def find_file(self, file_id):
        # print("Finding file id #{}".format(file_id))
        for queue in self._queues:
            for file in queue.files:
                # print(file)
                if file['id'] == file_id:
                    return file


    def remove_queue(self, file_name):
        temp_queues = []
        found_one = False
        for queue in self._queues:
            if queue.old_name == file_name:
                found_one = True
                if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                    print("Removing {0} from queue.".format(file_name))
            else:
                temp_queues.append(queue)
        self._queues = temp_queues
        if not found_one:
            raise ValueError("Did not find {0} in queues.".format(file_name))

    def make_complex(self, *args):
        # TODO: make_complex()
        pass

    def make_simple(self, *args):
        # TODO: make_simple()
        pass

    def execute_rename_from_queue_by_number(self, queue_number):
        # TODO: execute_rename_from_queue()

        pass

    def set_file_include(self, file_id, include):
        found_it = False

        for queue in self._queues:
            for file in queue.files:
                # print(file)
                if file['id'] == file_id:
                    print("From {} to {} for {}".format(file['included'], include, file))
                    file['included'] = include
                    print(file)
                    found_it = True
                    break
            if found_it:
                break


    def execute_rename_from_queue_by_record(self, record, print_status=False):
        return self._do_the_renaming(record, print_status=print_status)

    def _do_the_renaming(self, record, convert_format=None, print_status=False):
        if not isinstance(record, NameRecord):
            raise TypeError
        record.set_Working()
        temp_files = []
        for file in record.files:
            if file['file_status'] == FileStatus.NEEDS_TO_BE_CREATED or file['file_status'] == FileStatus.NEEDS_TO_BE_COPIED:
                # new_path = os.path.split(file['new'])[0]
                if not os.path.exists(self.new_path):
                    os.makedirs(self.new_path)
                record.set_Working()
                if file['file_status'] == FileStatus.NEEDS_TO_BE_COPIED:
                    if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                        print("Copying {0} to {1}.".format(file['source'], file['filename']), end="")
                    destination = os.path.join(self.new_path, file['output_filename'])
                    print(destination)
                    shutil.copy2(file['source'], destination)
                    if filecmp.cmp(file['source'], file['filename']):
                        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                            print("  ... Success!")
                        file['file_status'] = FileStatus.NEEDS_A_RECORD
                        file['file_extension'] = os.path.splitext(destination)
                        file['file_path'] = os.path.split(destination)[0]
                        file['file_suffix'] = "access"
                        file['file_type'] = FileTypes.ACCESS
                        file['filename'] = os.path.basename(destination)
                        file['md5'] = self._calculate_md5(destination)

                        record.set_NeedsUpdating()
                    else:
                        sys.stderr.write("Failed!\n")
                        raise IOError("File {0} does not match {1]".format(file['source'], file['filename']))
                elif file['file_status'] == FileStatus.NEEDS_TO_BE_CREATED:
                    if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                        print("Converting {0} to {1}.".format(file['source'], file['filename']), end="")
                    file = self.convert_format(file)
                    if os.path.exists(file['filename']):
                        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                            print("  ... Success!")
                    else:
                        sys.stderr.write("Failed to convert!\n")
                        raise IOError("File {} was not found after being converted from {}".format(file['filename'], file['source']))
            temp_files.append(file)
        record.files = temp_files

        record.set_NeedsUpdating()
        # print("Done")
        return record

    def clear_queues(self):
        self._queues = []

    def show_queues(self):
        for queue in self._queues:
            print(queue.get_dict())



    def swap_queues(self, queue_a, queue_b):
        pass

    def convert_format(self, file):
        if file['file_extension'] == AccessExtensions.JPEG:
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("converting {}".format(file['source']))
            img = Image.open(file['source'])
            img.save(file['output_filename'], 'jpeg', icc_profile=img.info.get("icc_profile"), quality=90, subsampling=1)
            img.close()
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("Calculating new checksum")
            file['md5'] = self._calculate_md5(file['source'])
        return file





def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class ReportFactory(metaclass=Singleton):
    '''
    This class interacts with the sqlite database for storing and retrieving the data for current and past renamings.
    This class is a singleton to avoid conflicts with writing and accessing the database.
    '''
    # _instance = None
    _database = sqlite3.connect('data.db')

    # def __new__(cls, *args, **kwargs):
    #     if not cls._instance:
    #         cls._instance = super(ReportFactory, cls).__new__(cls, *args, **kwargs)
    #     return cls._instance
    def __init__(self, username=None):
        if username:
            self.username = username
        else:
            self.username = ""
        self.database = []
        self._database.row_factory = dict_factory
        self._current_batch = 0

    @property
    def current_batch(self):
        return self._current_batch
    def initize_database(self):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("init the database")
        if not MODE == running_mode.INIT:
            # print("data.db: {}".format(os.path.exists('data.db')))
            # dummy = self._database.execute('SHOW TABLES').fetchall()
            # for dum in dummy:
            #     print(dum)
            try:
                last_batch = self._database.execute('SELECT MAX(job_id) from jobs').fetchone()['MAX(job_id)']
                # print("last_batch, type: {} value:{}".format(type(last_batch), last_batch))
                if last_batch:
                    self._current_batch = int(last_batch) + 1

                else:
                    self._current_batch = 0
            except sqlite3.OperationalError:
                print("Unable to find database")

        if MODE == running_mode.BUILD:
            pass
            # NEW FORMAT
            # Clear anything out if already exist
            # self._database.execute('DROP TABLE IF EXISTS jobs;')
            # self._database.execute('DROP TABLE IF EXISTS records;')
            # self._database.execute('DROP TABLE IF EXISTS files;')
            #
            # # jobs table
            # self._database.execute('CREATE TABLE jobs('
            #                        'job_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
            #                        'username VARCHAR(255) );')
            # # records table
            # self._database.execute('CREATE TABLE records('
            #                        'record_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL,'
            #                        'job_id INTEGER,'
            #                        'project_id_prefix VARCHAR(10),'
            #                        'project_id_number INTEGER,'
            #                        'object_id_prefix VARCHAR(10),'
            #                        'object_id_number INTERGER,'
            #                        'FOREIGN KEY(job_id) REFERENCES jobs(job_id));')
            #
            # # files table
            # self._database.execute('CREATE TABLE files('
            #                        'file_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
            #                        'record_id INTEGER,'
            #                        'source VARCHAR(255),'
            #                        'destination VARCHAR(255),'
            #                        'date_renamed DATE DEFAULT CURRENT_TIMESTAMP,'
            #                        'md5 VARCHAR(32),'
            #                        'file_suffix VARCHAR(20),'
            #                        'file_extension VARCHAR(4),'
            #                        'file_notes TEXT,'
            #                        'FOREIGN KEY(record_id) REFERENCES records(record_id));')




        self._database.execute('INSERT INTO jobs(username) '
                               'VALUES(?)',
                               (self.username,))
        self._current_batch = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
        self._database.commit()

    def _add_access_files(self, record):

        # print("Adding access")
        record_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
        for file in record.files:
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("File: {}".format(file))
            self._database.execute('INSERT INTO files('
                                   'type, file_name, file_location, md5, file_suffix, file_extension, destination_id) '
                                   'VALUES(?,?,?,?,?,?,?)',
                                   (file["file_type"].value, file['source'], file['filename'], file['md5'], file["file_suffix"], os.path.splitext(file['filename'])[1], record_id))
            # source_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
            # self._database.execute('UPDATE file_pairs'
            #                        'set record_id, source_id) '
            #                        'VALUES(?,?)', (record_id, source_id))
    def add_record(self, record):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("Adding record")

        # NEW WAY

        self._database.execute('INSERT INTO records('
                               'job_id, project_id_prefix, project_id_number, object_id_prefix, object_id_number, ia_url) '
                               'VALUES(?,?,?,?,?,?)',
                               (self._current_batch, record.project_id_prefix, record.project_id_number, record.object_id_prefix, record.object_id_number, record.ia_url))
        record_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
        for file in record.files:
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("File: {}".format(file))
            self._database.execute('INSERT INTO files('
                                   'type, file_name, file_location, md5, file_suffix, file_extension) '
                                   'VALUES(?,?,?,?,?,?)',
                                   (file["file_type"].value, file['source'], file['filename'], file['md5'], file["file_suffix"], os.path.splitext(file['filename'])[1]))
            source_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
            self._database.execute('INSERT INTO file_pairs('
                                   'record_id, source_id) '
                                   'VALUES(?,?)', (record_id, source_id))
            # print(FileTypes.MASTER.value)
        self._database.commit()
        pass


    def show_current_records(self, object_id=None):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("Getting record {0}.".format(object_id))
            queury = self._database.execute('SELECT * FROM report WHERE object_id is \"{0}\"'.format(object_id))
            for row in queury:
                print(row)
        pass

    def get_report(self, object_id=None):
        pass

    def close_database(self):
        self._database.close()

    def get_last_job(self):
        # results = self._database.execute('SELECT file_name, file_location, md5, project_id_prefix, project_id_number, object_id_prefix, object_id_number, ia_url '
        results = self._database.execute('SELECT pair_id, file_name, file_location, file_suffix, file_extension, type, '
                                         'md5, project_id_prefix, project_id_number, object_id_prefix, '
                                         'object_id_number, ia_url '
                                         'FROM jobs '
                                         'JOIN records ON jobs.job_id=records.job_id '
                                         'JOIN file_pairs on records.record_id=file_pairs.record_id '
                                         'JOIN files on files.file_id = file_pairs.source_id '
                                         'WHERE jobs.job_id IS (?)', (self._current_batch,))
        return results.fetchall()

    def get_job(self, jobNumber):
        results = self._database.execute('SELECT pair_id, file_name, file_location, file_suffix, file_extension, type, '
                                         'md5, project_id_prefix, project_id_number, object_id_prefix, '
                                         'object_id_number, ia_url  '
                                         'FROM jobs '
                                         'JOIN records ON jobs.job_id=records.job_id '
                                         'JOIN file_pairs on records.record_id=file_pairs.record_id '
                                         'JOIN files on files.file_id = file_pairs.source_id '
                                         'WHERE jobs.job_id IS (?)', (jobNumber,))
        return results.fetchall()



class record_bundle(object):

    def __init__(self, object_id_prefix=None, object_id_number=None, path=None):

        self.object_id_prefix = object_id_prefix
        self.object_id_number = object_id_number
        self._files = []
        self.complex = False
        if path:
            self.path = path
        else:
            raise ValueError("Needs a path")
            # self.path = expanduser("~")

    def __str__(self):
        reply = ""
        for file in self._files:
            reply += str(file)
        return reply

    def __len__(self):
        # print("len type: {}".format(type(len(self._files))))
        # int(len(self._files))
        return len(self._files)

    @property
    def files(self):
        return self._files

    def add_file(self, file_name, new_name=None):
        raise DeprecationWarning("Use add file2 instead")

        if not self._files:
            if new_name:
                file_pair = dict({"old": file_name, "new": os.path.join(self.path, new_name)})
            elif not self.object_id_prefix:  # in other words, if the file is ignored
                file_pair = dict({"old": file_name, "new": None})
            else:
                file_pair = dict({"old": file_name, "new": self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="prsv")})
        else:
            self.complex = True
            if new_name:
                file_pair = dict({"old": file_name, "new": os.path.join(self.path, new_name)})
            else:
                suffix = str(len(self._files)+1).zfill(4)+ "_presv"
                file_pair = dict({"old": file_name, "new": self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix=suffix)})

        self._files.append(file_pair)


    def add_file2(self, file_name, file_type=FileTypes.MASTER, include=True, new_format=None):
        if not self._files:
            new_file_name = None
            if file_type == FileTypes.MASTER:
                if new_format:
                    raise ValueError("Master files do not use the new_format argument")
                if include:
                    new_file_name = self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="access")
                    status = FileStatus.NEEDS_TO_BE_COPIED
                else:
                    status = FileStatus.IGNORE

                file_to_add = dict({"filename": os.path.basename(file_name),
                                    "file_path": os.path.split(file_name)[0],
                                    "file_type": FileTypes.MASTER,
                                    "source": file_name,
                                    "md5": self._calculate_md5(file_name),
                                    "file_suffix": "prsv",
                                    "file_extension": os.path.splitext(file_name)[1],
                                    "file_status": status})

            elif file_type == FileTypes.ACCESS:
                if new_format:
                    file_extension = new_format
                else:
                    file_extension = os.path.splitext(file_name)[1]
                if include:
                    new_file_name = self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="access", extension=file_extension)
                    status = FileStatus.NEEDS_TO_BE_CREATED
                else:
                    status = FileStatus.IGNORE
                file_to_add = dict({"filename": os.path.basename(file_name),
                                    "file_path": os.path.split(file_name)[0],
                                    "file_type": FileTypes.MASTER,
                                    "source": file_name,
                                    "md5": None,
                                    "file_suffix": "access",
                                    "file_extension": file_extension,
                                    "file_status": status})
            else:
                raise ValueError("file_type must be a FileTypes type")
            self._files.append(file_to_add)

        pass

    def generate_CAVPP_name(self, object_prefix, file_name, suffix, extension=None):
        # path = os.path.split(file_name)[0]
        if isinstance(extension, AccessExtensions):
            extension = extension.value
        if not extension:
            extension = os.path.splitext(file_name)[1]

        new_name = object_prefix + "_" + str(self.object_id_number).zfill(6) + "_" + suffix + str(extension)
        if self.path:
            new_name = os.path.join(self.path, new_name)
        return new_name

    def _calculate_md5(self, file_name):
        BUFFER = 8192
        md5 = hashlib.md5()
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(BUFFER), b''):
                md5.update(chunk)
        return md5.hexdigest()