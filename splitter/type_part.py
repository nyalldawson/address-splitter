from address_part import *
import re

from valid_address_types import *


class TypePart(AddressPart):
    """An extra qualifier at the start of an address, usually describing a unit or apartment number. Examples include:
    Unit 5,
    Shop 6A,
    Factory 4-5,
    Berth 1
    """

    def name(self):
        return "type"

    def check(self):
        # must have a number in it and follow the format
        #"Unit 5", "Unit 5A", or "Unit A5", "Unit T-05"
        if not re.match(r'.*\b\d+[a-z]{0,2}$', self.test_string) and not re.match(r'.*\b[a-z]{0,2}\d+$', self.test_string) and  \
                not re.match(r'.*\b[a-z]{0,2}\d+\s+&\s*[a-z]{0,2}\d+$', self.test_string) and not re.match(r'.*\b[a-z]\-\d+$', self.test_string):
            return False

        # Max of 5 words
        if self.test_string.count(' ') >= 4:
            return False

        # Must start with a special string
        if first_word(self.test_string) in [t[0] for t in valid_address_types]:
            return True
        if first_word(self.test_string) in [t[1] for t in valid_address_types]:
            return True

        return False

    def score(self):
        penalty = 0
        self.parts = {}

        # eg shop 12
        m = re.match(r'^([a-z]+) (\d+)$', self.test_string)
        if m:
            self.parts['address_type'] = m.group(1)
            self.parts['type_no'] = m.group(2)
            return 0

        # eg shop 12b
        m = re.match(r'^([a-z]+) (\d+[a-z]{0,2})$', self.test_string)
        if m:
            self.parts['address_type'] = m.group(1)
            self.parts['type_no'] = m.group(2)
            return 2

        m = re.match(r'^([a-z]+) ([a-z]{0,2}\d+)$', self.test_string)
        if m:
            # eg shop ab12
            self.parts['address_type'] = m.group(1)
            self.parts['type_no'] = m.group(2)
            return 0

        m = re.match(r'^([a-z]+) (\d+\s*\-\s*\d+)$', self.test_string)
        if m:
            # eg Shops 1-2
            self.parts['address_type'] = m.group(1)
            self.parts['type_no'] = m.group(2)
            return 0

        m = re.match(
            r'^([a-z]+) ([a-z]{0,2}\d+)\s+&\s*([a-z]{0,2}\d+)$', self.test_string)
        if m:
            # eg Lots 1 & 2
            self.parts['address_type'] = m.group(1)
            self.parts['type_no'] = m.group(2) + ", " + m.group(3)
            return 0

        m = re.match(r'([a-z]+) ([a-z]\-\d+)$', self.test_string)
        if m:
            # eg Unit t-05
            self.parts['address_type'] = m.group(1)
            self.parts['type_no'] = m.group(2)
            return 0

        return 50

    def breakdown(self):
        try:

            if self.parts['address_type'] in [t[0] for t in valid_address_types]:
                # part is an abbreviated type, eg "fcty"
                # expand to full type
                self.parts['address_type'] = [
                    t[1] for t in valid_address_types if t[0] == self.parts['address_type']][0]

            if self.parts['type_no'].isdigit():
                self.parts['type_no'] = str(int(self.parts['type_no']))
        except:
            pass

        return self.parts
