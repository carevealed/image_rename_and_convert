from enum import Enum, unique
import filecmp
import hashlib
import threading
from operator import itemgetter, attrgetter
import os
from os.path import expanduser
import sqlite3
import shutil
import sys
import types
from PIL import Image, ImageFile, ImageFilter
# from rename_files.worker import Worker2
import copy
from collections import namedtuple
import itertools


@unique
class running_mode(Enum):
    NORMAL = 0
    DEBUG = 1
    BUILD = 2
    INIT = 3

class FileTypes(Enum):
    ORIGINAL = "Original"
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
    DERIVED = 7


class AccessExtensions(Enum):
    JPEG = '.jpg'

class SupportedMasters(Enum):
    TIFF = '.tif'

class AmbiguousMode(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

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
    """
    Contains the information per each part of an object being converted. The files and project information

    """

    file_local_id = 0

    def __init__(self, parts,
                 queue,
                 obj_prefix,
                 obj_num,
                 proj_prefix,
                 proj_num,
                 path=None,
                 make_jpegs_from_tiffs=True,
                 simple=True,
                 included=True):
        """
        :type parts:                    list[record_bundle]
        :type queue:                    int
        :type obj_prefix:               str
        :type obj_num:                  int
        :type proj_prefix:              str
        :type proj_num:                 int
        :type make_jpegs_from_tiffs:    bool
        :type simple:                   bool
        :type included:                 bool


        """
        self.queue = queue
        self.parts = []

        # TODO: IF you want to make complex, here is where do it
        for part in parts:
            files = []
            for file in part.files:


                # file_data.id = self.file_local_id
                file.id = self.file_local_id
                if file.file_status == FileStatus.IGNORE:
                    file.output_filename = ""
                # elif file.file_status == FileStatus.NEEDS_TO_BE_COPIED:
                else:
                    ending = "_" + str(file.file_suffix) + file.file_extension
                    file.output_filename = obj_prefix + "_" + str(obj_num).zfill(6) + ending
                    file.included = included

                # file['id'] = self.file_local_id  # OLD WAY
                # if file['file_status'] == FileStatus.IGNORE:
                #     file['output_filename'] = ""
                # elif file['file_status'] == FileStatus.NEEDS_TO_BE_COPIED:
                # else:
                #     ending = "_" + str(file['file_suffix']) + file['file_extension']
                #     file['output_filename'] = obj_prefix + "_" + str(obj_num).zfill(6) + ending
                #     file['included'] = included
                # file['md5'] = self._calculate_md5(file['old'])

                files.append(file)
            NameRecord.file_local_id += 1
            self.parts.append(files)

        self.project_id = proj_prefix + "_" + str(proj_num)
        self.object_id = obj_prefix + "_" + str(obj_num)
        self.project_id_prefix = proj_prefix
        self.project_id_number = proj_num
        self.object_id_prefix = obj_prefix
        self.object_id_number = obj_num
        self.ia_url = "https://archive.org/details/" + obj_prefix + "_" + str(obj_num).zfill(6)
        self.included = included


        # self.md5 = self._calculate_md5(original_name)
        if len(self.parts) > 1:
            self.isSimple = True
        else:
            self.isSimple = False
        self.complex_obj_group = None
        self._status = RecordStatus.pending

    def reset_fileID(self):
        NameRecord.file_local_id = 0

    def get_status(self):
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
        raise DeprecationWarning
        BUFFER = 8192
        md5 = hashlib.md5()
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(BUFFER), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def __str__(self):
        return "data: " + str(self.get_dict())

    def get_dict(self):
        return {'queue': self.queue,
                'files': self.parts,
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
    halt = False

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

    @staticmethod
    def abort():
        RenameFactory.halt = True

    def update2(self, proj_prefix, proj_start_num, obj_marc, obj_start_num, path):
        queue_count = 0
        for queue in self._queues:
            if queue.included:
                queue.object_id_number = queue_count + obj_start_num
                queue.object_id_suffix = obj_marc
                queue.object_id = obj_marc + "_" +str(queue.object_id_number).zfill(6)
                queue.project_id_number = queue_count + proj_start_num
                queue.project_id_suffix = proj_prefix
                queue.project_id = proj_prefix + "_" + str(queue.project_id_number).zfill(6)
                queue.ia_url = 'https://archive.org/details/' + queue.object_id
                for part in queue.parts:
                    for file in part:
                        filename = queue.object_id + "_" + file.file_suffix + file.file_extension
                        file.included = True
                        file.filename = os.path.join(path, filename)
                        file.output_filename = filename
                queue_count += 1
            else:
                queue.object_id_number = None
                queue.object_id_suffix = None
                queue.object_id = None
                queue.project_id_number = None
                queue.project_id_suffix = None
                queue.project_id = None
                queue.ia_url = None
                for part in queue.parts:
                    for file in part:
                        filename = None
                        file.included = False
                        file.filename = None
                        file.output_filename = None







    def update(self, proj_prefix, proj_start_num, obj_marc, obj_start_num, path):
        raise DeprecationWarning
        new_queues = []
        # queues = )
        NameRecord.file_local_id = 0
        object_count = 0
        queue_count = 0
        for index, old_queue in enumerate(sorted(self._queues, key=lambda x: x.queue)):
            included_files = []
            excluded_files = []
            excluded_files = record_bundle(object_id_prefix=obj_marc, object_id_number=obj_start_num+object_count, path=path)
            new_parts = []
            for part in old_queue.parts:
                new_part = record_bundle(object_id_prefix=obj_marc, object_id_number=obj_start_num+object_count, path=path)
                for file in part:
                    if file.included == True:

                        # files.add_file(file['old'])
                        if file.file_type == FileTypes.MASTER:
                            new_part.add_file2(file.source, file_type_to_create=file.file_type)

                        if file.file_type == FileTypes.ACCESS:
                            new_part.add_file2(file.source, file_type_to_create=file.file_type, new_format=file.file_extension)
                new_parts.append(new_part)

            if len(record) > 0:
                new_queue = NameRecord(parts=new_parts,
                                       queue=queue_count,
                                       obj_prefix=obj_marc,
                                       obj_num=object_count+obj_start_num,
                                       proj_prefix=proj_prefix,
                                       proj_num=proj_start_num+object_count)
                queue_count += 1
                object_count += 1
                new_queues.append(new_queue)
            else:
                record = record_bundle(object_id_prefix=obj_marc, object_id_number=obj_start_num+object_count, path=path)
                for excluded_file in excluded_files.files:
                    file = record_bundle(path=path)
                    file_format = None
                    # file.add_file(excluded_file)
                    if os.path.splitext(excluded_file)[1] == ".jpg":
                        file_type = FileTypes.ACCESS
                    elif os.path.splitext(excluded_file)[1] == ".tif":
                        file_type = FileTypes.MASTER
                        file_format = AccessExtensions.JPEG
                    else:
                        raise TypeError("Unsupported file format, {}".format(os.path.splitext(excluded_file)[1]))
                    if file_type == FileTypes.MASTER:
                        record.add_file2(file_name=excluded_file, file_type_to_create=file_type, include=False)
                    elif file_type == FileTypes.ACCESS:
                        record.add_file2(file_name=excluded_file, file_type_to_create=file_type, include=False, new_format=file_format.value)

                new_queue = NameRecord(parts=record,
                                       queue=queue_count,
                                       obj_prefix=obj_marc,
                                       obj_num=object_count+obj_start_num,
                                       proj_prefix=proj_prefix,
                                       proj_num=proj_start_num+object_count,
                                       included=False)

                queue_count += 1
                new_queues.append(new_queue)



            # compaire the originals
        self._queues = new_queues
        pass


    def clear_queues(self):
        self._queues = []



    def add_queue(self, parts, obj_id_prefix, obj_id_num, proj_id_prefix, proj_id_num):
        if obj_id_prefix in self.object_ids:
            pass
        else:
            self.object_ids[obj_id_prefix] = obj_id_num

        new_queue = NameRecord(parts,
                               len(self._queues),
                               obj_prefix=obj_id_prefix,
                               obj_num=obj_id_num,
                               proj_prefix=proj_id_prefix,
                               proj_num=proj_id_num)


        self._queues.append(new_queue)

    def find_file(self, file_id):
        for queue in self._queues:
            for part in queue.parts:
                for file in part:
                    if file.id == file_id:
                        return file

    def find_queue(self, queue_number):
        for queue in self._queues:
            if queue.queue == queue_number:
                return queue
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

    def set_file_include(self, queue_id, include):
        found_it = False
        for queue in self._queues:

            if queue.queue == queue_id:
                for part in queue.parts:
                    for file in part:
                        # print("From {} to {} for {}".format(file['included'], include, file))
                        file.included = include

                        found_it = True

                if found_it:
                    queue.included = include
                    break




    def execute_rename_from_queue_by_record(self, record, print_status=False):
        return self._do_the_renaming(record, print_status=print_status)

    def _do_the_renaming(self, record, convert_format=None, print_status=False):
        if not isinstance(record, NameRecord):
            raise TypeError
        record.set_Working()
        temp_files = []
        for part in record.parts:

            for file in part:
                if RenameFactory.halt:
                    return False
                if file.file_status == FileStatus.NEEDS_TO_BE_CREATED or file.file_status == FileStatus.NEEDS_TO_BE_COPIED:
                    new_file = copy.copy(file)
                    # new_path = os.path.split(file['new'])[0]
                    if not os.path.exists(self.new_path):
                        os.makedirs(self.new_path)
                    record.set_Working()
                    if file.file_status == FileStatus.NEEDS_TO_BE_COPIED:
                        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                            print("Copying {0} to {1}.".format(file.source, file.filename), end="")
                        destination = os.path.join(self.new_path, file.output_filename)
                        shutil.copy2(file.source, destination)
                        if filecmp.cmp(file.source, destination):
                            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                                print("  ... Success!")

                            new_file.file_status = FileStatus.NEEDS_A_RECORD
                            new_file.file_extension = os.path.splitext(destination)[1]
                            new_file.file_path = os.path.split(destination)[0]
                            new_file.file_suffix = file.file_suffix
                            new_file.file_type = file.file_type
                            new_file.filename = os.path.basename(destination)
                            new_file.md5 = self._calculate_md5(destination)

                            record.set_NeedsUpdating()
                        else:
                            sys.stderr.write("Failed!\n")
                            raise IOError("File {0} does not match {1]".format(file.source, file.filename))
                    elif file.file_status == FileStatus.NEEDS_TO_BE_CREATED:
                        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                            print("Converting {0} to {1}.".format(file.source, file.filename), end="")
                        new_file = self.convert_format(file)

                        if os.path.exists(os.path.join(new_file.file_path, new_file.filename)):
                            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD or print_status:
                                print("  ... Success!")
                        else:
                            sys.stderr.write("Failed to convert!\n")
                            raise IOError("File {} was not found after being converted from {}".format(new_file.filename, file.source))
                    # FIXME!!!
                    file.md5 = self._calculate_md5(file.source)
                    file.file_suffix = None
                    file.file_type = FileTypes.ORIGINAL
                    temp_files.append(file)
                    temp_files.append(new_file)
                    destination = None
                else:
                    pass

        record.parts = temp_files

        record.set_NeedsUpdating()
        return record

    def clear_queues(self):
        self._queues = []

    def show_queues(self):
        # for queue in self._queues:
            # print(queue.get_dict())
        pass


    def swap_queues(self, queue_a, queue_b):
        pass

    def convert_format(self, file):
        new_file = copy.copy(file)
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("converting {}".format(file.source))
        img = Image.open(file.source)
        if img.mode == '1':
            # blur the image to make it compress better
            img = img.convert('RGB')
            img = img.filter(ImageFilter.GaussianBlur(3))
        img = img.convert('RGB')


            # raise AmbiguousMode(file['source'])
        img.save(os.path.join(self.new_path, file.output_filename),
                 'jpeg',
                 icc_profile=img.info.get("icc_profile"),
                 quality=90,
                 subsampling=1,
                 progressive=True)
        img.close()
        # except IOError:
        #     img = Image.open(file['source'])
        #     img.save(os.path.join(self.new_path, file['output_filename']), 'jpeg', icc_profile=img.info.get("icc_profile"), quality=90, subsampling=1, optimize=True)
        #     img.close()
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("Calculating new checksum")

        new_file.filename = file.output_filename
        new_file.md5 = self._calculate_md5(os.path.join(self.new_path, file.output_filename))
        new_file.file_path = self.new_path
        new_file.file_suffix = "access"
        new_file.file_extension = os.path.splitext(file.output_filename)[1]
        new_file.file_status = FileStatus.DERIVED
        new_file.file_type = FileTypes.ACCESS


        return new_file





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
    # _database = sqlite3.connect('data.db')
    _database = None

    # def __new__(cls, *args, **kwargs):
    #     if not cls._instance:
    #         cls._instance = super(ReportFactory, cls).__new__(cls, *args, **kwargs)
    #     return cls._instance
    def __init__(self, database, username=None):
        if database is None:
            raise ValueError("Database cannot be None")
        if username:
            self.username = username
        else:
            self.username = ""
        self._database = sqlite3.connect(database)
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
            try:
                last_batch = self._database.execute('SELECT MAX(job_id) from jobs').fetchone()['MAX(job_id)']
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

        record_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
        for file in record.files:
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("File: {}".format(file))
            self._database.execute('INSERT INTO files('
                                   'type, file_name, file_location, md5, file_suffix, file_extension, destination_id) '
                                   'VALUES(?,?,?,?,?,?,?)',
                                   (file.file_type.value,
                                    file.source,
                                    file.filename,
                                    file.md5,
                                    file.file_suffix,
                                    os.path.splitext(file.filename)[1],
                                    record_id))
            # source_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
            # self._database.execute('UPDATE file_pairs'
            #                        'set record_id, source_id) '
            #                        'VALUES(?,?)', (record_id, source_id))

    @DeprecationWarning
    def add_record(self, record):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("Adding record")

        # NEW WAY

        self._database.execute('INSERT INTO records('
                               'job_id, project_id_prefix, project_id_number, object_id_prefix, object_id_number, ia_url) '
                               'VALUES(?,?,?,?,?,?)',
                               (self._current_batch, record.project_id_prefix, record.project_id_number, record.object_id_prefix, record.object_id_number, record.ia_url))
        record_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']

        for part in record.parts:
            master = []
            original = None
            access = []
            for file in part:
                #FIXME: Something is getting mislabled as a access file after being copyied
                if file.file_type == FileTypes.MASTER:
                    master.append(file)
                elif file.file_type == FileTypes.ACCESS:
                    access.append(file)
                elif file.file_type == FileTypes.ORIGINAL:
                    original = file
                else:
                    raise ValueError

            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("File: {}".format(master))

            # add original into database
            query = 'INSERT INTO files '
            query += '(type, file_name, file_location, md5, file_suffix, file_extension) '
            query += 'VALUES("{}", "{}", "{}", "{}", "{}", "{}")'.format(original.file_type.value,
                                                                         original.source,
                                                                         original.file_path,
                                                                         original.md5,
                                                                         original.file_suffix,
                                                                         os.path.splitext(master[0].filename)[1])
            self._database.execute(query)

            source_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']


            # Add master into database
            for master_file in master:
                query = 'INSERT INTO files '
                query += '(type, file_name, file_location, md5, file_suffix, file_extension, source) '
                query += 'VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(master_file.value,
                                                                                   master_file.filename,
                                                                                   master_file.file_path,
                                                                                   master_file.md5,
                                                                                   master_file.file_suffix,
                                                                                   os.path.splitext(master_file.filename)[1],
                                                                                   source_id)
                self._database.execute(query)
            self._database.execute('INSERT INTO file_pairs('
                                   'record_id, source_id) '
                                   'VALUES(?,?)', (record_id, source_id))

            for access_file in access:
                if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                    print("File: {}".format(master))
                query = 'INSERT INTO files '
                query += '(type, file_name, file_location, md5, file_suffix, file_extension, source) '
                query += 'VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(access_file.file_type.value,
                                                                                   access_file.filename,
                                                                                   access_file.file_path,
                                                                                   access_file.md5,
                                                                                   access_file.file_suffix,
                                                                                   os.path.splitext(access_file.filename)[1],
                                                                                   os.path.splitext(access_file.filename)[1],
                                                                                   source_id)
                self._database.execute(query)
        self._database.commit()
        # pass

    def add_record2(self, record):
        # assert(isinstance(record, tuple))
        original = None
        access = None
        master = None
        # get original
        # get master
        # get access

        total_parts = max(record, key=attrgetter('part_number'))
        parts = []
        for key, group in itertools.groupby(record, key=attrgetter('part_number')):
            parts = list(group)
            for part in parts:

                if part.type == "Original":
                    original = part
                elif part.type == "Access Copy":
                    access = part
                elif part.type == "Preservation Master":
                    master = part
                else:
                    raise ValueError("Not a valid record type")

                # print(part)

            ia_url = "https://archive.org/details/" + original.object_id
            self._database.execute('INSERT INTO records('
                                   'job_id, project_id_prefix, project_id_number, object_id_prefix, object_id_number, ia_url) '
                                   'VALUES(?,?,?,?,?,?)',
                                   (self._current_batch,
                                    original.project_id_prefix,
                                    original.project_id_number,
                                    original.object_id_marc,
                                    original.object_id_number,
                                    ia_url))
            record_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
            # add original into database
            # for part in originals:
            name = os.path.basename(original.old_name)
            path = os.path.dirname(original.old_name)
            query = 'INSERT INTO files '
            query += '(type, file_name, file_location, md5, file_extension) '
            query += 'VALUES("{}", "{}", "{}", "{}", "{}")'.format(original.type,
                                                                   name,
                                                                   path,
                                                                   original.md5,
                                                                   original.file_extension)

            self._database.execute(query)
            source_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']

            # Add master into database
            # for part in masters:
            name = os.path.basename(master.new_name)
            path = os.path.dirname(master.new_name)
            master_notes = "\n".join(master.notes)
            query = 'INSERT INTO files '
            query += '(type, file_name, file_location, md5, file_suffix, file_extension, source, file_notes) '
            query += 'VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(master.type,
                                                                               name,
                                                                               path,
                                                                               master.md5,
                                                                               master.file_suffix.value,
                                                                               master.file_extension,
                                                                               source_id,
                                                                               master_notes)
            self._database.execute(query)
            self._database.execute('INSERT INTO file_pairs('
                                   'record_id, source_id) '
                                   'VALUES(?,?)', (record_id, source_id))

            # for access_file in access:
            #     if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            #         print("File: {}".format(master))
            # for part in access:
            if access:
                access_notes = "\n".join(access.notes)
                name = os.path.basename(access.new_name)
                path = os.path.dirname(access.new_name)
                query = 'INSERT INTO files '
                query += '(type, file_name, file_location, md5, file_suffix, file_extension, source, file_notes) '
                query += 'VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(access.type,
                                                                                   name,
                                                                                   path,
                                                                                   access.md5,
                                                                                   access.file_suffix.value,
                                                                                   access.file_extension,
                                                                                   source_id,
                                                                                   access_notes)
                self._database.execute(query)
        self._database.commit()

        pass
    def show_current_records(self, object_id=None):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("Getting record {0}.".format(object_id))
            queury = self._database.execute('SELECT * FROM report WHERE object_id is \"{0}\"'.format(object_id))
            # for row in queury:
            #     print(row)
        pass

    def get_report(self, object_id=None):
        pass

    def close_database(self):
        self._database.close()
        try:
            self._database.execute("SELECT * FROM jobs")
        except sqlite3.ProgrammingError:
            print("Closed the database")




    def get_last_job(self):
        # results = self._database.execute('SELECT pair_id, file_name, file_location, file_suffix, file_extension, type, '
        #                                  'md5, project_id_prefix, project_id_number, object_id_prefix, '
        #                                  'object_id_number, ia_url '
        #                                  'FROM jobs '
        #                                  'JOIN records ON jobs.job_id=records.job_id '
        #                                  'JOIN file_pairs on records.record_id=file_pairs.record_id '
        #                                  'JOIN files on files.file_id = file_pairs.source_id '
        #                                  'WHERE jobs.job_id IS (?)', (self._current_batch,))
        return self.get_job(self._current_batch)

    def get_job(self, jobNumber):
        # results = self._database.execute('SELECT pair_id, file_name, file_location, file_suffix, file_extension, type, '
        #                                  'md5, project_id_prefix, project_id_number, object_id_prefix, '
        #                                  'object_id_number, ia_url  '
        #                                  'FROM jobs '
        #                                  'JOIN records ON jobs.job_id=records.job_id '
        #                                  'JOIN file_pairs on records.record_id=file_pairs.record_id '
        #                                  'JOIN files on files.file_id = file_pairs.source_id '
        #                                  'WHERE jobs.job_id IS (?)', (jobNumber,))
        #
        results = self._database.execute('SELECT job_id, project_id_prefix, project_id_number, '
                                         'files.file_notes AS "notes", object_id_prefix, object_id_number, '
                                         'source_files.file_name AS "original_name", '
                                         'source_files.md5 AS "original_md5", files.file_name AS "new_name", '
                                         'files.md5 AS "new_md5", '
                                         'files.type, ia_url '
                                         'FROM files LEFT JOIN files AS source_files '
                                         'on files.source = source_files.file_id '
                                         'join file_pairs on source_files.file_id = file_pairs.source_id '
                                         'join records on records.record_id = file_pairs.record_id '
                                         'WHERE job_id is (?)', (jobNumber,))
        return results.fetchall()



class record_bundle(object):
    """
    :type files: list[namespace]
    """
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


    def add_file2(self, file_name, file_type_to_create, include=True, new_format=None):
        # if not self._files:
        include_message = ""
        new_file_name = None
        if file_type_to_create == FileTypes.MASTER:
            if new_format:
                raise ValueError("Master files do not use the new_format argument")
            if include:
                new_file_name = self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="prsv")
            status = FileStatus.NEEDS_TO_BE_COPIED
                # else:
                #     status = FileStatus.NEEDS_TO_BE_CREATED
            # else:
            #     status = FileStatus.IGNORE

            if not new_file_name:
                new_file_name = self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="prsv")

            file_to_add_ = types.SimpleNamespace(filename=new_file_name,
                                                 file_path=os.path.split(file_name)[0],
                                                 file_type=FileTypes.MASTER,
                                                 source=file_name,
                                                 md5=self._calculate_md5(file_name),
                                                 included=include,
                                                 file_suffix="prsv",
                                                 file_extension=os.path.splitext(file_name)[1],
                                                 file_status=status)
            # old style
            # file_to_add = dict({"filename": new_file_name,
            #                     "file_path": os.path.split(file_name)[0],
            #                     "file_type": FileTypes.MASTER,
            #                     "source": file_name,
            #                     "md5": self._calculate_md5(file_name),
            #                     "included": include,
            #                     "file_suffix": "prsv",
            #                     "file_extension": os.path.splitext(file_name)[1],
            #                     "file_status": status})

        elif file_type_to_create == FileTypes.ACCESS:
            if new_format:
                file_extension = new_format
            else:
                file_extension = os.path.splitext(file_name)[1]
            if include:
                new_file_name = self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="access", extension=file_extension)
            status = FileStatus.NEEDS_TO_BE_CREATED
            # else:
            #     status = FileStatus.IGNORE
            if not new_file_name:
                new_file_name = self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="access", extension=file_extension)
            file_to_add_ = types.SimpleNamespace(filename=new_file_name,
                                                 file_path=os.path.split(file_name)[0],
                                                 file_type=FileTypes.ACCESS,
                                                 source=file_name,
                                                 md5=None,
                                                 included=include,
                                                 file_suffix="access",
                                                 file_extension=file_extension,
                                                 file_status=status)



            # old style
            # file_to_add = dict({"filename": new_file_name,
            #                     "file_path": os.path.split(file_name)[0],
            #                     "file_type": FileTypes.ACCESS,
            #                     "source": file_name,
            #                     "md5": None,
            #                     "included": include,
            #                     "file_suffix": "access",
            #                     "file_extension": file_extension,
            #                     "file_status": status})
        else:
            raise ValueError("file_type must be a FileTypes type")
        self._files.append(file_to_add_)

    # pass

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
