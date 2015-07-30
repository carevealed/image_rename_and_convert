#!/usr/bin/python
# -*- coding: UTF-8 -*-
from abc import ABCMeta, abstractmethod, abstractproperty
from xml.dom.minidom import parseString
from xml.etree.ElementTree import tostring
from collections import namedtuple
# from NonAVModel import Element
import sys


class errors_report(enumerate):
    STRICT = 0
    WARNING = 1


class CAPS_node(object):
    __metaclass__ = ABCMeta
    xml_status = namedtuple("xml_status", ['valid','missing_fields', 'missing_attributes'])
    report_errors = errors_report.STRICT

    @abstractmethod
    def _make_xml(self):
        print("You shouldn't be here")
        pass

    # @abstractproperty
    @property
    def xml(self):
        errors = self.check_required_data()
        if self.report_errors == errors_report.STRICT:
            if len(errors.missing_fields) > 0:
                raise Exception("Missing required metadata fields, '" + "', '".join(errors.missing_fields) + "'.")
            if len(errors.missing_attributes) > 0:
                raise Exception("Missing required metadata attributes, '" +
                                "', '".join(errors.missing_attributes) +
                                "'.")

        elif self.report_errors == errors_report.WARNING:
            if len(errors.missing_fields) > 0:
                sys.stderr.write("Missing required metadata fields, '" +
                                 "', '".join(errors.missing_fields) +
                                 "'.\n")

            if len(errors.missing_attributes) > 0:
                sys.stderr.write("Missing required metadata attributes, '" +
                                 "', '".join(errors.missing_attributes)
                                 + "'.\n")

        xml = self._make_xml()

        return xml

    @classmethod
    def validate_tag(self):
        pass

    @abstractmethod
    def validate_attribute(self):
        pass

    @abstractmethod
    def check_required_data(self):
        pass

    @classmethod
    def __init__(self):
        self.__xML_attributes = None

    def get_xml(self):
        pass

    def __str__(self):
        # print(self.xml)

        assert self.xml is not None
        etree = tostring(self.xml.xml, encoding="utf-8")
        dom = parseString(str(etree.decode()))
        return dom.toprettyxml()
