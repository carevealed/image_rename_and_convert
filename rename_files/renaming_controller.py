import hashlib

__author__ = 'California Audio Visual Preservation Project'

import os
import csv
def generate_report(reporter, report_file_name):
    records = reporter.get_last_job()
    if os.path.exists(report_file_name):
        raise FileExistsError
    with open(report_file_name, 'w') as f:
        csv_file = csv.writer(f)
        csv_file.writerow(["#", "Project ID", "Object ID", "Original Name:", "MD5 of original file", "New Name:", "MD5 of new file", "Internet Archive URL" ])
        # f.write(
        #     "=============================================================================================================================================\n")
        # for index, record in enumerate(records):
        #     # print(record)
        #     project_id = (record['project_id_prefix'] + str(record['project_id_number']).zfill(6))
        #     object_id = (record['object_id_prefix'] + "_" + str(record['object_id_number']).zfill(6))
        #     original_name = record['file_name']
        #     original_md5 = _calculate_md5(original_name)
        #     new_name = os.path.basename(record['destination'])
        #     new_md5 = _calculate_md5(record['destination'])
        #     csv_file.writerow([index + 1, project_id, object_id, original_name, original_md5, new_name, new_md5, record['ia_url']])




def _calculate_md5(file_name):
    BUFFER = 8192
    md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(BUFFER), b''):
            md5.update(chunk)
    return md5.hexdigest()