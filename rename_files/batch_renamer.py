import argparse
import sys
from rename_files.cli import *

def main():

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

    if args.source:
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

    if args.gui:
        sys.stderr.write("I'm truly sorry about this but the GUI version isn't ready yet.\nGo tell Henry how disappointed you are with him.\n")
    else:
        print(parser.print_help())

    # if args.interactive:
    #     print("INTERACTIVE")

if __name__ == '__main__':

    main()