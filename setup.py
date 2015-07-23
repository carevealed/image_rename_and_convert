from setuptools import setup, find_packages

setup(
    name='rename_and_convert_images',
    version='0.5b1',
    packages=['rename_files', 'rename_files.gui_datafiles'],
    url='https://github.com/cavpp/rename_files',
    license='GPL',
    install_requires=['setuptools >= 14.3.1', 'Pillow >=2.8.1'],
    author='California Audio Visual Preservation Project',
    author_email='hborcher@berkeley.edu',
    zip_safe=False,
    description='Renames image files from a folder to CAVPP naming scheme',
    entry_points={'console_scripts': ['renameimages = rename_files.batch_renamer:main']}
)
