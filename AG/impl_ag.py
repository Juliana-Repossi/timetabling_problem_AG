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
    
    def fitness_pop_timetabling(self,matriz_iviab):
        
        for ind in self.pops:
            resul = ind.fitness_timetabling(matriz_iviab)

            if resul < self.best_score:
                self.best_score = resul
                self.best_timetabling = ind
        

        #adicionar o melhor da geração no gráfico
        self.graphic.append(self.best_score)

    def elitism_timetabling(self):
        return sorted(self.pops, key=lambda pop: pop.performance)[:self.tam_elit]
            
    def selection_tournament(self):

        tam = math.floor((self.percent_selection * self.tam_pop))
        pop_survivor = []

        while len(pop_survivor) < tam:

            # Escolhe-se n indivíduos aleatoriamente com mesma probabilidade
            individuos_escolhidos = random.sample(self.pops, 5)
            #Pega o melhor e coloca na pop sobrevivente
            pop_survivor.append(sorted(individuos_escolhidos, key=lambda ind: ind.performance)[0])
        return pop_survivor
    
    # Implementação de crossOver por troca de currículos entre horários
    def crossover_curricula(self,dad,mom):
        (curricula, period, day) = dad.timetabling.shape

        if(curricula < 2):
            return dad,mom
        
        if(curricula == 2):
            r = 1
        else:
            r = random.randint(1, curricula - 2)

        # Criar Tabelas-Horários vazias com as mesmas dimensões
        child1 = Timetabling(day,period,curricula)
        child2 = Timetabling(day,period,curricula)

        # Realizar o crossover na dimensão da profundidade
        child1.timetabling[:r, :, :] = dad.timetabling[:r, :, :]
        child1.timetabling[r:, :, :] = mom.timetabling[r:, :, :]

        child2.timetabling[:r, :, :] = mom.timetabling[:r, :, :]
        child2.timetabling[r:, :, :] = dad.timetabling[r:, :, :]

        return child1, child2

    def crossover_pop(self,pop_survivor):

        cross_pop_survivor = []
        
        for _ in range (round(len(pop_survivor)/2)):
            rand = random.uniform(0, 1)
            #sorteando um lista de pesos para sofrer cross
            fst_ind = random.randint(0, len(pop_survivor) - 1)
            scd_ind = random.randint(0, len(pop_survivor) - 1)

            
            parent1 = pop_survivor[fst_ind] 
            parent2 = pop_survivor[scd_ind]

            if fst_ind != scd_ind and rand <= self.prob_cross:

                parent1, parent2 = self.crossover_curricula(parent1, parent2)            
        
            cross_pop_survivor.append(parent1)
            cross_pop_survivor.append(parent2)
            
        return cross_pop_survivor
    
    def mutation_ind (self, ind):

        # a mutação foi pensada inicialmente para melhorar a qualidade da solução
            # trocando a sala alocada OU
            # trocando duas matérias
                #para retirar uma classtime de um bloco inviável OU 
                #para minimizar o conflito de prof
        # Porém a primeira implementação testada será a aleatória

        # Sortear uma posição
        (curricula, period, day) = ind.timetabling.shape

        i = random.randint(0, curricula-1)

        j1 = random.randint(0, period-1)
        k1 = random.randint(0, day-1)

        j2 = random.randint(0, period-1)
        k2 = random.randint(0, day-1)

        r = random.uniform(0,1)
        
        if r<= self.prob_mut:

            #primeira mutação mais simples possível -  troca de matérias
            mat = ind.timetabling[i][j1][k1]
            ind.timetabling[i][j1][k1] = ind.timetabling[i][j2][k2]
            ind.timetabling[i][j2][k2] = mat

        return ind
    

    def mutation_pop(self,pop_survivor):

        position = 0
        for ind in pop_survivor:
            rand = random.uniform(0, 1)

            if rand <= self.prob_mut:
                mutated = self.mutation_ind(ind)
                pop_survivor[position] = mutated
                    
            position+=1
        return pop_survivor  
    
    def new_generation(self,elit_pop, pop_survivor):

        self.pops = pop_survivor + elit_pop












   

        
        


        



            
        