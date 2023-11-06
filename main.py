# Importando a função de leitura
from read import read_entry

def main():
    # Chamar a função ler_dados do outro arquivo
    caminho_do_arquivo = 'instancias/comp01.ctt'  # Substitua pelo caminho do seu arquivo
    read_entry(caminho_do_arquivo)
    
main()