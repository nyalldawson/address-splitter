import re
from address_part import *
from valid_street_types import *
from valid_street_names import *
from valid_location_qualifiers import *


def make_street_name(name, type, suffix):
    return ' '.join(filter(None, [name, type, suffix]))


class StreetPart(AddressPart):
    """Street part of an address"""

    def name(self):
        return "street"

    def check(self):
        test_string = self.test_string

        # check if last word in string is a street suffix, eg "n"
        if last_word(test_string) in valid_street_suffixes:
            # remove it for now
            test_string = remove_last_word(test_string)

        if test_string.count(' ') > 5:
            # too many words
            return False

        # is the last word in the string a full street type, eg "road"?
        if last_word(test_string) in [t['type'] for t in valid_street_types]:
            return True

        # is the last word in the string an abbreviated street type, eg "rd"?
        if last_word(test_string) in [t['abbr'] for t in valid_street_types]:
            return True

        # check if street is a single word street name, eg "citylink"
        if test_string in single_word_streets:
            return True

        # check if street is a special street name, eg "pall mall"
        if test_string in special_street_names:
            return True

        return False

    def score(self):
        cost = 0
        test_string = self.test_string
        self.parts = {}

        # remove special characters from street name
        if re.search(r'[^a-zA-Z0-9\s\-]', test_string):
            self.penalties.append(['special characters', 10])
            cost += 10
            test_string = re.sub(r'[^a-zA-Z0-9\s\-]', '', test_string)

        # single word and special street names
        if test_string in special_street_names:
            # a special street name, eg "pall mall"
            self.penalties.append(['special street name', 1])
            self.parts['street_name'] = test_string
            return 1

        if not ' ' in test_string:
            # single word street name

            if test_string in single_word_streets:
                self.parts['street_name'] = test_string
                self.penalties.append(['known street name', 0])
                # known single word street name, no cost
                return 0
            else:
                # unknown single word street name, unlikely
                self.penalties.append(['unknown street name', 30])
                self.parts['street_name'] = test_string
                return 30
        else:
            # long street names are penalised
            length_penalty = test_string.count(' ') * 3
            if test_string.count(' ') > 4:
                # more than 4 words scores a massive penalty
                length_penalty += 20
            self.penalties.append(['long street name', length_penalty])
            cost += length_penalty

        # street suffixes
        if last_word(test_string) in valid_street_suffixes:
            # directional suffixes (eg, "N" from "SMITH ST N") are rare, so
            # they are penalised
            self.penalties.append(['directional suffix', 10])
            cost += 10
            # store suffix
            self.parts['street_suffix'] = last_word(test_string)[:1]
            # then remove it
            test_string = remove_last_word(test_string)

        # street types
        if last_word(test_string) in [t['type'] for t in valid_street_types]:
            # last word is a valid full street type - eg "street"
            # store the abbreviated street type
            self.parts['street_type'] = [t['abbr'] for t in valid_street_types if t[
                'type'] == last_word(test_string)][0]
            # fetch cost for this street type
            street_type_cost = [t['cost'] for t in valid_street_types if t[
                'abbr'] == self.parts['street_type']][0]
            cost += street_type_cost
            self.penalties.append(
                ['street type ' + self.parts['street_type'], street_type_cost])
            test_string = remove_last_word(test_string)

        elif last_word(test_string) in [t['abbr'] for t in valid_street_types]:
            # last word is an abbreviated street type - eg "st"
            self.parts['street_type'] = last_word(test_string)
            # fetch cost for this street type
            street_type_cost = [t['cost'] for t in valid_street_types if t[
                'abbr'] == self.parts['street_type']][0]
            cost += street_type_cost
            self.penalties.append(
                ['street type ' + self.parts['street_type'], street_type_cost])
            test_string = remove_last_word(test_string)

        else:
            # last word is not a valid street type, penalise
            self.penalties.append(['no street type', 5])
            cost += 5

        # street name
        if not test_string in valid_street_names:
            # not a known street name
            self.penalties.append(['unknown street name', 15])
            cost += 15

            # unknown street name which contains a location flag and isn't the last word
            # eg - don't want "sherwood PARK princes hwy"
            # but DO want "emerald LAKE rd"
            # so having a location flag as the last word in the street NAME is
            # ok but anywhere else is discouraged
            words = test_string.split(' ')[:-1]
            if words:
                for q in valid_location_qualifiers:
                    if q['text'] in words:
                        # found one
                        self.penalties.append(
                            ['name contains location flag', 10])
                        cost += 10

        self.parts['street_name'] = test_string

        if re.match(r'.*\d+', test_string):
            # name contains some numbers, unlikely
            self.penalties.append(['contains numbers', 50])
            cost += 50

        return cost

    def breakdown(self):
        # rebuild street string
        self.parts['street'] = make_street_name(self.parts.get(
            'street_name'), self.parts.get('street_type'), self.parts.get('street_suffix'))

        return self.parts
