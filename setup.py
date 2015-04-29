from setuptools import setup, find_packages

setup(
    name='rename_files',
    version='0.1.1',
    packages=find_packages(),
    url='https://github.com/cavpp/rename_files',
    license='GPL',
    install_requires=['setuptools >= 14.3.1','PySide >= 1.2.2'],
    author='California Audio Visual Preservation Project',
    author_email='hborcher@berkeley.edu',
    description='Renames image files from a folder to CAVPP naming scheme',
    entry_points={'console_scripts': ['rename = rename_files.batch_renamer:main']}
)
