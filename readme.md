# CAPS Renaming Script

## Description:
This script is used to rename files from a partner's drive into the internal naming scheme. 

## Important:
* This is the first script for CAVPP/CAPS that uses Python version 3 instead of Python 2.7. if you are uncertain 
if you have Python 3 install, (on OSX or Linux) open up terminal and type:

        which python3
        
    If Python 3 is install, you'll receive a path leading to the Python3 directory. If you receive nothing back, 
    you'll have to install Python 3 by typing in the following command in the terminal.
    
    On OSX:
    
        brew install python3

## How to install
You have a few options. You most likely want to use the first one as it is the easiest. 


Option 1: Install binary (Wheel)
--------------------------------

1. Download the latest version from the releases section of the project's Github page 
https://github.com/cavpp/rename_files/releases. Right click on the link to latest version that ends in .whl and copy the address.
2. Open a terminal and type "sudo pip install" and paste in the link. 
    
    
    For example:
    
        sudo pip install https://github.com/cavpp/rename_files/releases/download/Prerelease/rename_files-0.1-py2.py3-none-any.whl

#### Notes: 


* The actual name of the file will change with each version.

* If you have a problem that pip isn't installed, you can install it with the following command.
 
        sudo easy_install pip




Option 2: From source using Setuptools
--------------------------------------

1. Open a terminal window and type:

        cd Downloads
        git clone https://github.com/cavpp/rename_files.git
        cd PBCore
        sudo python3 setup.py install 
        
2. Enter your computer password and the script will install along with all the dependencies.

## How to use:

### Command line:

1. In a terminal window type "rename -s " + the path to the files you want to rename.
    
    For example:
    
        rename -s /Volumes/CAVPPTestDrive/DPLA0003/Images/_Anaheim/

2. Follow the instructions
3. After the files are renamed to the new location, you will also find a report in the form of a CSV file in the same folder as the renamed files.

## Credits:
* Henry Borchers