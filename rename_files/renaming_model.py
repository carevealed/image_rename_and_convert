from enum import Enum, unique
import filecmp
import hashlib
import os
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
    def __init__(self, files, queue, obj_prefix, obj_num, proj_prefix, proj_num, path=None, simple=True, included=True):
        self.queue = queue
        self.files = []
        for file in files.files:
            file['md5'] = self._calculate_md5(file['old'])
            file['included'] = included
            self.files.append(file)

        self.project_id = proj_prefix + "_" + str(proj_num)
        self.object_id = obj_prefix + "_" + str(obj_num)
        self.project_id_prefix = proj_prefix
        self.project_id_number = proj_num
        self.object_id_prefix = obj_prefix
        self.object_id_number = obj_num
        self.included = included

        # self.md5 = self._calculate_md5(original_name)
        self.isSimple = simple
        self.complex_obj_group = None
        self._status = RecordStatus.pending


        ## USE THIS IF NEED BE ****************************************************************************************************
    # def __init__(self, original_name, queue, object_id, project_id, file_type=None, new_name=None, path=None, simple=True):
    #     self.queue = queue
    #     self.old_name = original_name
    #
    #     if not new_name:
    #         if path:
    #             newpath = path
    #         else:
    #             # newpath = os.path.abspath(os.path.join(os.path.split(original_name)[0],"../newfiles/")) # FIXME WRONG FOLDER!!! REALLY BAD!!!
    #             newpath = '/Volumes/CAVPPTestDrive/test'
    #         _new_name = object_id
    #         if file_type:
    #             _new_name += ("_" + file_type)
    #         self.new_name = os.path.join(newpath, (_new_name + os.path.splitext(original_name)[1]))
    #     else:
    #         self.new_name = new_name
    #     self.project_id = project_id
    #     self.object_id = object_id
    #     self.md5 = self._calculate_md5(original_name)
    #     self.isSimple = simple
    #     self.complex_obj_group = None
    #     self._status = RecordStatus.pending
        ## USE THIS IF NEED BE ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def get_status(self):
        return self._status

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
        return str(self.get_dict())

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

    def add_queue(self, files, obj_id_prefix, obj_id_num, proj_id_prefix, proj_id_num):
        if obj_id_prefix in self.object_ids:
            # print("found one")
            pass
        else:
            self.object_ids[obj_id_prefix] = obj_id_num


        new_queue = NameRecord(files, len(self._queues), obj_prefix=obj_id_prefix, obj_num=obj_id_num, proj_prefix=proj_id_prefix, proj_num=proj_id_num)
        self._queues.append(new_queue)

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

    def include_file(self, fileName, include=True):

        for queue in self._queues:
            print(type(queue.files))
            print(queue.files)
        # self._do_the_renaming()

    def execute_rename_from_queue_by_record(self, record):
        return self._do_the_renaming(record)

    def _do_the_renaming(self, record):
        if not isinstance(record, NameRecord):
            raise TypeError
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
                               'job_id, project_id_prefix, project_id_number, object_id_prefix, object_id_number) '
                               'VALUES(?,?,?,?,?)',
                               (self.current_batch, record.project_id_prefix, record.project_id_number, record.object_id_prefix, record.object_id_number))
        record_id = self._database.execute('SELECT LAST_INSERT_ROWID()').fetchone()['LAST_INSERT_ROWID()']
        for file in record.files:
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
        results = self._database.execute('SELECT source, destination, md5, project_id_prefix, project_id_number, object_id_prefix, object_id_number '
                                         'FROM jobs '
                                         'JOIN records ON jobs.job_id=records.job_id '
                                         'JOIN files ON records.record_id=files.record_id '
                                         'WHERE jobs.job_id IS (?)', (self.current_batch,))
        return results.fetchall()


class record_bundle(object):

    def __init__(self, object_id_prefix, object_id_number, path=None):
        self.object_id_prefix = object_id_prefix
        self.object_id_number = object_id_number
        self._files = []
        self.complex = False
        if path:
            self.path = path
        else:
            self.path = None

    def __str__(self):
        reply = ""
        for file in self._files:
            reply += str(file)
        return reply
    @property
    def files(self):
        return self._files

    def add_file(self, file_name, new_name=None):
        if not self._files:
            if new_name:
                file_pair = dict({"old": file_name, "new": new_name})
            else:
                file_pair = dict({"old": file_name, "new": self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix="prsv")})
        else:
            self.complex = True
            if new_name:
                file_pair = dict({"old": file_name, "new": new_name})
            else:
                suffix = str(len(self._files)+1).zfill(4)+ "_presv"
                file_pair = dict({"old": file_name, "new": self.generate_CAVPP_name(object_prefix=self.object_id_prefix, file_name=file_name, suffix=suffix)})

        self._files.append(file_pair)


    def generate_CAVPP_name(self, object_prefix, file_name, suffix):
        # path = os.path.split(file_name)[0]
        extension = os.path.splitext(file_name)[1]
        new_name = object_prefix + "_" + str(self.object_id_number).zfill(5) +"_" + suffix + extension
        if self.path:
            new_name = os.path.join(self.path, new_name)
        return new_name