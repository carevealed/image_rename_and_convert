# CAPS Renaming Script

## Description:
This script is used to process image files from a partner's drive into new collections that conform to the CAPS 
standards. 

Just add metadata. 

 
## Note:
* This script uses Python version 3.4 instead of Python 2.7 so if you want to run the script from the source, make sure 
you have the correct version of python. **If you are running this through the Anaconda Launcher, you won't have to worry 
about this directly.** 

If you are uncertain if you have Python 3.4 or higher installed, 
(on OSX or Linux) open up terminal and type:

        which python3
        
    If Python 3 is install, you'll receive a path leading to the Python3 directory. If you receive nothing back, 
    you'll have to install Python 3 by typing in the following command in the terminal.
    
    On OSX:
    
        brew install python3

If this script is installed in through the Anaconda Launcher, make sure you install it into a environment that is at 
least Python 3.4 or higher.

## How to install
You have a few options. You most likely want to use the first one as it is the easiest. 

Option 1: Install using Conda (recommended)
-------------------------------------------

If you are setting up Conda/Anaconda for the first time, please look at the readme document 
[here](https://github.com/cavpp/conda_recipes/tree/master#setting-up-conda) first 

1. In the launcher program, open a Python 3.4 environment or higher.
2. Click on the install button for this script


Option 2: Install binary (Wheel)
--------------------------------

1. Download the latest version from the releases section of the project's Github page 
https://github.com/cavpp/rename_files/releases. Right click on the link to latest version that ends in .whl and copy the address.
2. Open a terminal and type "sudo pip3 install" and paste in the link. 
    
  
#### Notes: 


* This is useful if you need to install a previous version.
* The actual name of the file will change with each version.
* If you have a problem that pip isn't installed, you can install it with the following command.
 
        sudo easy_install pip

If easy_install doesn't work, try following the instructions at this [link](https://pip.pypa.io/en/latest/installing.html#install-pip).



Option 3: From source using Setuptools
--------------------------------------

1. Open a terminal window and type:

        cd Downloads
        git clone https://github.com/cavpp/rename_files.git
        cd PBCore
        sudo python3 setup.py install 
        
2. Enter your computer password and the script will install along with all the dependencies.


## How to update:

If you are using the script through the Conda/Anaconda Launcher, you will automatically see an icon to let you know 
that a new version is available. Simply, click the update button and Conda will take care of the rest

If you are using any other method, installing the newer version should override the old version.

## How to use:

### Command line:

1. In a terminal window type "rename -s " + the path to the files you want to rename.
    
    For example:
    
        rename -s /Volumes/CAVPPTestDrive/DPLA0003/Images/_Anaheim/

2. Follow the instructions
3. After the files are renamed to the new location, you will also find a report in the form of a CSV file in the same folder as the renamed files.

### Graphical User Interface:

1. In a terminal window type "rename -g ".

## Credits:
* Henry Borchers