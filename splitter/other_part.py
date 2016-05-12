from address_part import *
import re


class OtherPart(AddressPart):
    """A part of an address which is unable to be identified"""

    def name(self):
        return "other"

    def check(self):
        # allow max of 4 words
        if self.test_string.count(' ') > 3:
            return False

        return True

    def score(self):
        # Start cost at 20, since we generally don't want parts to be
        # identified as "other" unless we really have to
        cost = 20

        if re.match(r'.*\b\d+', self.test_string):
            # Contains some numbers, very unlikely for "other" parts since
            # they're more than likely something we want
            cost += 30

        #"Other" parts aren't likely to be at the very start of an address string
        if self.is_first():
            cost += 5

        # Penalise longer strings by adding a cost of 10 * number of words
        cost += self.test_string.count(' ') * 10

        return cost
