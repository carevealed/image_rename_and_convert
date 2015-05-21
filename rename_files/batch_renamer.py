
import argparse
import sys
import sqlite3
from rename_files.cli import *
from rename_files.gui import *
# from rename_files import start_gui

# import rename_files.gui
datafile = "data.db"

def initial_setup():
    if os.path.exists(datafile):
        print("Found database file: {}".format(os.path.abspath(datafile)))
        test1 = sqlite3.connect(os.path.abspath(datafile))
        try:
            test1.execute("SELECT job_id, username FROM jobs")
            test1.execute("SELECT pair_id, source_id, destination_id, record_id FROM file_pairs")
            test1.execute("SELECT record_id,job_id, project_id_number, project_id_prefix, object_id_number, object_id_prefix, ia_url FROM records")
            test1.execute("SELECT file_id, file_name, file_location, source, type, date_renamed, md5, file_suffix, file_extension FROM files")

            # test to see if the database will work.
            pass
        except sqlite3.OperationalError:
            valid = False
            while not valid:
                question = input("I couldn't open the database. Should I create a new one? y/[N]")
                if question.lower() == "y" or question.lower() == "yes":
                    # create new database
                    # Clear anything out if already exist
                    test1.execute('DROP TABLE IF EXISTS jobs;')
                    test1.execute('DROP TABLE IF EXISTS records;')
                    test1.execute('DROP TABLE IF EXISTS files;')
                    test1.execute('DROP TABLE IF EXISTS file_pairs;')

                    # jobs table
                    test1.execute('CREATE TABLE jobs('
                                  'job_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                                  'username VARCHAR(255) );')
                    # records table
                    test1.execute('CREATE TABLE records('
                                  'record_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL,'
                                  'job_id INTEGER,'
                                  'project_id_prefix VARCHAR(10),'
                                  'project_id_number INTEGER,'
                                  'object_id_prefix VARCHAR(10),'
                                  'object_id_number INTERGER,'
                                  'ia_url VARCHAR(512),'
                                  'FOREIGN KEY(job_id) REFERENCES jobs(job_id));')



                                  # 'FOREIGN KEY(record_id) REFERENCES records(record_id));')

                    # file_pair
                    test1.execute('CREATE TABLE file_pairs('
                                  'pair_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                                  'source_id INTEGER,'
                                  'destination_id INTEGER,'
                                  'record_id INTEGER, '
                                  'FOREIGN KEY(record_id) REFERENCES records(record_id),'
                                  'FOREIGN KEY(source_id) REFERENCES files(file_id)'
                                  ')')
                    # files table
                    test1.execute('CREATE TABLE files('
                                  'file_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                                  # 'record_id INTEGER,'
                                  'file_name VARCHAR(255),  '
                                  'file_location VARCHAR(255),'
                                  'source VARCHAR(255),'
                                  'type VARCHAR(20),'
                                  # 'destination VARCHAR(255),'
                                  'date_renamed DATE,'
                                  'md5 VARCHAR(32),'
                                  'destination_id INTEGER,'
                                  'file_suffix VARCHAR(20),'
                                  'file_extension VARCHAR(4),'
                                  'file_notes TEXT, '
                                  'FOREIGN KEY(destination_id) REFERENCES file_pairs(pair_id)'
                                  ')')

                    test1.close()
                    valid = True
                    pass
                if question.lower() == "n" or question.lower() == "no" or question == "":
                    print("Okay! Quitting")
                    test1.close()
                    quit()



    else:
        print("Nope")


def remove_database():
    print("Cleaning up database.")
    if os.path.exists(datafile):
        print("{} found".format(datafile))
        valid_response = False
        while not valid_response:
            response = input("Are you sure you want to remove it? y/[n]")
            if response.lower() == 'y' or response.lower() == 'yes':
                valid_response = True
                print("Okay. Deleting {}".format(datafile))
                os.remove(datafile)
                if os.path.exists(datafile):
                    sys.stderr.write("Error, Unable to remove file.")
                    quit()
                else:
                    print("Done")
                print("Cleaned")
            elif response.lower() == 'n' or response.lower() == 'no' or response.lower() == '':
                valid_response = True
                print("Okay. Canceling.")
            else:
                print("Not a valid answer. Please try again\n")

        # if confirm:

    print("Done.")
    pass


def found_data_file():
    if os.path.exists(datafile):
        pass


def main():
    parser = argparse.ArgumentParser(description="Renamer")
    parser.add_argument('-s', '--source', type=str, help="The source")
    parser.add_argument('-d', '--destination', type=str, help="Destination")
    parser.add_argument('-o', '--object_id_prefix', type=str, help="MARC code for the institution used for the object "
                                                                   "identifier ")
    parser.add_argument('-x', '--object_id_start', type=int, help="the starting number for the object identifier")

    parser.add_argument('-p', '--project_id_prefix', type=str, default="caps", help="Prefix code for the institution used for the project "
                                                                    "identifer. Default: caps")
    parser.add_argument('-y', '--project_id_start', type=int, help="the starting number for the object identifier")

    parser.add_argument('-u', '--username', type=str, help="Identify the user")
    # parser.add_argument('-i', '--interactive', action='store_true', help="Interactive mode")
    parser.add_argument('-g', '--gui', action='store_true', help="Graphical User Interface mode. EXPERIMENTAL!")
    parser.add_argument('--cleanup', action='store_true', help="Deletes stored data.")
    # parser.
    args = parser.parse_args()

    if args.cleanup:

        remove_database()
        quit()
    if not found_data_file():
        initial_setup()

    if args.source and not args.gui:
        print("Starting CLI mode")
        # from rename_files import cli

        # cli.start_cli(source=args.source, obj_id_prefix=args.object_id_prefix, output_path=args.destination, user=args.username)
        start_cli(source=args.source,
                  destination=args.destination,
                  object_id_prefix=args.object_id_prefix,
                  object_id_start=args.object_id_start,
                  project_id_prefix=args.project_id_prefix,
                  project_id_start=args.project_id_start,
                  user=args.username)

    elif args.gui and args.source:
        print("Starting GUI mode with {}".format(args.source))
        start_gui(folder=args.source)
    elif args.gui:
        print("Starting GUI mode")
        start_gui(folder=args.source)

    else:
        print(parser.print_help())

    # if args.interactive:
    #     print("INTERACTIVE")

if __name__ == '__main__':
    main()