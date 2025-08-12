import sys
sys.stdout.reconfigure(encoding='utf-8')
import os

def listar_arquivos(caminho, prefixo=""):
    arquivos = os.listdir(caminho)
    arquivos.sort()
    for i, nome in enumerate(arquivos):
        caminho_completo = os.path.join(caminho, nome)
        marcador = "└── " if i == len(arquivos) - 1 else "├── "
        print(prefixo + marcador + nome)
        if os.path.isdir(caminho_completo):
            novo_prefixo = prefixo + ("    " if i == len(arquivos) - 1 else "│   ")
            listar_arquivos(caminho_completo, novo_prefixo)

if __name__ == "__main__":
    raiz = r"D:\sistema\BrenddaNordHaus"  # Caminho do seu projeto
    print(os.path.basename(raiz))
    listar_arquivos(raiz)
