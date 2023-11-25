import numpy as np
from entities.classtime import Classtime

class Timetabling:

    def __init__(self,n_days,n_periods_per_day,n_curricula):
        
        #criar uma matriz tridimensional de:
            # linhas = periods per day
            # colunas = Days
            # profund = periodos(curricula)
         
        self.timetabling = np.empty((n_curricula,n_periods_per_day, n_days), dtype=object)
        self.performance =  float("inf")

    def __str__(self):
        string_final = f'__________________________{self.performance}__________________________\n\n'
        (curricula,period,day) = self.timetabling.shape
        for i in range(curricula):
            for j in range(period):
                for k in range(day):
                    string_final += self.timetabling[i][j][k].__str__() + ' '
                string_final += '\n'
            string_final += " - - - - - - - - - - - - - - - - - - - \n"
        string_final += "_____________________________***__________________________________________\n\n\n"
        return string_final 
    
    def fitness_timetabling(self,matriz_iviab):
        
        #avaliar cada ind da população
        (curricula,period,day) = self.timetabling.shape

        for j in range(period):
            for k in range(day):

                #hash de ocupação de salas
                hash_salas = {}
                hash_profs = {}

                for i in range(curricula):
                #percorrer em profundidade

                    if self.timetabling[i][j][k] is not None:
    
                        #avaliação de aptidão por restrições:

                        #FORTES --------------------------------------------------------

                        # H1 - alocação de aulas : garantida na inicialização
                        # H2 - ocupação de salas - verificação por hash
                        if  hash_salas.get((self.timetabling[i][j][k]).room) is not None:

                            #viola uma restrição forte de alocação de salas
                            self.performance = float('inf')
                            return self.performance
                        else:
                            hash_salas[(self.timetabling[i][j][k]).room] = 1

                        #H3.1 -  Conflitos de professor
                        #H3.2 -  Conflitos de curriculo - já garantida pela modelagem tridimensional

                        if  hash_profs.get((self.timetabling[i][j][k]).course.teacher) is not None:
                            #viola uma restrição forte de alocação de professores
                            self.performance = float('inf')
                            return self.performance
                        else:
                            hash_profs[(self.timetabling[i][j][k]).course.teacher] = 1

                        #H4 -  Conflitos de disponibilidade
                        if  matriz_iviab[j][k].get((self.timetabling[i][j][k]).course.name) is not None:
                            #viola uma restrição forte de inviabilidades declaradas
                            self.performance = float('inf')
                            return self.performance
                        
        #precisa ainda verificar as restrições fracas
        return 0 
                        
                        
