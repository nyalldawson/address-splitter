from address_part import *
from valid_street_types import *
from valid_street_names import *
from street_part import *
import re

valid_corner_strings = ['cnr.', 'cnr', 'crn', 'corner', 'intersection']
valid_nonword_corner_strings = ['cnr.']
valid_street_seperators = ['&']


class StreetCornerPart(AddressPart):

    def name(self):
        return "street_corner"

    def check(self):

        # min of 3 words
        if self.test_string.count(' ') < 2:
            return False

        if last_word(self.test_string) in valid_street_seperators:
            return False
        if first_word(self.test_string) in valid_street_seperators:
            return False

        if first_word(self.test_string) in valid_corner_strings:
            return True

        for corner_string in valid_corner_strings:
            if corner_string in self.test_string:
                return True

        for seperator in valid_street_seperators:
            if seperator in self.test_string:
                return True

        return False

    def score(self):
        cost = 0

        self.parts = {}

        test_string = self.test_string

        test_street_type = last_word(test_string)
        plural_street_type = False
        if test_street_type[-1:] == 's':
            # plural last word
            singular_last_word = test_street_type[:-1]
            if singular_last_word in [t['abbr'] for t in valid_street_types]:
                # part is a valid abbreviated street type, eg "st"
                self.parts['street_type'] = singular_last_word
                test_string = remove_last_word(test_string)
                plural_street_type = True
            elif singular_last_word in [t['type'] for t in valid_street_types]:
                self.parts['street_type'] = [
                    t['abbr'] for t in valid_street_types if t['type'] == singular_last_word][0]
                test_string = remove_last_word(test_string)
                plural_street_type = True

        if first_word(test_string) in valid_corner_strings:
            test_string = remove_first_word(test_string)
        else:
            for corner in valid_nonword_corner_strings:
                if test_string.startswith(corner):
                    # remove "cnr." part from string
                    test_string = test_string[len(corner):]
                    break

        done_split = False
        for seperator in valid_street_seperators:
            if seperator in test_string:
                streets = [street.strip()
                           for street in test_string.split(seperator)]
                self.parts['street_name'] = streets[0]
                self.parts['street_name_2'] = streets[1]
                done_split = True
                if plural_street_type:
                    self.parts['street_type_2'] = self.parts['street_type']
                else:
                    # need to get street types
                    self.parts['street_name'], self.parts['street_type'], self.parts[
                        'street_suffix'] = self.split_street_name(self.parts['street_name'])
                    self.parts['street_name_2'], self.parts['street_type_2'], self.parts[
                        'street_suffix_2'] = self.split_street_name(self.parts['street_name_2'])
                    # quick check - if first street doesn't have a type, our
                    # string may have been like "CNR WAVERLEY AND JELL RD"
                    if not self.parts['street_type'] and self.parts['street_type_2']:
                        # need to make sure this isn't a valid one name street,
                        # eg CITYLINK

                        if not self.parts['street_name'] in single_word_streets:
                            self.parts['street_type'] = self.parts[
                                'street_type_2']

        if not done_split:
            for seperator in valid_corner_strings:
                if seperator in test_string:
                    streets = [street.strip()
                               for street in test_string.split(seperator)]
                    if not streets[0] or not streets[1]:
                        continue
                    self.parts['street_name'] = streets[0]
                    self.parts['street_name_2'] = streets[1]
                    done_split = True
                    if plural_street_type:
                        self.parts['street_type_2'] = self.parts['street_type']
                    else:
                        street_type = last_word(streets[0])
                        if street_type in [t['abbr'] for t in valid_street_types]:
                            # part is a valid abbreviated street type, eg "st"
                            self.parts['street_type'] = street_type
                            self.parts['street_name'] = remove_last_word(streets[
                                                                         0])
                        elif street_type in [t['type'] for t in valid_street_types]:
                            # part is a full street type, eg "street"
                            # replace with abbreviation
                            self.parts['street_type'] = [
                                t['abbr'] for t in valid_street_types if t['type'] == street_type][0]
                            self.parts['street_name'] = remove_last_word(streets[
                                                                         0])
                        street_type2 = last_word(streets[1])
                        if street_type2 in [t['abbr'] for t in valid_street_types]:
                            # part is a valid abbreviated street type, eg "st"
                            self.parts['street_type_2'] = street_type2
                            self.parts['street_name_2'] = remove_last_word(streets[
                                                                           1])
                        elif street_type2 in [t['type'] for t in valid_street_types]:
                            # part is a full street type, eg "street"
                            # replace with abbreviation
                            self.parts['street_type_2'] = [
                                t['abbr'] for t in valid_street_types if t['type'] == street_type2][0]
                            self.parts['street_name_2'] = remove_last_word(streets[
                                                                           1])

        if not self.parts.get('street_name') or not self.parts.get('street_name_2'):
            return 100000

        if self.parts.get('street_type') and not self.parts.get('street_name') in valid_street_names:
            # not a known street name
            cost += 20
            cost += self.parts.get('street_name').count(' ') * 5
        elif not self.parts.get('street_type') and not self.parts['street_name'] in single_word_streets:
            # not a known single word street name
            cost += 100

        if not self.parts.get('street_name_2') in valid_street_names:
            # not a known street name
            cost += 20

        # if not self.parts.get('street_type'):
        #    cost += 100

        if not self.parts.get('street_type_2'):
            cost += 20

        return cost

    def split_street_name(self, text):
        street_name = None
        street_type = None
        street_suffix = None

        if last_word(text) in valid_street_suffixes:
            street_suffix = last_word(text)[:1]
            text = remove_last_word(text)

        if first_word(text) == 'the':
            street_name = text
        elif not ' ' in text:
            # one word street name
            street_name = text
        else:
            street_name = remove_last_word(text.strip())

            street_type = last_word(text.strip())
            if street_type in [t['abbr'] for t in valid_street_types]:
                # part is a valid abbreviated street type, eg "st"
                pass
            elif street_type in [t['type'] for t in valid_street_types]:
                # part is a full street type, eg "street"
                # replace with abbreviation
                street_type = [t['abbr'] for t in valid_street_types if t[
                    'type'] == street_type][0]
            else:
                # can't find a street type
                street_name = text
                street_type = None

        return street_name, street_type, street_suffix

    def breakdown(self):

        if self.parts.get('street_name'):
            # rebuild street string
            self.parts['street'] = make_street_name(self.parts.get(
                'street_name'), self.parts.get('street_type'), self.parts.get('street_suffix'))
            self.parts['street2'] = make_street_name(self.parts.get(
                'street_name_2'), self.parts.get('street_type_2'), self.parts.get('street_suffix_2'))

        return self.parts
