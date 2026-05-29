# from flask import Flask, jsonify, request
# from flask_cors import CORS


# app = Flask(__name__)
# CORS(app, supports_credentials=True)

# URL_JAVA = "http://localhost:8080/nota-fiscal/1"
# # URL_JAVA = "http://3.80.252.47/"

# @app.route("/receber-nf", methods=["POST"])
# def receber_nf():
#     try:
#         nf = request.get_json()

#         print("NF recebida:")
#         print(nf)

#         return jsonify({
#             "status": "ok",
#             "mensagem": "NF recebida com sucesso"
#         })

#     except Exception as e:
#         print("ERRO:", e)
#         return jsonify({
#             "status": "erro",
#             "mensagem": str(e)
#         }), 500

# if __name__ == "__main__":
#     app.run(port=5000)


import requests
import json
import os
from datetime import datetime, timedelta
from base64 import b64encode
from flask import Flask, jsonify, request, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ─── Configurações do Bling ───────────────────────────────────────────────────
CLIENT_ID     = "3a241b817839f9d8a9f9813636e0d82f61750766"
CLIENT_SECRET = "37d5e3369038caebf32589567b5832623f9a3e408bdb643b1fdf99017ddb"
REDIRECT_URI  = "http://127.0.0.1:5000/callback"
TOKEN_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bling_token.json")

# ─── Gerenciamento de token em arquivo ───────────────────────────────────────
def salvar_token(token_data):
    token_data["salvo_em"] = datetime.now().isoformat()
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)
    print("Token salvo em", TOKEN_FILE)

def carregar_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

def token_expirado(token_data):
    salvo_em = datetime.fromisoformat(token_data.get("salvo_em", "2000-01-01"))
    expires_in = token_data.get("expires_in", 21600)
    return datetime.now() >= salvo_em + timedelta(seconds=expires_in - 300)

def get_access_token():
    token_data = carregar_token()
    if not token_data:
        return None
    if token_expirado(token_data):
        print("Token expirado, renovando com refresh_token...")
        token_data = renovar_token(token_data.get("refresh_token"))
        if not token_data:
            return None
    return token_data.get("access_token")

def renovar_token(refresh_token):
    url = "https://bling.com.br/Api/v3/oauth/token"
    credentials = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Renovação token:", response.status_code, response.text)
    if response.status_code == 200:
        token_data = response.json()
        salvar_token(token_data)
        return token_data
    return None

# ─── OAuth: rota de callback ──────────────────────────────────────────────────
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"erro": "Código não recebido"}), 400
    token_data = obter_token(code)
    if token_data:
        salvar_token(token_data)
        return "<h2>✅ Autorizado com sucesso! Pode fechar esta aba.</h2>"
    else:
        return jsonify({"erro": "Falha ao obter token"}), 500

def obter_token(code):
    url = "https://bling.com.br/Api/v3/oauth/token"
    credentials = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    payload = {
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Resposta token:", response.status_code, response.text)
    if response.status_code == 200:
        return response.json()
    return None

# ─── Receber NF do Java e enviar pro Bling ────────────────────────────────────
@app.route("/receber-nf", methods=["POST"])
def receber_nf():
    try:
        nf = request.get_json()
        print("NF recebida:", nf)

        token = get_access_token()
        if not token:
            return jsonify({
                "status": "erro",
                "mensagem": "Token do Bling não configurado. Acesse /autorizar primeiro."
            }), 401

        resultado = enviar_para_bling(nf, token)
        return jsonify(resultado)

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


def transformar_para_bling(nf):
    fornecedor = nf["fornecedor"]
    endereco   = fornecedor["endereco"]

    # tipo: 0 = entrada, 1 = saída
    tipo = "0" if nf["tipoNota"] == "ENTRADA" else "1"

    # dataOperacao com hora
    data_operacao = nf["dataEmissao"] + " " + datetime.now().strftime("%H:%M:%S")

    return {
        "contato": {
            "nome":            fornecedor["nome"],
            "tipoPessoa":      "J" if len(fornecedor["documento"]) > 11 else "F",
            "numeroDocumento": fornecedor["documento"],
            "contribuinte":    2,
            "ie":              "",
            "rg":              "",
            "telefone":        "",
            "email":           "",
            "endereco": {
                "endereco":    endereco["logradouro"],
                "bairro":      endereco["bairro"],
                "municipio":   endereco["cidade"],
                "numero":      endereco["numero"],
                "complemento": "",
                "cep":         endereco["cep"],
                "uf":          endereco["estado"],
                "pais":        ""
            }
        },
        "tipo":           tipo,
        "situacao":       6,
        "dataOperacao":   data_operacao,
        "naturezaOperacao": {"id": "0"},
        "itens": [
            {
                "codigo":     str(item["idProduto"]),
                "descricao":  item["descricao"],
                "unidade":    "KG",
                "quantidade": str(item["quantidade"]),
                "valor":      str(item["valorUnitario"])
            }
            for item in nf["itens"]
        ]
    }


def enviar_para_bling(nf, token):
    try:
        bling_json = transformar_para_bling(nf)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        print("\nJSON enviado pro Bling:", json.dumps(bling_json, indent=2, ensure_ascii=False))
        response = requests.post(
            "https://api.bling.com.br/Api/v3/nfe",
            json=bling_json,
            headers=headers
        )
        print("Resposta Bling:", response.status_code, response.text)
        return {
            "status":   response.status_code,
            "resposta": response.json() if response.content else {}
        }
    except Exception as e:
        return {"erro": str(e)}


# ─── Rota de autorização ──────────────────────────────────────────────────────
@app.route("/autorizar")
def autorizar():
    url = (
        f"https://www.bling.com.br/Api/v3/oauth/authorize"
        f"?response_type=code&client_id={CLIENT_ID}&state=randomstate123"
    )
    return redirect(url)


if __name__ == "__main__":
    app.run(port=5000, debug=True)