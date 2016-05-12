from address_part import *
import re


class NumberPart(AddressPart):
    """House/unit number part of an address"""

    def name(self):
        return "number"

    def check(self):
        # String must have a number in it
        if not re.search(r'\b\d+', self.test_string):
            return False

        # Allow a maximum of 5 words for a number part
        if self.test_string.count(' ') >= 4:
            return False

        return True

    def score(self):

        if re.match(r'^\d+$', self.test_string):
            # Just numbers, no cost
            return 0
        elif re.match(r'^\d+[a-z]{1,2}$', self.test_string):
            # "10a"
            return 1
        elif re.match(r'^\d+\s*\-\s*\d+$', self.test_string):
            # "10-20"
            return 1
        elif re.match(r'^lot \d+$', self.test_string):
            # "lot 2"
            return 2
        elif re.match(r'^lot \d+ & \d+$', self.test_string):
            # "lot 1 & 2"
            return 3
        elif re.match(r'^\d+\s*[\/\\]\s*\d+$', self.test_string):
            # unit type "1/23"
            return 1
        elif re.match(r'^\d+\s*-\s*\d+\s*[\/\\]\s*\d+$', self.test_string):
            # unit type "1-2/23"
            return 3
        elif re.match(r'^no \d+$', self.test_string):
            # "no 2"
            return 2
        elif re.match(r'^\d+\s+[a-z]$', self.test_string):
            # "2 a"
            return 5

        # number which starts with a strange character (eg "/ 343")
        if re.match(r'^[//]\s*\d+\s*$', self.test_string):
            return 5

        if ',' in self.test_string:
            # Very unlikely to have commas in house number part
            return 70

        # Unknown house number format
        return 50

    def breakdown(self):
        parts = {}

        # get unit and house number from "4/5" format
        m = re.match(r'^(\d+)\s*[\/\\]\s*(\d+)$', self.test_string)
        if m:
            parts['type_no'] = m.group(1)
            parts['house_number_1'] = m.group(2)
            return parts

        # get house numbers from "4-6" format
        m = re.match(r'^(\d+)\s*\-\s*(\d+)$', self.test_string)
        if m:
            parts['house_number_1'] = m.group(1)
            parts['house_number_2'] = m.group(2)
            return parts

        # get numbers from "1-2/23" format
        m = re.match(r'^(\d+)\s*-\s*(\d+)\s*[\/\\]\s*(\d+)$', self.test_string)
        if m:
            parts['type_no'] = '-'.join([m.group(1), m.group(2)])
            parts['house_number_1'] = m.group(3)
            return parts

        # get house number from "no 5" format
        m = re.match(r'^no (\d+)$', self.test_string)
        if m:
            parts['house_number_1'] = m.group(1)
            return parts

        m = re.match(r'^(\d+)\s+([a-z])$', self.test_string)
        if m:
            # "2 a"
            parts['house_number_1'] = m.group(1) + m.group(2)
            return parts
        else:
            # unknown format
            # split string into words
            for word in self.test_string.split():
                clean = word.strip()
                if re.match(r'\d+[a-z]{0,2}', clean):
                    # part looks like a number, eg 47A
                    parts['house_number_1'] = clean

        return parts
