from address_part import *
import re


class AllotmentPart(AddressPart):

    def name(self):
        return "allotment"

    def check(self):
        # max of 2 words
        if self.test_string.count(' ') != 1:
            return False

        if not first_word(self.test_string) == 'allotment':
            return False

        return True

    def score(self):
        penalty = 0

        return penalty

    def breakdown(self):
        parts = {}

        parts['allotment'] = last_word(self.test_string)

        return parts


class SectionPart(AddressPart):

    def name(self):
        return "section"

    def check(self):
        # max of 2 words
        if self.test_string.count(' ') != 1:
            return False

        if not first_word(self.test_string) == 'section':
            return False

        return True

    def score(self):
        penalty = 0

        return penalty

    def breakdown(self):
        parts = {}

        parts['section'] = last_word(self.test_string)

        return parts


class ParishPart(AddressPart):

    def name(self):
        return "parish"

    def check(self):
        # max of 3 words
        if self.test_string.count(' ') != 2:
            return False

        if not remove_last_word(self.test_string) == 'parish of':
            return False

        return True

    def score(self):
        penalty = 0

        return penalty

    def breakdown(self):
        parts = {}

        parts['parish'] = last_word(self.test_string)

        return parts
