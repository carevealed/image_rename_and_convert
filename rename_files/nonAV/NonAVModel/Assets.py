#!/usr/bin/python
# -*- coding: UTF-8 -*-
from .Element import Element
# import NonAVModel.AssetPart
# from Model import DescriptionDocument
from .CAPS_node import CAPS_node

class Assets(CAPS_node):
    def __init__(self, object_id=None, project_id=None, physical_location=None, color=None, total_parts=None, additional_description=None):
        """
        :param str object_id:               Unique object identifier to be supplied by the California Preservation Service.
        :param str project_id:
        :param str physical_location:       Name of owning institution.
        :param str color:                   The color element describes whether the physical object made up of content that is black and white, color, or a mixture
        :param str total_parts:             Describes the object's total number of parts. For example, "1 page" or "3 pages of 3."
        :param str additional_description:

        _objectID (str):
        _projectID (str):
        _physicalLocation (str):
        _dimensionsHeight (str):
        _dimensionsWidth (str):
        _color (str):
        _hasParts (str):
        _additionalDescription (str):
        _assetPart (Element):

        """
        super(Assets, self).__init__()
        self._objectID = None
        self._projectID = None
        self._physicalLocation = None
        self._dimensionsHeight = None
        self._dimensionsHeightUnit = None
        self._dimensionsWidth = None
        self._dimensionsWidthUnit = None
        self._color = None
        self._hasParts = None
        self._additionalDescription = None
        self._assetPart = None


        if object_id:
            self.objectID = object_id

        if project_id:
            self.projectID = project_id

        if physical_location:
            self.physicalLocation = physical_location

        if color:
            self.color = color

        if total_parts:
            self.hasParts = total_parts

        if additional_description:
            self.additionalDescription = additional_description

    @property
    def objectID(self):
        return self._objectID

    @objectID.setter
    def objectID(self, value):
        self._objectID = value


    @property
    def projectID(self):
        return self._projectID

    @projectID.setter
    def projectID(self, value):
        self._projectID = value


    @property
    def physicalLocation(self):
        return self._physicalLocation

    @physicalLocation.setter
    def physicalLocation(self, value):
        self._physicalLocation = value


    @property
    def dimensionsHeight(self):
        return self._dimensionsHeight

    @dimensionsHeight.setter
    def dimensionsHeight(self, value):
        self._dimensionsHeight = value


    @property
    def dimensionsHeightUnit(self):
        return self._dimensionsHeightUnit

    @dimensionsHeightUnit.setter
    def dimensionsHeightUnit(self, value):
        self._dimensionsHeightUnit = value


    @property
    def dimensionsWidth(self):
        return self._dimensionsWidth

    @dimensionsWidth.setter
    def dimensionsWidth(self, value):
        self._dimensionsWidth = value


    @property
    def dimensionsWidthUnit(self):
        return self._dimensionsWidthUnit

    @dimensionsWidthUnit.setter
    def dimensionsWidthUnit(self, value):
        self._dimensionsWidthUnit = value


    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value


    @property
    def hasParts(self):
        return self._hasParts

    @hasParts.setter
    def hasParts(self, value):
        self._hasParts = value


    @property
    def additionalDescription(self):
        return self._additionalDescription

    @additionalDescription.setter
    def additionalDescription(self, value):
        self._additionalDescription = value


    @property
    def assetPart(self):
        return self._assetPart

    @assetPart.setter
    def assetPart(self, value):
        self._assetPart = value


    def _make_xml(self):
        root = Element(tag="Assets")

        root.add_child(Element(tag="objectID", data=self.objectID))
        root.add_child(Element(tag="projectID", data=self.projectID))
        root.add_child(Element(tag="physicalLocation", data=self.physicalLocation))

        if self.dimensionsHeight:
            if self.dimensionsHeightUnit:
                root.add_child(Element(tag="dimensionHeight", data=self.dimensionsHeight, attributes={"unit": self.dimensionsHeightUnit}))
            else:
                raise Exception("dimensionHeight element is used but is missing a unit attribute.")

        if self.dimensionsWidth:
            if self.dimensionsWidthUnit:
                root.add_child(Element(tag="dimensionWidth", data=self.dimensionsWidth, attributes={"unit": self.dimensionsWidthUnit}))
            else:
                raise Exception("dimensionWidth element is used but is missing a unit attribute.")

        root.add_child(Element(tag="color", data=self.color))
        root.add_child(Element(tag="hasParts", data=self.hasParts))
        root.add_child(Element(tag="additionalDescription", data=self.additionalDescription))

        if self.assetPart:
            root.add_child(self.assetPart)

        return root

    def check_required_data(self):
        missing_attributes = []
        missing_fields = []
        valid = False

        if not self.objectID:
            missing_fields.append("objectID")

        if not self.projectID:
            missing_fields.append("projectID")

        if not self.physicalLocation:
            missing_fields.append("physicalLocation")

        # if there are either dimension, check if there are both of them
        if self.dimensionsWidth:
            if not self.dimensionsHeight:
                missing_fields.append("dimensionsHeight")

            if not self.dimensionsHeightUnit:
                missing_attributes.append("dimensionsHeight unit")

        if self.dimensionsHeight:
            if not self.dimensionsWidth:
                missing_fields.append("dimensionsWidth")

            if not self.dimensionsWidthUnit:
                missing_attributes.append("dimensionsWidth unit")

        if not self.color:
            missing_fields.append("color")

        if not self.hasParts:
            missing_fields.append("hasParts")

        if len(missing_fields) == 0 and len(missing_attributes) == 0:
            valid = True
        return self.xml_status(valid=valid, missing_fields=missing_fields, missing_attributes=missing_attributes)

    def validate_attribute(self):
        pass

