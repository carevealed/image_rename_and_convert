#!/usr/bin/python
# -*- coding: UTF-8 -*-
# from Model import Instantiation
# from Model import Technical
# from Model import Instantiations
# from Model import Assets
# from Model import DublinCore

from xml.etree.ElementTree import Element as etElement
from xml.etree.ElementTree import tostring, fromstring
from xml.dom.minidom import parseString
from collections import OrderedDict


class Element(object):
    VALID_KEYS = ["CollectionReference",
                  "title",
                  "creator",
                  "subject",
                  "description",
                  "publisher",
                  "contributor",
                  "date",
                  "type",
                  "format",
                  "identifier",
                  "source",
                  "language",
                  "relation",
                  "coverage",
                  "rights",
                  "DescriptionDocument",
                  "DublinCore",
                  "title",
                  "creator",
                  "subject",
                  "subject",
                  "description",
                  "date",
                  "type",
                  "format",
                  "identifier",
                  "source",
                  "source",
                  "language",
                  "coverage",
                  "rights",
                  "Assets",
                  "objectID",
                  "projectID",
                  "physicalLocation",
                  "dimensionsHeight",
                  "dimensionsWidth",
                  "color",
                  "hasParts",
                  "additionalDescription",
                  "AssetPart",
                  "Instantiations",
                  "Instantiation",
                  "fileName",
                  "fileSize",
                  "checksum",
                  "derivedFrom",
                  "Technical",
                  "fileFormat",
                  "imageFormat",
                  "resolutionWidth",
                  "resolutionHeight",
                  "colorSpace",
                  "chromaSubsampling",
                  "colorDepth",
                  "compressionMode",
                  "additionalTechnicalNotes"]

    VALID_ATTRIBUTES = []  # TODO add in valid attributes

    def __init__(self, tag, data=None, attributes=None):
        """
        :param str tag: The XML tag (name of the element). This must be a valid tag in CAPS/CAPS Non-av metadata scheme.
        :param data: the value inside the element.
        :param dict attributes: Contains all the attributes for a given XML element

        tag (str): The XML tag (name of the element).
        value: the value inside the element.
        attributes (OrderedDict): Contains all the attributes for a given XML element

        """

        if not isinstance(tag, str):
            raise TypeError("Expected str, received " + str(type(tag)))
        if tag not in self.VALID_KEYS:
            raise ValueError("\"" + str(tag) + "\" is not a valid CAVPP element key.")
        self._tag = tag
        self._children = []
        if data:
            self._data = str(data)
        else:
            self._data = None
        if attributes:
            if not isinstance(attributes, dict):
                raise TypeError("Expected Dict, recieved " + str(type(attributes)))
            for key in attributes.keys():
                try:
                    test = int(key[0])
                    print(test)
                    raise TypeError("You cannot start attributes with a number")
                except ValueError:
                    pass
            self._attributes = OrderedDict(attributes)
        else:
            self._attributes = OrderedDict()

    def tag(self):
        return self._tag

    def get_attributes(self):
        """
        :rtype: OrderedDict
        """
        return self._attributes

    def add_attribute(self, key, value):
        """
        :param str key: The name part of the name/value pair
        :param str value: The value part of the name/value pair.
        :rtype: None
        """

        assert isinstance(self._attributes, OrderedDict)
        self._attributes[key] = value


    def delete_attribute(self, key):
        """
        :param str key: The key of the attribute you want to delete
        :rtype: None
        """
        if key not in self._attributes:
            raise KeyError("No attribute named '" + key + "' found.")
        del self._attributes[key]


    def __str__(self):
        """
        Returns the XML element pretty string.
        :rtype: str
        """
        etree = tostring(self.xml, encoding="utf-8")
        dom = parseString(str(etree.decode()))
        return dom.toprettyxml()

    def get_data(self):
        """
        :rtype: str
        """

        pass

    def add_child(self, child):
        if not isinstance(child, Element) and not isinstance(child, etElement):
            raise TypeError(str(type(Element)))
        self._children.append(child)

    @property
    def xml(self):
        element = etElement(self._tag)
        element.text = self._data
        if self._attributes:
            for key in self._attributes:
                # print(key)
                element.set(key, self._attributes[key])
        for child in self._children:
            if isinstance(child, Element):
                element.append(child.xml)
            if isinstance(child, etElement):
                element.append(child)
        return element
