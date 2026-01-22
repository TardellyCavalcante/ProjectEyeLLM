import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
import json

def desenhar_bbox(imagem_path, resposta_modelo):
    """
    Desenha as caixas delimitadoras (bounding boxes) na imagem com base na resposta do modelo.

    Args:
        imagem_path (str): Caminho para a imagem.
        resposta_modelo (str): Resposta do modelo em formato JSONL (uma linha por objeto).
    """
    try:
        # Carregar a imagem
        img = Image.open(imagem_path)
        plt.figure(figsize=(10, 8))
        plt.imshow(img)
        plt.axis('off')

        # Processar a resposta do modelo (JSONL)
        objetos = [json.loads(linha) for linha in resposta_modelo.strip().split("\n")]

        # Desenhar cada caixa delimitadora
        for objeto in objetos:
            if "bbox" in objeto:
                bbox = objeto["bbox"]
                x, y, largura, altura = bbox
                label = objeto.get("task", "object")  # Nome do objeto (task)
                plt.gca().add_patch(Rectangle((x, y), largura, altura, edgecolor='red', facecolor='none', linewidth=2))
                plt.text(x, y - 10, label, color='red', fontsize=10, bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

        # Exibir a imagem com as caixas
        plt.show()

    except Exception as e:
        print(f"Erro ao desenhar as caixas delimitadoras: {e}")

def main():
    """
    Função principal para criar uma imagem com bounding boxes de forma estática.
    """
    # Caminho para a imagem
    imagem_path = "dados/imagens/bottle/000000001455.jpg"

    # Resposta do modelo (JSONL)
    resposta_modelo = """
    {"name":"000000001455.jpg","subject":2,"task":"watermelon","condition":"present","bbox":[430,25,200,155]} 
    {"name":"000000001455.jpg","subject":2,"task":"bottle","condition":"present","bbox":[358,13,42,110]} 
    {"name":"000000001455.jpg","subject":2,"task":"basket","condition":"present","bbox":[563,60,77,136]} 
    {"name":"000000001455.jpg","subject":2,"task":"plate","condition":"present","bbox":[479,241,116,81]} 
    {"name":"000000001455.jpg","subject":2,"task":"box","condition":"present","bbox":[55,123,580,304]} 
    {"name":"000000001455.jpg","subject":2,"task":"donut","condition":"present","bbox":[279,266,69,56]} 
    {"name":"000000001455.jpg","subject":2,"task":"knife","condition":"present","bbox":[268,322,122,21]} 
    {"name":"000000001455.jpg","subject":2,"task":"bag","condition":"present","bbox":[0,125,110,100]}"""

    # Chamar a função para desenhar as caixas
    desenhar_bbox(imagem_path, resposta_modelo)

if __name__ == "__main__":
    main()