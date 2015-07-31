#!/usr/bin/python
# -*- coding: UTF-8 -*-
# from .DescriptionDocument import DescriptionDocument
from .CAPS_node import CAPS_node
from .Element import Element

class CollectionReference(CAPS_node):
    def __init__(self, collectionSource=None, projectSource=None):
        super(CollectionReference, self).__init__()
        self._descriptionDocument = None
        self._collectionSource = None
        self._projectSource = None

        if collectionSource:
            self._collectionSource = collectionSource
        if projectSource:
            self._projectSource = projectSource

    def _make_xml(self):
        root = Element(tag="CollectionReference")
        root.add_attribute("collectionSource", self._collectionSource)
        root.add_attribute("projectSource", self._projectSource)
        root.add_attribute("xmlns", "http://calpreservation.org/projects/audiovisual-preservation/dcscheme.html")
        root.add_attribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.add_attribute("xsi:schemaLocation", "http://calpreservation.org/projects/audiovisual-preservation/dcscheme.html http://calpreservation.org/projects/audiovisual-preservation/CAVPPDC.xsd")

        root.add_child(self._descriptionDocument)
        return root

    def check_required_data(self):
        missing_attributes = []
        missing_fields = []
        valid = False

        if not self._collectionSource:
            missing_attributes.append("collectionSource")
        if not self._projectSource:
            missing_attributes.append("projectSource")

        if not self._descriptionDocument:
            missing_fields.append("DescriptionDocument")

        if len(missing_fields) == 0 and len(missing_attributes) == 0:
            valid = True

        return self.xml_status(valid=valid, missing_fields=missing_fields, missing_attributes=missing_attributes)


    def validate_attribute(self):
        pass

    @property
    def descriptionDocument(self):
        return self._descriptionDocument

    @descriptionDocument.setter
    def descriptionDocument(self, value):
        self._descriptionDocument = value

    @property
    def collectionSource(self):
        return self._collectionSource

    @collectionSource.setter
    def collectionSource(self, value):
        self._collectionSource = value

    @property
    def projectSource(self):
        return self._projectSource

    @projectSource.setter
    def projectSource(self, value):
        self._projectSource = value