
import argparse
import sys
import sqlite3
from rename_files.cli import *


def initial_setup():
    if os.path.exists("data.db"):
        print("found it in {}", os.path.abspath("data.db"))
        test1 = sqlite3.connect('data.db')
        try:
            test1.execute("SELECT * FROM jobs JOIN records ON jobs.job_id=records.job_id JOIN files ON records.record_id=files.record_id")
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
                                  'FOREIGN KEY(job_id) REFERENCES jobs(job_id));')

                    # files table
                    test1.execute('CREATE TABLE files('
                                  'file_id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 1 NOT NULL, '
                                  'record_id INTEGER,'
                                  'source VARCHAR(255),'
                                  'destination VARCHAR(255),'
                                  'date_renamed DATE DEFAULT CURRENT_TIMESTAMP,'
                                  'md5 VARCHAR(32),'
                                  'file_suffix VARCHAR(20),'
                                  'file_extension VARCHAR(4),'
                                  'file_notes TEXT,'
                                  'FOREIGN KEY(record_id) REFERENCES records(record_id));')
                    test1.close()
                    valid = True
                    pass
                if question.lower() == "n" or question.lower() == "no" or question == "":
                    print("Okay! Quitting")
                    test1.close()
                    quit()



    else:
        print("Nope")



def main():
    initial_setup()
    parser = argparse.ArgumentParser(description="Renamer")
    parser.add_argument('-s', '--source', type=str, help="The source")
    parser.add_argument('-d', '--destination', type=str, help="Destination")
    parser.add_argument('-o', '--object_id_prefix', type=str, help="MARC code for the institution used for the object "
                                                                   "identifier ")
    parser.add_argument('-x', '--object_id_start', type=int, help="the starting number for the object identifier")

    parser.add_argument('-p', '--project_id_prefix', type=str, default="CAPS", help="MARC code for the institution used for the project "
                                                                    "identifer. Default: CAPS")
    parser.add_argument('-y', '--project_id_start', type=int, help="the starting number for the object identifier")

    parser.add_argument('-u', '--username', type=str, help="Identify the user")
    # parser.add_argument('-i', '--interactive', action='store_true', help="Interactive mode")
    parser.add_argument('-g', '--gui', action='store_true', help="Graphical User Interface mode. Not yet implemented.")
    # parser.
    args = parser.parse_args()

    # print("SOURCE: {0}.".format(args.source))
    # print("DESTINATION: {0}.".format(args.destination))
    # print("MARC code for the institution: {0}.".format(args.object_id_prefix))
    # print("username: {0}.".format(args.username))
    # print("INTERACTIVE: {0}.".format(args.interactive))
    # print("GUI: {0}.".format(args.gui))

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

    elif args.gui:
        sys.stderr.write("I'm truly sorry about this but the GUI version isn't ready yet.\n"
                         "Go tell Henry that you are disappointed with him.\n")
    else:
        print(parser.print_help())

    # if args.interactive:
    #     print("INTERACTIVE")

if __name__ == '__main__':

    main()