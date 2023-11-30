import time

from read import read_entry
from AG.impl_ag import ImplAG
from entities.violations import Violations

def main():
    # Chamar a função ler_dados do outro arquivo
    caminho_do_arquivo = 'instancias/comp18.ctt'  
    n_days,n_periods_per_day,n_curricula,list_rooms, array_curricula, matriz_inviab = read_entry(caminho_do_arquivo)

    ############### Parâmetros do AG ###############
    AG = ImplAG(50,0.6,0.75,0.2,5,500,43200000)

    ############### Inicialização da População ###############

    # Ideia 1: Inicialização aleatória
    # AG.inicializacao_aleatoria(n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula)

    # Ideia 2: Inicialização com bons horários em um período(alguma inteligencia de minimização de danos)
    AG.inicializacao_min_harm(n_days,n_periods_per_day,n_curricula,list_rooms,array_curricula,matriz_inviab)

    # Ideia 3: Inicialização com horários viáveis globalmente - ideia inviável a priori

    ################### Execução do AG ###################

    #valores de iteração
    start = time.process_time()

    #Auxiliar para avaliação das violações
    violations = Violations()
    
    #while not conv and iter < self.max_iter and end-start <= self.time_max:
    while not AG.check_convergence() and AG.real_iter < AG.max_iter and AG.real_time-start <= AG.max_time:

        #zera as violações
        violations.reset_violations()

        #avaliar toda a população
        AG.fitness_pop_timetabling(matriz_inviab,violations)

        print(violations)
        print(AG.best_score)


        if AG.best_score == 0:
            print(f"time: {AG.real_time}")
            print(f"iter: {AG.real_iter}")
            print(AG.best_timetabling)
            break

        #aplicar elitismo - colocar uma qtd n de melhores resultados na prox geração
        AG.elitism_timetabling()
  
        #selecionar a população
        AG.selection_tournament()   

        #aplicar nessa pop os operadores genéticos

        #crossover
        AG.crossover_pop()

        #mutação
        AG.mutation_pop(list_rooms,matriz_inviab)

        #atualiza a população
        AG.new_generation()

        #incrementa contadores de parada
        AG.real_iter +=1
        AG.real_time = time.process_time()

  
main()      
