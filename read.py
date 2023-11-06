from entities.course import Course

def read_entry(path_file):

    try:
        with open(path_file, 'r') as file:
            
            #leitura do cabeçalho

            #Name
            file.readline()
            #Courses
            n_courses = int(file.readline().split()[-1])
            #Rooms
            n_rooms = int(file.readline().split()[-1])
            #Days
            n_days = int(file.readline().split()[-1])
            #Periods_per_day
            n_periods_per_day = int(file.readline().split()[-1]) 
            #Curricula
            n_curriculay = int(file.readline().split()[-1])
            #Constraints
            n_constraints = int(file.readline().split()[-1])
            
            #linha em branco
            file.readline()
            #COURSES
            file.readline()
            
            list_courses = []
            
            for i in range(0,n_courses):
                atributos = file.readline().split()
                list_courses.append(Course(atributos[0],atributos[1],atributos[2],atributos[3],atributos[4]))
                
            print(list_courses)
            print(n_courses)

            
         
    except FileNotFoundError:
        return "Arquivo não encontrado ou caminho inválido."

