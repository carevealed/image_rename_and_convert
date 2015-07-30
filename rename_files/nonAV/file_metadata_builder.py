#!/usr/local/bin/python
__author__ = 'California Audio Visual Preservation Project'
import hashlib
import os
import sys
from os.path import getsize


from .imageSpecsExtractor import image_specs_extractor
from .NonAVModel.Instantiation import Instantiation
# from .NonAVModel import errors_report


def create_md5(file_name):

	BUFFER = 8192
	md5 = hashlib.md5()
	with open(file_name, 'rb') as f:
		for chunk in iter(lambda: f.read(BUFFER), b''):
			md5.update(chunk)
	return md5.hexdigest()


def get_human_filesize(filename):
	num = int(getsize(filename))
	file_size = 0
	unit = None
	for x in ['bytes', 'kilobytes', 'megabytes', 'gigabytes', 'terabytes']:
		if num < 1024.0:
			file_size = num
			unit = x
			break
		num /= 1024.0
	# file_size = 232
	#
	# unit = "kilobytes"
	assert file_size != 0
	assert unit is not None
	return file_size, unit




def file_metadata_builder(filename,
						  generation,
						  derived_from,
						  checksum=None,
						  checksum_type=None,
						  processing_notes=None):

	instance = Instantiation(os.path.basename(filename))
	# instance.report_errors = errors_report.WARNING #todo remove this line when done building

	instance.generation = generation
	instance.derivedFrom = derived_from

	if checksum:
		instance.checksum = checksum
		instance.checksumType = checksum_type
	else:
		instance.checksum = create_md5(filename)
		instance.checksumType = "md5"

	file_size, file_size_unit = get_human_filesize(filename)
	instance.fileSize = str("%.2f" % file_size)
	instance.fileSizeUnit = file_size_unit

	technical = image_specs_extractor(filename)
	technical.additionalTechnicalNotes = processing_notes
	instance.technical = technical.xml

	report = instance.check_required_data()
	if report.valid:
		return instance
	else:
		sys.stdout.flush()
		if len(report.missing_fields) > 0:
			sys.stderr.write("Missing fields:\n")
			for field in report.missing_fields:
				sys.stderr.write(field + "\n")
			print("")
		if len(report.missing_attributes) > 0:
			sys.stderr.write("Missing Attributes:\n")
			for attribute in report.missing_attributes:
				sys.stderr.write(attribute + "\n")
	pass


def test(source_folder):
	include_hidden = False
	valid_file_exensions = ['.tif', '.jpg']
	if os.path.exists(source_folder):
		for root, dirs, files in os.walk(source_folder):
			for file in files:
				if not include_hidden:
					if file.startswith('.'):
						continue
				if not os.path.splitext(file)[1] in valid_file_exensions:
					continue
				test_file = os.path.join(root, file)
				print(test_file)
				print(file_metadata_builder(test_file, generation="Unknown", derived_from="Unknown"))

def main():
	print("hello")
	if len(sys.argv) < 2:
		sys.stderr.write("Needs at least one argument.\n")
		exit(-1)

	if len(sys.argv) == 3:
		if sys.argv[1] == "-t":
			if not os.path.isdir(sys.argv[2]):
				sys.stderr.write("Not a directory.\n")
				quit(-1)
			if not os.path.exists(sys.argv[2]):
				sys.stderr.write("Directory does not exist.\n")
				quit(-1)

			print("Running test mode")
			test(sys.argv[2])
			print("Test finished.")
			exit(0)
		else:
			sys.stderr.write("Not a valid option.\n")
			quit(-1)
	if not os.path.isfile(sys.argv[1]):
		sys.stderr.write("Not a file.\n")
		exit(-1)

	if not os.path.exists(sys.argv[1]):
		sys.stderr.write("File doesn't exists.\n")
		exit(-1)
	else:
		print("\nInstantiation and Technical metadata for: " + os.path.basename(sys.argv[1]) + "\n")
		print(file_metadata_builder(sys.argv[1], generation="Unknown", derived_from="Unknown"))



if __name__ == '__main__':
	main()