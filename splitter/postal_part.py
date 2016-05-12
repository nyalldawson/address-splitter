from address_part import *
import re

from valid_postal_types import *


class PostalPart(AddressPart):

    def name(self):
        return "postal"

    def check(self):
        # must have a number in it
        if not re.match(r'.*\b\d+[a-z]{0,2}$', self.test_string) and not re.match(r'.*\b[a-z]{0,2}\d+$', self.test_string):
            return False

        if self.test_string.count(' ') >= 6:
            return False

        # must start with a special string
        for t in valid_postal_types:
            if t[0] in self.test_string:
                return True

        return False

    def score(self):
        penalty = 0
        if re.match(r'^[a-z\s]+ \d+$', self.test_string):
            return 0
        elif re.match(r'^[a-z\s]+ \d+[a-z]{0,2}$', self.test_string):
            # eg po box 12b
            return 2
        if re.match(r'^[a-z\s]+ [a-z]{0,2}\d+$', self.test_string):
            # eg po box ab12
            return 0
        elif re.match(r'^[a-z\s]+ \d+\s*\-\s*\d+$', self.test_string):
            # eg po box 1-2
            return 0

        return 30

    def breakdown(self):
        parts = {}

        matches = re.match(r'^([a-z\s]+) (\d+)$', self.test_string)
        if matches:
            parts['postal_type'] = matches.group(1)
            parts['postal_number'] = matches.group(2)

        # expand postal type
        if parts.get('postal_type'):
            parts['postal_type'] = [t[1]
                                    for t in valid_postal_types if t[0] == parts['postal_type']][0]

        return parts
