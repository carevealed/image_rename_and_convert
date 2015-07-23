import os
from rename_files.gui_datafiles.complex_gui import Ui_ComplexForm
from PyQt4.QtCore import *
from PyQt4.QtGui import *
class ComplexDialog(QDialog, Ui_ComplexForm):

	def __init__(self, parent=None):
		super(ComplexDialog, self).__init__(parent)
		self.setupUi(self)
		self.file_model = QFileSystemModel()
		self.bundle_model = QStringListModel()
		bundle_lists = []
		self.bundle_model.setStringList(bundle_lists)

		root = self.file_model.setRootPath("/Volumes")



		self.columnView_files.setModel(self.file_model)
		self.columnView_files.setRootIndex(root)
		self.listView_files.setModel(self.bundle_model)

		# connect the buttons
		self.pushButton_add_file.clicked.connect(self._add_to_bundle)
		self.pushButton_remove_file.clicked.connect(self._remove_from_bundle)
		self.pushButton_cancle.clicked.connect(self.close_window)
		self.pushButton_add_object.clicked.connect(self.return_bundle)



	def _add_to_bundle(self):
		selection = self.columnView_files.selectedIndexes()
		files = self.bundle_model.stringList()
		model = self.columnView_files.model()
		for index in selection:
			# path = os.path.join()
			if model.isDir(index):
				continue
			newfile = model.filePath(index)
			files.append(newfile)
		self.bundle_model.setStringList(files)
			# self.bundle_model.inser

	def _remove_from_bundle(self):
		selection = self.listView_files.selectedIndexes()
		model = self.listView_files.model()
		for index in selection:
			row = index.row()
			model.removeRows(row, 1)

	def return_bundle(self):
		self.close_window()

	@property
	def bundle(self):
		return self.bundle_model.stringList()

	def close_window(self):
		self.close()
