import math
import random
import numpy as np
from entities.timetabling import Timetabling
from entities.classtime import Classtime

class ImplAG:
      
    def __init__(self,tam_pop,percent_selection,prob_cross,prob_mut,tam_elit,max_iter,max_time):

        self.pops = []
        self.tam_pop = tam_pop

        self.tam_elit = tam_elit
        self.elit = []
        
        self.percent_selection = percent_selection

        self.prob_cross = prob_cross
        self.prob_mut = prob_mut
        
        self.real_iter = 0
        self.max_iter = max_iter

        self.real_time = 0
        self.max_time = max_time

        self.best_score = float('inf')
        self.best_timetabling = None
        self.graphic = []

    def inicializacao_aleatoria(self,n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula):
        
        #inicializa a população de forma paralela sem critérios
        for _ in range(self.tam_pop):
            individuo = Timetabling(n_days,n_periods_per_day,n_curricula)
            #cada indivíduo é uma tabela horário
            for n_curric in range(0,n_curricula):
                #para cada tabela horário dos períodos:
                #aloque todas as disciplinas daquele curriculo - 
                # Criar uma lista de todas as posições possíveis
                todas_posicoes = [(i, j) for i in range(n_periods_per_day) for j in range(n_days)]
                # sem preocupação com violar alguma condição
                for course in array_curricula[n_curric]:
                    #aloque todas as aulas daquela disciplina
                    for _ in range(0,course.qtd_class_week):
                        while True:
                            
                            linha,coluna = random.sample(todas_posicoes, 1)[0]
                                                
                            #se a janela de tempo estiver livre
                            if individuo.timetabling[n_curric][linha][coluna] == None :
                                room = list_rooms[np.random.randint(0,len(list_rooms)-1)]
                                individuo.timetabling[n_curric][linha][coluna] = Classtime(course,room)
                                break

            # print(individuo)
            self.pops.append(individuo)

    def inicializacao_min_harm(self,n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula,matriz_iviab):
        
        # inicializa a população de forma paralela min danos - com a alocação das 
        # matérias por ordem de dificuldade de alocação - definida na leitura dos dados
        # Essa alocação TENTARÁ não desrespeitar ou desrespeitar o min possível 
        # de alocações em dias inviáveis
        for _ in range(self.tam_pop):
            individuo = Timetabling(n_days,n_periods_per_day,n_curricula)
            #cada indivíduo é uma tabela horário
            for n_curric in range(0,n_curricula):
                #para cada tabela horário dos períodos:
                #aloque todas as disciplinas daquele curriculo - 
                # Criar uma lista de todas as posições possíveis
                todas_posicoes = [(i, j) for i in range(n_periods_per_day) for j in range(n_days)]
                room_curr = list_rooms
                # print(f'n curr:{n_curric}')
                for course in array_curricula[n_curric]:
                    todas_posicoes_curso = todas_posicoes
                    #escolher a sala
                    for sala in list_rooms:
                        room = sala
                        if sala.tam>= course.tam_students:
                            break
                    #aloque todas as aulas daquela disciplina - por ordem de dificuldade
                    for qtd in range(0,course.qtd_class_week):
                        # realizar uma qtd de tentativas de inserir em um lugar sem coflitos
                        while True:

                            #sorteia uma posição possivel de alocação
                            linha,coluna = random.sample(todas_posicoes_curso, 1)[0]

                            #verificar são as ultimas opções de alocação ou se é uma alocação sem indisponibilidade
                            if course.qtd_class_week-qtd == len(todas_posicoes_curso) or course not in matriz_iviab[linha][coluna]:
                                #alocar 
                                individuo.timetabling[n_curric][linha][coluna] = Classtime(course,room)
                                #retirar a posição da lista de possiveis
                                todas_posicoes.remove((linha,coluna))
                                break
                            
            # print(individuo)
            self.pops.append(individuo)
    
    def fitness_pop_timetabling(self,matriz_inviab,violations):
        
        for ind in self.pops:
            resul = ind.fitness_timetabling(matriz_inviab,violations)
            # print(f'resul: {resul}')
            # print(f'perfor: {ind.performance}')
            # print(f'violations: {violations}')

            if resul < self.best_score:
                self.best_score = resul
                self.best_timetabling = ind
        

        #adicionar o melhor da geração no gráfico
        self.graphic.append(self.best_score)

    def elitism_timetabling(self):
        self.elit = sorted(self.pops, key=lambda pop: pop.performance)[:self.tam_elit]
            
    def selection_tournament(self):

        tam = math.floor((self.percent_selection * self.tam_pop))
        pop_survivor = []

        while len(pop_survivor) < tam:

            # Escolhe-se n indivíduos aleatoriamente com mesma probabilidade
            individuos_escolhidos = random.choices(self.pops, k=5)
            #Pega o melhor e coloca na pop sobrevivente
            ind = sorted(individuos_escolhidos, key=lambda ind: ind.performance)[0]
            pop_survivor.append(ind)
            self.pops.remove(ind)
            
        self.pops = pop_survivor

    # Implementação de crossOver por troca de currículos entre horários
    def crossover_curricula(self,dad,mom):
        (curricula, period, day) = dad.timetabling.shape

        if(curricula < 2):
            return mom
        
        # Criar mascara para crossover uniforme a 50%
        mask = [0 if i < curricula//2 else 1 for i in range(curricula)]
        np.random.shuffle(mask)

        # Criar Tabelas-Horários vazias com as mesmas dimensões
        child = Timetabling(day,period,curricula)

        # Realizar o crossover na dimensão da profundidade
        for i in range(0,len(mask)):
            if mask[i]:
                #valor = 1 
                child.timetabling[i, :, :] = dad.timetabling[i, :, :]
            else:
                child.timetabling[i, :, :] = mom.timetabling[i, :, :]

        return child

    def crossover_pop(self):

        cross_pop_survivor = []
        
        #decisão de projeto - manter o tamanho da pop original
        while len(cross_pop_survivor) < self.tam_pop - self.tam_elit:
            rand = random.uniform(0, 1)
            #sorteando um lista de pesos para sofrer cross
            fst_ind = random.randint(0, len(self.pops) - 1)
            scd_ind = random.randint(0, len(self.pops) - 1)

            
            dad = self.pops[fst_ind] 
            mom = self.pops[scd_ind]

            if fst_ind != scd_ind and rand <= self.prob_cross:

                parent = self.crossover_curricula(dad, mom)
                cross_pop_survivor.append(parent)
            else:
                cross_pop_survivor.append(dad)
            
        self.pops = cross_pop_survivor
    
    def mutation_ind (self, ind):

        # a mutação foi pensada inicialmente para melhorar a qualidade da solução
            # trocando a sala alocada OU
            # trocando duas matérias
                #para retirar uma classtime de um bloco inviável OU 
                #para minimizar o conflito de prof
        # Porém a primeira implementação testada será a aleatória

        # Sortear duas posições
        (curricula, period, day) = ind.timetabling.shape

        i = random.randint(0, curricula-1)

        j1 = random.randint(0, period-1)
        k1 = random.randint(0, day-1)

        j2 = random.randint(0, period-1)
        k2 = random.randint(0, day-1)


        #primeira mutação mais simples possível -  troca de matérias
        mat = ind.timetabling[i][j1][k1]
        ind.timetabling[i][j1][k1] = ind.timetabling[i][j2][k2]
        ind.timetabling[i][j2][k2] = mat

        return ind
    
    def mutation_classroom(self, ind, list_rooms):

        #O conflito de sala pode acontecer se
            # em um dia e hora tem mais aulas que salas

                #Solução - Fazer (n de disciplinas naquele dia e hora - n de salas)
                # swaps com outras posições none do mesmo curriculo

            #Ou, mesmo tendo outras salas disp. uma esta alocada para duas aulas diferentes
                # Solução: Reorganizar salas
        
        (curricula, period, day) = ind.timetabling.shape
        
        if ind.loc_problem != None:
            #tem conflito de inviabilidade
            (j,k) = ind.loc_problem
            
            while  len(list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))) > len(list_rooms):
                # sorteia um curriculo
                i = random.randint(0, curricula-1)
                if ind.timetabling[i][j][k] is None:
                    # não tem materia nesse curriculo dia e hora
                    continue
                # tenta alocar em uma posição None daquele curriculo
                for p in range(0,period):
                    for d in range(0,day):
                        if ind.timetabling[i][p][d] is None:
                            #troca a posição None pela materia
                            ind.timetabling[i][p][d] = ind.timetabling[i][j][k]
                            ind.timetabling[i][j][k] = None
                            break
                    if ind.timetabling[i][j][k] is None:
                        break
        else:
            #sorteia posição
            j = random.randint(0, period-1)
            k = random.randint(0, day-1)

        lista_com_classtimes = list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))
        lista_com_classtimes.sort(key= lambda classtime: classtime.course.tam_students)
    
        # conflito do 2º tipo
        n_sala=0

        for i in range(0,len(lista_com_classtimes)):
            for classtime in ind.timetabling[ :,j,k]:
                if classtime is not None:
                    if lista_com_classtimes[i] == classtime:
                        while classtime.course.tam_students > list_rooms[n_sala].tam and len(list_rooms) - n_sala > len(lista_com_classtimes)-i:
                            n_sala +=1
                        classtime.room = list_rooms[n_sala]
                        n_sala +=1
                        break 

        return ind
    
    def mutation_inviab(self, ind,matriz_inviab):

        #violou uma condição de viabilidade
        (i,j,k) = ind.loc_problem

        (curricula, period, day) = ind.timetabling.shape

        #vai tentar colocar a mat em uma posição com none
        #caso não seja possível irá trocar com outra matéria

        mat_problem = ind.timetabling[i][j][k]
        mat_oport = (j,k)
        
        while mat_problem is not None:
            for p in range(0,period):
                for d in range(0,day):

                    if matriz_inviab[p][d].get(mat_problem.course.name) is None:
                        #pode ser alocada naquele slot

                        if ind.timetabling[i][p][d] is None:
                            #esta vazio -> aloca a matéria
                            #retira a mat do antigo lugar
                            ind.timetabling[i][j][k] = None
                            #novo lugar
                            ind.timetabling[i][p][d] = mat_problem
                            mat_problem = None
                            break                        
                        else:
                            # se está alocada - guarda a de menor dif de alocação
                            #para caso precise trocar
                            linha,coluna = mat_oport
                            if ind.timetabling[i][p][d].course.dificult < ind.timetabling[i][linha][coluna].course.dificult:
                                mat_oport = (p,d)
                if mat_problem is None:
                    break
            #percorreu todas as posições e não conseguiu alocar
            if mat_problem is not None:

                # troca a materia
                linha,coluna = mat_oport
                aux = ind.timetabling[i][linha][coluna]
                ind.timetabling[i][linha][coluna] = mat_problem
                mat_problem = aux
                ind.timetabling[i][j][k]  = None
        return ind
    
    def mutation_prof(self, ind):

        return ind

    def mutation_pop(self,list_rooms,matriz_inviab):

        pop_mutated = []

        for ind in self.pops:

            rand = random.uniform(0, 1)

            if rand <= self.prob_mut: 

                if ind.problem == 0:
                    pop_mutated.append(self.mutation_classroom(ind,list_rooms))
                elif ind.problem == 1:
                    pop_mutated.append(self.mutation_prof(ind))
                elif ind.problem == 2:
                    pop_mutated.append(self.mutation_inviab(ind,matriz_inviab))
                else:
                    #pode ter uma mutação para alterar performance
                    pop_mutated.append(ind)
            else:
                pop_mutated.append(ind)

        self.pops = pop_mutated
    
    def new_generation(self):

        self.pops += self.elit
        self.elit = []

    def check_convergence(self):

        ind_ref = self.pops[0]

        for ind in self.pops:
            if ind != ind_ref:
                return False
        print("CONVERGIU")
        print(f"score: {self.best_score}")
        print(f"time: {self.real_time}")
        print(f"iter: {self.real_iter}")
        print(self.best_timetabling)

        return True
            











   

        
        


        



            
        