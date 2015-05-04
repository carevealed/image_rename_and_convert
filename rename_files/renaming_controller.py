__author__ = 'California Audio Visual Preservation Project'

import os
import csv
def generate_report(reporter, report_file_name):
    records = reporter.get_last_job()
    if os.path.exists(report_file_name):
        raise FileExistsError
    with open(report_file_name, 'w') as f:
        csv_file = csv.writer(f)
        csv_file.writerow(["#", "Project ID", "Object ID", "Original Name:", "New Name:", "MD5"])
        # f.write(
        #     "=============================================================================================================================================\n")
        for index, record in enumerate(records):
            # print(record)
            project_id = (record['project_id_prefix'] + str(record['project_id_number']).zfill(6))
            object_id = (record['object_id_prefix'] + "_" + str(record['object_id_number']).zfill(5))
            csv_file.writerow([index + 1, project_id, object_id, record['source'], os.path.basename(record['destination']), record['md5']])