import argparse
def main():

    parser = argparse.ArgumentParser(description="Renamer")
    parser.add_argument('-s', '--source', type=str, help="The source")
    parser.add_argument('-d', '--destination', type=str, help="Destination")
    parser.add_argument('-o', '--object_id_prefix', type=str, help="MARC code for the institution")
    parser.add_argument('-u', '--username', type=str, help="Identify the user")
    parser.add_argument('-i', '--interactive', action='store_true', help="Interactive mode")
    parser.add_argument('-g', '--gui', action='store_true', help="Graphical User Interface mode. EXPERIMENTAL.")
    # parser.
    args = parser.parse_args()

    print("SOURCE: {0}.".format(args.source))
    print("DESTINATION: {0}.".format(args.destination))
    print("MARC code for the institution: {0}.".format(args.object_id_prefix))
    print("username: {0}.".format(args.username))
    print("INTERACTIVE: {0}.".format(args.interactive))
    print("GUI: {0}.".format(args.gui))

    if args.source and args.destination:
        print("Starting automatic mode")
        import cli
        cli.start_cli(source=args.source, obj_id_prefix=args.object_id_prefix, output_path=args.destination, user=args.username)

    # if args.interactive:
    #     print("INTERACTIVE")

if __name__ == '__main__':
    main()