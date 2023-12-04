import math
import random
import time
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
        self.min_violations = float('inf')
        self.graphic = []

    def inicializacao_aleatoria(self,n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula):
        
        #inicializa a população de forma paralela sem critérios
        for _ in range(round(self.tam_pop/2)):
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

    def inicializacao_min_harm(self,n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula,matriz_iviab,hash_inv_mat):
        
        # inicializa a população de forma paralela min danos - com a alocação das 
        # matérias por ordem de dificuldade de alocação - definida na leitura dos dados
        # Essa alocação TENTARÁ não desrespeitar ou desrespeitar o min possível 
        # de alocações em dias inviáveis
        for _ in range(round(self.tam_pop)):
            individuo = Timetabling(n_days,n_periods_per_day,n_curricula)
            #cada indivíduo é uma tabela horário
            for n_curric in range(0,n_curricula):
                #para cada tabela horário dos períodos:
                #aloque todas as disciplinas daquele curriculo - 
                # Criar uma lista de todas as posições possíveis
                todas_posicoes = [(i, j) for i in range(n_periods_per_day) for j in range(n_days)]
                
                for course in array_curricula[n_curric]:                   
                    if course.name in hash_inv_mat:
                        todas_posicoes_curso = list(filter(lambda item: item not in hash_inv_mat[course.name], todas_posicoes))
                    else:
                        todas_posicoes_curso = []

                    #escolher a sala (aleatória tem melhor perf)
                    sala = random.choice(list_rooms)

                    # causa mt conflito de sala
                    # for sala in list_rooms:
                    #     if sala.tam>= course.tam_students:
                    #         break

                    #aloque todas as aulas daquela disciplina - por ordem de dificuldade
                 
                    for _ in range(0,course.qtd_class_week):

                        #pode ser que não há locais fora da lista de inv para inserir a mat ou
                        # que aquela mat não tem restrições
                        if len(todas_posicoes_curso) == 0:
                            #sortear da lista geral
                            linha,coluna = random.choice(todas_posicoes)
                            todas_posicoes.remove((linha,coluna))
                    
                        else:
                            #sortear da lista que não vai gerar inviab
                            linha,coluna = random.choice(todas_posicoes_curso)
                            todas_posicoes_curso.remove((linha,coluna))
                            todas_posicoes.remove((linha,coluna))
                        #alocar 
                        individuo.timetabling[n_curric][linha][coluna] = Classtime(course,sala)
                            
            self.pops.append(individuo)
    
    def fitness_pop_timetabling(self,matriz_inviab,qtd_salas,violations):

        violations.reset_violations()
        
        for ind in self.pops:
            resul = ind.fitness_timetabling(matriz_inviab,qtd_salas,violations)

            if resul == 0:
                # encontrou a solução ótima
                self.best_score = resul
                self.best_timetabling = ind
                self.best_solution()

            if ind.total_problem <= self.min_violations:
                self.best_score = resul
                self.min_violations = ind.total_problem
                self.best_timetabling = ind

        # print(f"Violações: {violations}")
        # print(self.best_score)

        #adicionar o melhor da geração no gráfico
        self.graphic.append(self.best_score)

    def elitism_timetabling(self):

        list_elit = sorted(self.pops, key=lambda pop: pop.total_problem)[:self.tam_elit]

        for ind in list_elit:
           self.elit.append(ind.copy())
        
        print(f"Melhor: {self.elit[0].total_problem}")
            
    def selection_tournament(self):

        tam = math.floor((self.percent_selection * self.tam_pop))
        pop_survivor = []

        while len(pop_survivor) < tam:

            # Escolhe-se n indivíduos aleatoriamente com mesma probabilidade
            individuos_escolhidos = random.sample(self.pops,5)
            #Pega o melhor e coloca na pop sobrevivente
            ind = sorted(individuos_escolhidos, key=lambda ind: ind.total_problem)[0]
            pop_survivor.append(ind.copy())
            
        self.pops = pop_survivor

    # Implementação de crossOver por troca de currículos entre horários
    def crossover_curricula_uniform(self,dad,mom):

        (curricula, period, day) = dad.timetabling.shape

        if(curricula < 2):
            return mom.copy()
        
        # Criar mascara para crossover uniforme 
        mask = [0 if i%2 == 0 else 1 for i in range(0,curricula)]
        np.random.shuffle(mask)


        # realizar o cruzamento segundo a mascara
        return mom.crossover_timetabling(mask,dad)
    
    def crossover_pop(self):

        cross_pop_survivor = []
        
        #decisão de projeto - manter o tamanho da pop original
        while len(cross_pop_survivor) < self.tam_pop - self.tam_elit:
            rand = random.uniform(0, 1)

            while True:
                #sorteando um lista de pesos para sofrer cross
                fst_ind = random.randint(0, len(self.pops) - 1)
                scd_ind = random.randint(0, len(self.pops) - 1)
            
                dad = self.pops[fst_ind] 
                mom = self.pops[scd_ind]

                if fst_ind != scd_ind :
                    break            

            if rand <= self.prob_cross:
                child = self.crossover_curricula_uniform(dad, mom)
                cross_pop_survivor.append(child)

            else:
                cross_pop_survivor.append(mom.copy())      

            
        self.pops = cross_pop_survivor

    def crossover_classtimes(self, qtd_rooms):

        # a ideia é fazer um crossover entre coluna mais cheia e a mais vazia
        cross_pop_survivor = []
        
        for ind in self.pops:

            rand = random.uniform(0, 1)
            ind_copy = ind.copy()

            if rand <= self.prob_cross:

                #realizar o cross
                (curricula, period, day) = ind_copy.timetabling.shape

                qtd_colunas = []

                for j in range(0,period):
                    for k in range(0,day):
                        qtd_colunas.append((j,k,len(list(filter(lambda x: x is not None, ind_copy.timetabling[ :,j,k])))))

                menor = sorted(qtd_colunas, key=lambda tupla: tupla[2])[0]
                maior = sorted(qtd_colunas, key=lambda tupla: tupla[2],reverse=True)[0]

                value_maior = maior[2]
                value_menor = menor[2]

                if value_maior > qtd_rooms and value_menor < qtd_rooms:
                    
                    for i in range(0,curricula):

                        # faz o cross dos dois 
                        if ind_copy.timetabling[i][menor[0]][menor[1]] is None and ind_copy.timetabling[i][maior[0]][maior[1]] is not None:
                            #slot vazio
                            
                            ind_copy.timetabling[i][menor[0]][menor[1]] = ind_copy.timetabling[i][maior[0]][maior[1]]
                            ind_copy.timetabling[i][maior[0]][maior[1]] = None
                            value_menor +=1
                            value_maior -=1

                        if value_maior <= qtd_rooms or value_menor == qtd_rooms:
                            break  
    
            cross_pop_survivor.append(ind_copy)
        
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
    
    def mutation_many_class(self, ind, list_rooms,matriz_inviab):
        #O conflito de sala pode acontecer se em um dia e hora tem mais aulas 
        # que salas

        #Solução - Fazer (n de disciplinas naquele dia e hora - n de salas
        # swaps com outras posições none do mesmo curriculo

        (curricula, period, day) = ind.timetabling.shape
    
        for j in range(0,period):
            for k in range(0,day):                
                if len(list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))) > len(list_rooms):

                    i=0
                
                    #enquanto tiver mais disc que salas e ainda tiver profundidade - tenta trocar
                    while len(list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))) > len(list_rooms) and i<curricula :

                        if ind.timetabling[i][j][k] is None:
                            # não tem materia nesse curriculo dia e hora
                            i+=1
                            continue
                        # tenta alocar em uma posição None daquele curriculo ou fazer uma troca de mat
                        for p in range(0,period):
                            for d in range(0,day):
                                if ind.timetabling[i][p][d] is None:
                                    #verificar se essa troca não vai invibilizar aquela coluna
                                    if self._checks_allocation(ind,ind.timetabling[i][j][k],i,p,d,curricula,len(list_rooms),matriz_inviab):
                                        #troca a posição None pela materia
                                        ind.timetabling[i][p][d] = ind.timetabling[i][j][k].copy()
                                        ind.timetabling[i][j][k] = None
                                        break   

                            if ind.timetabling[i][j][k] is None:
                                break
                        i+=1

                    if len(list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))) <= len(list_rooms):
                        # acertou em no min uma coluna
                        return ind
        return ind
    
    def mutation_classroom(self, ind, list_rooms,matriz_inviab):

        #O conflito de sala pode acontecer se mesmo tendo outras salas disp. 
        # uma esta alocada para duas aulas diferentes
        # Solução: Reorganizar salas
        
        (curricula, period, day) = ind.timetabling.shape

        for j in range(0,period):
            for k in range(0,day):
                if len(list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))) <= len(list_rooms):

                    lista_com_classtimes = list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))
                    lista_com_classtimes.sort(key= lambda classtime: classtime.course.tam_students)
                
                    n_sala=-1
                    falta_loc = len(lista_com_classtimes)

                    for classtime in lista_com_classtimes:
                        n_sala +=1
                        while classtime.course.tam_students > list_rooms[n_sala].tam and len(list_rooms) - n_sala > falta_loc:
                            n_sala +=1
                        classtime.room = list_rooms[n_sala]
                        falta_loc -=1
                         

        return ind
    
    #verifica se alocar aquela matéria nas posições i,j,k gerará um conflito grave
    def _checks_allocation(self,ind,mat,i,j,k,n_curricula,n_classrooms,matriz_inviab):

        # verificar se estoura a qtd de aulas por dia x periodo
        if len(list(filter(lambda x: x is not None, ind.timetabling[ :,j,k]))) > n_classrooms-1 :
            return False

        #verificar se esse slot não tem restrição para essa mat
        if matriz_inviab[j][k].get(mat.course.name) is not None:
            return False
        
        # verificar se já há um professor dando essa aula nessa coluna
        for curr in range(0,n_curricula):
            if ind.timetabling[curr][j][k] is not None and  ind.timetabling[curr][j][k].course.teacher == mat.course.teacher:
                return False
            
        return True
    
    def mutation_inviab(self, ind,list_rooms,matriz_inviab):

        (curricula, period, day) = ind.timetabling.shape

        for i in range(0,curricula):
            for j in range(0,period):
                for k in range(0,day):

                    break_for = False

                    if  ind.timetabling[i][j][k] is None:
                        continue

                    if  matriz_inviab[j][k].get((ind.timetabling[i][j][k]).course.name) is not None:

                        #viola uma condição - tentar trocar

                        for p in range(0,period):
                            for d in range(0,day):
                            # verificar se pode colocar a mat conflitante nesse slot
                                
                                if self._checks_allocation(ind,ind.timetabling[i][j][k],i,p,d,curricula,len(list_rooms),matriz_inviab):
                                    # se o slot estiver vazio
                                    if ind.timetabling[i][p][d] is None:
                                        #troca a posição None pela materia (MOVE)
                                        ind.timetabling[i][p][d] = ind.timetabling[i][j][k].copy()
                                        ind.timetabling[i][j][k] = None
                                        break_for = True
                                        break
                                    
                                    else:
                                        # há uma matéria - verifica se (SWAP) é possível
                                        if self._checks_allocation(ind,ind.timetabling[i][p][d],i,j,k,curricula,len(list_rooms),matriz_inviab):
                                            mat = ind.timetabling[i][p][d].copy()
                                            ind.timetabling[i][p][d] = ind.timetabling[i][j][k].copy()
                                            ind.timetabling[i][j][k] = mat
                                            break_for = True
                                            break
                            if break_for:
                                break_for = False
                                break
        
        return ind
    
    def mutation_prof(self, ind,list_rooms,matriz_inviab):

        (curricula, period, day) = ind.timetabling.shape
        
        for j in range(0,period):
            for k in range(0,day):

                # dicionário para identificar conf de prof
                conf_prof = {}
                break_for = False

                for i in range(0,curricula):

                    if  ind.timetabling[i][j][k] is None:
                        continue
                    if conf_prof.get((ind.timetabling[i][j][k]).course.teacher) is None:
                        #primeira ocorrencia do prof
                        conf_prof[(ind.timetabling[i][j][k]).course.teacher] = 1
                    else:
                        conf_prof[(ind.timetabling[i][j][k]).course.teacher] +=1
                
                for i in range(0,curricula):
                    if ind.timetabling[i][j][k] is None:
                        continue
                    if conf_prof.get((ind.timetabling[i][j][k]).course.teacher) is not None and conf_prof.get((ind.timetabling[i][j][k]).course.teacher) > 1:
                        # está na lista - tentar alterar posição
                        for p in range(0,period):
                            for d in range(0,day):
                                # verificar se pode colocar a mat conflitante nesse slot
                                if self._checks_allocation(ind,ind.timetabling[i][j][k],i,p,d,curricula,len(list_rooms),matriz_inviab):
                                    # se o slot estiver vazio
                                    if ind.timetabling[i][p][d] is None:
                                        #troca a posição None pela materia (MOVE)
                                        ind.timetabling[i][p][d] = ind.timetabling[i][j][k].copy()
                                        ind.timetabling[i][j][k] = None
                                        conf_prof[(ind.timetabling[i][p][d]).course.teacher] -=1
                                        break_for = True
                                        break  
                                    else:
                                        # há uma matéria - verifica se (SWAP) é possível
                                        if self._checks_allocation(ind,ind.timetabling[i][p][d],i,j,k,curricula,len(list_rooms),matriz_inviab):
                                            mat = ind.timetabling[i][p][d].copy()
                                            ind.timetabling[i][p][d] = ind.timetabling[i][j][k].copy()
                                            ind.timetabling[i][j][k] = mat
                                            conf_prof[(ind.timetabling[i][p][d]).course.teacher] -=1
                                            break_for = True
                                            break         
                            if break_for:
                                break_for = False
                                break
        return ind
    
    def mutation_pop(self,list_rooms,matriz_inviab):

        pop_mutated = []

        for ind in self.pops:

            rand = random.uniform(0, 1)
            ind_copy = ind.copy()

            if rand <= self.prob_mut:
                                
                ind_copy = self.mutation_many_class(ind,list_rooms,matriz_inviab)
                
                ind_copy = self.mutation_classroom(ind,list_rooms,matriz_inviab)
                
                ind_copy = self.mutation_prof(ind,list_rooms,matriz_inviab)
                
                ind_copy = self.mutation_inviab(ind,list_rooms,matriz_inviab)
            
            pop_mutated.append(ind_copy)

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
    
    def best_solution(self):
        print("FIM: Melhor Solução Encontrada:")
        self.real_time = time.time()
        print(f"time: {self.real_time}")
        print(f"iter: {self.real_iter}")
        print(f"custo: {self.best_score}")
        print(self.best_timetabling)
        exit(0)
         