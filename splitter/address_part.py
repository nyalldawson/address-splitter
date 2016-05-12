def first_word(s):
    """Returns the first word in a string"""
    return s.split()[0]


def last_word(s):
    """Returns the last word in a string"""
    return s.split()[-1]


def remove_last_word(s):
    """Strips the last word from a string"""
    return s.rsplit(' ', 1)[0]


def remove_first_word(s):
    """Strips the first word from a string"""
    return s.split(' ', 1)[1]


class AddressPart:

    def __init__(self, part):
        self.part = part
        self.test_string = part.get_part()
        self.penalties = []

    def name(self):
        return ""

    def check(self):
        pass

    def score(self):
        return 0

    def breakdown(self):
        parts = {}
        return parts

    def is_first(self):
        return self.part.get_position() == 0

    def next_part(self):
        return self.part.next_part()

    def preceded_by(self, type):
        return isinstance(self.part.prev_part().get_type(), type)

    def followed_by(self, type):
        return isinstance(self.part.next_part().get_type(), type)

    def dupe_part_cost(self):
        return 50

    def get_penalties(self):
        return self.penalties
