from enum import Enum

class RecordStatus(Enum):
    pending = 1
    working = 2
    done = 3

class ProgressStatus(Enum):
    idle = 1
    working = 2

class NameRecord(object):
    def __init__(self, original_name, new_name):
        self.queue = int
        self.old_name = str
        self.new_name = str
        self.project_id = str
        self.md5 = str
        self.isSimple = bool
        self.group = int
        self.status = RecordStatus

    def get_status(self):
        pass

    def set_Pending(self):
        pass

    def set_Done(self):
        pass

    def calculate_md5(self):
        pass


class RenameFactory(object):
    def __init__(self):
        self._queues = []
        self.current_progress = 0
        self.status = ProgressStatus
        self.project_id = str
        pass

    def __len__(self):
        return len(self._queues)

    def add_queue(self, file_name):
        pass

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
        pass

    def swap_queues(self, queue_a, queue_b):
        pass


class ReportFactory(object):
    _instance = None
    _database = None
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

    def generate_report(self):
        pass

