import os
from time import sleep
import sys
from xml.etree.ElementTree import XMLParser

__author__ = 'California Audio Visual Preservation Project'
from csv import reader
from collections import namedtuple
from nonAV import NonAVModel
from xml.etree import ElementTree
from xml.dom import minidom
source_path = ""
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
                           'Date_record_created',
                           'Date_modified',
                           'Reference_URL',
                           'CONTENTdm_number',
                           'CONTENTdm_file_name',
                           'CONTENTdm_file_path'])



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


def map_to_dc(data):
    """
    :param Data data: Data packet to map to Dublin Core
    :return DublinCore: Dublin Core class
    """

    assert (isinstance(data, Data))
    dc = NonAVModel.DublinCore()
    dc.add_title(data.Main_or_Supplied_Title)
    dc.add_creator(data.Creator)
    dc.description = data.Description_or_Content_Summary
    for subject_topic in data.Subject_Topic.split("; "):
        dc.add_subject(subject_topic)
    for call_number in data.Call_Number.split("; "):
        dc.add_identifier(call_number, type="Call Number")
    dc.type = data.Media_Type
    dc.add_format(data.Gauge_and_Format)
    if data.Language:
        dc.add_language = data.Language
    dc.add_source(type="Owning institution", url=data.Institution_URL, value=data.Institution)
    dc.add_source(type="Internet Archive URL", value=data.Internet_Archive_URL)
    if data.Spatial_Coverage:
        dc.add_coverage(data.Spatial_Coverage, type="Spacial")
    if data.Temporal_Coverage:
        dc.add_coverage(data.Temporal_Coverage, type="Temporal")
    dc.rights = data.Copyright_Statement
    dc.add_date(data.Date_Created)

    return dc
    pass


def group_by_relationship(xml_files):
    parts = dict()
    for xml_file in xml_files:
        with open(xml_file, 'r') as f:
            dom = minidom.parseString(f.read())
            part_name = (dom.documentElement.getAttribute("relationship"))
            if part_name in parts:
                assert isinstance(parts[part_name], list)
                parts[part_name].append(xml_file)
                # files = parts[part_name]
                # files.append(xml_file)
                # parts[part_name] = files
            else:
                parts[part_name] = [xml_file]
    return parts


def compile_instances(folder, data):
    assert isinstance(data, Data)
    if not folder:
        raise ValueError("Folder parameter cannot be an empty string.")
    if not isinstance(folder, str):
        raise TypeError("Expected type: str, received: " + str(type(folder)))
    if not os.path.dirname(folder):
        raise ValueError("'" + str(folder)+"' is not a directory.")
    if not os.path.exists(folder):
        raise FileNotFoundError(str(folder) + " cannot be found.")

    pages = find_pages_xml(folder)

    assetPart = NonAVModel.AssetPart()
    for page in pages:
        preservation = None
        access = None
        page_xml = NonAVModel.Instantiations(relationship=page)
        page_instances = pages[page]
        # parser = XMLParser()

        for xml_instance in page_instances:
            xml_data = open_and_clean(xml_instance)
            xml_instance_tree = ElementTree.fromstring(xml_data)
            # FIXME this is really ugly code
            # x = xml_instance_tree.iter('additionalTechnicalNotes')
            tech_notes = xml_instance_tree.findall("additionalTechnicalNotes")
            # print(len(n))
            if tech_notes:
                for tech_note in xml_instance_tree.iter('additionalTechnicalNotes'):
                    if not tech_note:
                        print("No")
                        print(tech_note.text)
                    else:
                        print("yes")
                        print(tech_note.text)

                    # if xml_instance_tree[0].attrib['generation'] == 'Preservation':
                    tech_note.text = data.Additional_Technical_Notes

                    # else:
                    if xml_instance_tree[0].attrib['generation'] == 'Preservation' \
                            or xml_instance_tree[0].attrib['generation'] == 'Preservation Master' \
                            or xml_instance_tree[0].attrib['generation'] == 'Master':
                        tech_note.text = tech_note.text + "; " + data.Additional_Technical_Notes
            else:
                print("No notes found in file XML metadata")
                if xml_instance_tree[0].attrib['generation'] == 'Preservation':
                    print("Adding additionalTechnicalNotes to Preservation file XML.")
                    for note in xml_instance_tree.iter('Technical'):
                        # print(note)
                        ElementTree.SubElement(note, 'additionalTechnicalNotes')
                        for tech_note in xml_instance_tree.iter('additionalTechnicalNotes'):
                            if xml_instance_tree[0].attrib['generation'] == 'Preservation':
                                # print(data.Additional_Technical_Notes)
                                tech_note.text = data.Additional_Technical_Notes

            if xml_instance_tree[0].attrib['generation'] == 'Access Copy' \
                    or xml_instance_tree[0].attrib['generation'] == 'Access':
                access = xml_instance_tree[0]
                print("Access")
            elif xml_instance_tree[0].attrib['generation'] == 'Preservation':
                print("Preservation")
                preservation = xml_instance_tree[0]
            elif xml_instance_tree[0].attrib['generation'] == 'Preservation Master':
                print("Preservation")
                preservation = xml_instance_tree[0]
            elif xml_instance_tree[0].attrib['generation'] == 'Master':
                print("Preservation")
                preservation = xml_instance_tree[0]
            else:
                raise Exception("Something went wrong with your data. Got '{}' for the generation of your metadata".format(xml_instance_tree[0].attrib['generation']))
        page_xml.add_instantiation(preservation)


        if access:
            page_xml.add_instantiation(access)
        assetPart.add_instantiations(page_xml.xml)

    return assetPart



def open_and_clean(xml_instance):
    raw_data = None
    with open(xml_instance, 'r') as f:
        raw_data = f.read()
    data = raw_data.split("\n")
    cleaned_data = []
    for n in data:
        cleaned_data.append(n.strip())
    data = "".join(cleaned_data)
    return data


def find_pages_xml(folder):
    xml_files = []
    include_hidden = False
    for root, dirs, files in os.walk(folder):
        for file in files:
            if not include_hidden:
                if file.startswith('.'):
                    continue
            if os.path.splitext(file)[1] != '.xml':
                continue
            if not "_access" in file and not "_prsv" in file:
                continue
            xml_files.append(os.path.join(root, file))

    return group_by_relationship(xml_files)


def find_folder_from_oid(data, root):
    assert isinstance(data, Data)
    assert os.path.dirname(root)
    found_folder = False
    if not os.path.exists(root):
        raise FileNotFoundError(root)
    for root, dirs, files in os.walk(root):
        if data.Object_Identifier in root:
            found_folder = True
            break

    if found_folder:
        return root
    else:
        raise FileNotFoundError(Data.Object_Identifier)
    pass


def append_tech_nodes(assetPart):

    assert isinstance(assetPart, NonAVModel.Element)
    new_asset = assetPart.xml

    return new_asset

    pass



def build_assets(data):
    global source_path
    assert isinstance(data, Data)
    assets = NonAVModel.Assets()

    folder = find_folder_from_oid(data, source_path)
    assets.assetPart = compile_instances(folder, data).xml
    # add additional technical notes
    assets.assetPart = append_tech_nodes(assets.assetPart)

    assets.hasParts = data.Total_Number_of_Reels
    assets.objectID = data.Object_Identifier
    assets.projectID = data.Project_Identifier
    assets.physicalLocation = data.Institution
    # TODO: add assets.dimensionsHeight and the rest of the dimension
    assets.color = data.Color_and_or_Black_and
    assets.additionalDescription = data.Additional_Descriptive_Notes
    return assets


def build_descriptionDocument(data):
    assert isinstance(data, Data)
    descriptionDocument = NonAVModel.DescriptionDocument()
    descriptionDocument.dublinCore = map_to_dc(data).xml
    descriptionDocument.assets = build_assets(data)
    return descriptionDocument


def build_collectionReference(data):
    assert isinstance(data, Data)
    collection_reference = NonAVModel.CollectionReference(collectionSource=data.Institution, projectSource=data.Project_Note)
    collection_reference.report_errors = NonAVModel.errors_report.WARNING

    descriptionDocument = build_descriptionDocument(data).xml


    collection_reference.descriptionDocument = descriptionDocument
    return collection_reference


def build_record(data):

    assert isinstance(data, Data)
    root = build_collectionReference(data)

    return root


def test(param):
    pass


def main():
    global source_path
    if len(sys.argv) < 2:
        sys.stderr.write("Needs at least one argument.\n")
        exit(-1)

    if len(sys.argv) == 3:
        if sys.argv[1] == "-t":
            if not os.path.isdir(sys.argv[2]):
                sys.stderr.write("Not a directory.\n")
                quit(-1)
            if not os.path.exists(sys.argv[2]):
                sys.stderr.write("Directory does not exist.\n")
                quit(-1)

            print("Running test mode")
            test(sys.argv[2])
            print("Test finished.")
            exit(0)
        else:
            sys.stderr.write("Not a valid option.\n")
            quit(-1)
    if not os.path.exists(sys.argv[1]):
        sys.stderr.write("File doesn't exists.\n")
        exit(-1)
    else:
        print("\nCreating CAVPP Non-AV/Dublin Core XML records from: " + os.path.basename(sys.argv[1]) + "\n")
        source_path = os.path.dirname(sys.argv[1])
        print(source_path)
        data_set = get_csv_data(sys.argv[1])
        for data in data_set:
            assert(isinstance(data, Data))
            print("Building XML for {}.\n".format(data.Object_Identifier))
            try:
                new_path = find_folder_from_oid(data, source_path)
                assert os.path.exists(new_path)
                new_file_name = data.Object_Identifier + "_metadata.xml"
                new_file = os.path.join(new_path, new_file_name)
                new_xml = build_record(data)
                with open(new_file, 'w') as f:
                    f.write(new_xml.__str__())
                print("Saved compiled metadata as {}.\n\n".format(new_file))
            except FileNotFoundError as e:
                sys.stderr.write("Couldn't find file data for " + data.Object_Identifier + ".\n")
            # sleep(.01)

if __name__ == '__main__':
    main()
