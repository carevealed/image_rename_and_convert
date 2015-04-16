import os
import sys
import rename_files.renaming_model

__author__ = 'California Audio Visual Preservation Project'
debug = True

def main(source):
    builder = rename_files.renaming_model.RenameFactory()
    if debug:
        print(source)

    for root, subdirs, files in os.walk(source):
        for file in files:
            if os.path.splitext(file)[1] == '.tif':
                newfile = os.path.join(root, file)
                builder.add_queue(newfile, "caps", 1)

    reporter = rename_files.renaming_model.ReportFactory()
    reporter.initize_database()
    for i in builder:
        record = builder.execute_rename_from_queue_by_record(i)
        reporter.add_record(record)

    # print(type(reporter))
    reporter.show_current_records(object_id="dsafasdf")
    reporter.close_database()
    # for queue in builder.queues:
    #     print(queue)


if __name__ == "__main__":
    if debug:
        sys.stderr.write("Don't forget to get rid of this!!!\n")
        main("/Volumes/CAVPPTestDrive/DPLA0003/Images/_Anaheim/")
    sys.stderr.write("Not a main entry point\n")
    sys.stdout.flush()
