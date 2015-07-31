__author__ = 'California Audio Visual Preservation Project'
from csv import reader
from collections import namedtuple
from rename_files.nonAV import NonAVModel

Data = namedtuple("Data", ['Internet_Archive_URL',
                           'Object_Identifier',
                           'Call_Number',
                           'Project_Identifier',
                           'Project_Note',
                           'Institution',
                           'Asset_Type',
                           'Media_Type',
                           'Generation',
                           'Main_or_Supplied_Title',
                           'Additional_Title',
                           'Series_Title',
                           'Description_or_Content_Summary',
                           'Why_the_recording_is',
                           'Creator',
                           'Producer',
                           'Director',
                           'Writer',
                           'Interviewer',
                           'Performer',
                           'Country_of_Creation',
                           'Date_Created',
                           'Date_Published',
                           'Copyright_Statement',
                           'Gauge_and_Format',
                           'Total_Number_of_Reels',
                           'Duration',
                           'Silent_or_Sound',
                           'Color_and_or_Black_and',
                           'Contributor',
                           'Camera',
                           'Editor',
                           'Sound',
                           'Music',
                           'Cast',
                           'Interviewee',
                           'Speaker',
                           'Musician',
                           'Publisher',
                           'Distributor',
                           'Language',
                           'Subject_Topic',
                           'Subject_Topic_Authority_Source',
                           'Subject_Entity',
                           'Subject_Entity_Authority_Source',
                           'Genre',
                           'Genre_Authority_Source',
                           'Spatial_Coverage',
                           'Temporal_Coverage',
                           'Collection_Guide_Title',
                           'Collection_Guide_URL',
                           'Relationship',
                           'Relationship_Type',
                           'Aspect_Ratio',
                           'Running_Speed',
                           'Timecode_Content_Begins',
                           'Track_Standard',
                           'Channel_Configuration',
                           'Subtitles_Intertitles_Closed_Captions',
                           'Stock_Manufacturer',
                           'Base_Type',
                           'Base_Thickness',
                           'Copyright_Holder',
                           'Copyright_Holder_Info',
                           'Copyright_Date',
                           'Copyright_Notice',
                           'Institutional_Rights_Statement_URL',
                           'Object_ARK',
                           'Institution_ARK',
                           'Institution_URL',
                           'Quality_Control_Notes',
                           'Additional_Descriptive_Notes',
                           'Additional_Technical_Notes',
                           'Transcript',
                           'Cataloger_Notes',
                           'OCLC_number',
                           'Date_created',
                           'Date_modified',
                           'Reference_URL',
                           'CONTENTdm_number',
                           'CONTENTdm_file_name',
                           'CONTENTdm_file_path'])


def cleanup_headings(headings):

    newHeadings = []
    for heading in headings:
        assert(isinstance(heading, str))
        words = heading.split(" ")
        shorten = ""
        for index, word in enumerate(words):
            if index > 3:
                break
            else:
                if "/" in word:
                    word = word.replace("/", '_')
                if "(" or ")" in word:
                    word = word.replace("(", '')
                    word = word.replace(")", '')
                shorten += word
                shorten += "_"
        shorten = shorten[:-1]
        newHeadings.append(shorten)
        # newHeadings.append(heading.replace(" ", "_"))
    # newHeadings = headings
    return newHeadings


def get_csv_data(data_file):

    try:
        data_set = []
        with open(data_file, 'rU', encoding='utf-8') as f:
            data_reader = reader(f)
            next(data_reader)


            for row in data_reader:
                data = Data(*row)
                data_set.append(data)
    except UnicodeDecodeError:
        try:
            data_set = []
            with open(data_file, 'rU', encoding='ISO-8859-1') as f:
                data_reader = reader(f)
                next(data_reader)

                for row in data_reader:
                    data = Data(*row)
                    data_set.append(data)
        except UnicodeDecodeError:
            raise UnicodeDecodeError(str(data_file) +
                                     " is not in a supported format, only use UTF-8 or ISO-8859-1 formatted files.")
    return data_set


def build_record(data):

    assert isinstance(data, Data)
    root = NonAVModel.CollectionReference(collectionSource=data.Institution, projectSource=data.Project_Note)
    root.report_errors = NonAVModel.errors_report.WARNING

    descriptionDocument = NonAVModel.DescriptionDocument()

    # START Dublin Core
    dc = NonAVModel.DublinCore()
    dc.add_title(data.Main_or_Supplied_Title)
    dc.type = data.Media_Type
    dc.add_source(type="Owning instutution", url=data.Institution_URL, value=data.Institution)
    dc.add_coverage("what goes here?")  # FIXME Figure out what goes in Coverage
    dc.rights = data.Copyright_Statement

    print(dc)
    # END Dublin Core

    root.descriptionDocument = descriptionDocument
    pass


def main():
    data_file = "/Users/lpsdesk/PycharmProjects/rename_files/statelibrary_export.csv"

    data_set = get_csv_data(data_file)
    for data in data_set:
        assert(isinstance(data, Data))
        print("Building XML for {}".format(data.Object_Identifier))
        build_record(data)

if __name__ == '__main__':
    main()
