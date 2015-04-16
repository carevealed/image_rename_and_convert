from enum import Enum , unique
import filecmp
import hashlib
import os
import sqlite3
import shutil
import sys

CHECK_CHECKSUMS = True
DEBUG = True

@unique
class RecordStatus(Enum):
    pending = 0
    working = 1
    done = 2


class NameRecord(object):
    def __init__(self, original_name, new_name, queue, simple=True):

        self.queue = queue
        self.old_name = original_name
        self.new_name = new_name
        self.project_id = "adsfasdf"
        self.object_id = "dsafasdf"
        self.md5 = self._calculate_md5(original_name)
        self.isSimple = simple
        self.complex_obj_group = None
        self._status = RecordStatus.pending

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
                'original name': self.old_name,
                'new name': self.new_name,
                'project id': self.project_id,
                'md5': self.md5,
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

    def add_queue(self, file_name, object_id_prefix, start_number):
        if object_id_prefix in self.object_ids:
            # print("found one")
            pass
        else:
            self.object_ids[object_id_prefix] = start_number
        new_queue = NameRecord(file_name, os.path.join(self.new_path, self.generate_CAVPP_name(object_id_prefix, file_name)),len(self._queues))
        self._queues.append(new_queue)

    def remove_queue(self, file_name):
        temp_queues = []
        found_one = False
        for queue in self._queues:
            if queue.old_name == file_name:
                found_one = True
                if DEBUG:
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
        # self._do_the_renaming()

    def execute_rename_from_queue_by_record(self, record):
        return self._do_the_renaming(record)

    def _do_the_renaming(self, record):
        new_path = os.path.split(record.new_name)[0]
        if DEBUG:
            print("Copying {0} to {1}".format(record.old_name, new_path), end="")
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        record.set_Working()
        shutil.copy2(record.old_name, record.new_name)
        if filecmp.cmp(record.old_name, record.new_name):
            if DEBUG: print("  ...Success!")
            record.set_Done()
        else:
            sys.stderr.write("Failed!\n")
            raise IOError("File {0} does not match {1]".format(record.old_name, record.new_name))

        # print("Done")
        return record
    def clear_queues(self):
        self._queues = []

    def show_queues(self):
        for queue in self._queues:
            print(queue.get_dict())


    def generate_CAVPP_name(self, object_prefix, file_name):
        # path = os.path.split(file_name)[0]
        extension = os.path.splitext(file_name)[1]
        new_name = object_prefix + "_" + str(self.object_ids[object_prefix]).zfill(5) + extension
        # value = os.path.join(path, new_name)
        self.object_ids[object_prefix] += 1
        self.names_used.append(new_name)
        return new_name

    def swap_queues(self, queue_a, queue_b):
        pass

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class ReportFactory(object):
    '''
    This class interacts with the sqlite database for storing and retrieving the data for current and past renamings.
    This class is a singleton to avoid conflicts with writing and accessing the database.
    '''
    _instance = None
    _database = sqlite3.connect('data.db')

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ReportFactory, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        self.database = []
        self._database.row_factory = dict_factory

    def initize_database(self):
        if DEBUG:
            print("init the database")
        self._database.execute('DROP TABLE IF EXISTS report')
        self._database.execute('CREATE TABLE report('
                               'id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL,'
                               'source VARCHAR(255),'
                               'object_id VARCHAR(255),'
                               'project_id VARCHAR(255),'
                               'destination VARCHAR(255),'
                               'date_renamed DATE DEFAULT CURRENT_TIMESTAMP,'
                               'md5 VARCHAR(32))')

        self._database.commit()
        pass

    def add_record(self, record):
        if DEBUG:
            print("adding record")
        self._database.execute('INSERT INTO report(source, destination, md5, project_id, object_id) VALUES(?,?,?,?,?)',
                               (record.old_name, record.new_name, record.md5, record.project_id, record.object_id))
        self._database.commit()
        pass

    def show_current_records(self, object_id=None):
        if DEBUG:
            print("Getting record {0}.".format(object_id))
        queury = self._database.execute('SELECT * FROM report WHERE object_id is \"{0}\"'.format(object_id))
        for row in queury:
            print(row)
        pass

    def get_report(self, object_id=None):
        pass

    def close_database(self):
        self._database.close()
