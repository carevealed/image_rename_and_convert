#!/usr/bin/python
# -*- coding: UTF-8 -*-
from .Element import Element
# from collections import OrderedDict
# import NonAVModel.DescriptionDocument
from .CAPS_node import CAPS_node


class DublinCore(CAPS_node):
    def __init__(self,
                 title=None,
                 creator=None,
                 subject=None,
                 description=None,
                 publisher=None,
                 contributor=None,
                 created_date=None,
                 type=None,
                 format=None,
                 identifier=None,
                 source=None,
                 language=None,
                 relation=None,
                 coverage=None,
                 rights=None):
        """
        _title (list):
        _creator (list):
        _subject (list):
        _description (str):
        _publisher (list):
        _contributor (list):
        _date (list):
        _type (str):
        _format (list):
        _identifier (list):
        _source (list):
        _language (list):
        _relation (str):
        _coverage (list):
        _rights (str):
        """
        super(DublinCore, self).__init__()

        self._title = []
        self._creator = []
        self._subject = []
        self._description = None
        self._publisher = []
        self._contributor = []
        self._date = []
        self._type = None
        self._format = []
        self._identifier = []
        self._source = []
        self._language = []
        self._relation = None
        self._coverage = []
        self._rights = None

        if title:
            self.add_title(title)
        if creator:
            self.add_creator(creator)
        if subject:
            self.add_subject(subject)
        if description:
            self.description = description
        if publisher:
            self.add_publisher(publisher)
        if contributor:
            self.add_contributor(contributor)
        if created_date:
            self.add_date(created_date, "created")
        if type:
            self.type = type
        if format:
            self.add_format(format)
        if identifier:
            self.add_identifier(identifier)
        if source:
            self.add_source(source)
        if language:
            self.add_language(language)
        if relation:
            self.relation = relation
        if coverage:
            self.add_coverage(coverage)
        if rights:
            self.rights = rights

    def _make_xml(self):
        root = Element("DublinCore")
        if self.title:
            for title in self.title:
                root.add_child(Element(tag="title", data=title))

        if self.creator:
            for creator in self.creator:
                root.add_child(Element(tag="creator", data=creator))

        if self.subject:
            for subject in self.subject:
                root.add_child(Element(tag="subject", data=subject))

        if self.description:
            root.add_child(Element(tag="description", data=self.description))

        if self.publisher:
            for publisher in self.publisher:
                root.add_child(Element(tag="publisher", data=publisher))

        if self.contributor:
            for contributor in self.contributor:
                root.add_child(Element(tag="contributor", data=contributor))

        if self.date:
            for date in self.date:
                if date[1]:
                    root.add_child(Element(tag="date", data=date[0], attributes={"type": date[1]}))
                else:
                    root.add_child(Element(tag="date", data=date[0]))

        if self.type:
            root.add_child(Element(tag="type", data=self.type))

        if self.format:
            for format in self.format:
                root.add_child(Element(tag="format", data=format))

        if self.identifier:
            for identifier in self.identifier:
                if identifier[1]:
                    root.add_child(Element(tag="identifier", data=identifier[0], attributes={"type": identifier[1]}))
                else:
                    root.add_child(Element(tag="identifier", data=identifier[0]))

        for source in self.source:
            if source[2]:
                root.add_child(Element(tag="source", data=source[0], attributes={"url": source[2], "type": source[1]}))
            else:
                root.add_child(Element(tag="source", data=source[0], attributes={"type": source[1]}))

        if self.language:
            for language in self.language:
                root.add_child(Element(tag="language", data=language))

        if self.relation:
            root.add_child(Element(tag="relation", data=self.relation))

        for coverage in self.coverage:
            if coverage[1]:
                root.add_child(Element(tag="coverage", data=coverage[0], attributes={"type": coverage[1]}))
            else:
                root.add_child(Element(tag="coverage", data=coverage[0]))

        root.add_child(Element(tag="rights", data=self.rights))
        return root

    @property
    def title(self):
        return self._title

    def add_title(self, value):
        self._title.append(value)

    @property
    def creator(self):
        return self._creator

    def add_creator(self, value):
        self._creator.append(value)

    @property
    def subject(self):
        return self._subject

    def add_subject(self, value):
        self._subject.append(value)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def publisher(self):
        return self._publisher

    def add_publisher(self, value):
        self._publisher.append(value)

    @property
    def contributor(self):
        return self._contributor

    def add_contributor(self, value):
        self._contributor.append(value)

    @property
    def date(self):
        if len(self._date) > 0:
            for date in self._date:
                assert isinstance(date, tuple)
        return self._date

    def add_date(self, value, type=None):
        new_date = (value, type)
        self._date.append(new_date)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def format(self):
        return self._format

    def add_format(self, value):
        self._format.append(value)

    @property
    def identifier(self):
        for identifier in self._identifier:
            assert isinstance(identifier, tuple)
        return self._identifier

    def add_identifier(self, value, type=None):
        self._identifier.append((value, type))

    @property
    def source(self):
        return self._source

    def add_source(self, value, type, url=None):
        self._source.append((value, type, url))

    @property
    def language(self):
        return self._language

    def add_language(self, value):
        self._language.append(value)

    @property
    def relation(self):
        return self._relation

    @relation.setter
    def relation(self, value):
        self._relation = value

    @property
    def coverage(self):
        return self._coverage

    def add_coverage(self, value, type=None):
        self._coverage.append((value, type))

    @property
    def rights(self):
        return self._rights

    @rights.setter
    def rights(self, value):
        self._rights = value

    def check_required_data(self):
        missing_fields = []
        missing_attributes = []
        valid = False

        if not self.title:
            missing_fields.append("title")
        if not self.type:
            missing_fields.append("type")
        if not self.source:
            missing_fields.append("source")
        if not self.coverage:
            missing_fields.append("coverage")
        if not self.rights:
            missing_fields.append("rights")

        if len(missing_fields) == 0 and len(missing_attributes) == 0:
            valid = True

        return self.xml_status(valid=valid, missing_fields=missing_fields, missing_attributes=missing_attributes)

		#
        # if len(missing_fields) > 0:
        #     raise Exception("Missing required metadata fields, '" + "', '".join(missing_fields) + "'.")

    def validate_attribute(self):
        pass

