import numpy as np

class Timetabling:

    def __init__(self,n_days,n_periods_per_day,n_curricula):
        
        #criar uma matriz tridimensional de:
            # linhas = periods per day
            # colunas = Days
            # profund = periodos(curricula)
         
        self.timetabling = np.empty((n_curricula,n_periods_per_day, n_days), dtype=object)
        self.performance =  float("inf")
        self.problem = None
        self.loc_problem = None

    def __str__(self):
        string_final = f'______________{self.performance}______________{self.problem}______________\n\n'
        (curricula,period,day) = self.timetabling.shape
        for i in range(curricula):
            for j in range(period):
                for k in range(day):
                    string_final += self.timetabling[i][j][k].__str__() + ' '
                string_final += '\n'
            string_final += " - - - - - - - - - - - - - - - - - - - \n"
        string_final += "_____________________________***__________________________________________\n\n\n"
        return string_final 
    
    def fitness_timetabling(self,matriz_inviab,violations):
        
        #avaliar cada ind da população
        (curricula,period,day) = self.timetabling.shape

        #setar os parametros
        self.performance = 0.0
        self.problem = None

        for j in range(0,period):
            for k in range(0,day):

                #hash de ocupação de salas
                hash_salas = {}
                hash_profs = {}

                for i in range(0,curricula):
                #percorrer em profundidade

                    if self.timetabling[i][j][k] is not None:
    
                        #avaliação de aptidão por restrições:

                        #FORTES --------------------------------------------------------

                        # H1 - alocação de aulas : garantida na inicialização
                        # H2 - ocupação de salas - verificação por hash
                        if  hash_salas.get((self.timetabling[i][j][k]).room.name) is not None:

                            #viola uma restrição forte de alocação de salas
                            # print('violou sala')
                            self.performance = float('inf')
                            violations.classroom +=1
                            self.problem = 0
                            self.loc_problem = (j,k)
                            return self.performance
                        else:
                            hash_salas[(self.timetabling[i][j][k]).room.name] = 1

                        #H3.1 -  Conflitos de professor
                        #H3.2 -  Conflitos de curriculo - já garantida pela modelagem tridimensional

                        if  hash_profs.get((self.timetabling[i][j][k]).course.teacher) is not None:
                            #viola uma restrição forte de alocação de professores
                            # print('violou prof')
                            self.performance = float('inf')
                            violations.prof +=1
                            self.problem = 1
                            self.loc_problem = (j,k)
                            return self.performance
                        else:
                            hash_profs[(self.timetabling[i][j][k]).course.teacher] = 1

                        #H4 -  Conflitos de disponibilidade
                        if  matriz_inviab[j][k].get((self.timetabling[i][j][k]).course.name) is not None:
                            #viola uma restrição forte de inviabilidades declaradas
                            self.performance = float('inf')
                            # print('violou inv')
                            violations.inviab +=1
                            self.problem = 2
                            self.loc_problem = (i,j,k)
                            return self.performance
                        
        #precisa ainda verificar as restrições fracas
        return self.performance 
                        
                        
