#!/usr/local/bin/python
import mimetypes
import os
import subprocess
from xml.dom.minidom import parseString
import sys
import re

__author__ = 'California Audio Visual Preservation Project'

from PIL import Image, ExifTags
from .NonAVModel.Technical import Technical, CompressionModes


class MediaInfoException(Exception):
	def __init__(self, message):
		super(MediaInfoException, self).__init__(message)
		self.errors = message


def cleanup_bitdepth(bd):
	results = re.search("\d+(?=\sbit)", bd)

	return int(results.group(0))


def image_specs_extractor(file, technical_notes=None, media_info_path='mediainfo'):
	height = None
	width = None
	imageFormat = None  # todo: make more accurate
	colorspace = None  # todo: change to colorspace
	file_format = None
	compressionMode = None
	bitDepth = None
	imageFormat = None




	# standard Python
	file_format = mimetypes.types_map[os.path.splitext(file)[1]]

	# using pillow
	im = Image.open(file)
	height = im.size[1]
	width = im.size[0]
	compression = None
	compressionMode = None
	colorspace = im.mode
	bitDepth = None
	chroma_subsampling = None



	# using MediaInfo
	try:
		mediaInfoData = subprocess.check_output([media_info_path, '--Output=XML', file], universal_newlines=True)
	except FileNotFoundError as d:
		raise MediaInfoException("Error running mediainfo" + str(d))
	dom = parseString(mediaInfoData)
	for node in dom.getElementsByTagName("Color_space"):
		colorspace = node.firstChild.data

	for node in dom.getElementsByTagName("Chroma_subsampling"):
		chroma_subsampling = node.firstChild.data

	for node in dom.getElementsByTagName("Format"):
		imageFormat = node.firstChild.data

	for node in dom.getElementsByTagName("Compression_mode"):
		compression = node.firstChild.data
	if compression == "Lossy":
		compressionMode = CompressionModes.LOSSY
	elif compression == "Lossless":
		compressionMode = CompressionModes.LOSSLESS
	else:
		compressionMode = CompressionModes.UNKNOWN

	try:
		bitDepth = im.bits
	except:
		for node in dom.getElementsByTagName("Bit_depth"):
			bd = node.firstChild.data
			bitDepth = cleanup_bitdepth(bd)

	# print(dom.toprettyxml())

	xml = Technical(fileFormat=file_format,
					height=height,
					width=width,
					colorBitDepth=bitDepth)
	if imageFormat:
		xml.imageFormat = imageFormat
	xml.colorSpace = colorspace
	if chroma_subsampling:
		xml.chromaSubsampling = chroma_subsampling

	if compressionMode:
		xml.compressionMode = compressionMode
	if technical_notes:
		assert (isinstance(technical_notes, str))
		xml.additionalTechnicalNotes = technical_notes
	return xml


def main():
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
	if not os.path.exists(sys.argv[1]):
		sys.stderr.write("File doesn't exists.\n")
		exit(-1)
	else:
		print("\nTechnical metadata for: " + os.path.basename(sys.argv[1]) + "\n")
		print(image_specs_extractor(sys.argv[1]))


def test(test_folder):
	print("Running test")
	include_hidden = False
	accepted_formats = ['.tif', '.jpg']
	source_folder = test_folder
	if os.path.exists(source_folder):
		for root, dirs, files in os.walk(source_folder):
			for file in files:
				if not include_hidden:
					if file.startswith('.'):
						continue
				if not os.path.splitext(file)[1] in accepted_formats:
					continue
				current_file = os.path.join(root, file)
				print(current_file)
				try:
					xml = image_specs_extractor(current_file, technical_notes="This record is generated "
																			  "from a test using the files "
																			  "in {}.".format(source_folder))
					print(xml)
				except MediaInfoException as e:
					sys.stderr.write(str(e))
					quit(-1)
				# except Exception as e:
				# 	sys.stdout.flush()
				# 	sys.stderr.write("Error for " +current_file + ".\n")
				# 	sys.stderr.write(str(e))
	pass


if __name__ == '__main__':
	main()
