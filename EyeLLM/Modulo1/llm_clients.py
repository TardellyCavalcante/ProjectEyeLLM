import os
from openai import OpenAI
import google.generativeai as genai
import anthropic
import requests
import base64
from io import BytesIO
from PIL import Image

# Função para analisar com GPT (OpenAI)
def analyze_with_gpt(api_key, url_imagem, prompt, model="gpt-5.2-chat-latest"):
    """
    Realiza a chamada para a API da OpenAI (GPT).
    """
    client = OpenAI(api_key=api_key)
    
    print(f"Submetendo imagem ao {model} via URL...")

    try:
        response = client.responses.create(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": url_imagem
                        }
                    ]
                }
            ]
        )

        if response.output_text is None:
            raise RuntimeError("O modelo não retornou texto (output_text é None)")

        return response.output_text

    except Exception as e:
        print(f"Erro na chamada GPT: {e}")
        return None

# Função para analisar com Gemini (Google)
def analyze_with_gemini(api_key, url_imagem, prompt, model="gemini-1.5-flash"):
    """
    Estrutura para chamada da API do Gemini.
    Requer a biblioteca google-generativeai instalada.
    """
    print(f"Submetendo imagem ao {model} (Gemini)...")
    
    try:
        genai.configure(api_key=api_key)
        
        # Baixar a imagem da URL
        response = requests.get(url_imagem)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        
        # Configurar e chamar o modelo
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content([prompt, image])
        
        return response.text
    except Exception as e:
        print(f"Erro na chamada Gemini: {e}")
        return None

# Função para analisar com Claude (Anthropic)
def analyze_with_claude(api_key, url_imagem, prompt, model="claude-3-opus-20240229"):
    """
    Estrutura para chamada da API do Claude.
    Requer a biblioteca anthropic instalada.
    """
    print(f"Submetendo imagem ao {model} (Claude)...")
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Baixar a imagem e converter para base64
        response = requests.get(url_imagem)
        response.raise_for_status()
        media_type = response.headers.get('content-type', 'image/jpeg')
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        return message.content[0].text
    except Exception as e:
        print(f"Erro na chamada Claude: {e}")
        return None