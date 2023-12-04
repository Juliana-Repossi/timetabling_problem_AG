from entities.course import Course
from entities.room import Room

def read_entry(path_file):

    CONSTANT_DIFICULDADE_QTD_AULAS = 10
    CONSTANT_DIFICULDADE_INVIAB = 20
    # CONSTANT_DIFICULDADE_PROF = 20
    # CONSTANT_DIFICULDADE_QTD_AULAS_MIN = 1

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
            n_curricula = int(file.readline().split()[-1])
            #Constraints
            n_constraints = int(file.readline().split()[-1])
            
            #linha em branco
            file.readline()
            #COURSES
            file.readline()
            
            #tabela hash para garantir agilidade
            hash_courses = {}

            #tabela hash para calcular a sobrecarga de um prof
                #Quanto mais matérias um prof leciona - a tendencia é que 
                #mais dificil será alocá-la
            # hash_prof = {}
            
            for i in range(0,n_courses):
                atributos = file.readline().split()
                course = Course(atributos[0],atributos[1],int(atributos[2]),int(atributos[3]),int(atributos[4]))
                hash_courses[atributos[0]] = (course)
                #para calcular o coeficiente de dificuldade de alocar um Course:
                
                #dificuldade relativa a qtd de aulas na semana (0-1)
                course.dificult += CONSTANT_DIFICULDADE_QTD_AULAS*(int(atributos[2])/n_days)
                #dificuldade relativa a qtd de aulas minimas na semana
                # course.dificult += CONSTANT_DIFICULDADE_QTD_AULAS_MIN*(int(atributos[3])/int(atributos[2]))

                # if atributos[1] in hash_prof:
                #     hash_prof[atributos[1]] +=1
                # else:
                #     hash_prof[atributos[1]] = 1 

            #linha em branco
            file.readline()
            #ROOMS
            file.readline()

            #lista de salas ordenada
            list_rooms = []
            
            for i in range(0,n_rooms):
                atributos = file.readline().split()
                list_rooms.append(Room(atributos[0],int(atributos[1])))
            
            list_rooms.sort(key=lambda room: room.tam)

            #linha em branco
            file.readline()
            #CURRICULA
            file.readline()

            #lista de periodos com as disciplinas
            array_curricula = [[] for _ in range(n_curricula)]


            for i in range(0,n_curricula):
                atributos = file.readline().split()
                for j in range(0, int(atributos[1])):
                    array_curricula[i].append(hash_courses[atributos[j+2]])
            
            #linha em branco
            file.readline()
            #UNAVAILABILITY_CONSTRAINTS
            file.readline()

            #matriz de inviabilidades ( linhas são periodos - colunas são os dias)
            matriz_iviab = [[{} for _ in range(n_days)] for _ in range(n_periods_per_day)]
            #cada célula é um hash de inviabilidades de 0 e 1

            #tabela hash para calcular as inviabilidades de uma discp
            hash_inv = {}
            hash_inv_mat = {}

            for i in range(0,n_constraints):
                atributos = file.readline().split()
                matriz_iviab[int(atributos[2])][int(atributos[1])][atributos[0]] = 1
                if atributos[0] not in hash_inv_mat:
                    hash_inv_mat[atributos[0]] = []
                hash_inv_mat[atributos[0]].append((int(atributos[2]),int(atributos[1])))
                if atributos[0] in hash_inv:
                    hash_inv[atributos[0]] +=1
                else:
                    hash_inv[atributos[0]] = 1

            for period in range(0,n_curricula):
                for course in array_curricula[period]:
                    #dificuldade relativa a qtd de inviabilidades
                    if course.name in hash_inv:
                        course.dificult += CONSTANT_DIFICULDADE_INVIAB*(hash_inv[course.name]/n_days*n_periods_per_day)
                    #dificuldade relativa a qtd de professores
                    # course.dificult += CONSTANT_DIFICULDADE_PROF*(hash_prof[course.teacher]/n_courses)
            
            for period in range(0,n_curricula):
                array_curricula[period].sort(key=lambda course: course.dificult, reverse=True)

            return n_days,n_periods_per_day,n_curricula,list_rooms, array_curricula, matriz_iviab, hash_inv_mat

    except FileNotFoundError:
        return "Arquivo não encontrado ou caminho inválido."

