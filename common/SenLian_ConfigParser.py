# -*- coding: utf-8 -*-
from configparser import ConfigParser
import os, sys
import codecs


class ReConfigParser(ConfigParser):
    def __init__(self):
        super(ReConfigParser, self).__init__()
        reload(sys)
        sys.setdefaultencoding('utf-8')

    # TODO: 此处解决大小写不敏感问题
    def optionxform(self, optionstr):
        return optionstr

    # TODO: 此处解决记事本不换行问题
    def _write_section(self, fp, section_name, section_items, delimiter):
        """Write a single section to the specified `fp'."""
        fp.write("[{0}]\r\n".format(section_name))
        for key, value in section_items:
            value = self._interpolation.before_write(self, section_name, key, value)
            if value is not None or not self._allow_no_value:
                str(value).replace('\n', '\r\n\t')
                value = delimiter + str(value).replace('\n', '\r\n\t')
            else:
                value = ""
            fp.write("{0}{1}\r\n".format(key, value))
        fp.write("\r\n")


class DeployConfigure():
    def __init__(self, file, type='utf-8'):
        self.localparser = ReConfigParser()
        self.file = os.path.realpath(file)
        self.localparser.read(self.file, type)
        self.sections = self.get_sections()

    def get_sections(self):
        return self.localparser.sections()

    def get_options(self, section):
        return self.localparser.options(section)

    def get_value(self, section, option):
        return self.localparser.get(section, option)

    def get_values(self, section, options=[]):
        if len(options) == 0:
            options = self.get_options(section)
        values = []
        for option in options:
            value = self.get_value(section, option).replace(', ', ',').split(',')
            if "" in value:
                value.remove("")
            if len(value) != 0:
                values.extend(value)
        return values

    def set_value(self, section, option, value):
        if self.localparser.has_option(section, option):
            self.localparser.set(section, option, value)
        else:
            print(os.path.basename(self.file), 'has no section', section, 'or has no option', option)

    def set_value_by_option(self, option, value):
        for section in self.sections:
            self.set_value(section, option, value)

    def save(self, file=None, encoding='utf-8' ):
        file = file or self.file
        fp = codecs.open(filename=file, mode='w', encoding=encoding)
        self.localparser.write(fp)
        fp.close()
