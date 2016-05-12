try:
    import Levenshtein
    levenshtein_available = True
except:
    levenshtein_available = False
    print "Levenshtein module not found!!"


from address_part import *
from valid_localities import *


class LocalityPart(AddressPart):

    def name(self):
        return "locality"

    def check(self):
        self.cost = 0

        if self.test_string in valid_localities:
            return True

        # too slow!
        if False and levenshtein_available:
            for locality in valid_localities:
                if len(locality) > 8 and locality[:1] == self.test_string[:1] and float(Levenshtein.distance(locality, self.test_string)) / len(locality) <= .15:
                    self.cost = Levenshtein.distance(
                        locality, self.test_string) * 2
                    return True

        return False

    def score(self):
        # Localities aren't likely to be at the very start of an address string
        cost = 0
        if self.is_first():
            cost += 20

        return cost
