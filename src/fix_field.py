class FIXField:
    def __init__(self, number, name, type, values=None):
        self.number = number
        self.name = name
        self.type = type
        self.values = values if values else []