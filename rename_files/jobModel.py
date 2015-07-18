from collections import namedtuple
from enum import Enum
import os
import types
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, pyqtSignal

__author__ = 'California Audio Visual Preservation Project'


class DataRows(Enum):
    QUEUE_NUMBER = 0
    PROJECT_ID = 1
    SIMPLE_COMPLEX = 2
    PAGE_NUMBER = 3
    PAGE_SIDE = 4
    ORIGINAL_NAME = 5
    NEW_NAME = 6
    FILE_TYPE = 7
    INCLUDED_EXCLUDED = 8
    STATUS = 9

class FileType(Enum):
    ACCESS = "access"
    MASTER = "prsv"

class jobTreeModel(QAbstractItemModel):
    def __init__(self, root, parent=None):
        super(jobTreeModel, self).__init__(parent)
        assert(isinstance(root, jobTreeNode))
        self._root = root

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            parentNode = self._root
        else:
            parentNode = parent.internalPointer()
            # return parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        # if in_index.isValid():
        #     return in_index.internalPointer().columnCount()
        # return self._root.columnCount()
        return 10

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None
        node = index.internalPointer()



        if role == Qt.DisplayRole:
            # return "df"

            if index.column() == DataRows.QUEUE_NUMBER.value:
                if isinstance(node, ObjectNode):
                    return index.row() + 1
            else:
                return node.data(index.column())
        return None

    def parent(self, index):

        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._root:
            return QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)

    def getNode(self, index):
        assert(isinstance(index, QModelIndex))
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._root

    def add_object(self, object, parent=QModelIndex()):
        parentNode = self.getNode(parent)
        end = self.rowCount(parent)
        self.beginInsertRows(parent, end, end)
        success = parentNode.insertChild(self.rowCount(parent), object)
        self.endInsertRows()


    def insertRows(self, position, rows, parent=QModelIndex()):

        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = jobTreeNode("")
            success = parentNode.insertChild(position, childNode)


        self.endInsertRows()
        return success

    def removeRows(self, position, rows, parent=QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()
        return success


    def index(self, row, column, parent=QModelIndex()):
        # assert(isinstance(parent, QModelIndex))
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == DataRows.QUEUE_NUMBER.value:
                return "#"

            if section == DataRows.PAGE_NUMBER.value:
                return "Page Number"

            if section == DataRows.PAGE_SIDE.value:
                return "Page Side"

            if section == DataRows.PROJECT_ID.value:
                return "Project ID"

            if section == DataRows.FILE_TYPE.value:
                return "File Type"

            if section == DataRows.SIMPLE_COMPLEX.value:
                return "Simple/Complex"

            if section == DataRows.ORIGINAL_NAME.value:
                return "Original Name"

            if section == DataRows.NEW_NAME.value:
                return "New Name"

            if section == DataRows.INCLUDED_EXCLUDED.value:
                return "Included/Excluded"

            if section == DataRows.STATUS.value:
                return "Status"

    def get_active_jobs(self):
        return self._root.get_jobs()
    #     pass

    def update_object_numbers(self):
        jobTreeNode.total_active = 0
        self._root.update_id_numbers()



class jobTreeNode(object):
    total_active = 0
    pid_start_num = 0
    pid_prefix = ""
    oid_start_num = 0
    oid_marc = ""
    def __init__(self,
                 pid_prefix,
                 pid_start_num,
                 oid_marc,
                 oid_start_num,
                 simple_complex=None,
                 original_name=None,
                 new_name=None,
                 included_excluded=None,
                 status=None,
                 parent=None):
        jobTreeNode.pid_start_num = pid_start_num
        jobTreeNode.oid_start_num = oid_start_num
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

        self._data = types.SimpleNamespace(project_id_prefix=pid_prefix,
                                           project_id_number=None,
                                           object_id_marc=oid_marc,
                                           object_id_number=None,
                                           simple_complex=simple_complex,
                                           original_name=original_name,
                                           page_number=None,
                                           page_side=None,
                                           new_name=new_name,
                                           file_type=None,
                                           included=included_excluded,
                                           needs_conversion=None,
                                           status=status)

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):

        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):

        if position < 0 or position > len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None
        return True

    def data(self, column):
        if column == DataRows.PROJECT_ID.value:
            try:
                return self._data.project_id_prefix + "_" + str(self._data.project_id_number).zfill(6)
            except TypeError as e:
                print(column, str(type(self)), str(e))
                exit(1)

        if column == DataRows.SIMPLE_COMPLEX.value:
            if isinstance(self, ObjectNode):
                if len(self._children) == 0:
                    return "Empty"
                if len(self._children) > 1 or len(self._children[0]._children) > 1:
                    return "Complex"
                else:
                    return "Simple"

        if column == DataRows.ORIGINAL_NAME.value:
            return self._data.original_name

        if column == DataRows.NEW_NAME.value:
            if isinstance(self, NewFileNode):
                if self._data.included:
                    new_name = self._data.object_id_marc + "_" + str(self._data.object_id_number).zfill(6)
                    # print(self._parent._parent.childCount())
                    if self._parent._parent.childCount() > 1:
                        new_name += "_"
                        new_name += str(self._data.page_number).zfill(2)
                    if self._data.page_side:
                        new_name += "_"
                        new_name += str(self._data.page_side)
                    new_name += "_"
                    new_name += str(self._data.file_type.value)
                    if self._data.needs_conversion:
                        new_name += ".jpg"
                    else:
                        new_name += os.path.splitext(self._data.original_name)[1]
                    # print(new_name)
                    self._data.new_name = new_name
                    return self._data.new_name

        if column == DataRows.INCLUDED_EXCLUDED.value:
            if not self._data.included is None:
                if self._data.included:
                    return "Included"
                else:
                    return "Excluded"

        if column == DataRows.STATUS.value:
            return self._data.status

        if column == DataRows.PAGE_NUMBER.value:
            if isinstance(self, ObjectNode):
                total_pages = len(self._children)
                if total_pages == 1:
                    return "Single page"
                else:
                    return str(total_pages) + " pages"
            return self._data.page_number

        if column == DataRows.PAGE_SIDE.value:
            if isinstance(self, PageNode):
                total_sides = len(self._children)
                if total_sides == 1:
                    return "Single sided"
                elif total_sides == 2:
                    return "Double sided"
                else:
                    raise Exception("There should be only 1 or 2 sides")
            return self._data.page_side

        if column == DataRows.FILE_TYPE.value:
            return self._data.file_type

        # if column == dataRows.QUEUE_NUMBER.value:
        #     return 0


        # return self._data

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def type_info(self):
        return "NODE"

    def get_data(self):
        return self._data

    def is_included(self):
        return self._data.included

    def set_included(self, value):
        assert(isinstance(value, bool))
        if value:
            self._data.included = value
            for child in self._children:
                child.set_included(True)
        else:
            for child in self._children:
                child.set_included(False)

    # def children(self):
    #     return self._children

    def log(self, tabLevel=1):
        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "/-----" + self.type_info() + "\n"

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1

        return output

    def __repr__(self):
        return self.log()

    def name(self):
        return self._data

    @property
    def total_active_included(self):
        total = 0
        for child in self._children:
            if child.get_data().included:
                total += 1
        return total

    def get_jobs(self):
        if not isinstance(self, NewFileNode):


            jobs = []
            for child in self._children:
                jobs += child.get_jobs()

            return jobs

    def update_id_numbers(self):
        for child in self._children:
            child.update_id_numbers()
        pass

class ObjectNode(jobTreeNode):
    def __init__(self, pid_prefix, oid_marc, parent=None, included=True):

        self._children = []
        self._parent = parent
        self._data = None
        self.pid_prefix = pid_prefix
        self.oid_marc = oid_marc
        self.included = included


        if parent is not None:
            parent.addChild(self)
        if included:
            self._data = types.SimpleNamespace(project_id_prefix=jobTreeNode.pid_prefix,
                                               project_id_number=jobTreeNode.oid_start_num + jobTreeNode.total_active,
                                               object_id_marc=jobTreeNode.oid_marc,
                                               object_id_number=jobTreeNode.pid_start_num + jobTreeNode.total_active,
                                               simple_complex=None,
                                               page_number=None,
                                               page_side=None,
                                               original_name=None,
                                               new_name=None,
                                               file_type=None,
                                               included=self.included,
                                               needs_conversion=None,
                                               status=None)
            jobTreeNode.total_active += 1

        self.update_id_numbers()

    def update_id_numbers(self):
        if self._data.included:
            self._data.project_id_number = jobTreeNode.pid_start_num + jobTreeNode.total_active
            self._data.object_id_number = jobTreeNode.oid_start_num + jobTreeNode.total_active
            jobTreeNode.total_active += 1
            self._data.project_id_prefix = jobTreeNode.pid_prefix
            self._data.object_id_marc = jobTreeNode.oid_marc
        else:
            self._data.project_id_number = None
            self._data.object_id_number = None
        for child in self._children:
            child.update_id_numbers()

    def type_info(self):
        return "ObjectNode"

    def set_included(self, value):
        assert(isinstance(value, bool))
        self._data.included = value
        # if value:
        #     self.parent().set_included(True)
        #     for child in self._children:
        #         child.set_included(True)
        if not value:
            for child in self._children:
                child.set_included(False)



class PageNode(jobTreeNode):
    def __init__(self, page_number, parent, included=True):
        if not isinstance(page_number, int):
            raise TypeError("Expected int, recieved " + str(type(page_number)))

        self._children = []
        self._parent = parent
        self.page_numnber =page_number
        self.included = included
        self._data = types.SimpleNamespace(project_id_prefix=None,
                                   project_id_number=None,
                                   object_id_marc=None,
                                   object_id_number=None,
                                   simple_complex=None,
                                   page_number=self.page_numnber,
                                   page_side=None,
                                   original_name=None,
                                   new_name=None,
                                   file_type=None,
                                   included=self.included,
                                   needs_conversion=None,
                                   status=None)

        if parent is not None:
            parent.addChild(self)

        self.update_id_numbers()

    def update_id_numbers(self):
        self._data.project_id_prefix = self._parent.get_data().project_id_prefix
        self._data.project_id_number = self._parent.get_data().project_id_number
        self._data.object_id_marc = self._parent.get_data().object_id_marc
        self._data.object_id_number = self._parent.get_data().object_id_number
        for child in self._children:
            child.update_id_numbers()

    def type_info(self):
        return "PageNode"

    def set_included(self, value):
        assert(isinstance(value, bool))
        self._data.included = value
        if value:
            self.parent().set_included(True)
            # for child in self._children:
            #     child.set_included(True)

        else:
            for child in self._children:
                child.set_included(False)



class PageSideNode(jobTreeNode):
    def __init__(self, page_side, parent, original_filename, included=True):

        if page_side is None:
            self._data.page_side = ""
        self._children = []
        self._parent = parent

        self._data = types.SimpleNamespace(project_id_prefix=None,
                                           project_id_number=None,
                                           object_id_marc=None,
                                           object_id_number=None,
                                           simple_complex=None,
                                           page_number=None,
                                           page_side=page_side,
                                           original_name=original_filename,
                                           new_name=None,
                                           file_type=None,
                                           included=included,
                                           needs_conversion=None,
                                           status=None)
        if parent is not None:
            parent.addChild(self)

            self.update_id_numbers()

    def update_id_numbers(self):
        self._data.project_id_prefix = self._parent.get_data().project_id_prefix
        self._data.project_id_number = self._parent.get_data().project_id_number
        self._data.object_id_marc = self._parent.get_data().object_id_marc
        self._data.object_id_number = self._parent.get_data().object_id_number
        self._data.page_number = self._parent.get_data().page_number
        for child in self._children:
            child.update_id_numbers()

    def type_info(self):
        return "PageSideNode"

    def set_included(self, value):
        assert(isinstance(value, bool))
        self._data.included = value
        if value:
            self.parent().set_included(True)
            # for child in self._children:
            #     child.set_included(True)
        else:
            for child in self._children:
                child.set_included(False)

    def get_jobs(self):
            jobs = []
            for child in self._children:
                jobs.append(child.get_jobs())

            return jobs



class NewFileNode(jobTreeNode):
    def __init__(self, file_type, convert, parent, included=True):
        assert(isinstance(file_type, FileType))
        self._children = []
        self._parent = parent
        self._data = types.SimpleNamespace(project_id_prefix=None,
                                           project_id_number=None,
                                           object_id_marc=None,
                                           object_id_number=None,
                                           simple_complex=None,
                                           page_number=None,
                                           page_side=None,
                                           original_name=None,
                                           new_name=None,
                                           file_type=file_type,
                                           included=included,
                                           needs_conversion=convert,
                                           status=None)
        if parent is not None:
            parent.addChild(self)
            self.update_id_numbers()

    def update_id_numbers(self):
        self._data.project_id_prefix = self._parent.get_data().project_id_prefix
        self._data.project_id_number = self._parent.get_data().project_id_number
        self._data.object_id_marc = self._parent.get_data().object_id_marc
        self._data.object_id_number = self._parent.get_data().object_id_number
        self._data.page_number = self._parent.get_data().page_number
        self._data.original_name = self._parent.get_data().original_name

    def set_included(self, value):
        assert(isinstance(value, bool))
        self._data.included = value
        if value:
            self.parent().set_included(True)

    def get_jobs(self):
        job_packet = namedtuple('job_packet', ['old_name', 'new_name', 'object_id', 'copy_file', 'convert'])
        if self._data.included:
            packet = job_packet(old_name=self.data(DataRows.ORIGINAL_NAME.value),
                                new_name=self.data(DataRows.NEW_NAME.value),
                                object_id=self._data.project_id_prefix + "_" + str(self._data.project_id_number).zfill(6),
                                copy_file=True,
                                convert=self._data.needs_conversion)
            return packet

    def type_info(self):
        return "NewFileNodes"