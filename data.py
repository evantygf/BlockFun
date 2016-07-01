class Data:
    def __init__(self, id, metadata=None):
        self.id = id
        self.metadata = metadata
        if self.id == 9 and self.metadata == None:
            self.metadata = [None for i in range(5)]