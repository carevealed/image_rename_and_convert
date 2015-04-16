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
                builder.add_queue(newfile)
    if debug:
        print(builder.__dict__)
        print(len(builder))



if __name__ == "__main__":
    sys.stderr.write("Not a main entry point\n")
    sys.stderr.write("Don't forget to get rid of this!!!\n")


    main("/Volumes/CAVPPTestDrive/DPLA0003/Images/_Anaheim/")
