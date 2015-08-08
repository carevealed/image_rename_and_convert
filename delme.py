import os
import shutil
__author__ = 'California Audio Visual Preservation Project'
source_folder = "/Volumes/CAVPPTestDrive/anaTest/"
include_hidden = False
if os.path.exists(source_folder):
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if not include_hidden:
                if file.startswith('.'):
                    continue
                if os.path.splitext(file)[1] != ".xml":
                    continue
            shutil.copy(os.path.join(root, file), "/Volumes/CAVPPTestDrive/newxml/")
            print()