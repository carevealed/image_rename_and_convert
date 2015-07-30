#!/usr/bin/python
# -*- coding: UTF-8 -*-
from enum import Enum
from .Element import Element
# import NonAVModel.Instantiation
import re
from .CAPS_node import CAPS_node
from .CAPS_node import errors_report


class CompressionModes(Enum):
    LOSSLESS = "Lossless"
    LOSSY = "Lossy"
    UNCOMPRESSED = "Uncompressed"
    UNKNOWN = "Unknown"


class Technical(CAPS_node):
    VALID_ATTRIBUTES = []
    def __init__(self,
                 fileFormat = None,
                 imageFormat = None,
                 width = None,
                 height = None,
                 chromaSubsampling = None,
                 colorBitDepth = None,
                 compressionMode = None, report_errors=errors_report.STRICT):
        """
        :param str fileFormat:              Specifies the MIME type of the file.
        :param str imageFormat:             Specifies the encoding of the digital file. For example: JPEG200
        :param int width:                   Specifies the x dimensions of the digital file.
        :param int height:                  Specifies the y dimensions of the digital file
        :param str chromaSubsampling:       Specifies the Chroma Subsampling as a ratio in the format integer:integer:integer. For example 4:2:2.In the absence of subsampling, the value of this element is 4:4:4.
        :param colorDepth:                  The bit depth per channel
        :param str compressionMode:
        _fileFormat (str):                  Specifies the MIME type of the file.
        _imageFormat (str):                 Specifies the encoding of the digital file. For example: JPEG200
        _resolutionWidth                    Specifies the x dimensions of the digital file.
        _resolutionHeight                   Specifies the y dimensions of the digital file
        _colorSpace (str):                  Specifies the type of color space used by the digital file. For example: YUV
        _chromaSubsampling (str):           Specifies the Chroma Subsampling as a ratio in the format integer:integer:integer. For example 4:2:2.In the absence of subsampling, the value of this element is 4:4:4.
        _colorDepth                         The bit depth per channel
        _compressionMode                    Designates the type of compression. Please use only Lossless, Lossy, Uncompressed, or Unknown
        _additionalTechnicalNotes (str):    Additional techincal notes about the file that do not fit into other elements

        """
        super(Technical, self).__init__()
        self._fileFormat = None
        self._imageFormat = None
        self._resolutionWidth = None
        self._resolutionWidthUnit = None
        self._resolutionHeightUnit = None
        self._resolutionHeight = None
        self._colorSpace = None
        self._chromaSubsampling = None
        self._colorDepth = None
        self._compressionMode = None
        self._colorDepthUnit = None
        self._chromaSubsampling = None
        self._additionalTechnicalNotes = None

        self.report_errors = report_errors


        self.fileFormat = fileFormat
        self.imageFormat = imageFormat


        if width:
            if isinstance(width, int):
                self.resolutionWidthUnit = "pixels"
                self.resolutionWidth = width
            else:
                raise TypeError("Expected int received " + str(type(width)))
        if height:
            if isinstance(height, int):
                self.resolutionHeightUnit = "pixels"
                self.resolutionHeight = height
            else:
                raise TypeError("Expected int received " + str(type(height)))

        if colorBitDepth:

            self.colorDepth = colorBitDepth
            self.colorDepthUnit = "bits"


        if compressionMode:
            self.compressionMode = compressionMode

        if chromaSubsampling:
            self.chromaSubsampling = chromaSubsampling




    def _make_xml(self):
        root = Element(tag="Technical")
        root.add_child(Element(tag='fileFormat', data=self.fileFormat))
        root.add_child(Element(tag='imageFormat', data=self.imageFormat))
        root.add_child(Element(tag='resolutionWidth', data=self.resolutionWidth, attributes={"unit": self.resolutionWidthUnit}))
        root.add_child(Element(tag='resolutionHeight', data=self.resolutionHeight, attributes={"unit": self.resolutionHeightUnit}))
        root.add_child(Element(tag='colorSpace', data=self.colorSpace))

        if self._chromaSubsampling:
            root.add_child(Element(tag='chromaSubsampling', data=self.chromaSubsampling))

        root.add_child(Element(tag='colorDepth', data=self.colorDepth, attributes={"unit": self.colorDepthUnit}))
        root.add_child(Element(tag='compressionMode', data=self.compressionMode))
        if self._additionalTechnicalNotes:
            root.add_child(Element(tag='additionalTechnicalNotes', data=self.additionalTechnicalNotes))
        return root

    def validate_attribute(self):
        # todo fill in validate_attribute
        pass

    def check_required_data(self):
        missing_fields = []
        missing_attributes = []
        valid = False

        if not self.fileFormat:
            missing_fields.append("fileFormat")
        if not self.imageFormat:
            missing_fields.append("imageFormat")
        if not self.resolutionHeight:
            missing_fields.append("resolutionHeight")
        if not self.resolutionHeightUnit:
            missing_attributes.append("resolutionHeight unit")
        if not self.resolutionWidthUnit:
            missing_attributes.append("resolutionWidth unit")
        if not self.resolutionWidth:
            missing_fields.append("resolutionWidth")
        if not self.colorSpace:
            missing_fields.append("colorSpace")
        if not self.colorDepth:
            missing_fields.append("colorDepth")
        if not self.colorDepthUnit:
            missing_attributes.append("colorDepth unit")
        if not self.compressionMode:
            missing_fields.append("compressionMode")

        if len(missing_fields) == 0 and len(missing_attributes) == 0:
            valid = True

        return self.xml_status(valid=valid, missing_fields=missing_fields, missing_attributes=missing_attributes)

    @property
    def fileFormat(self):
        return self._fileFormat

    @fileFormat.setter
    def fileFormat(self, value):
        self._fileFormat = value


    @property
    def imageFormat(self):
        return self._imageFormat

    @imageFormat.setter
    def imageFormat(self, value):
        self._imageFormat = value


    @property
    def resolutionWidthUnit(self):
        return self._resolutionWidthUnit

    @resolutionWidthUnit.setter
    def resolutionWidthUnit(self, value):
        self._resolutionWidthUnit = value


    @property
    def resolutionWidth(self):
        return self._resolutionWidth

    @resolutionWidth.setter
    def resolutionWidth(self, value):
        self._resolutionWidth = value


    @property
    def resolutionHeightUnit(self):
        return self._resolutionHeightUnit

    @resolutionHeightUnit.setter
    def resolutionHeightUnit(self, value):
        self._resolutionHeightUnit = value


    @property
    def resolutionHeight(self):
        return self._resolutionHeight

    @resolutionHeight.setter
    def resolutionHeight(self, value):
        self._resolutionHeight = value


    @property
    def colorSpace(self):
        return self._colorSpace

    @colorSpace.setter
    def colorSpace(self, value):

        self._colorSpace = value


    @property
    def chromaSubsampling(self):
        return self._chromaSubsampling

    @chromaSubsampling.setter
    def chromaSubsampling(self, value):
        chroma_sub_pattern = re.compile('\d+:\d+:\d+')
        # Todo: check if colorSpace, it is properly formated with regex
        if not chroma_sub_pattern.match(value):
            raise ValueError( "'" + str(value) + "' is not a proper chroma subsampling format")

        self._chromaSubsampling = value


    @property
    def colorDepth(self):
        return self._colorDepth

    @colorDepth.setter
    def colorDepth(self, value):
        if not isinstance(value, int):
            raise TypeError("Expected an int, received " + str(type(value)))
        self._colorDepth = value


    @property
    def colorDepthUnit(self):
        return str(self._colorDepthUnit)

    @colorDepthUnit.setter
    def colorDepthUnit(self, value):
        self._colorDepthUnit = value


    @property
    def compressionMode(self):
        return self._compressionMode

    @compressionMode.setter
    def compressionMode(self, value):
        # Todo: check if compression mode, it is the right ENUM
        if not isinstance(value, CompressionModes):
            raise TypeError("Expected an CompressionModes, received " + str(type(value)))
        self._compressionMode = value.value


    @property
    def additionalTechnicalNotes(self):
        return self._additionalTechnicalNotes

    @additionalTechnicalNotes.setter
    def additionalTechnicalNotes(self, value):
        self._additionalTechnicalNotes = value

