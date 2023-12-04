import numpy as np
import entities.violations as Violations

class Timetabling:

    def __init__(self,n_days,n_periods_per_day,n_curricula):
        
        #criar uma matriz tridimensional de:
            # linhas = periods per day
            # colunas = Days
            # profund = periodos(curricula)
         
        self.timetabling = np.empty((n_curricula,n_periods_per_day, n_days), dtype=object)
        self.performance =  float("inf")
        self.total_problem = float("inf")

    def copy(self):
        
        (curricula, period, day) = self.timetabling.shape
        cop_timetabling = Timetabling(day,period,curricula)

        # copiar a tabela horário
        for i in range(0,curricula):
            for j in range(0,period):
                for k in range(0,day):
                    if self.timetabling[i][j][k] is None:
                        cop_timetabling.timetabling[i][j][k] = None
                    else:
                        cop_timetabling.timetabling[i][j][k] = self.timetabling[i][j][k].copy()


        cop_timetabling.performance =  self.performance
        cop_timetabling.total_problem = self.total_problem

        return cop_timetabling
    
    def crossover_timetabling(self,mask,dad):

        (curricula, period, day) = self.timetabling.shape
        child = Timetabling(day,period,curricula)

        # copiar a tabela horário
        for i in range(0,curricula):
            if mask[i] == 1:
                ref = dad
            else:
                ref = self

            for j in range(0,period):
                for k in range(0,day):
            
                    if ref.timetabling[i][j][k] is None:
                        child.timetabling[i][j][k] = None
                    else:
                        child.timetabling[i][j][k] = ref.timetabling[i][j][k].copy()

        return child

    def __str__(self):
        string_final = f'______________{self.performance}____________________________\n\n'
        (curricula,period,day) = self.timetabling.shape
        for i in range(curricula):
            for j in range(period):
                for k in range(day):
                    string_final += self.timetabling[i][j][k].__str__() + ' '
                string_final += '\n'
            string_final += " - - - - - - - - - - - - - - - - - - - \n"
        string_final += "_____________________________***__________________________________________\n\n\n"
        return string_final 
    
    def fitness_timetabling(self,matriz_inviab,qtd_salas,violations):
        
        #avaliar cada ind da população
        (curricula,period,day) = self.timetabling.shape

        #setar os parametros
        self.performance = 0.0
        self.total_problem = 0

        inv = 0
        prof = 0
        classroom = 0
        manyClass = 0
        
        for j in range(0,period):
            for k in range(0,day):

                #hash de ocupação de salas
                hash_salas = {}
                hash_profs = {}
                
                # se essa coluna tiver mais matérias que salas já esta violando
                if len(list(filter(lambda x: x is not None, self.timetabling[ :,j,k]))) > qtd_salas:
                    self.performance += float('inf')
                    manyClass +=1
                
                for i in range(0,curricula):
                #percorrer em profundidade

                    if self.timetabling[i][j][k] is not None:
    
                        #avaliação de aptidão por restrições:

                        #FORTES --------------------------------------------------------

                        # H1 - alocação de aulas : garantida na inicialização
                        # H2 - ocupação de salas - verificação por hash
                        if  hash_salas.get((self.timetabling[i][j][k]).room.name) is not None :

                            #viola uma restrição forte de alocação de salas - mesmo tendo menos matérias que qtd de salas
                            self.performance += float('inf')
                            classroom +=1

                        else:
                            hash_salas[(self.timetabling[i][j][k]).room.name] = 1

                        #H3.1 -  Conflitos de professor
                        #H3.2 -  Conflitos de curriculo - já garantida pela modelagem tridimensional

                        if  hash_profs.get((self.timetabling[i][j][k]).course.teacher) is not None :
                            #viola uma restrição forte de alocação de professores
                            #viola uma restrição forte de alocação de salas
                            self.performance += float('inf')
                            prof += 1
                        else:
                            hash_profs[(self.timetabling[i][j][k]).course.teacher] = 1

                        #H4 -  Conflitos de disponibilidade
                        if  matriz_inviab[j][k].get((self.timetabling[i][j][k]).course.name) is not None:
                            #viola uma restrição forte de inviabilidades declaradas
                            self.performance += float('inf')
                            inv +=1
                

        self.total_problem = inv + prof + classroom + manyClass

        if violations != None:
            violations.manyClass += manyClass
            violations.classroom += classroom
            violations.prof += prof
            violations.inviab += inv

            # print(f"Rest(manyClass,classroom,prof,inv) : {manyClass},{classroom},{prof},{inv} = {manyClass+classroom+prof+inv}")

        else:
            if manyClass == max(manyClass,classroom,prof,inv):
                return 1
            elif classroom == max(manyClass,classroom,prof,inv):
                return 2
            elif prof == max(manyClass,classroom,prof,inv):
                return 3
            elif inv == max(manyClass,classroom,prof,inv):
                return 4

        #precisa ainda verificar as restrições fracas
        return self.performance
                        
                      
    