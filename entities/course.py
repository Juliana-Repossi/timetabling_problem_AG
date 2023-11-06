class Course:

    def __init__(self, name, teacher, qtd_class_week, qtd_min_day, tam_students):
        self.name = name
        self.teacher = teacher
        self.qtd_class_week = qtd_class_week
        self.qtd_min_day = qtd_min_day
        self.tam_students = tam_students
        
    def __str__(self):
        return f"Nome: {self.name}"
    