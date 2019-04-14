class Pokemon:

    def __init__(self, id, has_item):

        self.id = id
        self.health = 100  # percentage of hp left
        self.typing = None  # use function to get typing
        self.status = None
        self.ability = None
        self.moves = None
        self.has_item = has_item
        # stat changes, values from -6 to 6
        self.stat_changes = {"atk": 0, "def": 0, "spatk": 0, "spdef": 0, "spe": 0, "acc": 0, "eva": 0}

    def print(self):
        print(self.id)