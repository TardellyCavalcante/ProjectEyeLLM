import os
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from PIL import Image

# Função para listar arquivos JSON na raiz da pasta 'dados/'
def listar_arquivos_json(pasta_dados):
    """
    Lista todos os arquivos JSON diretamente na raiz da pasta especificada.
    """
    return [f for f in os.listdir(pasta_dados) if f.endswith('.json') and os.path.isfile(os.path.join(pasta_dados, f))]

# Função para carregar e interpretar um arquivo JSON
def carregar_dados_json(caminho_arquivo):
    """
    Carrega e interpreta um arquivo JSON.
    Retorna os dados carregados ou None em caso de erro.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

# Função para processar os dados do JSON
def processar_dados(dados):
    """
    Processa os dados de um arquivo JSON.
    Retorna os campos relevantes: nome da imagem, participante, bbox, fixações (X, Y, T).
    """
    try:
        nome_imagem = dados["name"]
        participante = dados["subject"]
        task = dados["task"]
        bbox = dados["bbox"]  # [x, y, largura, altura]
        fixacoes_x = dados["X"]
        fixacoes_y = dados["Y"]
        tempos = dados["T"]

        # Verificar consistência dos tamanhos de X, Y e T
        if not (len(fixacoes_x) == len(fixacoes_y) == len(tempos)):
            raise ValueError("Tamanhos inconsistentes entre X, Y e T.")

        return nome_imagem, participante, task, bbox, fixacoes_x, fixacoes_y, tempos
    except KeyError as e:
        print(f"Erro ao processar os dados: chave ausente {e}")
        return None, None, None, None, None, None, None
    except ValueError as e:
        print(f"Erro nos dados: {e}")
        return None, None, None, None, None, None, None

# Função para gerar o gráfico de fixações
def gerar_grafico_fixacoes(imagem_path, bbox, fixacoes_x, fixacoes_y, tempos, participante, nome_imagem, pasta_saida):
    """
    Gera um gráfico com a imagem de fundo, a bounding box, as fixações sobrepostas e setas indicando a cronologia.
    Adiciona um círculo verde na posição (0, 0) com tamanho 50.
    """
    try:
        # Carregar a imagem de fundo
        img = Image.open(imagem_path)
        plt.figure(figsize=(10, 8))
        plt.imshow(img)
        plt.axis('off')

        # Desenhar a bounding box
        bbox_x, bbox_y, bbox_largura, bbox_altura = bbox
        plt.gca().add_patch(Rectangle((bbox_x, bbox_y), bbox_largura, bbox_altura,
                                      edgecolor='blue', facecolor='none', linewidth=2, label='Bounding Box'))

        # Sobrepor as fixações e adicionar setas
        for i, (x, y, t) in enumerate(zip(fixacoes_x, fixacoes_y, tempos)):
            # Desenhar a fixação como um círculo com maior transparência
            plt.gca().add_patch(Circle((x, y), radius=t * 0.3, color='red', alpha=0.4))  # Transparência aumentada
            plt.text(x, y, str(i + 1), color='white', fontsize=10, ha='center', va='center')  # Numerar as fixações

            # Adicionar uma seta para a próxima fixação
            if i < len(fixacoes_x) - 1:  # Se não for a última fixação
                plt.arrow(x, y, fixacoes_x[i + 1] - x, fixacoes_y[i + 1] - y,
                          color='yellow', width=2, head_width=10, head_length=15, length_includes_head=True,
                          alpha=0.8)  # Setas com transparência

        # Adicionar um círculo verde na posição (0, 0) com tamanho 50
        plt.gca().add_patch(Circle((0, 0), radius=50, color='green', alpha=0.6, label='Ponto (0, 0)'))

        # Adicionar título
        plt.title(f"Participante: {participante} – Imagem: {nome_imagem}")

        # Salvar o gráfico na pasta de saída
        os.makedirs(pasta_saida, exist_ok=True)
        caminho_saida = os.path.join(pasta_saida, f"{participante}_{nome_imagem}.png")
        plt.savefig(caminho_saida)
        plt.close()
        print(f"Gráfico salvo em: {caminho_saida}")
    except Exception as e:
        print(f"Erro ao gerar o gráfico para {nome_imagem}: {e}")

# Função principal
def main():
    # Caminhos
    pasta_dados = "dados"
    pasta_saida = "resultados"

    # Filtros
    filtro_subject = 2  # Substitua pelo ID do participante desejado ou use None para desativar o filtro
    filtro_nome_imagem = "000000001455.jpg"  # Substitua pelo nome da imagem desejada ou use None para desativar o filtro

    # Listar arquivos JSON
    arquivos_json = listar_arquivos_json(pasta_dados)

    # Processar cada arquivo JSON
    for arquivo in arquivos_json:
        caminho_arquivo = os.path.join(pasta_dados, arquivo)
        dados = carregar_dados_json(caminho_arquivo)

        if dados:
            # Verificar se o JSON é uma lista
            if isinstance(dados, list):
                for item in dados:
                    nome_imagem, participante, task, bbox, fixacoes_x, fixacoes_y, tempos = processar_dados(item)

                    # Aplicar filtros
                    if filtro_subject is not None and participante != filtro_subject:
                        continue
                    if filtro_nome_imagem is not None and nome_imagem != filtro_nome_imagem:
                        continue

                    if nome_imagem and participante and task and bbox and fixacoes_x and fixacoes_y and tempos:
                        # Caminho da imagem associada
                        caminho_imagem = os.path.join(pasta_dados, "imagens", task, nome_imagem)
                        print(f"BBOX: {bbox} para imagem {nome_imagem} do participante {participante}")
                        if os.path.exists(caminho_imagem):
                            # Gerar gráfico
                            gerar_grafico_fixacoes(caminho_imagem, bbox, fixacoes_x, fixacoes_y, tempos,
                                                   participante, nome_imagem, pasta_saida)
                        else:
                            print(f"Imagem não encontrada: {caminho_imagem}")
                    else:
                        print(f"Dados incompletos no item do arquivo: {arquivo}")
            else:
                print(f"O arquivo {arquivo} não contém uma lista de objetos JSON.")

if __name__ == "__main__":
    main()