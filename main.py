import time

from read import read_entry
from AG.impl_ag import ImplAG

def main():
    # Chamar a função ler_dados do outro arquivo
    caminho_do_arquivo = 'instancias/comp01.ctt'  
    n_days,n_periods_per_day,n_curricula,list_rooms, array_curricula, matriz_iviab = read_entry(caminho_do_arquivo)

    # teste de leitura - OK

    # print(f"n de dias:{n_days}")
    # print(f"n de periodos:{n_periods_per_day}")
    # print(f"n de periodos:{n_curricula}")
    # for room in list_rooms:
    #     print(room)
    # for curricula in array_curricula:
    #     for disc in curricula:
    #         print(disc)
    #     print()
    # linha - periodo - Coluna - Dia
    # for linha in matriz_iviab:
    #     for column in linha:
    #         print(column)
    #     print()

    ############### Parâmetros do AG ###############
    AG = ImplAG(50,0.6,0.75,0.4,2,10000000,43200000)

    ############### Inicialização da População ###############

    # Ideia 1: Inicialização aleatória
    AG.inicializacao_aleatoria(n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula)

    # Ideia 2: Inicialização com bons horários em um período(alguma inteligencia de minimização de danos)

    # Ideia 3: Inicialização com horários viáveis globalmente - ideia inviável a priori

    ################### Execução do AG ###################

    #valores de iteração
    start = time.process_time()

    #verificar a convergencia - adicionar convergencia no while
    
    #while not conv and iter < self.max_iter and end-start <= self.time_max:
    while AG.real_iter < AG.max_iter and AG.real_time-start <= AG.max_time:

        #avaliar toda a população
        AG.fitness_pop_timetabling(matriz_iviab)

        print(AG.best_score)

        if AG.best_score == 0:
            print(f"time: {AG.real_time}")
            print(f"iter: {AG.real_iter}")
            print(AG.best_timetabling)
            break

        #aplicar elitismo - colocar uma qtd n de melhores resultados na prox geração
        elit_pop = AG.elitism_timetabling()

        #selecionar a população
        pop_survivor = AG.selection_tournament()

        #aplicar nessa pop os operadores genéticos

        #crossover
        pop_survivor = AG.crossover_pop(pop_survivor)

        #mutação
        pop_survivor = AG.mutation_pop(pop_survivor)

        #atualiza a população
        AG.new_generation(elit_pop,pop_survivor)

        #incrementa contadores de parada
        AG.real_iter +=1
        AG.real_time = time.process_time()

  
main()      
