class Course:

    def __init__(self, name, teacher, qtd_class_week, qtd_min_day, tam_students):
        self.name = name
        self.teacher = teacher
        self.qtd_class_week = qtd_class_week
        self.qtd_min_day = qtd_min_day
        self.tam_students = tam_students
        self.dificult = 0.0
        
    def __str__(self):
        # return f"Nome: {self.name},Prof: {self.teacher},Qtd de aulas: {self.qtd_class_week},Qtd min de aulas: {self.qtd_min_day}, Qtd estudantes: {self.tam_students}, Dificuldade: {self.dificult}"
        # return f"{self.dificult}"
        return f"Nome: {self.name},Qtd estudantes: {self.tam_students}"
        #return self.name