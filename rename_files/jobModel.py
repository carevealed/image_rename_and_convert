from enum import Enum
import types
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt

__author__ = 'California Audio Visual Preservation Project'


class dataRows(Enum):
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

class jobTreeModel(QAbstractItemModel):
    total_queues = 0
    def __init__(self, root, parent=None):
        super(jobTreeModel, self).__init__(parent)
        assert(isinstance(root, jobTreeNode))
        self._root = root

    def rowCount(self, parent):
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

    def data(self, index, role):

        if not index.isValid():
            return None
        node = index.internalPointer()



        if role == Qt.DisplayRole:
            # return "df"

            if index.column() == dataRows.QUEUE_NUMBER.value:
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



    def index(self, row, column, parent):
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
            if section == dataRows.QUEUE_NUMBER.value:
                return "#"

            if section == dataRows.PAGE_NUMBER.value:
                return "Page Number"

            if section == dataRows.PAGE_SIDE.value:
                return "Page Side"

            if section == dataRows.PROJECT_ID.value:
                return "Project ID"

            if section == dataRows.FILE_TYPE.value:
                return "File Type"

            if section == dataRows.SIMPLE_COMPLEX.value:
                return "Simple/Complex"

            if section == dataRows.ORIGINAL_NAME.value:
                return "Original Name"

            if section == dataRows.NEW_NAME.value:
                return "New Name"

            if section == dataRows.INCLUDED_EXCLUDED.value:
                return "Included/Excluded"

            if section == dataRows.STATUS.value:
                return "Status"


class jobTreeNode(object):
    def __init__(self,
                 project_ID,
                 simple_complex=None,
                 original_name=None,
                 new_name=None,
                 included_excluded=None,
                 status=None,
                 parent=None):

        self._data = types.SimpleNamespace(project_ID=project_ID,
                                           simple_complex=simple_complex,
                                           original_name=original_name,
                                           page_number=None,
                                           page_side=None,
                                           new_name=new_name,
                                           file_type=None,
                                           included=included_excluded,
                                           status=status)
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

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
        if column == dataRows.PROJECT_ID.value:
            return self._data.project_ID

        if column == dataRows.SIMPLE_COMPLEX.value:
            if isinstance(self, ObjectNode):
                if len(self._children) == 0:
                    return "Empty"
                if len(self._children) > 1 or len(self._children[0]._children) > 1:
                    return "Complex"
                else:
                    return "Simple"

        if column == dataRows.ORIGINAL_NAME.value:
            return self._data.original_name

        if column == dataRows.NEW_NAME.value:
            return self._data.new_name

        if column == dataRows.INCLUDED_EXCLUDED.value:
            if not self._data.included is None:
                if self._data.included:
                    return "Included"
                else:
                    return "Excluded"

        if column == dataRows.STATUS.value:
            return self._data.status

        if column == dataRows.PAGE_NUMBER.value:
            if isinstance(self, ObjectNode):
                total_pages = len(self._children)
                if total_pages == 1:
                    return "Single page"
                else:
                    return str(total_pages) + " pages"
            return self._data.page_number

        if column == dataRows.PAGE_SIDE.value:
            if isinstance(self, PageNode):
                total_sides = len(self._children)
                if total_sides == 1:
                    return "Single sided"
                elif total_sides == 2:
                    return "Double sided"
                else:
                    raise Exception("There should be only 1 or 2 sides")
            return self._data.page_side

        if column == dataRows.FILE_TYPE.value:
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

    def log(self, tabLevel=1):
        output = ""
        tabLevel += 1

        for i in range(tabLevel):
            output += "\t"

        output += "/-----" + self._data + "\n"

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1

        return output



    def __repr__(self):
        return self.log()

    def name(self):
        return self._data


class ObjectNode(jobTreeNode):
    def __init__(self, project_id, parent=None, included=True):
        self._data = types.SimpleNamespace(project_ID=project_id,
                                           simple_complex=None,
                                           page_number=None,
                                           page_side=None,
                                           original_name=None,
                                           new_name=None,
                                           file_type=None,
                                           included=included,
                                           status=None)
        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    def type_info(self):
        return "ObjectNode"


class PageNode(jobTreeNode):
    def __init__(self, page_number, parent, included=True):
        if not isinstance(page_number, int):
            raise TypeError("Expected int, recieved " + str(type(page_number)))
        self._data = types.SimpleNamespace(project_ID=None,
                                           simple_complex=None,
                                           page_number=page_number,
                                           page_side=None,
                                           original_name=None,
                                           new_name=None,
                                           file_type=None,
                                           included=included,
                                           status=None)

        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)

    def type_info(self):
        return "PageNode"


class PageSideNode(jobTreeNode):
    def __init__(self, page_side, parent, original_filename, included=True):
        self._data = types.SimpleNamespace(project_ID=None,
                                           simple_complex=None,
                                           page_number=None,
                                           page_side=page_side,
                                           original_name=original_filename,
                                           new_name=None,
                                           file_type=None,
                                           included=included,
                                           status=None)

        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)


    def type_info(self):
        return "PageSideNode"

class NewFileNodes(jobTreeNode):
    def __init__(self, new_name, type, parent, included=True):
        self._data = types.SimpleNamespace(project_ID=None,
                                           simple_complex=None,
                                           page_number=None,
                                           page_side=None,
                                           original_name=None,
                                           new_name=new_name,
                                           file_type=type,
                                           included=included,
                                           status=None)

        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)


    def type_info(self):
        return "NewFileNodes"