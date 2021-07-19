class Country:
    def __init__(self, title):
        self.title = title
        self.data = dict()

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title
