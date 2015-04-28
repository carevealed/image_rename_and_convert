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
MODE = running_mode.NORMAL


def is_reponse_valid(response):
    if response.lower() == "q" or response.lower() == "quit":
        print("Quiting")
        quit()
    return True


def is_valid_folder_name(response):
    # TODO: build a function to check if a the folder name is accurate
    return True
    pass



# FIXME: Valid string isn't working at all
def valid_str(key, keyname, kwargs):
    valid = False
    while not valid:
        if key in kwargs:
            if kwargs[key]:
                if isinstance(kwargs[key], str):
                    print("{} {}".format("{}:".format(keyname), "[{}]".format(kwargs[key])), end="")
                else:
                    print("{}".format(keyname), end="")
                response = input(" :").strip()
                if response:
                    if not isinstance(response, str):
                        sys.stderr.write("This data must be made up of letters.\n")
                        continue
                    if is_reponse_valid(response):
                        # kwargs[key] = response
                        valid = True
                        return response
                    else:
                        valid = False
                        continue
                else:
                    valid = True
                    return kwargs[key]

            valid = True
        else:
            print("{}".format(keyname), end="")
            response = input(" :").strip()
            if response:
                if not isinstance(response, str):
                    sys.stderr.write("This data must be made up of letters.\n")
                    continue
                if is_reponse_valid(response):
                    # kwargs[key] = response
                    valid = True
                    return response
                else:
                    valid = False
                    continue
            else:
                valid = False
                continue

def valid_int(key, keyname, kwargs):
    valid = False
    while not valid:
        if key in kwargs:
            if kwargs[key]:
                int(kwargs[key])
                print("{}: {}".format(keyname, "[{}]".format(kwargs[key])), end="")
                response = input(" :").strip()
                if response:
                    try:
                        int(response)
                    except ValueError:
                        sys.stderr.write("This data must be an integer number.\n")
                        continue
                    if is_reponse_valid(response):
                        # kwargs[key] = response
                        valid = True
                        return response
                    else:
                        valid = False
                        sys.stderr.write("This information is required. Error code variation: 1.\n")
                        continue
                else:
                    valid = True
                    return kwargs[key]

        print("{}".format(keyname), end="")
        response = input(" :").strip()
        if response:
            try:
                int(response)
            except ValueError:
                sys.stderr.write("This data must be an integer number.\n")
                continue
            if is_reponse_valid(response):
                # kwargs[key] = response
                valid = True
                return response
            else:
                valid = False
                sys.stderr.write("This information is required. Error code variation: 2.\n")
                continue
        else:
            valid = False
            sys.stderr.write("This information is required. Error code variation: 3.\n")
            continue



def update_information(kwargs):

    print("This script needs some information before it can run. Please enter or update the following information. \n"
          "If a value is already suggested, you can confirm by pressing return without entering any values. \n"
          "To quit at any point, type \"q\" or \"quit\" and press enter. ")
    if MODE == running_mode.DEBUG:
        print("\n***** DEBUG INFORMATION ***** ")
        for keys,values in kwargs.items():
            print("{:<20}:{:<20}".format(keys, str(values)))
        print("***** DEBUG INFORMATION *****\n\n")


    valid = False
    while not valid:
        if 'source' in kwargs:
            print("Source: [{}]".format(kwargs['source']), end="")
            valid = True
        else:
            print("Source ", end="")
        response = input(" :").strip()
        if response:
            if is_reponse_valid(response):
                if os.path.isdir(response):
                    kwargs['source'] = response
                    valid = True
                    print("Directory found")
                else:
                    print("Directory not found. Please try again or type [q] or [quit] and press enter.")
                    valid = False
    valid = False
    while not valid:
        if 'destination' in kwargs:
            print("Destination: [{}]".format(kwargs['destination']), end="")
            valid = True
        else:
            print("Destination ", end="")
        response = input(" :").strip()
        if response:
            if is_reponse_valid(response):
                if is_valid_folder_name(response):
                    if not os.path.isdir(response):
                        key = input("That folder does not exist. Do wish to create it? [Y]").lower()
                        if not key == "yes" and not key == "y" and not key == "":
                            valid = False
                            continue
                        else:
                            print("Okay\n")
                            kwargs['destination'] = response
                            valid = True
                else:
                    print("Directory not found. Please try again or type [q] or [quit] and press enter.")
                    valid = False
    kwargs['object_id_prefix'] = valid_str('object_id_prefix', "Object ID MARC code", kwargs)
    kwargs['object_id_start'] = valid_int('object_id_start', 'Object ID starting number', kwargs)
    kwargs['project_id_prefix'] = valid_str('project_id_prefix', "Project ID MARC code", kwargs)
    kwargs['project_id_start'] = valid_int('project_id_start', "Project ID starting number", kwargs)

    return kwargs


def display_settings(kwargs):
    print("*****************************************************************************************")
    print("Source Directory:                    {}".format(kwargs['source']))
    print("Destination Directory:               {}".format(kwargs['destination']))
    print("Project Identifier MARC Identifier:  {}".format(kwargs['project_id_prefix']))
    print("Project Identifier Starting Number:  {}".format(kwargs['project_id_start']))
    print("Object Identifier MARC Identifier:   {}".format(kwargs['object_id_prefix']))
    print("Object Identifier Starting Number:   {}".format(kwargs['object_id_start']))
    print("User Name:                           {}".format(kwargs['user']))
    print("*****************************************************************************************")
    pass


def start_cli(**kwargs):
    source = None
    user = None
    object_id_prefix = None
    first_object_id = 1
    proj_id_prefix = "CAPS"
    first_project_id = 1
    output_path = None
    needs_more_info = True
    while needs_more_info:
        needs_more_info = False

        if 'source' in kwargs:
            source = kwargs['source']
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("source: pass")
        else:
            needs_more_info = True

        if 'object_id_prefix' in kwargs:
            object_id_prefix = kwargs['object_id_prefix']
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("object_id_prefix: pass")
        else:
            needs_more_info = True

        if 'object_id_start' in kwargs:
            try:
                first_object_id = int(kwargs['object_id_start'])
                if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                    print("object_id_start pass")
            except TypeError:
                needs_more_info = True
        else:
            needs_more_info = True

        if 'project_id_prefix' in kwargs:
            proj_id_prefix = kwargs['project_id_prefix']
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("project_id_prefix: pass")
        else:
            needs_more_info = True

        if 'project_id_start' in kwargs:
            try:
                first_project_id = int(kwargs['project_id_start'])
                if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                    print("project_id_start: pass")
            except TypeError:
                needs_more_info = True
        else:
            needs_more_info = True

        if 'user' in kwargs:
            user = kwargs['user']
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("user: pass")

        if 'destination' in kwargs:
            output_path = kwargs['destination']
            if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
                print("destination: pass")
        else:
            needs_more_info = True

        if needs_more_info:
            kwargs = update_information(kwargs)
            continue
        display_settings(kwargs)
        while True:
            is_user_happy = input("Are these correct? [y]/n/q :")
            if is_user_happy.lower() == 'n' or is_user_happy.lower() == 'no':
                needs_more_info = True
                kwargs = update_information(kwargs)
                break
            elif is_user_happy.lower() == 'y' or is_user_happy.lower() == 'yes' or not is_user_happy:
                needs_more_info = False
                break
            elif is_user_happy.lower() == 'q' or is_user_happy.lower() == 'quit':
                exit()
            else:
                sys.stderr.write("Not a valid answer. Please try again.\n")

    if MODE == running_mode.DEBUG or MODE == running_mode.BUILD:
        print("All data tests pass. Moving on")
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


    for queue in builder.queues:
        for file in queue.get_dict()['files']:
            print("\"{}\" -> \"{}\"".format(file['old'], file['new']))
        # print("{} {}".format(queue['files']['old'], queue['files']['new']))
    valid = False
    while(not valid):

        answer = input("Are you sure? [y]/n/q :")
        if answer.lower() == "n" or answer.lower() == "no" or answer.lower() == "q":
            print("Okay, exiting")
            quit()
        elif answer.lower() == "y" or answer.lower() == "yes" or answer == "":
            valid = True
        else:
            print("Not a valid input. Please try again.")

    reporter = rename_files.renaming_model.ReportFactory(username=user)
    reporter.initize_database()


    # Perform the renaming
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
