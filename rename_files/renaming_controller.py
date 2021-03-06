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
        record_number = 0
        csv_file.writerow(["#", "Object ID", "Original Name:", "MD5 of original file", "Master Name:", "MD5 of master file", "Access File Name", "Access File MD5", "Internet Archive URL", "Message", "Technical Notes"])
        for record in records:
            print(record)
            if record['type'] == "Master" or record['type'] == "Preservation Master":
                # project_id = record['project_id_prefix'] + "_" + str(record['project_id_number']).zfill(6)
                object_id = record['object_id_prefix'] + "_" + str(record['object_id_number']).zfill(6)
                original_name = record['original_name']
                original_md5 = record['original_md5']
                master_name = record['new_name']
                master_md5 = record['new_md5']


                # find an access file that matches the original source as the master file
                found_access = False
                for candidate in records:
                    if candidate['original_name'] == record['original_name'] and (candidate['type'] == "Access" or candidate['type'] == "Access Copy"):
                        access_name = candidate['new_name']
                        access_md5 = candidate['new_md5']
                        message = "Original file was named {}, which was renamed to {}. and an access file was produced from it " \
                                  "and was named {}.".format(os.path.basename(original_name), os.path.basename(master_name),
                                                             os.path.basename(access_name))
                        notes = candidate['notes']
                        csv_file.writerow([record_number + 1, object_id, original_name, original_md5, master_name, master_md5, access_name, access_md5, record['ia_url'], message, notes])
                        found_access = True
                        record_number += 1
                        break

                # if found no access, it should just print it that no access files was produced
                if not found_access:
                    notes = record['notes']
                    message = "Original file was named {}, which was renamed to {}.".format(os.path.basename(original_name), os.path.basename(master_name))
                    csv_file.writerow([record_number + 1, object_id, original_name, original_md5, master_name, master_md5, "", "", record['ia_url'], message, notes])
                    record_number += 1




        # for index, record in enumerate(records):
        # #
        #     # print(record)
        #     project_id = (record['project_id_prefix'] + "_" + str(record['project_id_number']).zfill(6))
        #     object_id = (record['object_id_prefix'] + "_" + str(record['object_id_number']).zfill(6))
        #     original_name = record['original_name']
        #     original_md5 = record['original_md5']
        #     new_name = os.path.basename(record['new_name'])
        #     new_md5 = record['new_md5']
        #
        #
        #
        #     csv_file.writerow([index + 1, project_id, object_id, original_name, original_md5, new_name, new_md5, record['ia_url']])

