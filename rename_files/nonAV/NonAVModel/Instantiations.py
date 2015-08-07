#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import NonAVModel.AssetPart
from .Element import Element
from xml.etree.ElementTree import Element as etElement
# import NonAVModel.Instantiation
from .CAPS_node import CAPS_node

class Instantiations(CAPS_node):
    def __init__(self, relationship=None):
        """
        _relationship (str):
        _instantiation (list): list of Instantiation Objects
        """
        super(Instantiations, self).__init__()
        self._relationship = relationship
        self._instantiation = []

    def add_instantiation(self, new_instantiation):
        # """@ParamType new_instantiation Model.Instantiation"""
        """
        :param Instantiation new_instantiation:
        """
        # assert(isinstance(new_instantiation, Element))
        self._instantiation.append(new_instantiation)

    def _make_xml(self):
        root = Element("Instantiations", attributes={"relationship": self.relationship})
        for instance in self._instantiation:
            root.add_child(instance)
        return root

    def check_required_data(self):
        missing_fields = []
        missing_attributes = []
        valid = False

        if not self.relationship:
            missing_attributes.append("relationship")
        if not self._instantiation:
            missing_fields.append("instantiation")

        if len(missing_fields) == 0 and len(missing_attributes) == 0:
            valid = True

        return self.xml_status(valid=valid, missing_fields=missing_fields, missing_attributes=missing_attributes)


    def validate_attribute(self):
        pass

    @property
    def relationship(self):
        return self._relationship

    @relationship.setter
    def relationship(self, value):
        self._relationship = value