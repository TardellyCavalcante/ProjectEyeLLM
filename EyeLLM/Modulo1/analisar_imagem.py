import base64
import os
from openai import OpenAI
from dotenv import load_dotenv

# Carregar .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def codificar_imagem(path_imagem):
    print(f"Codificando imagem: {path_imagem}") 
    with open(path_imagem, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def analisar_imagem(path_imagem, prompt):
    base64_img = codificar_imagem(path_imagem)

    response = client.responses.create(
        #model="gpt-4.1-mini",
        model="gpt-5.2-chat-latest",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_img}"
                    }
                ]
            }
        ]
    )

    saida = []
    for item in response.output[0].content:
        if item.type == "output_text":
            saida.append(item.text)

    return "\n".join(saida)


