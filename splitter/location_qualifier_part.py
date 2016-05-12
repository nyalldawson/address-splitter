from address_part import *
from locality_part import *
from valid_location_qualifiers import *
from valid_street_types import *
from valid_localities import *

import re

replacements = [[r'\bs[\\\/]c\b', 'shopping centre'],
                [r'\bs[\\\/]centre\b', 'shopping centre']]


class LocationQualifierPart(AddressPart):

    def name(self):
        return "location_qualifier"

    def check(self):
        self.qualifier = {}
        self.relation = ''

        for r in location_qualifiers_relations:
            if self.test_string.endswith(r):
                self.relation = r
                # remove relation from end of string
                self.test_string = self.test_string[:-len(r)].strip()
                break
            if self.test_string.startswith(r):
                self.relation = r
                # remove relation from end of string
                self.test_string = self.test_string[len(r):].strip()
                break

        for q in valid_location_qualifiers:
            if self.test_string.endswith(q['text']):
                self.qualifier = q
                return True

        for r in location_qualifier_regexs:
            if re.match(r, self.test_string):
                return True

        return False

    def score(self):
        penalty = 0

        # long phrases are penalised
        penalty += self.test_string.count(' ') * 3
        self.penalties.append(['long phrase', self.test_string.count(' ') * 3])

        if re.match(r'.*\b\d+', self.test_string):
            # contains some numbers, unlikely
            self.penalties.append(['contains numbers', 30])
            penalty += 30

        for type in valid_street_types:
            if type['type'] in self.test_string.split(' ') or type['abbr'] in self.test_string.split(' '):
                # contains a street type, unlikely
                street_type_cost = type.get('inv_cost', 10)
                self.penalties.append(
                    ['contains street type ' + type['abbr'], street_type_cost])
                penalty += street_type_cost

        for locality in valid_localities:
            if locality in self.test_string.split(' '):
                # contains a locality, unlikely
                self.penalties.append(['contains locality', 10])
                penalty += 10

        for q in valid_location_qualifiers:
            if self.test_string == q['text']:
                # entire string is a qualifier, rare
                self.penalties.append(['whole string qualifier', 5])
                penalty += 5
            if ' ' in self.test_string and q['text'] in remove_last_word(self.test_string).split(' '):
                # contains a second location qualifier, rare
                self.penalties.append(['second qualifier ' + q['text'], 5])
                penalty += 5

        # Locality followed immediately by a location qualifier is unlikely
        # It's more likely that this locality is actually part of the location qualifier, eg "CAIRNLEA TOWN CENTRE",
        # rather then "CAIRNLEA", "TOWN CENTRE"
        if self.preceded_by(LocalityPart):
            self.penalties.append(['preceded by locality', 5])
            penalty += self.qualifier.get('penalty_following_locality', 5)

        return penalty

    def breakdown(self):
        self.parts = {}

        if self.test_string[:1] == '-':
            self.test_string = self.test_string[1:].strip()

        for replacement in replacements:
            self.test_string = re.sub(
                replacement[0], replacement[1], self.test_string)

        if self.relation:
            self.parts['qualifier_relation'] = self.relation

        self.parts['location_qualifier'] = self.test_string

        return self.parts

    def dupe_part_cost(self):
        return 5
