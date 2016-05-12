from address_part import *
import re

valid_single_word_levels = ['basement']
valid_level_types = ['floors', 'floor', 'levels', 'level']
valid_level_numbers = ['first', 'second', 'ground', 'lower ground']


class LevelPart(AddressPart):

    def name(self):
        return "level"

    def check(self):
        # max of 3 words

        if self.test_string in valid_single_word_levels:
            return True
        elif not ' ' in self.test_string:
            return False

        if self.test_string.count(' ') > 2:
            return False

        if re.search(r'[\/\\,]', self.test_string):
            # invalid characters
            return False

        # must have a level type in it, eg level or floor
        if first_word(self.test_string.lower()) in valid_level_types:
            temp = remove_first_word(self.test_string)
            if re.match(r'^(\d)+(?:th|st|nd|rd)?$', temp):
                return True
            elif temp in valid_level_numbers:
                return True
        if last_word(self.test_string.lower()) in valid_level_types:
            if re.match(r'^(\d)+(?:th|st|nd|rd)?$', first_word(self.test_string.lower())):
                return True
            elif remove_last_word(self.test_string) in valid_level_numbers:
                return True

        return False

    def score(self):
        penalty = 0
        if re.match(r'^[a-z]+ \d+$', self.test_string):
            return 0

        return 0

    def breakdown(self):
        parts = {}

        if last_word(self.test_string.strip().lower()) in valid_level_types:
            parts['level_type'] = last_word(self.test_string.strip().lower())
            parts['level_number'] = remove_last_word(
                self.test_string.strip().lower())
        elif first_word(self.test_string.strip().lower()) in valid_level_types:
            parts['level_type'] = first_word(self.test_string.strip().lower())
            parts['level_number'] = last_word(self.test_string.strip().lower())

        if parts.get('level_number'):
            # make sure level number is valid type
            # eg, replace 5th with 5
            m = re.match(r'^(\d+)(?:th|st|nd|rd)$', parts['level_number'])
            if m:
                parts['level_number'] = m.group(1)

        return parts
