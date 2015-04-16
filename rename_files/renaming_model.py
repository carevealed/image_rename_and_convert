from enum import Enum , unique
import sqlite3

@unique
class RecordStatus(Enum):
    pending = 0
    working = 1
    done = 2


class NameRecord(object):
    def __init__(self, original_name, new_name):
        self.queue = int
        self.old_name = str
        self.new_name = str
        self.project_id = str
        self.md5 = str
        self.isSimple = bool
        self.complex_obj_group = int
        self.status = RecordStatus.pending

    def get_status(self):
        pass

    def set_Pending(self):
        pass

    def set_Done(self):
        pass

    def _calculate_md5(self):
        pass

@unique
class ProgressStatus(Enum):
    idle = 0
    working = 1

class RenameFactory(object):
    def __init__(self, project_id=None):
        self._queues = []
        self.names_used = []
        self.current_progress = 0
        self.status = ProgressStatus.idle
        self.project_id = str
        if project_id:
            self.project_id = project_id
        pass

    def __len__(self):
        return len(self._queues)

    def add_queue(self, file_name):
        new_queue = NameRecord(file_name, self.generate_CAVPP_name())
        if self.current_progress == 0:
            self.current_progress = 1
        self._queues.append(new_queue)

    def remove_queue(self, file_name):
        pass

    def make_complex(self, *args):
        pass

    def make_simple(self, *args):
        pass

    def execute_rename_from_queue(self, int):
        pass

    def execute_rename_next(self):
        pass

    def clear_queues(self):
        self._queues = []

    def show_queus(self):
        for queue in self._queues:
            print(queue)

    def generate_CAVPP_name(self):
        yield "sadfadsfads"

    def swap_queues(self, queue_a, queue_b):
        pass

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
            
    def __init__(self):
        self.database = []

    def initize_database(self):
        pass

    def add_record(self, record):
        pass

    def show_current_records(self, object_id=None):
        pass

    def get_report(self, object_id=None):
        pass

    def close_database(self):
        self._database.close()
