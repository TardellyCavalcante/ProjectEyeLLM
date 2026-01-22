from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import json
import time
import sqlite3
from datetime import datetime

# ---------------- Configurações ----------------
URL = "https://www3.honda.com.br/corp/ihs/portal/#/menu-principal"
API_PATH_SUBSTRING = "/eyar-you-vnruly-Sist-thinke-not-for-Lady-keene-S"

# Seletores (ajustar conforme HTML real)
SEARCH_FIELD = 'input[placeholder="Buscar"]'

# Lista de cotas que você quer buscar
COTAS = ["123456", "234567", "345678"]

# Intervalo entre buscas (em segundos)
INTERVALO = 60 * 30  # 30 minutos

# Arquivo do banco SQLite
DB_FILE = "cotas_honda.db"
# ------------------------------------------------

# Cria banco SQLite
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS cotas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cota TEXT,
        data_hora TEXT,
        resultado TEXT
    )
''')
conn.commit()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        resultados = {}

        # Captura respostas JSON da API
        def handle_response(response):
            try:
                if API_PATH_SUBSTRING in response.url and "application/json" in (response.headers.get("content-type") or ""):
                    try:
                        data = response.json()
                        resultados['data'] = data
                        print("\n=== JSON RECEBIDO ===")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                    except:
                        pass
            except Exception as e:
                print("Erro ao processar resposta:", e)

        page.on("response", handle_response)

        # Abrir portal
        page.goto(URL)

        # Resolver login e CAPTCHA manualmente
        input("Faça login e resolva o CAPTCHA no navegador e depois pressione Enter aqui...")

        print("Iniciando loop de consultas automáticas...")

        while True:
            for cota in COTAS:
                print(f"\nBuscando cota: {cota}")
                resultados.clear()
                try:
                    page.fill(SEARCH_FIELD, cota)
                    page.press(SEARCH_FIELD, "Enter")
                except PWTimeout:
                    print("Campo de busca não encontrado. Faça manualmente.")

                # Espera respostas da API
                time.sleep(5)

                # Salvar no banco
                if 'data' in resultados:
                    c.execute(
                        "INSERT INTO cotas (cota, data_hora, resultado) VALUES (?, ?, ?)",
                        (cota, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), json.dumps(resultados['data'], ensure_ascii=False))
                    )
                    conn.commit()
                    print(f"Cota {cota} salva no banco.")
                else:
                    print(f"Nenhum resultado para cota {cota}.")

                time.sleep(2)  # pequeno intervalo entre cotas

            print(f"\nAguardando {INTERVALO/60} minutos para próxima rodada...")
            time.sleep(INTERVALO)

if __name__ == "__main__":
    main()
