import time

from read import read_entry
from AG.impl_ag import ImplAG
from entities.violations import Violations

def main():

    caminho_do_arquivo = 'instancias/comp11.ctt'  
    n_days,n_periods_per_day,n_curricula,list_rooms, array_curricula, matriz_inviab, hash_inv_mat= read_entry(caminho_do_arquivo)

    ############### Parâmetros do AG ###############
    AG = ImplAG(600,0.7,0.8,0.5,1,20000,192)

    ############### Inicialização da População ###############

    # Ideia 1: Inicialização aleatória - 1/3 do tamanho da pop
    AG.inicializacao_aleatoria(n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula)

    # Ideia 2: Inicialização com bons horários em um período(alguma inteligencia de minimização de danos)
    AG.inicializacao_min_harm(n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula,matriz_inviab,hash_inv_mat)

    # Ideia 3: Inicialização com horários viáveis globalmente - ideia inviável a priori

    ################### Execução do AG ###################

    #valores de iteração
    start = time.time()

    #Auxiliar para avaliação das violações
    violations = Violations()

    # while not AG.check_convergence() and AG.real_iter < AG.max_iter and AG.real_time-start <= AG.max_time:
    while AG.real_iter < AG.max_iter and AG.real_time-start <= AG.max_time:

        #avaliar toda a população
        AG.fitness_pop_timetabling(matriz_inviab,len(list_rooms),violations)

        # #aplicar elitismo - colocar uma qtd n de melhores resultados na prox geração
        AG.elitism_timetabling()

        #selecionar a população
        AG.selection_tournament()

        #aplicar nessa pop os operadores genéticos

        #crossover
        #de curriculos
        AG.crossover_pop()

        #de matérias
        AG.crossover_classtimes(len(list_rooms))
        
        #mutação
        AG.mutation_pop(list_rooms,matriz_inviab)
        
        #atualiza a população
        AG.new_generation()

        #incrementa contadores de parada
        AG.real_iter +=1
        AG.real_time = time.time()

    AG.best_solution()

  
main()      
