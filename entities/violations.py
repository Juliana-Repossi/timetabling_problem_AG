
class Violations:

    def __init__(self):
        self.classroom = 0
        self.prof = 0
        self.inviab = 0
        self.manyClass = 0

    def __str__(self):
        return f"Class: {self.classroom}, ManyClass: {self.manyClass}, Prof: {self.prof}, Inviab: {self.inviab}"

    def reset_violations(self):
        self.inviab = 0
        self.classroom = 0
        self.prof = 0
        self.manyClass = 0
