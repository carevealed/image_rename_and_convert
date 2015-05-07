from enum import Enum, unique
import filecmp
import hashlib
from operator import itemgetter
import os
from os.path import expanduser
import sqlite3
import shutil
import sys


@unique
class running_mode(Enum):
    NORMAL = 0
    DEBUG = 1
    BUILD = 2
    INIT = 3

CHECK_CHECKSUMS = True
DEBUG = True
BUILD_MODE = True
MODE = running_mode.NORMAL

@unique
class RecordStatus(Enum):
    pending = 0
    working = 1
    done = 2


class Singleton(type):
    _instance = None
    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance

class NameRecord(object):
    file_local_id = 0
    def __init__(self, files, queue, obj_prefix, obj_num, proj_prefix, proj_num, path=None, simple=True, included=True):
        self.queue = queue
        self.files = []

        # print("files: {}".format(files))
        for file in files.files:
            file['id'] = self.file_local_id
            NameRecord.file_local_id += 1
            file['md5'] = self._calculate_md5(file['old'])
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

    def _calculate_md5(self, file_name):
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
    def __init__(self, project_id=None):
        self._queues = []
        self.names_used = []
        self.new_path = "/Volumes/CAVPPTestDrive/DPLA0003/newfolder/"
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

    def status(self):
        return self._status

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
                    files.add_file(file['old'])
                else:
                    excluded_files.append(file['old'])
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
                    file = record_bundle(path=path)
                    file.add_file(excluded_file)
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
        found_it = False;
        for queue in self._queues:
            for file in queue.files:
                # print(file)
                if file['id'] == file_id:
                    file['included'] = include
                    found_it = True
                    break
            if found_it:
                break


    def execute_rename_from_queue_by_record(self, record):
        return self._do_the_renaming(record)

    def _do_the_renaming(self, record):
        if not isinstance(record, NameRecord):
            raise TypeError
        record.set_Working()
        for file in record.files:

            new_path = os.path.split(file['new'])[0]
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("Copying {0} to {1}.".format(file['old'], new_path), end="")
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            record.set_Working()
            shutil.copy2(file['old'], file['new'])
            if filecmp.cmp(file['old'], file['new']):
                if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                    print("  ... Success!")
                record.set_Done()
            else:
                sys.stderr.write("Failed!\n")
                raise IOError("File {0} does not match {1]".format(file['old'], file['new']))
        record.set_Done()
        # print("Done")
        return record

    def clear_queues(self):
        self._queues = []

    def show_queues(self):
        for queue in self._queues:
            print(queue.get_dict())



    def swap_queues(self, queue_a, queue_b):
        pass

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
        self.current_batch = 0

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
                    self.current_batch = int(last_batch) + 1

                else:
                    self.current_batch = 0
            except sqlite3.OperationalError:
                print("Unable to find database")

        if MODE == running_mode.BUILD:
            # NEW FORMAT
            # Clear anything out if already exist
            self._database.execute('DROP TABLE IF EXISTS jobs;')
            self._database.execute('DROP TABLE IF EXISTS records;')
            self._database.execute('DROP TABLE IF EXISTS files;')

            # jobs table
            self._database.execute('CREATE TABLE jobs('
                                   'job_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                                   'username VARCHAR(255) );')
            # records table
            self._database.execute('CREATE TABLE records('
                                   'record_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL,'
                                   'job_id INTEGER,'
                                   'project_id_prefix VARCHAR(10),'
                                   'project_id_number INTEGER,'
                                   'object_id_prefix VARCHAR(10),'
                                   'object_id_number INTERGER,'
                                   'FOREIGN KEY(job_id) REFERENCES jobs(job_id));')

            # files table
            self._database.execute('CREATE TABLE files('
                                   'file_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                                   'record_id INTEGER,'
                                   'source VARCHAR(255),'
                                   'destination VARCHAR(255),'
                                   'date_renamed DATE DEFAULT CURRENT_TIMESTAMP,'
                                   'md5 VARCHAR(32),'
                                   'file_suffix VARCHAR(20),'
                                   'file_extension VARCHAR(4),'
                                   'file_notes TEXT,'
                                   'FOREIGN KEY(record_id) REFERENCES records(record_id));')




        self._database.execute('INSERT INTO jobs(username) '
                               'VALUES(?)',
                               (self.username,))
        self.current_batch = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
        self._database.commit()

    def add_record(self, record):
        if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
            print("Adding record")

        # NEW WAY

        self._database.execute('INSERT INTO records('
                               'job_id, project_id_prefix, project_id_number, object_id_prefix, object_id_number, ia_url) '
                               'VALUES(?,?,?,?,?,?)',
                               (self.current_batch, record.project_id_prefix, record.project_id_number, record.object_id_prefix, record.object_id_number, record.ia_url))
        record_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
        for file in record.files:
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("File: {}".format(file))
            self._database.execute('INSERT INTO files('
                                   'record_id, source, destination, md5, file_suffix, file_extension) '
                                   'VALUES(?,?,?,?,?,?)',
                                   (record_id, file['old'], file['new'], file['md5'], "prsv", os.path.splitext(file['new'])[1]))

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
        results = self._database.execute('SELECT source, destination, md5, project_id_prefix, project_id_number, object_id_prefix, object_id_number, ia_url '
                                         'FROM jobs '
                                         'JOIN records ON jobs.job_id=records.job_id '
                                         'JOIN files ON records.record_id=files.record_id '
                                         'WHERE jobs.job_id IS (?)', (self.current_batch,))
        return results.fetchall()

    def get_job(self, jobNumber):
        results = self._database.execute('SELECT source, destination, md5, project_id_prefix, project_id_number, object_id_prefix, object_id_number, ia_url '
                                         'FROM jobs '
                                         'JOIN records ON jobs.job_id=records.job_id '
                                         'JOIN files ON records.record_id=files.record_id '
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


    def generate_CAVPP_name(self, object_prefix, file_name, suffix):
        # path = os.path.split(file_name)[0]
        extension = os.path.splitext(file_name)[1]
        new_name = object_prefix + "_" + str(self.object_id_number).zfill(6) +"_" + suffix + extension
        if self.path:
            new_name = os.path.join(self.path, new_name)
        return new_name