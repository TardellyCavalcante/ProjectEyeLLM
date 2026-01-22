import os
import json
import openai
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image
from analisar_imagem import analisar_imagem
from visualizacao import desenhar_bbox  # Importar a função desenhar_bbox

# Configuração da API da OpenAI
openai.api_key = "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"  # Substitua pela sua chave da API da OpenAI

# Função para ler um arquivo JSON
def ler_arquivo_json(caminho_arquivo):
    """
    Lê um arquivo JSON e retorna os dados como um objeto JSON.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler o arquivo JSON: {e}")
        return []

# Função para submeter a imagem e o prompt à API da OpenAI
def submeter_api_openai(imagem_path, prompt):
    """
    Submete uma imagem e um prompt à API da OpenAI e retorna a resposta.
    """
    try:
        with open(imagem_path, "rb") as img_file:
            response = openai.Image.create_edit(
                model="gpt-5.2",  # Modelo GPT-5.2
                prompt=prompt,
                image=img_file
            )
            return response  # Retorna a resposta da API
    except Exception as e:
        print(f"Erro ao submeter à API da OpenAI: {e}")
        return None

# Função para desenhar as caixas delimitadoras na imagem
def desenhar_caixas(imagem_path, caixas, pasta_saida, resposta_api, subject, name, modelo):
    """
    Desenha as caixas delimitadoras na imagem e salva o resultado.
    """
    try:
        # Carregar a imagem
        img = Image.open(imagem_path)
        plt.figure(figsize=(10, 8))
        plt.imshow(img)
        plt.axis('off')

        # Desenhar as caixas delimitadoras
        for caixa in caixas:
            x, y, largura, altura = caixa
            plt.gca().add_patch(Rectangle((x, y), largura, altura, edgecolor='red', facecolor='none', linewidth=2))

        # Criar a pasta de saída para o modelo
        pasta_modelo = os.path.join(pasta_saida, modelo)
        os.makedirs(pasta_modelo, exist_ok=True)

        # Salvar a imagem com as caixas
        nome_arquivo = f"{subject}_{name}"
        caminho_saida = os.path.join(pasta_modelo, nome_arquivo)
        plt.savefig(caminho_saida)
        plt.close()
        print(f"Imagem com caixas salva em: {caminho_saida}")

        # Salvar a resposta da API em um arquivo .txt
        caminho_resposta = os.path.join(pasta_modelo, f"{subject}_{os.path.splitext(name)[0]}.txt")
        with open(caminho_resposta, 'w', encoding='utf-8') as f:
            f.write(json.dumps(resposta_api, indent=4))
        print(f"Resposta da API salva em: {caminho_resposta}")
    except Exception as e:
        print(f"Erro ao desenhar caixas ou salvar resultados: {e}")


# Função para listar e ler arquivos JSON em uma pasta
def listar_e_ler_json(pasta_dados, filtro_subject=None, filtro_nome_imagem=None):
    """
    Lista todos os arquivos JSON na raiz da pasta especificada, lê os registros e aplica os filtros.
    
    Args:
        pasta_dados (str): Caminho para a pasta onde os arquivos JSON estão localizados.
        filtro_subject (int, optional): ID do participante para filtrar os registros. Use None para desativar o filtro.
        filtro_nome_imagem (str, optional): Nome da imagem para filtrar os registros. Use None para desativar o filtro.
    
    Returns:
        list: Lista de registros JSON que atendem aos filtros.
    """
    registros_filtrados = []

    try:
        # Listar todos os arquivos JSON na pasta
        arquivos_json = [f for f in os.listdir(pasta_dados) if f.endswith('.json')]

        # Processar cada arquivo JSON
        for arquivo in arquivos_json:
            caminho_arquivo = os.path.join(pasta_dados, arquivo)
            registros = ler_arquivo_json(caminho_arquivo)

            # Verificar se o arquivo JSON contém uma lista de registros
            if isinstance(registros, list):
                for registro in registros:
                    try:
                        # Aplicar filtros
                        if filtro_subject is not None and registro.get("subject") != filtro_subject:
                            continue
                        if filtro_nome_imagem is not None and registro.get("name") != filtro_nome_imagem:
                            continue

                        # Adicionar registro filtrado à lista
                        registros_filtrados.append(registro)
                    except Exception as e:
                        print(f"Erro ao processar registro no arquivo {arquivo}: {e}")
            else:
                print(f"O arquivo {arquivo} não contém uma lista de registros.")
    except Exception as e:
        print(f"Erro ao listar ou ler arquivos JSON na pasta {pasta_dados}: {e}")

    return registros_filtrados

def ler_prompt(caminho_prompt):
    with open(caminho_prompt, 'r', encoding='utf-8') as f:
        return f.read().strip()

def gerar_texto(template_path, dados):
    with open(template_path, "r", encoding="utf-8") as f:
        texto = f.read()

    for chave, valor in dados.items():
        marcador = f"{{{{{chave}}}}}"
        texto = texto.replace(marcador, str(valor))
    print(f"Texto gerado: {repr(texto)}")
    print("-----")
    return texto


# Função principal
def main():
    # Caminhos
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAIZ = os.path.dirname(BASE_DIR)
    RAIZ_IMAGEMS = os.path.dirname(RAIZ)
    print(f"Raiz das imagens: {RAIZ_IMAGEMS}")

    # Nome do modelo LLM
    modelo = "GPT5_2"

    pasta_dados = "dados"
    pasta_saida = "resultados"

     # Filtros
    filtro_subject = 2  # Substitua pelo ID do participante desejado ou use None para desativar o filtro
    filtro_nome_imagem = "000000001455.jpg"  # Substitua pelo nome da imagem desejada ou use None para desativar o filtro

    # Criar a pasta de saída, se não existir
    os.makedirs(pasta_saida, exist_ok=True)

    # Ler os arquivos JSON
    registros = listar_e_ler_json(pasta_dados, filtro_subject, filtro_nome_imagem)
    print(f"Número de registros filtrados: {len(registros)}")

    caminho_prompt = os.path.join("resultados", "Modulo1", "Prompts", "GPT5_2.txt")
    
    
    # Processar cada registro nos arquivos JSON
    for registro in registros:
        try:
            # Localizar a imagem no caminho "dados/imagens/task/name"
            caminho_imagem = os.path.join(RAIZ_IMAGEMS, "dados/imagens", registro["task"], registro["name"])
            if not os.path.exists(caminho_imagem):
                print(f"Imagem não encontrada: {caminho_imagem}")
                continue

            # Gerar o prompt com base nos dados do registro
            #print(f"Processando imagem: {caminho_imagem}")
            dados = {"subject": registro['subject'], "name": registro['name']}
            prompt = gerar_texto(caminho_prompt, dados)
            # Verificar se o prompt foi gerado corretamente
            if not prompt:
                print("Erro: Não foi possível carregar o prompt.")
                return
            
            print(f"Prompt gerado: {repr(prompt)}")
            # Submeter à API da OpenAI
            resposta = analisar_imagem(caminho_imagem, prompt)
            print(f"Resposta da API para a imagem {registro['name']}: {resposta}")

            # Verificar se a resposta é uma string JSONL e processar cada linha
            if isinstance(resposta, str):
                print("Processando a resposta da API...")
                print(repr(resposta))
                try:
                    # Dividir a resposta em linhas e converter cada linha em um dicionário
                    objetos = [json.loads(linha) for linha in resposta.strip().split("\n")]
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar a resposta da API: {e}")
                    continue
            else:
                print(f"Resposta inválida da API para a imagem: {caminho_imagem}")
                continue

            # Processar cada objeto JSON na resposta
            caixas = []
            for objeto in objetos:
                if "bbox" in objeto:
                    caixas.append(objeto["bbox"])

            # Desenhar as caixas na imagem e salvar os resultados
            desenhar_bbox(caminho_imagem, resposta)
        except KeyError as e:
            print(f"Erro no registro JSON: chave ausente {e}")
        except Exception as e:
            print(f"Erro ao processar o registro: {e}")

if __name__ == "__main__":
    main()