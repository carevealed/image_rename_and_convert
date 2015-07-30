#!/usr/bin/python
# -*- coding: UTF-8 -*-
from . import DublinCore
# import NonAVModel.Assets
# from NonAVModel.CollectionReference import CollectionReference
from .Element import Element
from .CAPS_node import CAPS_node

class DescriptionDocument(CAPS_node):
    def __init__(self):
        """

        :return:
        """
        super(DescriptionDocument, self).__init__()
        self._dublinCore = None
        self._assets = None

    def _make_xml(self):
        root = Element("DescriptionDocument")
        root.add_child(self.dublinCore)
        root.add_child(self.assets)
        return root

    def check_required_data(self):
        missing_fields = []
        missing_attributes = []
        valid = False

        if not self.dublinCore:
            missing_fields.append("dublinCore")
        if not self.assets:
            missing_fields.append("assets")
        if len(missing_fields) == 0 and len(missing_attributes) == 0:
            valid = True
        return self.xml_status(valid=valid, missing_fields=missing_fields, missing_attributes=missing_attributes)

    def validate_attribute(self):
        pass

    @property
    def dublinCore(self):
        return self._dublinCore

    @dublinCore.setter
    def dublinCore(self, value):
        if not isinstance(value, Element):
            raise TypeError("Expected an Element type but received " + str(type(Element)))
        self._dublinCore = value

    @property
    def assets(self):
        return self._assets

    @assets.setter
    def assets(self, value):
        self._assets = value
