from address_part import *
from valid_business_qualifiers import *
from valid_street_types import *

import re


class BusinessPart(AddressPart):

    def name(self):
        return "business"

    def check(self):

        for q in valid_business_qualifiers:
            if self.test_string.endswith(q):
                return True

        return False

    def score(self):
        penalty = 0

        # long phrases are penalised
        penalty += self.test_string.count(' ') * 2

        if re.match(r'.*\b\d+', self.test_string):
            # contains some numbers, unlikely
            penalty += 30

        for type in valid_street_types:
            if type['type'] in self.test_string.split(' ') or type['abbr'] in self.test_string.split(' '):
                # contains a street type, unlikely
                penalty += 10
                break

        return penalty

    def breakdown(self):
        self.parts = {}

        if self.test_string[:1] == '-':
            self.test_string = self.test_string[1:].strip()

        self.parts['business'] = self.test_string

        return self.parts
