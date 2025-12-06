import requests
import json
import argparse
from base64 import b64encode
from flask import Flask, redirect, request
from datetime import datetime
import threading
import time
import webbrowser


app = Flask(__name__)
authorization_code = None

@app.route('/')
def index():
    return 'Acesse /authorize para iniciar o processo de autorização.'

@app.route('/authorize')
def authorize(args):
    authorization_url = (
        f"https://www.bling.com.br/Api/v3/oauth/authorize?"
        f"response_type=code&client_id={args.client_id}&state=3f51a288cc425c7dd45151fbebf86f37"
    )
    print("Redirecionando para a URL de autorização:", authorization_url)  # Adicionando print para debug
    webbrowser.open(authorization_url)

    return redirect(authorization_url)

@app.route('/callback')
def callback():
    global authorization_code
    print("Parâmetros recebidos:", request.args)  # Adicionando isto para ver os parâmetros
    authorization_code = request.args.get('code')
    return f"Autorizado! O código é: {authorization_code}. Você pode fechar esta janela."

def run_flask():
    app.run(port=5000)

def obter_token(client_id, client_secret, redirect_uri, code):
    url = "https://bling.com.br/Api/v3/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code
    }
    headers = {
        "Authorization": f"Basic {b64encode(f'{client_id}:{client_secret}'.encode()).decode()}"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    print("Resposta do servidor:", response.text)

    if response.status_code == 200:
        return response.json()
    else:
        print("Erro ao obter token:", response.status_code, response.text)
        return None

def emitir_nota_fiscal(token, dados_nota):

    print("Emitindo a NF:")

    url = "https://api.bling.com.br/Api/v3/nfe"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=dados_nota)

    if response.status_code == 201:        
        print ("NF emitida com SUCESSO: ", response.status_code, response.text)
    else:
        print("ERRO ao emitir a NF: ", response.status_code, response.text)

def main():
    parser = argparse.ArgumentParser(description="Emitir Nota Fiscal via API Bling")
    parser.add_argument("--client_id", required=True, help="Client ID da aplicação")
    parser.add_argument("--client_secret", required=True, help="Client Secret da aplicação")
    parser.add_argument("--redirect_uri", required=True, help="Redirect URI")
    parser.add_argument("--dados_nota", required=True, help="Dados da Nota Fiscal em JSON")
    
    args = parser.parse_args()

    # Iniciar o servidor Flask em uma nova thread
    thread = threading.Thread(target=run_flask)
    thread.start()

    # Esperar um momento para garantir que o servidor esteja ativo
    time.sleep(1)

    print("Iniciando o processo de autorização...")
    authorize(args)
    
    # Esperar até que o código seja capturado
    while authorization_code is None:
        time.sleep(1)  # Checar a captura do código
    
    # Após capturar o código, prosseguir com a obtenção do token
    token_data = obter_token(args.client_id, args.client_secret, args.redirect_uri, authorization_code)

    if token_data is None:
        print("Falha na obtenção do token. Verifique os parâmetros e tente novamente.")
        return

    token = token_data.get("access_token")
    
    if token:                   

        print("Token autorizado, emitindo NF:")

        # Mudar essa parte pra pegar a NF no Java!!!
        dados_nota = json.loads(args.dados_nota)                     
        
        emitir_nota_fiscal(token, dados_nota)
    else:
        print("Erro ao obter token:", token_data)

if __name__ == "__main__":
    main()