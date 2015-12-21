
import argparse
import sys
try:
    from PyQt4 import QtGui
except ImportError:
    from PyQt5 import QtGui
import sqlite3
from rename_files.cli import *
from rename_files.gui import *
# from rename_files import start_gui

# import rename_files.gui
# import rename_files.gui
this_dir, this_filename = os.path.split(__file__)
datafile = os.path.join(this_dir, "data", "data.db")

def initial_setup(gui):
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
            make_new_database = False
            if gui:
                message = "The required data file was not found.\n\nIf this is your first time running the script, " \
                          "you'll have to create a new one before you can start.\n\nWould you like to create one now?"
                app =QtGui.QApplication(sys.argv)
                reply = QtGui.QMessageBox.question(QtGui.QWidget(), "Data file not found", message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
                if reply == QtGui.QMessageBox.Ok:
                    make_new_database = True
                elif reply == QtGui.QMessageBox.Cancel:
                    make_new_database = False
                else:
                    make_new_database = False
                # w.show()

                # app.exec_()

            else:
                while not valid:
                    question = input("I couldn't open the database or is not valid. Should I create a new one? y/[N]")
                    if question.lower() == "y" or question.lower() == "yes":
                        make_new_database = True
                        valid = True

                    elif question.lower() == "n" or question.lower() == "no" or question == "":
                        make_new_database = False
                        valid = True
                        valid = True

            if make_new_database:
                initialize_database(datafile)
                valid = True
                if gui:
                    QtGui.QMessageBox.information(QtGui.QWidget(),"Success", "File created")
                pass
            else:
                print("Okay! Quitting")
                test1.close()
                quit()


    else:
        sys.stderr.write("Database could not be initialized\n")
        exit(-1)


def initialize_database(dbfile):
    '''

    :param dbfile: str
    :return:
    '''
    # create new database
    # Clear anything out if already exist


    database = sqlite3.connect(os.path.abspath(dbfile))
    database.execute('DROP TABLE IF EXISTS jobs;')
    database.execute('DROP TABLE IF EXISTS records;')
    database.execute('DROP TABLE IF EXISTS files;')
    database.execute('DROP TABLE IF EXISTS file_pairs;')
    # jobs table
    database.execute('CREATE TABLE jobs('
                     'job_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                     'username VARCHAR(255) );')
    # records table
    database.execute('CREATE TABLE records('
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
    database.execute('CREATE TABLE file_pairs('
                     'pair_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                     'source_id INTEGER,'
                     'destination_id INTEGER,'
                     'record_id INTEGER, '
                     'FOREIGN KEY(record_id) REFERENCES records(record_id),'
                     'FOREIGN KEY(source_id) REFERENCES files(file_id)'
                     ')')
    # files table
    database.execute('CREATE TABLE files('
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
    database.close()


def rebuild_database():
    global datafile
    print("Cleaning up database.")
    if os.path.exists(datafile):
        print("{} found".format(datafile))
        valid_response = False
        while not valid_response:
            response = input("Are you sure you want to clear it and rebuild it? y/[n]")
            if response.lower() == 'y' or response.lower() == 'yes':
                valid_response = True
                print("Okay. Rebuilding {}".format(datafile))
                # os.remove(datafile)
                # if os.path.exists(datafile):
                #     sys.stderr.write("Error, Unable to remove file.")
                #     quit()
                # else:
                #     print("Done")

                try:
                    initialize_database(datafile)
                except IOError:
                    sys.stderr.write("Error: Cannot edit the file.\n")
                    quit(-1)
                print("Rebuilt")
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

        rebuild_database()
        quit()
    if not found_data_file():
        initial_setup(args.gui)

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
                  database=datafile,
                  user=args.username)

    elif args.gui and args.source:
        print("Starting GUI mode with {}".format(args.source))
        start_gui(database=datafile, folder=args.source)
    elif args.gui:
        print("Starting GUI mode")
        start_gui(database=datafile, folder=args.source)

    else:
        print(parser.print_help())

    # if args.interactive:
    #     print("INTERACTIVE")

if __name__ == '__main__':
    main()
