from setuptools import setup

setup(
    name='rename_files',
    version='0.1',
    packages=['rename_files'],
    url='https://github.com/cavpp/rename_files',
    license='GPL',
    author='California Audio Visual Preservation Project',
    author_email='hborcher@berkeley.edu',
    description='Renames image files from a folder to CAVPP naming scheme',
    entry_points={'console_scripts': ['rename = rename_files.batch_renamer:main']}
)
