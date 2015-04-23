from enum import Enum, unique
import os
import sys
import rename_files.renaming_model



__author__ = 'California Audio Visual Preservation Project'

@unique
class running_mode(Enum):
    NORMAL = 0
    DEBUG = 1
    BUILD = 2
MODE = running_mode.DEBUG


def start_cli(source=None,
              obj_id_prefix=None,
              obj_id_start_num=None,
              proj_id_prefix=None,
              proj_id_start_num=None,
              output_path=None,
              user=None):

    if obj_id_prefix:
        object_id_prefix = obj_id_prefix
    else:
        object_id_prefix = None

    if obj_id_start_num:
        first_object_id = obj_id_start_num
    else:
        first_object_id = 0

    if proj_id_prefix:
        proj_id_prefix = proj_id_prefix
    else:
        proj_id_prefix = "CAPS"

    if proj_id_start_num:
        first_project_id = proj_id_start_num
    else:
        first_project_id = 0

    if MODE == running_mode.BUILD:
        first_object_id = 30
        first_project_id = 400
        object_id_prefix = "cusb"
        output_path = "/Volumes/CAVPPTestDrive/test/"


    builder = rename_files.renaming_model.RenameFactory()
    if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
        print(source)

    tiffs = []
    jpegs = []
# get all the files that match either tif or jpg

    for root, subdirs, files in os.walk(source):
        for index, file in enumerate(files):
            if os.path.splitext(file)[1] == '.tif':
                newfile = os.path.join(root, file)
                tiffs.append(newfile)
            if os.path.splitext(file)[1] == '.jpg':
                newfile = os.path.join(root, file)
                jpegs.append(newfile)

# go through all the jpegs found. if there is a tiff file with the same name,
# add that file the queue instead of the jpeg, otherwise, add the jpeg
    for index, jpeg in enumerate(jpegs):
        files_per_record = rename_files.renaming_model.record_bundle(object_id_prefix, index+first_object_id, path=output_path)
        jpeg_name = os.path.splitext(os.path.basename(jpeg))[0]
        found_tiff = False
        # print(jpeg_name)
        for tiff in tiffs:
            if jpeg_name == os.path.splitext(os.path.basename(tiff))[0]:
                # print("Found one")
                files_per_record.add_file(tiff)
                found_tiff = True
                break
        if not found_tiff:
            files_per_record.add_file(jpeg)
        builder.add_queue(files_per_record,
                          obj_id_prefix=object_id_prefix,
                          obj_id_num=index + first_object_id,
                          proj_id_prefix=proj_id_prefix,
                          proj_id_num=index + first_project_id)


    reporter = rename_files.renaming_model.ReportFactory(username=user)
    reporter.initize_database()
    for i in builder:
        record = builder.execute_rename_from_queue_by_record(i)
        reporter.add_record(record)

    # print(type(reporter))
    reporter.show_current_records(object_id=object_id_prefix)
    reporter.close_database()
    # for queue in builder.queues:
    #     print(queue)


if __name__ == "__main__":
    # if MODE == running_mode.BUILD:
    #     sys.stderr.write("Don't forget to get rid of this!!!\n")
    #     start_cli("/Volumes/CAVPPTestDrive/DPLA0003/Images/_Anaheim/")
    sys.stderr.write("Not a main entry point\n")
    sys.stdout.flush()
