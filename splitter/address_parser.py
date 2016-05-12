import itertools
import copy
import sys
from locality_part import *
from street_part import *
from number_part import *
from type_part import *
# location qualifiers, eg "Main Hall", "Smith Oval"
from location_qualifier_part import *
# floor/level part, eg "First Floor", "Basement Level"
from level_part import *
from postal_part import *
from street_corner_part import *
from business_part import *
from other_part import *
from parish_part import *

# List of all possible address part types to compare against
part_types = [NumberPart, StreetPart, StreetCornerPart, LocalityPart, TypePart, LocationQualifierPart,
              LevelPart, OtherPart, AllotmentPart, SectionPart, ParishPart, PostalPart, BusinessPart]


class AddressVariantPart:
    """A section of an address and a type to check it against"""

    def __init__(self, part, type):
        self.part = part['substring'].strip()
        self.position = part['position']
        self.type = type(self)
        # Check if this part is a possible match for the specified type
        # Eg, SMITH ST isn't a possible house number
        self.cost = 0
        self.penalties = []
        if self.type.check():
            self.valid = True
        else:
            self.valid = False

    def __repr__(self):
        return str(self.as_dict())

    def as_dict(self):
        return {'part': self.part, 'position': self.position, 'type': self.type.name(), 'cost': self.cost, 'penalties': self.penalties}

    def get_part(self):
        return self.part

    def get_type(self):
        return self.type

    def get_position(self):
        return self.position

    def set_path(self, path):
        self.path = path

    def next_part(self):
        try:
            return self.path[self.position + 1]
        except:
            return None

    def prev_part(self):
        try:
            return self.path[self.position - 1]
        except:
            return None

    def get_cost(self):
        # need to get position in path
        cost = self.type.score()
        self.cost = cost
        self.penalties = self.type.get_penalties()
        return cost

    def get_penalties(self):
        return self.penalties

    def is_valid(self):
        return self.valid


class AddressVariant:
    """A possible combination of parts for an address"""

    def __init__(self, variant):
        global part_types
        self.variant = variant
        self.cost = 0
        self.parts = []

        # Calculate costs for all possible intrepretations of each part of the
        # address variant
        for part in self.variant:
            parts = []
            # For every part of the address, check it against every possible type
            #(eg if the part is "SMITH ST", check it as a house number, street name, locality name, etc)
            for type in part_types:
                part_variant = AddressVariantPart(part, type)
                # Is this a possible type for this part of the address? (eg,
                # "SMITH ST" can't be a house number)
                if part_variant.is_valid():
                    parts.append(part_variant)

            self.parts.append(parts)

    def calc_cost(self, path, max_cost=100000):
        cost = 0
        for v in path:
            v.set_path(path)
            cost += v.get_cost()
            if cost > max_cost:
                return None

        return cost

    def least_cost(self, max_cost):
        """Calculates the combination of parts and types with lowest cost"""

        cheapest_cost = max_cost
        possible_paths = []

        # Get every combination of parts and types
        combinations = [[h for h in p if h] for p in self.parts]
        for path in itertools.product(*combinations):
            p = copy.deepcopy(path)
            # Calculate total cost for this path, but break if the cost is more
            # than the current cheapest cost
            cost = self.calc_cost(p, cheapest_cost)
            if cost is None:
                continue

            # Check if path has duplicated types
            notes = ''
            type_count = {}
            type_dupe_cost = {}
            for type in [v.get_type() for v in p]:
                type_count[type.name()] = type_count.get(type.name(), 0) + 1
                type_dupe_cost[type.name()] = type.dupe_part_cost()

            for type, counts in type_count.iteritems():
                if counts > 1:
                    # Having multiple values for the same part type (eg two
                    # street names) costs 50 for each duplicate part
                    cost += type_dupe_cost[type] * (counts - 1)
                    notes += 'duplicate ' + type + \
                        ' (' + str(type_dupe_cost[type] * (counts - 1)) + ')'

            if cost < cheapest_cost:
                cheapest_cost = cost

            current_path = {'path': p, 'cost': cost, 'notes': notes}
            possible_paths.append(current_path)

        if not possible_paths:
            return None, None, None

        # Sort possible path list by cost
        cheapest = sorted(possible_paths, key=lambda v: v['cost'])[0]
        cheapest_path = cheapest['path']
        cheapest_cost = cheapest['cost']
        cheapest_notes = cheapest['notes']
        # Penalise more complex splits with more parts, prefer simple
        cheapest_cost += len(cheapest_path) * 2
        cheapest_notes += "path length cost " + str(len(cheapest_path) * 2)

        return cheapest_path, cheapest_cost, cheapest_notes

    def __repr__(self):
        return str(self.parts) + ": " + str(self.penalty)


class Address:

    def __init__(self, address_string):
        self.address_string = address_string
        # Clean up address string prior to processing
        self.preprocess()
        self.variants = []
        self.parse()

    def __repr__(self):
        return self.address_string

    def parse(self, show_all=False):
        """Parses the address and gets all possible variants"""

        # Generate a list of all possible breakdowns for this address

        # Start with the entire string
        part_combinations = [
            [{'position': 0, 'substring': self.address_string}]]

        # Add all possible combinations of address string
        for x in self.break_down():
            part_combinations.append(x)

        number_paths = len(part_combinations)

        # Create address variants for all part combinations
        self.variants = []
        current_percent = 0
        for index, combination in enumerate(part_combinations):
            current_rounded_percent = int(20 * float(index) / number_paths)
            if current_rounded_percent != current_percent:
                sys.stdout.write(".")
                current_percent = current_rounded_percent

            self.variants.append(AddressVariant(combination))

        #self.variants = [AddressVariant(combination) for combination in part_combinations]

        # Calculate costs for all variants
        self.costed_variants = []
        max_cost = 1000000
        current_percent = 0
        number_variants = len(self.variants)
        for index, variant in enumerate(self.variants):
            current_rounded_percent = int(20 * float(index) / number_variants)
            if current_rounded_percent != current_percent:
                sys.stdout.write(".")
                current_percent = current_rounded_percent

            cheapest_variant, cost, notes = variant.least_cost(max_cost)
            if cheapest_variant is None:
                continue

            if cost < max_cost and not show_all:
                max_cost = cost

            self.costed_variants.append(
                {'variant': cheapest_variant, 'cost': cost, 'notes': notes})

        # Sort list with cheapest variants first
        self.costed_variants.sort(key=lambda v: v['cost'])

    def get_costed_variants(self, show_all=False):
        """Returns all costed variants"""
        self.parse(show_all)
        return self.costed_variants

    def get_best_variant(self):
        """Returns the best (cheapest) costed variant"""

        best_variant = self.costed_variants[0]

        # Further refine results by formatting the best variant
        # For example, this replaces "STREET" with "ST", splits street names into parts (name/type/suffix), etc
        # Also converts values to uppercase
        result = {part.get_type().name(): part.get_part().upper()
                  for part in best_variant['variant']}
        result2 = {}
        for part in best_variant['variant']:
            breakdown = part.get_type().breakdown()
            if breakdown:
                for b, v in breakdown.iteritems():
                    if result2.get(b):
                        result2[b] = result2[b] + ', ' + v
                    else:
                        result2[b] = v
            else:
                result2[part.get_type().name()] = part.get_part().upper()
                # result.update(breakdown)

        # Make result into a dictionary
        result2.update({k: str(v).upper() for k, v in result2.iteritems()})
        for key in result2:
            result2[key] = re.sub(r'^[\.]', '', result2[key])

        best_variant['result'] = result2

        return best_variant

    def break_down(self):
        """Breaks down a string a words into all possible combinations"""
        # Position of break characters:
        # At the beginning of the string
        breaks = [-1]
        # On special characters
        breaks.extend([m.start() for m in re.finditer(
            r"[;, \/\\\-]+", self.address_string)])
        # At the end of string
        breaks.append(len(self.address_string))

        ns = range(1, len(breaks) - 1)
        for n in ns:
            for indices in itertools.combinations(ns, n):
                # Split string at all possible combinations of break
                # characters, and return a list of dicts with 'position' and
                # 'substring'
                yield [{'position': a[0], 'substring': a[1]} for a in enumerate([self.address_string[breaks[i] + 1:breaks[j]] for i, j in zip((0,) + indices, indices + (-1,))])]

    def preprocess(self):
        """Cleans up an input string prior to processing"""
        # Replace multiple spaces with single space
        processed = re.sub(r"\s+", " ", self.address_string)
        # Remove any spaces around ' / '
        processed = re.sub(r"\s+\/\s+", "/", processed)
        # Convert to lowercase and remove leading/trailing spaces
        self.address_string = processed.strip().lower()
